# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for querying AI model risk classifications."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: model_risk_classification_info
short_description: Query AI model risk classifications
description:
    - List and query AI model risk classifications in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    model_name:
        description:
            - Filter by model name.
        type: str
    risk_level:
        description:
            - Filter by risk level.
        type: str
        choices:
            - minimal
            - limited
            - high
            - unacceptable
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: List all model risk classifications
  stevefulme1.rhoai_mlops.model_risk_classification_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"

- name: Get a specific model risk classification
  stevefulme1.rhoai_mlops.model_risk_classification_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    model_name: "example-model-name"
"""

RETURN = r"""
classifications:
    description: List of model risk classification resources.
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
        model_name=dict(type="str"),
        risk_level=dict(type="str", choices=['minimal', 'limited', 'high', 'unacceptable']),
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

    response = call_with_retry(client.get, "/apis/compliance/v1/risk_classifications")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list model risk classifications: {response.text}")

    items = response.json().get("items", response.json().get("data", []))

    if params.get("model_name"):
        items = [i for i in items if i.get("model_name") == params["model_name"]]

    if params.get("risk_level"):
        items = [i for i in items if i.get("risk_level") == params["risk_level"]]

    module.exit_json(changed=False, classifications=items)


if __name__ == "__main__":
    main()
