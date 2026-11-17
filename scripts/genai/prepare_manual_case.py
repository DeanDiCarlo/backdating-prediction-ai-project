"""Prepare short, verified source excerpts for a manual in-session model run."""
import hashlib
import json
from pathlib import Path

from scripts.genai.ingest_filings import ROOT


def main():
    record = json.loads((ROOT / 'data/processed/sec_filings/NVDA_0001045810-21-000010.json').read_text())
    excerpts = [
        ('E1', 'management_discussion', 'Graphics segment revenue increased by 29% in fiscal year 2021 compared to fiscal year 2020'),
        ('E2', 'management_discussion', 'Compute & Networking segment revenue increased by 109% in fiscal year 2021 compared to fiscal year 2020'),
        ('E3', 'risk_factors', 'We depend on third parties and their technology to manufacture, assemble, test and/or package our products, which reduces our control over product quantity and quality'),
    ]
    for _, section, text in excerpts:
        assert text in record['sections'][section], 'Excerpt must exactly match extracted source'
    prompt = (
        'Historical NVDA case study. Decision cutoff: 2022-01-03 09:30 America/New_York.\n'
        'Use ONLY excerpts E1-E3 below. Report two concise qualitative observations, each '
        'with evidence IDs. Describe reported results as historical, not a forecast. '
        'Do not use knowledge of later events or prices. Return JSON containing '
        'observations, qualitative_score, and abstentions. Set qualitative_score to null '
        'if these excerpts cannot establish a calibrated probability of outperforming SPY. '
        'Do not infer acquisition-free growth, valuation, future returns or investment advice.\n\n'
        + '\n'.join(f'{eid} [{section}]: {text}' for eid, section, text in excerpts)
    )
    out = ROOT / 'outputs/genai/manual-case'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'prompt.txt').write_text(prompt, encoding='utf-8')
    evidence = {**{k: record[k] for k in ['accession_number', 'source_url', 'filing_available_at', 'first_eligible_at']},
                'selection': 'manual, not similarity retrieval',
                'excerpts': [{'id': eid, 'section': section, 'text': text} for eid, section, text in excerpts],
                'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest()}
    (out / 'evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(prompt)
    print('PROMPT_SHA256', evidence['prompt_sha256'])


if __name__ == '__main__':
    main()
