# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for rhoai_common module utilities."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_common import (
    RHOAI_COMMON_ARGS,
    READY_STATES,
    WAIT_STATES,
    DEAD_STATES,
    FAILURE_STATES,
    to_dict,
)


class TestRHOAICommonArgs:
    """Tests for RHOAI_COMMON_ARGS."""

    def test_common_args_has_api_url(self):
        assert "api_url" in RHOAI_COMMON_ARGS
        assert RHOAI_COMMON_ARGS["api_url"]["type"] == "str"
        assert RHOAI_COMMON_ARGS["api_url"]["required"] is True

    def test_common_args_has_api_token(self):
        assert "api_token" in RHOAI_COMMON_ARGS
        assert RHOAI_COMMON_ARGS["api_token"]["no_log"] is True

    def test_common_args_has_validate_certs(self):
        assert "validate_certs" in RHOAI_COMMON_ARGS
        assert RHOAI_COMMON_ARGS["validate_certs"]["default"] is True

    def test_common_args_has_wait(self):
        assert "wait" in RHOAI_COMMON_ARGS
        assert RHOAI_COMMON_ARGS["wait"]["default"] is True

    def test_common_args_has_wait_timeout(self):
        assert "wait_timeout" in RHOAI_COMMON_ARGS
        assert RHOAI_COMMON_ARGS["wait_timeout"]["default"] == 600


class TestLifecycleStates:
    """Tests for lifecycle state constants."""

    def test_ready_states(self):
        assert "Available" in READY_STATES
        assert "Ready" in READY_STATES
        assert "Running" in READY_STATES

    def test_wait_states(self):
        assert "Creating" in WAIT_STATES
        assert "Updating" in WAIT_STATES
        assert "Deleting" in WAIT_STATES

    def test_dead_states(self):
        assert "Stopped" in DEAD_STATES

    def test_failure_states(self):
        assert "Failed" in FAILURE_STATES

    def test_no_state_overlap(self):
        assert len(READY_STATES & WAIT_STATES) == 0
        assert len(READY_STATES & FAILURE_STATES) == 0


class TestToDict:
    """Tests for to_dict helper."""

    def test_none_returns_empty_dict(self):
        assert to_dict(None) == {}

    def test_dict_passes_through(self):
        d = {"key": "value"}
        assert to_dict(d) == d

    def test_nested_dict(self):
        d = {"outer": {"inner": "value"}}
        assert to_dict(d) == d

    def test_primitive_passes_through(self):
        assert to_dict("string") == "string"
        assert to_dict(42) == 42
