"""Tests for envoy.group module."""

import pytest
from envoy.group import (
    group_by_prefix,
    group_by_labels,
    list_groups,
    format_groups,
    get_group,
)


SAMPLE_ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "envoy",
    "APP_DEBUG": "true",
    "SECRET": "abc123",
}


def test_group_by_prefix_basic():
    groups = group_by_prefix(SAMPLE_ENV)
    assert "DB" in groups
    assert "APP" in groups
    assert groups["DB"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert groups["APP"] == {"APP_NAME": "envoy", "APP_DEBUG": "true"}


def test_group_by_prefix_no_separator_goes_to_ungrouped():
    groups = group_by_prefix(SAMPLE_ENV)
    assert "__ungrouped__" in groups
    assert "SECRET" in groups["__ungrouped__"]


def test_group_by_prefix_custom_separator():
    env = {"DB.HOST": "localhost", "DB.PORT": "5432", "PLAIN": "val"}
    groups = group_by_prefix(env, separator=".")
    assert "DB" in groups
    assert "__ungrouped__" in groups
    assert groups["DB"]["DB.HOST"] == "localhost"


def test_group_by_labels_basic():
    labels = {
        "database": ["DB_HOST", "DB_PORT"],
        "app": ["APP_NAME", "APP_DEBUG"],
    }
    groups = group_by_labels(SAMPLE_ENV, labels)
    assert groups["database"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert groups["app"] == {"APP_NAME": "envoy", "APP_DEBUG": "true"}
    assert "__unlabeled__" in groups
    assert "SECRET" in groups["__unlabeled__"]


def test_group_by_labels_missing_key_ignored():
    labels = {"database": ["DB_HOST", "DB_MISSING"]}
    groups = group_by_labels(SAMPLE_ENV, labels)
    assert "DB_MISSING" not in groups["database"]
    assert "DB_HOST" in groups["database"]


def test_group_by_labels_no_unlabeled_when_all_assigned():
    labels = {
        "all": list(SAMPLE_ENV.keys())
    }
    groups = group_by_labels(SAMPLE_ENV, labels)
    assert "__unlabeled__" not in groups


def test_list_groups_sorted():
    groups = group_by_prefix(SAMPLE_ENV)
    names = list_groups(groups)
    assert names == sorted(names)


def test_format_groups_keys_only():
    groups = {"DB": {"DB_HOST": "localhost"}, "APP": {"APP_NAME": "envoy"}}
    output = format_groups(groups, show_values=False)
    assert "[APP]" in output
    assert "[DB]" in output
    assert "APP_NAME" in output
    assert "envoy" not in output


def test_format_groups_with_values():
    groups = {"DB": {"DB_HOST": "localhost"}}
    output = format_groups(groups, show_values=True)
    assert "DB_HOST=localhost" in output


def test_get_group_found():
    groups = {"DB": {"DB_HOST": "localhost"}}
    result = get_group(groups, "DB")
    assert result == {"DB_HOST": "localhost"}


def test_get_group_not_found():
    groups = {"DB": {"DB_HOST": "localhost"}}
    result = get_group(groups, "MISSING")
    assert result is None
