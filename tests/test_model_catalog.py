from __future__ import annotations

import asyncio
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import httpx

from zeta_coding.credentials import FileCredentialStore
from zeta_coding.model_catalog_cache import ModelCatalogCache, live_catalog
from zeta_coding.model_discovery import ModelDiscoveryService
from zeta_coding.paths import ZetaPaths
from zeta_coding.provider_catalog_merge import merge_model_metadata, unique_strings
from zeta_coding.provider_credentials import api_key_for_provider, has_usable_credentials
from zeta_coding.provider_config import (
    ProviderConfigError,
    load_provider_settings,
    provider_settings_from_json,
    save_provider_settings,
)
from zeta_coding.provider_settings_io import atomic_write_text, settings_path
from zeta_coding.provider_config import OpenAICompatibleProviderConfig


class ModelCatalogCacheTests(unittest.TestCase):
    def test_round_trip_preserves_catalog(self) -> None:
        with TemporaryDirectory() as directory:
            cache = ModelCatalogCache(Path(directory) / "models.json")
            cache.save({"ollama": live_catalog("ollama", ("qwen", "llama"))})

            catalog = cache.load()["ollama"]

            self.assertEqual(catalog.models, ("qwen", "llama"))
            self.assertEqual(catalog.status, "ready")
            self.assertEqual(catalog.source, "live")


class ProviderSettingsIoTests(unittest.TestCase):
    def test_settings_path_uses_zeta_home(self) -> None:
        path = settings_path(ZetaPaths(home=Path("/tmp/zeta-test")))
        self.assertEqual(path, Path("/tmp/zeta-test/providers.json"))

    def test_atomic_write_replaces_existing_file(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "providers.json"
            path.write_text("old", encoding="utf-8")

            atomic_write_text(path, "new")

            self.assertEqual(path.read_text(encoding="utf-8"), "new")
            self.assertFalse(path.with_suffix(".json.tmp").exists())


class ProviderSettingsTests(unittest.TestCase):
    def test_missing_settings_use_builtin_providers(self) -> None:
        with TemporaryDirectory() as directory:
            settings = load_provider_settings(ZetaPaths(home=Path(directory)))

            self.assertTrue(settings.providers)
            self.assertFalse((Path(directory) / "providers.json").exists())

    def test_invalid_settings_json_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            home = Path(directory)
            (home / "providers.json").write_text("[]", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_provider_settings(ZetaPaths(home=home))

    def test_saving_settings_creates_backup(self) -> None:
        with TemporaryDirectory() as directory:
            paths = ZetaPaths(home=Path(directory))
            settings = load_provider_settings(paths)
            save_provider_settings(settings, paths)
            save_provider_settings(settings, paths)

            self.assertTrue((paths.home / "providers.json").exists())
            self.assertTrue((paths.home / "providers.json.bak").exists())


class CredentialTests(unittest.TestCase):
    def test_stored_credential_has_precedence_over_environment(self) -> None:
        class Reader:
            def get(self, name: str) -> str | None:
                return "stored-key"

        provider = type("Provider", (), {
            "name": "test",
            "credential_name": "test-credential",
            "api_key_env": "TEST_CREDENTIAL_KEY",
        })()
        os.environ["TEST_CREDENTIAL_KEY"] = "environment-key"
        try:
            self.assertEqual(api_key_for_provider(provider, credential_reader=Reader()), "stored-key")
            self.assertTrue(has_usable_credentials(provider, credential_reader=Reader()))
        finally:
            os.environ.pop("TEST_CREDENTIAL_KEY", None)

    def test_environment_credential_is_used_when_store_is_empty(self) -> None:
        class Reader:
            def get(self, name: str) -> str | None:
                return None

        provider = type("Provider", (), {
            "name": "test",
            "credential_name": "test-credential",
            "api_key_env": "TEST_CREDENTIAL_KEY",
        })()
        os.environ["TEST_CREDENTIAL_KEY"] = "environment-key"
        try:
            self.assertEqual(api_key_for_provider(provider, credential_reader=Reader()), "environment-key")
        finally:
            os.environ.pop("TEST_CREDENTIAL_KEY", None)


class CatalogMergeHelperTests(unittest.TestCase):
    def test_unique_strings_preserves_first_seen_order(self) -> None:
        self.assertEqual(unique_strings(("a", "b", "a", "c", "b")), ("a", "b", "c"))

    def test_metadata_merge_preserves_incoming_and_adds_existing(self) -> None:
        merged = merge_model_metadata(
            {"shared": "new"},
            {"shared": "old", "legacy": "legacy"},
            lambda incoming, existing: f"{incoming}+{existing}",
        )

        self.assertEqual(merged, {"shared": "new+old", "legacy": "legacy"})


class ProviderCatalogMergeTests(unittest.TestCase):
    def test_legacy_provider_list_rejects_duplicate_names(self) -> None:
        with TemporaryDirectory() as directory:
            settings = load_provider_settings(ZetaPaths(home=Path(directory)))
            provider = settings.providers[0]
            data = {
                "default_provider": provider.name,
                "providers": [provider.to_json(), provider.to_json()],
            }

            with self.assertRaisesRegex(ProviderConfigError, "unique"):
                provider_settings_from_json(data)

    def test_provider_preferences_keep_a_valid_saved_model(self) -> None:
        with TemporaryDirectory() as directory:
            paths = ZetaPaths(home=Path(directory))
            settings = load_provider_settings(paths)
            provider = settings.providers[0]
            data = {
                "default_provider": provider.name,
                "provider_preferences": {
                    provider.name: {"default_model": provider.default_model}
                },
            }

            parsed = provider_settings_from_json(data, paths=paths)

            self.assertEqual(parsed.get_provider(provider.name).default_model, provider.default_model)


class ModelDiscoveryTests(unittest.TestCase):
    def test_openai_compatible_models_are_normalized(self) -> None:
        async def run() -> tuple[str, ...]:
            def respond(request: httpx.Request) -> httpx.Response:
                self.assertEqual(request.url.path, "/v1/models")
                return httpx.Response(
                    200,
                    json={"data": [{"id": "z-model"}, {"id": "a-model"}]},
                )

            with TemporaryDirectory() as directory:
                client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
                provider = OpenAICompatibleProviderConfig(
                    name="test",
                    base_url="https://example.test/v1",
                    api_key_env="TEST_MODEL_API_KEY",
                    credential_name=None,
                    models=("fallback",),
                    default_model="fallback",
                )
                service = ModelDiscoveryService(
                    cache=ModelCatalogCache(Path(directory) / "models.json"),
                    credentials=FileCredentialStore(Path(directory) / "credentials.json"),
                    client=client,
                )
                try:
                    import os

                    os.environ["TEST_MODEL_API_KEY"] = "test-key"
                    summary = await service.refresh((provider,))
                    return summary.catalogs[0].models
                finally:
                    os.environ.pop("TEST_MODEL_API_KEY", None)
                    await client.aclose()

        self.assertEqual(asyncio.run(run()), ("a-model", "z-model"))


if __name__ == "__main__":
    unittest.main()
