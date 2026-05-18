# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for generating compliance audit reports."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: audit_report
short_description: Generate compliance audit reports
description:
    - Create, update, and delete compliance audit reports in Red Hat OpenShift AI.
    - Generates comprehensive or summary audit reports for EU AI Act compliance.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    report_name:
        description:
            - Name of the audit report.
        type: str
        required: true
    report_type:
        description:
            - Type of audit report to generate.
        type: str
        choices:
            - full
            - summary
            - delta
    date_range_start:
        description:
            - Start date for the audit period (ISO 8601).
        type: str
    date_range_end:
        description:
            - End date for the audit period (ISO 8601).
        type: str
    include_models:
        description:
            - Whether to include model details.
        type: bool
        default: true
    include_data_flows:
        description:
            - Whether to include data flow analysis.
        type: bool
        default: true
    output_format:
        description:
            - Output format for the report.
        type: str
        choices:
            - json
            - pdf
            - html
        default: json
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
- name: Create a audit report
  stevefulme1.rhoai_mlops.audit_report:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    report_name: "example-report-name"
    state: present

- name: Delete a audit report
  stevefulme1.rhoai_mlops.audit_report:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    report_name: "example-report-name"
    state: absent
"""

RETURN = r"""
audit_report:
    description: Details of the audit report resource.
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
        report_name=dict(type="str", required=True),
        report_type=dict(type="str", choices=['full', 'summary', 'delta']),
        date_range_start=dict(type="str"),
        date_range_end=dict(type="str"),
        include_models=dict(type="bool", default=True),
        include_data_flows=dict(type="bool", default=True),
        output_format=dict(type="str", choices=['json', 'pdf', 'html'], default="json"),
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
    if params.get("report_name"):
        response = call_with_retry(client.get, "/apis/compliance/v1/audit_reports")
        if response.status_code == 200:
            for item in response.json().get("items", response.json().get("data", [])):
                if item.get("report_name") == params["report_name"]:
                    existing = item
                    break

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False)
        if module.check_mode:
            module.exit_json(changed=True)
        resource_id = existing.get("id", existing.get("report_name"))
        response = call_with_retry(client.delete, f"/apis/compliance/v1/audit_reports/{resource_id}")
        if response.status_code not in (200, 204, 404):
            module.fail_json(msg=f"Failed to delete audit report: {response.text}")
        module.exit_json(changed=True)
        return

    payload = {k: v for k, v in params.items() if v is not None and k not in
               ('api_url', 'api_token', 'validate_certs', 'wait', 'wait_timeout', 'wait_interval', 'state')}

    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True)
        response = call_with_retry(client.post, "/apis/compliance/v1/audit_reports", json=payload)
        if response.status_code not in (200, 201):
            module.fail_json(msg=f"Failed to create audit report: {response.text}")
        result = response.json()
        if params.get("wait") and result.get("id"):
            result = wait_for_resource(
                module,
                lambda rid: call_with_retry(client.get, f"/apis/compliance/v1/audit_reports/{rid}").json(),
                result["id"],
                target_states=READY_STATES,
            )
        module.exit_json(changed=True, audit_report=to_dict(result))
        return

    # Check if update is needed
    changed = False
    for key, value in payload.items():
        if existing.get(key) != value:
            changed = True
            break

    if not changed:
        module.exit_json(changed=False, audit_report=to_dict(existing))
        return

    if module.check_mode:
        module.exit_json(changed=True)

    resource_id = existing.get("id", existing.get("report_name"))
    response = call_with_retry(client.patch, f"/apis/compliance/v1/audit_reports/{resource_id}", json=payload)
    if response.status_code not in (200, 202):
        module.fail_json(msg=f"Failed to update audit report: {response.text}")

    result = response.json()
    if params.get("wait") and result.get("id"):
        result = wait_for_resource(
            module,
            lambda rid: call_with_retry(client.get, f"/apis/compliance/v1/audit_reports/{rid}").json(),
            result["id"],
            target_states=READY_STATES,
        )
    module.exit_json(changed=True, audit_report=to_dict(result))


if __name__ == "__main__":
    main()
