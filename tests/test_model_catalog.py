from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import httpx

from zeta_coding.credentials import FileCredentialStore
from zeta_coding.model_catalog_cache import ModelCatalogCache, live_catalog
from zeta_coding.model_discovery import ModelDiscoveryService
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
