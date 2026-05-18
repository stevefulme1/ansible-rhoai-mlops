# Ansible Collection: stevefulme1.rhoai_mlops

Ansible Collection for Red Hat OpenShift AI (RHOAI) MLOps event-driven automation.

Provides modules for managing model registry, model serving, data science projects,
ML pipelines, and model monitoring on OpenShift AI. Includes EDA event source plugins
and rulebooks for event-driven ML operations workflows.

## Requirements

- Ansible Core >= 2.16
- Python >= 3.10
- Access to a Red Hat OpenShift AI cluster with API endpoint and bearer token

## Installation

```bash
ansible-galaxy collection install stevefulme1.rhoai_mlops
```

## Modules

### Model Registry
- `model_registry` - Create, update, and delete model registry entries
- `model_registry_info` - List and get registered models
- `model_version` - Register new model versions
- `model_version_info` - List model versions

### Model Serving
- `inference_service` - Manage InferenceService resources (KServe)
- `inference_service_info` - List and get inference services
- `serving_runtime` - Manage serving runtimes (vLLM, TensorRT-LLM, Triton)
- `serving_runtime_info` - List serving runtimes
- `model_endpoint` - Manage model serving endpoints
- `model_endpoint_info` - Get endpoint status and metrics

### Data Science
- `data_science_project` - Manage RHOAI data science projects
- `data_science_project_info` - List projects
- `notebook` - Manage Jupyter notebooks
- `notebook_info` - List notebooks
- `pipeline` - Manage ML pipelines (Kubeflow Pipelines)
- `pipeline_run` - Trigger and manage pipeline runs
- `pipeline_run_info` - Get pipeline run status

### Monitoring
- `model_monitor` - Configure model monitoring and drift detection
- `model_monitor_info` - Get monitoring status and alerts
- `model_bias_check` - Run model bias and fairness checks

## EDA Event Sources

- `model_registry` - Watch model registry for lifecycle events
- `model_monitoring` - Stream model monitoring alerts
- `pipeline_events` - Watch pipeline runs for completion and failure events

## Roles

- `rhoai_webhook_config` - Configure RHOAI webhook integration with EDA controller
- `model_drift_response` - Automated drift response workflow
- `model_canary_deploy` - Canary deployment with traffic splitting
- `training_job_recovery` - Training job checkpoint recovery

## EDA Rulebooks

- `model_drift_rollback.yml` - Rollback on drift detection
- `training_failure_recovery.yml` - Retry failed training from checkpoint
- `model_promotion.yml` - Promote canary to production on passing metrics
- `gpu_health_remediation.yml` - Migrate workloads on GPU errors

## Authentication

All modules require:
- `api_url` - RHOAI/OpenShift API URL
- `api_token` - Bearer token for authentication
- `validate_certs` - Whether to validate SSL certificates (default: true)

## License

GPL-3.0-or-later
