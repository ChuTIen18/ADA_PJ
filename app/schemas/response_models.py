"""
Pydantic response models cho POST /api/simulate
Map 1-1 với bảng Response trong API_contract.md
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class Top10Item(BaseModel):
    ip: str = Field(..., description="Địa chỉ IP")
    true_count: int = Field(..., description="Số lần xuất hiện thực tế")
    estimate: int = Field(..., description="Số lần ước tính bởi CMS")
    is_elephant: bool = Field(..., description="IP này có phải Elephant không")


class RealMeta(BaseModel):
    """
    Chỉ có giá trị khi data_source == "real".
    Khi data_source == "synthetic", cả object này là None.
    """

    hot_threshold_percent: float = Field(
        ..., description="Ngưỡng % để xác định Elephant (VD: 0.05 = top 5%)"
    )
    total_unique_ips: int = Field(
        ..., description="Tổng số IP duy nhất trong dataset thực tế"
    )


class SimulationResponse(BaseModel):
    data_source: str = Field(..., description='"synthetic" hoặc "real"')
    algorithm: str = Field(..., description='"classic" hoặc "mixed"')
    elephant_detected: int = Field(
        ..., description="Số Elephant IP phát hiện đúng (nằm trong top estimate)"
    )
    elephant_total: int = Field(..., description="Tổng số Elephant IP thực tế")
    mice_avg_error: float = Field(
        ...,
        description=(
            "Lỗi ước tính trung bình của Mice IP (0.12 = 12%). "
            "Chỉ tính trên is_elephant=false: mean((estimate - true_count) / true_count)"
        ),
    )
    top10: List[Top10Item] = Field(
        ..., description="Danh sách 10 IP có estimate cao nhất"
    )
    real_meta: Optional[RealMeta] = Field(
        default=None,
        description='Chỉ có giá trị khi data_source="real", còn lại là null',
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "data_source": "synthetic",
                    "algorithm": "mixed",
                    "elephant_detected": 5,
                    "elephant_total": 5,
                    "mice_avg_error": 0.12,
                    "real_meta": None,
                    "top10": [
                        {
                            "ip": "10.0.0.1",
                            "true_count": 95283,
                            "estimate": 96100,
                            "is_elephant": True,
                        }
                    ],
                },
                {
                    "data_source": "real",
                    "algorithm": "classic",
                    "elephant_detected": 4,
                    "elephant_total": 6,
                    "mice_avg_error": 0.31,
                    "real_meta": {
                        "hot_threshold_percent": 0.05,
                        "total_unique_ips": 12483,
                    },
                    "top10": [
                        {
                            "ip": "203.0.113.5",
                            "true_count": 48201,
                            "estimate": 61500,
                            "is_elephant": True,
                        }
                    ],
                },
            ]
        }
