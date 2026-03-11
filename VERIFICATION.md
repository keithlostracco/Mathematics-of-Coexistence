# Verification Summary

This document describes the computational verification infrastructure for
*The Mathematics of Coexistence*.

## Overview

Every theorem, proposition, and key equation in the paper is independently
verified by at least one automated script. The scripts use a shared
`check()` / `section()` / `summary()` harness (defined in `modules/verify.py`)
that reports individual PASS/FAIL results and a final count.

| Suite | Location | Scripts | Checks |
|-------|----------|--------:|-------:|
| Core derivations | `scripts/simulations/derivations/` | 6 | 744 |
| AI applications | `scripts/simulations/case-studies/ai/` | 6 | 447 |
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

## AI-Application Scripts

These verify the six AI-alignment applications in §VII and generate figure data.

| Script | Application |
|--------|-------------|
| `verify_resource_constraints.py` | Finite-resource constraint satisfaction |
| `verify_cooperative_equilibrium.py` | Multi-agent cooperative equilibrium |
| `verify_deception_entropy.py` | Deception-entropy penalty |
| `verify_misalignment_friction.py` | Reward-hacking friction cost |
| `verify_foundation_collapse.py` | Foundation model ecosystem collapse |
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
# Core derivations
for f in scripts/simulations/derivations/verify_*.py; do python "$f"; done

# AI applications
for f in scripts/simulations/case-studies/ai/verify_*.py; do python "$f"; done
```

**PowerShell:**

```powershell
Get-ChildItem scripts/simulations/derivations/verify_*.py | ForEach-Object { python $_.FullName }
Get-ChildItem scripts/simulations/case-studies/ai/verify_*.py | ForEach-Object { python $_.FullName }
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
| `fig_foundation_collapse.py` | Foundation model ecosystem collapse |
| `fig_resource_pareto.py` | Resource-allocation Pareto frontier |
| `fig_burning_library.py` | Burning-library negentropy visualization |
| `fig_cooperative_equilibrium.py` | Cooperative equilibrium basin of attraction |
| `fig_deceptive_alignment_entropy.py` | Deception-entropy cost surface |
| `fig_reward_hacking_friction.py` | Reward-hacking friction landscape |

Figures are saved to `output/figures/`.
