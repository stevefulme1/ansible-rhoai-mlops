# rhoai_webhook_config

Configure RHOAI to push model lifecycle events to EDA controller webhook.

## Requirements

- Red Hat OpenShift AI cluster with API access
- Bearer token with appropriate permissions

## Role Variables

See `defaults/main.yml` for all configurable variables.

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - role: stevefulme1.rhoai_mlops.rhoai_webhook_config
      vars:
        rhoai_api_url: "https://rhoai.example.com"
        rhoai_api_token: "{{ vault_rhoai_token }}"
```

## License

GPL-3.0-or-later
