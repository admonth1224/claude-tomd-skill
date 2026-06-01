#!/usr/bin/env python3
"""
tomd universal extractor
=========================
Convert an office/document file into a clean Markdown *body* (no frontmatter).

Usage:
    python convert.py "<input path>" [--out "<output .md path>"]

Behavior:
    - Detects the format from the file extension.
    - Extracts the content as Markdown and writes it to --out
      (default: "<input_stem>.tomd.tmp.md" beside the input file).
    - Prints a JSON summary to STDOUT so the caller (Claude) can read
      title guess / counts / warnings without parsing the body.

Engines:
    .docx .xlsx .pptx .pdf .csv .html .htm .png .jpg .jpeg  -> markitdown
    .hwp                                                     -> pyhwp (hwp5txt)
    .hwpx                                                    -> zip + xml (built-in)
    .md .txt                                                 -> passthrough

The body is plain UTF-8 Markdown. Frontmatter is added by the skill afterwards.
"""
import sys
import os
import io
import json
import re
import subprocess
import zipfile
from xml.etree import ElementTree as ET

MARKITDOWN_EXT = {
    ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls",
    ".pdf", ".csv", ".html", ".htm", ".png", ".jpg", ".jpeg",
    ".json", ".xml", ".epub",
}


def log_warn(warnings, msg):
    warnings.append(msg)


def convert_markitdown(path, warnings):
    from markitdown import MarkItDown
    md = MarkItDown()
    result = md.convert(path)
    return result.text_content or ""


def convert_hwp(path, warnings):
    """Legacy HWP 5.0 (OLE binary) via pyhwp's hwp5txt, using the same interpreter."""
    # Try `python -m hwp5.hwp5txt` first (interpreter-agnostic), then the console script.
    attempts = [
        [sys.executable, "-m", "hwp5.hwp5txt", path],
    ]
    last_err = ""
    for cmd in attempts:
        try:
            proc = subprocess.run(cmd, capture_output=True)
            if proc.returncode == 0 and proc.stdout:
                text = proc.stdout.decode("utf-8", errors="replace")
                return text
            last_err = proc.stderr.decode("utf-8", errors="replace")[:400]
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
    # Fallback: locate hwp5txt.exe in the user scripts dir
    import site
    candidates = []
    try:
        base = site.getuserbase()
        candidates.append(os.path.join(base, "Python313", "Scripts", "hwp5txt.exe"))
        candidates.append(os.path.join(base, "Scripts", "hwp5txt.exe"))
    except Exception:  # noqa: BLE001
        pass
    for exe in candidates:
        if os.path.exists(exe):
            try:
                proc = subprocess.run([exe, path], capture_output=True)
                if proc.returncode == 0 and proc.stdout:
                    return proc.stdout.decode("utf-8", errors="replace")
                last_err = proc.stderr.decode("utf-8", errors="replace")[:400]
            except Exception as e:  # noqa: BLE001
                last_err = str(e)
    raise RuntimeError(
        "HWP 변환 실패. pyhwp(hwp5txt)가 필요합니다. 설치: pip install pyhwp\n"
        f"세부 오류: {last_err}"
    )


def convert_hwpx(path, warnings):
    """HWPX (OWPML) = zip of XML. Extract paragraph text from Contents/section*.xml."""
    paras = []
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist()
                 if re.search(r"Contents/section\d+\.xml$", n)]
        if not names:
            # some variants store sections directly
            names = [n for n in z.namelist() if n.endswith(".xml") and "ection" in n]
        names.sort()
        for name in names:
            data = z.read(name)
            try:
                root = ET.fromstring(data)
            except ET.ParseError as e:
                log_warn(warnings, f"{name} 파싱 오류: {e}")
                continue
            # OWPML paragraph = local-name 'p'; runs of text = local-name 't'
            for p in root.iter():
                if p.tag.split("}")[-1] != "p":
                    continue
                buf = []
                for t in p.iter():
                    if t.tag.split("}")[-1] == "t" and t.text:
                        buf.append(t.text)
                line = "".join(buf).strip()
                if line:
                    paras.append(line)
    if not paras:
        log_warn(warnings, "HWPX에서 추출된 텍스트가 없습니다 (이미지/표 위주 문서일 수 있음).")
    return "\n\n".join(paras)


def passthrough(path, warnings):
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def guess_title(body, fallback):
    for line in body.splitlines():
        s = line.strip().lstrip("#").strip()
        # skip markdown table rows / separators and empty bold markers
        if not s or set(s) <= set("|-: "):
            continue
        s = s.strip("*").strip()
        if s and set(s) <= set("|-: "):
            continue
        if s:
            return s[:120]
    return fallback


def main():
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"ok": False, "error": "input path required"}, ensure_ascii=False))
        return 2
    inp = args[0]
    out = None
    if "--out" in args:
        out = args[args.index("--out") + 1]
    if not os.path.exists(inp):
        print(json.dumps({"ok": False, "error": f"file not found: {inp}"}, ensure_ascii=False))
        return 2

    ext = os.path.splitext(inp)[1].lower()
    stem = os.path.splitext(os.path.basename(inp))[0]
    if out is None:
        out = os.path.join(os.path.dirname(os.path.abspath(inp)), stem + ".tomd.tmp.md")

    warnings = []
    try:
        if ext in MARKITDOWN_EXT:
            body = convert_markitdown(inp, warnings)
            fmt = "markitdown:" + ext.lstrip(".")
        elif ext == ".hwp":
            body = convert_hwp(inp, warnings)
            fmt = "hwp"
        elif ext == ".hwpx":
            body = convert_hwpx(inp, warnings)
            fmt = "hwpx"
        elif ext in (".md", ".txt", ".markdown"):
            body = passthrough(inp, warnings)
            fmt = "passthrough"
        else:
            print(json.dumps({"ok": False,
                              "error": f"지원하지 않는 확장자: {ext}",
                              "supported": sorted(MARKITDOWN_EXT) + [".hwp", ".hwpx", ".md", ".txt"]},
                             ensure_ascii=False))
            return 2
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e), "source_format": ext},
                         ensure_ascii=False))
        return 1

    body = (body or "").strip() + "\n"
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)

    summary = {
        "ok": True,
        "source_format": fmt,
        "out_path": out,
        "char_count": len(body),
        "table_count": body.count("\n|"),
        "title_guess": guess_title(body, stem),
        "warnings": warnings,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
