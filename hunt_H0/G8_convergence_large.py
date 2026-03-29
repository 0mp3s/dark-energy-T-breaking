"""G8 Large-scale convergence test: does Lambda_d/m_nu -> 1 on bigger grids?"""
import numpy as np
import math

M_CHI = 98.19       # GeV
B0    = 19.0 / 3.0  # SU(2) one-loop beta coefficient
V_EW  = 246.22      # GeV
MEV   = 1e12        # GeV -> meV

def Lambda_d(alpha):
    return M_CHI * math.exp(-2*math.pi / (B0 * alpha))

def m_nu_seesaw(M_R, y=1.0):
    return y**2 * V_EW**2 / M_R

def ratio(alpha, M_R):
    return Lambda_d(alpha) / m_nu_seesaw(M_R)

# ── Part A: HUGE grid 51 x 51 ──────────────────────────────────────
print("=" * 80)
print("  PART A: 51×51 GRID — fraction of points with ratio near 1")
print("  alpha_d in [0.01, 0.10],  M_R in [10^12, 10^19]")
print("=" * 80)

N = 51
alphas = np.linspace(0.01, 0.10, N)
logMRs = np.linspace(12, 19, N)

count_01  = 0   # ratio in [0.9, 1.1]
count_02  = 0   # ratio in [0.5, 2.0]
count_1OoM = 0  # ratio in [0.1, 10] (within 1 OoM)
total = 0

for a in alphas:
    for logMR in logMRs:
        MR = 10**logMR
        r = ratio(a, MR)
        total += 1
        if 0.9 <= r <= 1.1:
            count_01 += 1
        if 0.5 <= r <= 2.0:
            count_02 += 1
        if 0.1 <= r <= 10:
            count_1OoM += 1

print(f"  Grid: {N}×{N} = {total} points")
print(f"  alpha_d: [{alphas[0]:.3f}, {alphas[-1]:.3f}]")
print(f"  log10(M_R): [{logMRs[0]:.0f}, {logMRs[-1]:.0f}]")
print()
print(f"  |ratio - 1| < 10%:      {count_01:4d} / {total} = {count_01/total*100:.1f}%")
print(f"  ratio in [0.5, 2.0]:    {count_02:4d} / {total} = {count_02/total*100:.1f}%")
print(f"  ratio in [0.1, 10]:     {count_1OoM:4d} / {total} = {count_1OoM/total*100:.1f}%")
print()
print(f"  => Most of parameter space does NOT have ratio~1.")
print(f"  => The fact that OUR point does is non-trivial.")

# ── Part B: Increase grid size systematically ───────────────────────
print()
print("=" * 80)
print("  PART B: Does the FRACTION of ratio~1 points change with grid size?")
print("  (If it converges, it means a fixed fraction of parameter space gives ratio~1)")
print("=" * 80)
print()
print(f"  {'Grid':>8}  {'Points':>8}  {'|r-1|<10%':>12}  {'r∈[0.5,2]':>12}  {'r∈[0.1,10]':>12}")
print(f"  {'-'*8}  {'-'*8}  {'-'*12}  {'-'*12}  {'-'*12}")

for N in [11, 21, 51, 101, 201]:
    a_arr = np.linspace(0.01, 0.10, N)
    MR_arr = np.logspace(12, 19, N)
    c01, c02, c1 = 0, 0, 0
    tot = N * N
    for a in a_arr:
        Ld = Lambda_d(a)
        for MR in MR_arr:
            r = Ld / m_nu_seesaw(MR)
            if 0.9 <= r <= 1.1: c01 += 1
            if 0.5 <= r <= 2.0: c02 += 1
            if 0.1 <= r <= 10:  c1  += 1
    print(f"  {N:>3}×{N:<3}  {tot:>8}  {c01/tot*100:>10.2f}%  {c02/tot*100:>10.2f}%  {c1/tot*100:>10.2f}%")

# ── Part C: Slice through OUR alpha_d — how ratio changes with M_R ─
print()
print("=" * 80)
print("  PART C: SLICE at alpha_d = 0.0315 — ratio vs M_R")
print("  (Does ratio approach 1 as M_R increases?)")
print("=" * 80)
print()

our_alpha = 0.0315
our_Ld = Lambda_d(our_alpha) * MEV
print(f"  Our Lambda_d({our_alpha}) = {our_Ld:.4f} meV")
print()
print(f"  {'log10(M_R)':>11}  {'M_R [GeV]':>14}  {'m_nu [meV]':>12}  {'Ratio':>10}  Note")
print(f"  {'-'*11}  {'-'*14}  {'-'*12}  {'-'*10}  ----")

for logMR in np.arange(10, 20.1, 0.5):
    MR = 10**logMR
    mnu = m_nu_seesaw(MR) * MEV
    r = our_Ld / mnu
    note = ""
    if abs(logMR - 16.3) < 0.3:
        note = " <-- OUR M_R region"
    if 0.9 <= r <= 1.1:
        note += " ***"
    elif 0.5 <= r <= 2.0:
        note += " *"
    print(f"  {logMR:>11.1f}  {MR:>14.3e}  {mnu:>12.4f}  {r:>10.4f}{note}")

print()
print("  Key: *** = within 10%, * = within factor 2")
print()
print("  ANSWER: At fixed alpha_d = 0.0315, the ratio sweeps from")
print(f"  ~0 (M_R too small → m_nu huge) to ~inf (M_R too large → m_nu tiny).")
print("  It crosses ratio=1 at ONE specific M_R value.")

# Find that M_R
# Lambda_d = v^2/M_R  =>  M_R = v^2 / Lambda_d
MR_match = V_EW**2 / Lambda_d(our_alpha)
print(f"  The crossing M_R = v²/Λ_d = {MR_match:.3e} GeV  (log10 = {math.log10(MR_match):.2f})")
print(f"  GUT scale M_R = 2e16 GeV  (log10 = {math.log10(2e16):.2f})")
print(f"  Difference: {abs(math.log10(MR_match) - math.log10(2e16)):.2f} orders of magnitude")

# ── Part D: Slice through OUR M_R — how ratio changes with alpha_d ─
print()
print("=" * 80)
print("  PART D: SLICE at M_R = 2×10^16 — ratio vs alpha_d")
print("=" * 80)
print()

our_MR = 2e16
our_mnu = m_nu_seesaw(our_MR) * MEV
print(f"  m_nu(seesaw, M_R=2e16) = {our_mnu:.4f} meV")
print()
print(f"  {'alpha_d':>10}  {'Lambda_d [meV]':>16}  {'Ratio':>10}  Note")
print(f"  {'-'*10}  {'-'*16}  {'-'*10}  ----")

for a in np.arange(0.010, 0.101, 0.002):
    Ld = Lambda_d(a) * MEV
    r = Ld / our_mnu
    note = ""
    if abs(a - 0.0315) < 0.001:
        note = " <-- OUR alpha_d"
    if 0.9 <= r <= 1.1:
        note += " ***"
    elif 0.5 <= r <= 2.0:
        note += " *"
    print(f"  {a:>10.4f}  {Ld:>16.6f}  {r:>10.4f}{note}")

# Find alpha for ratio=1
print()
denom = B0 * (math.log(M_CHI * our_MR) - 2 * math.log(V_EW))
alpha_match = 2 * math.pi / denom
print(f"  alpha_d(match, ratio=1) = {alpha_match:.5f}")
print(f"  Our alpha_d              = 0.03150")
print(f"  Discrepancy: {abs(alpha_match - 0.0315)/0.0315*100:.1f}%")

# ── Part E: THE DEFINITIVE ANSWER ──────────────────────────────────
print()
print("=" * 80)
print("  DEFINITIVE ANSWER: DOES RATIO CONVERGE TO 1?")
print("=" * 80)
print()
print("  NO. The ratio does not 'converge to 1' in general.")
print("  The ratio is r = m_χ exp(-2π/b₀α_d) × M_R / v²")
print("  It can take ANY positive value depending on (α_d, M_R).")
print()
print("  HOWEVER:")
print("  There exists a CURVE in (α_d, M_R) space where r = 1 exactly:")
print("    α_d = 2π / [b₀ ln(m_χ M_R / v²)]")
print()
print("  Our model parameters sit VERY CLOSE to this curve:")
print(f"    α_d(ours)  = 0.0315")
print(f"    α_d(match) = {alpha_match:.4f}")
print(f"    Agreement: {abs(alpha_match - 0.0315)/0.0315*100:.1f}%")
print()
print("  This means: if α_d and M_R were random, finding ourselves")
print("  this close to the ratio=1 curve is UNLIKELY but not impossible.")
print()

# Monte Carlo: what fraction of random (alpha, M_R) pairs land this close?
rng = np.random.default_rng(42)
N_MC = 1_000_000
a_mc = rng.uniform(0.01, 0.10, N_MC)
logMR_mc = rng.uniform(12, 19, N_MC)
Ld_mc = M_CHI * np.exp(-2*np.pi / (B0 * a_mc))
mnu_mc = V_EW**2 / 10**logMR_mc
r_mc = Ld_mc / mnu_mc

within_10pct = np.sum((r_mc > 0.9) & (r_mc < 1.1)) / N_MC
within_factor2 = np.sum((r_mc > 0.5) & (r_mc < 2.0)) / N_MC
within_1OoM = np.sum((r_mc > 0.1) & (r_mc < 10.0)) / N_MC

# Also: what fraction has alpha_match within 1.2% of their alpha?
alpha_match_mc = 2*np.pi / (B0 * (np.log(M_CHI * 10**logMR_mc) - 2*np.log(V_EW)))
close_to_curve = np.sum(np.abs(a_mc - alpha_match_mc) / alpha_match_mc < 0.012) / N_MC

print(f"  Monte Carlo ({N_MC:,} random draws, α∈[0.01,0.10], M_R∈[10^12,10^19]):")
print(f"    P(|ratio-1| < 10%)     = {within_10pct*100:.2f}%")
print(f"    P(ratio ∈ [0.5, 2])    = {within_factor2*100:.2f}%")
print(f"    P(ratio ∈ [0.1, 10])   = {within_1OoM*100:.2f}%")
print(f"    P(α within 1.2% of matching curve) = {close_to_curve*100:.2f}%")
print()
print("  BOTTOM LINE:")
print("  The ratio=1 coincidence requires a SPECIAL RELATION between α_d and M_R.")
print("  Our parameters satisfy this relation to 1.2% precision.")
print("  This is either:")
print("    (a) A coincidence (p ~ a few %)")
print("    (b) Evidence for a deeper structural connection (seesaw ↔ dark QCD)")
print("  Verdict: SUGGESTIVE — worth reporting, not yet proven.")
