# -*- coding: utf-8 -*-
# Copyright (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing RHOAI model version resources."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: model_version
short_description: Register new model versions in RHOAI
description:
    - Create, update, and delete model version resources in Red Hat OpenShift AI.
    - Uses the RHOAI REST API with bearer token authentication.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    model_id:
        description:
            - ID of the registered model.
        type: str
        required: true
    version_name:
        description:
            - Name for this version.
        type: str
        required: true
    version_id:
        description:
            - ID of an existing version for update/delete.
        type: str
    description:
        description:
            - Description of this version.
        type: str
    artifact_uri:
        description:
            - URI to the model artifact (S3, PVC path).
        type: str
    labels:
        description:
            - Labels to apply to the version.
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
- name: Register a new model version
  stevefulme1.rhoai_mlops.model_version:
    api_url: "https://rhoai.example.com"
    api_token: "{ '{' } rhoai_token { '}' }"
    model_id: "model-123"
    version_name: "v2.0"
    artifact_uri: "s3://models/fraud-v2/model.onnx"
    state: "present"
"""

RETURN = r"""
model_version:
    description: Details of the model version resource.
    returned: On success.
    type: dict
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
        model_id=dict(type="str", required=True),
        version_name=dict(type="str", required=True),
        version_id=dict(type="str"),
        description=dict(type="str"),
        artifact_uri=dict(type="str"),
        labels=dict(type="dict"),
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
    if params.get("version_id"):
        response = call_with_retry(client.get, f"/apis/model-registry/v1/model_versions/{params['version_id']}")
        if response.status_code == 200:
            existing = response.json()
    elif params.get("version_name"):
        response = call_with_retry(client.get, "/apis/model-registry/v1/model_versions")
        if response.status_code == 200:
            for item in response.json().get("items", response.json().get("data", [])):
                if item.get("name") == params["version_name"]:
                    existing = item
                    break

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False)
        if module.check_mode:
            module.exit_json(changed=True)
        resource_id = existing.get("id", existing.get("name"))
        response = call_with_retry(client.delete, f"/apis/model-registry/v1/model_versions/{resource_id}")
        if response.status_code not in (200, 204, 404):
            module.fail_json(msg=f"Failed to delete model version: {response.text}")
        module.exit_json(changed=True)
        return

    payload = {k: v for k, v in params.items() if v is not None and k not in
                ("api_url", "api_token", "validate_certs", "wait", "wait_timeout",
                 "wait_interval", "state")}

    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True)
        response = call_with_retry(client.post, "/apis/model-registry/v1/model_versions", json=payload)
        if response.status_code not in (200, 201):
            module.fail_json(msg=f"Failed to create model version: {response.text}")
        result = response.json()
        if params.get("wait") and result.get("id"):
            result = wait_for_resource(
                module,
                lambda rid: call_with_retry(client.get, f"/apis/model-registry/v1/model_versions/{rid}").json(),
                result["id"],
                target_states=READY_STATES,
            )
        module.exit_json(changed=True, model_version=to_dict(result))
        return

    # Check if update is needed
    changed = False
    for key, value in payload.items():
        if existing.get(key) != value:
            changed = True
            break

    if not changed:
        module.exit_json(changed=False, model_version=to_dict(existing))
        return

    if module.check_mode:
        module.exit_json(changed=True)

    resource_id = existing.get("id", existing.get("name"))
    response = call_with_retry(client.patch, f"/apis/model-registry/v1/model_versions/{resource_id}", json=payload)
    if response.status_code not in (200, 202):
        module.fail_json(msg=f"Failed to update model version: {response.text}")

    result = response.json()
    if params.get("wait") and result.get("id"):
        result = wait_for_resource(
            module,
            lambda rid: call_with_retry(client.get, f"/apis/model-registry/v1/model_versions/{rid}").json(),
            result["id"],
            target_states=READY_STATES,
        )
    module.exit_json(changed=True, model_version=to_dict(result))


if __name__ == "__main__":
    main()
