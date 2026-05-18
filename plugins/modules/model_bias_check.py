# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing RHOAI bias check resources."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: model_bias_check
short_description: Run RHOAI model bias and fairness checks
description:
    - Trigger bias check resources in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    inference_service:
        description:
            - InferenceService to check.
        type: str
        required: true
    namespace:
        description:
            - Namespace of the service.
        type: str
        required: true
    protected_attributes:
        description:
            - List of protected attributes to check (e.g., gender, race).
        type: list
        required: true
    reference_dataset:
        description:
            - URI to the reference dataset.
        type: str
    metrics:
        description:
            - Bias metrics to compute (e.g., disparate_impact, equal_opportunity).
        type: list
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: Run a bias check
  stevefulme1.rhoai_mlops.model_bias_check:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
    inference_service: "fraud-detector"
    namespace: "ml-serving"
    protected_attributes:
      - "gender"
      - "age_group"
"""

RETURN = r"""
bias_check:
    description: Details of the bias check resource.
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
        inference_service=dict(type="str", required=True),
        namespace=dict(type="str", required=True),
        protected_attributes=dict(type="list", required=True, elements="str"),
        reference_dataset=dict(type="str"),
        metrics=dict(type="list", elements="str"),
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

    response = call_with_retry(client.post, "/apis/v1/bias-checks", json=payload)
    if response.status_code not in (200, 201, 202):
        module.fail_json(msg=f"Failed to create bias check: {response.text}")

    result = response.json()

    if params.get("wait") and result.get("id"):
        result = wait_for_resource(
            module,
            lambda rid: call_with_retry(client.get, f"/apis/v1/bias-checks/{rid}").json(),
            result["id"],
            target_states=READY_STATES,
        )

    module.exit_json(changed=True, bias_check=to_dict(result))


if __name__ == "__main__":
    main()
