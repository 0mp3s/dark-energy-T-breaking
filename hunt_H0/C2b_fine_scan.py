"""
C2b-1+2: Fine scan around golden point (theta_i=3.017, f=0.21 MPl)
+ check Omega_DE, Omega_DM at golden point.
"""
import numpy as np
import sys, os
from scipy.optimize import curve_fit

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(_ROOT, 'core'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layer8_cosmic_ode import (
    solve_layer8, V_sigma, M_PL, OMEGA_R_H2, OMEGA_B_H2, _RHO_UNIT
)

M_CHI, M_PHI, ALPHA_D, OMEGA, LD = 98.19, 9.66e-3, 3.274e-3, 0.120, 2.0e-12
H0_MIN, H0_MAX = 66.0, 74.0
WA_MIN, WA_MAX = -1.30, -0.60


def extract_w_and_fit(res, f):
    sol = res.sol
    N_arr = np.linspace(max(sol.t[0], -5.0), 0.0, 500)
    Y_arr = sol.sol(N_arr)
    sigma_arr, p_arr = Y_arr[0], Y_arr[1]
    a_arr = np.exp(N_arr)
    rho_r0 = OMEGA_R_H2 * _RHO_UNIT
    rho_m0 = (res.omega_chi_h2 + OMEGA_B_H2) * _RHO_UNIT
    rho_r = rho_r0 * a_arr**(-4)
    rho_m = rho_m0 * a_arr**(-3)
    V_arr = V_sigma(sigma_arr, f, LD)
    denom = 3.0 * M_PL**2 - 0.5 * p_arr**2
    H2_arr = np.where(denom > 0, (rho_r + rho_m + V_arr) / denom, 1e-100)
    rho_s = 0.5 * H2_arr * p_arr**2 + V_arr
    P_s   = 0.5 * H2_arr * p_arr**2 - V_arr
    w_arr = np.where(rho_s > 0, P_s / rho_s, -1.0)
    mask  = a_arr > 1.0/3.0
    a_fit, w_fit = a_arr[mask], w_arr[mask]
    def cpl(a, w0, wa): return w0 + wa*(1.0-a)
    try:
        popt, _ = curve_fit(cpl, a_fit, w_fit, p0=[-0.9, -0.5])
        return popt[0], popt[1]
    except Exception:
        c = np.polyfit(1.0-a_fit, w_fit, 1)
        return c[1], c[0]


def run_point(th, f_val):
    try:
        r = solve_layer8(M_CHI, M_PHI, ALPHA_D, f_val, LD, th,
                         omega_chi_h2=OMEGA, verbose=False)
        if r.H0_kms is None or r.H0_kms < 10:
            return None
        w0, wa = extract_w_and_fit(r, f_val)
        return r.H0_kms, r.Omega_DE, r.omega_chi_h2, w0, wa
    except Exception:
        return None


# ── C2b-2: Omega check at golden point ─────────────────────────────────
print("=" * 65)
print("  C2b-2: Omega_DE + Omega_DM at golden point")
print("=" * 65)
f_gold = 0.21 * M_PL
th_gold = 3.0167

r_gold = solve_layer8(M_CHI, M_PHI, ALPHA_D, f_gold, LD, th_gold,
                      omega_chi_h2=OMEGA, verbose=False)
w0_gold, wa_gold = extract_w_and_fit(r_gold, f_gold)

print(f"  theta_i    = {th_gold:.4f}")
print(f"  f/MPl      = 0.21")
print(f"  H0         = {r_gold.H0_kms:.2f} km/s/Mpc  [target: 66-74]")
print(f"  Omega_DE   = {r_gold.Omega_DE:.4f}         [target: ~0.69]")
print(f"  Omega_chi  = {r_gold.omega_chi_h2/r_gold.H0_kms*100/r_gold.H0_kms*100:.4f}  (Omega_chi_h2={r_gold.omega_chi_h2:.4f})")
print(f"  w0 (CPL)   = {w0_gold:.4f}")
print(f"  wa (CPL)   = {wa_gold:.4f}         [target: -1.3 to -0.6]")
h0_ok = H0_MIN <= r_gold.H0_kms <= H0_MAX
wa_ok = WA_MIN <= wa_gold <= WA_MAX
print(f"  H0 ok: {'✅' if h0_ok else '❌'}   wa ok: {'✅' if wa_ok else '❌'}")

# Compute Omega_m properly
h2 = (r_gold.H0_kms / 100.0)**2
omega_m_h2 = r_gold.omega_chi_h2 + OMEGA_B_H2
Omega_m = omega_m_h2 / h2
print(f"  Omega_m    = {Omega_m:.4f}         [target: ~0.31]")
print(f"  Omega_DE + Omega_m = {r_gold.Omega_DE + Omega_m:.4f}  [should be ~1.0]")
print()

# ── C2b-1: Fine scan ────────────────────────────────────────────────────
print("=" * 65)
print("  C2b-1: Fine scan 30×20 around golden point")
print("=" * 65)

THETA_FINE = np.linspace(2.95, 3.10, 31)
F_FINE     = np.linspace(0.18, 0.24, 21)

good, all_pts = [], []
for f_frac in F_FINE:
    f_val = f_frac * M_PL
    for th in THETA_FINE:
        res = run_point(th, f_val)
        if res is None:
            continue
        H0, OmDE, omchi, w0, wa = res
        hp = H0_MIN <= H0 <= H0_MAX
        wp = WA_MIN <= wa <= WA_MAX
        all_pts.append((th, f_frac, H0, OmDE, w0, wa, hp, wp))
        if hp and wp:
            good.append((th, f_frac, H0, OmDE, w0, wa))

print(f"  Grid: {len(THETA_FINE)}×{len(F_FINE)} = {len(THETA_FINE)*len(F_FINE)} pts  |  computed: {len(all_pts)}")
print(f"  Golden region (both): {len(good)} points")
print()

if good:
    print(f"  {'theta_i':>8s}  {'f/MPl':>6s}  {'H0':>7s}  {'Omega_DE':>9s}  {'w0':>8s}  {'wa':>8s}")
    print("  " + "-" * 60)
    for pt in sorted(good, key=lambda x: (round(x[1],3), x[0])):
        th, ff, H0, OmDE, w0, wa = pt
        print(f"  {th:8.4f}  {ff:6.3f}  {H0:7.2f}  {OmDE:9.4f}  {w0:8.4f}  {wa:8.4f}")

    # Summary of golden region extent
    ths = [p[0] for p in good]
    ffs = [p[1] for p in good]
    H0s = [p[2] for p in good]
    was = [p[5] for p in good]
    print(f"\n  Golden region extent:")
    print(f"    theta_i: [{min(ths):.4f}, {max(ths):.4f}]  (width={max(ths)-min(ths):.4f})")
    print(f"    f/MPl:   [{min(ffs):.3f}, {max(ffs):.3f}]  (width={max(ffs)-min(ffs):.3f})")
    print(f"    H0:      [{min(H0s):.1f}, {max(H0s):.1f}] km/s/Mpc")
    print(f"    wa:      [{min(was):.3f}, {max(was):.3f}]")
else:
    print("  No golden points in fine grid — showing closest 10:")
    def score(pt):
        th, ff, H0, OmDE, w0, wa, hp, wp = pt
        dH  = max(0, H0_MIN-H0, H0-H0_MAX) / 4.0
        dwa = max(0, WA_MIN-wa, wa-WA_MAX) / 0.35
        return dH**2 + dwa**2
    for pt in sorted(all_pts, key=score)[:10]:
        th, ff, H0, OmDE, w0, wa, hp, wp = pt
        print(f"  {th:.4f}  f={ff:.3f}  H0={H0:.1f}  wa={wa:.3f}  {'H0✅' if hp else 'H0❌'} {'wa✅' if wp else 'wa❌'}")

print()
print("=" * 65)
print("  C2b-2 VERDICT")
print("=" * 65)
omDE_ok = 0.64 <= r_gold.Omega_DE <= 0.74
omm_ok  = 0.25 <= Omega_m <= 0.37
print(f"  Omega_DE = {r_gold.Omega_DE:.4f}  {'✅ in [0.64,0.74]' if omDE_ok else '❌ outside'}")
print(f"  Omega_m  = {Omega_m:.4f}  {'✅ in [0.25,0.37]' if omm_ok else '❌ outside'}")
print(f"  Sum      = {r_gold.Omega_DE+Omega_m:.4f}  {'✅ ~1' if abs(r_gold.Omega_DE+Omega_m-1)<0.05 else '⚠️ check'}")
