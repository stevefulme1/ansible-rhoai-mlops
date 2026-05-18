# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Documentation fragment for RHOAI common parameters."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
    api_url:
        description:
            - The URL of the Red Hat OpenShift AI API endpoint.
            - Can also be set via the C(RHOAI_API_URL) environment variable.
        type: str
        required: true
    api_token:
        description:
            - Bearer token for authenticating to the RHOAI API.
            - Can also be set via the C(RHOAI_API_TOKEN) environment variable.
        type: str
        required: true
    validate_certs:
        description:
            - Whether to validate SSL certificates when connecting to the API.
        type: bool
        default: true
    wait:
        description:
            - Whether to wait for the resource to reach the desired state.
        type: bool
        default: true
    wait_timeout:
        description:
            - Maximum time in seconds to wait for the resource to reach the desired state.
        type: int
        default: 600
"""
