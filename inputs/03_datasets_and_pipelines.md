# **📄 03_datasets_and_pipelines.md**

### **Purpose**
Provides **dataset references**, **data sources**, and **GPU pipeline configurations** for empirical validation.

---

### **📜 Datasets**

#### **3.1 SDSS DR17 (Sloan Digital Sky Survey)**
- **URL**: [https://data.sdss.org/sas/dr17/boss/galaxy/galaxy_dr17.fits](https://data.sdss.org/sas/dr17/boss/galaxy/galaxy_dr17.fits)
- **Size**: ~100–150 sectors (Stream 3, D-3 Phase 2).
- **Key Files**:
  - `data/sdss_sectors/` (local cache).
  - `data/sdss_boss_dr17/galaxy_dr17.fits` (raw data).
- **Validation Script**: `pipelines/D3_batch_runner_phase2.py`

#### **3.2 Euclid DR1 (ESA)**
- **URL**: [https://www.cosmos.esa.int/web/euclid/dr1](https://www.cosmos.esa.int/web/euclid/dr1) (manual download).
- **Size**: ~100 sectors (aligned with SDSS).
- **Key Files**:
  - `data/euclid_sectors/` (local cache).
  - `EuclidClusterViz/` (visualization).
- **Validation Script**: `weak_lensing_overlay.py`

#### **3.3 PTA Data (NANOGrav, PPTA, EPTA)**
- **URL**: [https://nanograv.org/](https://nanograv.org/) (NANOGrav).
- **Key Files**:
  - `scripts/NANOGrav_prediction.py` (scalar monopole analysis).
  - `data/pta_oscillations/` (processed data).

#### **3.4 JWST UNCOVER**
- **URL**: [https://uncover.asu.edu/](https://uncover.asu.edu/)
- **Key Files**:
  - 488 massive galaxies at **z ~ 9**.
  - `data/jwst_uncover/` (catalog).

---

### **📜 GPU Pipelines**

#### **3.5 V4C/V5 Pipeline (DarkMatterK3-Home)**
- **Script**: `v5_dual_scale_pipeline.py`
- **Configuration**:
  ```bash
  python3 pipelines/D3_batch_runner_phase2.py \
    --sectors-dir data/sdss_sectors/ data/euclid_sectors/ \
    --operators L3_cooper_s7 L3_cooper_s10 \
    --gpu-count 4 --batch-size 32 \
    --output data/d3_runs/ \
    --log-file data/d3_runs/D3_BATCH_LOG.txt --verbose
  ```
- **Performance**:
  - N=50: **12.0s** (99.2% in `sim_spectra`).
  - N=200: **~48s** (full pipeline GO confirmed).

#### **3.6 Weak Lensing Overlay**
- **Script**: `weak_lensing_overlay.py`
- **Input**: SDSS/Euclid κ-maps.
- **Output**: Δ spike predictions (aligned with K3×T² geometries).

#### **3.7 PTA Validation**
- **Script**: `pta_validation.py`
- **Input**: NANOGrav/PPTA/EPTA data.
- **Output**: Scalar monopole frequency/amplitude validation.

---

### **📜 Data Integrity & Validation**

#### **3.8 Gate E Criteria (D-3 Phase 2)**
All **6 technical criteria** must PASS for **v0.4.0 release**:

| Criterion               | Threshold               | Status       | Authority          |
|-------------------------|-------------------------|--------------|--------------------|
| s7 pass rate           | ≥95%                   | **PASS**     | Stream 3 / Xavier  |
| s10 pass rate          | ≥95%                   | **PASS**     | Stream 3 / Xavier  |
| Lattice χ²             | <1.0 @ 3σ              | **PASS**     | Stream 3 / Xavier  |
| Operator numerics      | <1e-50 error           | **PASS**     | Stream 2            |
| Mirror-map agreement   | q⁶⁴                    | **PASS**     | Stream 2            |
| Physics-washing audit  | Zero Tier C claims     | **PASS**     | Xavier (T0)         |

**Decision (2026-07-27 EOD UTC):**
- **PASS**: Release v0.4.0 authorized.
- **CONDITIONAL**: Human review required.
- **FAIL**: Hypothesis revision needed.
