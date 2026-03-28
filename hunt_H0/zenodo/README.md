# Layer 8: Deriving H₀ from a Dark Matter Lagrangian via Coupled σ–Friedmann ODE

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19225823.svg)](https://doi.org/10.5281/zenodo.19225823)

## Description

Numerical solver for the coupled Klein-Gordon + Friedmann system that derives the Hubble constant H₀ as an **output** of a self-interacting dark matter (SIDM) Lagrangian extended with a dark QCD axion sector.

The dark axion field σ — a pseudo-Nambu-Goldstone boson of dark SU(2) chiral symmetry breaking — evolves in the potential V(σ) = Λ_d⁴(1 − cos(σ/f)) from reheating to today. The Hubble parameter H₀ = H(t₀) emerges from the numerical solution without being assumed.

## Key Result

With 6 Lagrangian parameters (m_χ, m_φ, α_D, f, Λ_d, θ_i) and observed Ω_χh² = 0.120:

| θ_i (rad) | H₀ (km/s/Mpc) | Ω_DE | w_σ |
|---|---|---|---|
| 3.0 | 71.1 | 0.72 | −0.86 |
| 3.1 | 73.1 | 0.73 | −0.99 |

The field naturally produces **dynamical dark energy** (w ≠ −1), distinguishable from ΛCDM by DESI/Euclid/CMB-S4.

## Physics

- The same Lagrangian that solves SIDM phenomenology (velocity-dependent cross sections, relic density Ωh² = 0.120, A₄ CP angle θ = 19.47°) also contains a dark axion that drives late-time acceleration.
- Λ_d ~ 2 meV = √(H₀ M_Pl) — the neutrino mass scale coincidence.
- Hilltop quintessence: θ_i ≈ π required for observed H₀.

## Files

| File | Description |
|---|---|
| `layer8_cosmic_ode.py` | **Self-contained** solver — no external dependencies beyond numpy/scipy/matplotlib. Includes embedded Boltzmann solver (Layer 7). |
| `layer8_evolution.png` | Four-panel diagnostic plot: θ(N), H(N), ρ(N), w(N) |
| `README.md` | This file |

## Requirements

```
Python >= 3.9
numpy
scipy
matplotlib  (for plotting only)
```

No other dependencies. This is fully self-contained — runs without the parent repository.

## Quick Start

```bash
python layer8_cosmic_ode.py
```

## Usage as Library

```python
from layer8_cosmic_ode import solve_layer8

result = solve_layer8(
    m_chi=98.19,        # GeV
    m_phi_GeV=9.66e-3,  # GeV
    alpha_d=3.274e-3,
    f=0.27 * 2.435e18,  # 0.27 M_Pl in GeV
    Lambda_d=2.0e-12,   # GeV (2 meV)
    theta_i=3.0,        # rad (near π)
    omega_chi_h2=0.120,
)

print(f"H₀ = {result.H0_kms:.2f} km/s/Mpc")
print(f"w_σ = {result.w_sigma:.4f}")
```

## Related

- **Paper 1 (SIDM):** [Secluded-Majorana-SIDM](https://github.com/0mp3s/Secluded-Majorana-SIDM) — Full numerical pipeline for velocity-dependent SIDM cross sections.
- **Paper 2 (in preparation):** Dark energy from the same Lagrangian — Layer 8 connects dark matter and dark energy.

## Citation

```bibtex
@software{SIDM_code:2026,
    author  = {Pesach, Omer},
    title   = {{Secluded Majorana SIDM}},
    version = {v0.1.0},
    year    = {2026},
    publisher = {Zenodo},
    doi     = {10.5281/zenodo.19225823},
    url     = {https://doi.org/10.5281/zenodo.19225823}
}
```

## License

CC-BY-4.0
