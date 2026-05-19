# eu_ai_act_setup

Sets up EU AI Act compliance framework with risk classification, compliance assessments, audit logging, evidence collection, and compliance dashboards.

## Requirements

- `stevefulme1.rhoai_mlops` collection
- Red Hat OpenShift AI cluster with API access

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `rhoai_api_url` | `https://rhoai.example.com` | RHOAI API endpoint |
| `rhoai_api_token` | `""` | Bearer token for authentication |
| `rhoai_validate_certs` | `true` | Validate SSL certificates |
| `risk_classifications` | `[]` | Model risk classifications to create |
| `compliance_assessments` | `[]` | Compliance assessments to run |
| `default_assessor` | `automated-setup` | Default assessor name |

See `defaults/main.yml` for all variables.

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - role: stevefulme1.rhoai_mlops.eu_ai_act_setup
      vars:
        rhoai_api_url: "https://rhoai.cluster.local"
        rhoai_api_token: "{{ rhoai_token }}"
        risk_classifications:
          - model_name: fraud-detection-v1
            risk_level: high
            human_oversight_required: true
```

## License

GPL-3.0-or-later
