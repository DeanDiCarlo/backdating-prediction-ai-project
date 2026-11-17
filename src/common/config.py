"""Validated experiment settings shared by the command-line pipeline."""
from __future__ import annotations

from datetime import date, time
from pathlib import Path

import yaml


def load_config(path: Path) -> dict:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("Experiment configuration must be a YAML mapping")
    pilot, experiment, sec, retrieval = (data.get(key) for key in ("pilot", "experiment", "sec", "retrieval"))
    if not all(isinstance(part, dict) for part in (pilot, experiment, sec, retrieval)):
        raise ValueError("Missing pilot, experiment, sec, or retrieval configuration")
    start, end = date.fromisoformat(str(experiment["start_date"])), date.fromisoformat(str(experiment["end_date"]))
    decision = date.fromisoformat(str(pilot["decision_date"]))
    time.fromisoformat(str(pilot["decision_time"]))
    if not start <= decision <= end:
        raise ValueError("Pilot decision must be within the experiment date range")
    if experiment["trading_calendar"] != "XNYS" or pilot["decision_timezone"] != "America/New_York":
        raise ValueError("Only XNYS and America/New_York are currently supported")
    if int(experiment["feature_lookback_months"]) < 1 or int(experiment["forward_target_months"]) < 1:
        raise ValueError("Feature lookback and forward horizon must be positive")
    if int(retrieval["overlap_words"]) < 0 or int(retrieval["chunk_words"]) <= int(retrieval["overlap_words"]):
        raise ValueError("Chunk overlap must be nonnegative and smaller than chunk size")
    if float(sec["request_delay_seconds"]) < 0.2:
        raise ValueError("SEC request delay must be at least 0.2 seconds")
    return data
