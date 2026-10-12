#!/usr/bin/env python3
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

PREFIX_BY_URI = {
    "http://schemas.openxmlformats.org/markup-compatibility/2006": "mc",
    "http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac": "x14ac",
    "http://schemas.microsoft.com/office/spreadsheetml/2014/revision": "xr",
    "http://schemas.microsoft.com/office/spreadsheetml/2015/revision2": "xr2",
    "http://schemas.microsoft.com/office/spreadsheetml/2016/revision3": "xr3",
}

DECL_BY_PREFIX = {prefix: uri for uri, prefix in PREFIX_BY_URI.items()}
XMLNS_RE = re.compile(r'\s+xmlns:([A-Za-z_][\w.-]*)="([^"]+)"')
IGNORABLE_RE = re.compile(r'\bmc:Ignorable="([^"]+)"')
WORKSHEET_ROOT_RE = re.compile(r'(<(?:[A-Za-z_][\w.-]*:)?worksheet\b[^>]*)(>)')


def replace_prefix(text: str, old: str, new: str, uri: str) -> str:
    desired_decl = f' xmlns:{new}="{uri}"'
    old_decl_re = re.compile(rf'\s+xmlns:{re.escape(old)}="{re.escape(uri)}"')

    if f'xmlns:{new}="{uri}"' in text:
        text = old_decl_re.sub("", text)
    else:
        text = old_decl_re.sub(desired_decl, text, count=1)

    return re.sub(rf'(?<=[<\s/]){re.escape(old)}:', f"{new}:", text)


def ensure_root_decl(text: str, prefix: str) -> str:
    uri = DECL_BY_PREFIX.get(prefix)
    if not uri or f'xmlns:{prefix}="' in text:
        return text

    match = WORKSHEET_ROOT_RE.search(text)
    if not match:
        raise ValueError("Worksheet root element not found")
    return text[:match.end(1)] + f' xmlns:{prefix}="{uri}"' + text[match.end(1):]


def normalise_worksheet(text: str) -> str:
    original = text
    for prefix, uri in XMLNS_RE.findall(text):
        wanted = PREFIX_BY_URI.get(uri)
        if wanted and prefix != wanted:
            text = replace_prefix(text, prefix, wanted, uri)

    match = IGNORABLE_RE.search(text)
    if match:
        text = ensure_root_decl(text, "mc")
        for prefix in match.group(1).split():
            text = ensure_root_decl(text, prefix)

    if text != original:
        ET.fromstring(text)
    return text


def normalise_xlsx(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() != ".xlsx":
        raise ValueError(f"Not an .xlsx file: {path}")

    changed: list[str] = []
    with ZipFile(path, "r") as zin:
        entries = [(info, zin.read(info.filename)) for info in zin.infolist()]

    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".xlsx", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        with ZipFile(tmp_path, "w", ZIP_DEFLATED) as zout:
            for info, data in entries:
                if info.filename.startswith("xl/worksheets/sheet") and info.filename.endswith(".xml"):
                    text = data.decode("utf-8")
                    normalised = normalise_worksheet(text)
                    if normalised != text:
                        changed.append(info.filename)
                        data = normalised.encode("utf-8")
                zout.writestr(info, data)

        if changed:
            tmp_path.replace(path)
        else:
            tmp_path.unlink()
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

    return changed


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: normalise_xlsx_namespaces.py <workbook.xlsx> [workbook.xlsx ...]", file=sys.stderr)
        return 2

    for arg in sys.argv[1:]:
        path = Path(arg)
        changed = normalise_xlsx(path)
        status = "updated" if changed else "unchanged"
        print(f"{status}: {path}")
        for name in changed:
            print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
