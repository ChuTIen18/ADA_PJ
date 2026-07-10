"""
test_cms_mixed.py

Unit tests cho MixedHypergraphCMS.
"""

import pytest

from app.algorithms.cms_mixed import MixedHypergraphCMS


def test_init():
    cms = MixedHypergraphCMS(
        table_size=100,
        k_hot=2,
        k_cold=5,
    )

    assert cms.table_size == 100
    assert cms.k_hot == 2
    assert cms.k_cold == 5
    assert len(cms.table) == 100


def test_invalid_table_size():
    with pytest.raises(ValueError):
        MixedHypergraphCMS(
            table_size=4,
            k_hot=2,
            k_cold=5,
        )


def test_query_empty_hot():
    cms = MixedHypergraphCMS(
        table_size=100,
        k_hot=2,
        k_cold=5,
    )

    assert cms.query("apple", True) == 0


def test_query_empty_cold():
    cms = MixedHypergraphCMS(
        table_size=100,
        k_hot=2,
        k_cold=5,
    )

    assert cms.query("apple", False) == 0


def test_insert_hot():
    cms = MixedHypergraphCMS(
        table_size=100,
        k_hot=2,
        k_cold=5,
    )

    cms.insert("apple", True)

    assert cms.query("apple", True) == 1


def test_insert_cold():
    cms = MixedHypergraphCMS(
        table_size=100,
        k_hot=2,
        k_cold=5,
    )

    cms.insert("banana", False)

    assert cms.query("banana", False) == 1


def test_insert_multiple_hot():
    cms = MixedHypergraphCMS(
        table_size=100,
        k_hot=2,
        k_cold=5,
    )

    for _ in range(10):
        cms.insert("apple", True)

    assert cms.query("apple", True) == 10


def test_insert_multiple_cold():
    cms = MixedHypergraphCMS(
        table_size=100,
        k_hot=2,
        k_cold=5,
    )

    for _ in range(10):
        cms.insert("banana", False)

    assert cms.query("banana", False) == 10


def test_memory_bytes():
    cms = MixedHypergraphCMS(
        table_size=5000,
        k_hot=2,
        k_cold=5,
    )

    assert cms.memory_bytes() == 5000 * 8
