from pathlib import Path
import re
import sys

def convert_file(p: Path):
    txt = p.read_text(encoding="utf-8")
    new = re.sub(r"(?m)^(\s*)##\s", r"\1### ", txt)
    if new != txt:
        bak = p.with_suffix(p.suffix + ".bak")
        bak.write_text(txt, encoding="utf-8")
        p.write_text(new, encoding="utf-8")
        print(f"Updated {p} (backup at {bak})")
    else:
        print(f"No changes in {p}")

def main():
    paths = sys.argv[1:] or ["chapters_combined.md"]
    for pat in paths:
        p = Path(pat)
        if not p.exists():
            print(f"Not found: {p}")
            continue
        convert_file(p)

if __name__ == "__main__":
    main()