"""
backend/app/main.py
Sở hữu: C (Hiếu)
3 route theo rules.md §3.2-3.4. Route chỉ gọi simulation_service, KHÔNG chứa
logic thuật toán/data trực tiếp (ai_agents.md, phần C).
"""

import os
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas.request_models import SimulationRequest
from app.schemas.response_models import PresetsResponse, SimulationResponse

app = FastAPI(
    title="Elephant Mice CMS Demo API",
    description="Backend phục vụ so sánh CMS classic k=3 vs Mixed Hypergraph CMS k=(2,5) — Fusy & Kucherov, SPIRE 2023",
    version="1.0.0",
)

# CORS: đọc origin của frontend từ env, KHÔNG hardcode (rules.md §3.1, ai_agents.md checklist C)
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5500")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Custom exception để tầng service raise, map thẳng sang khuôn lỗi rules.md §3.5
# ---------------------------------------------------------------------------

class AppError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=400, content={"error": {"code": exc.code, "message": exc.message}})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # model_validator trong request_models.py raise ValueError -> FastAPI bọc thành đây.
    # Map về đúng khuôn INVALID_PARAMS thay vì để lộ format 422 mặc định của FastAPI.
    first_error = exc.errors()[0]
    message = first_error.get("msg", "Invalid params")
    return JSONResponse(status_code=400, content={"error": {"code": "INVALID_PARAMS", "message": message}})


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500, content={"error": {"code": "INTERNAL_ERROR", "message": str(exc)}}
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/presets", response_model=PresetsResponse)
async def get_presets():
    """
    Trả 3 preset chuẩn (rules.md §3.3). TODO: khi presets.py của D (Tiên) sẵn sàng,
    import trực tiếp từ đó thay vì hardcode ở đây, để tránh 2 nguồn số liệu lệch nhau.
    """
    return {
        "presets": [
            {
                "id": "main",
                "label": "Trình diễn chính (dễ thấy khác biệt)",
                "params": {"n_hot": 5, "n_cold": 9995, "gap_factor": 100, "table_size": 5000, "total_packets": 500000},
            },
            {
                "id": "paper_faithful",
                "label": "Bám sát Figure 5 của paper",
                "params": {"n_hot": 300, "n_cold": 5000, "gap_factor": 20, "table_size": 1000, "total_packets": 500000},
            },
            {
                "id": "stress",
                "label": "Stress / vùng bão hoà (Figure 6)",
                "params": {"n_hot": 100, "n_cold": 900, "gap_factor": 10, "table_size": 1000, "total_packets": 500000},
            },
        ]
    }


@app.post("/api/simulate", response_model=SimulationResponse)
async def simulate(payload: SimulationRequest):
    """
    Nhận tham số đã validate (data_source rẽ nhánh ở request_models.py) →
    gọi simulation_service (A+D) → trả kết quả classic+mixed cùng 1 stream/seed.
    """
    # TODO (touch point A+D): thay mock dưới đây bằng
    #   from app.services.simulation_service import run_simulation
    #   return run_simulation(payload)
    # simulation_service nên raise AppError("TABLE_TOO_SMALL_FOR_K", ...) hoặc
    # AppError("DATASET_NOT_FOUND", ...) khi cần, để handler ở trên map đúng khuôn.

    used_seed = payload.seed if payload.seed is not None else 42

    mock_result_classic = {
        "k": payload.classic_k,
        "elephant_detected": 3,
        "elephant_total": 5,
        "mice_avg_error": 3.4,
        "top10": [{"ip": "10.0.0.1", "true_count": 95283, "estimate": 96100, "is_hot": True}],
    }
    mock_result_mixed = {
        "k_hot": payload.mixed_k_hot,
        "k_cold": payload.mixed_k_cold,
        "elephant_detected": 5,
        "elephant_total": 5,
        "mice_avg_error": 0.12,
        "top10": [{"ip": "10.0.0.1", "true_count": 95283, "estimate": 95400, "is_hot": True}],
    }

    return {
        "run_id": uuid.uuid4().hex[:8],
        "data_source": payload.data_source,
        "seed": used_seed,
        "params_used": payload.model_dump(),
        "results": {"classic": mock_result_classic, "mixed": mock_result_mixed},
    }
