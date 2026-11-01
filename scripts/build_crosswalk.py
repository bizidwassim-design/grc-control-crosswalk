#!/usr/bin/env python3
"""
Build every distributed format of the GRC Control Crosswalk from the hand-edited sources:
    data/crosswalk.csv            one row per ISO/IEC 27001:2022 Annex A control (source of truth)
    data/overlays/<overlay>.csv   UAE and sector overlays (UAE IAR, DESC ISR, UAE PDPL, PCI DSS, NIST SP 800-53,
                                  ISO 22301), each row keyed to Annex A controls and/or ISMS clauses

Outputs
    GRC-Control-Crosswalk.xlsx          Excel workbook (overview, full crosswalk, ISO -> overlays, one sheet per
                                        target framework and per overlay)
    data/crosswalk.yaml                 YAML, one record per ISO 27001 control, with target-framework and overlay lists
    data/iso27001-overlays.csv          Each ISO 27001 control -> the overlay identifiers that reference it
    data/by-framework/<framework>.csv   Reverse views: each target framework / overlay -> ISO 27001 controls

Usage
    pip install openpyxl pyyaml
    python scripts/build_crosswalk.py

The sources are validated first (scripts/validate_crosswalk.py); nothing is written if validation fails.
The workbook is written with fixed timestamps so that rebuilding unchanged data gives identical bytes.
No personal data. MIT License.
"""
from __future__ import annotations

import csv
import io
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.writer.excel import ExcelWriter

from validate_crosswalk import OVERLAYS, VERIFICATION, load_all, split_list

ROOT = Path(__file__).resolve().parent.parent
BUILD_DATE = datetime(2026, 11, 1)  # fixed workbook timestamp for reproducible output; bump on release

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


OVERLAY_DISCLAIMER = (
    "Overlays are informative expert-judgement mappings for planning and gap analysis. They are not legal advice, "
    "not an official mapping by any regulator or standards body, and not a substitute for the current official texts. "
    "Laws and regulations change: check current status (for the UAE PDPL, the Executive Regulations; DIFC and ADGM "
    "have their own data protection regimes) before relying on them."
)


def overlay_index(overlays: dict[str, list[dict]]) -> dict[str, dict[str, list[str]]]:
    """ISO 27001 control -> {overlay key: [overlay refs that reference it]} (source order preserved)."""
    index: dict[str, dict[str, list[str]]] = defaultdict(lambda: {k: [] for k in OVERLAYS})
    for key, items in overlays.items():
        for item in items:
            for control in split_list(item["iso27001_2022"]):
                index[control][key].append(item["ref"])
    return index


def overlay_record(item: dict, key: str) -> dict:
    rec = {
        "ref": item["ref"],
        "title": item["title"],
    }
    if item["group"]:
        rec["group"] = item["group"]
    for extra in OVERLAYS[key]["extra"]:
        rec[extra] = split_list(item[extra]) if extra == "priority" else item[extra]
    rec["iso27001_2022"] = split_list(item["iso27001_2022"])
    rec["iso27001_clauses"] = split_list(item["iso27001_clauses"])
    rec["confidence"] = item["confidence"]
    rec["verification"] = item["verification"]
    if item["notes"]:
        rec["notes"] = item["notes"]
    return rec


def write_yaml(rows, overlays):
    index = overlay_index(overlays)
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
            "overlays": {k: index[r["iso27001_2022"]][k] for k in OVERLAYS},
            "notes": r["notes"],
        })
    doc = {
        "crosswalk": {
            "version": "1.1",
            "source_framework": "ISO/IEC 27001:2022 Annex A",
            "target_frameworks": [v[2] for k, v in FRAMEWORKS.items() if k != "iso27001_2022"],
            "overlays": [OVERLAYS[k]["label"] for k in OVERLAYS],
            "license": "MIT",
            "disclaimer": "Mappings are best-effort equivalences for planning and gap analysis, not an official or audited interpretation.",
            "overlay_disclaimer": OVERLAY_DISCLAIMER,
            "verification_levels": VERIFICATION,
        },
        "controls": records,
        "overlays": {
            key: {
                "name": meta["name"],
                "edition": meta["edition"],
                "granularity": meta["granularity"],
                "items": [overlay_record(item, key) for item in overlays[key]],
            }
            for key, meta in OVERLAYS.items()
        },
    }
    out = ROOT / "data" / "crosswalk.yaml"
    out.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8", newline="\n")
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


def overlay_columns(key: str) -> list[tuple[str, str]]:
    """(source column, display header) pairs for an overlay's reverse view, in output order."""
    cols = [
        ("ref", OVERLAYS[key]["label"]),
        ("title", "title"),
        ("group", "group"),
        ("iso27001_2022", "iso27001_2022 controls"),
        ("_titles", "control titles"),
        ("iso27001_clauses", "iso27001_2022 clauses"),
        ("confidence", "confidence"),
        ("verification", "verification"),
    ]
    cols += [(extra, extra) for extra in OVERLAYS[key]["extra"]]
    cols.append(("notes", "notes"))
    return cols


def overlay_cell(item: dict, col: str, titles: dict[str, str]) -> str:
    if col == "_titles":
        return "; ".join(titles[c] for c in split_list(item["iso27001_2022"]))
    return item[col]


def write_overlay_csvs(rows, overlays):
    """data/by-framework/<overlay>.csv: each overlay item -> ISO 27001 controls and clauses (source order)."""
    outdir = ROOT / "data" / "by-framework"
    titles = {r["iso27001_2022"]: r["iso27001_title"] for r in rows}
    written = []
    for key in OVERLAYS:
        cols = overlay_columns(key)
        out = outdir / f"{key}.csv"
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow([h for _, h in cols])
            for item in overlays[key]:
                w.writerow([overlay_cell(item, c, titles) for c, _ in cols])
        written.append(out)
    return written


def write_iso_overlay_csv(rows, overlays):
    """data/iso27001-overlays.csv: each ISO 27001 control -> the overlay identifiers that reference it."""
    index = overlay_index(overlays)
    out = ROOT / "data" / "iso27001-overlays.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["iso27001_2022", "iso27001_title"] + list(OVERLAYS))
        for r in rows:
            w.writerow([r["iso27001_2022"], r["iso27001_title"]] + ["; ".join(index[r["iso27001_2022"]][k]) for k in OVERLAYS])
    return out


def natural_key(s: str):
    import re
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def save_reproducible(wb: Workbook, out: Path) -> None:
    """Save with fixed document and zip timestamps so unchanged data gives byte-identical workbooks."""
    wb.properties.created = BUILD_DATE
    wb.properties.modified = BUILD_DATE
    raw = io.BytesIO()
    with zipfile.ZipFile(raw, "w", zipfile.ZIP_DEFLATED) as archive:
        ExcelWriter(wb, archive).save()
    fixed = io.BytesIO()
    with zipfile.ZipFile(raw) as src, zipfile.ZipFile(fixed, "w", zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            entry = zipfile.ZipInfo(info.filename, date_time=BUILD_DATE.timetuple()[:6])
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            dst.writestr(entry, src.read(info.filename))
    out.write_bytes(fixed.getvalue())


def write_xlsx(rows, overlays):
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
        ("UAE and sector overlays", "; ".join(f"{m['label']} ({m['edition']}, by {m['granularity']})" for m in OVERLAYS.values()) + ". Each overlay item lists every Annex A control (and ISMS clause) it relies on — see 02_ISO_to_overlays and the ov_* sheets."),
        ("Confidence", "high = same objective and scope; medium = partial overlap, or the overlay item adds requirements ISO 27001 does not have."),
        ("Verification", " ".join(f"{k}: {v}" for k, v in VERIFICATION.items()) + " Sources are listed in docs/sources.md."),
        ("Formats", "This workbook, data/crosswalk.csv and data/overlays/*.csv (sources of truth), data/crosswalk.yaml, data/iso27001-overlays.csv and reverse CSVs per framework. All generated by scripts/build_crosswalk.py."),
        ("Disclaimer", "Best-effort equivalences for planning. Not an official mapping and not a substitute for reading each standard. Verify against the current editions before relying on it for certification."),
        ("Overlay disclaimer", OVERLAY_DISCLAIMER),
        ("Licence", "MIT — free to use, modify and redistribute. No personal data."),
    ]
    for i, (k, v) in enumerate(lines, start=3):
        a = ws.cell(row=i, column=1, value=k)
        a.font = font(bold=True)
        a.alignment = Alignment(vertical="top", wrap_text=True)
        b = ws.cell(row=i, column=2, value=v)
        b.font = font()
        b.alignment = Alignment(vertical="top", wrap_text=True)
        ws.row_dimensions[i].height = max(24, 14 * (len(v) // 95 + 1))

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

    # ---- ISO 27001 control -> overlay identifiers
    index = overlay_index(overlays)
    ws = wb.create_sheet("02_ISO_to_overlays", 2)
    heads = ["ISO 27001:2022", "Control title"] + [OVERLAYS[k]["label"] for k in OVERLAYS]
    header(ws, 1, heads)
    for w, col in zip([14, 46] + [18] * len(OVERLAYS), "ABCDEFGH"):
        ws.column_dimensions[col].width = w
    for ri, r in enumerate(rows, start=2):
        vals = [r["iso27001_2022"], r["iso27001_title"]] + ["; ".join(index[r["iso27001_2022"]][k]) for k in OVERLAYS]
        for ci, v in enumerate(vals, start=1):
            c = ws.cell(row=ri, column=ci, value=v)
            c.font = font(bold=(ci == 1))
            c.border = BORDER
            c.alignment = Alignment(vertical="top", wrap_text=True, horizontal="center" if ci != 2 else "left")
            if ri % 2 == 0:
                c.fill = fill(PALE)
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:{chr(ord('A') + len(heads) - 1)}{len(rows) + 1}"

    # ---- Per overlay (overlay item -> ISO 27001 controls and clauses)
    titles = {r["iso27001_2022"]: r["iso27001_title"] for r in rows}
    widths = {"ref": 12, "title": 40, "group": 28, "iso27001_2022": 26, "_titles": 50, "iso27001_clauses": 14,
              "confidence": 11, "verification": 12, "priority": 12, "articles": 18, "notes": 60}
    for key, meta in OVERLAYS.items():
        cols = overlay_columns(key)
        ws = wb.create_sheet(f"ov_{key}"[:31])
        ws["A1"].value = f"{meta['name']} {meta['edition']} → ISO/IEC 27001:2022 (informative overlay)"
        ws["A1"].font = font(bold=True, color="FFFFFF", size=12)
        for col in range(1, len(cols) + 1):
            ws.cell(row=1, column=col).fill = fill(MID)
        header(ws, 2, [h for _, h in cols])
        for ci, (c, _) in enumerate(cols):
            ws.column_dimensions[chr(ord("A") + ci)].width = widths[c]
        for ri, item in enumerate(overlays[key], start=3):
            for ci, (c, _) in enumerate(cols, start=1):
                cell = ws.cell(row=ri, column=ci, value=overlay_cell(item, c, titles))
                cell.font = font(bold=(c == "ref"))
                cell.border = BORDER
                cell.alignment = Alignment(vertical="top", wrap_text=True,
                                           horizontal="center" if c in ("ref", "confidence", "verification", "priority", "iso27001_clauses") else "left")
        ws.freeze_panes = "C3"
        ws.auto_filter.ref = f"A2:{chr(ord('A') + len(cols) - 1)}{len(overlays[key]) + 2}"

    out = ROOT / "GRC-Control-Crosswalk.xlsx"
    wb.properties.title = "GRC Control Crosswalk"
    wb.properties.description = ("MIT-licensed control mapping across ISO 27001, NIST CSF 2.0, CIS v8, ISO 42001 and SOC 2, "
                                 "with UAE IAR, DESC ISR, UAE PDPL, PCI DSS, NIST SP 800-53 and ISO 22301 overlays.")
    save_reproducible(wb, out)
    return out


def main():
    rows, overlays = load_all()
    outs = [write_xlsx(rows, overlays), write_yaml(rows, overlays), write_iso_overlay_csv(rows, overlays),
            *write_reverse_csvs(rows), *write_overlay_csvs(rows, overlays)]
    for o in outs:
        print("Wrote", o.relative_to(ROOT))
    print(f"{len(rows)} ISO 27001:2022 controls mapped.")
    for key, items in overlays.items():
        print(f"{OVERLAYS[key]['label']}: {len(items)} overlay items.")


if __name__ == "__main__":
    main()
