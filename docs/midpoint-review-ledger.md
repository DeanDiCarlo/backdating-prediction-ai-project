# Midpoint claim review

New artifact: docs/midpoint-checkin.pdf. Original retained as docs/midterm-report.pdf (archived draft).

| Claim | Evidence | Review status |
| --- | --- | --- |
| Price counts, holdings, returns | Merged Yahoo and Nick reproduction notes | Recorded evidence reviewed; private snapshot absent here; Nick financial confirmation pending |
| Filing counts and 56 chunks | Merged live NVDA note and retrieval audit | Recorded evidence reviewed; preserved cache absent here |
| Manual model observations and abstention | Exact retained prompt and JSON response | Agent review only; Dean citation review pending |
| Six-question experiment | midpoint-question-set.json | Specified, not executed; cache unavailable |
| FactSet escalation | Dean's instructions in this session | Nick pursuing escalation; access not secured |
| November 30 project deadline | Dean confirmed in this session | Planning date; presentation December 1 or 3 tentative |

Dean: reserve 45–60 minutes to read all three pages, check the manual example against the original filing, and confirm claims/roles. Record approval against the final PDF hash. Nick: verify return definitions/numbers, price adjustments and FactSet wording. These confirmations have not occurred in this implementation session. No submission has occurred.

Closure assessment: #9/#10 have merged completion evidence; #5 can close after documentation reconciliation lands; #1/#2 require contributor review; #12/#13 require final report acceptance; #3 remains open through submission; #7 retains dividend verification; #6/#8/#11/#14 remain future work. No issue state was changed.

Implementation verification: 17 existing tests passed, one live SEC test skipped; three builder checks passed. Three pages visually inspected before the final chart inset correction. All extracted text is at least 11 points; absolute HTTPS links and horizontal one-inch bounds checked. Two same-environment builds matched. Renderer: reportlab 5.1.0, PyMuPDF 2.1. PDF SHA-256: fb258a366f143219d25a60dc2dd0747ec3d9917b22612f660fa1f9576de7522c.

Link/layout revision: all three original GitHub references verified through authenticated connector at the recorded commit. Repository is private, so 404 is an access issue. Replaced repository links with self-contained source references, embedded exact evidence notes and a five-page companion PDF. New artifact SHA-256: b59bfa8fdf74edb7a80ba1ad8198f7b50c241eeedfab86ffa4f42f4fa9b106c2. Three pages; same-environment rebuild hashes match.

Shared-team revision: contributor roles and milestones now reflect joint responsibility for GenAI, data and evaluation. Public GitHub source links restored in both PDFs. Current report SHA-256: 2068a2e7b513e06d0a633990b61abcd4f9cb06f11a24af09e9182f28bd5a8c8c. Historical evidence provenance unchanged.

GitHub issue audit November 17: closed #9/#10 as completed based on merged PR #20 execution evidence. Updated all other open issue bodies with current status, documented completed checklist items and shared team workflow. #1/#2 remain for contributor review; #5 for remaining documentation merge; #12/#13 for final acceptance/publication; #3 for submission record; #7 for independent dividend verification; #6/#8/#11/#14 for unfinished final-project work. Revised PDFs/source remain local and uncommitted.

Publication update: revised source, PDFs, builder, question specification, team handoff and regression checks are included in the PR #19 branch update. Earlier references to local-only files describe the state at those audit checkpoints. Contributor approval and submission remain unrecorded.

Pre-commit checks in isolated PR checkout: 20 passed, one live SEC test skipped, four pandas warnings. Rebuilt report bytes match committed candidate. Final candidate PDF SHA-256: ae615fdc75a14c5f98cb117cc32516238d404810f7166bea86d30d1bdddd1f25.
