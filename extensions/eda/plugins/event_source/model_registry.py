"""EDA event source plugin for RHOAI model registry lifecycle events.

Watches the model registry for lifecycle events such as model registered,
deployed, deprecated, and retired.

Arguments:
    api_url: RHOAI API URL
    api_token: Bearer token for authentication
    validate_certs: Whether to validate SSL certificates (default: true)
    poll_interval: Polling interval in seconds (default: 10)
    model_filter: Optional model name filter pattern
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import asyncio
import logging
from typing import Any

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

logger = logging.getLogger(__name__)


async def main(queue: asyncio.Queue, args: dict[str, Any]) -> None:
    """Watch model registry for lifecycle events."""
    api_url = args["api_url"].rstrip("/")
    api_token = args["api_token"]
    validate_certs = args.get("validate_certs", True)
    poll_interval = int(args.get("poll_interval", 10))
    model_filter = args.get("model_filter")

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
    }

    ssl = None if validate_certs else False
    seen_versions: set[str] = set()

    async with aiohttp.ClientSession(headers=headers) as session:
        # Initial snapshot
        url = f"{api_url}/apis/model-registry/v1/model_versions"
        async with session.get(url, ssl=ssl) as resp:
            if resp.status == 200:
                data = await resp.json()
                for item in data.get("items", []):
                    seen_versions.add(item.get("id", ""))

        logger.info("RHOAI model registry event source started, tracking %d existing versions", len(seen_versions))

        while True:
            await asyncio.sleep(poll_interval)
            try:
                async with session.get(url, ssl=ssl) as resp:
                    if resp.status != 200:
                        logger.warning("Model registry poll returned status %d", resp.status)
                        continue

                    data = await resp.json()
                    for item in data.get("items", []):
                        version_id = item.get("id", "")
                        if version_id and version_id not in seen_versions:
                            seen_versions.add(version_id)
                            model_name = item.get("name", "unknown")
                            if model_filter and model_filter not in model_name:
                                continue
                            event = {
                                "model_registry": {
                                    "event_type": "model_version_created",
                                    "model_name": model_name,
                                    "version_id": version_id,
                                    "version_name": item.get("version_name", ""),
                                    "state": item.get("state", ""),
                                    "artifact_uri": item.get("artifact_uri", ""),
                                    "created_at": item.get("createTimeSinceEpoch", ""),
                                }
                            }
                            await queue.put(event)
                            logger.info("New model version detected: %s/%s", model_name, version_id)

            except aiohttp.ClientError as e:
                logger.error("Error polling model registry: %s", e)
            except Exception as e:
                logger.error("Unexpected error in model registry source: %s", e)


if __name__ == "__main__":

    class MockQueue:
        """Mock queue for standalone testing."""

        async def put(self, event: dict) -> None:
            """Print event for testing."""
            print(event)

    asyncio.run(
        main(
            MockQueue(),
            {
                "api_url": "https://rhoai.example.com",
                "api_token": "test-token",
                "poll_interval": 5,
            },
        )
    )
