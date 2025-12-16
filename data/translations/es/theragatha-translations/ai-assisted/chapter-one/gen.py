import os

chapter_number = "1"

def gen(verse_number):
        new_front_matter = f"""---
title: "{chapter_number}.{verse_number}"
id: "thag{chapter_number}.{verse_number}"
chapter: {chapter_number}
verse: {verse_number}
slug: "thag{chapter_number}.{verse_number}"
edition: ""
collection: "Theragāthā"
pali_source: "suttacentral"
translator: "AI Assisted"
weight: {verse_number}
bookHidden: true
---
"""

        new_content = new_front_matter + "\n# " + chapter_number + "." + verse_number + "\n\n\n\n<!-- ## Notes -->"

        # Write the new file (e.g., thag1.4.md)
        output_filename = f"thag{chapter_number}.{verse_number}.md"
        with open(output_filename, "w", encoding="utf-8") as out:
            out.write(new_content)
        print(f"Wrote {output_filename}")

vnum = input("Enter the verse number: ")
gen(vnum)