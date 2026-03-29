"""
C2: 2D scan over (theta_i, f) to find the region satisfying BOTH:
  - H0 in [66, 74] km/s/Mpc  (Planck + SH0ES range)
  - wa in [-1.3, -0.6]       (DESI+CMB+Union3/DESY5 2-sigma)

1D scan showed:
  theta_i=2.8: wa=-0.865 (DESI OK), H0=62 (too low)
  theta_i=2.9: H0=67.1  (Planck OK), wa=-0.44 (DESI too weak)

Physical expectation: larger f -> heavier sigma -> slower rolling -> 
  wa more negative (DESI-compatible) at the same H0.
  So increasing f at theta_i~2.9 should bring wa toward -0.87.
"""

import numpy as np
import sys, os
from scipy.optimize import curve_fit

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(_ROOT, 'core'))
_HUNT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HUNT)

from layer8_cosmic_ode import (
    solve_layer8, V_sigma, M_PL, H_100_GEV,
    OMEGA_R_H2, OMEGA_B_H2, _RHO_UNIT
)

# ── fixed model params ──────────────────────────────────────────────────
M_CHI   = 98.19
M_PHI   = 9.66e-3
ALPHA_D = 3.274e-3
OMEGA   = 0.120
LD      = 2.0e-12   # Lambda_d = 2 meV

# ── constraint windows ──────────────────────────────────────────────────
H0_MIN, H0_MAX = 66.0, 74.0        # km/s/Mpc
WA_MIN, WA_MAX = -1.30, -0.60      # DESI 2-sigma combined

# ── DESI reference ───────────────────────────────────────────────────────
DESI_W0, DESI_W0_ERR = -0.727, 0.067
DESI_WA, DESI_WA_ERR = -1.05,  0.29   # avg of +0.31/-0.27


def extract_w_and_fit(res, f):
    sol = res.sol
    N_arr = np.linspace(max(sol.t[0], -5.0), 0.0, 500)
    Y_arr = sol.sol(N_arr)
    sigma_arr, p_arr = Y_arr[0], Y_arr[1]
    a_arr = np.exp(N_arr)

    rho_r0 = OMEGA_R_H2 * _RHO_UNIT
    rho_m0 = (res.omega_chi_h2 + OMEGA_B_H2) * _RHO_UNIT
    rho_r  = rho_r0 * a_arr**(-4)
    rho_m  = rho_m0 * a_arr**(-3)
    V_arr  = V_sigma(sigma_arr, f, LD)

    denom  = 3.0 * M_PL**2 - 0.5 * p_arr**2
    H2_arr = np.where(denom > 0, (rho_r + rho_m + V_arr) / denom, 1e-100)
    rho_s  = 0.5 * H2_arr * p_arr**2 + V_arr
    P_s    = 0.5 * H2_arr * p_arr**2 - V_arr
    w_arr  = np.where(rho_s > 0, P_s / rho_s, -1.0)

    a_min = 1.0 / 3.0          # z < 2
    mask  = a_arr > a_min
    a_fit, w_fit = a_arr[mask], w_arr[mask]

    def cpl(a, w0, wa):
        return w0 + wa * (1.0 - a)
    try:
        popt, _ = curve_fit(cpl, a_fit, w_fit, p0=[-0.9, -0.5])
        return popt[0], popt[1]
    except Exception:
        x = 1.0 - a_fit
        c = np.polyfit(x, w_fit, 1)
        return c[1], c[0]


def run_point(theta_i, f):
    try:
        r = solve_layer8(M_CHI, M_PHI, ALPHA_D, f, LD, theta_i,
                         omega_chi_h2=OMEGA, verbose=False)
        if r.H0_kms is None or r.H0_kms < 10:
            return None
        w0, wa = extract_w_and_fit(r, f)
        return r.H0_kms, r.Omega_DE, w0, wa
    except Exception:
        return None


# ── GRID ────────────────────────────────────────────────────────────────
# theta_i: from the 1D scan, DESI-compatible range is ~2.7-2.95
# f: current value is 0.27 M_Pl; physical range 0.1-0.5 M_Pl
THETA_GRID = np.linspace(2.70, 3.05, 22)
F_FRAC     = np.array([0.15, 0.18, 0.21, 0.24, 0.27, 0.30, 0.33, 0.36,
                        0.40, 0.45, 0.50])   # f / M_Pl

print("=" * 72)
print("  C2: 2D scan (theta_i, f)  —  looking for DESI + Planck window")
print("=" * 72)
print(f"  H0 window: [{H0_MIN}, {H0_MAX}] km/s/Mpc")
print(f"  wa window: [{WA_MIN}, {WA_MAX}]")
print(f"  Grid: {len(THETA_GRID)} x {len(F_FRAC)} = {len(THETA_GRID)*len(F_FRAC)} points")
print()

# ── run ─────────────────────────────────────────────────────────────────
good   = []   # both constraints satisfied
h0ok   = []   # only H0
waok   = []   # only wa
all_pts = []

for f_frac in F_FRAC:
    f_val = f_frac * M_PL
    for th in THETA_GRID:
        res = run_point(th, f_val)
        if res is None:
            continue
        H0, OmDE, w0, wa = res
        h0_pass = H0_MIN <= H0 <= H0_MAX
        wa_pass = WA_MIN <= wa <= WA_MAX
        all_pts.append((th, f_frac, H0, w0, wa, h0_pass, wa_pass))
        if h0_pass and wa_pass:
            good.append((th, f_frac, H0, w0, wa))
        elif h0_pass:
            h0ok.append((th, f_frac, H0, w0, wa))
        elif wa_pass:
            waok.append((th, f_frac, H0, w0, wa))

# ── results ──────────────────────────────────────────────────────────────
print(f"  Total computed: {len(all_pts)} points")
print(f"  BOTH constraints: {len(good)}")
print(f"  H0 only: {len(h0ok)}")
print(f"  wa only: {len(waok)}")
print()

if good:
    print("=" * 72)
    print("  *** GOLDEN POINTS (both H0 and wa satisfied) ***")
    print("=" * 72)
    print(f"  {'theta_i':>8s}  {'f/MPl':>6s}  {'H0':>7s}  {'w0(CPL)':>9s}  {'wa(CPL)':>9s}")
    print("  " + "-" * 50)
    for pt in sorted(good, key=lambda x: abs(x[2]-70)):
        th, ff, H0, w0, wa = pt
        print(f"  {th:8.4f}  {ff:6.3f}  {H0:7.2f}  {w0:9.4f}  {wa:9.4f}")
else:
    print("  No golden points found — showing closest approach:")

    # Find point with best combined score
    def score(pt):
        th, ff, H0, w0, wa, hp, wp = pt
        dH = max(0, H0_MIN - H0, H0 - H0_MAX) / 4.0      # normalized
        dwa = max(0, WA_MIN - wa, wa - WA_MAX) / 0.35     # normalized
        return dH**2 + dwa**2

    all_pts_sorted = sorted(all_pts, key=score)
    print(f"  {'theta_i':>8s}  {'f/MPl':>6s}  {'H0':>7s}  {'w0(CPL)':>9s}  {'wa(CPL)':>9s}  {'H0 ok':>6s}  {'wa ok':>6s}")
    print("  " + "-" * 65)
    for pt in all_pts_sorted[:15]:
        th, ff, H0, w0, wa, hp, wp = pt
        print(f"  {th:8.4f}  {ff:6.3f}  {H0:7.2f}  {w0:9.4f}  {wa:9.4f}  {'✓' if hp else '✗':>6s}  {'✓' if wp else '✗':>6s}")

# ── per-f slice summary ───────────────────────────────────────────────────
print()
print("=" * 72)
print("  Per-f slice: best (theta_i, H0, wa) for each f value")
print("=" * 72)
print(f"  {'f/MPl':>6s}  {'best_theta':>10s}  {'H0':>7s}  {'wa':>8s}  status")
print("  " + "-" * 55)

for f_frac in F_FRAC:
    pts = [(th, H0, w0, wa, hp, wp)
           for th, ff, H0, w0, wa, hp, wp in all_pts if abs(ff - f_frac) < 0.001]
    if not pts:
        continue
    # find theta with H0 closest to 70 among wa-ok ones
    wa_pts = [(th, H0, w0, wa) for th, H0, w0, wa, hp, wp in pts if wp]
    if wa_pts:
        best = min(wa_pts, key=lambda x: abs(x[1] - 70.0))
        th, H0, w0, wa = best
        hp = H0_MIN <= H0 <= H0_MAX
        tag = "GOLDEN" if hp else "wa only"
        print(f"  {f_frac:6.3f}  {th:10.4f}  {H0:7.2f}  {wa:8.4f}  {tag}")
    else:
        # show H0-closest
        best = min(pts, key=lambda x: abs(x[1] - 70.0))
        th, H0, w0, wa, hp, wp = best
        print(f"  {f_frac:6.3f}  {th:10.4f}  {H0:7.2f}  {wa:8.4f}  no-wa")

# ── physical interpretation ────────────────────────────────────────────
print()
print("=" * 72)
print("  Physical insight: f vs wa at fixed H0~67")
print("=" * 72)
# Show for theta points near H0~67
h67 = [(th, ff, H0, w0, wa) for th, ff, H0, w0, wa, hp, wp in all_pts
       if 65 < H0 < 69]
h67.sort(key=lambda x: x[1])
if h67:
    print(f"  {'theta_i':>8s}  {'f/MPl':>6s}  {'H0':>7s}  {'wa':>8s}")
    for th, ff, H0, w0, wa in h67:
        marker = " <-- DESI window" if WA_MIN <= wa <= WA_MAX else ""
        print(f"  {th:8.4f}  {ff:6.3f}  {H0:7.2f}  {wa:8.4f}{marker}")
