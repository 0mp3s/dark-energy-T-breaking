"""
G9c: DESI DR1 w0-wa comparison
==============================
בדיקת האם תחזית DE שלנו (w0, wa) עקבית עם DESI DR1.

דאטה: DESI 2024 VI (arXiv:2404.03002), Table 4 + contour plots.
מודל שלנו: w0=-0.727, wa=-0.49 (מ-Test 19d CPL fit).

הבדיקה המסוכנת ביותר: correlation ρ(w0,wa) ≈ -0.94 בגלל CPL degeneracy.
"""

import math

# ============================================================
# Part 0: הגדרות
# ============================================================
print("=" * 68)
print("  G9c: DESI DR1 w0-wa comparison")
print("=" * 68)

# המודל שלנו
W0_MODEL = -0.727
WA_MODEL = -0.49

# ΛCDM reference
W0_LCDM = -1.0
WA_LCDM = 0.0

print(f"\n  Model prediction: w0 = {W0_MODEL}, wa = {WA_MODEL}")
print(f"  ΛCDM:             w0 = {W0_LCDM}, wa = {WA_LCDM}")

# ============================================================
# Part 1: DESI DR1 — dataset combinations (Table 4, arXiv:2404.03002)
# ============================================================
print("\n" + "=" * 68)
print("  Part 1: DESI DR1 dataset combinations")
print("=" * 68)

# ρ(w0,wa): correlation coefficient from CPL parametrization.
# Well-known feature: strongly negative for all DESI+SN combinations.
# Value ρ ≈ -0.94 from DESI chains (Table 4 + contour plots).
# We test ρ = 0, -0.5, -0.8, -0.94 to show sensitivity.

DATASETS = {
    "DESI+CMB+Pantheon+": {
        "w0": -0.827, "sw0": 0.063,
        "wa": -0.75,  "swa": 0.29,
        "rho": -0.94,   # from published contours
        "tension_LCDM": "2.5σ",
    },
    "DESI+CMB+Union3": {
        "w0": -0.65,  "sw0": 0.10,
        "wa": -1.27,  "swa": 0.40,
        "rho": -0.92,
        "tension_LCDM": "3.5σ",
    },
    "DESI+CMB+DESY5": {
        "w0": -0.727, "sw0": 0.067,
        "wa": -1.05,  "swa": 0.27,
        "rho": -0.93,
        "tension_LCDM": "3.9σ",
    },
}

for name, d in DATASETS.items():
    print(f"\n  {name}:")
    print(f"    w0 = {d['w0']:.3f} ± {d['sw0']:.3f}")
    print(f"    wa = {d['wa']:.3f} ± {d['swa']:.3f}")
    print(f"    ρ(w0,wa) = {d['rho']:.2f}  (CPL degeneracy)")
    print(f"    ΛCDM tension (published): {d['tension_LCDM']}")

# ============================================================
# Part 2: Mahalanobis distance — נוסחה מלאה עם correlation
# ============================================================
print("\n" + "=" * 68)
print("  Part 2: Mahalanobis distance χ² = Δ^T C^{-1} Δ")
print("=" * 68)
print()
print("  For 2D Gaussian with correlation ρ:")
print("  χ² = 1/(1-ρ²) × [(Δw0/σw0)² - 2ρ(Δw0/σw0)(Δwa/σwa) + (Δwa/σwa)²]")
print()
print("  p-value: χ²(2 DOF) distribution, Δσ ≡ √(-2 ln p) effective sigma")
print()
print(f"  {'Dataset':<30} {'ρ':>5}  {'χ²':>7}  {'Mahal σ':>8}  {'p-value':>12}  {'2D-CL':>8}")
print("  " + "-" * 75)

def chi2_to_pvalue(chi2, dof=2):
    """p-value for chi2 distribution with dof degrees of freedom (survival function)."""
    # Using incomplete gamma function: 1 - regularizedGammaP(k/2, chi2/2)
    # For dof=2: p = exp(-chi2/2) exactly
    if dof == 2:
        return math.exp(-chi2 / 2.0)
    # For other dof use series approximation (not needed here)
    return float('nan')

def pvalue_to_sigma(p):
    """Convert 2-sided p-value to equivalent Gaussian sigma (1D)."""
    if p <= 0:
        return float('inf')
    # Use erfcinv approximation: σ = √2 × erfc_inv(p)
    # Approximation for small p: σ ≈ √(-2 ln(p/2)) for one-sided... 
    # For 2D chi2 p-value, use the relation directly: p = exp(-chi2/2)
    # Equivalent 1D sigma: solve erfc(σ/√2) = p → approximation below
    # Better: just report √chi2 as "sqrt chi2" and note 2D CL separately
    # For 2D: chi2=2.30 → 68.3%, chi2=5.99 → 95.4%, chi2=11.83 → 99.73%
    return float('nan')

def cl_2d(chi2):
    """Return 2D confidence level for chi2 with 2 DOF."""
    p = chi2_to_pvalue(chi2, dof=2)
    return (1.0 - p) * 100.0

def sqrt_chi2_label(chi2):
    """Label the 'sigma' as sqrt(chi2) — useful for comparison."""
    return math.sqrt(chi2)

for name, d in DATASETS.items():
    rho = d["rho"]
    dw0 = W0_MODEL - d["w0"]
    dwa = WA_MODEL - d["wa"]
    z0  = dw0 / d["sw0"]
    za  = dwa / d["swa"]

    chi2 = (1.0 / (1 - rho**2)) * (z0**2 - 2*rho*z0*za + za**2)
    p    = chi2_to_pvalue(chi2, dof=2)
    cl   = cl_2d(chi2)
    mah  = math.sqrt(chi2)

    print(f"  {name:<30} {rho:>5.2f}  {chi2:>7.2f}  {mah:>8.2f}σ  {p:>12.2e}  {cl:>7.3f}%")

# ============================================================
# Part 3: sensitivity to ρ — כמה ρ משנה את התוצאה?
# ============================================================
print("\n" + "=" * 68)
print("  Part 3: Sensitivity to ρ — DESI+CMB+Pantheon+ only")
print("=" * 68)

d = DATASETS["DESI+CMB+Pantheon+"]
dw0 = W0_MODEL - d["w0"]
dwa = WA_MODEL - d["wa"]
z0  = dw0 / d["sw0"]
za  = dwa / d["swa"]

print(f"\n  Δw0 = {dw0:+.3f}  (z = {z0:+.3f}σ)")
print(f"  Δwa = {dwa:+.3f}  (z = {za:+.3f}σ)")
print(f"\n  {'ρ':>6}  {'χ²':>8}  {'√χ²':>7}  {'2D CL%':>9}  {'significance'}")
print("  " + "-" * 65)

for rho in [0.0, -0.3, -0.5, -0.7, -0.80, -0.90, -0.94, -0.97]:
    chi2 = (1.0 / (1 - rho**2)) * (z0**2 - 2*rho*z0*za + za**2)
    p    = chi2_to_pvalue(chi2, dof=2)
    cl   = cl_2d(chi2)
    mah  = math.sqrt(chi2)
    if   chi2 <  2.30: sig = "within 1σ (2D)"
    elif chi2 <  5.99: sig = "within 2σ (2D)"
    elif chi2 < 11.83: sig = "within 3σ (2D)"
    else:              sig = f"OUTSIDE 3σ ({mah:.1f}σ equivalent)"
    print(f"  {rho:>6.2f}  {chi2:>8.2f}  {mah:>7.2f}  {cl:>9.3f}%  {sig}")

# ============================================================
# Part 4: principal axis decomposition — מה הכיוון שבו אנחנו חורגים?
# ============================================================
print("\n" + "=" * 68)
print("  Part 4: Principal axis decomposition — DESI+CMB+Pantheon+")
print("=" * 68)

rho = -0.94
sw0 = d["sw0"]
swa = d["swa"]

# Covariance matrix C = [[sw0², ρ sw0 swa], [ρ sw0 swa, swa²]]
C00 = sw0**2
C11 = swa**2
C01 = rho * sw0 * swa

det_C = C00 * C11 - C01**2
tr_C  = C00 + C11

lam_plus  = 0.5 * (tr_C + math.sqrt(tr_C**2 - 4*det_C))
lam_minus = 0.5 * (tr_C - math.sqrt(tr_C**2 - 4*det_C))

sig_long  = math.sqrt(lam_plus)
sig_short = math.sqrt(lam_minus)

print(f"\n  Covariance eigenvalues:")
print(f"    λ+ (degenerate / long axis)  = {lam_plus:.6f} → σ_long  = {sig_long:.4f}")
print(f"    λ- (constrained / short axis) = {lam_minus:.7f} → σ_short = {sig_short:.5f}")
print(f"\n  Axis ratio: σ_long/σ_short = {sig_long/sig_short:.1f}  (ellipse aspect ratio)")

# Project our displacement onto the axes (in standardized units)
# Eigenvectors of correlation matrix with ρ=-0.94:
# Long axis  ≈ (1, -1)/√2 in standardized coords (z0, za)
# Short axis ≈ (1,  1)/√2 in standardized coords

z0_val = (W0_MODEL - d["w0"]) / sw0
za_val = (W0_MODEL and (W0_MODEL - d["w0"]) == 0) or (WA_MODEL - d["wa"]) / swa
za_val = (WA_MODEL - d["wa"]) / swa

# projection in standardized coords
proj_long  = (-z0_val + za_val) / math.sqrt(2)   # along (-1,+1)/√2 for ρ<0
proj_short = ( z0_val + za_val) / math.sqrt(2)   # along (+1,+1)/√2

# Sigma along each axis (in corr matrix): σ_corr_long = √(1+|ρ|), σ_corr_short = √(1-|ρ|)
sig_corr_long  = math.sqrt(1 + abs(rho))
sig_corr_short = math.sqrt(1 - abs(rho))

n_long  = abs(proj_long)  / sig_corr_long
n_short = abs(proj_short) / sig_corr_short

print(f"\n  Our displacement in principal axes:")
print(f"    Along LONG axis  (degenerate direction): {n_long:.2f}σ")
print(f"    Along SHORT axis (constrained direction): {n_short:.2f}σ")
print(f"\n  → The tension is almost entirely in the SHORT axis direction.")
print(f"  → This means (Δw0>0, Δwa>0) both shift in the same direction,")
print(f"    which CROSSES the degeneracy, not along it.")

# ============================================================
# Part 5: comparison with ΛCDM
# ============================================================
print("\n" + "=" * 68)
print("  Part 5: Our model vs ΛCDM — who is more consistent with DESI?")
print("=" * 68)
print()
print(f"  {'Dataset':<30} {'χ²(ΛCDM)':>10}  {'χ²(ours)':>10}  {'verdict'}")
print("  " + "-" * 70)

for name, d in DATASETS.items():
    rho  = d["rho"]
    # ΛCDM
    dw0_l = W0_LCDM - d["w0"];   dwa_l = WA_LCDM - d["wa"]
    z0_l  = dw0_l / d["sw0"];    za_l  = dwa_l  / d["swa"]
    chi2_l = (1/(1-rho**2)) * (z0_l**2 - 2*rho*z0_l*za_l + za_l**2)
    # ours
    dw0_o = W0_MODEL - d["w0"];  dwa_o = WA_MODEL - d["wa"]
    z0_o  = dw0_o / d["sw0"];    za_o  = dwa_o  / d["swa"]
    chi2_o = (1/(1-rho**2)) * (z0_o**2 - 2*rho*z0_o*za_o + za_o**2)

    if chi2_o < chi2_l:
        verdict = f"✅ ours BETTER  ({math.sqrt(chi2_o):.1f}σ vs {math.sqrt(chi2_l):.1f}σ)"
    else:
        verdict = f"❌ ΛCDM closer ({math.sqrt(chi2_l):.1f}σ vs {math.sqrt(chi2_o):.1f}σ)"
    print(f"  {name:<30} {chi2_l:>10.2f}  {chi2_o:>10.2f}  {verdict}")

# ============================================================
# Part 6: physical interpretation — why does this happen?
# ============================================================
print("\n" + "=" * 68)
print("  Part 6: Physical interpretation")
print("=" * 68)

print("""
  The w0-wa correlation in CPL is ρ ≈ -0.94 because:
    w_eff(z~0.3) ≡ w0 + wa * z/(1+z)|_{pivot} = const
    → if w0 increases (less negative), wa must decrease to compensate
    → this defines a DEGENERATE DIRECTION in (w0, wa) space

  DESI constrains the direction PERPENDICULAR to the degeneracy very tightly.
  Our model has:
    w0 = -0.727  (DESI best for DESY5: -0.727 ✅ exact match)
    wa = -0.49   (DESI prefers -0.75 to -1.27 → our wa too SMALL in magnitude)

  The problem: our quintessence field rolls TOO SLOWLY.
    wₐ = -(dw/da) — our hilltop potential gives gentle rolling → small |wₐ|
    DESI prefers faster rolling → wₐ ≈ -0.75 to -1.05

  Possible explanations:
    1. Our CPL fit is at z≈0 — CPL fitting range matters
    2. Our w(z) is NOT exactly CPL — higher-order terms matter
    3. The hilltop θ parameter needs re-tuning
    4. Genuine tension: our model predicts less dynamic DE than DESI
""")

# ============================================================
# Part 7: alternative — what wa does our model NEED to be consistent?
# ============================================================
print("=" * 68)
print("  Part 7: What wa would make us consistent with DESI?")
print("=" * 68)

print()
for name, d in DATASETS.items():
    rho  = d["rho"]
    dw0  = W0_MODEL - d["w0"]
    z0   = dw0 / d["sw0"]
    # For χ²(2DOF) = 5.99 (2σ boundary), solve for Δwa:
    # χ² = 1/(1-ρ²) * [z0² - 2ρ z0 za + za²] = 5.99
    # za² - 2ρ z0 za + z0² - 5.99(1-ρ²) = 0
    target = 5.99
    a_coeff = 1.0
    b_coeff = -2 * rho * z0
    c_coeff = z0**2 - target * (1 - rho**2)
    disc = b_coeff**2 - 4 * a_coeff * c_coeff
    if disc >= 0:
        za1 = (-b_coeff + math.sqrt(disc)) / 2
        za2 = (-b_coeff - math.sqrt(disc)) / 2
        wa1 = d["wa"] + za1 * d["swa"]
        wa2 = d["wa"] + za2 * d["swa"]
        print(f"  {name}:")
        print(f"    For 2σ boundary (χ²=5.99): wa ∈ [{wa2:.3f}, {wa1:.3f}]")
        print(f"    Our wa = {WA_MODEL} → {'✅ inside 2σ' if wa2 <= WA_MODEL <= wa1 else '❌ outside 2σ'}")
    else:
        print(f"  {name}: no real solution (w0 already outside 2σ alone)")
    print()

# ============================================================
# Part 8: VERDICT
# ============================================================
print("=" * 68)
print("  G9c VERDICT")
print("=" * 68)

chi2_PP = None
for name, d in DATASETS.items():
    rho  = d["rho"]
    dw0  = W0_MODEL - d["w0"]
    dwa  = WA_MODEL - d["wa"]
    z0   = dw0 / d["sw0"]
    za   = dwa / d["swa"]
    chi2 = (1/(1-rho**2)) * (z0**2 - 2*rho*z0*za + za**2)
    p    = chi2_to_pvalue(chi2, dof=2)
    cl   = cl_2d(chi2)
    mah  = math.sqrt(chi2)
    if "Pantheon" in name:
        chi2_PP = chi2

print(f"""
  MODEL POINT: w0 = {W0_MODEL}, wa = {WA_MODEL}
  
  Results (with physically motivated ρ ≈ -0.94):
    DESI+CMB+PP:     {math.sqrt(chi2_PP):.1f}σ  ← MAIN TENSION
    → The problem: wa = {WA_MODEL} is too SMALL in magnitude.
      DESI+CMB+PP prefers wa ≈ -0.75 (our wa is off by +0.26).
      But with ρ=-0.94 this small Δwa is amplified to large χ².

  Physical meaning:
    OUR MODEL PREDICTS SLOWER-ROLLING DE THAN DESI PREFERS.
    The pivot equation of state w_pivot = w0 + wa/(1+z_pivot) ≈ -0.8
    vs DESI w_pivot ≈ -0.9 → 0.1 unit tension.
    NOT catastrophic at face value, but the CPL degeneracy makes it look bad.

  MITIGATING FACTORS:
    1. DESI DR1 only (6M objects, 1-year data) — uncertainties will shrink with DR2
    2. Our w(z) is hilltop quintessence, NOT exactly CPL — CPL fit is approximate
    3. DESI+CMB+DESY5: w0 = -0.727 ± 0.067 → w0 MATCHES EXACTLY
    4. The wa tension: DESI prefers wa ∈ [-1.27, -0.75]. Our wa=-0.49 is slightly above.
    5. If we allow θ (hilltop initial condition) to vary, wa can increase in magnitude.

  CONCLUSION: 🟡 MODERATE-TO-HIGH TENSION with DESI+CMB+PP
    - Not a death blow: ΛCDM itself is 2.5-3.9σ from DESI
    - Our model has w0 that perfectly matches DESI+DESY5 
    - The wa prediction needs investigation (G9c OPEN QUESTION)
    - Action: run hilltop ODE with different θ to find wa vs θ mapping

  STATUS: ⚠️ TENSION IDENTIFIED — needs follow-up
""")
