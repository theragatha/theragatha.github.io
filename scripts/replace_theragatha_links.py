#!/usr/bin/env python3
"""Replace '../' prefixes before 'theragatha/' in a file and write output.

Usage:
  python scripts/replace_theragatha_links.py [SOURCE] [DEST] [--inplace]

Defaults:
  SOURCE: content/en/theragatha/_index.md
  DEST:   content/en/_index.md.new

Options:
  --inplace   Overwrite DEST (create backup as DEST.bak.TIMESTAMP if DEST exists)
"""

import argparse
import re
from pathlib import Path
from datetime import datetime

def replace_text(text: str) -> (str, int):
    pattern = re.compile(r'(?:\.\./)+(?=theragatha/)')
    new_text, n = pattern.subn('', text)
    return new_text, n


def backup_path(p: Path) -> Path:
    ts = datetime.now().strftime('%Y%m%dT%H%M%S')
    return p.with_name(p.name + f'.bak.{ts}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('source', nargs='?', default='content/en/theragatha/_index.md')
    p.add_argument('dest', nargs='?', default='content/en/_index.md.new')
    p.add_argument('--inplace', action='store_true', help='Overwrite dest (with backup)')
    args = p.parse_args()

    src = Path(args.source)
    dst = Path(args.dest)

    if not src.exists():
        print(f"Source file not found: {src}")
        raise SystemExit(2)

    text = src.read_text(encoding='utf-8')
    new_text, count = replace_text(text)

    if args.inplace and dst.exists():
        b = backup_path(dst)
        dst.rename(b)
        print(f"Existing dest backed up to: {b}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(new_text, encoding='utf-8')

    print(f"Wrote {dst} ({count} replacements)")

if __name__ == '__main__':
    main()
