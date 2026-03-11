# The Mathematics of Coexistence

**A Formal Framework for Universal Ethics**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18900496.svg)](https://doi.org/10.5281/zenodo.18900496)
[![Latest Release](https://img.shields.io/github/v/release/keithlostracco/ethics-theorem)](https://github.com/keithlostracco/ethics-theorem/releases/latest)
[![Verify](https://github.com/keithlostracco/ethics-theorem/actions/workflows/build-paper.yml/badge.svg)](https://github.com/keithlostracco/ethics-theorem/actions/workflows/build-paper.yml)

> **Paper PDF:** Download from [GitHub Releases](https://github.com/keithlostracco/ethics-theorem/releases/latest) or browse [`pdf/`](pdf/).

---

This repository is the **reproducibility package** for *The Mathematics of Coexistence*. It contains the computational verification scripts and figure-generation code that support every mathematical claim in the paper. Run them locally to reproduce all results.

## What This Paper Does

We derive ethical principles as mathematical theorems from a single conditional axiom — the *intent to persist* — applied to agents modeled as open thermodynamic systems in a shared, finite-resource environment. This is applied mathematics, not speculative philosophy: every claim is either a theorem proven from axioms or a cited result from existing literature.

From one axiom, the framework proves:

- **Rights as constraints.** Using Lagrangian mechanics, rights emerge as inequality constraints whose shadow prices quantify the cost of violation.
- **Cooperation as equilibrium.** Using energy-denominated payoffs and repeated-game analysis, cooperation is the unique efficient Nash Equilibrium for agents with discount factor δ ≥ δ\* = 0.363, resolving the Folk Theorem's equilibrium-selection problem.
- **Deception as self-defeating.** Using information thermodynamics, deliberate entropy injection degrades the network the deceiver depends on.
- **Destruction as irrational.** Accumulated negentropy — the integrated thermodynamic work embodied in complex systems — proves that destroying a biosphere to harvest its energy is irrational by a factor of ~10⁷.

The framework comprises 28 theorems, 46 definitions, 13 propositions, and 2 lemmas, all computationally verified (1,191 checks, 0 failures).

**Keywords:** mathematical ethics · thermodynamic game theory · AI alignment · accumulated negentropy · cooperative equilibrium · Hume's Is-Ought problem · constrained optimization

---

## Repository Structure

```
pdfs/                          Pre-built paper PDF
scripts/
  run_verification.py          Run all verification scripts + consolidated report
  generate_figures.py          Render all figures from verification data
  simulations/
    derivations/               Core derivation verification scripts (6)
    case-studies/ai/           AI application verification scripts (6)
  figures/                     Figure-rendering scripts (6)
modules/                       Python computation library
VERIFICATION.md                Verification methodology and results summary
```

## Getting Started

### Requirements

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

```bash
git clone https://github.com/keithlostracco/ethics-theorem.git
cd ethics-theorem
uv venv
uv pip install -e .
```

### Running Verification

All 1,191 computational checks can be run from the repository root:

```bash
python scripts/run_verification.py
```

This runs all verification scripts and prints a consolidated report. Pass `-v` for verbose per-check output.

### Verification Scripts

**Core derivation scripts** verify the mathematical results in the paper:

| Script | Verifies |
| --- | --- |
| `verify_lagrangian_constraints.py` | Lagrangian formulation, shadow prices, KKT conditions (§IV) |
| `verify_thermodynamic_friction.py` | Entropy production bounds, friction costs (§IV) |
| `verify_information_entropy.py` | Information-theoretic identities, deception costs (§IV) |
| `verify_game_theory.py` | Nash equilibrium existence, δ\* threshold, cooperative surplus (§V) |
| `verify_value_dynamics.py` | Value evolution equations, inequality dynamics (§V) |
| `verify_accumulated_negentropy.py` | Negentropy integrals, destruction-irrationality ratio (§V) |

**Application scripts** verify the applied results in §VII and generate figure data:

| Script | Verifies |
| --- | --- |
| `verify_misalignment_friction.py` | Reward-hacking friction landscape |
| `verify_deception_entropy.py` | Deception-entropy cost surface |
| `verify_cooperative_equilibrium.py` | Cooperative equilibrium basin of attraction |
| `verify_resource_constraints.py` | Resource-allocation Pareto frontier |
| `verify_biosphere_preservation.py` | Burning-library negentropy visualization |
| `verify_foundation_collapse.py` | Foundation model ecosystem collapse |

### Generating Figures

Verification scripts write intermediate data to `output/data/`. Figure scripts then render from that data:

```bash
python scripts/run_verification.py    # produces output/data/*.json
python scripts/generate_figures.py    # produces output/figures/*.png
```

## Computational Library

The `modules/` package provides reusable implementations of the framework's core mathematics:

| Module | Purpose |
| --- | --- |
| `lagrangian.py` | Constrained optimization and shadow-price computation |
| `thermodynamics.py` | Entropy production and thermodynamic friction |
| `information.py` | Information-theoretic measures and deception costs |
| `game_theory.py` | Nash equilibrium and cooperative surplus calculations |
| `value_dynamics.py` | Value evolution and inequality dynamics |
| `negentropy.py` | Accumulated negentropy and destruction-irrationality |
| `plotting.py` | Shared visualization utilities |
| `figure_data.py` | Save/load figure data (JSON) between verify and figure scripts |
| `verify.py` | Test harness (`check()` / `section()` helpers) |

## License

This work is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/) — see [LICENSE](LICENSE) for details.

## Citation

If you reference this work, please cite:

> Lostracco, K. (2026). *The Mathematics of Coexistence: A Formal Framework for Universal Ethics.* Zenodo. https://doi.org/10.5281/zenodo.18900496
