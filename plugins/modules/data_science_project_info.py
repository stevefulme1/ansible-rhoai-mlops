# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing RHOAI data science project resources."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: data_science_project_info
short_description: List RHOAI data science projects
description:
    - List and get data science project resources in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    project_id:
        description:
            - ID of a specific project to retrieve.
        type: str
    name:
        description:
            - Filter projects by name.
        type: str
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: List all projects
  stevefulme1.rhoai_mlops.data_science_project_info:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
"""

RETURN = r"""
data_science_projects:
    description: Details of the data science project resources.
    returned: On success.
    type: list
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_common import (
    RHOAI_COMMON_ARGS,
    READY_STATES,
    DEAD_STATES,
    to_dict,
)
from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_auth import create_rhoai_client
from ansible_collections.stevefulme1.rhoai_mlops.plugins.module_utils.rhoai_wait import (
    call_with_retry,
    wait_for_resource,
)


def get_module_args():
    module_args = dict(
        project_id=dict(type="str"),
        name=dict(type="str"),
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

    if params.get("project_id"):
        response = call_with_retry(client.get, f"/apis/v1/namespaces/{params['project_id']}")
        if response.status_code == 404:
            module.exit_json(changed=False, data_science_projects=[])
        elif response.status_code != 200:
            module.fail_json(msg=f"Failed to get data science project: {response.text}")
        module.exit_json(changed=False, data_science_projects=[response.json()])
        return

    response = call_with_retry(client.get, "/apis/v1/namespaces")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list data science projects: {response.text}")

    items = response.json().get("items", response.json().get("data", []))
    module.exit_json(changed=False, data_science_projects=items)


if __name__ == "__main__":
    main()
