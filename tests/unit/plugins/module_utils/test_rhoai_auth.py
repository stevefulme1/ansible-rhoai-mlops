# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for rhoai_auth module utilities."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_auth import (
    RHOAIClient,
    create_rhoai_client,
)


class TestRHOAIClient:
    """Tests for RHOAIClient."""

    def test_client_sets_auth_header(self):
        client = RHOAIClient("https://rhoai.example.com", "test-token")
        assert client.session.headers["Authorization"] == "Bearer test-token"

    def test_client_strips_trailing_slash(self):
        client = RHOAIClient("https://rhoai.example.com/", "test-token")
        assert client.api_url == "https://rhoai.example.com"

    def test_client_sets_content_type(self):
        client = RHOAIClient("https://rhoai.example.com", "test-token")
        assert client.session.headers["Content-Type"] == "application/json"

    def test_client_respects_validate_certs(self):
        client = RHOAIClient("https://rhoai.example.com", "test-token", validate_certs=False)
        assert client.session.verify is False


class TestCreateRHOAIClient:
    """Tests for create_rhoai_client."""

    def test_fails_without_requests(self):
        module = MagicMock()
        module.params = {"api_url": "https://rhoai.example.com", "api_token": "tok", "validate_certs": True}

        with patch(
            "ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_auth.HAS_REQUESTS",
            False,
        ):
            create_rhoai_client(module)
            module.fail_json.assert_called_once()

    def test_creates_client_with_params(self):
        module = MagicMock()
        module.params = {
            "api_url": "https://rhoai.example.com",
            "api_token": "test-token",
            "validate_certs": True,
        }

        client = create_rhoai_client(module)
        assert isinstance(client, RHOAIClient)
        assert client.api_url == "https://rhoai.example.com"

    def test_falls_back_to_env_vars(self):
        module = MagicMock()
        module.params = {"api_url": None, "api_token": None, "validate_certs": True}

        with patch.dict("os.environ", {"RHOAI_API_URL": "https://env.example.com", "RHOAI_API_TOKEN": "env-token"}):
            client = create_rhoai_client(module)
            assert client.api_url == "https://env.example.com"
