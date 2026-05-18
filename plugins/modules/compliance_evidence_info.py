# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for querying compliance evidence artifacts."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: compliance_evidence_info
short_description: Query compliance evidence artifacts
description:
    - List and query compliance evidence artifacts in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    evidence_name:
        description:
            - Filter by evidence name.
        type: str
    evidence_type:
        description:
            - Filter by evidence type.
        type: str
        choices:
            - documentation
            - test_result
            - audit_log
            - approval
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: List all compliance evidences
  stevefulme1.rhoai_mlops.compliance_evidence_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"

- name: Get a specific compliance evidence
  stevefulme1.rhoai_mlops.compliance_evidence_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    evidence_name: "example-evidence-name"
"""

RETURN = r"""
evidence_items:
    description: List of compliance evidence resources.
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
        evidence_name=dict(type="str"),
        evidence_type=dict(type="str", choices=['documentation', 'test_result', 'audit_log', 'approval']),
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

    response = call_with_retry(client.get, "/apis/compliance/v1/evidence")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list compliance evidences: {response.text}")

    items = response.json().get("items", response.json().get("data", []))

    if params.get("evidence_name"):
        items = [i for i in items if i.get("evidence_name") == params["evidence_name"]]

    if params.get("evidence_type"):
        items = [i for i in items if i.get("evidence_type") == params["evidence_type"]]

    module.exit_json(changed=False, evidence_items=items)


if __name__ == "__main__":
    main()
