# SocrateAI Stream 5: AlphaEvolve K3-T2 Accelerator & PoC

> **Master Scientific Investigation Project - Stream 5**  
> **Repository**: [https://github.com/xaviercallens/SocrateAI-Scientific-Agora-AlphaEvolve-K3-T2](https://github.com/xaviercallens/SocrateAI-Scientific-Agora-AlphaEvolve-K3-T2)

## Overview

Stream 5 serves as the **AlphaEvolve Accelerator and Proof of Concept (PoC)** for the SocrateAI supercomputing framework. It decouples the novel AutoML architecture search for K3 surfaces ($K3$) and $T^2$ torus fibers ($T^2$) from Stream 2 and Stream 3 to prevent branch conflicts while delivering state-of-the-art Ricci-flat metric approximations.

---

## Key Components

1. **`alphaevolve_core/`**: Evolving neural network topologies, symbolic activation functions, and Monge-Ampère loss evaluators for $K3$ and $T^2$ manifolds.
2. **`accelerators/`**: High-performance TPU Pod matrix sharding and direct streaming from the central Google Cloud Storage Data Lake (`gs://socrateai-datalake-gen-lang-client-0625573011/`).
3. **`config/`**: YAML hyperparameter definitions and Vertex AI Custom Job JSON manifests for GCP automated dispatch.
4. **`tests/`**: Complete `unittest` suite for all Stream 5 modules.
5. **`scripts/`**: One-line CLI launcher (`run_stream5_poc.py`) and GCP Vertex AI job submitter (`deploy_vertex_stream5_job.sh`).

---

## Quick Start

```bash
# Execute local Stream 5 AlphaEvolve PoC dry run
python3 scripts/run_stream5_poc.py

# Run unit verification suite
python3 -m unittest discover -s tests -p "test_*.py" -v
```

---

## GCP Vertex AI Integration

Deploy directly to Google Cloud Platform:
```bash
./scripts/deploy_vertex_stream5_job.sh
```
