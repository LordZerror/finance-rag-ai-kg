The application: a Cross-Company Risk Exposure Graph.
This is close to something AWS actually built and wrote up recently: they extracted entity-relationship triplets from 10-K filings (e.g., pulling from Apple's 10-K that AAPL is subject to the Securities Exchange Act of 1934) and linked them into a graph — their example connected 15 S&P 100 companies through 7 shared risk factors and 3 regulatory requirements, surfacing patterns like circular ownership structures and hidden risk concentrations through governance connections that stay invisible in tabular or per-document data. That's exactly the "opens up their viewpoint" moment you want — RAG answers questions about one filing at a time, but the graph reveals that five companies you never thought to compare are all exposed to the same risk. It's a genuinely honest showcase of why you'd bother with a KG at all instead of just more RAG. AWSAWS
I'd pick a sector where the shared-risk story is intuitive even to non-finance people. Two options:

Semiconductor/AI supply chain (NVIDIA, AMD, TSMC, ASML, Qualcomm, Micron) — shared risk factors around export controls and Taiwan concentration. Thematically on-brand for an "AI in Finance" session since the companies are AI companies, and export controls have been in the news.
Regional banks post-SVB — shared exposure to commercial real estate / interest rate risk. More dramatic "could this have been an early warning" narrative, but requires audience to know what happened in 2023.

I'd lean semiconductor/AI — it's more relatable to a mixed beginner audience and ties the whole session together thematically. Happy to switch if you want the banking angle instead.
Session outline:
Block 1 — Technical (30 min): EDGAR, sec-parser, and RAG

What EDGAR is, the forms that matter (10-K/10-Q/8-K), and why raw filing HTML is a nightmare — show one messy filing on screen, that's your motivating pain point.
Introduce sec-parser: show its output turning that mess into a clean semantic tree (titles, sections, tables). This is the "aha, that's useful" moment.
Walk through the RAG architecture on a slide: parsed sections → chunked by section (not arbitrary token windows — worth explicitly calling out why that's better) → embedded with a finance-tuned embedding model → stored in a vector index → retrieved + answered by an LLM → FinBERT tags sentiment on the retrieved chunk.

Block 2 — Coding (30 min): Build the mini RAG app

Scaffolded notebook, not from-scratch: 2-3 filings pre-downloaded, sec-parser already wired up. They run parsing, chunking, embedding (finance-tuned or bge-large), load into a lightweight in-memory store (Chroma or FAISS — no server setup needed, important for a 30-min slot), then ask questions and watch FinBERT tag sentiment on the answer's source chunk.
End with them typing their own question live — gets hands dirty without needing them to write embedding/indexing code from scratch.

Block 3 — Technical (30 min): Why go beyond RAG, and the risk graph

Show a RAG limitation live: ask your Block 2 app "which of these companies share exposure to export control risk?" — it'll struggle, because that's a cross-document relational question, not a single-passage lookup.
Introduce the graph model: nodes for Company, RiskFactor, Regulation, maybe Officer; relationships like DISCLOSES, SUBJECT_TO. Briefly explain how sec-parser's structured risk-factor sections feed entity/relationship extraction (rule-based for speed, or LLM-based triple extraction for messier prose — mention both, demo one).
Present the AWS-style graph as the target picture: this is what "seeing" shared risk looks like instead of reading it.

Block 4 — Coding (30 min): Build and query the graph

Pre-extract entities/relationships for ~6-8 companies beforehand (don't do live LLM extraction in a beginner 30-min slot — too slow/unreliable) and give them as a CSV/JSON they load into Neo4j via a few lines of Cypher.
Have them run 2-3 Cypher queries live, ending on the payoff query — something like finding companies that share a risk factor — and show it rendered as an actual graph in Neo4j Browser. That visual, more than anything else in the session, is what "opens up their viewpoint."

