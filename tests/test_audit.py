"""Tests for envoy.audit module."""

import os
import pytest
from pathlib import Path

from envoy.audit import log_event, read_events, clear_events


@pytest.fixture(autouse=True)
def set_audit_log(tmp_path, monkeypatch):
    log_file = tmp_path / "test_audit.log"
    monkeypatch.setenv("ENVOY_AUDIT_LOG", str(log_file))
    yield log_file


def test_log_and_read_single_event():
    log_event("encrypt", "dev.env")
    events = read_events()
    assert len(events) == 1
    assert events[0]["action"] == "encrypt"
    assert events[0]["target"] == "dev.env"
    assert "timestamp" in events[0]


def test_log_event_with_profile():
    log_event("push", "prod.env", profile="production")
    events = read_events()
    assert events[0]["profile"] == "production"


def test_log_event_with_extra():
    log_event("get", "staging.env", extra={"key": "DATABASE_URL"})
    events = read_events()
    assert events[0]["key"] == "DATABASE_URL"


def test_multiple_events_order():
    log_event("encrypt", "a.env")
    log_event("decrypt", "b.env")
    log_event("push", "c.env")
    events = read_events()
    assert len(events) == 3
    assert events[0]["action"] == "encrypt"
    assert events[2]["action"] == "push"


def test_read_events_limit():
    for i in range(5):
        log_event("show", f"env{i}.env")
    events = read_events(limit=3)
    assert len(events) == 3
    assert events[-1]["target"] == "env4.env"


def test_read_events_empty_log():
    events = read_events()
    assert events == []


def test_clear_events():
    log_event("decrypt", "dev.env")
    assert len(read_events()) == 1
    clear_events()
    assert read_events() == []
