# -*- coding: utf-8 -*-
"""Shared fixtures for RHOAI unit tests."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_module():
    """Return a mock AnsibleModule with check_mode disabled."""
    module = MagicMock()
    module.check_mode = False
    module.params = {
        "state": "present",
        "api_url": "https://rhoai.example.com",
        "api_token": "test-token",
        "validate_certs": False,
        "wait": True,
        "wait_timeout": 600,
        "wait_interval": 10,
    }
    return module


@pytest.fixture
def mock_module_check_mode():
    """Return a mock AnsibleModule with check_mode enabled."""
    module = MagicMock()
    module.check_mode = True
    module.params = {
        "state": "present",
        "api_url": "https://rhoai.example.com",
        "api_token": "test-token",
        "validate_certs": False,
        "wait": True,
        "wait_timeout": 600,
        "wait_interval": 10,
    }
    return module


@pytest.fixture
def mock_client():
    """Return a mock RHOAI API client."""
    client = MagicMock()
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"items": []}
    client.get.return_value = response
    create_response = MagicMock()
    create_response.status_code = 201
    create_response.json.return_value = {"id": "new-123", "name": "test"}
    client.post.return_value = create_response
    client.patch.return_value = response
    client.delete.return_value = MagicMock(status_code=204)
    return client
