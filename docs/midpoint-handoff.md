# Midpoint execution handoff

Start at GitHub issue #3. Nick and his Codex drive the queue; Dean supplies local artifacts and access. Scientific roles remain Dean DiCarlo (SEC/GenAI) and Nicholas Stanis (quantitative/evaluation).

## Goal text

Deliver a reviewed, reproducible FinSight midpoint report within a three-hour work window. Read issues #3, #5, #7, #1, #9, #10, #2, #12 and #13, the three reference PDFs, merged PRs #15/#16, the experiment contract and Yahoo evidence note. Follow the increments below. Commit coherent changes, create PRs and merge sequentially after applicable checks and diff review. Never bypass branch protection or claim unperformed human review. Keep issues synchronized with evidence. Do not invent results or expand into FactSet, fundamentals or walk-forward implementation tonight. Record blockers and continue independent work. Stop at a submission-ready artifact; record actual submission separately.

## Order and merge increments

1. 0–20 minutes: #3/#5 protocol and status documentation (increment A).
2. 20–50: #7 snapshot transfer and #1 second-contributor reproduction (B).
3. 50–100: #9 live filing, #10 real retrieval, #2 reviewed model example (C).
4. 100–155: #12 diagram/methods and #13 report assembly (D).
5. 155–180: contributor claim review, PDF inspection, final merge and readiness record.

Draft the skeleton while evidence is collected. Snapshot transfer and SEC access setup can happen alongside environment checks. Merge dependent increments in order. Do not create empty commits for issue-only updates. Never stage the unrelated FactSet YAML.

## Access and fallback

The ignored `data/raw/yahoo_pilot.csv` and adjacent JSON metadata must both reach Nick through an agreed private channel under applicable terms. A clone does not contain them. Hash and reproduction commands are in [Yahoo evidence](evidence/yahoo-pilot.md). A new download is a different snapshot unless its hash matches.

SEC_USER_AGENT was absent during this handoff. Supply a real contact before live SEC requests. If retrieval is blocked, use manually selected, historically eligible filing excerpts for a recorded LLM run and label it manual. Keep #10 open. Preserve exact prompt/passages/model/date/raw output and review every citation and claim against the original filing. Record reviewer identity, supported/unsupported/abstained counts and actual filing/section/chunk counts. If no reviewed example is ready at evidence freeze, state that it is pending; do not include a qualitative finding.

## Current verification

Local rerun on 2026-11-16 America/New_York using `/tmp/finsight-test-venv/bin/python`: `-m pytest -q` returned 16 passed, one skipped, four pandas deprecation warnings. The skipped test is live SEC integration. This is agent verification in the original workspace, not independent contributor reproduction.

`-m scripts.quant.run_pilot --snapshot data/raw/yahoo_pilot.csv --output /tmp/finsight-midpoint-reproduction` reproduced the recorded holdings and results. SHA-256 matched `d362425e39945c022603aea6a3bf1bf8983cd66512e6f55fa579346128a9bcb2`. Direct CSV inspection found 3,108 rows, 518 per ticker and zero duplicate ticker/date rows. Independent dividend-adjusted-series verification remains open.

## Report evidence map

| Section | Evidence | Remaining gate |
| --- | --- | --- |
| Overview | proposal.pdf, README research question | Keep original incremental-value question |
| Dataset | Yahoo metadata/evidence, inspected CSV counts | Nick snapshot access; real filing counts |
| Methods | merged source, config, contract, PRs #15/#16 | Distinguish defaults, fixture tests and actual execution |
| Results | reproduced momentum table | Second-contributor reproduction; reviewed qualitative example |
| Next Steps | issues #8/#11/#14 | Real scoring/coverage before matched comparison, then expansion |

Target three pages: overview .3, dataset .4, methods .9, results .9, next steps .5. Use 11-point single-column text, one-inch margins, names and roles. The example report is structural guidance only. Preserve report source and PDF; inspect the final PDF and record actual submission separately.
