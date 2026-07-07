
"""
cms_mixed.py

Mixed Hypergraph Conservative Count-Min Sketch

Theo bài báo:
- Hot elements dùng k_hot hash functions.
- Cold elements dùng k_cold hash functions.
- Chỉ có MỘT bảng counter dùng chung.
"""

from array import array

from .hash_utils import get_k_distinct_indices


class MixedHypergraphCMS:
    """
    Mixed Hypergraph Count-Min Sketch.

    Hot và Cold dùng số hash function khác nhau nhưng
    cùng chia sẻ một bảng counter.
    """

    def __init__(
        self,
        table_size: int,
        k_hot: int,
        k_cold: int,
        hot_seed_base: int = 0,
        cold_seed_base: int = 100,
    ):
        if table_size < max(k_hot, k_cold):
            raise ValueError(
                f"TABLE_TOO_SMALL_FOR_K: table_size ({table_size}) "
                f"< max(k_hot, k_cold)"
            )

        self.table_size = table_size

        self.k_hot = k_hot
        self.k_cold = k_cold

        self.hot_seed_base = hot_seed_base
        self.cold_seed_base = cold_seed_base

        # Một bảng counter dùng chung
        self.table = array("Q", [0] * table_size)

    def insert(self, item: str, is_hot: bool) -> None:
        """
        Conservative Update.

        Hot dùng k_hot.
        Cold dùng k_cold.
        """

        if is_hot:
            k = self.k_hot
            seed_base = self.hot_seed_base
        else:
            k = self.k_cold
            seed_base = self.cold_seed_base

        indices = get_k_distinct_indices(
            item=item,
            k=k,
            table_size=self.table_size,
            seed_base=seed_base,
        )

        min_value = min(self.table[idx] for idx in indices)

        for idx in indices:
            if self.table[idx] == min_value:
                self.table[idx] += 1

    def query(self, item: str, is_hot: bool) -> int:
        """
        Query phải truyền đúng is_hot giống lúc insert.

        Nếu query sai is_hot thì sẽ dùng sai k và sai tập
        counter nên kết quả không còn ý nghĩa.
        """

        if is_hot:
            k = self.k_hot
            seed_base = self.hot_seed_base
        else:
            k = self.k_cold
            seed_base = self.cold_seed_base

        indices = get_k_distinct_indices(
            item=item,
            k=k,
            table_size=self.table_size,
            seed_base=seed_base,
        )

        return min(self.table[idx] for idx in indices)

    def memory_bytes(self) -> int:
        """
        Bộ nhớ của sketch.

        Chỉ có một bảng counter nên không nhân theo k.
        """

        return self.table_size * 8

