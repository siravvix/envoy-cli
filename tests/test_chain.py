"""Tests for envoy.chain module."""

import pytest
from envoy.chain import load_chain, chain_sources, chain_conflicts, format_chain_sources


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / "base.env"
    base.write_text("APP=myapp\nDEBUG=false\nDB_HOST=localhost\n")

    override = tmp_path / "override.env"
    override.write_text("DEBUG=true\nNEW_KEY=hello\n")

    empty = tmp_path / "empty.env"
    empty.write_text("")

    return {"base": str(base), "override": str(override), "empty": str(empty)}


def test_load_chain_single_file(env_files):
    result = load_chain([env_files["base"]])
    assert result["APP"] == "myapp"
    assert result["DEBUG"] == "false"


def test_load_chain_override_order(env_files):
    result = load_chain([env_files["base"], env_files["override"]])
    assert result["DEBUG"] == "true"  # override wins
    assert result["APP"] == "myapp"   # from base
    assert result["NEW_KEY"] == "hello"


def test_load_chain_base_not_overridden(env_files):
    result = load_chain([env_files["override"], env_files["base"]])
    assert result["DEBUG"] == "false"  # base wins when listed last


def test_load_chain_empty_file(env_files):
    result = load_chain([env_files["base"], env_files["empty"]])
    assert result["APP"] == "myapp"


def test_load_chain_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_chain([str(tmp_path / "nonexistent.env")])


def test_chain_sources_correct_source(env_files):
    sources = chain_sources([env_files["base"], env_files["override"]])
    source_map = {k: (v, s) for k, v, s in sources}
    assert source_map["DEBUG"][0] == "true"
    assert source_map["DEBUG"][1] == env_files["override"]
    assert source_map["APP"][1] == env_files["base"]


def test_chain_conflicts_detects_difference(env_files):
    conflicts = chain_conflicts([env_files["base"], env_files["override"]])
    assert "DEBUG" in conflicts
    values = [v for v, _ in conflicts["DEBUG"]]
    assert "false" in values
    assert "true" in values


def test_chain_conflicts_no_conflict_when_same(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("KEY=value\n")
    b.write_text("KEY=value\n")
    conflicts = chain_conflicts([str(a), str(b)])
    assert "KEY" not in conflicts


def test_format_chain_sources_empty():
    assert format_chain_sources([]) == "(empty)"


def test_format_chain_sources_includes_path(env_files):
    sources = chain_sources([env_files["base"]])
    output = format_chain_sources(sources)
    assert env_files["base"] in output
    assert "APP=myapp" in output
