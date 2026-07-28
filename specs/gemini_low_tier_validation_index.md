# Gemini Low-Tier Model — Task Dependency & Validation Index

> Quick-reference companion to [`gemini_low_tier_plan.md`](file:///home/xavkal/.gemini/antigravity-ide/scratch/socrateai/specs/gemini_low_tier_plan.md)

---

## Task Dependency Graph

```mermaid
graph TD
    GLT008["TASK-GLT-008<br/>Config Schema<br/><i>gemini_model_config.yaml</i><br/><i>config_loader.py</i>"]
    GLT001["TASK-GLT-001<br/>Model Router<br/><i>model_router.py</i>"]
    GLT002["TASK-GLT-002<br/>Tier Classifier<br/><i>tier_classifier.py</i>"]
    GLT006["TASK-GLT-006<br/>Cost Tracker<br/><i>cost_tracker.py</i>"]
    GLT007["TASK-GLT-007<br/>Escalation Protocol<br/><i>escalation_protocol.py</i>"]
    GLT003["TASK-GLT-003<br/>Refactor Coordinator<br/><i>agent_kit_orchestrator.py</i>"]
    GLT004["TASK-GLT-004<br/>AlphaEvolve Summarizer<br/><i>feedback_summarizer.py</i>"]
    GLT005["TASK-GLT-005<br/>TPU Pre-Validator<br/><i>dispatch_pre_validator.py</i>"]
    GLT009["TASK-GLT-009<br/>E2E Integration Tests<br/><i>test_gemini_tiered_e2e.py</i>"]

    GLT008 --> GLT001
    GLT008 --> GLT002
    GLT008 --> GLT006
    GLT008 --> GLT007
    GLT001 --> GLT003
    GLT002 --> GLT003
    GLT007 --> GLT003
    GLT003 --> GLT004
    GLT003 --> GLT005
    GLT004 --> GLT009
    GLT005 --> GLT009
    GLT006 --> GLT009
    GLT007 --> GLT009

    classDef phase1 fill:#1a73e8,color:white,stroke:#1557b0
    classDef phase2 fill:#e8710a,color:white,stroke:#c25e08
    classDef phase3 fill:#0d652d,color:white,stroke:#0a4f23
    classDef phase4 fill:#9334e6,color:white,stroke:#7627b8

    class GLT008,GLT001,GLT002 phase1
    class GLT003,GLT006,GLT007 phase2
    class GLT004,GLT005 phase3
    class GLT009 phase4
```

**Legend**: 🔵 Phase 1 (Foundation) · 🟠 Phase 2 (Core Integration) · 🟢 Phase 3 (Pipeline) · 🟣 Phase 4 (Verification)

---

## Validation Checklist

| Task ID | Module | Min Tests | Test Command | DoD Items |
|---|---|---|---|---|
| GLT-001 | `core/model_router.py` | 21 | `pytest tests/test_model_router.py` | 5 |
| GLT-002 | `core/tier_classifier.py` | 50 | `pytest tests/test_tier_classifier.py` | 5 |
| GLT-003 | `core/agent_kit_orchestrator.py` | 8 | `pytest tests/test_orchestrator_multimodel.py` | 6 |
| GLT-004 | `pipeline/.../feedback_summarizer.py` | 9 | `pytest tests/test_feedback_summarizer.py` | 6 |
| GLT-005 | `pipeline/.../dispatch_pre_validator.py` | 12 | `pytest tests/test_dispatch_pre_validator.py` | 5 |
| GLT-006 | `core/cost_tracker.py` | 15 | `pytest tests/test_cost_tracker.py` | 5 |
| GLT-007 | `core/escalation_protocol.py` | 10 | `pytest tests/test_escalation_protocol.py` | 5 |
| GLT-008 | `config/gemini_model_config.yaml` | 12 | `pytest tests/test_config_loader.py` | 5 |
| GLT-009 | `tests/integration/` | 6 | `pytest tests/integration/` | 5 |
| **TOTAL** | | **143+** | `pytest tests/ -v` | **47** |

---

## Cost Projection Model

| Scenario | Flash Calls/Month | Pro Calls/Month | Ultra Calls/Month | Estimated Cost/Month |
|---|---|---|---|---|
| **Light** (10 runs/week) | 4,000 | 400 | 40 | ~$3.20 |
| **Standard** (5 runs/day) | 15,000 | 1,500 | 150 | ~$12.00 |
| **Heavy** (20 runs/day) | 60,000 | 6,000 | 600 | ~$48.00 |
| **Current** (all-Pro) | 0 | 60,000 | 0 | ~$840.00 |

> **Projected savings: 95–99.6%** compared to current all-Pro baseline.
