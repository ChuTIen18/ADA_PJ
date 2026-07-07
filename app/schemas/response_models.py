"""
backend/app/schemas/response_models.py
Sở hữu: C (Hiếu)
Khớp 100% với rules.md §3.3 (presets), §3.4 (simulate response), §3.5 (error).
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# GET /api/presets  (rules.md §3.3)
# ---------------------------------------------------------------------------

class PresetParams(BaseModel):
    n_hot: int
    n_cold: int
    gap_factor: float
    table_size: int
    total_packets: int


class PresetItem(BaseModel):
    id: Literal["main", "paper_faithful", "stress"]
    label: str
    params: PresetParams


class PresetsResponse(BaseModel):
    presets: list[PresetItem]


# ---------------------------------------------------------------------------
# POST /api/simulate  (rules.md §3.4)
# ---------------------------------------------------------------------------

class Top10Item(BaseModel):
    ip: str = Field(..., description="Định danh phần tử (IP hoặc hostname với data thật)")
    true_count: int = Field(..., description="Đếm thật từ Counter trên chính stream đã sinh, không suy lý thuyết")
    estimate: int = Field(..., description="Giá trị CMS trả về khi query")
    is_hot: bool = Field(..., description="Field chuẩn DUY NHẤT — không dùng is_elephant trong code/schema")


class AlgorithmResult(BaseModel):
    # classic dùng "k"; mixed dùng "k_hot"/"k_cold" — để None field không dùng tới
    k: Optional[int] = Field(None, description="Chỉ có ở kết quả classic")
    k_hot: Optional[int] = Field(None, description="Chỉ có ở kết quả mixed")
    k_cold: Optional[int] = Field(None, description="Chỉ có ở kết quả mixed")

    elephant_detected: int = Field(..., description="Số hot IP thực sự nằm trong top-N ước lượng cao nhất")
    elephant_total: int = Field(..., description="N = elephant_total (thường = tổng số hot thật)")
    mice_avg_error: float = Field(..., description="relative_error trung bình, tính RIÊNG trên nhóm cold/mice")
    top10: list[Top10Item] = Field(..., description="Toàn bộ hot + một số cold đại diện, cùng tập IP giữa classic/mixed")


class SimulationResults(BaseModel):
    classic: AlgorithmResult
    mixed: AlgorithmResult


class SimulationResponse(BaseModel):
    run_id: str
    data_source: Literal["synthetic", "real"]
    seed: int = Field(..., description="Seed thực tế đã dùng (để tái lập), kể cả khi request không truyền")
    params_used: dict = Field(..., description="Toàn bộ tham số thực tế đã dùng, kể cả default đã áp")
    results: SimulationResults


# ---------------------------------------------------------------------------
# Response lỗi — khuôn chung (rules.md §3.5)
# ---------------------------------------------------------------------------

ErrorCode = Literal["INVALID_PARAMS", "DATASET_NOT_FOUND", "TABLE_TOO_SMALL_FOR_K", "INTERNAL_ERROR"]


class ErrorDetail(BaseModel):
    code: ErrorCode
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
