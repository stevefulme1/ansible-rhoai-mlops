# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for retrieving RHOAI pipeline information."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: pipeline_info
short_description: Get RHOAI ML pipeline information
description:
    - List and get pipeline resources in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    namespace:
        description:
            - Namespace to list pipelines in.
        type: str
        required: true
    pipeline_id:
        description:
            - ID of a specific pipeline to retrieve.
        type: str
    name:
        description:
            - Filter pipelines by name.
        type: str
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: List all pipelines in a namespace
  stevefulme1.rhoai_mlops.pipeline_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    namespace: "fraud-detection"
  register: result

- name: Get a specific pipeline
  stevefulme1.rhoai_mlops.pipeline_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    namespace: "fraud-detection"
    pipeline_id: "pipeline-123"
  register: result

- name: Get pipelines by name
  stevefulme1.rhoai_mlops.pipeline_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    namespace: "fraud-detection"
    name: "training-pipeline"
  register: result
"""

RETURN = r"""
pipelines:
    description: Details of the pipeline resources.
    returned: On success.
    type: list
    elements: dict
    sample:
        - id: "pipeline-123"
          name: "training-pipeline"
          namespace: "fraud-detection"
          created_at: "2026-01-15T10:30:00Z"
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
        pipeline_id=dict(type="str"),
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

    if params.get("pipeline_id"):
        response = call_with_retry(client.get, f"/apis/v2beta1/pipelines/{params['pipeline_id']}")
        if response.status_code == 404:
            module.exit_json(changed=False, pipelines=[])
        elif response.status_code != 200:
            module.fail_json(msg=f"Failed to get pipeline: {response.text}")
        module.exit_json(changed=False, pipelines=[response.json()])
        return

    response = call_with_retry(client.get, "/apis/v2beta1/pipelines")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list pipelines: {response.text}")

    items = response.json().get("items", response.json().get("data", []))

    # Filter by name if specified
    if params.get("name"):
        items = [p for p in items if p.get("name") == params["name"]]

    # Filter by namespace
    items = [p for p in items if p.get("namespace") == params["namespace"]]

    module.exit_json(changed=False, pipelines=items)


if __name__ == "__main__":
    main()
