"""
G8c — Mechanism search: 5th dimension / CP phase / A₄ connection
================================================================

THE USER'S INSIGHT:
"There MUST be a mechanism. Maybe through the 5th dimension,
 maybe a connection through i = √(-1)"

STRUCTURE: The model has TWO couplings:
    α_SIDM = 3.274×10⁻³  (Yukawa: y_s²/(4π) = y²cos²θ/(4π))
    α_d    = 0.0315       (SU(2)_d gauge: g_d²/(4π))

HYPOTHESIS A: y = g_d × sinθ_relic
    The Yukawa coupling is the gauge coupling projected by the CP angle.
    → Physical: the CP-violating VEV projects the gauge interaction
    
HYPOTHESIS B: sinθ_relic = 1/q_CW = 1/3
    The clockwork gear ratio IS the inverse of the mixing angle.
    → Physical: A₄ determines both the mixing AND the clockwork structure

HYPOTHESIS C: y = g_d / N_f
    The Yukawa is suppressed by the number of Majorana fermions.
    → Physical: A₄ triplet = 3 fermions → sinθ = 1/N_f = 1/3

Parts:
    1. Numerical test of y = g_d sinθ
    2. The chain: g_d → A₄ → sinθ → y → α_SIDM
    3. The i connection: complex coupling Y = g_d sinθ e^{iθ}
    4. The 5D/clockwork connection: sinθ = 1/q
    5. Implications for G8: does the chain predict Λ_d ≈ m_ν?
"""

import numpy as np
import math

# ════════════════════════════════════════════════════════════════════════
#  Constants
# ════════════════════════════════════════════════════════════════════════
M_CHI       = 98.19        # MAP DM mass [GeV]
ALPHA_SIDM  = 3.274e-3     # MCMC Yukawa: y_s²/(4π) = y²cos²θ/(4π)
ALPHA_D     = 0.0315       # SU(2)_d gauge coupling at μ=m_χ
M_PHI_MEV   = 9.66         # mediator mass [MeV]
B0          = 19.0 / 3.0   # SU(2) one-loop beta (Nf=3 Majorana)
V_EW        = 246.22       # GeV
M_R_GUT     = 2e16         # GUT-scale seesaw [GeV]
MEV         = 1e12         # GeV → meV

# A₄ angle
THETA_RELIC = math.asin(1.0/3.0)  # 19.47°
SIN_THETA   = 1.0/3.0
COS_THETA   = math.sqrt(8.0/9.0)  # 2√2/3

# Couplings
g_d = math.sqrt(4 * math.pi * ALPHA_D)    # gauge coupling
y_total = math.sqrt(4 * math.pi * ALPHA_SIDM / COS_THETA**2)  # total Yukawa
y_s = y_total * COS_THETA   # scalar Yukawa
y_p = y_total * SIN_THETA   # pseudoscalar Yukawa

# Clockwork
Q_CW_ORIG = 3    # original PI-12
Q_CW_V2   = 2    # updated v2
N_CW_ORIG = 31
N_CW_V2   = 49
NF_DARK    = 3    # number of Majorana fermions in SU(2)_d

def Lambda_d(alpha_d, m_chi):
    return m_chi * math.exp(-2 * math.pi / (B0 * alpha_d))

def m_nu_seesaw(M_R):
    return V_EW**2 / M_R

# ════════════════════════════════════════════════════════════════════════
#  Part 1: THE NUMERICAL TEST — y = g_d × sinθ
# ════════════════════════════════════════════════════════════════════════
print("=" * 78)
print("  Part 1: HYPOTHESIS TEST — y = g_d × sinθ_relic")
print("=" * 78)
print()
print(f"  KNOWN VALUES:")
print(f"    g_d = √(4π α_d) = √(4π × {ALPHA_D}) = {g_d:.6f}")
print(f"    y_total = √(4π α_SIDM / cos²θ) = {y_total:.6f}")
print(f"    y_s = y cosθ = {y_s:.6f}")
print(f"    y_p = y sinθ = {y_p:.6f}")
print(f"    θ_relic = arcsin(1/3) = {math.degrees(THETA_RELIC):.2f}°")
print()

# Test: y = g_d × sinθ
y_predicted = g_d * SIN_THETA
match_pct = abs(y_predicted - y_total) / y_total * 100

print(f"  TEST: y = g_d × sinθ_relic")
print(f"    Predicted: y = {g_d:.6f} × {SIN_THETA:.6f} = {y_predicted:.6f}")
print(f"    Actual:    y = {y_total:.6f}")
print(f"    Agreement: {100 - match_pct:.1f}%  (discrepancy: {match_pct:.1f}%)")
print()

# In terms of α:
# α_SIDM = y²cos²θ/(4π) = g_d²sin²θcos²θ/(4π) = α_d × sin²θcos²θ
alpha_SIDM_pred = ALPHA_D * SIN_THETA**2 * COS_THETA**2
match_alpha = abs(alpha_SIDM_pred - ALPHA_SIDM) / ALPHA_SIDM * 100

print(f"  IN TERMS OF α:")
print(f"    If y = g_d sinθ, then:")
print(f"    α_SIDM = α_d × sin²θ × cos²θ = α_d × (1/9)(8/9) = α_d × 8/81")
print(f"    = {ALPHA_D} × {8.0/81.0:.6f} = {alpha_SIDM_pred:.6e}")
print(f"    Actual α_SIDM = {ALPHA_SIDM:.6e}")
print(f"    Agreement: {100 - match_alpha:.1f}%  (discrepancy: {match_alpha:.1f}%)")
print()

# Using sin2θ:
sin2theta = math.sin(2 * THETA_RELIC)
print(f"  EQUIVALENTLY (using double-angle):")
print(f"    α_SIDM = α_d × sin²(2θ)/4 = α_d × {sin2theta**2/4:.6f}")
print(f"    sin(2θ) = 2sinθcosθ = 2×(1/3)×(2√2/3) = 4√2/9 = {sin2theta:.6f}")

# ════════════════════════════════════════════════════════════════════════
#  Part 2: THE CHAIN — where does sinθ = 1/3 come from?
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 2: THE CHAIN — g_d → A₄ → sinθ → y → α_SIDM → Λ_d → m_ν")
print("=" * 78)
print()
print("  1) SU(2)_d gauge group → α_d = 0.0315 (transmutation → Λ_d)")
print("  2) 3 Majorana fermions → A₄ ≅ alternating group of order 12")
print("  3) A₄ CG coefficients → sin²θ_dark = 1/9, sinθ = 1/3")
print("  4) HYPOTHESIS: y = g_d × sinθ")
print("  5) α_SIDM = α_d sin²θ cos²θ = α_d × 8/81")
print("  6) Λ_d = m_χ exp(-2π/(b₀α_d))")
print("  7) m_ν = v²/M_R (seesaw)")
print()
print("  IF this chain holds, then SIDM + Dark Energy + Neutrino mass")
print("  are ALL determined by just THREE inputs:")
print()
print("    ┌─────────────────────────────────────────────────────┐")
print("    │  1. α_d  (SU(2)_d gauge coupling)                  │")
print("    │  2. m_χ  (DM mass)                                  │")
print("    │  3. M_R  (seesaw scale)                             │")
print("    │                                                     │")
print("    │  OUTPUTS:                                           │")
print("    │  → α_SIDM = α_d × 8/81         → SIDM σ/m         │")
print("    │  → Λ_d = m_χ e^{-2π/(b₀α_d)}   → dark energy      │")
print("    │  → m_ν = v²/M_R                 → neutrino mass    │")
print("    │  → Λ_d ≈ m_ν if α_d satisfies matching condition   │")
print("    └─────────────────────────────────────────────────────┘")

# ════════════════════════════════════════════════════════════════════════
#  Part 3: THE i CONNECTION — complex coupling structure
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 3: THE i CONNECTION — Y = y_s + iy_p = y e^{iθ}")
print("=" * 78)
print()

# The complex coupling
Y_mod = y_total
Y_phase = THETA_RELIC
Y_s = y_s
Y_p = y_p

print(f"  The full Yukawa: Y = y_s + i y_p = y e^{{iθ}}")
print(f"    |Y| = {Y_mod:.6f}")
print(f"    arg(Y) = θ = {math.degrees(Y_phase):.2f}°")
print()

# If y = g_d sinθ:
print(f"  If y = g_d sinθ, then:")
print(f"    Y = g_d sinθ × e^{{iθ}} = g_d sinθ cosθ + i g_d sin²θ")
print(f"    Re(Y) = y_s = g_d × sin(2θ)/2 = {g_d * math.sin(2*THETA_RELIC)/2:.6f}")
print(f"    Im(Y) = y_p = g_d × sin²θ    = {g_d * SIN_THETA**2:.6f}")
print()

# Alternative form: Y = g_d × Im(e^{iθ}) × e^{iθ}
print(f"  ELEGANT FORM:")
print(f"    Y = g_d × Im(e^{{iθ}}) × e^{{iθ}}")
print(f"    = g_d × sinθ × e^{{iθ}}")
print(f"    = (g_d/2i)(e^{{2iθ}} - 1)")
print()

# The i² = -1 connection:
# y² = g_d² sin²θ
# g_d² = y² / sin²θ = y² × 9
# So: g_d² = 9 y², or: α_d = 9 × (y²/(4π)) = 9 × α_total
alpha_total = y_total**2 / (4*math.pi)
print(f"  RATIO g_d²/y² = {g_d**2/y_total**2:.4f} ≈ 1/sin²θ = {1/SIN_THETA**2:.1f}")
print(f"  ⇒ α_d = 9 α_total  where α_total = y²/(4π) = {alpha_total:.6e}")
print(f"  ⇒ 9 × α_total = {9*alpha_total:.6f} vs α_d = {ALPHA_D:.6f}")
match_9 = abs(9*alpha_total - ALPHA_D)/(ALPHA_D)*100
print(f"  Agreement: {100-match_9:.1f}% ({match_9:.1f}% off)")
print()

# The NUMBER 9 = N_f² = 3²
print(f"  THE KEY NUMBER: 9 = N_f² = 3²")
print(f"    N_f = 3 Majorana fermions in SU(2)_d")
print(f"    sinθ = 1/N_f (from A₄ CG coefficients)")
print(f"    sin²θ = 1/N_f²")
print(f"    ⇒ α_d = N_f² × α_total = N_f² × y²/(4π)")
print(f"    ⇒ g_d = N_f × y")

# ════════════════════════════════════════════════════════════════════════
#  Part 4: sinθ = 1/q — the clockwork connection
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 4: sinθ_relic = 1/q — clockwork gear ratio = A₄ angle")
print("=" * 78)
print()
print(f"  sinθ_relic = 1/3")
print(f"  q_CW (original PI-12) = 3")
print(f"  ⇒ sinθ_relic = 1/q_CW  (!)")
print()
print(f"  This means the clockwork gear ratio is determined by A₄:")
print(f"    A₄ → sinθ = 1/3 → q = 1/sinθ = 3")
print()
print(f"  Physical meaning:")
print(f"  ─────────────────")
print(f"  In the deconstructed 5D picture (PI-15):")
print(f"    ka = ln(q) = ln(3) = {math.log(3):.4f}")
print(f"    warp factor per site = q = e^{{ka}} = 3")
print(f"    The A₄ angle FIXES the curvature of the extra dimension!")
print()

# 5D geometry for q=3
a_lat = 755.3 / 500**2  # original f₀/Λ_CW² GeV⁻¹
k_curv = math.log(3) / a_lat
L5 = 32 * a_lat
print(f"  5D PARAMETERS (original q=3, N=31):")
print(f"    Lattice spacing a = f₀/Λ_CW² = {a_lat:.4e} GeV⁻¹")
print(f"    Curvature k = ln(q)/a = {k_curv:.1f} GeV")
print(f"    Total length L₅ = {L5:.4e} GeV⁻¹")
print(f"    kL₅ = {k_curv*L5:.1f}")
print(f"    Warp factor q^N = 3^31 = {3**31:.3e}")
print()

# v2 comparison
print(f"  ⚠ v2 UPDATE: q=2, N=49 gives better f_DE/f_target")
print(f"    sinθ = 1/3 ≠ 1/2 = 1/q_v2")
print(f"    BUT: sinθ = 1/3 is still from A₄, independent of clockwork")
print(f"    The relation y = g_d sinθ holds in BOTH cases:")
print(f"      y = g_d/3 = {g_d/3:.6f} vs y = {y_total:.6f} ({abs(g_d/3 - y_total)/y_total*100:.1f}%)")
print()
print(f"  Two scenarios:")
print(f"    (a) q=3 is correct, and sinθ=1/q is a deep structural constraint")
print(f"        → Both the 5D curvature AND the Yukawa are A₄-determined")
print(f"    (b) q is free, and y = g_d sinθ holds regardless of clockwork")
print(f"        → The coupling relation is from confining SU(2)_d, not clockwork")

# ════════════════════════════════════════════════════════════════════════
#  Part 5: THE BIG PICTURE — does this close G8?
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 5: IMPLICATIONS FOR G8 — Λ_d ≈ m_ν")
print("=" * 78)
print()

# The chain:
# α_SIDM is measured by MCMC to be 3.274e-3
# If y = g_d sinθ, then α_d = 9 × y²/(4π)
# But we measure α_SIDM = y²cos²θ/(4π) = y²(8/9)/(4π)
# So y²/(4π) = α_SIDM × 9/8
# And α_d = 9 × α_SIDM × 9/8 = 81α_SIDM/8

alpha_d_from_chain = 81.0 * ALPHA_SIDM / 8.0
Ld_from_chain = Lambda_d(alpha_d_from_chain, M_CHI) * MEV
mnu = m_nu_seesaw(M_R_GUT) * MEV

print(f"  IF y = g_d × sinθ holds, then we can DERIVE α_d from α_SIDM:")
print(f"    α_d = (81/8) × α_SIDM = {alpha_d_from_chain:.6f}")
print(f"    vs actual α_d = {ALPHA_D:.6f}")
print(f"    Agreement: {100 - abs(alpha_d_from_chain - ALPHA_D)/ALPHA_D*100:.1f}%")
print()
print(f"  ⇒ This PREDICTS Λ_d from SIDM measurements alone:")
print(f"    Λ_d = m_χ exp(-2π/(b₀ × 81α_SIDM/8))")
print(f"    = {M_CHI} × exp(-2π/({B0:.3f} × {alpha_d_from_chain:.6f}))")
print(f"    = {Ld_from_chain:.4f} meV")
print()
print(f"    Compare: m_ν(seesaw) = {mnu:.4f} meV")
print(f"    Ratio Λ_d/m_ν = {Ld_from_chain/mnu:.4f}")
print()

# Sensivitity: since α_d enters exponentially, the 5% error matters
# What α_d gives exact match?
alpha_d_exact = 2*math.pi / (B0 * math.log(M_CHI * M_R_GUT / V_EW**2))
print(f"  FINE STRUCTURE:")
print(f"    α_d for exact Λ_d = m_ν: {alpha_d_exact:.6f}")
print(f"    α_d from chain (81α_SIDM/8): {alpha_d_from_chain:.6f}")
print(f"    α_d used in model: {ALPHA_D:.6f}")
print(f"    Discrepancy chain vs exact: {abs(alpha_d_from_chain - alpha_d_exact)/alpha_d_exact*100:.1f}%")
print()

# What if the matching is not exact sinθ = 1/3 but includes radiative correction?
# Try: α_d = C × α_SIDM and find best C
C_exact = alpha_d_exact / ALPHA_SIDM
print(f"  EXACT COEFFICIENT: α_d = C × α_SIDM")
print(f"    C(for Λ_d = m_ν) = {C_exact:.4f}")
print(f"    C(hypothesis) = 81/8 = {81/8:.4f}")
print(f"    Ratio: {C_exact/(81/8):.4f}")
print()

# Could the correction be from running?
print(f"  POSSIBLE CORRECTIONS:")
print(f"    81/8 = {81/8:.4f}")
print(f"    Exact C = {C_exact:.4f}")
print(f"    Ratio = {C_exact/(81/8):.4f}")
print(f"    Missing factor: {C_exact/(81/8):.4f}")
delta = C_exact - 81/8
print(f"    Δ = C_exact - 81/8 = {delta:.4f}")
print(f"    Δ/(81/8) = {delta/(81/8)*100:.1f}% — could be O(α_d) radiative correction?")
print(f"    α_d/(4π) = {ALPHA_D/(4*math.pi):.4f} → one-loop: ~{ALPHA_D/(4*math.pi)*100:.1f}% correction")
print(f"    → {delta/(81/8)*100:.1f}% vs {ALPHA_D/(4*math.pi)*100:.1f}%... ", end="")
ratio_check = delta/(81/8) / (ALPHA_D/(4*math.pi))
print(f"factor {ratio_check:.1f}")

# ════════════════════════════════════════════════════════════════════════
#  Part 6: PREDICTION TABLE — what does the chain predict?
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 6: PREDICTION TABLE — if y = g_d sinθ is structural")
print("=" * 78)
print()

# From α_SIDM alone, predict:
# α_d = (81/8) α_SIDM
# Λ_d = m_χ exp(-2π/(b₀ α_d))
# Require Λ_d ≈ m_ν → constrains M_R

# What M_R does the chain predict?
Ld_gev = Lambda_d(alpha_d_from_chain, M_CHI)
M_R_pred = V_EW**2 / Ld_gev
print(f"  From chain + Λ_d = m_ν requirement:")
print(f"    α_d = 81α_SIDM/8 = {alpha_d_from_chain:.6f}")
print(f"    Λ_d = {Ld_gev:.4e} GeV = {Ld_from_chain:.4f} meV")
print(f"    M_R (predicted) = v²/Λ_d = {M_R_pred:.3e} GeV")
print(f"    M_R (GUT) = {M_R_GUT:.0e} GeV")
print(f"    Ratio M_R(pred)/M_R(GUT) = {M_R_pred/M_R_GUT:.3f}")
print()

print(f"  {'Quantity':<30}  {'Predicted':>14}  {'Observed/Used':>14}  {'Match':>8}")
print(f"  {'─'*30}  {'─'*14}  {'─'*14}  {'─'*8}")

predictions = [
    ("α_SIDM [input]",          f"{ALPHA_SIDM:.4e}",  f"{ALPHA_SIDM:.4e}", "input"),
    ("sinθ = 1/3 [A₄]",         f"{SIN_THETA:.4f}",   "0.3333", "A₄"),
    ("α_d = 81α_SIDM/8",        f"{alpha_d_from_chain:.6f}", f"{ALPHA_D:.6f}",
     f"{100 - abs(alpha_d_from_chain - ALPHA_D)/ALPHA_D*100:.1f}%"),
    ("Λ_d [meV]",               f"{Ld_from_chain:.4f}", "2.0611",
     f"{100 - abs(Ld_from_chain - 2.0611)/2.0611*100:.0f}%"),
    ("M_R from Λ_d=m_ν [GeV]",  f"{M_R_pred:.2e}", f"{M_R_GUT:.0e}",
     f"{M_R_pred/M_R_GUT:.2f}×"),
    ("m_ν(seesaw) [meV]",       f"{mnu:.4f}",  "~50 meV (atm)", "scale"),
]

for name, pred, obs, match in predictions:
    print(f"  {name:<30}  {pred:>14}  {obs:>14}  {match:>8}")

# ════════════════════════════════════════════════════════════════════════
#  Part 7: THE MECHANISM — why y = g_d sinθ might be true
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 7: PHYSICAL MECHANISM — why y = g_d × sinθ?")
print("=" * 78)
print()
print("  Three possibility levels:")
print()
print("  LEVEL 1 — Confining gauge theory (most physical):")
print("  ──────────────────────────────────────────────────")
print("  In SU(2)_d with 3 Majorana, the mediator φ is a composite.")
print("  The effective Yukawa coupling between DM and mediator")
print("  is related to the fundamental gauge coupling by:")
print("    y_eff = g_d × (matrix element)")
print("  In A₄ symmetry, the relevant matrix element is:")
print("    ⟨χφ|V|χ⟩ ∝ CG coefficient = sinθ_dark = 1/3")
print("  ⇒ y = g_d × 1/3 = g_d × sinθ_relic")
print()
print("  LEVEL 2 — 5D geometry (clockwork):")
print("  ──────────────────────────────────")
print("  In the deconstructed 5D with linear dilaton:")
print("    warp per site = q = e^{ka}")
print("  If q = 1/sinθ = 3 (A₄ determines curvature):")
print("    The coupling at site j is g_d/q^j")
print("    The effective 4D coupling involves 1/q = sinθ")
print("  ⇒ y = g_d/q = g_d sinθ")
print()
print("  LEVEL 3 — Complex coupling (the i connection):")
print("  ───────────────────────────────────────────────")
print("  The CP-violating Yukawa is Y = y_s + iy_p = ye^{iθ}")
print("  With y = g_d sinθ:")
print("    Y = g_d sinθ e^{iθ} = (g_d/2i)(e^{2iθ} - 1)")
print("  The factor i appears naturally!")
print("  The coupling VANISHES at θ = 0 (CP conservation)")
print("  and is maximal at θ = π/4 (max CP violation).")
print("  Our θ = 19.47° gives |Y|/g_d = sinθ = 1/3.")
print()
print("  ⇒ The link to i = √(-1):")
print("    Y = (g_d/2i)(e^{2iθ} - 1)")
print("    The factor 1/i = -i means the coupling is π/2 rotated")
print("    in the complex plane relative to the gauge coupling.")
print("    CP violation IS the mechanism that reduces g_d → y.")

# ════════════════════════════════════════════════════════════════════════
#  Part 8: WHAT WOULD CLINCH IT?
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 8: WHAT WOULD CLINCH IT?")
print("=" * 78)
print()
print("  The hypothesis y = g_d sinθ currently matches at 2.5%.")
print("  (Or: α_d = (81/8) α_SIDM matches at 5%.)")
print()
print("  TO PROVE IT:")
print("  1. Derive y = g_d sinθ from the A₄ × SU(2)_d Lagrangian")
print("     → need to show the CG coefficient projects g_d → y = g_d/3")
print("  2. OR: compute the one-loop matching g_d → y_Yukawa")
print("     in confining SU(2)_d (lattice or semi-analytic)")
print("  3. OR: check against OTHER A₄ BSM models with confining sectors")
print("     → if the pattern repeats, it's structural")
print()
print("  TO STRENGTHEN:")
print("  4. Find a SECOND prediction from this chain")
print("     → e.g., the mediator mass m_φ relation to Λ_d?")
print("  5. Check if the 5% discrepancy is exactly α_d/(4π) ~ 0.25%,")
print("     which would be a one-loop radiative correction signal")
print()
print("  TO FALSIFY:")
print("  6. If lattice SU(2)_d gives y/g_d ≠ sinθ → coincidence")
print("  7. If other benchmark points (BP1, BP9, BP16) break the pattern")

# ════════════════════════════════════════════════════════════════════════
#  BONUS: Check other benchmarks
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  BONUS: Other benchmark points")
print("=" * 78)
print()

benchmarks = {
    "MAP":  {"m_chi": 98.19,  "alpha_s": 3.274e-3, "m_phi_MeV": 9.660},
    "BP1":  {"m_chi": 54.556, "alpha_s": 2.645e-3, "m_phi_MeV": 12.975},
    "BP9":  {"m_chi": 48.329, "alpha_s": 2.350e-3, "m_phi_MeV": 8.657},
    "BP16": {"m_chi": 14.384, "alpha_s": 7.555e-4, "m_phi_MeV": 5.047},
}

print(f"  For each BP, α_SIDM = y²cos²θ/(4π).")
print(f"  If y = g_d sinθ, then α_d = 81α_SIDM/8 (BP-dependent!)")
print(f"  But α_d should be UNIVERSAL (one gauge coupling).")
print()
print(f"  {'BP':>5}  {'m_χ':>8}  {'α_SIDM':>12}  {'α_d(chain)':>12}  {'Λ_d [meV]':>12}  {'Λ_d/m_ν':>10}")
print(f"  {'─'*5}  {'─'*8}  {'─'*12}  {'─'*12}  {'─'*12}  {'─'*10}")

for name, bp in benchmarks.items():
    ad_bp = 81.0 * bp['alpha_s'] / 8.0
    Ld_bp = Lambda_d(ad_bp, bp['m_chi']) * MEV
    r_bp = Ld_bp / mnu
    marker = " ←" if name == "MAP" else ""
    print(f"  {name:>5}  {bp['m_chi']:>8.2f}  {bp['alpha_s']:>12.4e}  {ad_bp:>12.6f}  {Ld_bp:>12.4f}  {r_bp:>10.4f}{marker}")

print()
print("  KEY QUESTION: α_d should be UNIVERSAL for all BPs.")
print("  The chain gives different α_d for each BP.")
print("  This means EITHER:")
print("    (a) The relation involves running: α_d(μ = m_χ) varies with m_χ")
print("    (b) The A₄ matrix element depends on representation (m_χ-dependent)")
print("    (c) The relation is only approximate / coincidental")
print()

# Check: does RG running explain the variation?
# 1-loop: α_d(μ₂) = α_d(μ₁) / (1 + b₀ α_d(μ₁)/(2π) ln(μ₂/μ₁))
alpha_d_at_MAP = 81 * 3.274e-3 / 8  # 0.03316
print(f"  RG running check:")
print(f"    α_d(MAP, m_χ=98.19) = {alpha_d_at_MAP:.6f}")
for name, bp in benchmarks.items():
    if name == "MAP":
        continue
    mu_ratio = bp['m_chi'] / 98.19
    # Run from MAP scale to BP scale
    ad_run = alpha_d_at_MAP / (1 + B0 * alpha_d_at_MAP / (2*math.pi) * math.log(mu_ratio))
    ad_chain = 81 * bp['alpha_s'] / 8
    print(f"    α_d({name}, m_χ={bp['m_chi']:.1f}): chain={ad_chain:.6f}, RG={ad_run:.6f}, "
          f"Δ={abs(ad_chain-ad_run)/ad_run*100:.1f}%")

# ════════════════════════════════════════════════════════════════════════
#  VERDICT
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  ▌ VERDICT")
print("=" * 78)
print()
print("  y = g_d × sinθ_relic  (2.5% match)")
print()
print("  PHYSICAL INTERPRETATION:")
print("    The Yukawa coupling of χ to the mediator φ is the")
print("    SU(2)_d gauge coupling PROJECTED onto the CP-violating")
print("    direction by the A₄-determined angle θ = arcsin(1/3).")
print()
print("  THE CHAIN Λ_d ~ m_ν:")
print("    If this holds, then from SIDM measurements + A₄:")
print("      α_SIDM → α_d = (81/8)α_SIDM → Λ_d → Λ_d ≈ m_ν")
print("    The coincidence becomes a PREDICTION (not an input).")
print()
print("  STATUS: HYPOTHESIS — promising numerically, needs derivation.")
print("  The 5% discrepancy could be radiative corrections or a sign")
print("  that the exact relation is more complex.")
print()
print("  OPEN QUESTIONS:")
print("  1. Is α_d universal or BP-dependent? (running vs structure)")
print("  2. Derive y = g_d sinθ from A₄ × SU(2)_d theory")
print("  3. Is sinθ = 1/q a coincidence or structural? (q=3 vs q=2)")
print("  4. Does the 5D geometry naturally give y = g_d/q?")
