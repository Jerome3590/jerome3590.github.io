"""Generate first-page-style publication thumbnails."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images" / "publications"
FONT_DIR = Path("C:/Windows/Fonts")

W, H = 720, 960
MARGIN = 48


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


F_KICKER = font("segoeuib.ttf", 22)
F_JOURNAL = font("georgia.ttf", 28)
F_TITLE = font("georgiab.ttf", 36)
F_AUTHORS = font("georgia.ttf", 22)
F_BODY = font("georgia.ttf", 20)
F_META = font("segoeui.ttf", 18)
F_DOI = font("consola.ttf", 16)


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if draw.textlength(trial, font=fnt) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


PAPERS = [
    {
        "slug": "journal-pending",
        "kicker": "MANUSCRIPT",
        "journal": "Journal pending",
        "year": "2026",
        "title": "Journal pending",
        "authors": "Venue and DOI not yet assigned",
        "blurb": "Unpublished work is listed without a target journal until acceptance.",
        "doi": "DOI pending",
        "accent": "#57534E",
    },
    {
        "slug": "ch01-seeking-venue",
        "kicker": "SEEKING VENUE",
        "journal": "Systematic Review",
        "year": "2026",
        "title": "Explainable AI and Pharmacogenomics for Opioid and Polypharmacy Risk: A Systematic Review",
        "authors": "R. Jerome Dixon  ·  Elvin T. Price",
        "blurb": "Literature map of explainable ML and pharmacogenomic features for prescription-drug risk. Next journal to be selected.",
        "doi": "DOI pending",
        "accent": "#57534E",
    },
    {
        "slug": "cts-70690",
        "kicker": "OPEN ACCESS  ·  ARTICLE",
        "journal": "Clinical and Translational Science",
        "year": "2026",
        "title": "Temporal Drivers of Opioid-Related ED Visits: An Ensemble Machine Learning Study With Consensus-Based Feature Attribution",
        "authors": "R. Jerome Dixon  ·  Elvin T. Price",
        "blurb": "Ensemble models and consensus-based feature attribution identify temporal drivers of opioid-related emergency department visits in statewide claims data.",
        "doi": "10.1111/cts.70690",
        "accent": "#8C1D18",
    },
    {
        "slug": "cts-70697",
        "kicker": "OPEN ACCESS  ·  ARTICLE",
        "journal": "Clinical and Translational Science",
        "year": "2026",
        "title": "A Serverless Pharmacogenomic Risk Dashboard: Translating Ensemble Models and Model-Based Scenario Rules to Clinical Decision Support",
        "authors": "R. Jerome Dixon  ·  Elvin T. Price",
        "blurb": "A serverless dashboard that turns ensemble risk models and model-based scenario rules into pharmacogenomic clinical decision support.",
        "doi": "10.1111/cts.70697",
        "accent": "#8C1D18",
    },
    {
        "slug": "cts-0235",
        "kicker": "ACCEPTED  ·  IN PRESS",
        "journal": "Clinical and Translational Science",
        "year": "2026",
        "title": "A SHAP-Informed Formal Feature Attribution Framework for Drug–Drug Interaction Risk in Large-Scale Claims Data",
        "authors": "R. Jerome Dixon  ·  Elvin T. Price",
        "blurb": "Accepted 19 August 2026. Formal feature attribution for polypharmacy and drug–drug interaction risk using large-scale claims data.",
        "doi": "DOI pending",
        "accent": "#5D6D7E",
    },
    {
        "slug": "digital-6010018",
        "kicker": "OPEN ACCESS  ·  ARTICLE",
        "journal": "Digital",
        "year": "2026",
        "title": "Leveraging Virtual Reality and Haptics to Teach Surgical Skills: A Usability Study on Retropubic Midurethral Slings",
        "authors": "Siff  ·  Watson  ·  Dixon  ·  Feldman  ·  Bost  ·  Giabbanelli",
        "blurb": "Usability of a VR + haptic trainer for retropubic midurethral sling surgery, evaluated with expert surgeons and trainees.",
        "doi": "10.3390/digital6010018",
        "accent": "#1A5276",
    },
    {
        "slug": "spv-1791",
        "kicker": "ARTICLE",
        "journal": "Urogynecology",
        "year": "2026",
        "title": "What Makes an Expert Surgeon? Novel Metrics for Evaluating Skills in Simulation",
        "authors": "Siff  ·  Dixon  ·  Watson  ·  Bost  ·  Giabbanelli  ·  Feldman",
        "blurb": "Motion and haptic metrics distinguish expert and novice pathways during virtual-reality retropubic midurethral sling simulation.",
        "doi": "10.1097/spv.0000000000001791",
        "accent": "#6C3483",
    },
    {
        "slug": "jmig-064",
        "kicker": "ARTICLE",
        "journal": "Journal of Minimally Invasive Gynecology",
        "year": "2026",
        "title": "SlingVR: A Virtual Reality Surgical Training System for Haptic-based “Blind” Surgical Procedures",
        "authors": "Siff  ·  Dixon  ·  Bost  ·  Feldman",
        "blurb": "A haptic VR platform for training “blind” surgical procedures, developed for retropubic midurethral sling placement.",
        "doi": "10.1016/j.jmig.2026.01.064",
        "accent": "#1F618D",
    },
    {
        "slug": "petr-70329",
        "kicker": "ARTICLE",
        "journal": "Pediatric Transplantation",
        "year": "2026",
        "title": "Donation After Circulatory Death in Pediatric Heart Transplantation",
        "authors": "Grorud  ·  Porter  ·  Rajab  ·  Dixon  ·  McCulloch  ·  Haregu",
        "blurb": "DCD listing is associated with more frequent donor offers in pediatric heart transplantation without worse early graft survival.",
        "doi": "10.1111/petr.70329",
        "accent": "#0E6655",
    },
    {
        "slug": "petr-70095",
        "kicker": "OPEN ACCESS  ·  ARTICLE",
        "journal": "Pediatric Transplantation",
        "year": "2025",
        "title": "Machine Learning for Predicting Waitlist Mortality in Pediatric Heart Transplantation",
        "authors": "Haregu  ·  Dixon  ·  McCulloch  ·  Porter",
        "blurb": "Machine learning identifies candidate and institutional offer-acceptance factors associated with pediatric heart transplant waitlist mortality.",
        "doi": "10.1111/petr.70095",
        "accent": "#0E6655",
    },
    {
        "slug": "petr-14747",
        "kicker": "ARTICLE",
        "journal": "Pediatric Transplantation",
        "year": "2024",
        "title": "Pediatric Donor Heart Utilization Variability among Organ Procurement Organizations",
        "authors": "Haregu  ·  Dixon  ·  Porter  ·  McCulloch",
        "blurb": "Variation in pediatric donor heart utilization is driven more by listing-center acceptance practice than by OPO clinical management.",
        "doi": "10.1111/petr.14747",
        "accent": "#0E6655",
    },
]


def render(paper: dict) -> None:
    img = Image.new("RGB", (W, H), "#F4F1EA")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 18), fill=paper["accent"])
    draw.rectangle((0, H - 18, W, H), fill=paper["accent"])
    draw.rectangle((MARGIN, 56, W - MARGIN, 58), fill=paper["accent"])

    y = 76
    inner = W - 2 * MARGIN
    draw.text((MARGIN, y), paper["kicker"], font=F_KICKER, fill=paper["accent"])
    y += 36
    draw.text((MARGIN, y), paper["journal"].upper(), font=F_JOURNAL, fill="#1B1B1B")
    y += 42
    draw.text((MARGIN, y), paper["year"], font=F_META, fill="#5D6D7E")
    y += 36
    draw.line((MARGIN, y, W - MARGIN, y), fill="#D5D0C6", width=2)
    y += 28

    for line in wrap(draw, paper["title"], F_TITLE, inner):
        draw.text((MARGIN, y), line, font=F_TITLE, fill="#1B1B1B")
        y += 46

    y += 8
    for line in wrap(draw, paper["authors"], F_AUTHORS, inner):
        draw.text((MARGIN, y), line, font=F_AUTHORS, fill="#4A4A4A")
        y += 30

    y += 18
    draw.line((MARGIN, y, W - MARGIN, y), fill="#D5D0C6", width=1)
    y += 24
    for line in wrap(draw, paper["blurb"], F_BODY, inner):
        draw.text((MARGIN, y), line, font=F_BODY, fill="#2C2C2C")
        y += 30

    doi_text = paper["doi"] if paper["doi"].startswith("DOI") else f"doi.org/{paper['doi']}"
    draw.text((MARGIN, H - 78), doi_text, font=F_DOI, fill="#5D6D7E")

    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{paper['slug']}.png"
    img.save(dest, "PNG", optimize=True)
    print(dest.name)


def main() -> None:
    for paper in PAPERS:
        render(paper)


if __name__ == "__main__":
    main()
