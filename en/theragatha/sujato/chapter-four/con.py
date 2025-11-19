import re
from pathlib import Path

chapter_number = "4"
chapter_number_word = "Four"

def extract_verse_data(file_path):
    """Extract verse number, title, body from a thag file."""
    content = file_path.read_text(encoding='utf-8')
    
    # Split front matter from body
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None
    
    front_matter = parts[1].strip()
    body = parts[2].strip()
    
    # Extract verse number from filename (e.g., thag2.1 -> 2.1)
    match = re.search(r'thag(\d+\.\d+)', file_path.stem)
    if not match:
        return None
    
    verse_num = match.group(1)
    
    # Extract title line (## N.N Name) — note the double ##
    title_match = re.search(r'^#\s+(\d+\.\d+)\s+(.+)$', body, re.MULTILINE)
    if not title_match:
        return None
    
    title = title_match.group(2).strip()
    
    # Extract verse content: from ## line to ## Notes or end of file
    verse_start = body.find(f'# {verse_num}')
    notes_start = body.find('## Notes')
    
    if verse_start == -1:
        return None
    
    if notes_start > verse_start:
        verse_content = body[verse_start:notes_start].strip()
    else:
        verse_content = body[verse_start:].strip()
    
    # Remove the title line from verse content (keep only the poem)
    verse_lines = verse_content.split('\n')
    poem_lines = verse_lines[1:]  # skip the title
    poem = '\n'.join(poem_lines).strip()
    
    return {
        'num': verse_num,
        'title': title,
        'poem': poem,
        'front_matter': front_matter
    }

def create_consolidated_file(chapter_dir, output_filename='chapter-' + chapter_number_word.lower() + '-consolidated.md'):
    """Read all thag*.md files, sort by verse number, create consolidated file."""
    verses = []
    
    # Collect all verses
    for md_file in sorted(chapter_dir.glob('thag' + chapter_number + '*.md')):
        data = extract_verse_data(md_file)
        if data:
            verses.append(data)
            print(f"Extracted {md_file.name}: {data['num']} {data['title']}")
        else:
            print(f"Failed to extract from {md_file.name}")
    
    if not verses:
        print("No verses found")
        return
    
    # Sort by verse number (2.1, 2.2, etc.)
    verses.sort(key=lambda v: tuple(map(int, v['num'].split('.'))))
    
    # Build output
    output_lines = []
    
    # Build output
    output_lines = ["---"]
    
    # Use front matter from first verse as template
    first_fm = verses[0]['front_matter']
    fm_lines = first_fm.split('\n')
    for line in fm_lines:
        if line.startswith('title:'):
            output_lines.append(f'title: "Chapter {chapter_number_word}"')
        elif line.startswith('id:'):
            output_lines.append(f'id: "chapter-{chapter_number_word.lower()}"')
        elif line.startswith('slug:'):
            output_lines.append(f'slug: "chapter-{chapter_number_word.lower()}"')
        elif line.startswith('weight:'):
            output_lines.append(f'weight: {chapter_number}')
        elif line.startswith('verse:'):
            continue  # skip verse-specific field
        elif line.startswith('bookHidden:'):
            output_lines.append('bookHidden: false')
        else:
            output_lines.append(line)
    
    output_lines.append('---')
    output_lines.append('')
    output_lines.append(f'# Chapter {chapter_number_word}')
    
    # Add each verse with its content
    for verse in verses:
        output_lines.append('')
        output_lines.append(f"## [{verse['num']} {verse['title']}](../thag{verse['num']}/)")
        output_lines.append('')
        output_lines.append(verse['poem'])
    
    output_lines.append('')
    output_lines.append('## Notes')
    
    # Write consolidated file
    output_path = chapter_dir / output_filename
    output_path.write_text('\n'.join(output_lines) + '\n', encoding='utf-8')
    print(f"\nWrote consolidated file: {output_path}")

def main():
    chapter_dir = Path(__file__).parent
    create_consolidated_file(chapter_dir)

if __name__ == '__main__':
    main()