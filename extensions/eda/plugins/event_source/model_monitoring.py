"""EDA event source plugin for RHOAI model monitoring alerts.

Streams model monitoring alerts including drift detection, accuracy
degradation, and latency spikes from RHOAI model monitors.

Arguments:
    api_url: RHOAI API URL
    api_token: Bearer token for authentication
    validate_certs: Whether to validate SSL certificates (default: true)
    poll_interval: Polling interval in seconds (default: 15)
    namespace: Namespace to monitor (optional, monitors all if not set)
    severity_filter: Minimum severity to emit (info, warning, critical)
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

SEVERITY_LEVELS = {"info": 0, "warning": 1, "critical": 2}


async def main(queue: asyncio.Queue, args: dict[str, Any]) -> None:
    """Stream model monitoring alerts."""
    api_url = args["api_url"].rstrip("/")
    api_token = args["api_token"]
    validate_certs = args.get("validate_certs", True)
    poll_interval = int(args.get("poll_interval", 15))
    namespace = args.get("namespace")
    severity_filter = args.get("severity_filter", "info")
    min_severity = SEVERITY_LEVELS.get(severity_filter, 0)

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
    }

    ssl = None if validate_certs else False
    seen_alerts: set[str] = set()

    async with aiohttp.ClientSession(headers=headers) as session:
        logger.info("RHOAI model monitoring event source started")

        while True:
            await asyncio.sleep(poll_interval)
            try:
                url = f"{api_url}/apis/v1/monitors/alerts"
                params = {}
                if namespace:
                    params["namespace"] = namespace

                async with session.get(url, params=params, ssl=ssl) as resp:
                    if resp.status != 200:
                        logger.warning("Monitor alerts poll returned status %d", resp.status)
                        continue

                    data = await resp.json()
                    for alert in data.get("items", data.get("alerts", [])):
                        alert_id = alert.get("id", "")
                        if alert_id and alert_id not in seen_alerts:
                            seen_alerts.add(alert_id)
                            severity = alert.get("severity", "info")
                            if SEVERITY_LEVELS.get(severity, 0) < min_severity:
                                continue

                            event = {
                                "model_monitoring": {
                                    "event_type": alert.get("type", "unknown"),
                                    "alert_id": alert_id,
                                    "severity": severity,
                                    "model_name": alert.get("model_name", ""),
                                    "inference_service": alert.get("inference_service", ""),
                                    "namespace": alert.get("namespace", ""),
                                    "metric_name": alert.get("metric_name", ""),
                                    "metric_value": alert.get("metric_value"),
                                    "threshold": alert.get("threshold"),
                                    "message": alert.get("message", ""),
                                    "timestamp": alert.get("timestamp", ""),
                                }
                            }
                            await queue.put(event)
                            logger.info(
                                "Model monitoring alert: %s severity=%s model=%s",
                                alert.get("type"),
                                severity,
                                alert.get("model_name"),
                            )

            except aiohttp.ClientError as e:
                logger.error("Error polling model monitoring: %s", e)
            except Exception as e:
                logger.error("Unexpected error in model monitoring source: %s", e)


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
