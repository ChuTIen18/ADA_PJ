from .hash_utils import hash_item


class MixedCMS:

    def __init__(self, width: int, min_depth=2, max_depth=5):

        self.width = width

        self.min_depth = min_depth

        self.max_depth = max_depth

        self.table = [
            [0] * width
            for _ in range(max_depth)
        ]

    def update(self, item: str, k: int):

        k = max(self.min_depth, min(k, self.max_depth))

        for i in range(k):

            index = hash_item(item, i, self.width)

            self.table[i][index] += 1

    def query(self, item: str, k: int):

        k = max(self.min_depth, min(k, self.max_depth))

        values = []

        for i in range(k):

            index = hash_item(item, i, self.width)

            values.append(self.table[i][index])

        return min(values)

    def display(self):

        print()

        for row in self.table:
            print(row)
