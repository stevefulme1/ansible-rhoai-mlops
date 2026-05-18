# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing RHOAI model endpoint resources."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: model_endpoint_info
short_description: Get RHOAI model endpoint status and metrics
description:
    - List and get model endpoint resources in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    namespace:
        description:
            - Namespace to list endpoints in.
        type: str
        required: true
    name:
        description:
            - Name of a specific endpoint to retrieve.
        type: str
    include_metrics:
        description:
            - Include endpoint metrics (latency, throughput).
        type: bool
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: Get all endpoints
  stevefulme1.rhoai_mlops.model_endpoint_info:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
    namespace: "ml-serving"
- name: Get endpoint with metrics
  stevefulme1.rhoai_mlops.model_endpoint_info:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
    namespace: "ml-serving"
    name: "fraud-api"
    include_metrics: true
"""

RETURN = r"""
model_endpoints:
    description: Details of the model endpoint resources.
    returned: On success.
    type: list
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_common import (
    RHOAI_COMMON_ARGS,
    READY_STATES,
    DEAD_STATES,
    to_dict,
)
from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_auth import create_rhoai_client
from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_wait import (
    call_with_retry,
    wait_for_resource,
)


def get_module_args():
    module_args = dict(
        namespace=dict(type="str", required=True),
        name=dict(type="str"),
        include_metrics=dict(type="bool"),
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
        response = call_with_retry(client.get, f"/apis/v1beta1/endpoints/{params['name']}")
        if response.status_code == 404:
            module.exit_json(changed=False, model_endpoints=[])
        elif response.status_code != 200:
            module.fail_json(msg=f"Failed to get model endpoint: {response.text}")
        module.exit_json(changed=False, model_endpoints=[response.json()])
        return

    response = call_with_retry(client.get, "/apis/v1beta1/endpoints")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list model endpoints: {response.text}")

    items = response.json().get("items", response.json().get("data", []))
    module.exit_json(changed=False, model_endpoints=items)


if __name__ == "__main__":
    main()
