# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing RHOAI inference service resources."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: inference_service_info
short_description: List and get RHOAI InferenceService resources
description:
    - List and get inference service resources in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    namespace:
        description:
            - Namespace to list services in.
        type: str
        required: true
    name:
        description:
            - Name of a specific service to retrieve.
        type: str
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: List all inference services
  stevefulme1.rhoai_mlops.inference_service_info:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
    namespace: "ml-serving"
"""

RETURN = r"""
inference_services:
    description: Details of the inference service resources.
    returned: On success.
    type: list
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_common import (
    RHOAI_COMMON_ARGS,
)
from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_auth import create_rhoai_client
from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_wait import (
    call_with_retry,
)


def get_module_args():
    module_args = dict(
        namespace=dict(type="str", required=True),
        name=dict(type="str"),
    )
    module_args.update(RHOAI_COMMON_ARGS)
    return module_args


def main():
    module = AnsibleModule(
        argument_spec=get_module_args(),
        supports_check_mode=True,
    )

    client = create_rhoai_client(module)
    params = module.params

    if params.get("name"):
        response = call_with_retry(client.get, f"/apis/v1beta1/inferenceservices/{params['name']}")
        if response.status_code == 404:
            module.exit_json(changed=False, inference_services=[])
        elif response.status_code != 200:
            module.fail_json(msg=f"Failed to get inference service: {response.text}")
        module.exit_json(changed=False, inference_services=[response.json()])
        return

    response = call_with_retry(client.get, "/apis/v1beta1/inferenceservices")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list inference services: {response.text}")

    items = response.json().get("items", response.json().get("data", []))
    module.exit_json(changed=False, inference_services=items)


if __name__ == "__main__":
    main()
