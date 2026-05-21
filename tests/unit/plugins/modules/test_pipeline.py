# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for pipeline module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from ansible_collections.stevefulme1.rhoai_mlops.plugins.modules import pipeline


class TestDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert hasattr(pipeline, "DOCUMENTATION")
        assert len(pipeline.DOCUMENTATION) > 0

    def test_documentation_has_module_name(self):
        assert "pipeline" in pipeline.DOCUMENTATION

    def test_documentation_has_short_description(self):
        assert "short_description" in pipeline.DOCUMENTATION

    def test_documentation_has_options(self):
        assert "options" in pipeline.DOCUMENTATION

    def test_examples_exist(self):
        assert hasattr(pipeline, "EXAMPLES")
        assert len(pipeline.EXAMPLES) > 0

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.rhoai_mlops" in pipeline.EXAMPLES

    def test_return_exists(self):
        assert hasattr(pipeline, "RETURN")
        assert len(pipeline.RETURN) > 0


class TestModuleArgs:
    """Validate module argument spec."""

    def test_get_module_args_returns_dict(self):
        args = pipeline.get_module_args()
        assert isinstance(args, dict)

    def test_required_params_present(self):
        args = pipeline.get_module_args()
        required_params = [p for p in args if args[p].get("required")]
        assert len(required_params) > 0

    def test_common_args_included(self):
        args = pipeline.get_module_args()
        assert "api_url" in args
        assert "api_token" in args
        assert "validate_certs" in args

    def test_state_choices(self):
        args = pipeline.get_module_args()
        assert "state" in args
        assert args["state"]["choices"] == ["present", "absent"]
        assert args["state"]["default"] == "present"

    def test_api_token_is_no_log(self):
        args = pipeline.get_module_args()
        assert args["api_token"].get("no_log") is True


class TestMainFunction:
    """Validate main function exists and is callable."""

    def test_main_exists(self):
        assert hasattr(pipeline, "main")
        assert callable(pipeline.main)

    def test_module_has_name_guard(self):
        """Verify the module has if __name__ == __main__ guard."""
        import inspect
        source = inspect.getsource(pipeline)
        assert 'if __name__ == "__main__"' in source or "if __name__ == '__main__'" in source
