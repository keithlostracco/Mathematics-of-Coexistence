# The Mathematics of Coexistence

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18900496.svg)](https://doi.org/10.5281/zenodo.18900496)
[![Latest Release](https://img.shields.io/github/v/release/keithlostracco/ethics-theorem)](https://github.com/keithlostracco/ethics-theorem/releases/latest)
[![Verify](https://github.com/keithlostracco/ethics-theorem/actions/workflows/ci.yml/badge.svg)](https://github.com/keithlostracco/ethics-theorem/actions/workflows/ci.yml)

Source TeX files, verification scripts, and figure-generation code for the following paper series:

**Thermodynamics of Cooperation**

| Paper | Title |
| --- | --- |
| TC-I | Necessary Constraints |
| TC-II | Strategic Entropy Injection |
| TC-III | Accumulated Negentropy |
| TC-IV | Thermodynamic Friction |
| TC-V | Cooperative Equilibrium |
| TC-VI | Value Dynamics |

**A Theory of Ethics from First Principles**

| Paper | Title |
| --- | --- |
| Ethics-I | Thermodynamic Norms |

**Monograph**

| Paper | Title |
| --- | --- |
| — | The Mathematics of Coexistence: A Formal Framework for Universal Ethics |

Pre-built PDFs are available from [GitHub Releases](https://github.com/keithlostracco/ethics-theorem/releases/latest) or in [`pdf/`](pdf/).

## Repository Structure

```
pdf/                           Pre-built paper PDFs
tex/                           TeX sources
  shared/                      Shared bibliography and figures
  <paper>/paper/               Per-paper TeX source
scripts/
  run_verification.py          Consolidated verification runner
  generate_figures.py          Figure generation from verification data
  simulations/                 Verification scripts
  figures/                     Figure-rendering scripts
modules/                       Python computation library
VERIFICATION.md                Verification methodology and results
```

## Running Verification

```bash
git clone https://github.com/keithlostracco/ethics-theorem.git
cd ethics-theorem
uv venv
uv pip install -e .
python scripts/run_verification.py
```

Requires Python ≥ 3.11. Pass `-v` for verbose output. See [VERIFICATION.md](VERIFICATION.md) for details.

## License

[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) — see [LICENSE](LICENSE).

## Citation

> Lostracco, K. (2026). *The Mathematics of Coexistence: A Formal Framework for Universal Ethics.* Zenodo. https://doi.org/10.5281/zenodo.18900496
