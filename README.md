# The Mathematics of Coexistence

**A Formal Framework for Universal Ethics**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18900496.svg)](https://doi.org/10.5281/zenodo.18900496)
[![Latest Release](https://img.shields.io/github/v/release/keithlostracco/ethics-theorem)](https://github.com/keithlostracco/ethics-theorem/releases/latest)
[![Verify](https://github.com/keithlostracco/ethics-theorem/actions/workflows/ci.yml/badge.svg)](https://github.com/keithlostracco/ethics-theorem/actions/workflows/ci.yml)

> **Paper PDFs:** Download from [GitHub Releases](https://github.com/keithlostracco/ethics-theorem/releases/latest) or browse [`pdf/`](pdf/).

---

This repository is the **reproducibility package** for *The Mathematics of Coexistence*. It contains the computational verification scripts and figure-generation code that support every mathematical claim in the paper series. Run them locally to reproduce all results.

## What This Paper Does

We derive ethical principles as mathematical theorems from a single conditional axiom (the *intent to persist*) applied to agents modeled as open thermodynamic systems in a shared, finite-resource environment. This is applied mathematics, not speculative philosophy: every claim is either a theorem proven from axioms or a cited result from existing literature.

From one axiom, the framework proves:

- **Rights as constraints.** Using Lagrangian mechanics, rights emerge as inequality constraints whose shadow prices quantify the cost of violation.
- **Cooperation as equilibrium.** Using energy-denominated payoffs and repeated-game analysis, cooperation is the unique efficient Nash Equilibrium for agents with discount factor δ ≥ δ\* = 0.363, resolving the Folk Theorem's equilibrium-selection problem.
- **Deception as self-defeating.** Using information thermodynamics, deliberate entropy injection degrades the network the deceiver depends on.
- **Destruction as irrational.** Accumulated negentropy (the integrated thermodynamic work embodied in complex systems) proves that destroying a biosphere to harvest its energy is irrational by a factor of ~10⁷.

The framework comprises 28 theorems, 46 definitions, 13 propositions, and 2 lemmas, all computationally verified (744 checks, 0 failures).

**Keywords:** mathematical ethics · thermodynamic game theory · AI alignment · accumulated negentropy · cooperative equilibrium · Hume's Is-Ought problem · constrained optimization

---

## Repository Structure

```
pdf/                           Pre-built paper PDFs
tex/                           TeX sources
  shared/                      Shared bibliography and figures
  <paper>/paper/               Per-paper TeX source
scripts/
  run_verification.py          Run all verification scripts + consolidated report
  generate_figures.py          Render all figures from verification data
  simulations/
    derivations/               Core derivation verification scripts (6)
  figures/                     Figure-rendering scripts (8)
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

All computational checks can be run from the repository root:

```bash
python scripts/run_verification.py
```

This runs all verification scripts and prints a consolidated report. Pass `-v` for verbose per-check output.

### Verification Scripts

**Core derivation scripts** verify the mathematical results across all papers:

| Script | Verifies |
| --- | --- |
| `verify_lagrangian_constraints.py` | Lagrangian formulation, shadow prices, KKT conditions |
| `verify_thermodynamic_friction.py` | Entropy production bounds, friction costs |
| `verify_information_entropy.py` | Information-theoretic identities, deception costs |
| `verify_game_theory.py` | Nash equilibrium existence, δ\* threshold, cooperative surplus |
| `verify_value_dynamics.py` | Value evolution equations, inequality dynamics |
| `verify_accumulated_negentropy.py` | Negentropy integrals, destruction-irrationality ratio |

### Generating Figures

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
