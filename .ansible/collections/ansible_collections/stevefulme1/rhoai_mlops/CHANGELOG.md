# Changelog

## 0.0.1 (unreleased)

### Removed

- 15 modules with fabricated API endpoints removed:
  - `ai_act_compliance[_info]` - called nonexistent `/apis/compliance/v1/assessments`
  - `audit_report[_info]` - called nonexistent `/apis/compliance/v1/audit_reports`
  - `compliance_evidence[_info]` - called nonexistent `/apis/compliance/v1/evidence`
  - `data_residency_policy[_info]` - called nonexistent `/apis/sovereignty/v1/residency_policies`
  - `data_sovereignty_report[_info]` - called nonexistent `/apis/sovereignty/v1/reports`
  - `geo_fence_audit[_info]` - called nonexistent `/apis/sovereignty/v1/geo_fence_audits`
  - `model_bias_check` - called nonexistent `/apis/v1/bias-checks`
  - `model_risk_classification[_info]` - called nonexistent `/apis/compliance/v1/risk_classifications`
- Role `eu_ai_act_setup` removed (used deleted modules)
- Role `data_residency_enforcement` removed (used deleted modules)
- All unit tests for deleted modules removed

### Retained (19 modules with real RHOAI APIs)

- `data_science_project[_info]` - /apis/v1/namespaces
- `inference_service[_info]` - /apis/v1beta1/inferenceservices (KServe)
- `model_registry[_info]` - /apis/model-registry/v1/registered_models
- `model_version[_info]` - /apis/model-registry/v1/model_versions
- `notebook[_info]` - /apis/v1/notebooks
- `pipeline[_info]` - /apis/v2beta1/pipelines (Kubeflow)
- `pipeline_run[_info]` - /apis/v2beta1/runs
- `serving_runtime[_info]` - /apis/v1beta1/servingruntimes
- `model_endpoint[_info]` - /apis/v1beta1/endpoints
- `model_monitor[_info]` - /apis/v1/monitors
