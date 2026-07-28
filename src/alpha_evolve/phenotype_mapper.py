import math

def map_k3_to_cosmology(candidate: dict) -> dict:
    """
    Translates the abstract K3xT2 moduli into effective cosmological parameters.
    Based on the Dual-Scale Topological Universe Hypothesis.
    """
    picard = candidate.get("picard_number", 19)
    tau = candidate.get("t2_modulus_tau", 0.5)
    complex_struct = candidate.get("complex_structure", [1.0, 1.0, 1.0])
    
    # 1. Dark Energy Equation of State (w_0)
    # Determined by the T2 torus volume and moduli stabilization deviation
    w_0 = -1.0 - (0.5 * (tau - 0.5)) 
    
    # 2. Matter Density (\Omega_m)
    # Influenced by the K3 Picard number (visible sector coupling)
    omega_m = 0.30 + 0.02 * (19 - picard)
    
    # 3. Hubble Constant (H_0)
    # Modulated by the complex structure magnitude
    cs_mag = math.sqrt(sum(x**2 for x in complex_struct))
    h_0 = 67.4 + (cs_mag - math.sqrt(3)) * 2.0
    
    return {
        "w0": max(-1.2, min(-0.8, w_0)), # Bound to physical priors
        "omega_m": max(0.2, min(0.4, omega_m)),
        "h0": max(65.0, min(75.0, h_0))
    }
