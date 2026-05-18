# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing RHOAI pipeline run resources."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: pipeline_run_info
short_description: Get RHOAI pipeline run status
description:
    - List and get pipeline run resources in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    namespace:
        description:
            - Namespace to list runs in.
        type: str
        required: true
    run_id:
        description:
            - ID of a specific run to retrieve.
        type: str
    pipeline_id:
        description:
            - Filter runs by pipeline ID.
        type: str
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: Get pipeline run status
  stevefulme1.rhoai_mlops.pipeline_run_info:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
    namespace: "fraud-detection"
    run_id: "run-456"
"""

RETURN = r"""
pipeline_runs:
    description: Details of the pipeline run resources.
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
        run_id=dict(type="str"),
        pipeline_id=dict(type="str"),
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

    if params.get("run_id"):
        response = call_with_retry(client.get, f"/apis/v2beta1/runs/{params['run_id']}")
        if response.status_code == 404:
            module.exit_json(changed=False, pipeline_runs=[])
        elif response.status_code != 200:
            module.fail_json(msg=f"Failed to get pipeline run: {response.text}")
        module.exit_json(changed=False, pipeline_runs=[response.json()])
        return

    response = call_with_retry(client.get, "/apis/v2beta1/runs")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list pipeline runs: {response.text}")

    items = response.json().get("items", response.json().get("data", []))
    module.exit_json(changed=False, pipeline_runs=items)


if __name__ == "__main__":
    main()
