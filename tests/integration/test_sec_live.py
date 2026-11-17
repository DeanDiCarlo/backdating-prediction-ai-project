"""Opt-in SEC network check; excluded without explicit credentials and switch."""
from datetime import date
import os

import pytest

from src.genai.sec_ingestion import SecClient, decision_cutoff, eligible_filings

pytestmark = pytest.mark.integration


def test_live_nvda_metadata():
    if os.environ.get("RUN_SEC_INTEGRATION") != "1" or not os.environ.get("SEC_USER_AGENT"):
        pytest.skip("Set RUN_SEC_INTEGRATION=1 and a real SEC_USER_AGENT")
    found = eligible_filings(SecClient(os.environ["SEC_USER_AGENT"]), "NVDA",
                             decision_cutoff(date(2022, 1, 3)), {"10-K", "10-Q"})
    assert found
    assert all(f.first_eligible_at for f in found)
