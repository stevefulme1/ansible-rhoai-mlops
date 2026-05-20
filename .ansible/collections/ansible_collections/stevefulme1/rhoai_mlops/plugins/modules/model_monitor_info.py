# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing RHOAI model monitor resources."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: model_monitor_info
short_description: Get RHOAI model monitoring status and alerts
description:
    - List and get model monitor resources in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    namespace:
        description:
            - Namespace to list monitors in.
        type: str
        required: true
    monitor_id:
        description:
            - ID of a specific monitor to retrieve.
        type: str
    include_alerts:
        description:
            - Include active alerts in the response.
        type: bool
extends_documentation_fragment:
    - stevefulme1.rhoai_mlops.rhoai
requirements:
    - "python >= 3.10"
    - "requests"
"""

EXAMPLES = r"""
- name: Get monitoring status
  stevefulme1.rhoai_mlops.model_monitor_info:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
    namespace: "ml-serving"
- name: Get monitor with alerts
  stevefulme1.rhoai_mlops.model_monitor_info:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
    namespace: "ml-serving"
    monitor_id: "mon-123"
    include_alerts: true
"""

RETURN = r"""
model_monitors:
    description: Details of the model monitor resources.
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
        namespace=dict(type="str", required=True),
        monitor_id=dict(type="str"),
        include_alerts=dict(type="bool"),
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

    if params.get("monitor_id"):
        response = call_with_retry(client.get, f"/apis/v1/monitors/{params['monitor_id']}")
        if response.status_code == 404:
            module.exit_json(changed=False, model_monitors=[])
        elif response.status_code != 200:
            module.fail_json(msg=f"Failed to get model monitor: {response.text}")
        module.exit_json(changed=False, model_monitors=[response.json()])
        return

    response = call_with_retry(client.get, "/apis/v1/monitors")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to list model monitors: {response.text}")

    items = response.json().get("items", response.json().get("data", []))
    module.exit_json(changed=False, model_monitors=items)


if __name__ == "__main__":
    main()
