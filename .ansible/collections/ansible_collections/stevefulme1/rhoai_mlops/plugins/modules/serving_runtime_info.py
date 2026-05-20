# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing RHOAI serving runtime resources."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: serving_runtime_info
short_description: List RHOAI serving runtimes
description:
    - List and get serving runtime resources in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    namespace:
        description:
            - Namespace to list runtimes in.
        type: str
        required: true
    name:
        description:
            - Name of a specific runtime to retrieve.
        type: str
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: List all serving runtimes
  stevefulme1.rhoai_mlops.serving_runtime_info:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
    namespace: "ml-serving"
"""

RETURN = r"""
serving_runtimes:
    description: Details of the serving runtime resources.
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
        response = call_with_retry(client.get, f"/apis/v1beta1/servingruntimes/{params['name']}")
        if response.status_code == 404:
            module.exit_json(changed=False, serving_runtimes=[])
        elif response.status_code != 200:
            module.fail_json(msg=f"Failed to get serving runtime: {response.text}")
        module.exit_json(changed=False, serving_runtimes=[response.json()])
        return

    response = call_with_retry(client.get, "/apis/v1beta1/servingruntimes")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list serving runtimes: {response.text}")

    items = response.json().get("items", response.json().get("data", []))
    module.exit_json(changed=False, serving_runtimes=items)


if __name__ == "__main__":
    main()
