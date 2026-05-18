# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for querying data sovereignty reports."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: data_sovereignty_report_info
short_description: Query data sovereignty reports
description:
    - List and query data sovereignty compliance reports in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    report_name:
        description:
            - Filter by report name.
        type: str
    jurisdiction:
        description:
            - Filter by jurisdiction.
        type: str
        choices:
            - eu
            - us
            - apac
            - custom
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: List all data sovereignty reports
  stevefulme1.rhoai_mlops.data_sovereignty_report_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"

- name: Get a specific data sovereignty report
  stevefulme1.rhoai_mlops.data_sovereignty_report_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    report_name: "example-report-name"
"""

RETURN = r"""
reports:
    description: List of data sovereignty report resources.
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
        jurisdiction=dict(type="str", choices=['eu', 'us', 'apac', 'custom']),
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

    response = call_with_retry(client.get, "/apis/sovereignty/v1/reports")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list data sovereignty reports: {response.text}")

    items = response.json().get("items", response.json().get("data", []))

    if params.get("report_name"):
        items = [i for i in items if i.get("report_name") == params["report_name"]]

    if params.get("jurisdiction"):
        items = [i for i in items if i.get("jurisdiction") == params["jurisdiction"]]

    module.exit_json(changed=False, reports=items)


if __name__ == "__main__":
    main()
