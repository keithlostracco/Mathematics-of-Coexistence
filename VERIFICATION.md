# Verification Summary

This document describes the computational verification infrastructure for
the *Thermodynamics of Cooperation* series, *A Theory of Ethics from First Principles* series,
and the *Mathematics of Coexistence* monograph.

## Overview

Every theorem, proposition, and key equation in the paper series is independently
verified by at least one automated script. The scripts use a shared
`check()` / `section()` / `summary()` harness (defined in `modules/verify.py`)
that reports individual PASS/FAIL results and a final count.

| Suite | Location | Scripts | Checks |
|-------|----------|--------:|-------:|
| Core derivations | `scripts/simulations/derivations/` | 6 | 744 |
| Applied case studies | `scripts/simulations/applied/` | 22 | 447 (CORE) |
| **Total (CORE)** | | **12** | **1,191** |

All 1,191 checks pass with 0 failures.

## Core Derivation Scripts

These verify the mathematical results in Appendix A and the corresponding
paper sections.

| Script | Verifies |
|--------|----------|
| `verify_lagrangian_constraints.py` | Lagrangian formulation, shadow prices, KKT conditions (§IV, Appendix A) |
| `verify_thermodynamic_friction.py` | Entropy production bounds, friction costs (§IV, Appendix A) |
| `verify_information_entropy.py` | Information-theoretic identities, deception costs (§IV, Appendix A) |
| `verify_game_theory.py` | Nash equilibrium existence, δ* threshold, cooperative surplus (§V, Appendix A) |
| `verify_value_dynamics.py` | Value evolution equations, inequality dynamics (§V, Appendix A) |
| `verify_accumulated_negentropy.py` | Negentropy integrals, destruction-irrationality ratio (§V, Appendix A) |

## Applied Case-Study Scripts

These verify the applied case studies and generate figure data.
All 22 scripts live in `scripts/simulations/applied/`.

### Empirical Case Studies

Each applies the framework to a real-world scenario with historical data.

| Script | Application |
|--------|-------------|
| `verify_nile_water.py` | Nile Basin water-rights allocation |
| `verify_minimum_wage.py` | Minimum-wage constraint analysis |
| `verify_iraq_war.py` | Iraq War thermodynamic conflict costs |
| `verify_criminal_justice.py` | Criminal justice system friction |
| `verify_social_media.py` | Social-media misinformation entropy |
| `verify_corruption.py` | Corruption and institutional trust |
| `verify_governance.py` | Governance mechanism design |
| `verify_altruism.py` | Altruism as rational strategy |
| `verify_amazon.py` | Amazon deforestation negentropy loss |
| `verify_alexandria.py` | Library of Alexandria destruction cost |
| `verify_inequality.py` | Wealth-inequality dynamics |
| `verify_libya.py` | Libya intervention analysis |
| `verify_tariff.py` | Predictive tariff-policy model |
| `verify_alliance.py` | Alliance formation dynamics |
| `verify_power_concentration.py` | Power-concentration instability |
| `verify_tariff_value_dynamics.py` | Tariff-policy value-dynamics bandwidth |

### Framework Case Studies

These verify the six framework case studies and generate figure data.

| Script | Application |
|--------|-------------|
| `verify_resource_constraints.py` | Finite-resource constraint satisfaction |
| `verify_cooperative_equilibrium.py` | Multi-agent cooperative equilibrium |
| `verify_deception_entropy.py` | Deception-entropy penalty |
| `verify_adversarial_friction.py` | Adversarial exploitation friction cost |
| `verify_institutional_collapse.py` | Institutional ecosystem collapse |
| `verify_biosphere_preservation.py` | Biosphere-preservation rationality |

## How to Run

### Prerequisites

```bash
uv venv && uv pip install -e ".[dev]"
```

### Run All Checks

The recommended way is the consolidated runner:

```bash
python scripts/run_verification.py
```

Pass `-v` for verbose per-check output:

```bash
python scripts/run_verification.py -v
```

Or run scripts individually:

```bash
# Core
for f in scripts/simulations/derivations/verify_*.py; do python "$f"; done

# Applied case studies
for f in scripts/simulations/applied/verify_*.py; do python "$f"; done
```

**PowerShell:**

```powershell
Get-ChildItem scripts/simulations/derivations/verify_*.py | ForEach-Object { python $_.FullName }
Get-ChildItem scripts/simulations/applied/verify_*.py | ForEach-Object { python $_.FullName }
```

### Interpret Output

Each script prints check-by-check results followed by a summary:

```
========================================================================
  TOTAL: N/N passed, 0 failed
  ✓ ALL CHECKS PASSED
========================================================================
```

A non-zero exit code indicates at least one failure.

## Shared Library

All scripts import from `modules/`:

| Module | Role |
|--------|------|
| `verify.py` | `check()`, `section()`, `summary()`, numeric-comparison helpers |
| `lagrangian.py` | Constrained optimization computations |
| `thermodynamics.py` | Entropy and friction calculations |
| `information.py` | Information-theoretic measures |
| `game_theory.py` | Nash equilibrium solvers |
| `value_dynamics.py` | Value-evolution ODEs |
| `negentropy.py` | Accumulated negentropy integrals |

## Figure Generation

Six scripts in `scripts/figures/` produce the application figures:

| Script | Output |
|--------|--------|
| `fig_institutional_collapse.py` | Institutional ecosystem collapse |
| `fig_resource_pareto.py` | Resource-allocation Pareto frontier |
| `fig_burning_library.py` | Burning-library negentropy visualization |
| `fig_cooperative_equilibrium.py` | Cooperative equilibrium basin of attraction |
| `fig_deception_entropy.py` | Deception-entropy cost surface |
| `fig_adversarial_friction.py` | Adversarial friction landscape |

Figures are saved to `output/figures/`.
