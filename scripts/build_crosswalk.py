#!/usr/bin/env python3
"""
Build every distributed format of the GRC Control Crosswalk from the single
source of truth: data/crosswalk.csv

Outputs
    GRC-Control-Crosswalk.xlsx          Excel workbook (overview + full crosswalk + one sheet per source framework)
    data/crosswalk.yaml                 YAML, one record per ISO 27001 control, with target-framework lists
    data/by-framework/<framework>.csv   Reverse views: each target framework -> ISO 27001 controls (and the others)

Usage
    pip install openpyxl pyyaml
    python scripts/build_crosswalk.py

No personal data. MIT License.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import yaml
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "crosswalk.csv"

FONT = "Arial"
NAVY = "1F3864"
MID = "2F5597"
PALE = "F2F2F2"
thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

FRAMEWORKS = {
    # column key : (display name, edition, column header in CSV)
    "iso27001_2022": ("ISO/IEC 27001", "2022, Annex A", "ISO 27001:2022"),
    "nist_csf_2": ("NIST CSF", "2.0 (subcategories)", "NIST CSF 2.0"),
    "cis_v8": ("CIS Controls", "v8 (safeguards)", "CIS Controls v8"),
    "iso42001": ("ISO/IEC 42001", "2023, Annex A", "ISO 42001"),
    "soc2_tsc": ("SOC 2", "Trust Services Criteria (2017, rev. 2022)", "SOC 2 TSC"),
}


def font(bold=False, color="000000", size=10, italic=False):
    return Font(name=FONT, bold=bold, color=color, size=size, italic=italic)


def fill(hex_color):
    return PatternFill("solid", start_color=hex_color, end_color=hex_color)


def header(ws, row, labels, bg=NAVY):
    for i, label in enumerate(labels, start=1):
        c = ws.cell(row=row, column=i, value=label)
        c.font = font(bold=True, color="FFFFFF")
        c.fill = fill(bg)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[row].height = 32


def load_rows() -> list[dict]:
    with SRC.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    required = ["domain", "iso27001_2022", "iso27001_title", "nist_csf_2", "cis_v8", "iso42001", "soc2_tsc", "notes"]
    for r in rows:
        missing = [k for k in required if not r.get(k)]
        if missing:
            raise SystemExit(f"Row {r.get('iso27001_2022')} is missing {missing}")
    ids = [r["iso27001_2022"] for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate ISO 27001 control identifiers in crosswalk.csv")
    return rows


def write_yaml(rows):
    records = []
    for r in rows:
        records.append({
            "iso27001_2022": r["iso27001_2022"],
            "title": r["iso27001_title"],
            "domain": r["domain"],
            "maps_to": {
                "nist_csf_2": r["nist_csf_2"],
                "cis_v8": r["cis_v8"],
                "iso42001": r["iso42001"],
                "soc2_tsc": r["soc2_tsc"],
            },
            "notes": r["notes"],
        })
    doc = {
        "crosswalk": {
            "version": "1.0",
            "source_framework": "ISO/IEC 27001:2022 Annex A",
            "target_frameworks": [v[2] for k, v in FRAMEWORKS.items() if k != "iso27001_2022"],
            "license": "MIT",
            "disclaimer": "Mappings are best-effort equivalences for planning and gap analysis, not an official or audited interpretation.",
        },
        "controls": records,
    }
    out = ROOT / "data" / "crosswalk.yaml"
    out.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    return out


def write_reverse_csvs(rows):
    outdir = ROOT / "data" / "by-framework"
    outdir.mkdir(parents=True, exist_ok=True)
    written = []
    for key, (name, edition, label) in FRAMEWORKS.items():
        if key == "iso27001_2022":
            continue
        groups: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            groups[r[key]].append(r)
        out = outdir / f"{key}.csv"
        others = [k for k in FRAMEWORKS if k not in (key, "iso27001_2022")]
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow([label, "iso27001_2022 controls", "control titles"] + [FRAMEWORKS[o][2] for o in others])
            for ref in sorted(groups, key=natural_key):
                grp = groups[ref]
                w.writerow([
                    ref,
                    "; ".join(g["iso27001_2022"] for g in grp),
                    "; ".join(g["iso27001_title"] for g in grp),
                    *["; ".join(sorted({g[o] for g in grp}, key=natural_key)) for o in others],
                ])
        written.append(out)
    return written


def natural_key(s: str):
    import re
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def write_xlsx(rows):
    wb = Workbook()

    # ---- Overview
    ws = wb.active
    ws.title = "00_Overview"
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 100
    ws["A1"].value = "GRC Control Crosswalk"
    ws["A1"].font = font(bold=True, color="FFFFFF", size=16)
    for col in (1, 2):
        ws.cell(row=1, column=col).fill = fill(NAVY)
    ws.row_dimensions[1].height = 32
    lines = [
        ("Purpose", "Map each ISO/IEC 27001:2022 Annex A control to its closest equivalents in NIST CSF 2.0, CIS Controls v8, ISO/IEC 42001:2023 and the SOC 2 Trust Services Criteria. Use it for gap analysis, to reuse evidence across audits, and to build a single control library."),
        ("Source framework", "ISO/IEC 27001:2022 Annex A (93 controls) — one row per control."),
        ("Target frameworks", ", ".join(v[2] for k, v in FRAMEWORKS.items() if k != "iso27001_2022") + "."),
        ("How to read a row", "The target identifier is the single best match (closest objective). Many-to-many relationships exist; use the 'notes' column and the per-framework sheets to see all ISO controls that land on the same target."),
        ("Granularity", "NIST CSF 2.0 at subcategory level (e.g. PR.AA-05); CIS v8 at safeguard level (e.g. CIS 6.8); ISO 42001 at Annex A control level (e.g. A.6.2.6); SOC 2 at criterion level (e.g. CC6.1)."),
        ("Formats", "This workbook, data/crosswalk.csv (source of truth), data/crosswalk.yaml and reverse CSVs per framework. All generated by scripts/build_crosswalk.py."),
        ("Disclaimer", "Best-effort equivalences for planning. Not an official mapping and not a substitute for reading each standard. Verify against the current editions before relying on it for certification."),
        ("Licence", "MIT — free to use, modify and redistribute. No personal data."),
    ]
    for i, (k, v) in enumerate(lines, start=3):
        a = ws.cell(row=i, column=1, value=k)
        a.font = font(bold=True)
        a.alignment = Alignment(vertical="top", wrap_text=True)
        b = ws.cell(row=i, column=2, value=v)
        b.font = font()
        b.alignment = Alignment(vertical="top", wrap_text=True)
        ws.row_dimensions[i].height = 46 if len(v) > 120 else 24

    # ---- Full crosswalk
    ws = wb.create_sheet("01_Crosswalk")
    heads = ["Domain", "ISO 27001:2022", "Control title", "NIST CSF 2.0", "CIS Controls v8", "ISO 42001", "SOC 2 TSC", "Notes"]
    keys = ["domain", "iso27001_2022", "iso27001_title", "nist_csf_2", "cis_v8", "iso42001", "soc2_tsc", "notes"]
    header(ws, 1, heads)
    for w, col in zip([16, 14, 46, 14, 14, 12, 11, 60], "ABCDEFGH"):
        ws.column_dimensions[col].width = w
    for ri, r in enumerate(rows, start=2):
        for ci, k in enumerate(keys, start=1):
            c = ws.cell(row=ri, column=ci, value=r[k])
            c.font = font(bold=(k == "iso27001_2022"))
            c.border = BORDER
            c.alignment = Alignment(vertical="top", wrap_text=True,
                                    horizontal="center" if k in ("iso27001_2022", "nist_csf_2", "cis_v8", "iso42001", "soc2_tsc") else "left")
            if ri % 2 == 0:
                c.fill = fill(PALE)
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = f"A1:H{len(rows) + 1}"

    # ---- Per target framework (reverse view)
    for key, (name, edition, label) in FRAMEWORKS.items():
        if key == "iso27001_2022":
            continue
        ws = wb.create_sheet(f"by_{key}"[:31])
        ws["A1"].value = f"{name} {edition} → ISO/IEC 27001:2022 controls"
        ws["A1"].font = font(bold=True, color="FFFFFF", size=12)
        for col in range(1, 5):
            ws.cell(row=1, column=col).fill = fill(MID)
        header(ws, 2, [label, "Number of ISO controls", "ISO 27001:2022 controls", "Control titles"])
        for w, col in zip([16, 12, 30, 90], "ABCD"):
            ws.column_dimensions[col].width = w
        groups: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            groups[r[key]].append(r)
        for ri, ref in enumerate(sorted(groups, key=natural_key), start=3):
            grp = groups[ref]
            vals = [ref, len(grp), "; ".join(g["iso27001_2022"] for g in grp), "; ".join(g["iso27001_title"] for g in grp)]
            for ci, v in enumerate(vals, start=1):
                c = ws.cell(row=ri, column=ci, value=v)
                c.font = font(bold=(ci == 1))
                c.border = BORDER
                c.alignment = Alignment(vertical="top", wrap_text=True, horizontal="center" if ci < 3 else "left")
        ws.freeze_panes = "A3"
        ws.auto_filter.ref = f"A2:D{len(groups) + 2}"

    out = ROOT / "GRC-Control-Crosswalk.xlsx"
    wb.properties.title = "GRC Control Crosswalk"
    wb.properties.description = "MIT-licensed control mapping across ISO 27001, NIST CSF 2.0, CIS v8, ISO 42001 and SOC 2."
    wb.save(out)
    return out


def main():
    rows = load_rows()
    outs = [write_xlsx(rows), write_yaml(rows), *write_reverse_csvs(rows)]
    for o in outs:
        print("Wrote", o.relative_to(ROOT))
    print(f"{len(rows)} ISO 27001:2022 controls mapped.")


if __name__ == "__main__":
    main()
