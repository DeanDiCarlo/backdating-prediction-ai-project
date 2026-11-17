from pathlib import Path

import pytest

pytest.importorskip('reportlab')
pymupdf = pytest.importorskip('pymupdf')
from scripts.build_midterm_report import build


def test_source_content_and_absolute_links_reach_pdf(tmp_path):
    source = tmp_path / 'source.md'
    source.write_text('# Test\n\nA revised scientific claim.\n\n[Source](https://www.sec.gov/)\n\n[[architecture]]\n')
    output = tmp_path / 'report.pdf'
    build(source, output)
    with pymupdf.open(output) as document:
        text = ''.join(page.get_text() for page in document)
        assert 'A revised scientific claim.' in text
        assert 'Executed: prices' in text
        assert document[0].get_links()[0]['uri'] == 'https://www.sec.gov/'


@pytest.mark.parametrize('unsupported', ['```text\nignored content\n```', '[[unknown]]'])
def test_unsupported_content_fails_instead_of_silent_substitution(tmp_path, unsupported):
    source = tmp_path / 'source.md'
    source.write_text(unsupported)
    with pytest.raises(ValueError):
        build(source, tmp_path / 'report.pdf')
