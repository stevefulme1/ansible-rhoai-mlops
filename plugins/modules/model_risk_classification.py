# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for classifying AI models per EU AI Act risk tiers."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: model_risk_classification
short_description: Classify AI models per EU AI Act risk tiers
description:
    - Create, update, and delete AI model risk classifications in Red Hat OpenShift AI.
    - Assigns EU AI Act risk tier classification to ML models.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    model_name:
        description:
            - Name of the AI model being classified.
        type: str
        required: true
    risk_level:
        description:
            - EU AI Act risk tier.
        type: str
        choices:
            - minimal
            - limited
            - high
            - unacceptable
    classification_reason:
        description:
            - Rationale for the risk classification.
        type: str
    data_categories:
        description:
            - Categories of data processed by the model.
        type: list
        elements: str
    intended_use:
        description:
            - Intended use description for the AI model.
        type: str
    human_oversight_required:
        description:
            - Whether human oversight is required.
        type: bool
    state:
        description:
            - Desired state.
        type: str
        choices:
            - present
            - absent
        default: present
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: Create a model risk classification
  stevefulme1.rhoai_mlops.model_risk_classification:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    model_name: "example-model-name"
    state: present

- name: Delete a model risk classification
  stevefulme1.rhoai_mlops.model_risk_classification:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    model_name: "example-model-name"
    state: absent
"""

RETURN = r"""
classification:
    description: Details of the model risk classification resource.
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
        model_name=dict(type="str", required=True),
        risk_level=dict(type="str", choices=['minimal', 'limited', 'high', 'unacceptable']),
        classification_reason=dict(type="str"),
        data_categories=dict(type="list", elements="str"),
        intended_use=dict(type="str"),
        human_oversight_required=dict(type="bool"),
        state=dict(type="str", choices=['present', 'absent'], default="present"),
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
    state = params.get("state", "present")

    existing = None
    if params.get("model_name"):
        response = call_with_retry(client.get, "/apis/compliance/v1/risk_classifications")
        if response.status_code == 200:
            for item in response.json().get("items", response.json().get("data", [])):
                if item.get("model_name") == params["model_name"]:
                    existing = item
                    break

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False)
        if module.check_mode:
            module.exit_json(changed=True)
        resource_id = existing.get("id", existing.get("model_name"))
        response = call_with_retry(client.delete, f"/apis/compliance/v1/risk_classifications/{resource_id}")
        if response.status_code not in (200, 204, 404):
            module.fail_json(msg=f"Failed to delete model risk classification: {response.text}")
        module.exit_json(changed=True)
        return

    payload = {k: v for k, v in params.items() if v is not None and k not in
               ('api_url', 'api_token', 'validate_certs', 'wait', 'wait_timeout', 'wait_interval', 'state')}

    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True)
        response = call_with_retry(client.post, "/apis/compliance/v1/risk_classifications", json=payload)
        if response.status_code not in (200, 201):
            module.fail_json(msg=f"Failed to create model risk classification: {response.text}")
        result = response.json()
        if params.get("wait") and result.get("id"):
            result = wait_for_resource(
                module,
                lambda rid: call_with_retry(client.get, f"/apis/compliance/v1/risk_classifications/{rid}").json(),
                result["id"],
                target_states=READY_STATES,
            )
        module.exit_json(changed=True, classification=to_dict(result))
        return

    # Check if update is needed
    changed = False
    for key, value in payload.items():
        if existing.get(key) != value:
            changed = True
            break

    if not changed:
        module.exit_json(changed=False, classification=to_dict(existing))
        return

    if module.check_mode:
        module.exit_json(changed=True)

    resource_id = existing.get("id", existing.get("model_name"))
    response = call_with_retry(client.patch, f"/apis/compliance/v1/risk_classifications/{resource_id}", json=payload)
    if response.status_code not in (200, 202):
        module.fail_json(msg=f"Failed to update model risk classification: {response.text}")

    result = response.json()
    if params.get("wait") and result.get("id"):
        result = wait_for_resource(
            module,
            lambda rid: call_with_retry(client.get, f"/apis/compliance/v1/risk_classifications/{rid}").json(),
            result["id"],
            target_states=READY_STATES,
        )
    module.exit_json(changed=True, classification=to_dict(result))


if __name__ == "__main__":
    main()
