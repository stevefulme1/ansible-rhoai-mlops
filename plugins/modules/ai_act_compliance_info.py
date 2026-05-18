# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for querying EU AI Act compliance assessments."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ai_act_compliance_info
short_description: Query EU AI Act compliance assessments
description:
    - List and query EU AI Act compliance assessments in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    assessment_name:
        description:
            - Filter by assessment name.
        type: str
    risk_category:
        description:
            - Filter by risk category.
        type: str
        choices:
            - minimal
            - limited
            - high
            - unacceptable
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: List all ai act compliances
  stevefulme1.rhoai_mlops.ai_act_compliance_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"

- name: Get a specific ai act compliance
  stevefulme1.rhoai_mlops.ai_act_compliance_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    assessment_name: "example-assessment-name"
"""

RETURN = r"""
assessments:
    description: List of ai act compliance resources.
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
        assessment_name=dict(type="str"),
        risk_category=dict(type="str", choices=['minimal', 'limited', 'high', 'unacceptable']),
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

    response = call_with_retry(client.get, "/apis/compliance/v1/assessments")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list ai act compliances: {response.text}")

    items = response.json().get("items", response.json().get("data", []))

    if params.get("assessment_name"):
        items = [i for i in items if i.get("assessment_name") == params["assessment_name"]]

    if params.get("risk_category"):
        items = [i for i in items if i.get("risk_category") == params["risk_category"]]

    module.exit_json(changed=False, assessments=items)


if __name__ == "__main__":
    main()
