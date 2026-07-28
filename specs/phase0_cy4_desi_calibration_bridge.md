# Phase 0 Specification: CY4 ↔ DESI BAO Calibration Bridge (MVP/PoC)

> **Version**: 1.0.0  
> **Phase**: 0 (MVP / Proof of Concept)  
> **Status**: APPROVED & IMPLEMENTED  
> **Target**: Validation of 3-Tier Neuro-Symbolic Architecture on Solved Cosmology Problem

---

## 1. Executive Summary

Phase 0 validates the **3-Tier Neuro-Symbolic Architecture** on a known, well-constrained cosmological problem before deploying to the full K3×T² moduli space. 

By mapping Calabi-Yau 4-fold ($\mathbb{P}^5_w$) topological invariants to Dark Energy parameters ($w_0, w_a, \Omega_m, H_0$) and evaluating them against DESI DR1 BAO & Lyman-$\alpha$ likelihoods, Phase 0 proves:
1. **Tier 1 Surrogate Efficacy**: Fast pre-screening culls 90%+ of unstable/singular geometries.
2. **Tier 2 Gatekeeper Rigor**: Symbolic invariant checks ($\sum w_i = d$, $\chi$ bounds) enforce hard Pass/Fail filtering with $\infty$ penalty on failure.
3. **Tier 3 TPU Ground Truth**: High-fidelity Cobaya/MCMC likelihood evaluation feeds back exact $\chi^2$ loss to drive evolutionary convergence toward $\Lambda\text{CDM}$ ($w_0 \approx -1, \Omega_m \approx 0.3$).
4. **End-to-End Autonomous Execution**: 20+ generation evolutionary loops run without memory leaks or orchestration timeouts.

---

## 2. 3-Tier Neuro-Symbolic Architecture (Phase 0 Mapping)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PHASE 0 EVOLUTIONARY LOOP (20 Gen)                    │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 TIER 1: FAST SURROGATE FILTER (cy4_metric_search.py)        │
│  • Generates mutated 𝔽⁵_w weights from stream2_cy4_ml GCS data stream       │
│  • Instantly culls bottom 90% singular / zero-volume topologies             │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ 10% survive
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│            TIER 2: MOCK SYMBOLIC GATEKEEPER (mock_symbolic_gatekeeper.py)   │
│  • Verifies Calabi-Yau condition ∑ w_i = d and Euler characteristic χ bounds │
│  • Hard Pass/Fail (Fail → ∞ penalty, fitness = 0.0)                         │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ Elite survivors
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│           TIER 3: EMPIRICAL TPU GROUND-TRUTH (cobaya_tpu_dispatcher.py)     │
│  • Streams DESI DR1 BAO likelihoods from stream3_desi_dr1 GCS bucket         │
│  • Evaluates χ² loss against ΛCDM target (w₀ ≈ -1.0, Ω_m ≈ 0.3)             │
│  • Feeds back χ² scores to seed parent selection for next generation        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Streams & Physical Mapping

### 3.1 Data Lake Streams
- **Stream 2 (CY4 Topologies)**: `gs://socrateai-datalake-gen-lang-client-0625573011/stream2_cy4_ml/`
- **Stream 3 (DESI DR1 BAO)**: `gs://socrateai-datalake-gen-lang-client-0625573011/stream3_desi_dr1/`
- **Phase 0 Outputs**: `gs://socrateai-datalake-gen-lang-client-0625573011/phase0_outputs/generations/`

### 3.2 Genotype to Phenotype Mapping
Given a weighted projective space $\mathbb{P}^5(w_1, w_2, w_3, w_4, w_5, w_6)$ with degree $d = \sum w_i$:
- **Degree Ratio**: $r = d / (\max(w_i) \cdot 6)$
- **Euler Characteristic Approximation**: $\chi_{CY4} = 6 \cdot (d^2 / \prod w_i)^{1/2}$
- **Dark Energy Mapping**:
  $$\Omega_m = 0.15 + 0.30 \cdot r$$
  $$w_0 = -1.50 + 1.00 \cdot (1 - r) + 0.1 \cdot \sin(\chi_{CY4} / 100)$$
  $$H_0 = 65.0 + 10.0 \cdot r$$

---

## 4. Definition of Done (Acceptance Criteria)

| Metric | Target | Verification Method |
|---|---|---|
| Continuous Autonomous Execution | 20+ generations completed | `scripts/run_phase0_cy4_desi_mvp.py` |
| Tier 1 & 2 Filtering Efficacy | ≥ 80% reduction in TPU calls | Logger / Execution metrics |
| Physics Convergence | $w_0 \to -1.0 \pm 0.1$, $\Omega_m \to 0.30 \pm 0.05$ | Pareto front analysis |
| Unit Test Pass Rate | 100% (all existing + Phase 0 tests) | `unittest discover` |
| Output Logging | Generation logs & Pareto front saved to `results/phase0_outputs/` | JSON file inspection |
