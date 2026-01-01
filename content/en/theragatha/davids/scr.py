import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString

URL = "https://obo.genaud.net/dhamma-vinaya/pts/kd/thag/thag.200.rhyc.pts.htm"

from bs4 import NavigableString

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


def main():
    response = requests.get(URL)
    response.raise_for_status()  # fail fast if the request breaks

    soup = BeautifulSoup(response.text, "html.parser")
    # print(soup.get_text())
    with open("scraped_content.md", "w", encoding="utf-8") as f:
        f.write(soup.get_text())

    monk_name = soup.find('h1').get_text(strip=True)[2:]  # Adjust tag if necessary
    print("Monk Name:", monk_name)
    # commentary =
    verse = soup.find_all(class_="f4 in2")

    notes = soup.find_all(class_="lgqt")

    if verse:
        for element in verse:
            print("Verse text:", element.get_text(strip=True))
    else:
        print("Not found")

    if notes:
        for element in notes:
            print("Notes text:", element.get_text(strip=True))
    else:
        print("Not found")

""" if __name__ == "__main__":
    main() """

soup = BeautifulSoup(requests.get(URL).text, "html.parser")

""" test = soup.find_all(class_="f2 ctr")
for i, t in enumerate(test):
    print(f"\nTEST {i}")
    print(t.get_text(" ", strip=True)) """

""" start = soup.select_one("div.f2.ctr")
commentary = extract_commentary(start)

print(commentary) """

start = soup.find("p", class_="f2 ctr")
assert start is not None, "Could not find commentary start"
commentary = extract_commentary(start)
print(commentary)






