"""
G9a: NuFIT 5.3 Neutrino Mass Cross-Validation
==============================================

Our model predicts: Λ_d = 3.031 meV = m₁ (lightest neutrino, NH)

Test: Given m₁ = Λ_d = 3.031 meV and NuFIT 5.3 oscillation parameters,
compute m₂, m₃, Σmν and check consistency with Planck 2018 upper bound.

References:
  - NuFIT 5.3 (2023): https://www.nu-fit.org  (arXiv:2007.14792 updated)
  - Planck 2018 TT+TE+EE+lowE+lensing: Σmν < 0.12 eV (95% CL)
  - Planck 2018 + BAO: Σmν < 0.12 eV (95% CL)
"""

import math

# ── NuFIT 5.3 best-fit oscillation parameters (Normal Hierarchy) ──────────
# From nufit.org/v5.3 (2023), without SK atmospheric data
# Δm²_21 [eV²], Δm²_31 [eV²], sin²θ₁₂, sin²θ₁₃, sin²θ₂₃

Dm2_21 = 7.53e-5   # eV²   (solar mass splitting)
Dm2_31 = 2.453e-3  # eV²   (atmospheric mass splitting, NH: m₃ > m₂ > m₁)

# ── Our model's prediction ─────────────────────────────────────────────────
Lambda_d_meV = 3.031     # meV  (from G8f scan: universal for all m_chi)
m1_eV        = Lambda_d_meV * 1e-3  # eV

# ── Constraints ────────────────────────────────────────────────────────────
PLANCK_SUM_LIMIT_EV   = 0.120   # 95% CL  (Planck 2018 TT+TE+EE+lowE+lensing+BAO)
KATRIN_M_BETA_LIMIT   = 0.45    # eV  (KATRIN 2022, 90% CL on m_νe)
COSMOLOGY_LIMIT_EV    = 0.12    # same as Planck

print("=" * 68)
print("  G9a: NuFIT 5.3 Neutrino Mass Cross-Validation")
print("=" * 68)

print(f"""
  Our prediction: Λ_d = m₁ (lightest neutrino, Normal Hierarchy)
         Λ_d = {Lambda_d_meV:.4f} meV  →  m₁ = {m1_eV*1e3:.4f} meV
""")

# ── Compute m₂, m₃ ────────────────────────────────────────────────────────
m2_eV = math.sqrt(m1_eV**2 + Dm2_21)
m3_eV = math.sqrt(m1_eV**2 + Dm2_31)

sum_mnu_eV  = m1_eV + m2_eV + m3_eV
sum_mnu_meV = sum_mnu_eV * 1e3

# m_νe (effective electron neutrino mass for beta decay)
sin2_th12 = 0.303    # NuFIT 5.3 NH
sin2_th13 = 0.02229  # NuFIT 5.3 NH
cos2_th12 = 1.0 - sin2_th12
cos2_th13 = 1.0 - sin2_th13

m_beta_sq = cos2_th13 * cos2_th12 * m1_eV**2 \
          + cos2_th13 * sin2_th12  * m2_eV**2 \
          + sin2_th13              * m3_eV**2
m_beta_eV = math.sqrt(m_beta_sq)

print("  NuFIT 5.3 inputs (NH, without SK atm):")
print(f"    Δm²₂₁ = {Dm2_21:.4e} eV²")
print(f"    Δm²₃₁ = {Dm2_31:.4e} eV²")
print(f"    sin²θ₁₂ = {sin2_th12:.4f}")
print(f"    sin²θ₁₃ = {sin2_th13:.5f}")
print()

print("  Neutrino mass spectrum:")
print(f"    m₁ = {m1_eV*1e3:8.4f} meV  (= Λ_d, our prediction)")
print(f"    m₂ = {m2_eV*1e3:8.4f} meV  (= √(m₁² + Δm²₂₁))")
print(f"    m₃ = {m3_eV*1e3:8.4f} meV  (= √(m₁² + Δm²₃₁))")
print(f"    ─────────────────────────────")
print(f"    Σmν = {sum_mnu_meV:.4f} meV  =  {sum_mnu_eV*1e3:.2f} meV")
print()

print("  Constraints:")
print(f"    Planck 2018 + BAO:  Σmν < {PLANCK_SUM_LIMIT_EV*1e3:.0f} meV (95% CL)")
print(f"    KATRIN 2022:        m_β < {KATRIN_M_BETA_LIMIT*1e3:.0f} meV (90% CL effective)")
print()

# ── Verdict ────────────────────────────────────────────────────────────────
print("  Results:")
margin_planck = (PLANCK_SUM_LIMIT_EV - sum_mnu_eV) / PLANCK_SUM_LIMIT_EV * 100
margin_katrin = (KATRIN_M_BETA_LIMIT - m_beta_eV) / KATRIN_M_BETA_LIMIT * 100

planck_pass = sum_mnu_eV < PLANCK_SUM_LIMIT_EV
katrin_pass = m_beta_eV < KATRIN_M_BETA_LIMIT

print(f"    Σmν  = {sum_mnu_meV:.2f} meV   vs limit {PLANCK_SUM_LIMIT_EV*1e3:.0f} meV")
print(f"           {'✅ PASS' if planck_pass else '❌ FAIL'}  "
      f"(margin = {margin_planck:.1f}%  →  factor {PLANCK_SUM_LIMIT_EV/sum_mnu_eV:.1f}× below limit)")
print()
print(f"    m_β  = {m_beta_eV*1e3:.4f} meV  vs limit {KATRIN_M_BETA_LIMIT*1e3:.0f} meV")
print(f"           {'✅ PASS' if katrin_pass else '❌ FAIL'}  "
      f"(margin = {margin_katrin:.1f}%  →  factor {KATRIN_M_BETA_LIMIT/m_beta_eV:.1f}× below limit)")
print()

# ── Neutrino mass ordering check ────────────────────────────────────────────
print("  Normal Hierarchy consistency:")
print(f"    m₁ < m₂ < m₃:  {m1_eV:.4e} < {m2_eV:.4e} < {m3_eV:.4e} eV")
nh_ok = m1_eV < m2_eV < m3_eV
print(f"    {'✅ NH confirmed' if nh_ok else '❌ wrong ordering'}")
print()

# ── KATRIN sensitivity check (future) ─────────────────────────────────────
KATRIN_FUTURE_EV = 0.2e-3  # ~0.2 meV sensitivity (future goal)
print(f"  Future KATRIN sensitivity: {KATRIN_FUTURE_EV*1e3:.1f} meV")
detectable = m_beta_eV > KATRIN_FUTURE_EV
print(f"    m_β = {m_beta_eV*1e3:.4f} meV  {'→ DETECTABLE' if detectable else '→ below sensitivity'}")
print()

# ── CMB-S4 future projection ───────────────────────────────────────────────
CMB_S4_LIMIT_EV = 0.030e-3 * 1e0  # 0.03 eV = 30 meV projected
print(f"  CMB-S4 projected: Σmν < 30 meV (1σ error ~15 meV)")
cmbs4_detectable = sum_mnu_eV > 0.030
print(f"    Σmν = {sum_mnu_meV:.2f} meV: {'→ may be detectable' if cmbs4_detectable else '→ at detection threshold'}")
print()

print("=" * 68)
print("  VERDICT")
print("=" * 68)
if planck_pass and katrin_pass:
    print(f"""
  ✅ G9a PASS: Λ_d = m₁ = {Lambda_d_meV:.4f} meV is consistent with all
  cosmological and laboratory neutrino mass bounds.

  Σmν = {sum_mnu_meV:.2f} meV  ≪  120 meV  (Planck)     factor {PLANCK_SUM_LIMIT_EV/sum_mnu_eV:.1f}× margin

  The model is quasi-degenerate with the normal hierarchy minimum:
  m₁ ≪ m₂ ≪ m₃  (hierarchical limit, NOT quasi-degenerate)
  The sum is dominated by m₃ ≈ {m3_eV*1e3:.1f} meV.

  Physical picture:
    Λ_d = dark QCD confinement scale = lightest SM neutrino mass
    Both set by seesaw-like physics if M_R ~ 10¹⁴ GeV × (f/M_Pl)
    Common A₄ origin: sin²θ₁₂ = 1/3 (neutrinos) = sin²θ_dark (SIDM)
""")
else:
    print(f"  ❌ FAIL: Σmν = {sum_mnu_meV:.2f} meV exceeds bound")
