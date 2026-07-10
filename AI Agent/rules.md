# rules.md — Luật chung của dự án (BẮT BUỘC đọc trước khi code)

> **File này là nguồn chân lý (single source of truth) cho mọi tên biến, tên hàm, contract API, và quy ước dùng chung.**
> Nếu code của bạn và file này khác nhau — **file này đúng, code sai, phải sửa code.**
> Nếu bạn thấy cần đổi một quy ước trong đây (vd đổi tên field), **không tự đổi âm thầm** — cập nhật `requirement.md` trước (mục Changelog), được duyệt rồi mới sửa file này và code liên quan. Xem quy trình đầy đủ ở `requirement.md`.

---

## 0. Bối cảnh bắt buộc phải biết trước khi code bất kỳ dòng nào

Demo này tái hiện thực nghiệm của bài báo:

> Éric Fusy, Gregory Kucherov. **"Count-min sketch with variable number of hash functions: an experimental study"**, SPIRE 2023. (arXiv: 2302.05245; PDF: xem `linkbaibao`)

Phần demo tương tác chỉ tái hiện **Section 3.2 (Step distribution / hot-cold elements)** — cụ thể là **Figure 5 (Section 3.2.2)**: so sánh CMS đồng nhất k=3 với **Mixed Hypergraph CMS k=(2,5)**. Section 3.1 (Uniform) và 3.3 (Zipf) **không** code demo tương tác — dùng số liệu/hình có sẵn trong bài báo cho báo cáo viết tay.

### 0.1 Quy tắc trích dẫn — tránh sai lệch học thuật
- Bài báo dùng thuật ngữ **"hot" / "cold" element**. Bài báo **KHÔNG** dùng chữ "Elephant flow", "Mice flow", hay "DDoS" — đó là tên nhóm tự mượn từ lĩnh vực network traffic monitoring (một ứng dụng CMS được chính bài báo nêu ở phần giới thiệu) để minh hoạ trực quan hơn cho người xem demo.
  → Trong **code, schema, JSON**: luôn dùng `is_hot` / `is_cold` (xem §2).
  → Trong **UI, slide, lời thuyết trình**: được phép dùng "Elephant / Mice" như nhãn hiển thị cho người xem, nhưng khi viết báo cáo học thuật phải ghi rõ đây là cách nhóm áp dụng khái niệm hot/cold của bài báo vào bài toán elephant/mice flow, **không** viết như thể bài báo tự dùng cụm từ này.
- Bài báo **không** thử nghiệm trên bất kỳ dataset thật nào — cả 3 phân phối (Uniform, Step, Zipf) đều là dữ liệu sinh ngẫu nhiên theo mô hình lý thuyết. Việc nhóm chạy thêm trên NASA HTTP logs là **phần mở rộng của nhóm**, không phải thực nghiệm gốc của bài báo. Khi viết báo cáo/thuyết trình, phải nói rõ ranh giới này (xem thêm `project_ovr.md §7`).
- Mọi docstring/comment trong code khi giải thích "tại sao làm vậy" mà dựa trên bài báo, phải ghi rõ **"theo Fusy & Kucherov 2023, Section X.X"** — không diễn giải chung chung kiểu "theo nghiên cứu".

### 0.2 Quy tắc kỹ thuật quan trọng nhất — ĐỌC KỸ TRƯỚC KHI VIẾT `cms.py`

Mô hình CMS trong bài báo là **hypergraph 1 mảng dùng chung**, KHÔNG phải CMS cổ điển kiểu d-hàng × w-cột:

- Chỉ có **MỘT mảng `table_size` ô đếm** (không phải k mảng riêng).
- Mỗi phần tử được ánh xạ tới **k ô riêng biệt (phân biệt, không trùng)** trong mảng đó qua k hash function — giống một "cạnh" (edge) nối k "đỉnh" (counter) trong hypergraph → đây là lý do tên gọi "Mixed **Hypergraph** CMS".
- **Conservative update**: khi insert, chỉ tăng **giá trị NHỎ NHẤT** trong số k ô được gán (không tăng cả k ô như CMS thường).
- Query: trả về **giá trị nhỏ nhất (min)** trong số k ô được gán cho phần tử đó.
- **Bộ nhớ ước tính = `table_size` × kích thước 1 counter, KHÔNG nhân thêm theo k** (vì dùng chung 1 mảng). Ví dụ: `table_size=5000`, counter kiểu `uint64` (8 byte) → 5000 × 8 = 40.000 byte ≈ 39 KB — khớp với con số "40KB" nêu trong kịch bản demo.
  - ⚠️ Nếu ai đó code `cms.py` theo kiểu "k mảng riêng, mỗi mảng w ô" (CMS cổ điển phổ biến trên mạng) — đó là **SAI** so với bài báo này, kết quả sẽ không thể so sánh được với Figure 5. Đây là lỗi dễ mắc nhất vì hầu hết tutorial CMS trên mạng dạy theo kiểu cổ điển.

---

## 1. Cấu trúc thư mục (bám theo `Rules_Code_Demo`, có bổ sung)

```text
elephant-mice-cms-demo/
├── rules.md                 ← file này
├── ai_agents.md
├── project_ovr.md
├── requirement.md
├── README.md
├── .gitignore
├── data_real/                ← Folder chứa tài liệu và code dữ liệu thật
│   ├── analyze_nasa_log.py
│   ├── huongdan_keo_data_access_log.md
│   ├── processed_cache.json  # Dữ liệu cache đã tổng hợp (~1.9 MB, được push git)
│   └── backend/              # Mã nguồn backend phục vụ dữ liệu thật
│       ├── app/
│       │   ├── main.py
│       │   ├── algorithms/
│       │   │   ├── __init__.py
│       │   │   ├── hash_utils.py
│       │   │   ├── cms.py
│       │   │   └── cms_mixed.py
│       │   ├── data/
│       │   │   ├── __init__.py
│       │   │   ├── data_generator.py
│       │   │   ├── real_loader.py        ← MỚI so với bản cũ (xem §5)
│       │   │   └── presets.py
│       │   ├── schemas/
│       │   │   ├── request_models.py
│       │   │   └── response_models.py
│       │   ├── services/
│       │   │   └── simulation_service.py
│       │   └── utils/
│       │       └── metrics.py
│       ├── scripts/
│       │   └── run_full_experiments.py   ← MỚI: quét tham số đầy đủ, xuất số liệu/hình cho báo cáo (KHÔNG qua API, xem `project_ovr.md §6`)
│       ├── tests/
│       │   ├── test_cms.py
│       │   ├── test_cms_mixed.py
│       │   ├── test_data_generator.py
│       │   └── test_real_loader.py       ← MỚI
│       ├── requirements.txt
│       └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   ├── js/
│   │   ├── app.js
│   │   ├── api.js
│   │   ├── charts.js
│   │   └── mock_data.js
│   └── assets/
└── data/
    └── mock/
        └── sample_response.json
```

Không tạo lại folder `docs/` (đã bỏ theo quyết định cũ) — toàn bộ nội dung từng nằm ở `docs/api_contract.md` nay gộp vào `rules.md §3`.

---

## 2. Bảng thuật ngữ & tên biến chuẩn (theo đúng ký hiệu bài báo)

| Ký hiệu trong bài báo | Ý nghĩa | Tên biến/field trong code | Kiểu | Ghi chú |
|---|---|---|---|---|
| n | số ô đếm (counters) | `table_size` | `int` | Kích thước MỘT mảng dùng chung |
| k, k_e | số hash function gán cho 1 phần tử | `k` (classic) / `k_hot`, `k_cold` (mixed) | `int` | Xem §0.2 |
| λ | load factor = số phần tử phân biệt / n | tính runtime, không lưu field riêng | `float` | `λh = n_hot/table_size`, `λc = n_cold/table_size` |
| G | **gap factor**: tỉ lệ xác suất xuất hiện của **MỘT** phần tử hot so với **MỘT** phần tử cold | `gap_factor` | `float` | ⚠️ KHÔNG phải tỉ lệ tổng khối lượng traffic hot/cold. Công thức đúng: `ph/pc = gap_factor × (n_hot/n_cold)`, với `ph`, `pc` là xác suất gộp cả nhóm. Nếu code nhầm `gap_factor = ph/pc` trực tiếp → toàn bộ preset sai. |
| occ(e) | số lần xuất hiện thật của phần tử trong stream | `true_count` | `int` | Lấy từ **đếm thật trên chính stream đã sinh ra**, không suy từ công thức lý thuyết (xem §4.2) |
| c(e) | giá trị CMS trả về khi query | `estimate` | `int` | |
| err(e) | (c(e) − occ(e)) / occ(e) | `relative_error` | `float` | Luôn ≥ 0 (Count-Min chỉ overestimate) |
| — | phần tử thuộc nhóm hot/elephant | `is_hot` | `bool` | **Tên field DUY NHẤT dùng xuyên suốt code/schema/JSON.** Không dùng `is_elephant` trong code (chỉ dùng "Elephant" làm nhãn hiển thị UI, xem §0.1) |
| — | định danh nguồn gửi request | `ip` | `str` | Giữ tên `ip` cho khớp toàn bộ tài liệu đã có, dù với data thật (NASA log) giá trị này có thể là **hostname** (vd `in24.inetnebr.com`) chứ không luôn là địa chỉ IP thuần — không ảnh hưởng thuật toán (CMS chỉ cần string để hash) |
| — | tên thuật toán | `"classic"` \| `"mixed"` | `str` (enum) | Case-sensitive, dùng đúng 2 giá trị này trong toàn bộ request/response |

---

## 3. API Contract — CHỐT CỨNG, mọi người code đúng theo đây

### 3.1 Quy ước chung
- Base URL backend (dev): `http://localhost:8000`
- Base URL frontend (dev, static server): `http://localhost:5500`
- Toàn bộ route có prefix `/api`
- Toàn bộ field JSON dùng **snake_case** (kể cả phía JS chỉ đọc, không tự đổi thành camelCase)
- CORS: backend phải allow origin của frontend (cấu hình qua biến, không hardcode rải rác)
- Content-Type: `application/json` hai chiều

### 3.2 `GET /api/health`
Trả `{"status": "ok"}` — dùng để C/B kiểm tra kết nối nhanh.

### 3.3 `GET /api/presets`
Trả danh sách preset synthetic có sẵn (định nghĩa đầy đủ ở `project_ovr.md §5` và `backend/app/data/presets.py`):

```json
{
  "presets": [
    {"id": "main", "label": "Trình diễn chính (dễ thấy khác biệt)", "params": {"n_hot": 5, "n_cold": 9995, "gap_factor": 100, "table_size": 5000, "total_packets": 500000}},
    {"id": "paper_faithful", "label": "Bám sát Figure 5 của paper", "params": {"n_hot": 300, "n_cold": 5000, "gap_factor": 20, "table_size": 1000, "total_packets": 500000}},
    {"id": "stress", "label": "Stress / vùng bão hoà (Figure 6)", "params": {"n_hot": 100, "n_cold": 900, "gap_factor": 10, "table_size": 1000, "total_packets": 500000}}
  ]
}
```

### 3.4 `POST /api/simulate` — endpoint chính

**Nguyên tắc bắt buộc**: một lần gọi trả kết quả của **CẢ classic lẫn mixed cùng lúc**, chạy trên **CÙNG một stream/dữ liệu** (cùng `seed`). Lý do: nếu classic và mixed chạy trên 2 stream random sinh riêng, chênh lệch kết quả có thể do random khác nhau chứ không phải do thuật toán tốt hơn — làm sai lệch kết luận "chứng minh bằng số liệu thực tế". Frontend vẫn có thể **hiển thị progressive** (bấm Run 1 → hiện panel classic, bấm Run 2 → hiện panel mixed) từ CÙNG một response đã nhận, không cần gọi API 2 lần (xem `ai_agents.md` phần Role B).

**Request — trường chung (mọi `data_source`):**

| Field | Kiểu | Bắt buộc | Mặc định | Ghi chú |
|---|---|---|---|---|
| `data_source` | `"synthetic"` \| `"real"` | ✅ | — | |
| `seed` | `int` \| `null` | ❌ | random nếu không truyền | Server phải **trả lại seed đã dùng** trong response để tái lập được |
| `table_size` | `int` | ✅ | — | |
| `classic_k` | `int` | ❌ | `3` | |
| `mixed_k_hot` | `int` | ❌ | `2` | |
| `mixed_k_cold` | `int` | ❌ | `5` | |

**Request — trường riêng khi `data_source = "synthetic"`:**

| Field | Kiểu | Bắt buộc |
|---|---|---|
| `n_hot` | `int` | ✅ |
| `n_cold` | `int` | ✅ |
| `gap_factor` | `float` | ✅ |
| `total_packets` | `int` | ✅ |

**Request — trường riêng khi `data_source = "real"`:**

| Field | Kiểu | Bắt buộc | Mặc định |
|---|---|---|---|
| `hot_threshold_percent` | `float` | ❌ | `1.0` (top 1% host tần suất cao nhất = hot) |

> C (Hiếu) dùng Pydantic `model_validator(mode="after")` để bắt lỗi thiếu field theo `data_source`, không dùng if/else rải rác trong route.

**Response:**

```json
{
  "run_id": "a1b2c3d4",
  "data_source": "synthetic",
  "seed": 42,
  "params_used": { "...": "toàn bộ tham số thực tế đã dùng, kể cả default đã áp" },
  "results": {
    "classic": {
      "k": 3,
      "elephant_detected": 3,
      "elephant_total": 5,
      "mice_avg_error": 3.4,
      "top10": [
        {"ip": "10.0.0.1", "true_count": 95283, "estimate": 96100, "is_hot": true}
      ]
    },
    "mixed": {
      "k_hot": 2,
      "k_cold": 5,
      "elephant_detected": 5,
      "elephant_total": 5,
      "mice_avg_error": 0.12,
      "top10": [
        {"ip": "10.0.0.1", "true_count": 95283, "estimate": 95400, "is_hot": true}
      ]
    }
  }
}
```

- `elephant_detected` / `elephant_total`: số hot IP nằm trong top-N ước lượng cao nhất (N = `elephant_total`) đúng thực sự là hot.
- `mice_avg_error`: trung bình `relative_error` tính **riêng trên nhóm cold/mice** (không tính hot).
- `top10`: 10 dòng đại diện (ưu tiên: toàn bộ hot + một số cold ngẫu nhiên/đại diện), giống hệt tập IP giữa classic và mixed để FE dễ join khi vẽ bảng so sánh.

### 3.5 Response lỗi — dùng chung 1 khuôn

```json
{ "error": { "code": "INVALID_PARAMS", "message": "table_size phải > 0" } }
```

Mã lỗi chuẩn hoá: `INVALID_PARAMS`, `DATASET_NOT_FOUND`, `TABLE_TOO_SMALL_FOR_K`, `INTERNAL_ERROR`. Không tự bịa thêm mã khác mà không cập nhật bảng này.

---

## 4. Quy tắc đảm bảo tính đúng đắn thực nghiệm

### 4.1 Seed & tính tái lập
- `seed` ở API level chỉ điều khiển việc **sinh dữ liệu/stream** (`data_generator.py`, `real_loader.py` khi shuffle) — dùng chung 1 seed cho cả classic và mixed trong 1 lần `/api/simulate`.
- Hash-seed **bên trong** mỗi CMS (dùng cho `hash_utils.py`) là chi tiết triển khai riêng của từng sketch, không cần trùng giữa classic và mixed. Nhưng **bên trong Mixed**, seed dùng cho nhóm hot và nhóm cold phải **tách namespace** (vd hot dùng seed `0..k_hot-1`, cold dùng seed `100..100+k_cold-1`) để tránh tương quan giả tạo giữa 2 nhóm.
- Phải xử lý va chạm khi chọn k chỉ số: dùng thử seed kế tiếp nếu trùng, đảm bảo đủ k ô **phân biệt** cho một phần tử (đúng định nghĩa hyperedge).

### 4.2 True count phải lấy từ đếm thật
`true_count` của mỗi phần tử phải lấy từ **đếm trực tiếp trên chính stream đã sinh ra** (chạy 1 lượt qua stream, đếm bằng dict/Counter), **không** suy từ công thức lý thuyết `ph`, `pc`. Nếu dùng số lý thuyết, sai số làm tròn sẽ trộn lẫn vào sai số của CMS, làm méo kết luận so sánh.

### 4.3 Hiệu năng — 10 triệu packet
- Mục tiêu narration ("router xử lý 10 triệu packet") mô tả **quy mô bài toán**, không bắt buộc live-demo phải xử lý đúng 10 triệu packet trong 1 request/response còn mượt.
- **Mặc định cho demo tương tác (click trực tiếp)**: `total_packets = 500,000` — đủ nhanh (ước lượng vài giây cho cả classic+mixed), vẫn đủ lớn để thấy rõ hiệu ứng.
- **Số liệu chính thức cho báo cáo/slide**: chạy `backend/scripts/run_full_experiments.py` riêng (không qua FastAPI, không giới hạn thời gian response) với `total_packets = 10,000,000` và quét nhiều tham số để vẽ lại dạng đường cong giống Figure 5/6 của bài báo.
- `data_generator.generate_step_distribution()` PHẢI dùng generator/`yield`, không dựng list 10 triệu phần tử trong RAM.

### 4.4 Validation input tối thiểu
`table_size > 0`; `table_size > max(classic_k, mixed_k_hot, mixed_k_cold)`; `gap_factor > 1`; `n_hot, n_cold > 0`; `0 < hot_threshold_percent < 100`; `total_packets > 0`.

---

## 5. Dataset thật — NASA HTTP access logs (Kaggle)

Xác nhận: file tải về là **log thô dạng text**, định dạng NCSA Common Log (không phải CSV có sẵn cột). Mọi người dùng chung 1 cách parse sau, không tự viết regex khác:

```python
import re

NASA_LOG_PATTERN = re.compile(
    r'^(\S+) \S+ \S+ \[([^\]]+)\] "([^"]*)" (\d{3}) (\S+)$'
)
# group(1) = host (hostname HOẶC ip thô nếu DNS không resolve được)
# group(2) = timestamp, vd "01/Jul/1995:00:00:01 -0400"
# group(3) = request line, vd "GET /images/x.gif HTTP/1.0"
# group(4) = status code
# group(5) = bytes (có thể là "-" nếu không rõ → coi như 0)
```

- Dòng không khớp pattern → **bỏ qua và đếm số dòng bị skip** (log thật luôn có tỉ lệ dòng lỗi/thiếu field — phải báo cáo minh bạch tỉ lệ này, không âm thầm bỏ).
- **Tiền xử lý 1 lần, cache lại**: parse toàn bộ file log → đếm `{host: count}` → lưu ra `data_real/processed_cache.json`. Mỗi request `/api/simulate` với `data_source=real` chỉ đọc file cache này, **không** parse lại log thô mỗi lần (file có thể vài trăm nghìn — hàng triệu dòng, parse lại mỗi request sẽ rất chậm).
- Gắn nhãn hot/cold: sort giảm dần theo count, top `hot_threshold_percent`% đầu = `is_hot: true`.
- File log gốc và cache **gitignore** nếu dung lượng lớn (ghi rõ trong README hướng dẫn tải lại từ Kaggle).

---

## 6. Naming convention

| Loại | Quy ước | Ví dụ |
|---|---|---|
| Python file/function/variable | `snake_case` | `data_generator.py`, `generate_step_distribution()` |
| Python class | `PascalCase` | `ConservativeCMS`, `MixedHypergraphCMS` |
| JS file | `snake_case` (giữ theo cấu trúc cũ) | `mock_data.js` |
| JS function/variable | `camelCase` | `runSimulation()`, `renderTop10Table()` |
| JSON field (wire format) | `snake_case` | `is_hot`, `table_size` |
| Pydantic model | `PascalCase` + hậu tố rõ nghĩa | `SimulationRequest`, `SimulationResponse`, `AlgorithmResult` |
| Test file | `test_<module>.py` | `test_cms_mixed.py` |
| Commit message | Conventional Commits | `feat(algo): implement conservative update`, `fix(data): xử lý dòng log lỗi` |

## 7. Git workflow (giữ nguyên từ bản cũ)
```
main (protected)
 ├── feature/algorithm-cms        → A (Khoa)
 ├── feature/data-generator       → D (Tiên)
 ├── feature/data-mock            → E (Thịnh)
 ├── feature/frontend-ui          → B (Mai)
 └── feature/backend-integration  → C (Hiếu)
```
Mỗi người code trong nhánh riêng theo đúng file mình sở hữu (`ai_agents.md`). Không sửa file không thuộc vai trò của mình mà không báo trước — kể cả khi "chỉ sửa 1 dòng".

## 8. Thư viện bắt buộc dùng chung (tránh mỗi module chọn 1 kiểu khác nhau)

| Nhu cầu | Thư viện | Lý do |
|---|---|---|
| Hash function có seed, nhanh | `mmh3` (MurmurHash3) | Nhanh, seed được, không dùng `hash()` built-in của Python (không ổn định giữa các lần chạy do `PYTHONHASHSEED` random) |
| Web framework | `fastapi` + `uvicorn` | Đã chốt trong cấu trúc cũ |
| Validate schema | `pydantic` v2 | Đi kèm FastAPI |
| Test | `pytest` | |
| Chart FE | `Chart.js` (qua CDN) | Đã chốt trong cấu trúc cũ, không đổi sang thư viện khác giữa chừng |

---

**Tóm tắt 5 điều tối quan trọng không được sai:**
1. CMS dùng **1 mảng `table_size` ô dùng chung**, không nhân theo k.
2. Field chuẩn là `is_hot` (không phải `is_elephant`) trong code/schema.
3. `gap_factor` là tỉ lệ **per-element**, không phải `ph/pc` trực tiếp.
4. Classic và Mixed trong 1 lần so sánh **phải chạy trên cùng 1 stream** (cùng seed).
5. `true_count` lấy từ **đếm thật**, không suy lý thuyết.
