"""Tests for envoy/watch.py"""

import os
import time
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from envoy.watch import get_mtime, watch_file, make_print_callback


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return str(f)


def test_get_mtime_returns_float(env_file):
    mtime = get_mtime(env_file)
    assert isinstance(mtime, float)
    assert mtime > 0


def test_get_mtime_reflects_file_update(env_file):
    """Verify get_mtime returns an updated value after the file is touched."""
    before = get_mtime(env_file)
    new_time = before + 10
    os.utime(env_file, (new_time, new_time))
    after = get_mtime(env_file)
    assert after > before


def test_watch_file_raises_if_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        watch_file(str(tmp_path / "missing.env"), callback=lambda p: None, max_iterations=1)


def test_watch_file_no_change_no_callback(env_file):
    callback = MagicMock()
    # Run 3 iterations with no file modification
    watch_file(env_file, callback=callback, interval=0.01, max_iterations=3)
    callback.assert_not_called()


def test_watch_file_detects_change(env_file):
    callback = MagicMock()
    original_mtime = get_mtime(env_file)

    call_count = [0]

    def fake_sleep(seconds):
        call_count[0] += 1
        if call_count[0] == 1:
            # Simulate file change by updating mtime
            new_time = original_mtime + 10
            os.utime(env_file, (new_time, new_time))

    with patch("envoy.watch.time.sleep", side_effect=fake_sleep):
        watch_file(env_file, callback=callback, interval=0.01, max_iterations=2)

    callback.assert_called_once_with(env_file)


def test_watch_file_stops_if_deleted(tmp_path):
    f = tmp_path / ".env"
    f.write_text("A=1\n")
    path = str(f)

    call_count = [0]

    def fake_sleep(seconds):
        call_count[0] += 1
        if call_count[0] == 1:
            f.unlink()  # Delete the file

    callback = MagicMock()
    with patch("envoy.watch.time.sleep", side_effect=fake_sleep):
        # Should not raise even if file disappears mid-watch
        watch_file(path, callback=callback, interval=0.01, max_iterations=3)

    callback.assert_not_called()


def test_make_print_callback_output(capsys):
    cb = make_print_callback(label="updated")
    cb("/some/.env")
    captured = capsys.readouterr()
    assert "updated" in captured.out
    assert "/some/.env" in captured.out


def test_make_print_callback_default_label(capsys):
    """Verify make_print_callback works without an explicit label."""
    cb = make_print_callback()
    cb("/some/.env")
    captured = capsys.readouterr()
    assert "/some/.env" in captured.out
