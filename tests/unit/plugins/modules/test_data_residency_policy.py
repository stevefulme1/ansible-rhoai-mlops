# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for data_residency_policy module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.stevefulme1.rhoai_mlops.plugins.modules.data_residency_policy import (
    get_module_args,
)


class TestDataResidencyPolicyArgs:
    """Tests for data_residency_policy argument spec."""

    def test_includes_common_args(self):
        args = get_module_args()
        assert "api_url" in args
        assert "api_token" in args
        assert "validate_certs" in args

    def test_has_policy_name_param(self):
        args = get_module_args()
        assert "policy_name" in args
        assert args["policy_name"]["required"] is True

    def test_has_state_param(self):
        args = get_module_args()
        assert "state" in args
        assert args["state"]["default"] == "present"
        assert "present" in args["state"]["choices"]
        assert "absent" in args["state"]["choices"]

    def test_has_data_classification_param(self):
        args = get_module_args()
        assert "data_classification" in args
        assert "choices" in args["data_classification"]

    def test_allowed_regions_is_list(self):
        args = get_module_args()
        assert "allowed_regions" in args
        assert args["allowed_regions"]["type"] == "list"
