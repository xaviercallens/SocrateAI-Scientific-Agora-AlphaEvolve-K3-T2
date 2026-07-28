# **📄 04_integration_guide.md**

### **Purpose**
Provides a **step-by-step guide** to integrate the above components into **AlphaEvolve-K3-T2**.

---

### **📜 Step 1: Repository Initialization**

#### **4.1.1 Create Repository Structure**
```bash
mkdir -p SocrateAI-Scientific-Agora-AlphaEvolve-K3-T2/{src/{evolution/{genetic_operators,population},validation,integration,utils},tests,notebooks,scripts,outputs/{evolved_geometries,validation_results,logs},docs}
```

#### **4.1.2 Add Core Files**
- **Lean 4**: Copy `FTheoryFibration.lean`, `DualScaleMaster.lean`, `SymSquare.lean` to `src/evolution/`.
- **Python**: Copy `auto_evolve_k3_selection.py`, `v5_dual_scale_pipeline.py` to `scripts/`.
- **Markdown**: Copy `K3_SELECTION_REPORT.md`, `DUAL_SCALE_EXPERIMENTATION_BRIEF_2026_07_25.md` to `docs/`.

---

### **📜 Step 2: AlphaEvolve Engine Implementation**

#### **4.2.1 Genetic Operators**
- **K3 Mutation**: Perturb K3 surface parameters (Picard-Fuchs ODE coefficients).
- **T² Mutation**: Adjust torus moduli (complex structure, Kähler parameters).
- **Crossover**: Combine K3 and T² parameters from parent geometries.
- **Fitness Function**: Score candidates based on **theoretical + empirical alignment**.

#### **4.2.2 Fitness Metrics**
```python
# src/evolution/fitness_functions.py
def fitness_function(candidate):
    # Theoretical Score (60%)
    swampland_score = check_swampland_compliance(candidate)  # Distance Conjecture, dS Conjecture
    f_theory_score = check_f_theory_consistency(candidate)    # Weierstrass model, Kodaira types
    
    # Empirical Score (30%)
    sdss_score = validate_sdss_alignment(candidate)          # Δ spikes, CV maps
    euclid_score = validate_euclid_alignment(candidate)      # Dynamic S₈ gradient
    pta_score = validate_pta_predictions(candidate)          # Scalar monopole
    
    # Consistency Score (10%)
    chameleon_score = check_chameleon_viability(candidate)  # α_eff > 0.45
    gd1_score = check_gd1_bounds(candidate)                 # GD-1 heating bounds
    
    # Weighted Score
    total_score = (
        0.6 * (swampland_score + f_theory_score) / 2 +
        0.3 * (sdss_score + euclid_score + pta_score) / 3 +
        0.1 * (chameleon_score + gd1_score) / 2
    )
    return total_score
```

---

### **📜 Step 3: Integration with Existing Repositories**

#### **4.3.1 Dual-Scale Model Interface**
- **Input**: Evolved K3×T² geometries from AlphaEvolve.
- **Output**: Validation against **Dual-Scale Model theorems** (`DualScaleMaster.lean`).
- **Tools**:
  - `dual_scale_interface.py`: Converts evolved geometries to Lean 4 input format.
  - `swampland_checks.lean`: Runs Swampland compliance tests.

#### **4.3.2 K3 Selection Interface**
- **Input**: Ranked K3 candidates from AlphaEvolve.
- **Output**: Integration with **AutoEvolve** for further refinement.
- **Tools**:
  - `k3_selection_interface.py`: Exports candidates to **SocrateAI-Scientific-Agora-K3-DarkMatter**.
  - `auto_evolve_k3_selection.py`: Uses **AutoEvolve criteria** to rank candidates.

#### **4.3.3 GPU Pipeline Interface**
- **Input**: Evolved geometries for empirical validation.
- **Output**: Results from **V4C/V5 pipelines** (SDSS/Euclid/PTA alignment).
- **Tools**:
  - `gpu_pipeline_interface.py`: Submits geometries to **DarkMatterK3-Home.github.io**.
  - `weak_lensing_prediction.py`: Validates **Δ spike alignment**.

---

### **📜 Step 4: Validation Framework**

#### **4.4.1 Theoretical Validation (Lean 4)**
- **Swampland Checks**: Verify evolved geometries satisfy **Swampland conjectures**.
- **F-Theory Checks**: Confirm **elliptic fibration** and **Kodaira type classifications**.

#### **4.4.2 Empirical Validation (Python)**
- **SDSS/Euclid Alignment**: Compare evolved geometries with observational data.
- **PTA/JWST Predictions**: Validate scalar monopole signatures and high-z galaxy signatures.

---

### **📜 Step 5: Execution Workflow**

#### **4.5.1 Phase 1: Foundation (0–3 Months)**
1. Set up repository structure.
2. Implement AlphaEvolve engine (genetic operators + fitness functions).
3. Integrate with Dual-Scale Model (Lean 4 validation).
4. Initial validation with Cooper s7/s10 as benchmarks.

#### **4.5.2 Phase 2: Integration (3–6 Months)**
1. Connect to AutoEvolve (rank K3 candidates).
2. Empirical validation with SDSS DR17 and Euclid data.
3. PTA/JWST prediction scripts for falsifiable tests.
4. Optimize evolution parameters (mutation rates, population size).

#### **4.5.3 Phase 3: Validation & Publication (6–12 Months)**
1. Full Dual-Scale Model validation (K3×T² + Elliptic EFT).
2. Submit to **arXiv/PRL/Nature Astronomy** after empirical confirmation.
3. Open-source release with reproducibility guidelines.

---

## **📌 Summary of Key Updates (2026-07-28)**

### **From SocrateAI-DualScaleTopologicalUniverseModel-LeanProposal**
- **Theorem 1 (FTheoryFibration)**: **S1-07 non-vacuous rebuild** with concrete θ-form operators.
- **Master Theorem**: Unified proof of **Dual-Scale Model consistency** (Theorems 1–3).
- **Axiom Inventory**: Only **3 axioms** remain (1 empirical, 2 numerical certificates).

### **From SocrateAI-Scientific-Agora-K3-DarkMatter**
- **Cooper s7**: **Kernel-verified K3 surface** with Sym² structure (partner: A279619).
- **Route A vs. Route B**: **Route B (Cooper s7) selected** for S3-00 input.
- **Gate E Criteria**: All **6 technical criteria PASS** → **v0.4.0 authorized**.

### **From DarkMatterK3-Home.github.io**
- **V4C/V5 Pipeline**: Full pipeline **GO confirmed** (N=200 in ~48s).
- **JWST UNCOVER**: **488 massive galaxies at z ~ 9** confirm **19% heavier primordial axion**.
- **PTA Validation**: Scalar monopole predictions aligned with NANOGrav data.

---

## **🎯 Next Steps**
1. **Review and refine** the provided Lean code, astrophysics criteria, and datasets.
2. **Initialize the AlphaEvolve-K3-T2 repository** with the proposed structure.
3. **Develop the AlphaEvolve engine** (genetic operators + fitness functions).
4. **Integrate with existing repositories** (Dual-Scale Model, K3-DarkMatter, DarkMatterK3-Home).
5. **Run initial evolution** with Cooper s7/s10 as benchmarks.
6. **Validate against SDSS/Euclid data** using V4C/V5 pipelines.
