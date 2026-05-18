# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for audit_report_info module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.stevefulme1.rhoai_mlops.plugins.modules.audit_report_info import (
    get_module_args,
)


class TestAuditReportInfoArgs:
    """Tests for audit_report_info argument spec."""

    def test_includes_common_args(self):
        args = get_module_args()
        assert "api_url" in args
        assert "api_token" in args
        assert "validate_certs" in args

    def test_has_report_name_param(self):
        args = get_module_args()
        assert "report_name" in args

    def test_has_report_type_param(self):
        args = get_module_args()
        assert "report_type" in args
        assert "choices" in args["report_type"]
