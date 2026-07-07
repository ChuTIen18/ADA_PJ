"""
metrics.py

Các hàm đánh giá kết quả của Count-Min Sketch.
"""

from typing import Optional


def relative_error(
    estimate: int,
    true_count: int,
) -> Optional[float]:
    """
    Tính sai số tương đối.

    relative_error = (estimate - true_count) / true_count

    Returns
    -------
    float
        Sai số tương đối.

    None
        Nếu true_count = 0.
    """

    if true_count == 0:
        return None

    return (estimate - true_count) / true_count


def average_error(
    records: list[dict],
    only_hot: bool | None,
) -> float:
    """
    Tính sai số trung bình.

    Parameters
    ----------
    records :
        [
            {
                "estimate": ...,
                "true_count": ...,
                "is_hot": ...
            }
        ]

    only_hot
        True  -> chỉ tính hot
        False -> chỉ tính cold
        None  -> tính tất cả
    """

    errors = []

    for record in records:

        if only_hot is not None:
            if record["is_hot"] != only_hot:
                continue

        err = relative_error(
            record["estimate"],
            record["true_count"],
        )

        if err is not None:
            errors.append(err)

    if not errors:
        return 0.0

    return sum(errors) / len(errors)


def elephant_detection_rate(
    all_records_with_estimate: list[dict],
    top_n: int,
) -> tuple[int, int]:
    """
    Đánh giá khả năng phát hiện Elephant.

    Lấy top_n estimate lớn nhất.
    Đếm bao nhiêu phần tử thật sự là hot.

    Returns
    -------
    (elephant_detected, elephant_total)
    """

    sorted_records = sorted(
        all_records_with_estimate,
        key=lambda record: record["estimate"],
        reverse=True,
    )

    top_records = sorted_records[:top_n]

    detected = sum(
        1
        for record in top_records
        if record["is_hot"]
    )

    return detected, top_n
