import re
from pathlib import Path

BASE = Path(__file__).parent
TARGET = BASE / "_index.md"

if not TARGET.exists():
    print(f"Not found: {TARGET}")
    exit(1)

text = TARGET.read_text(encoding="utf-8")

# Match "## Chapter One", "## Chapter Two", etc.
# Convert to "## [Chapter One](../theragatha/sujato/chapter-one/chapter-one/)"

def replace_chapter(match):
    chapter_word = match.group(1)  # "One", "Two", etc.
    
    # Map word to number if needed
    word_to_num = {
        "One": "one", "Two": "two", "Three": "three", "Four": "four", 
        "Five": "five", "Six": "six", "Seven": "seven", "Eight": "eight",
        "Nine": "nine", "Ten": "ten", "Eleven": "eleven", "Twelve": "twelve",
        "Thirteen": "thirteen", "Fourteen": "fourteen", "Fifteen": "fifteen",
        "Sixteen": "sixteen", "Seventeen": "seventeen", "Eighteen": "eighteen",
        "Nineteen": "nineteen", "Twenty": "twenty", "Twenty-One": "twenty-one"
    }
    
    chapter_lower = word_to_num.get(chapter_word, chapter_word.lower())
    return f"## [Chapter {chapter_word}](../theragatha/sujato/chapter-{chapter_lower}/chapter-{chapter_lower}/)"

# Match "## Chapter [Word]" pattern
new_text = re.sub(
    r'^##\s+Chapter\s+([A-Za-z\-]+)\s*$',
    replace_chapter,
    text,
    flags=re.MULTILINE
)

if new_text == text:
    print("No changes made.")
else:
    bak = TARGET.with_suffix(TARGET.suffix + ".bak")
    bak.write_text(text, encoding="utf-8")
    TARGET.write_text(new_text, encoding="utf-8")
    print(f"Updated {TARGET} (backup at {bak})")