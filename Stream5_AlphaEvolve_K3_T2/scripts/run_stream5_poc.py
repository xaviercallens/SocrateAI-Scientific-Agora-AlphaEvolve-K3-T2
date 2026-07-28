#!/usr/bin/env python3
"""
CLI Launcher for Stream 5 AlphaEvolve K3-T2 Accelerator & PoC.
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from alphaevolve_core.topology_search import run_k3_t2_alphaevolve_search
from accelerators.tpu_sharding_accelerator import setup_tpu_pod_sharding, stream_gcs_k3_data

def main():
    print("======================================================================")
    print("  SOCRATEAI STREAM 5: ALPHAEVOLVE K3-T2 ACCELERATOR & POC LAUNCHER   ")
    print("======================================================================")
    
    # 1. Setup TPU Pod Accelerator & GCS Data Streaming
    mesh = setup_tpu_pod_sharding(32)
    stream = stream_gcs_k3_data("gs://socrateai-datalake-gen-lang-client-0625573011")
    
    # 2. Run AlphaEvolve Search on K3-T2 Fibrations
    results = run_k3_t2_alphaevolve_search(100)
    
    print("\n======================================================================")
    print("  STREAM 5 POC COMPLETED SUCCESSFULLY WITH MIN LOSS: {:.6e}".format(results["min_monge_ampere_loss"]))
    print("======================================================================")

if __name__ == "__main__":
    main()
