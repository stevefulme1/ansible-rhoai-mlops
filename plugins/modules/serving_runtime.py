# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing RHOAI serving runtime resources."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: serving_runtime
short_description: Manage RHOAI serving runtimes
description:
    - Create, update, and delete serving runtime resources in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    name:
        description:
            - Name of the serving runtime.
        type: str
        required: true
    namespace:
        description:
            - Namespace for the runtime.
        type: str
        required: true
    runtime_id:
        description:
            - ID of an existing runtime for update/delete.
        type: str
    runtime_type:
        description:
            - Type of runtime (vllm, triton, tgis, caikit, openvino).
        type: str
    image:
        description:
            - Container image for the runtime.
        type: str
    supported_formats:
        description:
            - List of supported model formats.
        type: list
    resources:
        description:
            - Resource requests and limits.
        type: dict
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
- name: Create a serving runtime
  stevefulme1.rhoai_mlops.serving_runtime:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
    name: "vllm-runtime"
    namespace: "ml-serving"
    runtime_type: "vllm"
    state: "present"
"""

RETURN = r"""
serving_runtime:
    description: Details of the serving runtime resource.
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
        name=dict(type="str", required=True),
        namespace=dict(type="str", required=True),
        runtime_id=dict(type="str"),
        runtime_type=dict(type="str"),
        image=dict(type="str"),
        supported_formats=dict(type="list"),
        resources=dict(type="dict"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
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
    if params.get("runtime_id"):
        response = call_with_retry(client.get, f"/apis/v1beta1/servingruntimes/{params['runtime_id']}")
        if response.status_code == 200:
            existing = response.json()
    elif params.get("name"):
        response = call_with_retry(client.get, "/apis/v1beta1/servingruntimes")
        if response.status_code == 200:
            for item in response.json().get("items", response.json().get("data", [])):
                if item.get("name") == params["name"]:
                    existing = item
                    break

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False)
        if module.check_mode:
            module.exit_json(changed=True)
        resource_id = existing.get("id", existing.get("name"))
        response = call_with_retry(client.delete, f"/apis/v1beta1/servingruntimes/{resource_id}")
        if response.status_code not in (200, 204, 404):
            module.fail_json(msg=f"Failed to delete serving runtime: {response.text}")
        module.exit_json(changed=True)
        return

    payload = {k: v for k, v in params.items() if v is not None and k not in
               ("api_url", "api_token", "validate_certs", "wait", "wait_timeout",
                "wait_interval", "state")}

    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True)
        response = call_with_retry(client.post, "/apis/v1beta1/servingruntimes", json=payload)
        if response.status_code not in (200, 201):
            module.fail_json(msg=f"Failed to create serving runtime: {response.text}")
        result = response.json()
        if params.get("wait") and result.get("id"):
            result = wait_for_resource(
                module,
                lambda rid: call_with_retry(client.get, f"/apis/v1beta1/servingruntimes/{rid}").json(),
                result["id"],
                target_states=READY_STATES,
            )
        module.exit_json(changed=True, serving_runtime=to_dict(result))
        return

    # Check if update is needed
    changed = False
    for key, value in payload.items():
        if existing.get(key) != value:
            changed = True
            break

    if not changed:
        module.exit_json(changed=False, serving_runtime=to_dict(existing))
        return

    if module.check_mode:
        module.exit_json(changed=True)

    resource_id = existing.get("id", existing.get("name"))
    response = call_with_retry(client.patch, f"/apis/v1beta1/servingruntimes/{resource_id}", json=payload)
    if response.status_code not in (200, 202):
        module.fail_json(msg=f"Failed to update serving runtime: {response.text}")

    result = response.json()
    if params.get("wait") and result.get("id"):
        result = wait_for_resource(
            module,
            lambda rid: call_with_retry(client.get, f"/apis/v1beta1/servingruntimes/{rid}").json(),
            result["id"],
            target_states=READY_STATES,
        )
    module.exit_json(changed=True, serving_runtime=to_dict(result))


if __name__ == "__main__":
    main()
