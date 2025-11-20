import os

def gen(verse_number):
        new_front_matter = f"""---
title: "3.{verse_number}"
id: "thag3.{verse_number}"
chapter: 3
verse: verse_number
slug: "thag3.{verse_number}"
edition: "Dhammatalks.org"
collection: "Theragāthā"
pali_source: "Dhammatalks.org"
translator: "Ṭhānissaro Bhikkhu"
weight: {verse_number}
bookHidden: true
---
"""

        new_content = new_front_matter + "\n# 3." + verse_number + "\n\n## Notes"

        # Write the new file (e.g., thag1.4.md)
        output_filename = f"thag3.{verse_number}.md"
        with open(output_filename, "w", encoding="utf-8") as out:
            out.write(new_content)
        print(f"Wrote {output_filename}")

vnum = input("Enter the verse number: ")
gen(vnum)