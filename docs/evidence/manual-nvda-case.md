# Recorded manual, filing-grounded model example

Run: 2026-11-17 UTC in Nick's Codex session. Model identity: the current Codex
assistant (identified by the session instructions as based on GPT-6); an exact
deployment revision, sampling settings and separate API request ID are not
exposed. This is a manual, in-session generation, not an automated provider
integration, independent model benchmark or validated investment signal.

The assistant was shown the exact prompt below by running
`python -m scripts.genai.prepare_manual_case`. It generated the JSON retained
verbatim in `manual-nvda-response.json`. No additional provider call occurred.
The authoring session also knew the quantitative pilot outcome, so instruction
grounding does not demonstrate blinding or eliminate future-knowledge leakage.
This limitation prevents using this example as predictive evidence.

## Exact prompt and source excerpts

```text
Historical NVDA case study. Decision cutoff: 2022-01-03 09:30 America/New_York.
Use ONLY excerpts E1-E3 below. Report two concise qualitative observations, each with evidence IDs. Describe reported results as historical, not a forecast. Do not use knowledge of later events or prices. Return JSON containing observations, qualitative_score, and abstentions. Set qualitative_score to null if these excerpts cannot establish a calibrated probability of outperforming SPY. Do not infer acquisition-free growth, valuation, future returns or investment advice.

E1 [management_discussion]: Graphics segment revenue increased by 29% in fiscal year 2021 compared to fiscal year 2020
E2 [management_discussion]: Compute & Networking segment revenue increased by 109% in fiscal year 2021 compared to fiscal year 2020
E3 [risk_factors]: We depend on third parties and their technology to manufacture, assemble, test and/or package our products, which reduces our control over product quantity and quality
```

Prompt SHA-256 (UTF-8, no terminal newline):
`48dfb11182f1ec9fc07bd601b05526d90c0c0e8498136c82c11277bc3e93dcc1`.

All three excerpts were manually selected, not returned by similarity search.
They are exact substrings of the extracted source sections. E1/E2 come from
Item 7's segment revenue discussion; E3 comes from Item 1A's supply/manufacturing
risks. Source: [NVDA fiscal 2021 10-K](https://www.sec.gov/Archives/edgar/data/1045810/000104581021000010/nvda-20210131.htm),
accession `0001045810-21-000010`, accepted 2021-02-26 22:03:14 UTC, first eligible
2021-03-01 14:30 UTC. See `live-nvda.md` for source hash and extraction checks.

## Citation and claim review

Reviewer: Codex, the same agent that generated the response. This is an agent
self-check, not human or independent peer review. Nick and Dean must review
before final claim sign-off.

| Output | Source check | Outcome |
| --- | --- | --- |
| Fiscal 2021 Graphics +29%; Compute & Networking +109% | Exact figures, periods and segment names in E1/E2 | Supported |
| Third-party production reduces quantity/quality control | Explicitly stated in E3 | Supported |

Two observations supported, zero unsupported observations, two stated abstention
items. These are descriptive counts for one manually selected example, not
accuracy estimates. The null score is an abstention; it is not the prototype's
neutral 0.5 fixture. No investment ranking or quant-plus-GenAI result is produced.

The surrounding source attributes part of Compute & Networking growth to the
Mellanox acquisition, so the response deliberately does not call growth organic.
The example demonstrates source traceability and abstention only. Reproducing
the source excerpts and exact prompt is deterministic; regenerating a model
response need not produce identical text.
