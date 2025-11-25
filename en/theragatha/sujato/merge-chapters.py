import re
from pathlib import Path

# Output filename (in the same sujato folder)
OUT = "chapters_combined.md"

# map common word-numbers to digits as fallback
WORD_TO_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20
}

def get_chapter_number_from_frontmatter(fm: str):
    m = re.search(r'(?m)^chapter:\s*(\d+)\s*$', fm)
    if m:
        return int(m.group(1))
    return None

def get_chapter_number_from_filename(name: str):
    # try digits in filename: chapter-2.md or chapter-02.md
    m = re.search(r'chapter[-_]?(\d+)', name, re.IGNORECASE)
    if m:
        return int(m.group(1))
    # try word form: chapter-two.md
    m2 = re.search(r'chapter[-_]?([a-z]+)', name, re.IGNORECASE)
    if m2:
        word = m2.group(1).lower()
        return WORD_TO_NUM.get(word)
    return None

def strip_frontmatter(text: str):
    # remove YAML front matter between first pair of '---'
    parts = text.split('---', 2)
    if len(parts) >= 3:
        return parts[2].lstrip()
    return text

def convert_verse_titles(body: str):
    out_lines = []
    for line in body.splitlines():
        # match verse title variants like:
        # ## 1.1 Name
        # ## [1.1 Name](../thag1.1/)
        if re.match(r'^\s*##\s*(?:\[?\s*)\d+\.\d+', line):
            # replace only the leading '##' with '###' (preserve spacing after)
            out_lines.append(re.sub(r'^(\s*)##', r'\1###', line, count=1))
        else:
            out_lines.append(line)
    return "\n".join(out_lines).rstrip()

def main():
    base = Path(__file__).parent
    files = sorted(base.glob("chapter-*.md"))
    chapters = []

    for f in files:
        txt = f.read_text(encoding='utf-8')
        # capture front matter area for chapter lookup
        fm = ""
        parts = txt.split('---', 2)
        if len(parts) >= 3:
            fm = parts[1]
            body_raw = parts[2]
        else:
            fm = ""
            body_raw = txt

        chap_num = get_chapter_number_from_frontmatter(fm) or get_chapter_number_from_filename(f.name)
        if chap_num is None:
            print(f"Skipping {f.name}: couldn't determine chapter number")
            continue

        # strip front matter
        body = strip_frontmatter(txt)

        # convert verse title '## 1.1...' -> '### 1.1...' but leave other headings alone
        body = convert_verse_titles(body)

        chapters.append((chap_num, f.name, body))

    if not chapters:
        print("No chapter files found or no valid chapters detected.")
        return

    # sort by numeric chapter
    chapters.sort(key=lambda t: t[0])

    out_lines = []
    for chap_num, fname, body in chapters:
        out_lines.append(f"## Chapter {chap_num}")
        out_lines.append("")  # single blank line
        out_lines.append(body)
        out_lines.append("")  # blank line between chapters

    out_path = base / OUT
    # backup existing output if present
    if out_path.exists():
        out_path.with_suffix(out_path.suffix + ".bak").write_text(out_path.read_text(encoding='utf-8'), encoding='utf-8')

    out_path.write_text("\n".join(out_lines).rstrip() + "\n", encoding='utf-8')
    print(f"Wrote combined file: {out_path}")

if __name__ == "__main__":
    main()