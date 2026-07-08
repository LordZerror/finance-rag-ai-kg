"""Offline entity/relationship extraction for the Session 2 risk graph.

This is the provenance script for data/graph/*.csv. It was run once before the
session, and its output was then HAND-CURATED (deduplicated, renamed to canonical
risk-factor ids, spot-checked against the filings). The live session loads the
curated CSVs directly — never run LLM extraction live in a 30-minute slot.

Usage (requires GEMINI_API_KEY and cached filings from download_filings.py):

    export GEMINI_API_KEY=...
    python scripts/extract_graph_data.py

Writes candidate triples to data/graph/candidates/<TICKER>_triples.csv.
"""

import csv
import json
import os
from pathlib import Path

import sec_parser as sp
from google import genai

ROOT = Path(__file__).resolve().parent.parent
FILINGS_DIR = ROOT / "data" / "filings"
OUT_DIR = ROOT / "data" / "graph" / "candidates"

MODEL = "gemini-2.5-flash"

EXTRACTION_PROMPT = """\
You are building a financial knowledge graph from a company's SEC filing risk
factors (Item 1A). Extract entity-relationship triples from the text below.

Allowed relationship types:
- DISCLOSES: company -> a risk factor category (short canonical name, e.g. "US export controls on advanced chips", "Geopolitical concentration in Taiwan")
- SUBJECT_TO: company -> a specific named regulation (e.g. "U.S. Export Administration Regulations")
- DEPENDS_ON: company -> another specific named company it relies on (supplier, foundry, single customer)

Rules:
- Only extract what the text explicitly supports; include a short evidence quote (<= 25 words) for each triple.
- Use general, reusable risk factor names so the same risk can match across companies.
- Return a JSON array of objects: {"source": ..., "rel_type": ..., "target": ..., "evidence": ...}

Company: {ticker}
Risk factor text:
{text}
"""


def get_risk_factor_text(html: str, max_chars: int = 60_000) -> str:
    """Pull the Item 1A / Risk Factors part of the filing via sec-parser."""
    elements = sp.Edgar10QParser().parse(html)
    tree = sp.TreeBuilder().build(elements)

    collected: list[str] = []
    in_risk = False
    for node in tree.nodes:
        if isinstance(node.semantic_element, sp.TopSectionTitle) or isinstance(
            node.semantic_element, sp.TitleElement
        ):
            title = node.text.lower()
            if "risk factors" in title:
                in_risk = True
            elif in_risk and title.startswith("item "):
                break
        if in_risk:
            collected.append(node.text)
    text = "\n".join(collected)
    if not text:  # fallback: crude keyword window over the whole parse
        all_text = "\n".join(e.text for e in elements)
        idx = all_text.lower().find("risk factors")
        text = all_text[idx : idx + max_chars] if idx >= 0 else all_text[:max_chars]
    return text[:max_chars]


def extract_triples(client: genai.Client, ticker: str, text: str) -> list[dict]:
    response = client.models.generate_content(
        model=MODEL,
        contents=EXTRACTION_PROMPT.format(ticker=ticker, text=text),
        config={"response_mime_type": "application/json"},
    )
    return json.loads(response.text)


def main() -> None:
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit("Set GEMINI_API_KEY first (https://aistudio.google.com/apikey)")
    client = genai.Client()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for filing in sorted(FILINGS_DIR.glob("*_10-K.html")):
        ticker = filing.name.split("_")[0]
        print(f"{ticker}: extracting risk-factor text ...")
        text = get_risk_factor_text(filing.read_text(encoding="utf-8"))
        print(f"{ticker}: {len(text):,} chars -> {MODEL} ...")
        triples = extract_triples(client, ticker, text)

        out_path = OUT_DIR / f"{ticker}_triples.csv"
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["source", "rel_type", "target", "evidence"])
            writer.writeheader()
            writer.writerows(triples)
        print(f"{ticker}: wrote {len(triples)} candidate triples to {out_path}")


if __name__ == "__main__":
    main()
