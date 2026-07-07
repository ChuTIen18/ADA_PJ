"""
Pydantic request models cho POST /api/simulate
Map 1-1 với bảng Request trong API_contract.md
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class AlgorithmType(str, Enum):
    classic = "classic"
    mixed = "mixed"


class DataSourceType(str, Enum):
    synthetic = "synthetic"
    real = "real"


class SimulationRequest(BaseModel):
    algorithm: AlgorithmType = Field(
        ..., description='"classic" (k=3) hoặc "mixed" (k_hot=2, k_cold=5)'
    )
    data_source: DataSourceType = Field(
        ..., description='"synthetic" (data giả lập) hoặc "real" (data thực tế)'
    )
    table_size: int = Field(
        ..., gt=0, description="Số ô đếm trong sketch (VD: 5000 ≈ 40KB RAM)"
    )

    # Các field dưới đây chỉ bắt buộc khi data_source == "synthetic"
    n_hot: Optional[int] = Field(
        default=None, gt=0, description="Số lượng Elephant IP (VD: 5)"
    )
    n_cold: Optional[int] = Field(
        default=None, gt=0, description="Số lượng Mice IP (VD: 9995)"
    )
    gap_factor: Optional[float] = Field(
        default=None, gt=1, description="Tỉ lệ tần suất hot/cold, G > 1 (VD: 100)"
    )
    total_packets: Optional[int] = Field(
        default=None, gt=0, description="Tổng số packet trong stream (VD: 10000000)"
    )

    @model_validator(mode="after")
    def validate_synthetic_fields(self) -> "SimulationRequest":
        """
        Theo contract: n_hot, n_cold, gap_factor, total_packets là bắt buộc
        khi data_source == "synthetic". Khi data_source == "real" thì bỏ qua.
        """
        if self.data_source == DataSourceType.synthetic:
            missing = [
                name
                for name, value in [
                    ("n_hot", self.n_hot),
                    ("n_cold", self.n_cold),
                    ("gap_factor", self.gap_factor),
                    ("total_packets", self.total_packets),
                ]
                if value is None
            ]
            if missing:
                raise ValueError(
                    f"Thiếu field bắt buộc khi data_source='synthetic': {', '.join(missing)}"
                )
        return self

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "algorithm": "mixed",
                    "data_source": "synthetic",
                    "n_hot": 5,
                    "n_cold": 9995,
                    "gap_factor": 100,
                    "table_size": 5000,
                    "total_packets": 10000000,
                },
                {
                    "algorithm": "classic",
                    "data_source": "real",
                    "table_size": 5000,
                },
            ]
        }
