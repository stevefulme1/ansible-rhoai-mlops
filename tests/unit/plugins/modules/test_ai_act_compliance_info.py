# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for ai_act_compliance_info module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.stevefulme1.rhoai_mlops.plugins.modules.ai_act_compliance_info import (
    get_module_args,
)


class TestAiActComplianceInfoArgs:
    """Tests for ai_act_compliance_info argument spec."""

    def test_includes_common_args(self):
        args = get_module_args()
        assert "api_url" in args
        assert "api_token" in args
        assert "validate_certs" in args

    def test_has_assessment_name_param(self):
        args = get_module_args()
        assert "assessment_name" in args

    def test_has_risk_category_param(self):
        args = get_module_args()
        assert "risk_category" in args
        assert "choices" in args["risk_category"]
