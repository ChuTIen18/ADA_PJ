import hashlib


def hash_item(item: str, seed: int, width: int) -> int:
    """
    Băm một phần tử về khoảng [0, width-1]

    Parameters
    ----------
    item : str
        Phần tử cần băm

    seed : int
        Seed tạo hàm băm khác nhau

    width : int
        Số cột của Sketch

    Returns
    -------
    int
        Chỉ số cột
    """

    value = f"{seed}-{item}"

    digest = hashlib.sha256(value.encode()).hexdigest()

    return int(digest, 16) % width
