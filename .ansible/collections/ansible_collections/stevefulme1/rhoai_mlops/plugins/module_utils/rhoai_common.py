"""Common RHOAI argument specs and constants used across all modules."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module_utils: rhoai_common
short_description: Shared RHOAI argument specs and lifecycle constants
description:
  - Defines RHOAI_COMMON_ARGS, the common argument spec shared by all RHOAI modules,
    covering API URL, authentication token, certificate validation, and wait behavior.
  - Provides lifecycle state constants and frozen sets used for resource state
    management and polling.
author:
  - Steve Fulmer (@stevefulme1)
"""


RHOAI_COMMON_ARGS = dict(
    api_url=dict(type="str", required=True, fallback=(lambda: None,)),
    api_token=dict(type="str", required=True, no_log=True),
    validate_certs=dict(type="bool", default=True),
    wait=dict(type="bool", default=True),
    wait_timeout=dict(type="int", default=600),
    wait_interval=dict(type="int", default=10),
)

STATE_AVAILABLE = "Available"
STATE_READY = "Ready"
STATE_RUNNING = "Running"
STATE_CREATING = "Creating"
STATE_UPDATING = "Updating"
STATE_DELETING = "Deleting"
STATE_SUCCEEDED = "Succeeded"
STATE_FAILED = "Failed"
STATE_STOPPED = "Stopped"
STATE_PENDING = "Pending"

WAIT_STATES = frozenset({
    STATE_CREATING,
    STATE_UPDATING,
    STATE_DELETING,
    STATE_PENDING,
})

READY_STATES = frozenset({
    STATE_AVAILABLE,
    STATE_READY,
    STATE_RUNNING,
    STATE_SUCCEEDED,
})

DEAD_STATES = frozenset({
    STATE_STOPPED,
})

FAILURE_STATES = frozenset({
    STATE_FAILED,
})


def to_dict(resource):
    """Convert a resource object or dict to a plain dictionary."""
    if resource is None:
        return {}
    if isinstance(resource, dict):
        return resource
    if hasattr(resource, "__dict__"):
        result = {}
        for key, value in resource.__dict__.items():
            if key.startswith("_"):
                continue
            if isinstance(value, list):
                result[key] = [to_dict(i) if hasattr(i, "__dict__") else i for i in value]
            elif hasattr(value, "__dict__") and not isinstance(value, (str, int, float, bool, dict)):
                result[key] = to_dict(value)
            else:
                result[key] = value
        return result
    return resource
