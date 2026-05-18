# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for querying compliance audit reports."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: audit_report_info
short_description: Query compliance audit reports
description:
    - List and query compliance audit reports in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    report_name:
        description:
            - Filter by report name.
        type: str
    report_type:
        description:
            - Filter by report type.
        type: str
        choices:
            - full
            - summary
            - delta
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: List all audit reports
  stevefulme1.rhoai_mlops.audit_report_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"

- name: Get a specific audit report
  stevefulme1.rhoai_mlops.audit_report_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    report_name: "example-report-name"
"""

RETURN = r"""
audit_reports:
    description: List of audit report resources.
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
        report_name=dict(type="str"),
        report_type=dict(type="str", choices=['full', 'summary', 'delta']),
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

    response = call_with_retry(client.get, "/apis/compliance/v1/audit_reports")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list audit reports: {response.text}")

    items = response.json().get("items", response.json().get("data", []))

    if params.get("report_name"):
        items = [i for i in items if i.get("report_name") == params["report_name"]]

    if params.get("report_type"):
        items = [i for i in items if i.get("report_type") == params["report_type"]]

    module.exit_json(changed=False, audit_reports=items)


if __name__ == "__main__":
    main()
