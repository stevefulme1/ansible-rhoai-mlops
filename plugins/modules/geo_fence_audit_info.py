# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for querying geo-fence audit results."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: geo_fence_audit_info
short_description: Query geo-fence audit results
description:
    - List and query geo-fence audit results in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    audit_name:
        description:
            - Filter by audit name.
        type: str
    policy_name:
        description:
            - Filter by policy name.
        type: str
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: List all geo fence audits
  stevefulme1.rhoai_mlops.geo_fence_audit_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"

- name: Get a specific geo fence audit
  stevefulme1.rhoai_mlops.geo_fence_audit_info:
    api_url: "https://rhoai.example.com"
    api_token: "{{ rhoai_token }}"
    audit_name: "example-audit-name"
"""

RETURN = r"""
audits:
    description: List of geo fence audit resources.
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
        audit_name=dict(type="str"),
        policy_name=dict(type="str"),
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

    response = call_with_retry(client.get, "/apis/sovereignty/v1/geo_fence_audits")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list geo fence audits: {response.text}")

    items = response.json().get("items", response.json().get("data", []))

    if params.get("audit_name"):
        items = [i for i in items if i.get("audit_name") == params["audit_name"]]

    if params.get("policy_name"):
        items = [i for i in items if i.get("policy_name") == params["policy_name"]]

    module.exit_json(changed=False, audits=items)


if __name__ == "__main__":
    main()
