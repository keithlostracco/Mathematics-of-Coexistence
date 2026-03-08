# The Mathematics of Coexistence

**A Formal Framework for Universal Ethics**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18900496.svg)](https://doi.org/10.5281/zenodo.18900496)
[![Latest Release](https://img.shields.io/github/v/release/keithlostracco/ethics-theorem)](https://github.com/keithlostracco/ethics-theorem/releases/latest)

> **Paper PDF:** Download the latest revision from [GitHub Releases](https://github.com/keithlostracco/ethics-theorem/releases/latest) or [Zenodo](https://zenodo.org/records/18900496).

---

This repository contains the paper, mathematical derivations, verification scripts, and figure-generation code for *The Mathematics of Coexistence*.

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
paper/                                Main manuscript (§0–§IX + references)
supplementary/
  A-mathematical-derivations/         Full proofs and derivations (5 files)
  E-conceptual-overview/              Conceptual overview for non-mathematical readers
scripts/
  simulations/                        Core verification scripts (6)
  simulations/applications/           Application verification scripts (6)
  simulations/case-studies/           Case study scripts (non-CORE)
  figures/                            Figure-rendering scripts
  build_paper.py                      Pandoc → PDF build script
  generate_figures.py                 Render all figures from pre-computed data
  run_verification.py                 Run all scripts + consolidated report
modules/                              Python computation library
output/
  figures/                            Generated figures (gitignored)
  data/                               Generated data (gitignored)
```

## Paper Sections

| §    | File                                   | Title                         |
| ---- | -------------------------------------- | ----------------------------- |
| 0    | `paper/00-abstract.md`                 | Abstract                      |
| I    | `paper/01-introduction.md`             | Introduction                  |
| II   | `paper/02-literature-review.md`        | Literature Review             |
| III  | `paper/03-axioms-definitions.md`       | Axioms & Definitions          |
| IV   | `paper/04-rights-constraints.md`       | Rights as Constraints         |
| V    | `paper/05-ethics-equilibrium.md`       | Ethics as Equilibrium         |
| VI   | `paper/06-stress-testing.md`           | Stress-Testing                |
| VII  | `paper/07-applications.md`             | Applications and Implications |
| VIII | `paper/08-limitations-scope-future.md` | Limitations, Scope & Future   |
| IX   | `paper/09-conclusion.md`              | Conclusion                    |
| —    | `paper/references.bib`                | Bibliography                  |

## Supplementary Material

**Appendix A — Mathematical Derivations.** Complete proofs for:

| File                        | Domain                                                                    |
| --------------------------- | ------------------------------------------------------------------------- |
| `lagrangian-constraints.md` | Lagrangian formulation, shadow prices, KKT conditions                     |
| `thermodynamic-friction.md` | Entropy production bounds, friction costs                                 |
| `information-negentropy.md` | Information-theoretic identities, deception costs, accumulated negentropy |
| `game-theory-payoffs.md`    | Nash equilibrium existence, δ\* threshold, cooperative surplus            |
| `value-dynamics.md`         | Value evolution equations, inequality dynamics                            |

## Getting Started

### Requirements

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

For building the PDF:
- [Pandoc](https://pandoc.org/) ≥ 3.0
- A LaTeX distribution (TeX Live, MiKTeX, or TinyTeX)

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

This runs all 13 scripts and prints a consolidated report:

```
  FINAL REPORT
========================================================================
  Script                                            Passed  Failed    Time
  ------------------------------------------------  ------  ------  ------
  ✓ verify_lagrangian_constraints.py                    90       0    0.9s
  ✓ verify_thermodynamic_friction.py                   172       0    0.4s
  ✓ verify_information_entropy.py                      127       0    0.5s
  ✓ verify_game_theory.py                              143       0    0.4s
  ✓ verify_value_dynamics.py                           107       0    0.5s
  ✓ verify_accumulated_negentropy.py                   105       0    0.3s
  ✓ verify_misalignment_friction.py                    54       0    0.3s
  ✓ verify_deception_entropy.py                        105       0    0.6s
  ✓ verify_cooperative_equilibrium.py                   84       0    0.3s
  ✓ verify_resource_constraints.py                      23       0    0.6s
  ✓ verify_biosphere_preservation.py                    67       0    0.3s
  ✓ verify_foundation_collapse.py                      114       0    0.5s
  ------------------------------------------------  ------  ------  ------
  TOTAL                                               1191       0    5.7s

  ✓ ALL 1191/1191 CHECKS PASSED
========================================================================
```

Pass `-v` for verbose per-check output:

```bash
python scripts/run_verification.py -v
```

### Verification Scripts

**Core derivation scripts** verify the mathematical results in the paper and Appendix A:

| Script                              | Verifies                                                            |
| ----------------------------------- | ------------------------------------------------------------------- |
| `verify_lagrangian_constraints.py`  | Lagrangian formulation, shadow prices, KKT conditions (§IV)         |
| `verify_thermodynamic_friction.py`  | Entropy production bounds, friction costs (§IV)                     |
| `verify_information_entropy.py`     | Information-theoretic identities, deception costs (§IV)             |
| `verify_game_theory.py`             | Nash equilibrium existence, δ\* threshold, cooperative surplus (§V) |
| `verify_value_dynamics.py`          | Value evolution equations, inequality dynamics (§V)                 |
| `verify_accumulated_negentropy.py`  | Negentropy integrals, destruction-irrationality ratio (§V)          |

**Application scripts** verify the applied results in §VII and generate figure data:

| Script                                 | Verifies                                            |
| -------------------------------------- | --------------------------------------------------- |
| `verify_misalignment_friction.py`      | Reward-hacking friction landscape (§VII)            |
| `verify_deception_entropy.py`          | Deception-entropy cost surface (§VII)               |
| `verify_cooperative_equilibrium.py`    | Cooperative equilibrium basin of attraction (§VII)  |
| `verify_resource_constraints.py`       | Resource-allocation Pareto frontier (§VII)          |
| `verify_biosphere_preservation.py`     | Burning-library negentropy visualization (§VII)     |
| `verify_foundation_collapse.py`        | Foundation model ecosystem collapse (§VII)          |

### Generating Figures

Figure scripts render from JSON data generated by the verification suite in `output/data/`:

```bash
python scripts/generate_figures.py   # render all figures
```

Figures are written to `output/figures/`.

### Building the PDF

```bash
python scripts/build_paper.py
```

This runs verification, generates figures, then calls Pandoc with `--citeproc` to render all `[@BibKey]` citations from `paper/references.bib` and produces `output/ethics-theorem.pdf`. See `python scripts/build_paper.py --help` for options.

## Computational Library

The `modules/` package provides reusable implementations of the framework's core mathematics:

| Module              | Purpose                                                                |
| ------------------- | ---------------------------------------------------------------------- |
| `lagrangian.py`     | Constrained optimization and shadow-price computation                  |
| `thermodynamics.py` | Entropy production and thermodynamic friction                          |
| `information.py`    | Information-theoretic measures and deception costs                     |
| `game_theory.py`    | Nash equilibrium and cooperative surplus calculations                  |
| `value_dynamics.py` | Value evolution and inequality dynamics                                |
| `negentropy.py`     | Accumulated negentropy and destruction-irrationality                   |
| `plotting.py`       | Shared visualization utilities                                         |
| `figure_data.py`    | Save/load figure data (JSON) between verify and figure scripts         |
| `verify.py`         | Test harness (`check()` / `section()` helpers)                         |

## License

This work is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/) — see [LICENSE](LICENSE) for details.

## Citation

If you reference this work, please cite:

> Lostracco, K. (2026). *The Mathematics of Coexistence: A Formal Framework for Universal Ethics.* Zenodo. https://doi.org/10.5281/zenodo.18900496
