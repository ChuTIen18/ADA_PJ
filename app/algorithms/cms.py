from .hash_utils import hash_item


class CountMinSketch:

    def __init__(self, width: int, depth: int = 3):

        self.width = width
        self.depth = depth

        self.table = [
            [0] * width
            for _ in range(depth)
        ]

    def update(self, item: str, count: int = 1):

        for i in range(self.depth):

            index = hash_item(item, i, self.width)

            self.table[i][index] += count

    def query(self, item: str) -> int:

        values = []

        for i in range(self.depth):

            index = hash_item(item, i, self.width)

            values.append(self.table[i][index])

        return min(values)

    def display(self):

        print("\nCurrent Sketch\n")

        for row in self.table:
            print(row)
