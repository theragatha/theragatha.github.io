import re
import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString
from pathlib import Path

def gen(chapter_number, verse_number, URL):
        
        #new_content = new_front_matter + "\n# " + chapter_number + "." + verse_number + "\n\n## Commentary\n\n## Verse\n\n## Attribution\n\n## Notes"
        extracted_content, verses_content, monk_name = extract(chapter_number, verse_number, URL)

        new_front_matter = f"""---
title: "{chapter_number}.{verse_number} {monk_name}"
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
        
        new_content_c = new_front_matter + "\n" + extracted_content
        new_content = new_front_matter + "\n" +  f"## {chapter_number}.{verse_number} {monk_name}\n\n" + verses_content

        # Create commentary folder if it doesn't exist
        output_dir = Path("chapter-one/commentary")
        output_dir.mkdir(exist_ok=True)

        # Write the new file (e.g., commentary/thag1.4-commentary.md)
        output_filename = output_dir / f"thag{chapter_number}.{verse_number}-commentary.md"
        with open(output_filename, "w", encoding="utf-8") as out:
            out.write(new_content_c)

        # Write the verses only file
        output_dir = Path("chapter-one")
        output_dir.mkdir(exist_ok=True)
        output_filename = output_dir / f"thag{chapter_number}.{verse_number}.md"
        with open(output_filename, "w", encoding="utf-8") as out:
            out.write(new_content)
        
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

    monk_name = soup.find('h1').decode_contents().split("<br/>")[1].strip()[:-4]

    # Extract commentary
    start = soup.find("p", class_="f2 ctr")
    assert start is not None, "Could not find commentary start"
    commentary = extract_commentary(start)
    
    # Remove "Public Domain" and subsequent linebreak if present
    if commentary.startswith("Public Domain\n\n"):
        commentary = commentary[len("Public Domain\n\n"):]
    elif commentary.startswith("Public Domain"):
        commentary = commentary[len("Public Domain"):].lstrip()

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
        
    attribution = collect_attribution_from_last_verse(last_verse_p) if last_verse_p else ""

    # Extract notes
    notes = soup.find_all(class_="lgqt")

    # Reformat notes
    reformatting_notes = []
    for note in notes:
        text = note.get_text(separator=" ", strip=True)
        if text.startswith("["):
            # Extract the footnote number (e.g., "[1]" → "1")
            number = text[1:text.find("]")].strip()
            # Get the footnote content after the closing bracket
            content = text[text.find("]") + 1:].strip()
            # Format as markdown footnote: [^1]: content
            text = f"[^{number}]: {content}"
        note.replace_with(text)
        reformatting_notes.append(text)

    # return monk_name, commentary, verse, reformatting_notes

    # Write to file
    extracted_text = ""
    with open("scraped_content.md", "w", encoding="utf-8") as f:
       
        # Monk Name
        # f.write(f"# {monk_name}\n\n")
        extracted_text += f"# {monk_name}\n\n"

        # Commentary
        # f.write("## Commentary\n\n")
        # f.write(commentary + "\n\n")
        extracted_text += "## Commentary\n\n" + commentary + "\n\n"

        # Verses
        # f.write("## Verses\n\n")
        # for element in verses:
            # f.write(element + "\n\n")
        extracted_text += "## Verses\n\n" + "\n\n".join(verses) + "\n\n"

        # Attribution
        # f.write("## Attribution\n\n")
        attribution_lines = attribution.split("\n\n")
        # for i in range(len(attribution_lines)-1):
            # f.write(attribution_lines[i] + "\\\n")
        # f.write(attribution_lines[-1] + "\n\n")
        # f.write("\n\n")
        extracted_text += "## Attribution\n\n" + attribution + "\n\n"

        # Notes
        # f.write("## Notes\n\n")
        # for element in reformatting_notes:
            # f.write(element + "\n\n")
        extracted_text += "## Notes\n\n" + "\n\n".join(reformatting_notes) + "\n\n"
    return extracted_text, re.sub(r'\[.*?\]', "", "\n\n".join(verses)).strip() + "\n\n", monk_name

def url_exists(url):
    """
    Checks if a URL exists and is reachable using a HEAD request.
    """
    try:
        # Send a HEAD request and allow redirects (important for sites like Google)
        response = requests.head(url, allow_redirects=True, timeout=5)
        # Check if status code is in the 2xx (success) or 3xx (redirection handled) range
        return 200 <= response.status_code < 400
    except requests.exceptions.ConnectionError:
        # Handles cases like DNS errors, refused connections, etc.
        return False
    except requests.exceptions.RequestException:
        # Handles any other potential errors during the request
        return False
    
def bulk():
    url_1 = "https://obo.genaud.net/dhamma-vinaya/pts/kd/thag/thag."
    url_2 = ".rhyc.pts.htm"
    for i in range(1,121):
        num = f"{i:03}"
        url = url_1 + num + url_2
        if url_exists(url):
            gen("1", i, url)



bulk()

# URL = "https://obo.genaud.net/dhamma-vinaya/pts/kd/thag/thag.001.rhyc.pts.htm"








