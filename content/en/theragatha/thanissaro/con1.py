# ...existing code...
import re
from pathlib import Path

chapter_number = "4"
chapter_number_word = "Four"

def extract_verse_data(file_path: Path):
    """Extract verse number, title, poem body and front matter from a thag file.
    Accepts headings starting with # or ## and title lines that are plain or link-wrapped.
    Returns None on failure (caller will skip)."""
    txt = file_path.read_text(encoding='utf-8')
    parts = txt.split('---', 2)
    front_matter = parts[1].strip() if len(parts) >= 3 else ""
    body = parts[2].lstrip() if len(parts) >= 3 else txt

    # try to get verse number from filename first
    mfn = re.search(r'thag(\d+\.\d+)', file_path.stem)
    if not mfn:
        return None
    verse_num = mfn.group(1)

    # find a title line that starts with 1 or 2 hashes: "# 1.1 Title" or "## 1.1 Title"
    # also accept "## [1.1 Title](...)" forms
    title_re = re.compile(r'(?m)^\s*#{1,2}\s*(?:\[?\s*)?(\d+\.\d+)\s+([^\]\n(]+)')
    tm = title_re.search(body)
    if not tm:
        # fallback: search for the explicit heading "## <verse_num>"
        tm = re.search(r'(?m)^\s*#{1,2}\s*' + re.escape(verse_num) + r'\b\s*(.*)', body)
        if not tm:
            return None
        title = tm.group(1).strip()
    else:
        title = tm.group(2).strip()

    # Determine start of verse block (position of the matched heading)
    heading_pos = tm.start()
    # Find end: look for a Notes heading (## Notes / ### Notes) after heading_pos
    notes_re = re.compile(r'(?m)^\s*#{2,3}\s*Notes\b')
    notes_m = notes_re.search(body, heading_pos)
    verse_block = body[heading_pos:notes_m.start()].strip() if notes_m else body[heading_pos:].strip()

    # Remove the title line from the verse block, keep poem only
    lines = verse_block.splitlines()
    poem_lines = lines[1:] if len(lines) > 1 else []
    poem = "\n".join(poem_lines).strip()

    # remove footnote markers like [^1] and any inline footnote definitions
    poem = re.sub(r'\[\^[^\]]+\]', '', poem)
    poem = re.sub(r'(?m)^\s*\[\^[^\]]+\]:.*\n?', '', poem)
    # collapse multiple spaces and trim line ends
    poem = re.sub(r' {2,}', ' ', poem)
    poem = '\n'.join(line.rstrip() for line in poem.splitlines()).strip()

    return {
        "num": verse_num,
        "title": title,
        "poem": poem,
        "front_matter": front_matter
    }

def create_consolidated_file(chapter_number, chapter_number_word):
    """Run inside the chapter folder (or will adapt if placed elsewhere)."""
    # if script is placed in the chapter folder, use current dir; otherwise try parent / chapter-...
    here = Path(__file__).parent
    if re.match(r'chapter[-_]?', here.name, re.IGNORECASE):
        chapter_dir = here
    else:
        chapter_dir = here / f'chapter-{chapter_number_word.lower()}'

    if not chapter_dir.exists():
        print(f"Chapter directory not found: {chapter_dir}")
        return

    pattern = f"thag{chapter_number}*.md"
    files = sorted(chapter_dir.glob(pattern))
    if not files:
        print(f"No verse files found for pattern {pattern} in {chapter_dir}")
        return

    verses = []
    for md in files:
        data = extract_verse_data(md)
        if data:
            verses.append(data)
            print(f"Included {md.name}: {data['num']} {data['title']}")
        else:
            print(f"Skipped {md.name}: could not parse title/verse")

    if not verses:
        print("No verses parsed successfully.")
        return

    # sort by numeric verse (e.g., 1.1, 1.2, 1.10)
    def sort_key(v):
        return tuple(int(x) for x in v['num'].split('.'))
    verses.sort(key=sort_key)

    # Build front matter for consolidated file using first file fm as template
    output_lines = ["---"]
    first_fm = verses[0].get("front_matter", "")
    for line in first_fm.splitlines():
        if line.startswith("title:"):
            output_lines.append(f'title: "Chapter {chapter_number_word}"')
        elif line.startswith("id:"):
            output_lines.append(f'id: "chapter-{chapter_number_word.lower()}"')
        elif line.startswith("slug:"):
            output_lines.append(f'slug: "chapter-{chapter_number_word.lower()}"')
        elif line.startswith("weight:"):
            output_lines.append(f'weight: {chapter_number}')
        elif line.startswith("verse:"):
            continue
        elif line.startswith("bookHidden:"):
            output_lines.append("bookHidden: false")
        elif line.startswith("pali_source:"):
            output_lines.append('pali_source: ""')
        else:
            output_lines.append(line)
    # ensure required fields if missing
    if not any(l.startswith("slug:") for l in output_lines):
        output_lines.append(f'slug: "chapter-{chapter_number}"')
    if not any(l.startswith("weight:") for l in output_lines):
        output_lines.append(f'weight: {chapter_number}')
    if not any(l.startswith("bookHidden:") for l in output_lines):
        output_lines.append("bookHidden: false")

    output_lines.append("---")
    output_lines.append("")
    output_lines.append(f"# Chapter {chapter_number_word}")
    output_lines.append("")

    for v in verses:
        output_lines.append(f"## [{v['num']} {v['title']}](../thag{v['num']}/)")
        output_lines.append("")
        output_lines.append(v['poem'])
        output_lines.append("")

    output_lines.append("## Notes")
    output_path = chapter_dir / f"chapter-{chapter_number_word.lower()}.md"
    output_path.write_text("\n".join(output_lines).rstrip() + "\n", encoding='utf-8')
    print(f"Wrote consolidated file: {output_path}")

if __name__ == "__main__":
    create_consolidated_file(chapter_number, chapter_number_word)
# ...existing code...
```# filepath: /Users/trashboy/Documents/theragatha/content/en/theragatha/thanissaro/con1.py
# ...existing code...
import re
from pathlib import Path

chapter_number = "4"
chapter_number_word = "Four"

def extract_verse_data(file_path: Path):
    """Extract verse number, title, poem body and front matter from a thag file.
    Accepts headings starting with # or ## and title lines that are plain or link-wrapped.
    Returns None on failure (caller will skip)."""
    txt = file_path.read_text(encoding='utf-8')
    parts = txt.split('---', 2)
    front_matter = parts[1].strip() if len(parts) >= 3 else ""
    body = parts[2].lstrip() if len(parts) >= 3 else txt

    # try to get verse number from filename first
    mfn = re.search(r'thag(\d+\.\d+)', file_path.stem)
    if not mfn:
        return None
    verse_num = mfn.group(1)

    # find a title line that starts with 1 or 2 hashes: "# 1.1 Title" or "## 1.1 Title"
    # also accept "## [1.1 Title](...)" forms
    title_re = re.compile(r'(?m)^\s*#{1,2}\s*(?:\[?\s*)?(\d+\.\d+)\s+([^\]\n(]+)')
    tm = title_re.search(body)
    if not tm:
        # fallback: search for the explicit heading "## <verse_num>"
        tm = re.search(r'(?m)^\s*#{1,2}\s*' + re.escape(verse_num) + r'\b\s*(.*)', body)
        if not tm:
            return None
        title = tm.group(1).strip()
    else:
        title = tm.group(2).strip()

    # Determine start of verse block (position of the matched heading)
    heading_pos = tm.start()
    # Find end: look for a Notes heading (## Notes / ### Notes) after heading_pos
    notes_re = re.compile(r'(?m)^\s*#{2,3}\s*Notes\b')
    notes_m = notes_re.search(body, heading_pos)
    verse_block = body[heading_pos:notes_m.start()].strip() if notes_m else body[heading_pos:].strip()

    # Remove the title line from the verse block, keep poem only
    lines = verse_block.splitlines()
    poem_lines = lines[1:] if len(lines) > 1 else []
    poem = "\n".join(poem_lines).strip()

    # remove footnote markers like [^1] and any inline footnote definitions
    poem = re.sub(r'\[\^[^\]]+\]', '', poem)
    poem = re.sub(r'(?m)^\s*\[\^[^\]]+\]:.*\n?', '', poem)
    # collapse multiple spaces and trim line ends
    poem = re.sub(r' {2,}', ' ', poem)
    poem = '\n'.join(line.rstrip() for line in poem.splitlines()).strip()

    return {
        "num": verse_num,
        "title": title,
        "poem": poem,
        "front_matter": front_matter
    }

def create_consolidated_file(chapter_number, chapter_number_word):
    """Run inside the chapter folder (or will adapt if placed elsewhere)."""
    # if script is placed in the chapter folder, use current dir; otherwise try parent / chapter-...
    here = Path(__file__).parent
    if re.match(r'chapter[-_]?', here.name, re.IGNORECASE):
        chapter_dir = here
    else:
        chapter_dir = here / f'chapter-{chapter_number_word.lower()}'

    if not chapter_dir.exists():
        print(f"Chapter directory not found: {chapter_dir}")
        return

    pattern = f"thag{chapter_number}*.md"
    files = sorted(chapter_dir.glob(pattern))
    if not files:
        print(f"No verse files found for pattern {pattern} in {chapter_dir}")
        return

    verses = []
    for md in files:
        data = extract_verse_data(md)
        if data:
            verses.append(data)
            print(f"Included {md.name}: {data['num']} {data['title']}")
        else:
            print(f"Skipped {md.name}: could not parse title/verse")

    if not verses:
        print("No verses parsed successfully.")
        return

    # sort by numeric verse (e.g., 1.1, 1.2, 1.10)
    def sort_key(v):
        return tuple(int(x) for x in v['num'].split('.'))
    verses.sort(key=sort_key)

    # Build front matter for consolidated file using first file fm as template
    output_lines = ["---"]
    first_fm = verses[0].get("front_matter", "")
    for line in first_fm.splitlines():
        if line.startswith("title:"):
            output_lines.append(f'title: "Chapter {chapter_number_word}"')
        elif line.startswith("id:"):
            output_lines.append(f'id: "chapter-{chapter_number_word.lower()}"')
        elif line.startswith("slug:"):
            output_lines.append(f'slug: "chapter-{chapter_number_word.lower()}"')
        elif line.startswith("weight:"):
            output_lines.append(f'weight: {chapter_number}')
        elif line.startswith("verse:"):
            continue
        elif line.startswith("bookHidden:"):
            output_lines.append("bookHidden: false")
        elif line.startswith("pali_source:"):
            output_lines.append('pali_source: ""')
        else:
            output_lines.append(line)
    # ensure required fields if missing
    if not any(l.startswith("slug:") for l in output_lines):
        output_lines.append(f'slug: "chapter-{chapter_number}"')
    if not any(l.startswith("weight:") for l in output_lines):
        output_lines.append(f'weight: {chapter_number}')
    if not any(l.startswith("bookHidden:") for l in output_lines):
        output_lines.append("bookHidden: false")

    output_lines.append("---")
    output_lines.append("")
    output_lines.append(f"# Chapter {chapter_number_word}")
    output_lines.append("")

    for v in verses:
        output_lines.append(f"## [{v['num']} {v['title']}](../thag{v['num']}/)")
        output_lines.append("")
        output_lines.append(v['poem'])
        output_lines.append("")

    output_lines.append("## Notes")
    output_path = chapter_dir / f"chapter-{chapter_number_word.lower()}.md"
    output_path.write_text("\n".join(output_lines).rstrip() + "\n", encoding='utf-8')
    print(f"Wrote consolidated file: {output_path}")

if __name__ == "__main__":
    create_consolidated_file(chapter_number, chapter_number_word)
# ...existing code...