# Aegis — pediatric BSI / CLABSI adjudication

Streamlit workbench for **NHSN-style bloodstream infection review**. A positive blood culture with a central line is not automatically a CLABSI. Aegis runs four sequential surveillance checks, then a parallel bedside ΔTTP lane, so infection prevention and the clinical team see different questions side by side.

Educational demo. **Not a medical device** and not a substitute for NHSN definitions.

## Synthetic test cases

The five review-window events are **synthetic**. Names, MRNs, units, organisms, labs, and timestamps are invented for demonstration and engine tests. They are not real patients and contain no PHI.

## What you see

Each event is a **pair**:

| Column | Question | Color |
| --- | --- | --- |
| Surveillance class · quality | Does this count in the SIR? | Teal = excluded / non-event · Pink = Primary CLABSI |
| Bedside action · clinical | Keep or pull the line? | Teal = salvage · Pink = extract · Gold = missing data |

## Five synthetic review-window cases (18–24 Aug 2026)

1. **Maya Chen** — *E. coli* MBI-LCBI, ΔTTP 12 min → excluded from SIR, salvage the line
2. **Jonah Reyes** — *S. epidermidis* biofilm, ΔTTP 160 min → Primary CLABSI, extract
3. **Amira Haddad** — *P. aeruginosa* lung match → Secondary BSI, salvage
4. **Leo Park** — *S. aureus*, line-only draw → Primary CLABSI, gold gap: draw a peripheral
5. **Sofia Alvarez** — single commensal bottle → contaminant, gold gap: redraw

Expected engine outcomes live in [`streamlit_app/fixtures/expected-outcomes.json`](streamlit_app/fixtures/expected-outcomes.json) (`synthetic: true`).

## Run locally

```bash
cd streamlit_app
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the URL Streamlit prints (usually http://localhost:8501).

## Pipeline

1. Integrity — LCBI 1 vs LCBI 2/3 vs contaminant
2. Source origin — secondary BSI attribution (SBAP)
3. Pathophysiology — MBI-LCBI (neutropenia / HSCT)
4. Device eligibility — line present on DOE, not MBI
5. Bedside (parallel) — paired TTP; ΔTTP ≥ 120 min supports intraluminal biofilm

## Repo layout

```
streamlit_app/     Streamlit UI, NHSN engine, synthetic fixtures
.streamlit/        Theme
```
