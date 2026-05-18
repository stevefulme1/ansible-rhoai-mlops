# Changelog

## 1.1.0 (2026-05-18)

### New Features

- 8 EU AI Act compliance modules:
  - `ai_act_compliance` / `ai_act_compliance_info` - Manage and query compliance assessments
  - `model_risk_classification` / `model_risk_classification_info` - Classify AI models per EU AI Act risk tiers
  - `audit_report` / `audit_report_info` - Generate and query compliance audit reports
  - `compliance_evidence` / `compliance_evidence_info` - Manage and query compliance evidence artifacts
- 6 sovereign data residency modules:
  - `data_residency_policy` / `data_residency_policy_info` - Manage and query data residency policies
  - `geo_fence_audit` / `geo_fence_audit_info` - Audit data flows against geo-fencing rules
  - `data_sovereignty_report` / `data_sovereignty_report_info` - Generate and query sovereignty reports
- 2 new roles:
  - `eu_ai_act_setup` - Set up EU AI Act compliance framework with risk classification,
    audit logging, evidence collection, and compliance dashboard
  - `data_residency_enforcement` - Enforce data residency with geo-fencing policies,
    data locality constraints, cross-border audit logging, and sovereignty monitoring
- Unit tests for all 14 new modules
- Updated galaxy.yml with compliance and sovereignty tags

## 1.0.0 (2026-05-18)

### New Features

- Initial release of the `stevefulme1.rhoai_mlops` collection.
- 20 modules for RHOAI model registry, model serving, data science projects,
  pipelines, and monitoring.
- 4 roles for webhook configuration, drift response, canary deployment,
  and training job recovery.
- 3 EDA event source plugins for model registry, model monitoring,
  and pipeline events.
- 4 EDA rulebooks for drift rollback, training failure recovery,
  model promotion, and GPU health remediation.
