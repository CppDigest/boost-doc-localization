#!/usr/bin/env python3
"""
Sum/count extensions from a libraries list file (5th column).
Outputs: (1) all extensions, (2) documentation extensions only.

Expects CSV-like lines with fields separated by \", \"; the last field
(extensions) is pipe-separated (e.g. \".adoc|.html|.qbk\").
"""
import sys
from collections import Counter

# Documentation content formats only (case-insensitive match)
DOC_EXTENSIONS = {
    ".adoc", ".asciidoc", ".dox", ".ent", ".htm", ".html", ".md", ".qbk",
    ".reno", ".rst", ".tex", ".txt", ".xml", ".xsl",
}

DEFAULT_INPUT_PATH = "boost-1.90.0_libraries_list.txt"
OUTPUT_ALL = "boost-1.90.0_all_extensions_summary.txt"
OUTPUT_DOC = "boost-1.90.0_doc_extensions_summary.txt"


def norm_ext(ext: str) -> str:
    """Normalize extension to lowercase with leading dot."""
    e = ext.strip().strip('"')
    return e.lower() if e.startswith(".") else "." + e.lower()


def write_summary(path: str, title: str, counts: dict[str, int]) -> None:
    """Write extension summary to path. Raises OSError on write failure."""
    lines = [
        title,
        "Extension -> # libraries that have at least one file with that extension:",
        "",
    ]
    for ext, n in sorted(counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {ext}: {n}")
    lines.extend([
        "",
        f"Total unique extensions: {len(counts)}",
        f"Total (library, extension) pairs: {sum(counts.values())}",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    input_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT_PATH

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            lines_content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: Could not read {input_path}: {e}", file=sys.stderr)
        sys.exit(1)

    exts = []
    for line in lines_content.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split('", "')
        if len(parts) < 5:
            continue
        last = parts[-1].rstrip('"').strip()
        if not last:
            continue
        for e in last.split("|"):
            e = e.strip().strip('"')
            if e:
                exts.append(e)

    counts_raw = Counter(exts)
    counts_all: dict[str, int] = {}
    for ext, n in counts_raw.items():
        key = norm_ext(ext)
        counts_all[key] = counts_all.get(key, 0) + n

    counts_doc = {ext: n for ext, n in counts_all.items() if ext in DOC_EXTENSIONS}

    title_all = f"All extensions (from {input_path})"
    title_doc = f"Documentation extensions only (from {input_path})"

    try:
        write_summary(OUTPUT_ALL, title_all, counts_all)
        write_summary(OUTPUT_DOC, title_doc, counts_doc)
    except OSError as e:
        print(f"Error: Could not write output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Wrote {OUTPUT_ALL}")
    print(f"Wrote {OUTPUT_DOC}")


if __name__ == "__main__":
    main()
