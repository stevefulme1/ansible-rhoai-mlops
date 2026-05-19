# data_residency_enforcement

Enforces data residency for AI workloads with geo-fencing policies, data locality constraints, cross-border audit logging, and sovereignty monitoring.

## Requirements

- `stevefulme1.rhoai_mlops` collection
- Red Hat OpenShift AI cluster with API access

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `rhoai_api_url` | `https://rhoai.example.com` | RHOAI API endpoint |
| `rhoai_api_token` | `""` | Bearer token for authentication |
| `rhoai_validate_certs` | `true` | Validate SSL certificates |
| `residency_policies` | `[]` | Geo-fencing policies to apply |
| `default_allowed_regions` | `[eu-west-1, eu-central-1, eu-north-1]` | Default allowed regions |
| `default_enforcement_mode` | `audit` | Mode: audit (log only) or enforce (block) |

See `defaults/main.yml` for all variables.

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - role: stevefulme1.rhoai_mlops.data_residency_enforcement
      vars:
        rhoai_api_url: "https://rhoai.cluster.local"
        rhoai_api_token: "{{ rhoai_token }}"
        residency_policies:
          - policy_name: eu-data-residency
            allowed_regions: ["eu-west-1", "eu-central-1"]
            data_classification: confidential
            enforcement_mode: enforce
```

## License

GPL-3.0-or-later
