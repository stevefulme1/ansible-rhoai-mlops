# model_drift_response

Automated drift response - detect, alert, rollback, and notify.

## Requirements

- Red Hat OpenShift AI cluster with API access
- Bearer token with appropriate permissions

## Role Variables

See `defaults/main.yml` for all configurable variables.

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - role: stevefulme1.rhoai_mlops.model_drift_response
      vars:
        rhoai_api_url: "https://rhoai.example.com"
        rhoai_api_token: "{{ vault_rhoai_token }}"
```

## License

GPL-3.0-or-later
