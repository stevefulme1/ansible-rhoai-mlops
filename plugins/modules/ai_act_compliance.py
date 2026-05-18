# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing EU AI Act compliance assessments."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ai_act_compliance
short_description: Manage EU AI Act compliance assessments
description:
    - Create, update, and delete EU AI Act compliance assessments in Red Hat OpenShift AI.
    - Tracks risk classification, compliance status, and evidence for AI systems.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    assessment_name:
        description:
            - Name of the compliance assessment.
        type: str
        required: true
    ai_system_name:
        description:
            - Name of the AI system being assessed.
        type: str
    risk_category:
        description:
            - EU AI Act risk category for the system.
        type: str
        choices:
            - minimal
            - limited
            - high
            - unacceptable
    compliance_status:
        description:
            - Current compliance status.
        type: str
    evidence_urls:
        description:
            - List of URLs to supporting evidence artifacts.
        type: list
        elements: str
    assessor:
        description:
            - Name or ID of the person performing the assessment.
        type: str
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
- name: Create a ai act compliance
  stevefulme1.rhoai_mlops.ai_act_compliance:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    assessment_name: "example-assessment-name"
    state: present

- name: Delete a ai act compliance
  stevefulme1.rhoai_mlops.ai_act_compliance:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    assessment_name: "example-assessment-name"
    state: absent
"""

RETURN = r"""
assessment:
    description: Details of the ai act compliance resource.
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
        assessment_name=dict(type="str", required=True),
        ai_system_name=dict(type="str"),
        risk_category=dict(type="str", choices=['minimal', 'limited', 'high', 'unacceptable']),
        compliance_status=dict(type="str"),
        evidence_urls=dict(type="list", elements="str"),
        assessor=dict(type="str"),
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
    if params.get("assessment_name"):
        response = call_with_retry(client.get, "/apis/compliance/v1/assessments")
        if response.status_code == 200:
            for item in response.json().get("items", response.json().get("data", [])):
                if item.get("assessment_name") == params["assessment_name"]:
                    existing = item
                    break

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False)
        if module.check_mode:
            module.exit_json(changed=True)
        resource_id = existing.get("id", existing.get("assessment_name"))
        response = call_with_retry(client.delete, f"/apis/compliance/v1/assessments/{resource_id}")
        if response.status_code not in (200, 204, 404):
            module.fail_json(msg=f"Failed to delete ai act compliance: {response.text}")
        module.exit_json(changed=True)
        return

    payload = {k: v for k, v in params.items() if v is not None and k not in
               ('api_url', 'api_token', 'validate_certs', 'wait', 'wait_timeout', 'wait_interval', 'state')}

    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True)
        response = call_with_retry(client.post, "/apis/compliance/v1/assessments", json=payload)
        if response.status_code not in (200, 201):
            module.fail_json(msg=f"Failed to create ai act compliance: {response.text}")
        result = response.json()
        if params.get("wait") and result.get("id"):
            result = wait_for_resource(
                module,
                lambda rid: call_with_retry(client.get, f"/apis/compliance/v1/assessments/{rid}").json(),
                result["id"],
                target_states=READY_STATES,
            )
        module.exit_json(changed=True, assessment=to_dict(result))
        return

    # Check if update is needed
    changed = False
    for key, value in payload.items():
        if existing.get(key) != value:
            changed = True
            break

    if not changed:
        module.exit_json(changed=False, assessment=to_dict(existing))
        return

    if module.check_mode:
        module.exit_json(changed=True)

    resource_id = existing.get("id", existing.get("assessment_name"))
    response = call_with_retry(client.patch, f"/apis/compliance/v1/assessments/{resource_id}", json=payload)
    if response.status_code not in (200, 202):
        module.fail_json(msg=f"Failed to update ai act compliance: {response.text}")

    result = response.json()
    if params.get("wait") and result.get("id"):
        result = wait_for_resource(
            module,
            lambda rid: call_with_retry(client.get, f"/apis/compliance/v1/assessments/{rid}").json(),
            result["id"],
            target_states=READY_STATES,
        )
    module.exit_json(changed=True, assessment=to_dict(result))


if __name__ == "__main__":
    main()
