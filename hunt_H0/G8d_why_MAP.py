"""
G8d — Why MAP is special: universal relation search
====================================================

G8c found y = g_d sinθ at 97.5% for MAP but NOT for other BPs.
This script investigates:

1. Among 80K viable SIDM points, which satisfy α_d(chain) ≈ constant?
2. Does adding m_φ dependence fix universality?
3. Does the dark energy constraint (Λ_d ≈ 2 meV) select MAP?
4. Is there a modified relation y = g_d × sinθ × F(m_φ/m_χ)?
5. What combination of SIDM + DE constraints uniquely picks MAP?

Key insight: if α_d is UNIVERSAL (one gauge coupling), then 
α_SIDM = (8/81)α_d should be CONSTANT. But MCMC varies it.
The question is whether the DE constraint + gauge universality 
SELECTS a unique (m_χ, α, m_φ) = MAP.
"""

import numpy as np
import csv
import math
from collections import defaultdict

# ════════════════════════════════════════════════════════════════════════
#  Constants
# ════════════════════════════════════════════════════════════════════════
ALPHA_D     = 0.0315       # SU(2)_d gauge coupling
B0          = 19.0 / 3.0   # one-loop beta coefficient
V_EW        = 246.22       # GeV
M_R_GUT     = 2e16         # seesaw scale
MEV_PER_GEV = 1e3
MEV_CONV    = 1e12         # GeV → meV

SIN_THETA   = 1.0/3.0
COS_THETA   = math.sqrt(8.0/9.0)

# Predicted α_SIDM if gauge-Yukawa relation holds
ALPHA_SIDM_PRED = (8.0/81.0) * ALPHA_D  # = 3.11e-3

# Lambda_d from transmutation
def Lambda_d_meV(alpha_d, m_chi_GeV):
    """Dark confinement scale in meV."""
    exp_arg = -2 * math.pi / (B0 * alpha_d)
    if exp_arg < -700:
        return 0.0
    return m_chi_GeV * math.exp(exp_arg) * MEV_CONV

def m_nu_meV(M_R_GeV):
    """Seesaw neutrino mass in meV."""
    return V_EW**2 / M_R_GeV * MEV_CONV

# Target
LAMBDA_D_TARGET = Lambda_d_meV(ALPHA_D, 98.19)  # ~ 2.06 meV
MNU_TARGET = m_nu_meV(M_R_GUT)                   # ~ 3.03 meV

print("=" * 78)
print("  G8d — Why MAP? Universal relation search")
print("=" * 78)
print()
print(f"  Inputs:")
print(f"    α_d = {ALPHA_D}")
print(f"    α_SIDM(predicted) = (8/81)α_d = {ALPHA_SIDM_PRED:.6e}")
print(f"    Λ_d(MAP) = {LAMBDA_D_TARGET:.4f} meV")
print(f"    m_ν(seesaw) = {MNU_TARGET:.4f} meV")

# ════════════════════════════════════════════════════════════════════════
#  Part 1: Load SIDM scan data
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 1: Loading 80K viable SIDM points")
print("=" * 78)

data_path = r"c:\Users\omerp\source\omer_mind\V10\all_viable_raw_v8.csv"
m_chi_arr = []
m_phi_arr = []
alpha_arr = []
sigma30_arr = []
sigma1000_arr = []

with open(data_path, 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        m_chi_arr.append(float(row[0]))
        m_phi_arr.append(float(row[1]))  # in GeV
        alpha_arr.append(float(row[2]))
        sigma30_arr.append(float(row[3]))
        sigma1000_arr.append(float(row[4]))

m_chi  = np.array(m_chi_arr)
m_phi  = np.array(m_phi_arr)  # GeV
alpha  = np.array(alpha_arr)
sigma30 = np.array(sigma30_arr)
sigma1000 = np.array(sigma1000_arr)
m_phi_MeV = m_phi * 1e3  # convert to MeV

N = len(m_chi)
print(f"  Loaded {N} points")
print(f"  m_χ range: [{m_chi.min():.2f}, {m_chi.max():.2f}] GeV")
print(f"  m_φ range: [{m_phi_MeV.min():.2f}, {m_phi_MeV.max():.2f}] MeV")
print(f"  α range: [{alpha.min():.4e}, {alpha.max():.4e}]")

# ════════════════════════════════════════════════════════════════════════
#  Part 2: The naive chain α_d = 81α/8 — distribution
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 2: Distribution of α_d(chain) = 81α/8")
print("=" * 78)

alpha_d_chain = 81.0 * alpha / 8.0

print(f"  α_d(chain) range: [{alpha_d_chain.min():.6f}, {alpha_d_chain.max():.6f}]")
print(f"  α_d(chain) mean: {alpha_d_chain.mean():.6f}")
print(f"  α_d(chain) median: {np.median(alpha_d_chain):.6f}")
print(f"  α_d(chain) std: {alpha_d_chain.std():.6f}")
print(f"  Target α_d = {ALPHA_D}")
print()

# How many points have α_d(chain) ≈ 0.0315?
for tol in [0.01, 0.05, 0.10, 0.20]:
    mask = np.abs(alpha_d_chain - ALPHA_D) / ALPHA_D < tol
    print(f"  Within {tol*100:.0f}% of α_d=0.0315: {mask.sum()} points ({mask.sum()/N*100:.2f}%)")
    if mask.sum() > 0 and mask.sum() < 20:
        idx = np.where(mask)[0]
        for i in idx[:5]:
            print(f"    m_χ={m_chi[i]:.2f} GeV, m_φ={m_phi_MeV[i]:.2f} MeV, α={alpha[i]:.4e}")

# ════════════════════════════════════════════════════════════════════════
#  Part 3: Add DE constraint: Λ_d ≈ 2 meV
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 3: Combined SIDM + DE constraint")
print("=" * 78)
print()
print("  For each SIDM point, IF α_d = 81α/8, compute Λ_d.")
print("  The DE constraint requires Λ_d ∈ [1, 5] meV (order of magnitude).")
print()

Lambda_d_arr = np.zeros(N)
for i in range(N):
    ad = alpha_d_chain[i]
    if ad > 0.005:  # avoid numerical underflow
        Lambda_d_arr[i] = Lambda_d_meV(ad, m_chi[i])

# Filter for Λ_d in meV range
mask_de = (Lambda_d_arr > 0.5) & (Lambda_d_arr < 50)
n_de = mask_de.sum()
print(f"  Points with Λ_d ∈ [0.5, 50] meV: {n_de} ({n_de/N*100:.3f}%)")

if n_de > 0:
    print(f"  Among these:")
    print(f"    m_χ range: [{m_chi[mask_de].min():.2f}, {m_chi[mask_de].max():.2f}] GeV")
    print(f"    m_φ range: [{m_phi_MeV[mask_de].min():.2f}, {m_phi_MeV[mask_de].max():.2f}] MeV")
    print(f"    α range: [{alpha[mask_de].min():.4e}, {alpha[mask_de].max():.4e}]")
    print(f"    α_d(chain) range: [{alpha_d_chain[mask_de].min():.6f}, {alpha_d_chain[mask_de].max():.6f}]")
    print(f"    Λ_d range: [{Lambda_d_arr[mask_de].min():.4f}, {Lambda_d_arr[mask_de].max():.4f}] meV")
    print()
    
    # Tighter: Λ_d ∈ [1, 10] meV 
    mask_tight = (Lambda_d_arr > 1.0) & (Lambda_d_arr < 10.0)
    n_tight = mask_tight.sum()
    print(f"  Tight: Λ_d ∈ [1, 10] meV: {n_tight} points")
    
    if n_tight > 0:
        # Show the closest points to MAP
        dist_to_MAP = np.abs(m_chi - 98.19) + np.abs(alpha - 3.274e-3)/3.274e-3*10 + np.abs(m_phi_MeV - 9.66)
        idx_de = np.where(mask_tight)[0]
        closest_idx = idx_de[np.argsort(dist_to_MAP[idx_de])[:20]]
        
        print(f"\n  Top 20 closest to MAP:")
        print(f"  {'m_χ':>8}  {'m_φ[MeV]':>10}  {'α':>12}  {'α_d(chain)':>12}  {'Λ_d[meV]':>10}  {'σ/m(30)':>10}  {'σ/m(1k)':>10}")
        print(f"  {'─'*8}  {'─'*10}  {'─'*12}  {'─'*12}  {'─'*10}  {'─'*10}  {'─'*10}")
        for i in closest_idx:
            print(f"  {m_chi[i]:>8.2f}  {m_phi_MeV[i]:>10.2f}  {alpha[i]:>12.4e}  {alpha_d_chain[i]:>12.6f}  {Lambda_d_arr[i]:>10.4f}  {sigma30[i]:>10.4f}  {sigma1000[i]:>10.4f}")

# ════════════════════════════════════════════════════════════════════════
#  Part 4: The inverse approach — fix α_d, find which SIDM points survive
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 4: Fix α_d = 0.0315, what α_SIDM is predicted?")
print("=" * 78)
print()

alpha_pred = ALPHA_SIDM_PRED  # = (8/81) × 0.0315 = 3.111e-3
print(f"  Predicted α_SIDM = {alpha_pred:.6e}")
print()

# Find viable points with α ≈ α_pred
for tol_pct in [5, 10, 20, 30]:
    tol = tol_pct / 100.0
    mask_alpha = np.abs(alpha - alpha_pred) / alpha_pred < tol
    n_match = mask_alpha.sum()
    print(f"  α within {tol_pct}% of {alpha_pred:.4e}: {n_match} points ({n_match/N*100:.2f}%)")
    if n_match > 0:
        print(f"    m_χ range: [{m_chi[mask_alpha].min():.2f}, {m_chi[mask_alpha].max():.2f}] GeV")
        print(f"    m_φ range: [{m_phi_MeV[mask_alpha].min():.2f}, {m_phi_MeV[mask_alpha].max():.2f}] MeV")
        print(f"    σ/m(30) range: [{sigma30[mask_alpha].min():.4f}, {sigma30[mask_alpha].max():.4f}]")

# ════════════════════════════════════════════════════════════════════════
#  Part 5: Yukawa parameter λ = α m_χ / m_φ
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 5: The resonance parameter λ = α m_χ / m_φ")
print("=" * 78)
print()

lam = alpha * m_chi / m_phi  # dimensionless Yukawa parameter
lam_MAP = 3.274e-3 * 98.19 / 0.00966

print(f"  λ(MAP) = {lam_MAP:.2f}")
print(f"  λ range: [{lam.min():.2f}, {lam.max():.2f}]")
print(f"  λ median: {np.median(lam):.2f}")
print()

# Does λ enter the relation? Test: α_d = C × α × f(λ)
# If f(λ) = (λ/λ_MAP)^n, then α_d = C × α × (α m_χ/m_φ)^n / λ_MAP^n
# This would give α_d(chain) ∝ α^{1+n} × (m_χ/m_φ)^n

# For universality: α_d = 0.0315 for ALL points
# So: C × α × f(λ) = 0.0315
# With C = 81/8: (81/8) × α × f(λ) = 0.0315
# f(λ) = 0.0315 / ((81/8) × α) = α_pred / α

# So the "correction" needed is: f(λ) = α_pred / α
f_correction = alpha_pred / alpha

# Is f_correction a function of λ?
print("  Testing: is f = α_pred/α correlated with λ?")
print()
print(f"  {'λ-bin':>10}  {'mean f':>10}  {'std f':>10}  {'N':>8}")
print(f"  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*8}")

lam_bins = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 25), (25, 30), (30, 40), (40, 60)]
for lo, hi in lam_bins:
    mask_bin = (lam >= lo) & (lam < hi)
    if mask_bin.sum() > 0:
        mean_f = f_correction[mask_bin].mean()
        std_f = f_correction[mask_bin].std()
        print(f"  [{lo:>3},{hi:>3})  {mean_f:>10.4f}  {std_f:>10.4f}  {mask_bin.sum():>8}")

print()

# Try functional forms: f(λ) = (λ)^n
# ln(f) = n × ln(λ) + const
# Fit n from the data
valid = (lam > 0.1) & (f_correction > 0)
if valid.sum() > 100:
    ln_f = np.log(f_correction[valid])
    ln_lam = np.log(lam[valid])
    
    # Linear regression: ln(f) = a + b × ln(λ)
    A = np.vstack([np.ones(valid.sum()), ln_lam]).T
    result = np.linalg.lstsq(A, ln_f, rcond=None)
    a, b = result[0]
    residual = np.sqrt(result[1][0] / valid.sum()) if len(result[1]) > 0 else np.nan
    
    print(f"  Power-law fit: f = C × λ^n")
    print(f"    n = {b:.4f}")
    print(f"    C = exp(a) = {math.exp(a):.6f}")
    print(f"    Residual: {residual:.4f}")
    print(f"    ⟹ α_d = (81/8) × α × C × λ^{b:.4f}")
    print(f"       = (81/8) × C × α^{{1+{b:.4f}}} × (m_χ/m_φ)^{{{b:.4f}}}")
    print()
    
    # Also try with m_phi/m_chi directly
    ratio = m_phi / m_chi  # m_φ/m_χ
    ln_r = np.log(ratio[valid])
    A2 = np.vstack([np.ones(valid.sum()), ln_r]).T
    result2 = np.linalg.lstsq(A2, ln_f, rcond=None)
    a2, b2 = result2[0]
    residual2 = np.sqrt(result2[1][0] / valid.sum()) if len(result2[1]) > 0 else np.nan
    print(f"  Mass ratio fit: f = C × (m_φ/m_χ)^n")
    print(f"    n = {b2:.4f}")
    print(f"    C = {math.exp(a2):.6f}")
    print(f"    Residual: {residual2:.4f}")
    print()
    
    # Try 2D fit: ln(f) = a + b1×ln(α) + b2×ln(m_χ/m_φ)
    ln_alpha = np.log(alpha[valid])
    ln_mrat = np.log(m_chi[valid] / m_phi[valid])
    A3 = np.vstack([np.ones(valid.sum()), ln_alpha, ln_mrat]).T
    result3 = np.linalg.lstsq(A3, ln_f, rcond=None)
    a3, b3_1, b3_2 = result3[0]
    print(f"  2D fit: f = C × α^p × (m_χ/m_φ)^q")
    print(f"    p = {b3_1:.4f}")
    print(f"    q = {b3_2:.4f}")
    print(f"    C = {math.exp(a3):.6f}")
    # Check at MAP
    f_MAP_pred = math.exp(a3) * (3.274e-3)**b3_1 * (98.19/0.00966)**b3_2
    alpha_d_MAP_2d = 81/8 * 3.274e-3 * f_MAP_pred
    print(f"    α_d(MAP) = {alpha_d_MAP_2d:.6f} (target: {ALPHA_D})")

# ════════════════════════════════════════════════════════════════════════
#  Part 6: Is there a SIMPLER relation? α_d from m_χ alone
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 6: Alternative — maybe the relation involves σ/m, not α alone")
print("=" * 78)
print()

# The SIDM cross-section σ/m depends on (m_χ, α, m_φ) in a complex way.
# Maybe what determines α_d is not α_SIDM alone but the PHYSICAL observable σ/m.
#
# Hypothesis: α_d = f(σ_T/m × m_φ²) — Born limit
# In the Born limit: σ_T/m ∝ α² m_χ / m_φ⁴
# So: α² m_χ / m_φ⁴ ~ σ/m → α² ~ σ/m × m_φ⁴ / m_χ

# Define the "Born parameter": B = α² × m_χ / m_φ⁴ (proportional to σ/m in Born)
B_born = alpha**2 * m_chi / (m_phi)**4  # units: GeV⁻³

# Test: is α_d correlated with B_born?
print("  Born parameter B = α² m_χ / m_φ⁴:")
print(f"  B(MAP) = {(3.274e-3)**2 * 98.19 / (0.00966)**4:.4e} GeV⁻³")

# ════════════════════════════════════════════════════════════════════════
#  Part 7: THE DEEP QUESTION — what if only MAP satisfies BOTH constraints?
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 7: Joint constraint surface")
print("=" * 78)
print()
print("  Constraint 1 (SIDM): (m_χ, α, m_φ) must give viable σ_T/m")
print("  Constraint 2 (gauge-Yukawa): α = (8/81) × α_d")
print("  Constraint 3 (DE): Λ_d = m_χ exp(-2π/(b₀α_d)) ≈ 2 meV")
print()
print("  Constraints 2+3 with α_d = (81/8)α give:")
print("    Λ_d = m_χ exp(-2π/(b₀ × 81α/8)) ≈ 2 meV")
print("  This defines a 1D curve α(m_χ) in the SIDM scan.")
print()

# Compute the required α for each m_χ such that Λ_d ≈ target
# Λ_d = m_χ exp(-2π/(b₀ × 81α/8)) = target
# -2π/(b₀ × 81α/8) = ln(target(GeV) / m_χ)
# α = -2π / (b₀ × (81/8) × ln(target(GeV)/m_χ))

# But target is in meV, need GeV: 2 meV = 2e-15 GeV
target_GeV = 2.0e-15  # 2 meV in GeV

m_chi_grid = np.linspace(m_chi.min(), m_chi.max(), 200)
alpha_required = np.zeros_like(m_chi_grid)

for i, mc in enumerate(m_chi_grid):
    log_ratio = math.log(target_GeV / mc)  # negative
    if log_ratio < 0:
        # α = -2π / (b₀ × 81/8 × ln(target/m_χ))
        alpha_required[i] = -2 * math.pi / (B0 * 81/8 * log_ratio)

print(f"  Required α(m_χ) for Λ_d = 2 meV:")
print(f"  {'m_χ [GeV]':>10}  {'α_required':>12}  {'α_d(chain)':>12}")
print(f"  {'─'*10}  {'─'*12}  {'─'*12}")
for mc_test in [15, 30, 50, 75, 98.19, 120, 150]:
    log_r = math.log(target_GeV / mc_test)
    alpha_req = -2*math.pi / (B0 * 81/8 * log_r)
    alpha_d_req = 81/8 * alpha_req
    print(f"  {mc_test:>10.2f}  {alpha_req:>12.4e}  {alpha_d_req:>12.6f}")

print()

# Now: for each SIDM viable point, how close is α to α_required(m_χ)?
alpha_req_at_point = np.zeros(N)
for i in range(N):
    log_r = math.log(target_GeV / m_chi[i])
    if log_r < 0:
        alpha_req_at_point[i] = -2*math.pi / (B0 * 81/8 * log_r)

fractional_diff = np.abs(alpha - alpha_req_at_point) / alpha_req_at_point
fractional_diff[alpha_req_at_point == 0] = 999

print(f"  Points satisfying α ≈ α_required(m_χ) for Λ_d ≈ 2 meV:")
for tol_pct in [5, 10, 20, 50]:
    tol = tol_pct / 100.0
    mask_joint = fractional_diff < tol
    n_joint = mask_joint.sum()
    print(f"    Within {tol_pct}%: {n_joint} points ({n_joint/N*100:.3f}%)")
    if 0 < n_joint <= 30:
        idx_j = np.where(mask_joint)[0]
        idx_sorted = idx_j[np.argsort(fractional_diff[idx_j])]
        print(f"    Best matches:")
        for i in idx_sorted[:10]:
            Ld = Lambda_d_meV(81/8*alpha[i], m_chi[i])
            print(f"      m_χ={m_chi[i]:.2f}, α={alpha[i]:.4e}, m_φ={m_phi_MeV[i]:.2f} MeV, "
                  f"Λ_d={Ld:.3f} meV, Δα={fractional_diff[i]*100:.1f}%")

# ════════════════════════════════════════════════════════════════════════
#  Part 8: The MAP region — zoom in
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 8: Zoom into MAP region")
print("=" * 78)
print()

# MAP point: m_χ=98.19, α=3.274e-3, m_φ=9.66 MeV
mask_MAP_region = (m_chi > 80) & (m_chi < 120) & (alpha > 2e-3) & (alpha < 5e-3)
n_map = mask_MAP_region.sum()
print(f"  Points near MAP (80-120 GeV, α 2-5e-3): {n_map}")

if n_map > 0:
    idx_map_region = np.where(mask_MAP_region)[0]
    
    # Compute α_d(chain) and Λ_d for region
    ad_reg = 81/8 * alpha[mask_MAP_region]
    Ld_reg = np.array([Lambda_d_meV(ad, mc) for ad, mc in 
                       zip(ad_reg, m_chi[mask_MAP_region])])
    
    print(f"  α_d(chain) range: [{ad_reg.min():.6f}, {ad_reg.max():.6f}]")
    print(f"  Λ_d range: [{Ld_reg.min():.4f}, {Ld_reg.max():.4f}] meV")
    
    # Best match to α_d = 0.0315
    diff_ad = np.abs(ad_reg - ALPHA_D)
    best_idx_local = np.argsort(diff_ad)[:10]
    print(f"\n  Best 10 matches to α_d = 0.0315:")
    print(f"  {'m_χ':>8}  {'m_φ[MeV]':>10}  {'α':>12}  {'α_d':>10}  {'Λ_d[meV]':>10}  {'σ/m(30)':>10}")
    print(f"  {'─'*8}  {'─'*10}  {'─'*12}  {'─'*10}  {'─'*10}  {'─'*10}")
    for k in best_idx_local:
        i = idx_map_region[k]
        print(f"  {m_chi[i]:>8.2f}  {m_phi_MeV[i]:>10.2f}  {alpha[i]:>12.4e}  {ad_reg[k]:>10.6f}  {Ld_reg[k]:>10.4f}  {sigma30[i]:>10.4f}")

# ════════════════════════════════════════════════════════════════════════
#  Part 9: Alternative — α_d from Λ_d = m_ν constraint ALONE
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 9: What if α_d is determined INDEPENDENTLY by Λ_d = m_ν?")
print("=" * 78)
print()
print("  The transmutation formula: Λ_d = m_χ exp(-2π/(b₀α_d))")
print("  If Λ_d = m_ν(seesaw) = v²/M_R:")
print("    α_d = 2π / (b₀ × ln(m_χ M_R / v²))")
print("  This gives α_d as a function of m_χ (and M_R, v).")
print()

# α_d for each viable point (M_R = 2e16)
alpha_d_from_matching = np.zeros(N)
for i in range(N):
    arg = m_chi[i] * M_R_GUT / V_EW**2
    if arg > 1:
        alpha_d_from_matching[i] = 2*math.pi / (B0 * math.log(arg))

print(f"  α_d(matching) range: [{alpha_d_from_matching[alpha_d_from_matching>0].min():.6f}, {alpha_d_from_matching.max():.6f}]")
print(f"  α_d(matching) at m_χ=98.19: {2*math.pi/(B0*math.log(98.19*M_R_GUT/V_EW**2)):.6f}")
print()

# Compare α_d(matching) with α_d(chain) = 81α/8
# If both constraints hold: α_d(matching) = (81/8)α
# ⟹ α = (8/81) × 2π/(b₀ ln(m_χ M_R/v²))
print("  IF both constraints hold simultaneously:")
print("    α_d(matching) = (81/8) × α")
print("    ⟹ α(predicted) = (8/81) × 2π/(b₀ ln(m_χ M_R/v²))")
print()
alpha_sidm_from_both = (8.0/81.0) * alpha_d_from_matching

# How many SIDM points actually satisfy this dual constraint?
dual_diff = np.abs(alpha - alpha_sidm_from_both) / alpha_sidm_from_both
dual_diff[alpha_sidm_from_both == 0] = 999

print(f"  Dual constraint matching:")
for tol_pct in [1, 5, 10, 20, 50]:
    mask_dual = dual_diff < tol_pct/100
    n_dual = mask_dual.sum()
    print(f"    Within {tol_pct}%: {n_dual} points ({n_dual/N*100:.3f}%)")

print()

# Show the best dual-matching points
best_dual = np.argsort(dual_diff)[:20]
print(f"  Top 20 dual-constraint matches:")
print(f"  {'m_χ':>8}  {'m_φ':>8}  {'α':>12}  {'α(pred)':>12}  {'α_d(match)':>10}  {'Δ%':>6}  {'σ/m(30)':>10}")
print(f"  {'─'*8}  {'─'*8}  {'─'*12}  {'─'*12}  {'─'*10}  {'─'*6}  {'─'*10}")
for i in best_dual:
    print(f"  {m_chi[i]:>8.2f}  {m_phi_MeV[i]:>8.2f}  {alpha[i]:>12.4e}  {alpha_sidm_from_both[i]:>12.4e}  {alpha_d_from_matching[i]:>10.6f}  {dual_diff[i]*100:>6.1f}  {sigma30[i]:>10.4f}")

# ════════════════════════════════════════════════════════════════════════
#  Part 10: How close is MAP to this dual constraint?
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  Part 10: How special is MAP?")
print("=" * 78)
print()

# MAP parameters
mc_MAP = 98.19
alpha_MAP = 3.274e-3
mphi_MAP = 9.66e-3  # GeV

alpha_d_match_MAP = 2*math.pi/(B0*math.log(mc_MAP*M_R_GUT/V_EW**2))
alpha_pred_MAP = (8/81) * alpha_d_match_MAP
dual_diff_MAP = abs(alpha_MAP - alpha_pred_MAP)/alpha_pred_MAP

print(f"  MAP point:")
print(f"    m_χ = {mc_MAP} GeV")
print(f"    α_SIDM = {alpha_MAP:.6e}")
print(f"    α_pred = (8/81) × α_d(Λ_d=m_ν) = {alpha_pred_MAP:.6e}")
print(f"    Dual constraint mismatch: {dual_diff_MAP*100:.1f}%")
print()

# Ranks: where does MAP sit in the dual_diff distribution?
# Can't directly test MAP since it may not be in the CSV exactly
# Find closest point to MAP in the scan
dist_to_map = np.sqrt(((m_chi - 98.19)/98.19)**2 + ((alpha - 3.274e-3)/3.274e-3)**2)
map_idx = np.argmin(dist_to_map)
print(f"  Closest scan point to MAP:")
print(f"    idx={map_idx}, m_χ={m_chi[map_idx]:.2f}, α={alpha[map_idx]:.4e}, m_φ={m_phi_MeV[map_idx]:.2f}")
print(f"    Dual mismatch: {dual_diff[map_idx]*100:.1f}%")
print(f"    Rank among {N} points: {np.searchsorted(np.sort(dual_diff), dual_diff[map_idx])+1}")
percentile = np.searchsorted(np.sort(dual_diff), dual_diff[map_idx]) / N * 100
print(f"    Percentile: {percentile:.1f}% (lower = better match)")

# ════════════════════════════════════════════════════════════════════════
#  VERDICT
# ════════════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("  ▌ VERDICT")
print("=" * 78)
print()
print("  G8d investigates what makes MAP special for y = g_d sinθ.")
print()
print("  Key questions answered:")
print("  1. How many viable points satisfy α_d(chain) ≈ 0.0315?")
print("  2. Does the joint SIDM + DE constraint select MAP?")
print("  3. Is there a universal relation with m_φ dependence?")
print("  4. How close is MAP to the dual constraint surface?")
