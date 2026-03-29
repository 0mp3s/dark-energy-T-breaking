"""
G8f_analyze.py  — analyze whatever is in G8f_hits_checkpoint.csv
=================================================================
Can be run at any time (mid-scan or after completion).
Reads: G8f_hits_checkpoint.csv  (m_chi, m_phi, alpha, sd, sc, ires)
       G8f_grains_done.txt       (ic,ip pairs)
"""

import math
import os
import numpy as np

# ── constants (same as G8f_extended_scan_mp.py) ──────────────────────────────
B0          = 19.0 / 3.0
V_EW        = 246.22
M_R_GUT     = 2e16
MEV_CONV    = 1e12

MAP_MCHI   = 98.19
MAP_ALPHA  = 3.274e-3
MAP_MPHI   = 9.66e-3

N_CHI_EXT  = 10
N_PHI_EXT  = 20
M_CHI_VALS = np.logspace(np.log10(100.0), np.log10(500.0), N_CHI_EXT)

HERE = os.path.dirname(os.path.abspath(__file__))
HITS_FILE   = os.path.join(HERE, 'G8f_hits_checkpoint.csv')
GRAINS_FILE = os.path.join(HERE, 'G8f_grains_done.txt')

def Lambda_d_meV(alpha_d, m_chi_GeV):
    exp_arg = -2 * math.pi / (B0 * alpha_d)
    if exp_arg < -700:
        return 0.0
    return m_chi_GeV * math.exp(exp_arg) * MEV_CONV

m_nu_target = V_EW**2 / M_R_GUT * MEV_CONV   # ~3.031 meV

def alpha_d_chain(m_chi_GeV):
    arg = m_chi_GeV * M_R_GUT / V_EW**2
    if arg <= 1:
        return 0.0
    return 2 * math.pi / (B0 * math.log(arg))

def alpha_sidm_pred(alpha_d_val):
    return (8.0 / 81.0) * alpha_d_val

# ── load data ─────────────────────────────────────────────────────────────────
print("=" * 78)
print("  G8f_analyze — partial/full checkpoint analysis")
print("=" * 78)

if not os.path.exists(HITS_FILE):
    print(f"\n  ERROR: {HITS_FILE} not found. Run G8f_extended_scan_mp.py first.")
    exit(1)

rows = []
with open(HITS_FILE, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            parts = line.split(',')
            rows.append([float(x) for x in parts])

n_grains_done = 0
if os.path.exists(GRAINS_FILE):
    with open(GRAINS_FILE, 'r') as f:
        n_grains_done = sum(1 for ln in f if ln.strip())

total_grains = N_CHI_EXT * N_PHI_EXT
pct_done = 100.0 * n_grains_done / total_grains

print(f"\n  Checkpoint: {n_grains_done}/{total_grains} grains done ({pct_done:.1f}%)")
print(f"  Total hits: {len(rows)}")

if len(rows) == 0:
    print("\n  No data yet.")
    exit(0)

res     = np.array(rows)
mc_all  = res[:, 0]
mp_all  = res[:, 1]
a_all   = res[:, 2]
sd_all  = res[:, 3]
sc_all  = res[:, 4]
ires_all = res[:, 5].astype(int)
lam_all = a_all * mc_all / mp_all

# ── Part 3: summary ───────────────────────────────────────────────────────────
print()
print("=" * 78)
print("  Part 3: Summary of available data")
print("=" * 78)
print(f"\n  {len(rows)} viable points")
print(f"  m_chi: [{mc_all.min():.1f}, {mc_all.max():.1f}] GeV")
print(f"  m_phi: [{mp_all.min()*1e3:.2f}, {mp_all.max()*1e3:.2f}] MeV")
print(f"  alpha: [{a_all.min():.4e}, {a_all.max():.4e}]")
print(f"  lambda: [{lam_all.min():.2f}, {lam_all.max():.2f}]")

# ── Part 4: alpha_d(chain) match ──────────────────────────────────────────────
print()
print("=" * 78)
print("  Part 4: alpha_d(chain) match")
print("=" * 78)

ad_chain_arr = np.array([alpha_d_chain(mc) for mc in mc_all])
a_sidm_pr    = np.array([alpha_sidm_pred(ad) for ad in ad_chain_arr])
rel_err      = np.abs(a_all - a_sidm_pr) / a_sidm_pr

print()
for thr in [0.10, 0.05, 0.01]:
    n = np.sum(rel_err < thr)
    print(f"  |alpha - pred| < {thr*100:.0f}%: {n:6d} / {len(rows)} ({100*n/len(rows):.2f}%)")

# ── Part 5: transmutation ─────────────────────────────────────────────────────
print()
print("=" * 78)
print("  Part 5: Transmutation Lambda_d ~ m_nu")
print("=" * 78)

ld_arr = np.array([Lambda_d_meV(ad, mc) for ad, mc in zip(ad_chain_arr, mc_all)])
in_de  = np.sum((ld_arr > 1.0) & (ld_arr < 10.0))
print(f"\n  Lambda_d in [1,10] meV: {in_de} / {len(rows)} ({100*in_de/len(rows):.2f}%)")

dual_mask = (rel_err < 0.10) & (ld_arr > 1.0) & (ld_arr < 10.0)
n_dual = int(np.sum(dual_mask))
print(f"  Dual constraint:        {n_dual} / {len(rows)} ({100*n_dual/len(rows):.3f}%)")

# ── Part 6: MAP comparison ────────────────────────────────────────────────────
print()
print("=" * 78)
print("  Part 6: MAP vs extended points")
print("=" * 78)

ad_map     = alpha_d_chain(MAP_MCHI)
a_pred_map = alpha_sidm_pred(ad_map)
ld_map     = Lambda_d_meV(ad_map, MAP_MCHI)
err_map    = abs(MAP_ALPHA - a_pred_map) / a_pred_map * 100

print(f"\n  MAP: m_chi={MAP_MCHI:.2f} GeV  m_phi={MAP_MPHI*1e3:.2f} MeV  alpha={MAP_ALPHA:.4e}")
print(f"       pred={a_pred_map:.4e}  mismatch={err_map:.1f}%  Lambda_d={ld_map:.4f} meV")

if n_dual > 0:
    dual_idx = np.where(dual_mask)[0]
    best_i   = dual_idx[np.argmin(rel_err[dual_idx])]
    mc_b, mp_b, a_b = mc_all[best_i], mp_all[best_i], a_all[best_i]
    ad_b = alpha_d_chain(mc_b)
    ap_b = alpha_sidm_pred(ad_b)
    ld_b = Lambda_d_meV(ad_b, mc_b)
    print(f"\n  Best dual: m_chi={mc_b:.1f} GeV  m_phi={mp_b*1e3:.2f} MeV  alpha={a_b:.4e}")
    print(f"             mismatch={abs(a_b-ap_b)/ap_b*100:.1f}%  Lambda_d={ld_b:.4f} meV")
else:
    print("\n  No dual-constraint points yet in available data.")

# ── Part 7: distribution by m_chi ────────────────────────────────────────────
print()
print("=" * 78)
print("  Part 7: Distribution by m_chi slice")
print("=" * 78)
print()
print(f"  {'m_chi':>8}  {'N_hits':>7}  {'grains':>8}  {'alpha_d':>10}  {'Ld[meV]':>9}  {'<alpha>':>12}  {'pred':>12}  {'err%':>6}")
print(f"  {'─'*8}  {'─'*7}  {'─'*8}  {'─'*10}  {'─'*9}  {'─'*12}  {'─'*12}  {'─'*6}")

# Load grains done per m_chi from grains file
grains_per_chi = {ic: 0 for ic in range(N_CHI_EXT)}
if os.path.exists(GRAINS_FILE):
    with open(GRAINS_FILE, 'r') as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                ic_s, _ = ln.split(',')
                grains_per_chi[int(ic_s)] += 1

for ic, mc_val in enumerate(M_CHI_VALS):
    mask   = np.abs(mc_all - mc_val) < 0.01 * mc_val
    n_mc   = int(np.sum(mask))
    g_done = grains_per_chi[ic]
    ad     = alpha_d_chain(mc_val)
    ld     = Lambda_d_meV(ad, mc_val)
    ap     = alpha_sidm_pred(ad)
    status = "complete" if g_done == N_PHI_EXT else f"{g_done}/{N_PHI_EXT}"
    if n_mc > 0:
        mean_a = float(np.mean(a_all[mask]))
        mm     = abs(mean_a - ap) / ap * 100
        print(f"  {mc_val:>8.1f}  {n_mc:>7d}  {status:>8}  {ad:>10.6f}  {ld:>9.4f}  {mean_a:>12.4e}  {ap:>12.4e}  {mm:>6.1f}")
    else:
        print(f"  {mc_val:>8.1f}  {'---':>7}  {status:>8}  {ad:>10.6f}  {ld:>9.4f}  {'---':>12}  {ap:>12.4e}  {'---':>6}")

# ── Part 8: deep resonance ────────────────────────────────────────────────────
print()
print("=" * 78)
print("  Part 8: Deep resonance (lambda > 25 / > 30)")
print("=" * 78)

deep_mask  = lam_all > 25
n_deep     = int(np.sum(deep_mask))
vdeep_mask = lam_all > 30
n_vdeep    = int(np.sum(vdeep_mask))

print(f"\n  lambda > 25: {n_deep} / {len(rows)}")
if n_deep > 0:
    err_d = rel_err[deep_mask]
    print(f"  Mean mismatch: {np.mean(err_d)*100:.1f}%  |  within 5%: {int(np.sum(err_d<0.05))}/{n_deep}")

print(f"\n  lambda > 30 (MAP-like): {n_vdeep}")
if n_vdeep > 0:
    mc_vd  = mc_all[vdeep_mask]
    mp_vd  = mp_all[vdeep_mask]
    a_vd   = a_all[vdeep_mask]
    err_vd = rel_err[vdeep_mask]
    top5   = np.argsort(err_vd)[:5]
    for idx in top5:
        lv = a_vd[idx] * mc_vd[idx] / mp_vd[idx]
        print(f"    m_chi={mc_vd[idx]:.1f}  m_phi={mp_vd[idx]*1e3:.2f} MeV  "
              f"alpha={a_vd[idx]:.4e}  lam={lv:.1f}  err={err_vd[idx]*100:.2f}%")

# ── Verdict ───────────────────────────────────────────────────────────────────
print()
print("=" * 78)
print("  VERDICT (partial data)")
print("=" * 78)
print(f"\n  Grains done: {n_grains_done}/{total_grains} ({pct_done:.1f}%)")
print(f"  Hits so far: {len(rows)}")
print(f"  Dual-constraint: {n_dual}")
if n_dual > 0:
    print(f"  -> YES — extended points satisfy both SIDM + transmutation")
else:
    print(f"  -> Not yet / NO — MAP may be at physical boundary")
print()
print("  Note: Run again after full scan for complete picture.")
