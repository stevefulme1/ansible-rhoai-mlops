# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for model_monitor module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from ansible_collections.stevefulme1.rhoai_mlops.plugins.modules import model_monitor


class TestDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert hasattr(model_monitor, "DOCUMENTATION")
        assert len(model_monitor.DOCUMENTATION) > 0

    def test_documentation_has_module_name(self):
        assert "model_monitor" in model_monitor.DOCUMENTATION

    def test_documentation_has_short_description(self):
        assert "short_description" in model_monitor.DOCUMENTATION

    def test_documentation_has_options(self):
        assert "options" in model_monitor.DOCUMENTATION

    def test_examples_exist(self):
        assert hasattr(model_monitor, "EXAMPLES")
        assert len(model_monitor.EXAMPLES) > 0

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.rhoai_mlops" in model_monitor.EXAMPLES

    def test_return_exists(self):
        assert hasattr(model_monitor, "RETURN")
        assert len(model_monitor.RETURN) > 0


class TestModuleArgs:
    """Validate module argument spec."""

    def test_get_module_args_returns_dict(self):
        args = model_monitor.get_module_args()
        assert isinstance(args, dict)

    def test_required_params_present(self):
        args = model_monitor.get_module_args()
        required_params = [p for p in args if args[p].get("required")]
        assert len(required_params) > 0

    def test_common_args_included(self):
        args = model_monitor.get_module_args()
        assert "api_url" in args
        assert "api_token" in args
        assert "validate_certs" in args

    def test_state_choices(self):
        args = model_monitor.get_module_args()
        assert "state" in args
        assert args["state"]["choices"] == ["present", "absent"]
        assert args["state"]["default"] == "present"

    def test_api_token_is_no_log(self):
        args = model_monitor.get_module_args()
        assert args["api_token"].get("no_log") is True


class TestMainFunction:
    """Validate main function exists and is callable."""

    def test_main_exists(self):
        assert hasattr(model_monitor, "main")
        assert callable(model_monitor.main)

    def test_module_has_name_guard(self):
        """Verify the module has if __name__ == __main__ guard."""
        import inspect
        source = inspect.getsource(model_monitor)
        assert 'if __name__ == "__main__"' in source or "if __name__ == '__main__'" in source
