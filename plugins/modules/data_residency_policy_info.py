# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for querying data residency policies."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: data_residency_policy_info
short_description: Query data residency policies
description:
    - List and query data residency policies in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    policy_name:
        description:
            - Filter by policy name.
        type: str
    data_classification:
        description:
            - Filter by data classification.
        type: str
        choices:
            - public
            - internal
            - confidential
            - restricted
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: List all data residency policys
  stevefulme1.rhoai_mlops.data_residency_policy_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"

- name: Get a specific data residency policy
  stevefulme1.rhoai_mlops.data_residency_policy_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    policy_name: "example-policy-name"
"""

RETURN = r"""
policies:
    description: List of data residency policy resources.
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
        policy_name=dict(type="str"),
        data_classification=dict(type="str", choices=['public', 'internal', 'confidential', 'restricted']),
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

    response = call_with_retry(client.get, "/apis/sovereignty/v1/residency_policies")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list data residency policys: {response.text}")

    items = response.json().get("items", response.json().get("data", []))

    if params.get("policy_name"):
        items = [i for i in items if i.get("policy_name") == params["policy_name"]]

    if params.get("data_classification"):
        items = [i for i in items if i.get("data_classification") == params["data_classification"]]

    module.exit_json(changed=False, policies=items)


if __name__ == "__main__":
    main()
