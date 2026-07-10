"""
test_cms.py

Unit tests cho ConservativeCMS.
"""

import pytest

from app.algorithms.cms import ConservativeCMS


def test_init():
    cms = ConservativeCMS(
        table_size=100,
        k=3,
    )

    assert cms.table_size == 100
    assert cms.k == 3
    assert len(cms.table) == 100


def test_invalid_table_size():
    with pytest.raises(ValueError):
        ConservativeCMS(
            table_size=2,
            k=3,
        )


def test_query_empty():
    cms = ConservativeCMS(
        table_size=100,
        k=3,
    )

    assert cms.query("apple") == 0


def test_insert_once():
    cms = ConservativeCMS(
        table_size=100,
        k=3,
    )

    cms.insert("apple")

    assert cms.query("apple") == 1


def test_insert_multiple_times():
    cms = ConservativeCMS(
        table_size=100,
        k=3,
    )

    for _ in range(10):
        cms.insert("apple")

    assert cms.query("apple") == 10


def test_memory_bytes():
    cms = ConservativeCMS(
        table_size=5000,
        k=3,
    )

    assert cms.memory_bytes() == 5000 * 8


def test_conservative_update_only_updates_minimum():
    """
    Conservative Update:
    chỉ những counter nhỏ nhất mới được tăng.
    """

    cms = ConservativeCMS(
        table_size=100,
        k=3,
    )

    # insert nhiều lần để tạo trạng thái ổn định
    for _ in range(5):
        cms.insert("apple")

    estimate_before = cms.query("apple")

    cms.insert("apple")

    estimate_after = cms.query("apple")

    assert estimate_after == estimate_before + 1
