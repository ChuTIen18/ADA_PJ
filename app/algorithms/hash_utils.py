
"""
hash_utils.py

Các hàm hỗ trợ băm cho Conservative Count-Min Sketch.

Theo rules.md:
- Dùng mmh3.hash(item, seed)
- Trả đúng k chỉ số PHÂN BIỆT
- Nếu trùng chỉ số thì retry bằng seed_base + 1000 + i
"""

from typing import List
import mmh3


def get_k_distinct_indices(
    item: str,
    k: int,
    table_size: int,
    seed_base: int = 0,
) -> List[int]:
    """
    Sinh đúng k chỉ số khác nhau trong [0, table_size).

    Parameters
    ----------
    item : str
        Phần tử cần hash.
    k : int
        Số chỉ số cần lấy.
    table_size : int
        Kích thước bảng counter.
    seed_base : int
        Seed bắt đầu.

    Returns
    -------
    List[int]
        Danh sách gồm đúng k chỉ số phân biệt.

    Raises
    ------
    ValueError
        Nếu table_size < k.
    """

    if table_size < k:
        raise ValueError(
            f"TABLE_TOO_SMALL_FOR_K: table_size ({table_size}) < k ({k})"
        )

    indices = []
    used = set()

    # Hash chính
    for i in range(k):
        seed = seed_base + i
        index = mmh3.hash(item, seed=seed, signed=False) % table_size

        # Nếu bị trùng thì retry
        retry = 0
        while index in used:
            retry_seed = seed_base + 1000 + retry
            index = mmh3.hash(
                item,
                seed=retry_seed,
                signed=False,
            ) % table_size
            retry += 1

        used.add(index)
        indices.append(index)

    return indices

