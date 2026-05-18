# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for model_registry module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.stevefulme1.rhoai_mlops.plugins.modules.model_registry import (
    get_module_args,
)


class TestModelRegistryArgs:
    """Tests for model_registry argument spec."""

    def test_has_name_param(self):
        args = get_module_args()
        assert "name" in args
        assert args["name"]["required"] is True

    def test_has_state_param(self):
        args = get_module_args()
        assert "state" in args
        assert args["state"]["default"] == "present"
        assert "present" in args["state"]["choices"]
        assert "absent" in args["state"]["choices"]

    def test_includes_common_args(self):
        args = get_module_args()
        assert "api_url" in args
        assert "api_token" in args
        assert "validate_certs" in args
        assert "wait" in args
        assert "wait_timeout" in args

    def test_has_description_param(self):
        args = get_module_args()
        assert "description" in args

    def test_has_labels_param(self):
        args = get_module_args()
        assert "labels" in args
        assert args["labels"]["type"] == "dict"
