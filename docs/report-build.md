# Rebuild and inspect the midpoint report

The editable source is `docs/midterm-draft.md`; `scripts/build_midterm_report.py`
renders its five sections, results table and architecture diagram. The PDF is a
review draft until contributor claims and the outstanding gates in #3 are reviewed.
Do not interpret the existence of a PDF as evidence of submission or human review.

From the repository root on Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install -e '.[report]'
.\.venv\Scripts\python.exe -m scripts.build_midterm_report
```

On other platforms use the corresponding environment's Python executable. Default
output is `docs/midterm-report.pdf`; `--source` and `--output` override the paths.
No snapshot or network access is required to render the documented report.
Rendering the documented results is separate from reproducing the experiment:
see `docs/evidence/nick-reproduction.md` and `docs/evidence/yahoo-pilot.md`.

The builder uses US Letter, one column, 72-point margins and 11-point Times body
text. The title is 14 points; diagram labels are 8 points. Inspect every page for
clipping, table readability, heading placement, missing glyphs and 2–3 page length
after any source change. Keep evidence limitations and pending review visible.

The final review draft is three pages, with explicit page breaks before Methods
and Preliminary Results. PDF timestamps and document IDs are invariant so the
same source and pinned renderer produce the same bytes. Rebuild twice and compare
SHA-256 values before recording the review version. Vector figure labels are
smaller than body text; inspect their legibility at normal zoom.

Requirements, proposal and example PDFs were read locally. The example supplies
structure only; its dataset and measured findings are unrelated to FinSight.
