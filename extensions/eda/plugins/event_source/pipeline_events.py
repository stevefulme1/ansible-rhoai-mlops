"""EDA event source plugin for RHOAI pipeline run events.

Watches pipeline runs for completion and failure events, emitting events
when runs succeed, fail, or encounter errors.

Arguments:
    api_url: RHOAI API URL
    api_token: Bearer token for authentication
    validate_certs: Whether to validate SSL certificates (default: true)
    poll_interval: Polling interval in seconds (default: 15)
    namespace: Namespace to monitor (optional, monitors all if not set)
    pipeline_id: Specific pipeline ID to watch (optional)
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

TERMINAL_STATES = frozenset({"Succeeded", "Failed", "Error", "Skipped", "Cancelled"})


async def main(queue: asyncio.Queue, args: dict[str, Any]) -> None:
    """Watch pipeline runs for completion and failure events."""
    api_url = args["api_url"].rstrip("/")
    api_token = args["api_token"]
    validate_certs = args.get("validate_certs", True)
    poll_interval = int(args.get("poll_interval", 15))
    namespace = args.get("namespace")
    pipeline_id = args.get("pipeline_id")

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
    }

    ssl = None if validate_certs else False
    completed_runs: set[str] = set()

    async with aiohttp.ClientSession(headers=headers) as session:
        # Initial snapshot of completed runs
        url = f"{api_url}/apis/v2beta1/runs"
        params = {}
        if namespace:
            params["namespace"] = namespace
        if pipeline_id:
            params["pipeline_id"] = pipeline_id

        async with session.get(url, params=params, ssl=ssl) as resp:
            if resp.status == 200:
                data = await resp.json()
                for run in data.get("runs", data.get("items", [])):
                    state = run.get("state", run.get("status", ""))
                    if state in TERMINAL_STATES:
                        completed_runs.add(run.get("run_id", run.get("id", "")))

        logger.info("RHOAI pipeline events source started, tracking %d completed runs", len(completed_runs))

        while True:
            await asyncio.sleep(poll_interval)
            try:
                async with session.get(url, params=params, ssl=ssl) as resp:
                    if resp.status != 200:
                        logger.warning("Pipeline runs poll returned status %d", resp.status)
                        continue

                    data = await resp.json()
                    for run in data.get("runs", data.get("items", [])):
                        run_id = run.get("run_id", run.get("id", ""))
                        state = run.get("state", run.get("status", ""))

                        if run_id and state in TERMINAL_STATES and run_id not in completed_runs:
                            completed_runs.add(run_id)

                            event_type = "pipeline_run_succeeded" if state == "Succeeded" else "pipeline_run_failed"
                            event = {
                                "pipeline_events": {
                                    "event_type": event_type,
                                    "run_id": run_id,
                                    "run_name": run.get("display_name", run.get("name", "")),
                                    "pipeline_id": run.get("pipeline_id", ""),
                                    "pipeline_name": run.get("pipeline_name", ""),
                                    "namespace": run.get("namespace", ""),
                                    "state": state,
                                    "error_message": run.get("error", {}).get("message", ""),
                                    "started_at": run.get("created_at", ""),
                                    "finished_at": run.get("finished_at", ""),
                                }
                            }
                            await queue.put(event)
                            logger.info("Pipeline run %s: %s (state=%s)", event_type, run_id, state)

            except aiohttp.ClientError as e:
                logger.error("Error polling pipeline runs: %s", e)
            except Exception as e:
                logger.error("Unexpected error in pipeline events source: %s", e)


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
