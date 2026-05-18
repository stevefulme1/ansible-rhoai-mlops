# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for compliance_evidence module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.stevefulme1.rhoai_mlops.plugins.modules.compliance_evidence import (
    get_module_args,
)


class TestComplianceEvidenceArgs:
    """Tests for compliance_evidence argument spec."""

    def test_includes_common_args(self):
        args = get_module_args()
        assert "api_url" in args
        assert "api_token" in args
        assert "validate_certs" in args

    def test_has_evidence_name_param(self):
        args = get_module_args()
        assert "evidence_name" in args
        assert args["evidence_name"]["required"] is True

    def test_has_state_param(self):
        args = get_module_args()
        assert "state" in args
        assert args["state"]["default"] == "present"
        assert "present" in args["state"]["choices"]
        assert "absent" in args["state"]["choices"]

    def test_has_evidence_type_param(self):
        args = get_module_args()
        assert "evidence_type" in args
        assert "choices" in args["evidence_type"]
