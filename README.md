# AI in Finance — Hands-On Session: RAG & Risk Graphs over SEC Filings

Two 30-minute coding notebooks for the "AI in Finance" technical session:

| | Notebook | What you build |
|---|---|---|
| Session 1 | [`notebooks/session1_rag.ipynb`](notebooks/session1_rag.ipynb) | A RAG question-answering system over real 10-K filings (NVIDIA, AMD, Micron): sec-parser → section-aware chunking → BGE embeddings → Chroma → Gemini answers with citations → FinBERT sentiment |
| Session 2 | [`notebooks/session2_risk_graph.ipynb`](notebooks/session2_risk_graph.ipynb) | A cross-company risk exposure graph of 8 semiconductor companies in Neo4j: shared risks, hidden supply-chain exposure, single points of failure |

**Open in Colab:**

- Session 1: `https://colab.research.google.com/github/LordZerror/finance-rag-ai-kg/blob/main/notebooks/session1_rag.ipynb`
- Session 2: `https://colab.research.google.com/github/LordZerror/finance-rag-ai-kg/blob/main/notebooks/session2_risk_graph.ipynb`

## Before the session (attendees — 5 minutes)

1. **Google account** — the notebooks run in [Google Colab](https://colab.research.google.com), nothing to install.
2. **Gemini API key (free)** — go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey) → *Create API key*. No credit card.
   In Colab, click the 🔑 icon in the left sidebar and save it as a secret named `GEMINI_API_KEY` (enable notebook access).
3. **Neo4j Aura free instance (Session 2 only)** — go to [console.neo4j.io](https://console.neo4j.io) → sign up → *Create instance* → **Free**.
   Download the credentials file it offers (it's shown **only once**) — you'll paste the URI and password into the notebook.
   The instance takes ~2 minutes to spin up, so do this before the session starts.

No key / no instance? You can still run everything except the LLM-generated answers (Session 1) and the live Cypher queries (Session 2) — the notebooks degrade gracefully and say so.

## Repo map

```
notebooks/
  session1_rag.ipynb        Session 1: RAG over SEC filings
  session2_risk_graph.ipynb Session 2: build & query the risk graph
data/
  filings/                  cached 10-K HTML (NVDA, AMD, MU) — offline fallback for Session 1
  graph/                    curated nodes + relationships CSVs loaded in Session 2
scripts/
  download_filings.py       re-fetch the cached filings from SEC EDGAR
  extract_graph_data.py     provenance: LLM-assisted triple extraction that produced the
                            graph CSVs (output was then hand-curated — see script docstring)
requirements.txt            for running locally instead of Colab
```

## Running locally instead of Colab

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/download_filings.py   # optional: refresh cached filings
jupyter lab notebooks/
```

## Presenter notes

- **Session 1** cold-start: the pip installs + model downloads take ~3 minutes in Colab — have
  attendees hit *Runtime → Run all* at the top of the block while you talk through the pipeline
  diagram, then walk the cells.
- **Session 2** payoff visual: the PyVis cell renders inline for everyone; for the big-screen
  moment, open your own Aura instance's *Query* tab and run
  `MATCH path = (:Company)-[]->() RETURN path`.
- The graph CSVs are deliberately hand-curated so the live session never depends on LLM
  extraction quality. `scripts/extract_graph_data.py` is the honest story of where they came
  from — mention it, don't run it live.
- sec-parser officially targets 10-Qs; it parses these three 10-Ks cleanly (the notebooks
  suppress its warnings and say so on screen).
