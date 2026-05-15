from pathlib import Path
import xml.etree.ElementTree as ET
import html

TEI_DIR = Path("collection/tei")
print("Letar efter TEI-filer i:", TEI_DIR)
print("Antal XML-filer:", len(list(TEI_DIR.glob("*.xml"))))
OUT_DIR = Path("docs/objects")
OUT_DIR.mkdir(exist_ok=True)

NS = {"tei": "http://www.tei-c.org/ns/1.0"}

LABELS = {
    "coated": "bestruket",
    "uncoated": "obestruket",
    "thin": "tunt papper",
    "thick": "kraftigt papper",
    "black": "svart tryck",
    "oneColor": "enfärgstryck",
    "twoColor": "tvåfärgstryck",
    "multiColor": "flerfärgstryck",
    "unbound": "obunden/vikt",
    "stapled": "häftad",
    "glued": "limmad",
    "sewn": "sydd",
    "centered": "centrerad",
    "justified": "marginaljusterad",
    "leftAligned": "vänsterjusterad",
    "rightAligned": "högerjusterad",
    "transitionalSerif": "transitional serif",
    "sansSerif": "sans-serif",
    "oldStyleSerif": "old style-serif",
    "modernSerif": "modern serif",
    "slabSerif": "slab serif",
    "blackLetter": "fraktur",
    "script": "script",
    "glyphic": "glyfisk",
    "mixedType": "blandade typsnitt",
    "decorative": "dekorativt/icke-standardiserat typsnitt",
    "photography": "fotografi",
    "illustration": "illustration",
    "decoratedInitial": "anfang",
    "line": "linje",
    "fleuron": "fleuron",
    "emblem": "emblem",
    "signature": "signatur",
    "textFrame": "textram",
    "figurativeGraphicElement": "figurativt grafiskt element",
    "geometricGraphicElement": "geometriskt grafiskt element",
    "otherGraphicElement": "övrigt grafiskt element",
}

def text(root, xpath):
    found = root.find(xpath, NS)
    return html.escape(found.text.strip()) if found is not None and found.text else ""

def ana_values(root, xpath, allowed):
    el = root.find(xpath, NS)
    if el is None:
        return ""

    ana = el.get("ana", "")
    ids = [x.replace("#", "") for x in ana.split()]
    labels = [LABELS.get(x, x) for x in ids if x in allowed]

    return html.escape(", ".join(labels))

def make_page(data):
    return f"""<!DOCTYPE html>
<html lang="sv">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{data["title"]}</title>
  <link rel="stylesheet" href="../assets/css/main.css">
</head>

<body>

<nav>
  <a href="../index.html">← Tillbaka till galleriet</a>
</nav>

<main class="object-page">

  <div class="object-facsimile">
    <div class="flip-box">
      <div class="flip-box-inner">

        <div class="flip-box-front">
<img src="../assets/img/documents/SAK_{data["filename"]}_a.jpg"
               alt="Framsida av {data["title"]}">
        </div>

        <div class="flip-box-back">
<img src="../assets/img/documents/SAK_{data["filename"]}_b.jpg"
               alt="Baksida av {data["title"]}">
        </div>

      </div>
    </div>
  </div>

  <aside class="object-metadata">
    <h1>{data["title"]}</h1>

    <p><strong>År:</strong> {data["year"]}</p>
    <p><strong>Titel:</strong> {data["title"]}</p>
    <p><strong>Tryckeri:</strong> {data["printer"]}</p>
    <p><strong>Höjd:</strong> {data["height"]}</p>
    <p><strong>Bredd:</strong> {data["width"]}</p>
    <p><strong>Tjocklek:</strong> {data["depth"]}</p>
    <p><strong>Bindningsteknik:</strong> {data["binding"]}</p>
    <p><strong>Pappersyta:</strong> {data["paper_surface"]}</p>
    <p><strong>Papperskvalitet:</strong> {data["paper_quality"]}</p>
    <p><strong>Färgschema:</strong> {data["color_scheme"]}</p>
    <p><strong>Layout:</strong> {data["layout"]}</p>
    <p><strong>Typsnitt:</strong> {data["typeface"]}</p>
    <p><strong>Bildinnehåll:</strong> {data["image_content"]}</p>
    <p><strong>Grafiska element:</strong> {data["graphic_elements"]}</p>
    <p><strong>Bevarandestatus:</strong> {data["condition"]}</p>
  </aside>

</main>

</body>
</html>
"""

for tei_file in TEI_DIR.glob("*.xml"):
    tree = ET.parse(tei_file)
    root = tree.getroot()
    filename = tei_file.stem

    data = {
        "filename": filename,
        "title": text(root, ".//tei:monogr/tei:title"),
        "year": text(root, ".//tei:imprint/tei:date"),
        "printer": text(root, ".//tei:imprint/tei:note/tei:name"),
        "height": text(root, ".//tei:supportDesc//tei:height"),
        "width": text(root, ".//tei:supportDesc//tei:width"),
        "depth": text(root, ".//tei:supportDesc//tei:depth"),
        "condition": text(root, ".//tei:bindingDesc//tei:condition"),

        "paper_surface": ana_values(root, ".//tei:supportDesc//tei:support", {"coated", "uncoated"}),
        "paper_quality": ana_values(root, ".//tei:supportDesc//tei:support", {"thin", "thick"}),
        "color_scheme": ana_values(root, ".//tei:supportDesc//tei:support", {"black", "oneColor", "twoColor", "multiColor"}),
        "layout": ana_values(root, ".//tei:layoutDesc//tei:layout", {"centered", "justified", "leftAligned", "rightAligned"}),
        "typeface": ana_values(root, ".//tei:typeDesc//tei:typeNote", {
            "oldStyleSerif", "sansSerif", "modernSerif", "transitionalSerif",
            "slabSerif", "blackLetter", "script", "glyphic", "mixedType", "decorative"
        }),
        "image_content": ana_values(root, ".//tei:decoDesc//tei:decoNote", {"photography", "illustration"}),
        "graphic_elements": ana_values(root, ".//tei:decoDesc//tei:decoNote", {
            "decoratedInitial", "line", "fleuron", "emblem", "signature",
            "textFrame", "figurativeGraphicElement", "geometricGraphicElement",
            "otherGraphicElement"
        }),
        "binding": ana_values(root, ".//tei:bindingDesc//tei:binding", {"unbound", "stapled", "glued", "sewn"}),
    }

    output = OUT_DIR / f"{filename}.html"
    output.write_text(make_page(data), encoding="utf-8")
    print(f"Skapade {output}")