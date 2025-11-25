from pathlib import Path
import re

BASE = Path(__file__).parent
OUT = BASE / "chapters_combined.md"

# find any file whose name starts with "chapter" (matches chapter-one.md and chapter_one.md in subdirs)
files = sorted(BASE.rglob("chapter*.md"))

if not files:
    print("No chapter files found (searched recursively).")
    raise SystemExit(0)

def chapter_number_from_frontmatter(text):
    m = re.search(r'(?m)^chapter:\s*(\d+)\s*$', text)
    return int(m.group(1)) if m else None

def chapter_number_from_path(p: Path):
    # try filename like chapter-2.md or chapter_two.md or directory name chapter-two
    m = re.search(r'chapter[-_]?(\d+)', p.name, re.IGNORECASE)
    if m:
        return int(m.group(1))
    # try parent directory name
    m2 = re.search(r'chapter[-_]?(\d+)', p.parent.name, re.IGNORECASE)
    if m2:
        return int(m2.group(1))
    return None

items = []
for f in files:
    txt = f.read_text(encoding='utf-8')
    fm_match = txt.split('---', 2)
    front = fm_match[1] if len(fm_match) >= 3 else ""
    num = chapter_number_from_frontmatter(front) or chapter_number_from_path(f)
    items.append((num if num is not None else 9999, f, txt))

# sort by detected chapter number then by path
items.sort(key=lambda t: (t[0], str(t[1])))

# Backup existing output
if OUT.exists():
    OUT.with_suffix(OUT.suffix + ".bak").write_text(OUT.read_text(encoding='utf-8'), encoding='utf-8')

parts = []
for num, f, txt in items:
    # remove YAML front matter between the first pair of ---
    segs = txt.split("---", 2)
    body = segs[2] if len(segs) >= 3 else txt
    parts.append(body.strip())

OUT.write_text("\n\n".join(parts).rstrip() + "\n", encoding='utf-8')
print(f"Wrote combined file: {OUT}")