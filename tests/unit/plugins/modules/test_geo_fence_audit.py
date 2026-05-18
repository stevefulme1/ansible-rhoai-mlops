# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for geo_fence_audit module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.stevefulme1.rhoai_mlops.plugins.modules.geo_fence_audit import (
    get_module_args,
)


class TestGeoFenceAuditArgs:
    """Tests for geo_fence_audit argument spec."""

    def test_includes_common_args(self):
        args = get_module_args()
        assert "api_url" in args
        assert "api_token" in args
        assert "validate_certs" in args

    def test_has_audit_name_param(self):
        args = get_module_args()
        assert "audit_name" in args
        assert args["audit_name"]["required"] is True

    def test_has_state_param(self):
        args = get_module_args()
        assert "state" in args
        assert args["state"]["default"] == "present"
        assert "present" in args["state"]["choices"]
        assert "absent" in args["state"]["choices"]

    def test_has_scan_scope_param(self):
        args = get_module_args()
        assert "scan_scope" in args
        assert "choices" in args["scan_scope"]

    def test_report_violations_is_bool(self):
        args = get_module_args()
        assert "report_violations" in args
        assert args["report_violations"]["type"] == "bool"
