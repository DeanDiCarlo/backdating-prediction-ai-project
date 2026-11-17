# Build the revised midpoint check-in

Install .[report] in the environment, then run `python -m scripts.build_midterm_report`. Source: docs/midpoint-checkin.md; output: docs/midpoint-checkin.pdf. The former report is retained as docs/midterm-report.pdf (archived draft).

Explicit markers [[architecture]], [[returns]], and [[example]] select figures in the builder. Edit their data/labels in the builder; these markers do not claim to render diagram syntax from Markdown. Fenced code and unknown markers fail clearly. Body and figure labels are 11 points; US Letter, one column, one-inch margins. Source hyperlinks use absolute HTTPS URLs.

Inspect every rendered page after editing. Confirm three pages, caption accuracy, readable labels and no clipping. Build twice in the same recorded environment and compare hashes. Cross-platform identical bytes are not promised. Record final contributor approval against the exact PDF hash in the review ledger. A generated artifact is not proof of contributor approval or submission.

The builder now also creates FinSight-midpoint-evidence.pdf with the three complete supporting notes, and embeds their original Markdown files in the report. GitHub evidence URLs were verified but removed from reader-facing references because the repository is private. Public SEC hyperlinks remain. Heading typography uses Helvetica Bold; body remains 11-point Times with 13.5-point leading. Explicit [[roadmap]] renders the dated milestone table.
