"""Waiter and retry utilities for RHOAI resources."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module_utils: rhoai_wait
short_description: Waiter and retry utilities for RHOAI API operations
description:
  - Provides wait_for_resource to poll an RHOAI resource until it reaches a
    target state, with configurable timeout and failure state detection.
  - Includes call_with_retry for exponential backoff retries on transient
    API errors.
author:
  - Steve Fulmer (@stevefulme1)
"""

import time

try:
    from requests.exceptions import RequestException
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def wait_for_resource(
    module,
    get_fn,
    resource_id,
    target_states,
    failure_states=None,
    state_key="state",
):
    """Poll a resource until it reaches a target state."""
    wait = module.params.get("wait", True)
    if not wait:
        return get_fn(resource_id)

    timeout = module.params.get("wait_timeout", 600)
    interval = module.params.get("wait_interval", 10)

    if failure_states is None:
        failure_states = frozenset({"Failed"})

    start = time.monotonic()
    while True:
        try:
            resource = get_fn(resource_id)
        except RequestException as e:
            if "404" in str(e) and "Deleted" in target_states:
                return None
            raise

        if resource is None:
            if "Deleted" in target_states:
                return None
            elapsed = time.monotonic() - start
            if elapsed >= timeout:
                module.fail_json(
                    msg=f"Timed out waiting for resource {resource_id}. Resource not found.",
                )
            time.sleep(min(interval, timeout - elapsed))
            continue

        state = resource.get(state_key) if isinstance(resource, dict) else getattr(resource, state_key, None)
        if state in target_states:
            return resource
        if state in failure_states:
            module.fail_json(
                msg=f"Resource {resource_id} entered failure state: {state}",
            )

        elapsed = time.monotonic() - start
        if elapsed >= timeout:
            module.fail_json(
                msg=f"Timed out waiting for resource {resource_id} to reach "
                f"state {target_states}. Current state: {state}",
            )
        time.sleep(min(interval, timeout - elapsed))


def call_with_retry(fn, *args, max_retries=3, retry_on=(429, 500, 502, 503), **kwargs):
    """Call an API function with exponential backoff retry."""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = fn(*args, **kwargs)
            if hasattr(response, "status_code") and response.status_code in retry_on:
                if attempt == max_retries:
                    response.raise_for_status()
                time.sleep(2 ** attempt)
                continue
            return response
        except RequestException as e:
            last_error = e
            if attempt == max_retries:
                raise
            time.sleep(2 ** attempt)
    raise last_error
