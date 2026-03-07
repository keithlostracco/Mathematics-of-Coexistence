# Verification Summary

This document describes the computational verification infrastructure for
*The Mathematics of Coexistence*.

## Overview

Every theorem, proposition, and key equation in the paper is independently
verified by at least one automated script. The scripts use a shared
`check()` / `section()` / `summary()` harness (defined in `modules/verify.py`)
that reports individual PASS/FAIL results and a final count.

| Suite              | Scripts | Checks |
| ------------------ | ------: | -----: |
| Core derivations   |       6 |    744 |
| **Total**          |   **6** |**744** |

All 744 checks pass with 0 failures.

## Core Derivation Scripts

These verify the mathematical results in Appendix A and the corresponding
paper sections.

| Script                              | Verifies                                                                          |
| ----------------------------------- | --------------------------------------------------------------------------------- |
| `verify_lagrangian_constraints.py`  | Lagrangian formulation, shadow prices, KKT conditions (§IV, Appendix A)           |
| `verify_thermodynamic_friction.py`  | Entropy production bounds, friction costs (§IV, Appendix A)                       |
| `verify_information_entropy.py`     | Information-theoretic identities, deception costs (§IV, Appendix A)               |
| `verify_game_theory.py`            | Nash equilibrium existence, δ\* threshold, cooperative surplus (§V, Appendix A)    |
| `verify_value_dynamics.py`         | Value evolution equations, inequality dynamics (§V, Appendix A)                    |
| `verify_accumulated_negentropy.py` | Negentropy integrals, destruction-irrationality ratio (§V, Appendix A)             |

## How to Run

### Prerequisites

```bash
uv venv && uv pip install -e .
```

### Run All Checks

The recommended way is the consolidated runner, which runs all scripts and prints a single summary table:

```bash
python scripts/run_verification.py
```

Or run scripts individually:

**Bash:**

```bash
for f in scripts/simulations/verify_*.py; do python "$f"; done
```

**PowerShell:**

```powershell
Get-ChildItem scripts/simulations/verify_*.py | ForEach-Object { python $_.FullName }
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

| Module             | Role                                            |
| ------------------ | ----------------------------------------------- |
| `verify.py`        | `check()`, `section()`, `summary()` helpers     |
| `lagrangian.py`    | Constrained optimization computations           |
| `thermodynamics.py`| Entropy and friction calculations               |
| `information.py`   | Information-theoretic measures                  |
| `game_theory.py`   | Nash equilibrium solvers                        |
| `value_dynamics.py`| Value-evolution ODEs                            |
| `negentropy.py`    | Accumulated negentropy integrals                |

## Figure Generation

Scripts in `scripts/figures/` produce the paper figures:

| Script                              | Output                                      |
| ----------------------------------- | ------------------------------------------- |
| `fig_ai_foundation_collapse.py`     | Foundation model ecosystem collapse (also used for power-concentration dynamics) |
| `fig_ai_resource_pareto.py`         | Resource-allocation Pareto frontier         |
| `fig_burning_library_ai.py`         | Burning-library negentropy visualization    |
| `fig_cooperative_ai_equilibrium.py` | Cooperative equilibrium basin of attraction  |
| `fig_deceptive_alignment_entropy.py`| Deception-entropy cost surface              |
| `fig_reward_hacking_friction.py`    | Reward-hacking friction landscape           |
| `fig_argument_stack.py`             | Argument structure diagram                  |

Figures are saved to `output/figures/`.
