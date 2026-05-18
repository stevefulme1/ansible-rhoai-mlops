# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for auditing data flows against geo-fencing rules."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: geo_fence_audit
short_description: Audit data flows against geo-fencing rules
description:
    - Create, update, and delete geo-fence audit scans in Red Hat OpenShift AI.
    - Audits data flows against geographic fencing policies for compliance.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    audit_name:
        description:
            - Name of the geo-fence audit.
        type: str
        required: true
    policy_name:
        description:
            - Name of the data residency policy to audit against.
        type: str
    scan_scope:
        description:
            - Scope of the audit scan.
        type: str
        choices:
            - all
            - training_data
            - model_artifacts
            - inference_logs
        default: all
    report_violations:
        description:
            - Whether to report policy violations.
        type: bool
        default: true
    auto_remediate:
        description:
            - Whether to automatically remediate violations.
        type: bool
        default: false
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
- name: Create a geo fence audit
  stevefulme1.rhoai_mlops.geo_fence_audit:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    audit_name: "example-audit-name"
    state: present

- name: Delete a geo fence audit
  stevefulme1.rhoai_mlops.geo_fence_audit:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    audit_name: "example-audit-name"
    state: absent
"""

RETURN = r"""
audit:
    description: Details of the geo fence audit resource.
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
        audit_name=dict(type="str", required=True),
        policy_name=dict(type="str"),
        scan_scope=dict(type="str", choices=['all', 'training_data', 'model_artifacts', 'inference_logs'], default="all"),
        report_violations=dict(type="bool", default=True),
        auto_remediate=dict(type="bool", default=False),
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
    if params.get("audit_name"):
        response = call_with_retry(client.get, "/apis/sovereignty/v1/geo_fence_audits")
        if response.status_code == 200:
            for item in response.json().get("items", response.json().get("data", [])):
                if item.get("audit_name") == params["audit_name"]:
                    existing = item
                    break

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False)
        if module.check_mode:
            module.exit_json(changed=True)
        resource_id = existing.get("id", existing.get("audit_name"))
        response = call_with_retry(client.delete, f"/apis/sovereignty/v1/geo_fence_audits/{resource_id}")
        if response.status_code not in (200, 204, 404):
            module.fail_json(msg=f"Failed to delete geo fence audit: {response.text}")
        module.exit_json(changed=True)
        return

    payload = {k: v for k, v in params.items() if v is not None and k not in
               ('api_url', 'api_token', 'validate_certs', 'wait', 'wait_timeout', 'wait_interval', 'state')}

    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True)
        response = call_with_retry(client.post, "/apis/sovereignty/v1/geo_fence_audits", json=payload)
        if response.status_code not in (200, 201):
            module.fail_json(msg=f"Failed to create geo fence audit: {response.text}")
        result = response.json()
        if params.get("wait") and result.get("id"):
            result = wait_for_resource(
                module,
                lambda rid: call_with_retry(client.get, f"/apis/sovereignty/v1/geo_fence_audits/{rid}").json(),
                result["id"],
                target_states=READY_STATES,
            )
        module.exit_json(changed=True, audit=to_dict(result))
        return

    # Check if update is needed
    changed = False
    for key, value in payload.items():
        if existing.get(key) != value:
            changed = True
            break

    if not changed:
        module.exit_json(changed=False, audit=to_dict(existing))
        return

    if module.check_mode:
        module.exit_json(changed=True)

    resource_id = existing.get("id", existing.get("audit_name"))
    response = call_with_retry(client.patch, f"/apis/sovereignty/v1/geo_fence_audits/{resource_id}", json=payload)
    if response.status_code not in (200, 202):
        module.fail_json(msg=f"Failed to update geo fence audit: {response.text}")

    result = response.json()
    if params.get("wait") and result.get("id"):
        result = wait_for_resource(
            module,
            lambda rid: call_with_retry(client.get, f"/apis/sovereignty/v1/geo_fence_audits/{rid}").json(),
            result["id"],
            target_states=READY_STATES,
        )
    module.exit_json(changed=True, audit=to_dict(result))


if __name__ == "__main__":
    main()
