
"""
cms.py

Conservative Count-Min Sketch (Hypergraph version)

Theo rules.md:
- Một mảng counter dùng chung.
- Conservative Update:
    + Chỉ tăng các ô đang có giá trị nhỏ nhất.
- Query:
    + Trả về giá trị nhỏ nhất.
"""

from array import array

from .hash_utils import get_k_distinct_indices


class ConservativeCMS:
    """
    Conservative Count-Min Sketch sử dụng một bảng counter dùng chung.
    """

    def __init__(
        self,
        table_size: int,
        k: int,
        seed_base: int = 0,
    ):
        if table_size < k:
            raise ValueError(
                f"TABLE_TOO_SMALL_FOR_K: table_size ({table_size}) < k ({k})"
            )

        self.table_size = table_size
        self.k = k
        self.seed_base = seed_base

        # uint64
        self.table = array("Q", [0] * table_size)

    def insert(self, item: str) -> None:
        """
        Conservative Update.

        Chỉ tăng những counter có giá trị nhỏ nhất.
        """

        indices = get_k_distinct_indices(
            item=item,
            k=self.k,
            table_size=self.table_size,
            seed_base=self.seed_base,
        )

        min_value = min(self.table[idx] for idx in indices)

        for idx in indices:
            if self.table[idx] == min_value:
                self.table[idx] += 1

    def query(self, item: str) -> int:
        """
        Trả về estimate của item.
        """

        indices = get_k_distinct_indices(
            item=item,
            k=self.k,
            table_size=self.table_size,
            seed_base=self.seed_base,
        )

        return min(self.table[idx] for idx in indices)

    def memory_bytes(self) -> int:
        """
        Bộ nhớ sử dụng của bảng counter.

        Chỉ có 1 bảng nên KHÔNG nhân theo k.
        """

        return self.table_size * 8

