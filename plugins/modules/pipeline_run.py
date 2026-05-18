# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing RHOAI pipeline run resources."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: pipeline_run
short_description: Trigger RHOAI pipeline runs
description:
    - Trigger pipeline run resources in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    pipeline_id:
        description:
            - ID of the pipeline to run.
        type: str
        required: true
    namespace:
        description:
            - Namespace for the run.
        type: str
        required: true
    run_name:
        description:
            - Name for this run.
        type: str
    parameters:
        description:
            - Pipeline parameters for this run.
        type: dict
    experiment_id:
        description:
            - ID of the experiment to associate with.
        type: str
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: Trigger a pipeline run
  stevefulme1.rhoai_mlops.pipeline_run:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
    pipeline_id: "pipeline-123"
    namespace: "fraud-detection"
    run_name: "training-run-42"
    parameters:
      learning_rate: "0.001"
      epochs: "50"
"""

RETURN = r"""
pipeline_run:
    description: Details of the pipeline run resource.
    returned: On success.
    type: dict
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_common import (
    RHOAI_COMMON_ARGS,
    READY_STATES,
    to_dict,
)
from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_auth import create_rhoai_client
from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_wait import (
    call_with_retry,
    wait_for_resource,
)


def get_module_args():
    module_args = dict(
        pipeline_id=dict(type="str", required=True),
        namespace=dict(type="str", required=True),
        run_name=dict(type="str"),
        parameters=dict(type="dict"),
        experiment_id=dict(type="str"),
    )
    module_args.update(RHOAI_COMMON_ARGS)
    return module_args


def main():
    module = AnsibleModule(
        argument_spec=get_module_args(),
        supports_check_mode=True,
    )

    if module.check_mode:
        module.exit_json(changed=True)

    client = create_rhoai_client(module)
    params = module.params

    payload = {k: v for k, v in params.items() if v is not None and k not in
                ("api_url", "api_token", "validate_certs", "wait", "wait_timeout", "wait_interval")}

    response = call_with_retry(client.post, "/apis/v2beta1/runs", json=payload)
    if response.status_code not in (200, 201, 202):
        module.fail_json(msg=f"Failed to create pipeline run: {response.text}")

    result = response.json()

    if params.get("wait") and result.get("id"):
        result = wait_for_resource(
            module,
            lambda rid: call_with_retry(client.get, f"/apis/v2beta1/runs/{rid}").json(),
            result["id"],
            target_states=READY_STATES,
        )

    module.exit_json(changed=True, pipeline_run=to_dict(result))


if __name__ == "__main__":
    main()
