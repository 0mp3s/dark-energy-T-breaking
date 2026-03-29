"""Quick expanded scan: does Lambda_d/m_nu converge to 1?"""
import numpy as np
import math

M_CHI = 98.19
B0 = 19.0 / 3.0
V_EW = 246.22
GEV_TO_MEV = 1e12

print("=" * 75)
print("  FINE SCAN: alpha_d vs M_R  -->  Ratio = Lambda_d / m_nu(seesaw)")
print("  Lambda_d = m_chi * exp(-2pi/(b0*alpha_d)),  m_nu = v^2/M_R")
print("=" * 75)

alphas = np.linspace(0.028, 0.038, 11)
M_Rs = np.logspace(14.5, 17.0, 11)

header = "  alpha_d "
for MR in M_Rs:
    header += f"  {MR:.1e}"
print(header)
print("  " + "-" * 8 + ("  " + "-" * 9) * len(M_Rs))

for alpha in alphas:
    Ld = M_CHI * math.exp(-2 * math.pi / (B0 * alpha))
    row = f"  {alpha:.4f} "
    for MR in M_Rs:
        mnu = V_EW**2 / MR
        ratio = Ld / mnu
        if 0.9 <= ratio <= 1.1:
            marker = " *"
        elif 0.5 <= ratio <= 2.0:
            marker = " @"
        else:
            marker = "  "
        row += f"  {ratio:>7.3f}{marker}"
    print(row)

print()
print("  * = ratio in [0.9, 1.1]  (within 10%)")
print("  @ = ratio in [0.5, 2.0]  (within factor 2)")

# Part B: matching curve
print()
print("=" * 75)
print("  MATCHING CURVE: alpha_d that gives Lambda_d = m_nu(seesaw) exactly")
print("  (ratio = 1.000 everywhere on this curve)")
print("=" * 75)

M_R_fine = np.logspace(13, 18, 30)
print(f"  {'M_R [GeV]':>14}  {'alpha_d(match)':>14}  {'Lambda_d [meV]':>14}  {'m_nu [meV]':>12}  {'Ratio':>8}")
print(f"  {'-'*14}  {'-'*14}  {'-'*14}  {'-'*12}  {'-'*8}")

for MR in M_R_fine:
    denom = B0 * (math.log(M_CHI * MR) - 2 * math.log(V_EW))
    if denom <= 0:
        continue
    alpha_match = 2 * math.pi / denom
    Ld = M_CHI * math.exp(-2 * math.pi / (B0 * alpha_match))
    mnu = V_EW**2 / MR
    ratio = Ld / mnu
    marker = "  <-- OUR alpha_d" if abs(alpha_match - 0.0315) / 0.0315 < 0.05 else ""
    print(f"  {MR:>14.3e}  {alpha_match:>14.5f}  {Ld * GEV_TO_MEV:>14.4f}  {mnu * GEV_TO_MEV:>12.4f}  {ratio:>8.4f}{marker}")

# Part C: width of the ratio~1 band
print()
print("=" * 75)
print("  WIDTH OF THE ratio=1 BAND (how narrow is the convergence?)")
print("=" * 75)
print()
print(f"  {'M_R':>12}  {'alpha_min':>10}  {'alpha(r=1)':>10}  {'alpha_max':>10}  {'width':>8}  Note")
print(f"  {'-'*12}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*8}  ----")

for MR in [1e14, 3e14, 1e15, 3e15, 1e16, 2e16, 3e16, 1e17]:
    # Find alpha for ratio = 0.5, 1.0, 2.0
    a_list = {}
    for target in [0.5, 1.0, 2.0]:
        arg = target * V_EW**2 / (MR * M_CHI)
        if 0 < arg < 1:
            alpha = -2 * math.pi / (B0 * math.log(arg))
            if 0.01 < alpha < 0.2:
                a_list[target] = alpha
    if len(a_list) == 3:
        note = " <-- OUR" if abs(a_list[1.0] - 0.0315) / 0.0315 < 0.1 else ""
        print(f"  {MR:>12.0e}  {a_list[0.5]:>10.5f}  {a_list[1.0]:>10.5f}  {a_list[2.0]:>10.5f}  {a_list[2.0]-a_list[0.5]:>8.5f}{note}")

# Part D: The key question
print()
print("=" * 75)
print("  CONVERGENCE QUESTION: Does the matching curve 'attract' our model?")
print("=" * 75)
print()
print("  The matching condition alpha_d = 2pi / (b0 * ln(m_chi * M_R / v^2))")
print("  is a CURVE in the (alpha_d, M_R) plane where ratio = 1 exactly.")
print()
print("  Our model sits at:")
print(f"    alpha_d = 0.0315,  M_R = 2e16 GeV")
print(f"    Ratio = {M_CHI * math.exp(-2*math.pi/(B0*0.0315)) / (V_EW**2/2e16):.4f}")
print()
print("  The band where ratio is within factor 2 has width:")
denom_ours = B0 * (math.log(M_CHI * 2e16) - 2 * math.log(V_EW))
alpha_match_ours = 2 * math.pi / denom_ours
for tgt, lbl in [(0.5, "ratio=0.5"), (1.0, "ratio=1.0"), (2.0, "ratio=2.0")]:
    arg = tgt * V_EW**2 / (2e16 * M_CHI)
    a = -2 * math.pi / (B0 * math.log(arg))
    print(f"    {lbl}: alpha_d = {a:.5f}")

width_05 = abs(-2*math.pi/(B0*math.log(0.5*V_EW**2/(2e16*M_CHI))) - (-2*math.pi/(B0*math.log(2.0*V_EW**2/(2e16*M_CHI)))))
print(f"    Width (factor-2 band): delta_alpha = {width_05:.5f}")
print(f"    Our alpha: 0.0315 is at distance {abs(0.0315 - alpha_match_ours):.5f} from center")
print(f"    That's {abs(0.0315-alpha_match_ours)/width_05*100:.0f}% of the band width from center")
print()
print("  ANSWER: The ratio does NOT converge to 1 by magic.")
print("  But our specific (alpha_d, M_R) pair HAPPENS to sit on the curve.")
print(f"  The precision: ratio = {M_CHI * math.exp(-2*math.pi/(B0*0.0315)) / (V_EW**2/2e16):.3f} (32% off from exact 1)")
print("  But alpha_d(match) = 0.0319 vs ours 0.0315 = 1.2% match.")
print("  This is what makes it suggestive: not exact, but suspiciously close.")
