from __future__ import annotations

import asyncio
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic, time

import httpx

from zeta_coding.commands import create_default_command_registry
from zeta_coding.credentials import FileCredentialStore
from zeta_coding.model_catalog_cache import (
    ModelCatalogCache,
    ProviderModelCatalog,
    catalogs_are_fresh,
    live_catalog,
)
from zeta_coding.model_discovery import ModelDiscoveryService
from zeta_coding.provider_config import OpenAICompatibleProviderConfig


def _provider(name: str) -> OpenAICompatibleProviderConfig:
    return OpenAICompatibleProviderConfig(
        name=name,
        base_url=f"https://{name}.test/v1",
        api_key_env=f"{name.upper()}_KEY",
        credential_name=None,
        models=("fallback",),
        default_model="fallback",
    )


class CatalogFreshnessTests(unittest.TestCase):
    def test_empty_cache_is_never_fresh(self) -> None:
        self.assertFalse(catalogs_are_fresh({}))

    def test_catalog_without_refreshed_at_is_not_fresh(self) -> None:
        catalogs = {"a": ProviderModelCatalog(provider="a", models=("m",), status="ready")}
        self.assertFalse(catalogs_are_fresh(catalogs))

    def test_recent_catalog_is_fresh(self) -> None:
        catalogs = {"a": live_catalog("a", ("m",))}
        self.assertTrue(catalogs_are_fresh(catalogs))

    def test_stale_catalog_is_not_fresh(self) -> None:
        catalogs = {"a": ProviderModelCatalog(
            provider="a", models=("m",), status="ready", refreshed_at=0.0
        )}
        self.assertFalse(catalogs_are_fresh(catalogs))
        self.assertFalse(catalogs_are_fresh(catalogs, max_age=1.0, now=10.0))

    def test_all_entries_must_be_fresh(self) -> None:
        now = time()
        catalogs = {
            "a": live_catalog("a", ("m",)),
            "b": ProviderModelCatalog(
                provider="b", models=("m",), status="ready", refreshed_at=now - 10_000.0
            ),
        }
        # One stale entry is enough to make the whole cache stale.
        self.assertFalse(catalogs_are_fresh(catalogs, now=now))


class DiscoveryConcurrencyTests(unittest.TestCase):
    """Providers must be queried concurrently, not one 8s timeout after another."""

    PROVIDERS = tuple(_provider(f"p{index}") for index in range(6))
    DELAY = 0.2

    def _service(self, directory: str) -> ModelDiscoveryService:
        async def slow(request: httpx.Request) -> httpx.Response:
            await asyncio.sleep(self.DELAY)
            return httpx.Response(200, json={"data": [{"id": "m"}]})

        return ModelDiscoveryService(
            cache=ModelCatalogCache(Path(directory) / "models.json"),
            credentials=FileCredentialStore(Path(directory) / "credentials.json"),
            client=httpx.AsyncClient(transport=httpx.MockTransport(slow)),
        )

    def test_refresh_time_is_bounded_by_slowest_provider(self) -> None:
        async def run() -> float:
            import os

            for provider in self.PROVIDERS:
                os.environ[f"{provider.name.upper()}_KEY"] = "test-key"
            try:
                with TemporaryDirectory() as directory:
                    service = self._service(directory)
                    started = monotonic()
                    summary = await service.refresh(self.PROVIDERS)
                    elapsed = monotonic() - started
                    await service._client.aclose()
                    self.assertEqual(summary.ready_count, len(self.PROVIDERS))
                    return elapsed
            finally:
                for provider in self.PROVIDERS:
                    os.environ.pop(f"{provider.name.upper()}_KEY", None)

        elapsed = asyncio.run(run())
        sequential = self.DELAY * len(self.PROVIDERS)
        self.assertLess(elapsed, sequential * 0.75)


class ModelsCommandTests(unittest.TestCase):
    def test_models_command_opens_picker_and_refreshes_in_background(self) -> None:
        registry = create_default_command_registry()

        command = registry.get("/models")

        self.assertIsNotNone(command)
        result = command.handler(_StubContext())  # type: ignore[misc]
        self.assertTrue(result.model_picker_requested)
        self.assertTrue(result.model_catalog_refresh_requested)


class _StubContext:
    """Minimal CommandContext stand-in for the /models handler."""

    args = ""
    text = "/models"
    name = "models"


if __name__ == "__main__":
    unittest.main()
