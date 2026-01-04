import re
import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString

def gen(chapter_number, verse_number, URL):
        new_front_matter = f"""---
title: "{chapter_number}.{verse_number}"
id: "thag{chapter_number}.{verse_number}"
chapter: {chapter_number}
verse: {verse_number}
slug: "thag{chapter_number}.{verse_number}"
edition: "Pāli Text Society"
collection: "Theragāthā"
pali_source: "Pāli Text Society"
translator: "Mrs. C.A.F. Rhys Davids"
weight: {verse_number}
bookHidden: true
---
"""
        
        #new_content = new_front_matter + "\n# " + chapter_number + "." + verse_number + "\n\n## Commentary\n\n## Verse\n\n## Attribution\n\n## Notes"
        new_content = new_front_matter + "\n" + extract(chapter_number, verse_number, URL)

        # Write the new file (e.g., thag1.4.md)
        output_filename = f"thag{chapter_number}.{verse_number}-commentary.md"
        with open(output_filename, "w", encoding="utf-8") as out:
            out.write(new_content)
        print(f"Wrote {output_filename}")

def rewrite_inline_footnotes(soup):
    """
    Convert <span class="f1">[1]</span> → ^1
    """
    for span in soup.select("span.f1"):
        text = span.get_text(strip=True)
        # Expecting format like "[1]"
        if text.startswith("[") and text.endswith("]"):
            number = text[1:-1]
            span.replace_with(f"[^{number}]")
    return soup


def extract_commentary(start):
    parts = []

    for sib in start.next_siblings:
        if isinstance(sib, NavigableString):
            continue

        classes = sib.get("class", [])

        # Stop at the verse section
        if "f4" in classes and "in2" in classes:
            break

        text = sib.get_text(" ", strip=True)
        if text:
            parts.append(text)

    return "\n\n".join(parts)

from bs4 import Tag

def collect_attribution_from_last_verse(last_verse_p):
    """
    Collect attribution paragraphs between:
    <p class="f4 in2">...</p>
    and
    <p>&nbsp;</p>
    """
    parts = []

    for sib in last_verse_p.next_siblings:
        if not isinstance(sib, Tag):
            continue

        # Stop at spacer paragraph
        if sib.name == "p" and sib.get_text(strip=True) == "":
            break

        # Collect only plain <p> with no class
        if sib.name == "p" and not sib.get("class"):
            text = sib.get_text(" ", strip=True)
            if text:
                parts.append(text)
            continue

        # Anything else → stop
        break

    return "\n\n".join(parts)


def extract(chapter_number, verse_number,URL):
    response = requests.get(URL)
    response.raise_for_status()  # fail fast if the request breaks

    # Rewrite inline footnotes
    soup = rewrite_inline_footnotes(BeautifulSoup(response.text, "html.parser"))
    # soup = BeautifulSoup(response.text, "html.parser")

    # Extract monk name
    monk_name = soup.find('h1').get_text(strip=True)[1:]  # Adjust tag if necessary
    #print("Monk Name:", monk_name)

    test = soup.find('h1')
    # Get all the text, split at <br>
    parts = test.decode_contents().split("<br/>")
    print(parts[1].get_text(strip=True  ))

    # Everything after <br> is the monk's name
    monk_t = parts[1].strip() if len(parts) > 1 else ""


    # Extract commentary
    start = soup.find("p", class_="f2 ctr")
    assert start is not None, "Could not find commentary start"
    commentary = extract_commentary(start)

    # Extract verses
    verses_raw = soup.find_all(class_="f4 in2")

    # Replace <br> with line breaks and collect verses
    verses = []
    for verse in verses_raw:
        for br in verse.find_all("br"):
            br.replace_with(NavigableString("\\"))

        verse_text = verse.get_text(strip=False)  # strip leading/trailing spaces
        cleaned_lines = []
        for line in verse_text.splitlines():
            cleaned_lines.append(line.lstrip())  # remove leading whitespace only
        verse_text = "\n".join(cleaned_lines)
        verses.append(verse_text)

    current_verse = []
    last_verse_p = None

    for p in verses_raw:
        current_verse.append(p.get_text(strip=True))
        last_verse_p = p
        
    attribution = collect_attribution_from_last_verse(last_verse_p)
    #print("Attribution:", attribution)

    # Extract notes
    notes = soup.find_all(class_="lgqt")

    # Reformat notes
    reformatting_notes = []
    for note in notes:
        text = note.get_text(strip=True)
        if text.startswith("["):
            text = "[" + text[1:3] + ": " + text[3:].strip()  # Ensure proper formatting
        note.replace_with(text)
        reformatting_notes.append(text)

    # return monk_name, commentary, verse, reformatting_notes

    # Write to file
    extracted_text = ""
    with open("scraped_content.md", "w", encoding="utf-8") as f:
       
        # Monk Name
        f.write(f"# {monk_name}\n\n")
        extracted_text += f"# {monk_name}\n\n"

        # Commentary
        f.write("## Commentary\n\n")
        f.write(commentary + "\n\n")
        extracted_text += "## Commentary\n\n" + commentary + "\n\n"

        # Verses
        f.write("## Verses\n\n")
        for element in verses:
            f.write(element + "\n\n")
        extracted_text += "## Verses\n\n" + "\n\n".join(verses) + "\n\n"

        # Attribution
        f.write("## Attribution\n\n")
        attribution_lines = attribution.split("\n\n")
        for i in range(len(attribution_lines)-1):
            f.write(attribution_lines[i] + "\\\n")
        f.write(attribution_lines[-1] + "\n\n")
        f.write("\n\n")
        extracted_text += "## Attribution\n\n" + attribution + "\n\n"

        # Notes
        f.write("## Notes\n\n")
        for element in reformatting_notes:
            f.write(element + "\n\n")
        extracted_text += "## Notes\n\n" + "\n\n".join(reformatting_notes) + "\n\n"

    return extracted_text

def bulk():
    url_1 = "https://obo.genaud.net/dhamma-vinaya/pts/kd/thag/thag."
    url_2 = ".rhyc.pts.htm"
    for i in range(1,10):
        num = f"{i:03}"
        url = url_1 + num + url_2
        gen("1", i, url)

bulk()

# URL = "https://obo.genaud.net/dhamma-vinaya/pts/kd/thag/thag.001.rhyc.pts.htm"








