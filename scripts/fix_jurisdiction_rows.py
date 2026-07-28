#!/usr/bin/env python3
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET

DEFAULT_PATH = Path(__file__).resolve().parents[1] / (
    "src/main/resources/uk/gov/hmcts/ccd/test_definitions/excel/BEFTA_MASTER_GROUPACCESS.xlsx"
)

NS = {
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
ET.register_namespace("", NS["s"])
ET.register_namespace("r", NS["r"])

COL_RE = re.compile(r"([A-Z]+)([0-9]+)")


def col_to_idx(col: str) -> int:
    idx = 0
    for c in col:
        idx = idx * 26 + (ord(c) - ord("A") + 1)
    return idx


def idx_to_col(idx: int) -> str:
    col = ""
    while idx:
        idx, rem = divmod(idx - 1, 26)
        col = chr(rem + ord("A")) + col
    return col


def main() -> None:
    path = DEFAULT_PATH
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    with zipfile.ZipFile(path, "r") as zin:
        files = {info.filename: zin.read(info.filename) for info in zin.infolist()}
        wb_xml = ET.fromstring(files["xl/workbook.xml"])
        wb_rels_xml = ET.fromstring(files["xl/_rels/workbook.xml.rels"])

    rid_to_target = {}
    for rel in wb_rels_xml.findall(
        "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
    ):
        rid_to_target[rel.attrib["Id"]] = rel.attrib["Target"].lstrip("/")

    sheet_path = None
    for sheet in wb_xml.findall("s:sheets/s:sheet", NS):
        if sheet.attrib.get("name") == "Jurisdiction":
            rid = sheet.attrib.get("{%s}id" % NS["r"])
            sheet_path = rid_to_target.get(rid)
            break

    if not sheet_path:
        raise SystemExit("Jurisdiction sheet not found")
    if not sheet_path.startswith("xl/"):
        sheet_path = "xl/" + sheet_path

    sheet_xml = ET.fromstring(files[sheet_path])
    sheet_data = sheet_xml.find("s:sheetData", NS)
    if sheet_data is None:
        raise SystemExit("sheetData not found")

    rows_removed = 0
    for row in list(sheet_data.findall("s:row", NS)):
        r = int(row.attrib.get("r", "0"))
        if 5 <= r <= 100:
            sheet_data.remove(row)
            rows_removed += 1

    # recompute dimension
    max_row = 1
    max_col = 1
    for cell in sheet_xml.findall(".//s:c", NS):
        ref = cell.attrib.get("r")
        if not ref:
            continue
        m = COL_RE.match(ref)
        if not m:
            continue
        max_col = max(max_col, col_to_idx(m.group(1)))
        max_row = max(max_row, int(m.group(2)))

    dim = sheet_xml.find("s:dimension", NS)
    if dim is None:
        dim = ET.Element("{%s}dimension" % NS["s"])
        sheet_xml.insert(0, dim)
    dim.attrib["ref"] = f"A1:{idx_to_col(max_col)}{max_row}"

    files[sheet_path] = ET.tostring(sheet_xml, encoding="utf-8", xml_declaration=True)

    # update table refs for Jurisdiction sheet
    rels_path = sheet_path.replace("worksheets/", "worksheets/_rels/") + ".rels"
    if rels_path in files:
        rels_xml = ET.fromstring(files[rels_path])
        table_targets = []
        for rel in rels_xml.findall(
            "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
        ):
            if rel.attrib.get("Type", "").endswith("/table"):
                target = rel.attrib["Target"]
                if target.startswith("/"):
                    table_path = target.lstrip("/")
                else:
                    base = rels_path.rsplit("/", 1)[0]
                    table_path = str(Path(base) / target).replace("\\", "/")
                if not table_path.startswith("xl/"):
                    table_path = "xl/" + table_path
                table_targets.append(table_path)

        remaining_rows = [int(r.attrib["r"]) for r in sheet_data.findall("s:row", NS)]
        last_row = max(remaining_rows) if remaining_rows else 3

        for table_path in table_targets:
            if table_path not in files:
                continue
            table_xml = ET.fromstring(files[table_path])
            ref = table_xml.attrib.get("ref")
            if not ref or ":" not in ref:
                continue
            start, end = ref.split(":")
            start_col = "".join([c for c in start if c.isalpha()])
            end_col = "".join([c for c in end if c.isalpha()])
            start_row = int("".join([c for c in start if c.isdigit()]) or "1")
            new_ref = f"{start_col}{start_row}:{end_col}{last_row}"
            table_xml.attrib["ref"] = new_ref
            af = table_xml.find("s:autoFilter", NS)
            if af is not None:
                af.attrib["ref"] = new_ref
            files[table_path] = ET.tostring(
                table_xml, encoding="utf-8", xml_declaration=True
            )

    with zipfile.ZipFile(path, "w") as zout:
        for name, data in files.items():
            zout.writestr(name, data)

    print(path)
    print(f"rows_removed={rows_removed} dimension={dim.attrib['ref']}")


if __name__ == "__main__":
    main()
