"""Download and cache the annual filings used in the session notebooks.

Run once before the session (requires internet access to SEC EDGAR):

    python scripts/download_filings.py

Saves the primary filing HTML for each company to data/filings/<TICKER>_10-K.html.
SEC EDGAR requires a declared User-Agent (company name + contact email) — edit
COMPANY_NAME / CONTACT_EMAIL below if you fork this repo.
"""

from pathlib import Path

from sec_downloader import Downloader

COMPANY_NAME = "AIFinanceSession"
CONTACT_EMAIL = "sharedneetcodeusc@gmail.com"

# US filers only: TSMC and ASML are foreign private issuers and file 20-F,
# not 10-K. They still show up in the Session 2 graph as supplier nodes.
TICKERS = ["NVDA", "AMD", "MU"]
FORM = "10-K"

OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "filings"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dl = Downloader(COMPANY_NAME, CONTACT_EMAIL)
    for ticker in TICKERS:
        out_path = OUT_DIR / f"{ticker}_10-K.html"
        if out_path.exists():
            print(f"{ticker}: already cached at {out_path}")
            continue
        print(f"{ticker}: downloading latest {FORM} from EDGAR ...")
        html = dl.get_filing_html(ticker=ticker, form=FORM)
        if isinstance(html, bytes):
            html = html.decode("utf-8", errors="replace")
        out_path.write_text(html, encoding="utf-8")
        print(f"{ticker}: saved {len(html):,} characters to {out_path}")


if __name__ == "__main__":
    main()
