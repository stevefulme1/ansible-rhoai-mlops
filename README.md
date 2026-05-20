> **EXPERIMENTAL** - This collection is a proof of concept and is not production ready.
> Modules may use placeholder API endpoints and have not been validated against real infrastructure.
> Do not use in production environments.

# Ansible Collection: stevefulme1.rhoai_mlops

Ansible Collection for Red Hat OpenShift AI (RHOAI) MLOps event-driven automation.

Provides modules for managing model registry, model serving, data science projects,
ML pipelines, model monitoring, EU AI Act compliance, and sovereign data residency
on OpenShift AI. Includes EDA event source plugins and rulebooks for event-driven
ML operations workflows.

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

### EU AI Act Compliance
- `ai_act_compliance` - Manage EU AI Act compliance assessments
- `ai_act_compliance_info` - Query compliance assessments
- `model_risk_classification` - Classify AI models per EU AI Act risk tiers
- `model_risk_classification_info` - Query model risk classifications
- `audit_report` - Generate compliance audit reports
- `audit_report_info` - Query existing audit reports
- `compliance_evidence` - Manage compliance evidence artifacts
- `compliance_evidence_info` - Query evidence artifacts

### Sovereign Data Residency
- `data_residency_policy` - Manage data residency policies for AI workloads
- `data_residency_policy_info` - Query data residency policies
- `geo_fence_audit` - Audit data flows against geo-fencing rules
- `geo_fence_audit_info` - Query geo-fence audit results
- `data_sovereignty_report` - Generate data sovereignty compliance reports
- `data_sovereignty_report_info` - Query data sovereignty reports

## EDA Event Sources

- `model_registry` - Watch model registry for lifecycle events
- `model_monitoring` - Stream model monitoring alerts
- `pipeline_events` - Watch pipeline runs for completion and failure events

## Roles

- `rhoai_webhook_config` - Configure RHOAI webhook integration with EDA controller
- `model_drift_response` - Automated drift response workflow
- `model_canary_deploy` - Canary deployment with traffic splitting
- `training_job_recovery` - Training job checkpoint recovery
- `eu_ai_act_setup` - Set up EU AI Act compliance framework (risk classification, audit logging, evidence collection, compliance dashboard)
- `data_residency_enforcement` - Enforce data residency (geo-fencing policies, data locality constraints, cross-border audit logging, sovereignty monitoring)

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
