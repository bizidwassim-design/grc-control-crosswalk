# Contributing

Mapping work benefits enormously from a second pair of eyes. Fixes, better matches, caveats in the notes column,
translations and new target frameworks are all welcome.

## The one rule

**Edit `data/crosswalk.csv` only.** The YAML, the reverse CSVs and the Excel workbook are generated —
never edit them by hand. Regenerate with:

```bash
pip install openpyxl pyyaml
python scripts/build_crosswalk.py
```

Commit the CSV change together with the regenerated files.

## Proposing a mapping change

1. Open an issue or a pull request titled with the ISO control, e.g. `A.8.16 → NIST DE.CM-01 vs DE.CM-03`.
2. Quote (briefly) the text of both controls you are comparing and explain why the new target is a closer match.
3. If a control genuinely maps to several targets, keep the **closest** one in the cell and describe the others in `notes`.
4. Keep identifiers in the canonical form used in the file: `PR.AA-05`, `CIS 6.8`, `A.6.2.6`, `CC6.1`.

## Adding a target framework

1. Add a column to `data/crosswalk.csv` (e.g. `pci_dss_4`) and fill it for all 93 rows.
2. Add the key to `FRAMEWORKS` in `scripts/build_crosswalk.py` with its display name and edition.
3. Regenerate and check the new `by_<framework>` sheet and CSV.

## Ground rules

* No reproduction of the standards' copyrighted text — identifiers and short titles only.
* No personal data, no client-specific content.
* Be respectful — see the [Code of Conduct](CODE_OF_CONDUCT.md).
* By contributing you agree your work is released under the [MIT License](LICENSE).
