# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for rhoai_wait module utilities."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch


from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_wait import (
    call_with_retry,
    wait_for_resource,
)


class TestCallWithRetry:
    """Tests for call_with_retry."""

    def test_success_on_first_try(self):
        fn = MagicMock(return_value="ok")
        result = call_with_retry(fn, "arg1")
        assert result == "ok"
        fn.assert_called_once_with("arg1")

    def test_retries_on_server_error(self):
        response = MagicMock()
        response.status_code = 500
        response.raise_for_status.side_effect = Exception("500")

        fn = MagicMock(side_effect=[response, MagicMock(status_code=200)])
        with patch("time.sleep"):
            result = call_with_retry(fn, max_retries=1, retry_on=(500,))
            assert result.status_code == 200

    def test_passes_kwargs(self):
        fn = MagicMock(return_value="ok")
        call_with_retry(fn, "arg1", key="value")
        fn.assert_called_once_with("arg1", key="value")


class TestWaitForResource:
    """Tests for wait_for_resource."""

    def test_returns_immediately_when_wait_false(self):
        module = MagicMock()
        module.params = {"wait": False}

        get_fn = MagicMock(return_value={"id": "123", "state": "Creating"})
        result = wait_for_resource(module, get_fn, "123", target_states={"Available"})
        assert result == {"id": "123", "state": "Creating"}

    def test_returns_when_target_state_reached(self):
        module = MagicMock()
        module.params = {"wait": True, "wait_timeout": 60, "wait_interval": 1}

        get_fn = MagicMock(return_value={"id": "123", "state": "Available"})
        with patch("time.sleep"):
            result = wait_for_resource(module, get_fn, "123", target_states={"Available"})
            assert result["state"] == "Available"

    def test_fails_on_failure_state(self):
        module = MagicMock()
        module.params = {"wait": True, "wait_timeout": 60, "wait_interval": 1}

        get_fn = MagicMock(return_value={"id": "123", "state": "Failed"})
        with patch("time.sleep"):
            wait_for_resource(module, get_fn, "123", target_states={"Available"})
            module.fail_json.assert_called_once()
