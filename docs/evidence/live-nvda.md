# Live historical NVDA filing validation

Codex retrieved one real filing on 2026-11-17 UTC in Nick's Windows workspace,
using a real SEC contact supplied by Nick. This is agent execution and review;
human contributor review is still required. Protocol approval was explicitly
granted by Nick and recorded on issue #5.

## Source and availability

- [NVDA fiscal 2021 10-K](https://www.sec.gov/Archives/edgar/data/1045810/000104581021000010/nvda-20210131.htm).
- Accession `0001045810-21-000010`; filing date 2021-02-26.
- SEC acceptance `2021-02-26T22:03:14+00:00`.
- First regular XNYS open after acceptance: `2021-03-01T14:30:00+00:00`.
- Decision cutoff: `2022-01-03T09:30:00-05:00`; this filing is eligible and
  within the configured 24-month lookback.
- Raw HTML: 2,511,774 bytes; SHA-256
  `280f822792eac7c1604863512cf850d2cb49473f2f1f63ce516280f22df6ba20`.

The command found 62 historically eligible metadata records and selected one
document, the latest eligible 10-K. It did not download all eligible filings or
the subsequent quarterly filings. This annual document alone is not complete
coverage of the available company information at the decision date.

## Extraction review

Both sections were nonempty: MD&A 6,346 whitespace-delimited words (41,797
characters), Risk Factors 10,313 words (68,406 characters). Codex checked the
extracted text against the normalized source, inspected section beginnings and
endings, and checked source Item headings. MD&A covers the company overview,
segment discussion and financial condition through accounting pronouncements;
Risk Factors covers industry, competition, supply/manufacturing and financial
risks. These checks are bounded spot checks, not a line-by-line human audit.

Observed preprocessing limitations: page numbers and "Table of Contents"
markers remain in narrative text; financial table cells can concatenate.
Whitespace and typographic punctuation differ from source presentation. No
Unicode replacement characters were found. A parser status of `complete`
means both requested sections are present, not that extraction is error-free.

## Commands

```powershell
$env:SEC_USER_AGENT = 'FinSight Research <your real contact email>'
.\.venv\Scripts\python.exe -m scripts.genai.ingest_filings --max-downloads 1
$env:RUN_SEC_INTEGRATION = '1'
.\.venv\Scripts\python.exe -m pytest tests/integration/test_sec_live.py -q
```

Observed ingestion: one completed, zero failed, no missing sections. The opt-in
live SEC metadata test passed (one test); it validates historical metadata,
not predictive performance. Raw HTML, processed sections and manifests remain
in ignored data directories. No bulk filing text or contact credentials are
committed. A rerun can obtain changed metadata, so preserve the recorded cache
and hashes when reproducing this particular evidence.

The combined suite subsequently passed all 18 tests with live SEC enabled:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -ra -p no:cacheprovider --basetemp outputs/pytest-live-validation
```

Four pandas deprecation warnings remain. An earlier combined run encountered
four fixture setup errors from access to Windows' shared pytest temporary
directory; the fresh workspace-local directory above resolved those errors.

## Real retrieval validation

The real `all-MiniLM-L6-v2` model embedded 56 chunks (21 MD&A, 35 Risk Factors).
Chroma persisted the index; reopening it returned the same 56 records. The
configured query, `growth competitive position and business risks`, returned
five passages at the January 2022 cutoff with the 24-month lookback. All five
matched their cited source section after whitespace normalization; each retained
the correct accession, URL and eligibility timestamp. They all came from Risk
Factors: this single query does not demonstrate balanced growth/risk coverage
or measured retrieval relevance. No retrieval-quality accuracy is inferred.

Negative checks against the same real-text index returned zero passages for
MSFT, for a cutoff before the filing became eligible, and for a one-month
lookback that makes this filing stale. Cache reuse was verified with an ingestion
client that fails on any document request. All these assertions passed.

```powershell
.\.venv\Scripts\python.exe -m pip install -e '.[retrieval]'
$env:HF_HOME = Join-Path (Get-Location) 'outputs/huggingface-cache'
.\.venv\Scripts\python.exe -m scripts.genai.validate_live_slice
```

Observed versions: sentence-transformers 6.3.0, transformers 5.23.0, torch 2.15.0,
Chroma 1.5.9. The local Hugging Face model ref was
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. The current model config does not
expose a commit hash, so the audit falls back to the local cache's ref. Preserve
that cache for this run; a future model download may differ. Full passages and
audit outputs remain under ignored `outputs/genai/live-validation/`; the compact
audit is retained alongside this note. The separate recorded model example uses
manually selected excerpts, not these similarity-ranked passages.
