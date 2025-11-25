import re
from pathlib import Path

BASE = Path(__file__).parent
TARGET = BASE / "_index.md"

if not TARGET.exists():
    print(f"Not found: {TARGET}")
    exit(1)

text = TARGET.read_text(encoding="utf-8")

# First, let's see what we're actually matching
test = re.findall(r'###\s+\[[\d.]+\s+[^\]]+\]\([^)]+\)', text)
if test:
    print(f"Found {len(test)} verse title lines:")
    for t in test[:3]:
        print(f"  {t}")
else:
    print("No ### [N.N ...](link) lines found. Check the file format.")
    exit(1)

def replace_link(match):
    full = match.group(0)  # entire match
    # extract number and title from ### [1.1 Title]
    m = re.search(r'\[(\d+\.\d+)\s+([^\]]+)\]', full)
    if not m:
        return full
    
    num = m.group(1)
    title = m.group(2)
    
    chapter_num = num.split('.')[0]
    word_map = {
        "1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
        "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten",
        "11": "eleven", "12": "twelve", "13": "thirteen", "14": "fourteen",
        "15": "fifteen", "16": "sixteen", "17": "seventeen", "18": "eighteen",
        "19": "nineteen", "20": "twenty", "21": "twenty-one"
    }
    
    chapter_word = word_map.get(chapter_num, "unknown")
    return f'### [{num} {title}](../theragatha/sujato/chapter-{chapter_word}/thag{num}/)'

# Match ### [N.N Title](any link)
new_text = re.sub(
    r'###\s+\[[\d.]+\s+[^\]]+\]\([^)]+\)',
    replace_link,
    text
)

if new_text == text:
    print("No changes made.")
else:
    bak = TARGET.with_suffix(TARGET.suffix + ".bak")
    bak.write_text(text, encoding="utf-8")
    TARGET.write_text(new_text, encoding="utf-8")
    print(f"Updated {TARGET} (backup at {bak})")