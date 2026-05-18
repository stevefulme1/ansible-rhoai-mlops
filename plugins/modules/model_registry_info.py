# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing RHOAI registered model resources."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: model_registry_info
short_description: List and get RHOAI registered models
description:
    - List and get registered model resources in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    model_id:
        description:
            - ID of a specific registered model to retrieve.
        type: str
    name:
        description:
            - Filter models by name.
        type: str
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: List all registered models
  stevefulme1.rhoai_mlops.model_registry_info:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
- name: Get a specific model
  stevefulme1.rhoai_mlops.model_registry_info:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
    model_id: "model-123"
"""

RETURN = r"""
registered_models:
    description: Details of the registered model resources.
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
        model_id=dict(type="str"),
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

    if params.get("model_id"):
        response = call_with_retry(client.get, f"/apis/model-registry/v1/registered_models/{params['model_id']}")
        if response.status_code == 404:
            module.exit_json(changed=False, registered_models=[])
        elif response.status_code != 200:
            module.fail_json(msg=f"Failed to get registered model: {response.text}")
        module.exit_json(changed=False, registered_models=[response.json()])
        return

    response = call_with_retry(client.get, "/apis/model-registry/v1/registered_models")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list registered models: {response.text}")

    items = response.json().get("items", response.json().get("data", []))
    module.exit_json(changed=False, registered_models=items)


if __name__ == "__main__":
    main()
