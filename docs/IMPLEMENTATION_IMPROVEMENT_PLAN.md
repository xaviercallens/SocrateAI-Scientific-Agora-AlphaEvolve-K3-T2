# AlphaEvolve-K3-T2: Implementation Improvement Plan
**Version**: 1.0  
**Date**: 2026-07-28  
**Status**: Pre-Implementation — Ready for Execution  
**Auditor**: Gemini 3.1 Pro (Code Review Agent)  
**Owner**: Xavier Callens

---

## 📋 Overall Scores (Audit Baseline)

| Category               | Score | Status         |
|------------------------|-------|----------------|
| Lean 4 Formalization   | 9/10  | ✅ Strong       |
| Astrophysics Criteria  | 8/10  | ✅ Robust       |
| Datasets & Pipelines   | 7/10  | ⚠️ Partial      |
| Integration Guide      | 8/10  | ✅ Clear        |
| Testing Framework      | 0/10  | ❌ Missing      |
| Documentation          | 6/10  | ⚠️ Incomplete   |
| Performance            | 5/10  | ⚠️ Unvalidated  |
| **Overall**            | **7.1/10** |            |

---

## 🗂️ Sub-Task Index

> Each sub-task is **atomic** and independently executable.

| ID       | Title                                              | Priority | Effort |
|----------|----------------------------------------------------|----------|--------|
| L4-01    | Modularize Lean 4 geometry files                   | P0       | High   |
| L4-02    | Formalize T² torus moduli in Lean 4               | P0       | High   |
| L4-03    | Add JSON serialization for Lean structures         | P1       | Medium |
| L4-04    | Implement Weak Gravity & Refined Swampland proofs  | P1       | High   |
| L4-05    | Add numerical Float fallbacks for discriminants    | P2       | Low    |
| AP-01    | Implement `astrophysics_validator.py`              | P0       | Medium |
| AP-02    | Explicitly filter Cooper s18 from evolution        | P0       | Low    |
| AP-03    | Implement GD-1 stream validator                    | P2       | Medium |
| AP-04    | Implement Core-Cusp tension resolver               | P2       | Medium |
| AP-05    | Add dynamic fitness weight adapter                 | P1       | Medium |
| PL-01    | Replace stub `auto_evolve_k3_selection.py`         | P0       | High   |
| PL-02    | Implement unified `data_preprocessor.py`           | P1       | Medium |
| PL-03    | Add DVC data versioning                            | P3       | Low    |
| PL-04    | Add `benchmark_v5_pipeline.py`                     | P2       | Medium |
| PL-05    | Add error handling to all pipeline scripts         | P0       | Medium |
| INT-01   | Add `cross_repo_validator.py`                      | P1       | Medium |
| INT-02   | Add `RISK_MITIGATION.md`                           | P1       | Low    |
| INT-03   | Add `Dockerfile` and `requirements.txt`            | P2       | Low    |
| CI-01    | Add GitHub Actions CI/CD workflow                  | P1       | High   |
| CI-02    | Add Security scan workflow (Bandit, TruffleHog)    | P2       | Low    |
| TEST-01  | Add Lean 4 unit tests (`lean_test.lean`)           | P0       | High   |
| TEST-02  | Add Python unit tests (pytest)                     | P0       | High   |
| TEST-03  | Add integration tests for cross-repo validation    | P1       | Medium |
| TEST-04  | Add property-based tests (Hypothesis)              | P2       | Medium |
| TEST-05  | Add performance benchmark tests                    | P2       | Medium |
| TEST-06  | Add memory profiling tests                         | P2       | Medium |
| MON-01   | Add centralized `monitoring.py` logger             | P2       | Medium |
| MON-02   | Add `InputValidator` utility class                 | P0       | Medium |
| DOC-01   | Add `API_DOCUMENTATION.md`                         | P3       | High   |
| DOC-02   | Add `USAGE_EXAMPLES.md`                            | P3       | Medium |

---

## 🔴 P0 — Critical (Must Fix Before Production)

### L4-01 — Modularize Lean 4 Geometry Files
**Target Structure**:
```
Agora/
├── Geometry/
│   ├── FTheory/PicardFuchs.lean, Weierstrass.lean, Kodaira.lean, Discriminant.lean
│   ├── T2/Moduli.lean, Kaehler.lean
│   └── K3xT2/Product.lean, FTheoryEmbedding.lean
├── Swampland/DistanceConjecture.lean, DeSitterConjecture.lean, WeakGravity.lean, RefinedSwampland.lean
└── SymSquare/Operators.lean, SymSquare.lean, GoldenTests.lean
```
- [ ] All existing Lean proofs pass after refactor
- [ ] `lake build` succeeds with new structure
- [ ] Each module imports cleanly in isolation

---

### L4-02 — Formalize T² Torus Moduli in Lean 4
**File**: `Agora/Geometry/T2/Moduli.lean`
```lean
structure T2Moduli where
  tau : ℂ
  rho : ℂ
def T2.discriminant (m : T2Moduli) : ℝ := ...
def T2.jInvariant (m : T2Moduli) : ℝ := ...
```
- [ ] Compiles with zero `sorry`
- [ ] JSON deserialization from Python IPC works

---

### AP-01 — Implement `astrophysics_validator.py`
**File**: `src/validation/astrophysics_validator.py`

Methods: `validate_weak_lensing()`, `validate_pta()`, `validate_chameleon()`, `validate_gd1()`, `validate_core_cusp()`, `validate_all()`

- [ ] `validate_weak_lensing(47.0)` → `True`
- [ ] `validate_pta(1e-8, 1e-15)` → `True`
- [ ] `validate_chameleon(0.40)` → `False`

---

### AP-02 — Filter Cooper s18 from Evolution
**Change**:
```python
BLOCKED_CANDIDATES = {"cooper_s18"}
population = [c for c in population if c["candidate_id"] not in BLOCKED_CANDIDATES]
```
- [ ] `cooper_s18` never appears in any generation population
- [ ] Unit test verifies filter at initialization

---

### PL-01 — Replace Stub `auto_evolve_k3_selection.py`
**File**: `src/evolution/auto_evolve_k3_selection.py`

Sub-tasks:
1. Implement `K3Candidate` dataclass
2. Implement `EvolutionParameters` config
3. Implement 60/30/10 fitness function
4. Implement tournament selection
5. Implement uniform ODE coefficient crossover
6. Implement Gaussian mutation
7. Implement plateau-based convergence detection
8. Implement `save_results()` to JSON

- [ ] `evolve.run(num_generations=50)` returns valid `K3Candidate`
- [ ] Fitness monotonically improves or plateaus

---

### PL-05 — Add Error Handling to All Pipeline Scripts
```python
try:
    verdict = lean_oracle.send_and_receive(cand)
except (BrokenPipeError, json.JSONDecodeError) as e:
    logger.error(f"Lean IPC failure for {cand['candidate_id']}: {e}")
    continue
```
- [ ] Lean daemon crash does not abort the evolution loop
- [ ] GCS timeout falls back to local cache gracefully

---

### TEST-01 — Add Lean 4 Unit Tests
**File**: `tests/unit/lean_test.lean`

Tests: `theorem1`, `theorem2`, `theorem3`, S12 is Order-2, s7 is Order-3, algebraic incompatibility

- [ ] `lake test` passes with 0 failures

---

### TEST-02 — Add Python Unit Tests
**Files**: `tests/unit/test_auto_evolve.py`, `tests/unit/test_astrophysics_validator.py`

- [ ] `pytest tests/unit/ -v` — 100% pass
- [ ] Coverage ≥ 80%

---

### MON-02 — Add `InputValidator` Utility Class
**File**: `src/utils/validation.py`

Methods: `validate_file_path()`, `validate_directory_path()`, `validate_positive_integer()`, `validate_probability()`, `validate_list_length()`

- [ ] All pipeline entrypoints call `InputValidator` before logic begins
- [ ] Invalid inputs raise `ValidationError` with descriptive messages

---

## 🟡 P1 — High Priority (Next 1–2 Months)

### L4-03 — Add JSON Serialization for Lean Structures
**File**: `Agora/Serialization.lean`
- `ToJson PicardFuchsODE` and `OfJson PicardFuchsODE` instances
- Round-trip JSON encode/decode test passes

### L4-04 — Implement Weak Gravity & Refined Swampland Proofs
**File**: `Agora/Swampland/WeakGravity.lean`
- `weak_gravity_conjecture` theorem
- `refined_swampland_distance` theorem
- Both called in `rpc_server.lean::verifySwamplandBounds`

### AP-05 — Dynamic Fitness Weight Adapter
**File**: `src/evolution/dynamic_weights.py`
- Weights update based on per-criterion pass rates
- Weights always sum to 1.0
- Weight history saved to checkpoint

### INT-01 — Cross-Repo Validator
**File**: `src/integration/cross_repo_validator.py`
- `validate_stream1_lean_proofs(lean_file)` → `lean --make`
- `validate_stream2_k3_ranking(k3_report)` → checks `cooper_s7` selected
- `validate_stream3_gpu_results(gpu_log)` → checks pass rate ≥ 95%

### INT-02 — Risk Mitigation Document
**File**: `docs/RISK_MITIGATION.md`

Covers: GPU failure, GCS unavailability, Lean proof failures, dependency conflicts, cross-repo inconsistencies

### CI-01 — GitHub Actions CI/CD
**File**: `.github/workflows/ci_cd.yml`

Jobs: lint (flake8/black/mypy), test (pytest), lean (`lean --make`), build (Docker), deploy (MkDocs to GitHub Pages)

### TEST-03 — Cross-Repo Integration Tests
**File**: `tests/integration/test_cross_repo.py`

### PL-02 — Unified Data Preprocessor
**File**: `src/utils/data_preprocessor.py`

Datasets: SDSS, Euclid, PTA (NANOGrav), JWST UNCOVER  
Output format: Parquet with standardized schema

---

## 🟢 P2 — Medium Priority (Next 3–6 Months)

| Sub-task | File | Description |
|----------|------|-------------|
| L4-05 | `Agora/Numerics.lean` | Float fallbacks for discriminants |
| AP-03 | `src/validation/gd1_core_cusp.py` | GD-1 stream heating validator |
| AP-04 | `src/validation/gd1_core_cusp.py` | Core-Cusp density slope resolver |
| PL-04 | `src/utils/benchmark_v5_pipeline.py` | V5 pipeline runtime/memory benchmarks |
| INT-03 | `Dockerfile`, `requirements.txt` | Pinned dependencies and container |
| TEST-04 | `tests/property/` | Hypothesis property-based tests |
| TEST-05 | `tests/benchmark/` | Performance benchmark tests |
| TEST-06 | `tests/benchmark/` | Memory profiling tests |
| MON-01 | `src/utils/monitoring.py` | Centralized logger + metrics JSON |
| CI-02 | `.github/workflows/security_scan.yml` | Bandit, TruffleHog, Safety |

---

## 🔵 P3 — Low Priority (Next 6–12 Months)

| Sub-task | File | Description |
|----------|------|-------------|
| PL-03 | `.dvc/config`, `data.dvc` | DVC data versioning for SDSS/Euclid/PTA/JWST |
| DOC-01 | `docs/API_DOCUMENTATION.md` | Full Lean 4 + Python API reference |
| DOC-02 | `docs/USAGE_EXAMPLES.md` | End-to-end usage examples |

---

## 📊 12-Month Roadmap

```
Month 1-2 (P0):  L4-01, L4-02, AP-01, AP-02, PL-01, PL-05, TEST-01, TEST-02, MON-02
Month 2-4 (P1):  L4-03, L4-04, AP-05, INT-01, INT-02, CI-01, TEST-03, PL-02
Month 4-6 (P2):  L4-05, AP-03, AP-04, PL-04, INT-03, TEST-04, TEST-05, TEST-06, MON-01, CI-02
Month 6-12 (P3): PL-03, DOC-01, DOC-02
```

---

## 📈 Success Metrics

| Metric                        | Baseline | 3 Months | 12 Months |
|-------------------------------|----------|----------|-----------|
| Lean 4 Test Coverage           | 0%       | 80%      | 95%       |
| Python Test Coverage           | 0%       | 80%      | 95%       |
| Pipeline Success Rate          | N/A      | 95%      | 99%       |
| Cross-Repo Consistency         | N/A      | 90%      | 99%       |
| Documentation Completeness     | 60%      | 80%      | 95%       |
| Evolution Runtime (N=100)      | N/A      | < 60s    | < 30s     |
| Memory Usage (N=1000)          | N/A      | < 1 GB   | < 500 MB  |

---

*Total sub-tasks: 29 | Plan prepared 2026-07-28 | Execution pending sign-off.*
