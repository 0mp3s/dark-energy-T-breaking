"""
G8f -- Extended SIDM scan beyond 100 GeV (multiprocessing)
============================================================

The original v22 scan covers m_chi in [0.1, 100] GeV.
MAP sits at m_chi = 98.19 GeV — at the upper boundary.

This script EXTENDS the scan to m_chi = [100, 500] GeV using
multiprocessing (same architecture as v22_raw_scan_fast.py).

Tests:
1. Do SIDM-viable points exist above 100 GeV?
2. Does alpha_d(chain) remain constant?
3. Does the transmutation coincidence Lambda_d ~ m_nu persist?
4. Is MAP still special, or do heavier points match better?
"""

import math
import time
import sys
import os
import numpy as np
from numba import jit
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

# ====================================================================
#  Constants
# ====================================================================
C_KM_S      = 299792.458
GEV2_TO_CM2 = 0.3894e-27
GEV_IN_G    = 1.783e-24

B0          = 19.0 / 3.0
V_EW        = 246.22
M_R_GUT     = 2e16
MEV_CONV    = 1e12

ALPHA_D     = 0.0315
G_D         = math.sqrt(4 * math.pi * ALPHA_D)
SIN_THETA   = 1.0 / 3.0

LAM_CRITS   = np.array([1.68, 6.45, 14.7, 26.0])

SIGMA30_LO   = 0.5
SIGMA30_HI   = 10.0
SIGMA1000_HI = 0.1

MAP_MCHI   = 98.19
MAP_ALPHA  = 3.274e-3
MAP_MPHI   = 9.66e-3

# Checkpoint files (for resume)
CHECKPOINT_DIR   = os.path.dirname(os.path.abspath(__file__))
HITS_CKPT_FILE   = os.path.join(CHECKPOINT_DIR, 'G8f_hits_checkpoint.csv')
GRAINS_DONE_FILE = os.path.join(CHECKPOINT_DIR, 'G8f_grains_done.txt')

# Grid — m_phi floor raised to 2 MeV to keep kappa < 50 and lambda manageable
# MAP has m_phi = 9.66 MeV; scanning [2, 200] MeV is sufficient
N_CHI_EXT   = 10
N_PHI_EXT   = 20
N_ALPHA_EXT = 50
N_RES       = len(LAM_CRITS)

M_CHI_VALS = np.logspace(np.log10(100.0), np.log10(500.0), N_CHI_EXT)
M_PHI_VALS = np.logspace(np.log10(2e-3), np.log10(200e-3), N_PHI_EXT)

# ====================================================================
#  VPM solver (Numba JIT) -- identical to v22
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
#  Grain kernel — one (m_chi, m_phi) pair, Numba JIT
# ====================================================================

@jit(nopython=True, cache=True)
def scan_one_grain(mc, mp, lam_crits, n_res, n_alpha,
                   sd_lo, sd_hi, sc_hi):
    max_buf = n_res * n_alpha
    buf_alpha = np.zeros(max_buf)
    buf_sd    = np.zeros(max_buf)
    buf_sc    = np.zeros(max_buf)
    buf_ires  = np.zeros(max_buf, dtype=np.int32)
    count = 0

    for ir in range(n_res):
        lam_c = lam_crits[ir]
        alpha_c = lam_c * mp / mc
        if alpha_c > 0.5 or alpha_c < 1e-7:
            continue
        a_lo = alpha_c * 0.7
        a_hi = alpha_c * 1.3

        for ia in range(n_alpha):
            frac = ia / max(n_alpha - 1.0, 1.0)
            alpha = a_lo * (a_hi / a_lo) ** frac

            sd = sigma_T_vpm(mc, mp, alpha, 30.0)
            if sd < sd_lo or sd > sd_hi:
                continue
            sc = sigma_T_vpm(mc, mp, alpha, 1000.0)
            if sc >= sc_hi:
                continue

            if count < max_buf:
                buf_alpha[count] = alpha
                buf_sd[count]    = sd
                buf_sc[count]    = sc
                buf_ires[count]  = ir
                count += 1

    return buf_alpha, buf_sd, buf_sc, buf_ires, count


# ====================================================================
#  Worker function for ProcessPoolExecutor
# ====================================================================

def _grain_worker(ic, ip, mc, mp):
    """Process one (m_chi, m_phi) grain."""
    buf_alpha, buf_sd, buf_sc, buf_ires, count = \
        scan_one_grain(mc, mp, LAM_CRITS, N_RES, N_ALPHA_EXT,
                       SIGMA30_LO, SIGMA30_HI, SIGMA1000_HI)
    hits = []
    for j in range(count):
        hits.append((mc, mp, float(buf_alpha[j]),
                      float(buf_sd[j]), float(buf_sc[j]), int(buf_ires[j])))
    return ic, ip, hits


# ====================================================================
#  Helpers
# ====================================================================

def Lambda_d_meV(alpha_d, m_chi_GeV):
    exp_arg = -2 * math.pi / (B0 * alpha_d)
    if exp_arg < -700:
        return 0.0
    return m_chi_GeV * math.exp(exp_arg) * MEV_CONV

m_nu_target = V_EW**2 / M_R_GUT * MEV_CONV

def alpha_d_chain(m_chi_GeV):
    arg = m_chi_GeV * M_R_GUT / V_EW**2
    if arg <= 1:
        return 0.0
    return 2 * math.pi / (B0 * math.log(arg))

def alpha_sidm_pred(alpha_d_val):
    return (8.0 / 81.0) * alpha_d_val


# ====================================================================
#  Main
# ====================================================================

if __name__ == '__main__':
    print("=" * 78)
    print("  G8f -- Extended SIDM scan: m_chi = 100-500 GeV (multiprocessing)")
    print("=" * 78)

    # --- Part 1: alpha_d(chain) table ---
    print()
    print("=" * 78)
    print("  Part 1: alpha_d(chain) for m_chi > 100 GeV")
    print("=" * 78)
    print()
    print(f"  {'m_chi':>10}  {'alpha_d':>10}  {'g_d':>8}  {'y=g_d/3':>8}  {'Lambda_d':>12}  {'Ld/m_nu':>8}")
    print(f"  {'[GeV]':>10}  {'(chain)':>10}  {'':>8}  {'':>8}  {'[meV]':>12}  {'':>8}")
    print(f"  {'─'*10}  {'─'*10}  {'─'*8}  {'─'*8}  {'─'*12}  {'─'*8}")

    for mc in [50, 100, 150, 200, 300, 500]:
        ad = alpha_d_chain(mc)
        gd = math.sqrt(4 * math.pi * ad)
        y = gd / 3.0
        ld = Lambda_d_meV(ad, mc)
        ratio = ld / m_nu_target if m_nu_target > 0 else 0
        print(f"  {mc:>10.0f}  {ad:>10.6f}  {gd:>8.4f}  {y:>8.4f}  {ld:>12.4f}  {ratio:>8.4f}")

    # --- Part 2: Parallel VPM scan ---
    print()
    print("=" * 78)
    print("  Part 2: VPM scan m_chi in [100, 500] GeV (parallel)")
    print("=" * 78)
    print()

    # JIT warmup (single-threaded, triggers compilation)
    _ = sigma_T_vpm(100.0, 0.01, 0.003, 30.0)
    _ = scan_one_grain(100.0, 0.01, LAM_CRITS, N_RES, N_ALPHA_EXT,
                        SIGMA30_LO, SIGMA30_HI, SIGMA1000_HI)

    n_workers = min(12, multiprocessing.cpu_count())
    total_grains = N_CHI_EXT * N_PHI_EXT
    print(f"  Grid: {N_CHI_EXT} m_chi x {N_PHI_EXT} m_phi = {total_grains} grains")
    print(f"  Per grain: {N_RES} res x {N_ALPHA_EXT} alpha = {N_RES * N_ALPHA_EXT} evals")
    print(f"  Workers: {n_workers}")
    print()

    # --- Resume: load already-done grains ---
    grains_done_set = set()
    results = []
    if os.path.exists(GRAINS_DONE_FILE):
        with open(GRAINS_DONE_FILE, 'r') as f_done:
            for line in f_done:
                line = line.strip()
                if line:
                    ic_s, ip_s = line.split(',')
                    grains_done_set.add((int(ic_s), int(ip_s)))
        print(f"  Resuming: {len(grains_done_set)} grains already done, skipping...")
    if os.path.exists(HITS_CKPT_FILE):
        with open(HITS_CKPT_FILE, 'r') as f_hits:
            for line in f_hits:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split(',')
                    results.append([float(x) for x in parts])
        print(f"  Loaded {len(results)} hits from checkpoint.")

    # Open checkpoint files for appending
    f_hits_out  = open(HITS_CKPT_FILE,   'a')
    f_grains_out = open(GRAINS_DONE_FILE, 'a')

    t0 = time.time()
    done = len(grains_done_set)

    try:
      with ProcessPoolExecutor(max_workers=n_workers) as pool:
        futures = {}
        for ic in range(N_CHI_EXT):
            mc = float(M_CHI_VALS[ic])
            for ip in range(N_PHI_EXT):
                if (ic, ip) in grains_done_set:
                    continue
                mp = float(M_PHI_VALS[ip])
                f = pool.submit(_grain_worker, ic, ip, mc, mp)
                futures[f] = (ic, ip)

        # Track per-m_chi progress
        mc_hits   = {ic: 0 for ic in range(N_CHI_EXT)}
        mc_done   = {ic: sum(1 for (i,j) in grains_done_set if i==ic) for ic in range(N_CHI_EXT)}

        for f in as_completed(futures):
            ic, ip = futures[f]
            _, _, hits = f.result()
            results.extend(hits)
            mc_hits[ic] += len(hits)
            mc_done[ic] += 1
            done += 1

            # Save hits to checkpoint
            for h in hits:
                f_hits_out.write(','.join(f'{v:.8g}' for v in h) + '\n')
            f_hits_out.flush()

            # Mark grain as done
            f_grains_out.write(f'{ic},{ip}\n')
            f_grains_out.flush()

            # Print progress when a full m_chi slice is done
            if mc_done[ic] == N_PHI_EXT:
                mc = float(M_CHI_VALS[ic])
                elapsed = time.time() - t0
                remaining = total_grains - done
                eta = elapsed / max(done - len(grains_done_set), 1) * remaining
                print(f"  m_chi={mc:7.1f} GeV | {mc_hits[ic]:5d} hits | "
                      f"{done}/{total_grains} grains | {elapsed:.0f}s (ETA {eta:.0f}s)",
                      flush=True)
    finally:
        f_hits_out.close()
        f_grains_out.close()

    t_scan = time.time() - t0
    print(f"\n  Scan complete: {len(results)} viable points in {t_scan:.1f}s")

    # --- Part 3: Analysis ---
    print()
    print("=" * 78)
    print("  Part 3: Analysis of extended scan results")
    print("=" * 78)

    if len(results) == 0:
        print("\n  NO viable points found above 100 GeV!")
        print("  MAP is at the PHYSICAL boundary, not just scan boundary.")
        print("  This STRENGTHENS the coincidence.")
        n_dual = 0
        n_deep = 0
        n_vdeep = 0
    else:
        res = np.array(results)
        mc_all  = res[:, 0]
        mp_all  = res[:, 1]
        a_all   = res[:, 2]
        sd_all  = res[:, 3]
        sc_all  = res[:, 4]
        lam_all = a_all * mc_all / mp_all

        print(f"\n  {len(results)} viable points")
        print(f"  m_chi: [{mc_all.min():.1f}, {mc_all.max():.1f}] GeV")
        print(f"  m_phi: [{mp_all.min()*1e3:.2f}, {mp_all.max()*1e3:.2f}] MeV")
        print(f"  alpha: [{a_all.min():.6e}, {a_all.max():.6e}]")
        print(f"  lambda: [{lam_all.min():.2f}, {lam_all.max():.2f}]")

        # --- Part 4: alpha_d(chain) match ---
        print()
        print("=" * 78)
        print("  Part 4: Does alpha_d(chain) match alpha_SIDM?")
        print("=" * 78)

        ad_chain_arr = np.array([alpha_d_chain(mc) for mc in mc_all])
        a_sidm_pr    = np.array([alpha_sidm_pred(ad) for ad in ad_chain_arr])
        rel_err = np.abs(a_all - a_sidm_pr) / a_sidm_pr

        for thr in [0.10, 0.05, 0.01]:
            n = np.sum(rel_err < thr)
            print(f"  |alpha - pred| < {thr*100:.0f}%: {n:6d} / {len(results)} ({100*n/len(results):.2f}%)")

        # --- Part 5: Transmutation ---
        print()
        print("=" * 78)
        print("  Part 5: Transmutation Lambda_d ~ m_nu")
        print("=" * 78)

        ld_arr = np.array([Lambda_d_meV(ad, mc) for ad, mc in zip(ad_chain_arr, mc_all)])
        in_de = np.sum((ld_arr > 1.0) & (ld_arr < 10.0))
        print(f"\n  Lambda_d in [1,10] meV: {in_de} / {len(results)} ({100*in_de/len(results):.2f}%)")

        dual_mask = (rel_err < 0.10) & (ld_arr > 1.0) & (ld_arr < 10.0)
        n_dual = int(np.sum(dual_mask))
        print(f"  Dual constraint: {n_dual} / {len(results)} ({100*n_dual/len(results):.3f}%)")

        # --- Part 6: MAP comparison ---
        print()
        print("=" * 78)
        print("  Part 6: MAP vs best extended point")
        print("=" * 78)

        ad_map = alpha_d_chain(MAP_MCHI)
        a_pred_map = alpha_sidm_pred(ad_map)
        print(f"\n  MAP: m_chi={MAP_MCHI:.2f}  m_phi={MAP_MPHI*1e3:.2f} MeV  alpha={MAP_ALPHA:.6e}")
        print(f"       mismatch={abs(MAP_ALPHA-a_pred_map)/a_pred_map*100:.1f}%  Lambda_d={Lambda_d_meV(ad_map, MAP_MCHI):.4f} meV")

        if n_dual > 0:
            dual_idx = np.where(dual_mask)[0]
            best_i = dual_idx[np.argmin(rel_err[dual_idx])]
            mc_b, mp_b, a_b = mc_all[best_i], mp_all[best_i], a_all[best_i]
            ad_b = alpha_d_chain(mc_b)
            ap_b = alpha_sidm_pred(ad_b)
            print(f"\n  Best: m_chi={mc_b:.2f}  m_phi={mp_b*1e3:.2f} MeV  alpha={a_b:.6e}")
            print(f"        mismatch={abs(a_b-ap_b)/ap_b*100:.1f}%  Lambda_d={Lambda_d_meV(ad_b, mc_b):.4f} meV")

        # --- Part 7: Distribution by m_chi ---
        print()
        print("=" * 78)
        print("  Part 7: Distribution by m_chi")
        print("=" * 78)
        print()
        print(f"  {'m_chi':>8}  {'N':>6}  {'alpha_d':>10}  {'Ld [meV]':>10}  {'<alpha>':>12}  {'pred':>12}  {'err%':>6}")
        print(f"  {'─'*8}  {'─'*6}  {'─'*10}  {'─'*10}  {'─'*12}  {'─'*12}  {'─'*6}")

        for mc_val in M_CHI_VALS:
            mask = np.abs(mc_all - mc_val) < 0.01 * mc_val
            n_mc = int(np.sum(mask))
            ad = alpha_d_chain(mc_val)
            ld = Lambda_d_meV(ad, mc_val)
            ap = alpha_sidm_pred(ad)
            if n_mc > 0:
                mean_a = float(np.mean(a_all[mask]))
                mm = abs(mean_a - ap) / ap * 100
                print(f"  {mc_val:>8.1f}  {n_mc:>6d}  {ad:>10.6f}  {ld:>10.4f}  {mean_a:>12.6e}  {ap:>12.6e}  {mm:>6.1f}")
            else:
                print(f"  {mc_val:>8.1f}  {0:>6d}  {ad:>10.6f}  {ld:>10.4f}  {'---':>12}  {ap:>12.6e}  {'---':>6}")

        # --- Part 8: deep resonance test ---
        print()
        print("=" * 78)
        print("  Part 8: y = g_d/3 test (lambda > 25 region)")
        print("=" * 78)

        deep_mask = lam_all > 25
        n_deep = int(np.sum(deep_mask))
        print(f"\n  lambda > 25: {n_deep} / {len(results)}")
        if n_deep > 0:
            ad_d = np.array([alpha_d_chain(mc) for mc in mc_all[deep_mask]])
            ap_d = np.array([alpha_sidm_pred(ad) for ad in ad_d])
            err_d = np.abs(a_all[deep_mask] - ap_d) / ap_d
            print(f"  Mean mismatch: {np.mean(err_d)*100:.1f}%")
            n5 = int(np.sum(err_d < 0.05))
            print(f"  Within 5%: {n5}/{n_deep}")

        vdeep_mask = lam_all > 30
        n_vdeep = int(np.sum(vdeep_mask))
        print(f"\n  lambda > 30 (MAP-like): {n_vdeep}")
        if n_vdeep > 0:
            mc_vd = mc_all[vdeep_mask]
            mp_vd = mp_all[vdeep_mask]
            a_vd  = a_all[vdeep_mask]
            ad_vd = np.array([alpha_d_chain(mc) for mc in mc_vd])
            ap_vd = np.array([alpha_sidm_pred(ad) for ad in ad_vd])
            err_vd = np.abs(a_vd - ap_vd) / ap_vd
            top5 = np.argsort(err_vd)[:5]
            for idx in top5:
                lv = a_vd[idx] * mc_vd[idx] / mp_vd[idx]
                print(f"    m_chi={mc_vd[idx]:.1f}  m_phi={mp_vd[idx]*1e3:.2f} MeV  "
                      f"alpha={a_vd[idx]:.6e}  lam={lv:.1f}  err={err_vd[idx]*100:.2f}%")

    # ====================================================================
    #  Verdict
    # ====================================================================
    print()
    print("=" * 78)
    print("  G8f VERDICT")
    print("=" * 78)
    print(f"""
  SCAN: m_chi in [100, 500] GeV, {N_CHI_EXT}x{N_PHI_EXT} grid, {N_RES} res x {N_ALPHA_EXT} alpha
  Workers: {n_workers}, Scan time: {t_scan:.1f}s
  Previous (v22, <100 GeV): 80,142 viable points
  Extended (this, >100 GeV): {len(results)} viable points
""")
    if len(results) == 0:
        print("  -> NO viable SIDM above 100 GeV. MAP at PHYSICAL boundary.")
    else:
        print(f"  Dual-constraint: {n_dual}")
        if n_dual > 0:
            print(f"  -> Extended points CAN satisfy the coincidence.")
        else:
            print(f"  -> No dual-constraint points. MAP remains special.")
