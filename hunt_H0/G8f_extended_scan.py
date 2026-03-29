"""
G8f -- Extended SIDM scan beyond 100 GeV
==========================================

The original v22 scan covers m_chi in [0.1, 100] GeV.
MAP sits at m_chi = 98.19 GeV, at the upper boundary.
G8d showed alpha_d ~ const (7% variation over 15-150 GeV)
and that the y = g_d/3 relation works only for lambda >> 1 (resonant regime).

This script EXTENDS the scan to m_chi = [100, 500] GeV to test:
1. Do SIDM-viable points exist above 100 GeV?
2. Does alpha_d(chain) remain constant?
3. Does the transmutation coincidence Lambda_d ~ m_nu persist?
4. Is MAP still special, or do heavier points match better?

Physics: VPM (Variable Phase Method) for Yukawa sigma_T, identical to v22.
"""

import math
import time
import numpy as np
from numba import jit

# ====================================================================
#  Constants
# ====================================================================
C_KM_S      = 299792.458
GEV2_TO_CM2 = 0.3894e-27   # 1 GeV^-2 in cm^2
GEV_IN_G    = 1.783e-24     # 1 GeV in grams

# Transmutation / seesaw
B0          = 19.0 / 3.0
V_EW        = 246.22        # GeV
M_R_GUT     = 2e16          # seesaw scale GeV
MEV_CONV    = 1e12          # GeV -> meV

# A4 / gauge
ALPHA_D     = 0.0315
G_D         = math.sqrt(4 * math.pi * ALPHA_D)  # = 0.6292
SIN_THETA   = 1.0 / 3.0

# Resonance band centres (lambda_c values)
LAM_CRITS = np.array([1.68, 6.45, 14.7, 26.0])

# SIDM cuts (same as v22)
SIGMA30_LO  = 0.5
SIGMA30_HI  = 10.0
SIGMA1000_HI = 0.1  # cluster constraint

# MAP for reference
MAP_MCHI   = 98.19
MAP_ALPHA  = 3.274e-3
MAP_MPHI   = 9.66e-3  # GeV

# ====================================================================
#  VPM solver (Numba JIT) -- byte-for-byte identical to v22
# ====================================================================

@jit(nopython=True, cache=True)
def sph_jn(l, z):
    if z < 1e-30:
        return 1.0 if l == 0 else 0.0
    j0 = math.sin(z) / z
    if l == 0:
        return j0
    j1 = math.sin(z) / (z * z) - math.cos(z) / z
    if l == 1:
        return j1
    jp, jc = j0, j1
    for n in range(1, l):
        jn = (2 * n + 1) / z * jc - jp
        jp = jc
        jc = jn
        if abs(jc) < 1e-300:
            return 0.0
    return jc

@jit(nopython=True, cache=True)
def sph_yn(l, z):
    if z < 1e-30:
        return -1e300
    y0 = -math.cos(z) / z
    if l == 0:
        return y0
    y1 = -math.cos(z) / (z * z) - math.sin(z) / z
    if l == 1:
        return y1
    yp, yc = y0, y1
    for n in range(1, l):
        yn = (2 * n + 1) / z * yc - yp
        yp = yc
        yc = yn
        if abs(yc) > 1e200:
            return yc
    return yc

@jit(nopython=True, cache=True)
def _vpm_rhs(l, kappa, lam, x, delta):
    if x < 1e-20:
        return 0.0
    z = kappa * x
    if z < 1e-20:
        return 0.0
    jl = sph_jn(l, z)
    nl = sph_yn(l, z)
    j_hat = z * jl
    n_hat = -z * nl
    cd = math.cos(delta)
    sd = math.sin(delta)
    bracket = j_hat * cd - n_hat * sd
    if not math.isfinite(bracket):
        return 0.0
    pot = lam * math.exp(-x) / (kappa * x)
    val = pot * bracket * bracket
    return val if math.isfinite(val) else 0.0

@jit(nopython=True, cache=True)
def vpm_phase_shift(l, kappa, lam, x_max=50.0, N_steps=4000):
    if lam < 1e-30 or kappa < 1e-30:
        return 0.0
    x_min = max(1e-5, 0.05 / (kappa + 0.01))
    if l > 0:
        x_barrier = l / kappa
        if x_barrier > x_min:
            x_min = x_barrier
    h = (x_max - x_min) / N_steps
    delta = 0.0
    for i in range(N_steps):
        x = x_min + i * h
        k1 = _vpm_rhs(l, kappa, lam, x, delta)
        k2 = _vpm_rhs(l, kappa, lam, x + 0.5*h, delta + 0.5*h*k1)
        k3 = _vpm_rhs(l, kappa, lam, x + 0.5*h, delta + 0.5*h*k2)
        k4 = _vpm_rhs(l, kappa, lam, x + h, delta + h*k3)
        delta += h * (k1 + 2*k2 + 2*k3 + k4) / 6.0
    return delta

@jit(nopython=True, cache=True)
def sigma_T_vpm(m_chi, m_phi, alpha, v_km_s):
    """sigma_T/m [cm^2/g] -- Yukawa VPM, identical to v22."""
    v = v_km_s / C_KM_S
    mu = m_chi / 2.0
    k = mu * v
    kappa = k / m_phi
    lam = alpha * m_chi / m_phi
    if kappa < 1e-15:
        return 0.0
    if kappa < 5:
        x_max, N_steps = 50.0, 4000
    elif kappa < 50:
        x_max, N_steps = 80.0, 8000
    else:
        x_max, N_steps = 100.0, 12000
    l_max = min(max(3, min(int(kappa * x_max), int(kappa) + int(lam) + 20)), 500)
    sigma_sum = 0.0
    peak = 0.0
    n_small = 0
    for l in range(l_max + 1):
        delta = vpm_phase_shift(l, kappa, lam, x_max, N_steps)
        w = 1.0 if l % 2 == 0 else 3.0
        c = w * (2*l + 1) * math.sin(delta)**2
        sigma_sum += c
        if c > peak:
            peak = c
        if peak > 0.0 and c / peak < 1e-4:
            n_small += 1
            if n_small >= 5:
                break
        else:
            n_small = 0
    sigma_GeV2 = 2.0 * math.pi * sigma_sum / (k * k)
    sigma_cm2 = sigma_GeV2 * GEV2_TO_CM2
    return sigma_cm2 / (m_chi * GEV_IN_G)

# ====================================================================
#  Helper: transmutation + seesaw
# ====================================================================
def Lambda_d_meV(alpha_d, m_chi_GeV):
    exp_arg = -2 * math.pi / (B0 * alpha_d)
    if exp_arg < -700:
        return 0.0
    return m_chi_GeV * math.exp(exp_arg) * MEV_CONV

m_nu_target = V_EW**2 / M_R_GUT * MEV_CONV  # ~ 3.03 meV

def alpha_d_chain(m_chi_GeV):
    """alpha_d from m_chi via transmutation chain: alpha_d = 2pi / (b0 * ln(m_chi * M_R / v^2))."""
    arg = m_chi_GeV * M_R_GUT / V_EW**2
    if arg <= 1:
        return 0.0
    return 2 * math.pi / (B0 * math.log(arg))

def y_total_pred(alpha_d_val):
    """Predicted y_total = g_d/3 from alpha_d."""
    g_d = math.sqrt(4 * math.pi * alpha_d_val)
    return g_d / 3.0

def alpha_sidm_pred(alpha_d_val):
    """Predicted alpha_SIDM = (8/81) * alpha_d from gauge-Yukawa."""
    return (8.0 / 81.0) * alpha_d_val


# ====================================================================
#  Main scan
# ====================================================================
print("=" * 78)
print("  G8f -- Extended SIDM scan: m_chi = 100-500 GeV")
print("=" * 78)

# --- Part 1: alpha_d(chain) remains constant above 100 GeV? ---
print()
print("=" * 78)
print("  Part 1: alpha_d(chain) for m_chi > 100 GeV")
print("=" * 78)
print()
print(f"  {'m_chi [GeV]':>12}  {'alpha_d(chain)':>14}  {'g_d':>8}  {'y=g_d/3':>8}  {'Lambda_d [meV]':>16}  {'Lambda_d/m_nu':>13}")
print(f"  {'':->12}  {'':->14}  {'':->8}  {'':->8}  {'':->16}  {'':->13}")

check_masses = [50, 100, 150, 200, 250, 300, 400, 500]
for mc in check_masses:
    ad = alpha_d_chain(mc)
    gd = math.sqrt(4 * math.pi * ad)
    y = gd / 3.0
    ld = Lambda_d_meV(ad, mc)
    ratio = ld / m_nu_target if m_nu_target > 0 else 0
    print(f"  {mc:>12.1f}  {ad:>14.6f}  {gd:>8.4f}  {y:>8.4f}  {ld:>16.6f}  {ratio:>13.4f}")

# --- Part 2: VPM scan for m_chi = 100-500 GeV ---
print()
print("=" * 78)
print("  Part 2: VPM scan m_chi in [100, 500] GeV")
print("=" * 78)
print()

# Grid: 10 m_chi x 20 m_phi x 4 resonance x 50 alpha = 40K evaluations
N_CHI_EXT   = 10
N_PHI_EXT   = 20
N_ALPHA_EXT = 50

m_chi_vals = np.logspace(np.log10(100.0), np.log10(500.0), N_CHI_EXT)
m_phi_vals = np.logspace(np.log10(0.1e-3), np.log10(200e-3), N_PHI_EXT)  # GeV

t0 = time.time()

# Collect viable points
results = []
total_eval = 0
n_res = len(LAM_CRITS)

# JIT warmup
_ = sigma_T_vpm(100.0, 0.01, 0.003, 30.0)
print(f"  JIT warmup done.")
print(f"  Grid: {N_CHI_EXT} m_chi x {N_PHI_EXT} m_phi x {n_res} res x {N_ALPHA_EXT} alpha")
print(f"  Total evaluations (max): ~{N_CHI_EXT * N_PHI_EXT * n_res * N_ALPHA_EXT * 2}")
print(f"  (Many skipped due to alpha_c bounds)")
print()
for ic, mc in enumerate(m_chi_vals):
    n_found_this_mc = 0
    for ip, mp in enumerate(m_phi_vals):
        for ir in range(n_res):
            lam_c = LAM_CRITS[ir]
            alpha_c = lam_c * mp / mc
            if alpha_c > 0.5 or alpha_c < 1e-7:
                continue
            a_lo = alpha_c * 0.7
            a_hi = alpha_c * 1.3
            for ia in range(N_ALPHA_EXT):
                frac = ia / max(N_ALPHA_EXT - 1, 1)
                a = a_lo * (a_hi / a_lo) ** frac
                total_eval += 1
                sd = sigma_T_vpm(mc, mp, a, 30.0)
                if sd < SIGMA30_LO or sd > SIGMA30_HI:
                    continue
                total_eval += 1
                sc = sigma_T_vpm(mc, mp, a, 1000.0)
                if sc >= SIGMA1000_HI:
                    continue
                # Viable point!
                results.append((mc, mp, a, sd, sc, ir))
                n_found_this_mc += 1
    elapsed = time.time() - t0
    print(f"  m_chi={mc:7.1f} GeV | found {n_found_this_mc:5d} | total={len(results):6d} | elapsed={elapsed:6.1f}s")

t_scan = time.time() - t0
print(f"\n  Scan complete: {len(results)} viable points in {t_scan:.1f}s")
print(f"  Total VPM evaluations: {total_eval}")

# --- Part 3: Analyse extended results ---
print()
print("=" * 78)
print("  Part 3: Analysis of extended scan results")
print("=" * 78)

if len(results) == 0:
    print("\n  NO viable points found above 100 GeV!")
    print("  This would mean MAP is at the PHYSICAL boundary, not just scan boundary.")
else:
    res = np.array(results)
    mc_all  = res[:, 0]
    mp_all  = res[:, 1]  # GeV
    a_all   = res[:, 2]
    sd_all  = res[:, 3]
    sc_all  = res[:, 4]
    
    lam_all = a_all * mc_all / mp_all  # lambda parameter
    
    print(f"\n  Extended scan: {len(results)} viable points")
    print(f"  m_chi range: [{mc_all.min():.1f}, {mc_all.max():.1f}] GeV")
    print(f"  m_phi range: [{mp_all.min()*1e3:.2f}, {mp_all.max()*1e3:.2f}] MeV")
    print(f"  alpha range: [{a_all.min():.6e}, {a_all.max():.6e}]")
    print(f"  lambda range: [{lam_all.min():.2f}, {lam_all.max():.2f}]")
    
    # --- Part 4: alpha_d(chain) for each point ---
    print()
    print("=" * 78)
    print("  Part 4: Does alpha_d(chain) match alpha_SIDM?")
    print("=" * 78)
    
    ad_chain_arr = np.array([alpha_d_chain(mc) for mc in mc_all])
    a_sidm_pred  = np.array([alpha_sidm_pred(ad) for ad in ad_chain_arr])
    
    # How many have alpha_SIDM within 10% of predicted?
    rel_err = np.abs(a_all - a_sidm_pred) / a_sidm_pred
    n_match_10 = np.sum(rel_err < 0.10)
    n_match_5  = np.sum(rel_err < 0.05)
    n_match_1  = np.sum(rel_err < 0.01)
    
    print(f"\n  Points with |alpha - (8/81)alpha_d(chain)| / pred:")
    print(f"    < 10%: {n_match_10:6d} / {len(results)} ({100*n_match_10/len(results):.2f}%)")
    print(f"    <  5%: {n_match_5:6d} / {len(results)} ({100*n_match_5/len(results):.2f}%)")
    print(f"    <  1%: {n_match_1:6d} / {len(results)} ({100*n_match_1/len(results):.2f}%)")
    
    # --- Part 5: Transmutation coincidence ---
    print()
    print("=" * 78)
    print("  Part 5: Transmutation Lambda_d ~ m_nu for extended points")
    print("=" * 78)
    
    ld_arr = np.array([Lambda_d_meV(ad, mc) for ad, mc in zip(ad_chain_arr, mc_all)])
    ratio_arr = ld_arr / m_nu_target
    
    in_de_window = np.sum((ld_arr > 1.0) & (ld_arr < 10.0))
    print(f"\n  Lambda_d in DE window [1, 10] meV: {in_de_window} / {len(results)} ({100*in_de_window/len(results):.2f}%)")
    
    # Dual constraint: alpha_SIDM within 10% AND Lambda_d in [1,10]
    dual_mask = (rel_err < 0.10) & (ld_arr > 1.0) & (ld_arr < 10.0)
    n_dual = np.sum(dual_mask)
    print(f"  Dual (alpha<10% + DE window): {n_dual} / {len(results)} ({100*n_dual/len(results):.3f}%)")
    
    # --- Part 6: Comparison with MAP ---
    print()
    print("=" * 78)
    print("  Part 6: MAP vs best extended point")
    print("=" * 78)
    
    # Find the point closest to alpha_SIDM_pred with Lambda_d in DE window
    if n_dual > 0:
        dual_idx = np.where(dual_mask)[0]
        best_i = dual_idx[np.argmin(rel_err[dual_idx])]
        
        print(f"\n  MAP:      m_chi={MAP_MCHI:.2f}  m_phi={MAP_MPHI*1e3:.2f} MeV  alpha={MAP_ALPHA:.6e}")
        ad_map = alpha_d_chain(MAP_MCHI)
        a_pred_map = alpha_sidm_pred(ad_map)
        print(f"            alpha_d(chain)={ad_map:.6f}  alpha_pred={(8/81)*ad_map:.6e}  mismatch={abs(MAP_ALPHA-a_pred_map)/a_pred_map*100:.1f}%")
        print(f"            Lambda_d={Lambda_d_meV(ad_map, MAP_MCHI):.4f} meV")
        
        mc_b = mc_all[best_i]
        mp_b = mp_all[best_i]
        a_b  = a_all[best_i]
        ad_b = alpha_d_chain(mc_b)
        ap_b = alpha_sidm_pred(ad_b)
        
        print(f"\n  Best ext: m_chi={mc_b:.2f}  m_phi={mp_b*1e3:.2f} MeV  alpha={a_b:.6e}")
        print(f"            alpha_d(chain)={ad_b:.6f}  alpha_pred={ap_b:.6e}  mismatch={abs(a_b-ap_b)/ap_b*100:.1f}%")
        print(f"            Lambda_d={Lambda_d_meV(ad_b, mc_b):.4f} meV")
    else:
        print("\n  No dual-constraint points found in extended range.")

    # --- Part 7: Distribution by m_chi ---
    print()
    print("=" * 78)
    print("  Part 7: Distribution by m_chi")
    print("=" * 78)
    print()
    print(f"  {'m_chi [GeV]':>12}  {'N_viable':>8}  {'alpha_d(chain)':>14}  {'Lambda_d [meV]':>14}  {'<alpha_SIDM>':>14}  {'pred alpha':>12}  {'mismatch%':>10}")
    print(f"  {'':->12}  {'':->8}  {'':->14}  {'':->14}  {'':->14}  {'':->12}  {'':->10}")
    
    for mc_val in m_chi_vals:
        mask_mc = np.abs(mc_all - mc_val) < 0.01 * mc_val
        n_mc = np.sum(mask_mc)
        if n_mc == 0:
            print(f"  {mc_val:>12.1f}  {0:>8d}")
            continue
        ad = alpha_d_chain(mc_val)
        ld = Lambda_d_meV(ad, mc_val)
        mean_a = np.mean(a_all[mask_mc])
        ap = alpha_sidm_pred(ad)
        mm = abs(mean_a - ap) / ap * 100 if ap > 0 else 0
        print(f"  {mc_val:>12.1f}  {n_mc:>8d}  {ad:>14.6f}  {ld:>14.4f}  {mean_a:>14.6e}  {ap:>12.6e}  {mm:>10.1f}")

    # --- Part 8: y = g_d/3 test for lambda >> 1 region ---
    print()
    print("=" * 78)
    print("  Part 8: y = g_d/3 test for extended points")
    print("=" * 78)
    
    # Points with lambda > 25 (deep resonant, where y=g_d/3 should work)
    deep_mask = lam_all > 25
    n_deep = np.sum(deep_mask)
    print(f"\n  Points with lambda > 25: {n_deep} / {len(results)}")
    
    if n_deep > 0:
        # For these points, check alpha vs (8/81)*alpha_d(chain)
        a_deep = a_all[deep_mask]
        mc_deep = mc_all[deep_mask]
        ad_deep = np.array([alpha_d_chain(mc) for mc in mc_deep])
        ap_deep = np.array([alpha_sidm_pred(ad) for ad in ad_deep])
        err_deep = np.abs(a_deep - ap_deep) / ap_deep
        
        print(f"  Mean mismatch (alpha vs (8/81)alpha_d): {np.mean(err_deep)*100:.1f}%")
        print(f"  Median mismatch: {np.median(err_deep)*100:.1f}%")
        n_5pct = np.sum(err_deep < 0.05)
        print(f"  Within 5%: {n_5pct} / {n_deep} ({100*n_5pct/n_deep:.1f}%)")
    
    # Points with lambda > 30 (MAP has lambda = 33.28)
    vdeep_mask = lam_all > 30
    n_vdeep = np.sum(vdeep_mask)
    print(f"\n  Points with lambda > 30 (MAP-like): {n_vdeep}")
    
    if n_vdeep > 0:
        a_vd = a_all[vdeep_mask]
        mc_vd = mc_all[vdeep_mask]
        mp_vd = mp_all[vdeep_mask]
        ad_vd = np.array([alpha_d_chain(mc) for mc in mc_vd])
        ap_vd = np.array([alpha_sidm_pred(ad) for ad in ad_vd])
        err_vd = np.abs(a_vd - ap_vd) / ap_vd
        
        print(f"  Mean mismatch: {np.mean(err_vd)*100:.1f}%")
        print(f"  Best 5 points:")
        top5 = np.argsort(err_vd)[:5]
        for idx in top5:
            lam_val = a_vd[idx] * mc_vd[idx] / mp_vd[idx]
            print(f"    m_chi={mc_vd[idx]:.1f}  m_phi={mp_vd[idx]*1e3:.2f} MeV  alpha={a_vd[idx]:.6e}  lambda={lam_val:.1f}  mismatch={err_vd[idx]*100:.2f}%")

# ====================================================================
#  Verdict
# ====================================================================
print()
print("=" * 78)
print("  G8f VERDICT")
print("=" * 78)

print(f"""
  SCAN: m_chi in [100, 500] GeV, {N_CHI_EXT}x{N_PHI_EXT} grid, 4 resonances x {N_ALPHA_EXT} alpha
  Total VPM evaluations: {total_eval}
  Scan time: {t_scan:.1f}s

  PREVIOUS (v22, m_chi < 100 GeV): 80,142 viable points
  EXTENDED (this scan, m_chi > 100 GeV): {len(results)} viable points
""")

if len(results) > 0:
    # Summary statistics
    frac_dual = 100*n_dual/len(results) if len(results) > 0 else 0
    print(f"  Dual-constraint points: {n_dual} ({frac_dual:.3f}%)")
    print(f"  Deep resonant (lambda>25): {n_deep}")
    print(f"  Very deep resonant (lambda>30): {n_vdeep}")
    if n_dual > 0:
        print(f"  -> MAP is NOT unique! Extended points may satisfy the coincidence.")
    else:
        print(f"  -> MAP remains special: no dual-constraint points above 100 GeV.")
else:
    print(f"  -> NO viable SIDM points exist above 100 GeV.")
    print(f"  -> MAP is at the PHYSICAL upper boundary, not just a scan artifact.")
    print(f"  -> This strengthens the coincidence: nature chose the extreme point.")
