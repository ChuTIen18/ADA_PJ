"""
backend/app/schemas/request_models.py
Sở hữu: C (Hiếu)
Khớp 100% với rules.md §3.4 (contract) và §4.4 (validation tối thiểu).
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator


class SimulationRequest(BaseModel):
    # --- Trường chung (mọi data_source) ---
    data_source: Literal["synthetic", "real"] = Field(
        ..., description="Nguồn dữ liệu: 'synthetic' (giả lập) hoặc 'real' (NASA log)"
    )
    seed: Optional[int] = Field(
        None, description="Seed dùng chung cho cả classic+mixed. None = random, server tự sinh và trả lại trong response."
    )
    table_size: int = Field(..., description="Kích thước MỘT mảng counter dùng chung (n trong bài báo)")
    classic_k: int = Field(3, description="Số hash function cho CMS classic")
    mixed_k_hot: int = Field(2, description="Số hash function cho phần tử hot trong Mixed CMS")
    mixed_k_cold: int = Field(5, description="Số hash function cho phần tử cold trong Mixed CMS")

    # --- Trường riêng khi data_source = "synthetic" ---
    n_hot: Optional[int] = Field(None, description="Số phần tử hot phân biệt (bắt buộc nếu synthetic)")
    n_cold: Optional[int] = Field(None, description="Số phần tử cold phân biệt (bắt buộc nếu synthetic)")
    gap_factor: Optional[float] = Field(
        None,
        description="G: tỉ lệ xác suất xuất hiện của 1 phần tử hot so với 1 phần tử cold (per-element, "
        "KHÔNG phải ph/pc trực tiếp — xem rules.md §2). Bắt buộc nếu synthetic.",
    )
    total_packets: Optional[int] = Field(None, description="Tổng số packet trong stream (bắt buộc nếu synthetic)")

    # --- Trường riêng khi data_source = "real" ---
    hot_threshold_percent: float = Field(
        1.0, description="Top X% host tần suất cao nhất được gắn is_hot=true (chỉ dùng khi data_source='real')"
    )

    @model_validator(mode="after")
    def validate_by_data_source(self) -> "SimulationRequest":
        # 1. Bắt buộc theo nhánh data_source (thay vì if/else rải rác ở route)
        if self.data_source == "synthetic":
            missing = [
                name
                for name, value in (
                    ("n_hot", self.n_hot),
                    ("n_cold", self.n_cold),
                    ("gap_factor", self.gap_factor),
                    ("total_packets", self.total_packets),
                )
                if value is None
            ]
            if missing:
                raise ValueError(
                    f"data_source='synthetic' yêu cầu các field: {', '.join(missing)}"
                )
            if self.n_hot <= 0 or self.n_cold <= 0:
                raise ValueError("n_hot và n_cold phải > 0")
            if self.gap_factor <= 1:
                raise ValueError("gap_factor phải > 1")
            if self.total_packets <= 0:
                raise ValueError("total_packets phải > 0")

        if self.data_source == "real":
            if not (0 < self.hot_threshold_percent < 100):
                raise ValueError("hot_threshold_percent phải nằm trong khoảng (0, 100)")

        # 2. Validate chung (rules.md §4.4)
        if self.table_size <= 0:
            raise ValueError("table_size phải > 0")
        max_k = max(self.classic_k, self.mixed_k_hot, self.mixed_k_cold)
        if self.table_size <= max_k:
            raise ValueError(f"table_size phải > {max_k} (max của classic_k/mixed_k_hot/mixed_k_cold)")

        return self
