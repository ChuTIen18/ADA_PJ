# ai_agents.md — Hướng dẫn chi tiết theo từng vai trò

> Đọc `rules.md` **trước** file này — mọi tên biến/API/thuật ngữ dưới đây phải khớp 100% với `rules.md`. Nếu bạn (người hoặc AI coding assistant) chỉ được giao code 1 file cụ thể, vẫn nên đọc nguyên phần vai trò của mình + mục 6 (Touch point) để biết mình phụ thuộc/ảnh hưởng ai.
>
> Mỗi mục dưới đây gồm: **Nhiệm vụ** → **File sở hữu** → **Chi tiết từng file (input/output, function signature mẫu)** → **Edge case phải xử lý** → **Checklist Done** → **Phụ thuộc/ảnh hưởng ai**.
> Function signature ở đây là **mẫu tối thiểu bắt buộc giữ đúng tên/tham số** — được phép thêm hàm phụ trợ private, không được đổi tên/tham số của hàm public đã liệt kê mà không cập nhật `requirement.md`.

---

## [A] Khoa — Thuật toán

### Nhiệm vụ
Cài đặt đúng Conservative Count-Min theo mô hình **hypergraph 1 mảng dùng chung** (xem `rules.md §0.2`) — cả bản classic (k đồng nhất) và bản Mixed (k khác nhau theo hot/cold). Đây là phần lõi học thuật của project — sai phần này thì toàn bộ số liệu vô nghĩa.

### File sở hữu
`backend/app/algorithms/hash_utils.py`, `cms.py`, `cms_mixed.py`, `backend/app/utils/metrics.py`, `backend/tests/test_cms.py`, `test_cms_mixed.py`

### `hash_utils.py`
```python
def get_k_distinct_indices(item: str, k: int, table_size: int, seed_base: int = 0) -> list[int]:
    """
    Trả về đúng k chỉ số PHÂN BIỆT trong [0, table_size), dùng mmh3 với
    seed lần lượt seed_base, seed_base+1, ..., seed_base+k-1.
    Nếu 2 seed cho cùng 1 chỉ số (trùng) → thử seed_base + 1000 + i để lấy đủ k
    chỉ số khác nhau (retry, không được trả về < k phần tử).
    Raises ValueError nếu table_size < k (không thể có k chỉ số phân biệt).
    """
```
Dùng `mmh3.hash(item, seed=seed) % table_size`.

### `cms.py`
```python
class ConservativeCMS:
    def __init__(self, table_size: int, k: int, seed_base: int = 0): ...
    def insert(self, item: str) -> None:
        """Tăng CHỈ ô nhỏ nhất trong k ô gán cho item (nếu nhiều ô cùng bằng min, tăng tất cả các ô đang bằng min đó — đúng định nghĩa conservative update)."""
    def query(self, item: str) -> int:
        """Trả về min(k ô gán cho item)."""
    def memory_bytes(self) -> int:
        """table_size * 8 (counter kiểu uint64/Python int trong mảng array('Q', ...) hoặc numpy uint64). KHÔNG nhân theo k."""
```

### `cms_mixed.py`
```python
class MixedHypergraphCMS:
    def __init__(self, table_size: int, k_hot: int, k_cold: int,
                 hot_seed_base: int = 0, cold_seed_base: int = 100): ...
    def insert(self, item: str, is_hot: bool) -> None: ...
    def query(self, item: str, is_hot: bool) -> int:
        """QUAN TRỌNG: phải truyền đúng is_hot lúc query giống lúc insert,
        vì k (và do đó tập ô được gán) khác nhau giữa hot/cold. Query sai
        is_hot -> query nhầm k, ra kết quả vô nghĩa."""
```
`hot_seed_base`/`cold_seed_base` mặc định lệch nhau (0 vs 100) để tránh 2 nhóm dùng trùng dải seed — xem `rules.md §4.1`.

### `metrics.py`
```python
def relative_error(estimate: int, true_count: int) -> float | None:
    """(estimate-true_count)/true_count. Trả None nếu true_count == 0 (loại khỏi thống kê trung bình, không raise exception làm sập cả run)."""

def average_error(records: list[dict], only_hot: bool | None) -> float:
    """only_hot=True: chỉ tính trên record có is_hot=True.
    only_hot=False: chỉ tính is_hot=False (đây là 'mice_avg_error' trong response).
    only_hot=None: tính tất cả. Bỏ qua record có relative_error=None."""

def elephant_detection_rate(all_records_with_estimate: list[dict], top_n: int) -> tuple[int, int]:
    """Sort giảm dần theo estimate, lấy top_n, đếm bao nhiêu trong đó thực sự is_hot=True.
    Trả (số đúng, top_n) = (elephant_detected, elephant_total)."""
```

### Edge case phải xử lý
- `table_size` nhỏ hơn k → raise lỗi rõ ràng, để C map sang `TABLE_TOO_SMALL_FOR_K` (rules.md §3.5), không để lỗi generic.
- `true_count = 0` (phần tử có trong danh sách nhưng chưa từng xuất hiện trong stream do random) → không chia cho 0.
- Nhiều ô cùng giá trị min khi insert → tăng **tất cả** ô đang = min (đúng conservative update, không chỉ tăng 1 ô ngẫu nhiên trong số đó).
- 10 triệu packet: tránh tạo object Python nặng trong vòng lặp insert (không dùng list/dict lồng nhau mỗi lần insert) — dùng cấu trúc mảng phẳng (`array` module hoặc `numpy`).

### Checklist Done
- [ ] `pytest backend/tests/test_cms.py test_cms_mixed.py` pass 100%
- [ ] Có test riêng xác nhận conservative update chỉ tăng min-ô (không tăng hết k ô)
- [ ] Có test xác nhận Mixed dùng đúng k_hot khi is_hot=True và k_cold khi is_hot=False
- [ ] Có test `memory_bytes()` trả đúng `table_size * 8`, không phụ thuộc k
- [ ] Benchmark thời gian insert 500,000 packet < ~3 giây (ghi số đo thật vào PR)

### Phụ thuộc / ảnh hưởng
- D (Tiên) gọi trực tiếp `ConservativeCMS`/`MixedHypergraphCMS` trong `simulation_service.py` — đổi signature phải báo D+C ngay.
- Không phụ thuộc ai để bắt đầu — có thể code + test độc lập với `pytest` thuần, không cần chờ FastAPI (đúng như kế hoạch cũ).

---

## [B] Mai — Frontend

### Nhiệm vụ
Dựng giao diện web tĩnh (không framework, không build step) thể hiện đúng luồng trong `Kịch bản DEMO`: 2 nút chọn nguồn data → chạy classic → chạy mixed → tab so sánh.

### File sở hữu
`frontend/index.html`, `frontend/css/style.css`, `frontend/js/app.js`, `frontend/js/charts.js`

### `app.js`
```javascript
let lastResponse = null; // cache kết quả /api/simulate gần nhất, tránh gọi lại API khi chỉ chuyển tab hiển thị

async function runSimulation(dataSource, params) {
  // Gọi api.js (do C viết) — 1 LẦN duy nhất cho cả classic+mixed (xem rules.md §3.4)
  // Lưu vào lastResponse, KHÔNG gọi lại API khi user bấm nút "Run mixed" ngay sau "Run classic"
}

function showClassicPanel() {
  // Đọc từ lastResponse.results.classic, gọi charts.js
}

function showMixedPanel() {
  // Đọc từ lastResponse.results.mixed, gọi charts.js
}

function showComparisonTab() {
  // Join top10 của classic và mixed theo `ip` (cùng thứ tự vì cùng seed), vẽ 2 cột song song
}
```

### `charts.js`
```javascript
function renderErrorBarChart(canvasId, classicMiceError, mixedMiceError) { /* Chart.js bar chart */ }
function renderDetectionBarChart(canvasId, classicDetected, classicTotal, mixedDetected, mixedTotal) { }
function renderTop10Table(containerId, top10Array, options = {}) { }
```

### Lưu ý UI (theo đúng `Kịch bản DEMO`)
- Luôn hiển thị rõ nhãn "Đang xem: Data giả lập" hoặc "Data thực tế" (field `data_source` trong response).
- Nhãn hiển thị dùng "Elephant/Mice" (thân thiện người xem) — nhưng đọc field `is_hot` từ JSON, không phải field tên khác.
- Chỉ ra trực quan IP nào bị "nhận sai" (Mice có estimate cao bất thường do va chạm hash) — có thể highlight màu đỏ trong bảng top10 nếu `estimate` lệch `true_count` quá X% (X có thể để cấu hình, đề xuất 50%).
- Trước khi có backend thật: import `mock_data.js` (do E viết) thay cho gọi API thật — đổi 1 dòng import sang `api.js` khi backend sẵn sàng (không sửa code UI khác).

### Checklist Done
- [ ] Chạy được hoàn toàn với `mock_data.js`, không cần backend
- [ ] 2 nút chọn nguồn data + progressive reveal (Run classic → Run mixed) đúng luồng kịch bản
- [ ] Tab "So sánh" hiển thị song song 2 cột như mô tả Bước trình bày 4
- [ ] Responsive tối thiểu (không vỡ layout khi chiếu màn hình lớn lúc thuyết trình)
- [ ] Đã swap `mock_data.js` → `api.js` thật và test lại toàn bộ luồng

### Phụ thuộc / ảnh hưởng
- Phụ thuộc E để có `mock_data.js` đúng schema `rules.md §3.4` ngay từ đầu.
- Phụ thuộc C để có `api.js` thật khi tới giai đoạn nối backend — **không tự viết fetch logic** (rules.md/README đã quy định `api.js` do C sở hữu dù nằm trong `frontend/js/`).

---

## [C] Hiếu — Kết nối Backend–Frontend

### Nhiệm vụ
Là người **duy nhất động vào cả 2 thư mục** `backend/` và `frontend/js/api.js`. Chốt và giữ đúng API contract (`rules.md §3`) xuyên suốt.

### File sở hữu
`backend/app/main.py`, `backend/app/schemas/request_models.py`, `response_models.py`, `frontend/js/api.js`, `backend/requirements.txt`, `backend/Dockerfile`, `README.md`

### `request_models.py`
```python
from pydantic import BaseModel, model_validator
from typing import Literal, Optional

class SimulationRequest(BaseModel):
    data_source: Literal["synthetic", "real"]
    seed: Optional[int] = None
    table_size: int
    classic_k: int = 3
    mixed_k_hot: int = 2
    mixed_k_cold: int = 5
    # synthetic-only
    n_hot: Optional[int] = None
    n_cold: Optional[int] = None
    gap_factor: Optional[float] = None
    total_packets: Optional[int] = None
    # real-only
    hot_threshold_percent: Optional[float] = 1.0

    @model_validator(mode="after")
    def check_mode_fields(self):
        if self.data_source == "synthetic":
            missing = [f for f in ("n_hot", "n_cold", "gap_factor", "total_packets") if getattr(self, f) is None]
            if missing:
                raise ValueError(f"Thiếu field bắt buộc cho synthetic: {missing}")
        return self
```

### `response_models.py`
```python
class AlgorithmResult(BaseModel):
    elephant_detected: int
    elephant_total: int
    mice_avg_error: float
    top10: list[dict]  # {ip, true_count, estimate, is_hot}

class SimulationResponse(BaseModel):
    run_id: str
    data_source: str
    seed: int
    params_used: dict
    results: dict  # {"classic": AlgorithmResult, "mixed": AlgorithmResult}
```

### `main.py`
```python
# FastAPI app, CORS middleware (allow origin = frontend URL, đọc từ config/env, không hardcode)
# Routes: GET /api/health, GET /api/presets, POST /api/simulate
# Route chỉ gọi simulation_service, KHÔNG chứa logic thuật toán/data trực tiếp trong route
```

### `frontend/js/api.js`
```javascript
const API_BASE = "http://localhost:8000/api"; // đổi qua config nếu deploy khác

async function callSimulate(payload) { /* fetch POST /api/simulate, throw Error có message rõ nếu response.error tồn tại */ }
async function fetchPresets() { /* fetch GET /api/presets */ }
```
B chỉ gọi `callSimulate()`/`fetchPresets()`, không tự viết `fetch()` trong `app.js`.

### Checklist Done
- [ ] `request_models.py`/`response_models.py` khớp 100% với `rules.md §3.4`
- [ ] Validate lỗi trả đúng khuôn `rules.md §3.5`, đúng mã lỗi
- [ ] CORS chạy được từ `frontend` mở qua static server (không lỗi CORS trên console)
- [ ] `README.md` có hướng dẫn chạy backend (`uvicorn`) + frontend (static server) từ đầu, ai clone repo cũng chạy được trong < 5 phút
- [ ] Test bằng Postman/curl so với đúng ví dụ trong `rules.md §3.4` trước khi báo nhóm

### Phụ thuộc / ảnh hưởng
- Chờ A (algorithms) + D (data/simulation_service) xong phần lõi mới nối được `main.py` thật — nhưng **chốt schema/contract ngay ngày 1**, không chờ.
- Đổi bất kỳ field nào trong request/response models → phải sửa `rules.md §3.4` trước, báo B + E cập nhật `mock_data.js`/`charts.js` theo.

---

## [D] Tiên — Data + hỗ trợ Backend

### Nhiệm vụ
Sinh dữ liệu giả lập đúng mô hình Step distribution (Section 3.2) cho phần backend của mình, và ráp cùng A vào `simulation_service.py`.

### File sở hữu
`backend/app/data/data_generator.py`, `presets.py`, `backend/app/services/simulation_service.py` (đồng sở hữu với A), `test_data_generator.py`

### Không thuộc phạm vi của D
`backend/app/data/real_loader.py` và toàn bộ nội dung trong `backend/app/data/real/` do Thịnh phụ trách.

### `data_generator.py`
```python
def generate_step_distribution(n_hot: int, n_cold: int, gap_factor: float,
                                total_packets: int, seed: int | None = None):
    """
    Generator (yield từng packet {"ip": str, "is_hot": bool}) theo đúng Step
    distribution Section 3.2: ph/pc = gap_factor * (n_hot/n_cold);
    ph = gap_factor*n_hot / (n_cold + gap_factor*n_hot);  # suy ra từ ph/pc và ph+pc=1
    pc = n_cold / (n_cold + gap_factor*n_hot)
    Mỗi packet: với xác suất ph rơi vào nhóm hot (chọn đều 1 trong n_hot hot-ip),
    ngược lại rơi vào nhóm cold (chọn đều 1 trong n_cold cold-ip).
    PHẢI dùng yield — không dựng list total_packets phần tử trong RAM.
    """

def build_ground_truth(stream_records: list[dict]) -> list[dict]:
    """Nhận list đã VẬT CHẤT HOÁ (hoặc consume generator 1 lần, lưu lại) →
    đếm true_count thật bằng Counter theo ip → trả [{"ip", "true_count", "is_hot"}].
    KHÔNG suy true_count từ ph/pc lý thuyết (xem rules.md §4.2)."""
```
Lưu ý triển khai: vì cần vừa insert vào CMS vừa đếm true_count, nên trong `simulation_service.py`, consume generator **một lần duy nhất**, vừa insert vào cả 2 sketch (classic + mixed) vừa cập nhật Counter cho true_count — tránh sinh stream 2 lần (tốn thời gian + có thể ra 2 stream khác nhau nếu quên seed).

### `real_loader.py`
```python
import re
NASA_LOG_PATTERN = re.compile(r'^(\S+) \S+ \S+ \[([^\]]+)\] "([^"]*)" (\d{3}) (\S+)$')

def parse_nasa_log_line(line: str) -> str | None:
    """Trả về host (group 1) nếu khớp pattern, None nếu không (dòng lỗi)."""

def load_and_aggregate(filepath: str, cache_path: str) -> dict[str, int]:
    """Nếu cache_path đã tồn tại → đọc cache, trả luôn (không parse lại).
    Nếu chưa → đọc từng dòng filepath, parse, đếm {host: count}, đếm số dòng
    skip (log lại số này), ghi ra cache_path (JSON), rồi trả kết quả."""

def label_hot_cold(counts: dict[str, int], hot_threshold_percent: float) -> list[dict]:
    """Sort giảm dần theo count. Top hot_threshold_percent% đầu -> is_hot=True.
    Trả [{"ip": host, "true_count": count, "is_hot": bool}, ...]."""
```

### `presets.py`
3 preset hằng số đúng theo `rules.md §3.3` (`main`, `paper_faithful`, `stress`) — xem giá trị cụ thể + lý do từng preset ở `project_ovr.md §7`. Không tự đổi số mà không cập nhật cả 2 file.

### Edge case phải xử lý
- File log thật có dòng thiếu field, ký tự lạ, dòng trống → skip + đếm, không crash toàn bộ pipeline.
- `hot_threshold_percent` quá nhỏ (0 host nào được chọn) hoặc quá lớn (gần hết là hot) → validate + trả lỗi rõ ràng thay vì chạy ra kết quả vô nghĩa.
- Dataset thật có thể có hàng chục nghìn host phân biệt — cache bắt buộc, không parse lại mỗi request.

### Checklist Done
- [ ] `generate_step_distribution` cho cùng seed → cho ra đúng cùng 1 stream ở 2 lần gọi khác nhau (test reproducibility)
- [ ] Tỉ lệ hot/cold thực tế sinh ra khớp `ph`/`pc` lý thuyết trong sai số thống kê chấp nhận được (test với số lượng packet đủ lớn)
- [ ] `real_loader` chạy được trên file NASA log thật đã tải, in ra được số dòng skip
- [ ] Cache hoạt động đúng (lần 2 gọi nhanh hơn hẳn lần 1)
- [ ] `presets.py` khớp chính xác `project_ovr.md §7`

### Phụ thuộc / ảnh hưởng
- Dùng trực tiếp class từ A (`cms.py`/`cms_mixed.py`) trong `simulation_service.py` — 2 người (A+D, cùng C khi ráp `main.py`) nên trao đổi trực tiếp trước khi viết `simulation_service.py`, đây là file dễ conflict nhất khi merge.
- Đổi preset → báo C (ảnh hưởng `/api/presets`) và E (ảnh hưởng `mock_data.js` nếu mock có dùng số preset).
- Phần `real_loader.py` và dữ liệu NASA logs chuyển sang Thịnh, nên D không chỉnh nhánh `real/` khi không được giao lại.

---

## [E] Mai — Data + hỗ trợ Frontend (Mock data)

### Nhiệm vụ
Cho phép B code UI **độc lập, không chờ backend xong**, bằng cách tạo mock data đúng 100% schema đã chốt trong `rules.md §3.4`. Phần này do Mai phụ trách.

### File sở hữu
`frontend/js/mock_data.js`, `data/mock/sample_response.json`

```javascript
// mock_data.js
const MOCK_SIMULATE_RESPONSE_SYNTHETIC = { /* đúng schema rules.md §3.4, data_source: "synthetic" */ };
const MOCK_SIMULATE_RESPONSE_REAL = { /* đúng schema, data_source: "real" */ };
const MOCK_PRESETS_RESPONSE = { /* đúng schema GET /api/presets */ };
```

### Checklist Done
- [ ] `mock_data.js` render đúng và đẹp trên UI của B khi chưa có backend thật
- [ ] `sample_response.json` giống hệt cấu trúc `mock_data.js` (dùng cho test tự động nếu cần)
- [ ] Đã đối chiếu lại với `data_generator.py` thật của D — số liệu mock có hợp lý (không phải số bịa vô lý, vd elephant_detected > elephant_total) không

### Phụ thuộc / ảnh hưởng
- **Ngay khi C đổi schema trong `rules.md §3.4`, E phải cập nhật mock_data.js theo trong cùng ngày** — đây là điểm dễ bị "quên đồng bộ" nhất trong nhóm.
- Việc "làm slide cùng Tiên (D)" không thuộc phạm vi code — xem `project_ovr.md §9` (Timeline) cho mốc slide.

### Không thuộc phạm vi của E
E không phụ trách dữ liệu thật trong backend; toàn bộ `backend/app/data/real/` và `backend/app/data/real_loader.py` do Thịnh phụ trách.

---

## 6. Bảng đồng bộ chéo (Touch point) — đọc trước khi đổi bất kỳ field/API nào

| Nếu đổi... | Bắt buộc báo/đổi theo... |
|---|---|
| Field trong request/response (`rules.md §3.4`) | C (chủ schema) → B (UI đọc field) → E (mock_data.js) → D (nếu ảnh hưởng `params_used`) |
| Tên hàm/tham số public trong `cms.py`/`cms_mixed.py` | D (gọi trực tiếp trong `simulation_service.py`) |
| Giá trị preset (`presets.py`) | C (`/api/presets`), E (`mock_data.js` nếu có tham chiếu số preset), `project_ovr.md §7` |
| Port/CORS origin | C, B (nếu B tự chạy static server khác port mặc định) |
| Bất kỳ điều nào ở trên | Luôn cập nhật `requirement.md` (mục Changelog) trước khi merge vào `main` |

## 7. Slide (Tiên + Thịnh)
Không thuộc phạm vi code/AI-agent — mỗi người tự viết `slides/X_6x6.md` (folder `slides/` ở root, tách riêng khỏi `docs/` đã bỏ) theo mốc ở `project_ovr.md §9`, nhóm trưởng gom lại. File này không quản lý phần slide.
