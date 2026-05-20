"""RHOAI authentication utilities for creating authenticated REST clients."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module_utils: rhoai_auth
short_description: RHOAI authentication and REST client creation
description:
  - Provides create_rhoai_client to build an authenticated REST client
    for the Red Hat OpenShift AI API using bearer token authentication.
  - Supports environment variable fallback for API URL and token.
author:
  - Steve Fulmer (@stevefulme1)
"""

import os

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class RHOAIClient(object):
    """Authenticated REST client for the RHOAI API."""

    def __init__(self, api_url, api_token, validate_certs=True):
        self.api_url = api_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        self.session.verify = validate_certs

    def get(self, path, **kwargs):
        """Send a GET request."""
        return self.session.get(f"{self.api_url}{path}", **kwargs)

    def post(self, path, json=None, **kwargs):
        """Send a POST request."""
        return self.session.post(f"{self.api_url}{path}", json=json, **kwargs)

    def put(self, path, json=None, **kwargs):
        """Send a PUT request."""
        return self.session.put(f"{self.api_url}{path}", json=json, **kwargs)

    def patch(self, path, json=None, **kwargs):
        """Send a PATCH request."""
        return self.session.patch(f"{self.api_url}{path}", json=json, **kwargs)

    def delete(self, path, **kwargs):
        """Send a DELETE request."""
        return self.session.delete(f"{self.api_url}{path}", **kwargs)


def create_rhoai_client(module):
    """Create an authenticated RHOAI REST client from module params."""
    if not HAS_REQUESTS:
        module.fail_json(msg="The 'requests' Python library is required. Install with: pip install requests")
        return None

    api_url = module.params.get("api_url") or os.environ.get("RHOAI_API_URL")
    api_token = module.params.get("api_token") or os.environ.get("RHOAI_API_TOKEN")
    validate_certs = module.params.get("validate_certs", True)

    if not api_url:
        module.fail_json(msg="Parameter 'api_url' is required or set RHOAI_API_URL environment variable.")
    if not api_token:
        module.fail_json(msg="Parameter 'api_token' is required or set RHOAI_API_TOKEN environment variable.")

    return RHOAIClient(api_url, api_token, validate_certs)
