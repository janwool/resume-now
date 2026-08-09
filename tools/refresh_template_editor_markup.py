#!/usr/bin/env python3
"""Refresh the editor CSS/JS inside already-exported template HTML files."""

from __future__ import annotations

import re
from pathlib import Path

from build_editable_template_html import EDITOR_STYLE, OUTPUT_ROOT


PATTERN = re.compile(
    r'<meta name="viewport" content="width=794, initial-scale=1">.*?</script>\s*',
    flags=re.DOTALL,
)


def main() -> int:
    changed = 0
    for path in sorted(OUTPUT_ROOT.glob("template-*/index.html")):
        html = path.read_text(encoding="utf-8", errors="replace")
        refreshed, count = PATTERN.subn(EDITOR_STYLE + "\n", html, count=1)
        if count:
            path.write_text(refreshed, encoding="utf-8")
            changed += 1
    print(f"Refreshed {changed} template editors")
    return 0 if changed else 1


if __name__ == "__main__":
    raise SystemExit(main())
