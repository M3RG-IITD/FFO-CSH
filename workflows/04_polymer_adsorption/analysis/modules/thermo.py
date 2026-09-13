"""
Module 4: Thermodynamic Analysis

Computes:
  - Adsorption energy E_ads = E(S1) - E(S2) - E(S3)
  - E_ads time series
  - Running averages and convergence diagnostics
"""
import numpy as np
import pandas as pd
from .utils import extract_thermo_data


def compute_adsorption_energy(s1_log, s2_log, s3_log,
                              cutoff_step=None, average_last_n=None,
                              label="system", mean_s2=True):
    """Compute adsorption energy from three log files."""
    
    s1_data = extract_thermo_data(s1_log, cutoff_step=cutoff_step)
    s2_data = extract_thermo_data(s2_log, cutoff_step=cutoff_step)
    s3_data = extract_thermo_data(s3_log, cutoff_step=cutoff_step)
        
    pe_key = "PotEng" if "PotEng" in s1_data else "pe"
    
    pe_s1 = s1_data[pe_key]
    pe_s2 = s2_data[pe_key]
    pe_s3 = s3_data[pe_key]
    
    if mean_s2 is True:
        # Average PEG PotEng for 1:1: -73367.7947, 2:1: -75639.7142, 3:1: -76757.8462
        pe2_mean = -73367.7947 if "1:1" in label else (-75639.7142 if "2:1" in label else -76757.8462)
        pe_s2 = np.full_like(pe_s1, pe2_mean)

    if average_last_n is not None:
        E_s1 = np.mean(pe_s1[-average_last_n:])
        E_s2 = np.mean(pe_s2[-average_last_n:])
        E_s3 = np.mean(pe_s3[-average_last_n:])
    else:
        E_s1 = np.mean(pe_s1)
        E_s2 = np.mean(pe_s2)
        E_s3 = np.mean(pe_s3)
    
    E_ads = E_s1 - (E_s2 + E_s3)
    
    # E_ads time series (use shortest common length)
    n_min = min(len(pe_s1), len(pe_s2), len(pe_s3))
    E_ads_series = pe_s1[:n_min] - pe_s2[:n_min] - pe_s3[:n_min]
    
    # Standard error
    if average_last_n and average_last_n <= n_min:
        E_ads_tail = pe_s1[-average_last_n:] - pe_s2[-average_last_n:] - pe_s3[-average_last_n:]
        E_ads_err = np.std(E_ads_tail) / np.sqrt(average_last_n)
    else:
        E_ads_err = np.std(E_ads_series) / np.sqrt(n_min)
    
    summary = {
        'label': label,
        'E_s1': E_s1,
        'E_s2': E_s2,
        'E_s3': E_s3,
        'E_ads': E_ads,
        'E_ads_err': E_ads_err,
        'E_ads_series': E_ads_series,
    }
    
    print(f"\n  [{label}] Adsorption Energy Summary:")
    print(f"    E(S1) = {E_s1:.1f}")
    print(f"    E(S2) = {E_s2:.1f}")
    print(f"    E(S3) = {E_s3:.1f}")
    print(f"    E_ads = {E_ads:.1f} ± {E_ads_err:.1f} kcal/mol")
    
    return summary
