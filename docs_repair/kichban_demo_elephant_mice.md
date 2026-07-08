# Kịch bản Demo: Elephant & Mice Flow Detection
> Count-Min Sketch with Variable Hash Functions — Fusy & Kucherov (2023)
> Link bài báo: http://igm.univ-mlv.fr/~fusy/Articles/countmin-exp.pdf

---

## 1. Mục tiêu Demo

Chứng minh bằng số liệu thực tế rằng **Mixed Hypergraph CMS k=(2,5)** vượt trội hơn **CMS truyền thống k=3** trong bài toán phát hiện Elephant Flows (DDoS, bandwidth hog) giữa hàng ngàn Mice Flows, dùng cùng một lượng bộ nhớ cố định.

Đây là minh chứng thực nghiệm cho **Section 3.2 (Step Distribution)** của bài báo gốc.

> **Lưu ý phạm vi demo**: Nhóm chỉ triển khai demo cho kịch bản Elephant/Mice (tương ứng Section 3.2). Các kết quả Uniform distribution (Section 3.1) và Zipf distribution (Section 3.3) sẽ được trình bày bằng số liệu/đồ thị có sẵn trong bài báo ở phần Chương 3 — Kết quả thực nghiệm của báo cáo, **không cần code demo tương tác cho 2 phần này**.

### Căn cứ chính xác từ bài báo (đã kiểm chứng)

| Thành phần demo | Trích dẫn/căn cứ từ bài báo |
|---|---|
| Cấu hình k=(2,5) hot/cold | Section 3.2.2, Figure 5: *"k = (2, 5) for hot and cold elements respectively"* |
| Giả định biết trước hot/cold | Section 3.2: *"we assume that we have a prior knowledge on whether a given element belongs to hot or cold ones"* |
| Định nghĩa Gap factor G | Section 3.2: *"G > 1, called gap factor, denotes the ratio between probabilities of a hot and a cold element"* — công thức ph/pc = G·λh/λc |
| Hiện tượng background noise | Section 3.2.1: cold edges đẩy "background level" của counter cao hơn true count của hot, gây overestimate |
| Lý do k_cold lớn hơn giúp ích | Section 3.2.2: tăng cardinality cold edge → tăng xác suất ít nhất 1 vertex không bị incident với hot edge |


---

## 2. Phân công 7 vai trò + cấu trúc repo

Dựa theo kịch bản demo (FastAPI backend + Chart.js frontend, thuật toán CMS), đây là cách chia việc theo đúng 7 vai trò, kèm cấu trúc repo để 5 người code không đụng file của nhau.

### 2.1 Phân vai trò chi tiết (7 người)

| # | Vai trò | Việc cụ thể | File sở hữu chính |
|---|---|---|---|
| **A** | Code chính thuật toán | Cài `CMS classic k=3` và `Mixed CMS k=(2,5)`, hàm tính error rate, detection rate | `backend/app/algorithms/`, `backend/app/utils/metrics.py` |
| **B** | Code chính FE | UI chọn tham số, nút Run, tab "So sánh", vẽ Chart.js | `frontend/index.html`, `frontend/js/charts.js`, `frontend/css/` |
| **C** | Code giữa (Integration) | Định nghĩa API contract (request/response JSON) **trước tiên**, viết FastAPI routes, gọi thuật toán của A, trả JSON đúng schema cho B | `backend/app/main.py`, `backend/app/schemas/`, `frontend/js/api.js` |
| **D** | Data — hỗ trợ BE | Viết `data_generator.py` (Step distribution theo mục 4.3), 3 bộ preset tham số (mục 4.5) | `backend/app/data/data_generator.py`, `presets.py` |
| **E** | Data — hỗ trợ FE | Tạo file JSON mẫu (mock response) đúng schema của C để B code UI **không cần chờ backend xong** | `data/mock/sample_response.json`, `frontend/js/mock_data.js` |
| **F, G** | Slide prompting | Nhận nội dung 6x6 từ 5 người trên, prompt ra slide | `docs/slide_prompts/` |
| Nhóm trưởng | (thường là A hoặc C) | Tổng hợp `docs/final_report.md` từ 5 file 6x6 | `docs/final_report.md` |

**Điểm mấu chốt để 5 người code song song không bị nghẽn nhau:** C phải chốt **API contract** (cấu trúc JSON request/response) ngay ngày đầu tiên, viết vào `docs/api_contract.md`. Sau đó:
- A code thuật toán độc lập, test bằng pytest, không cần biết FastAPI.
- B code UI dựa trên **mock JSON của E**, không cần chờ A hay C xong.
- C nối A vào FastAPI route, trả đúng JSON đã chốt.
- D nuôi dữ liệu cho A test, E nuôi dữ liệu giả cho B test.

### 2.2 Cấu trúc repo

```
elephant-mice-cms-demo/
├── backend/
│   ├── app/
│   │   ├── main.py                      # [C] FastAPI app + routes
│   │   ├── algorithms/
│   │   │   ├── __init__.py
│   │   │   ├── cms.py                   # [A] CMS classic k=3
│   │   │   ├── cms_mixed.py             # [A] Mixed CMS k=(2,5)
│   │   │   └── hash_utils.py            # [A] hash functions dùng chung
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── data_generator.py        # [D] Step distribution generator
│   │   │   └── presets.py               # [D] 3 bộ tham số (chính/khó/stress)
│   │   ├── schemas/
│   │   │   ├── request_models.py        # [C] Pydantic: SimulationRequest
│   │   │   └── response_models.py       # [C] Pydantic: SimulationResponse
│   │   ├── services/
│   │   │   └── simulation_service.py    # [A+C] gen → insert → query → so sánh
│   │   └── utils/
│   │       └── metrics.py               # [A] error rate, detection rate
│   ├── tests/
│   │   ├── test_cms.py                  # [A]
│   │   ├── test_cms_mixed.py            # [A]
│   │   └── test_data_generator.py       # [D]
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── index.html                       # [B]
│   ├── css/style.css                    # [B]
│   ├── js/
│   │   ├── app.js                       # [B] logic chính + render kết quả
│   │   ├── api.js                       # [C] fetch wrapper gọi backend
│   │   ├── charts.js                    # [B] Chart.js: bar chart, bảng top-10
│   │   └── mock_data.js                 # [E] data giả để B dev độc lập
│   └── assets/
│
├── data/
│   └── mock/
│       └── sample_response.json         # [E] JSON mẫu đúng schema, dùng test FE
│
├── docs/
│   ├── api_contract.md                  # [C] chốt schema NGÀY ĐẦU
│   ├── slides_6x6/
│   │   ├── A_6x6.md
│   │   ├── B_6x6.md
│   │   ├── C_6x6.md
│   │   ├── D_6x6.md
│   │   └── E_6x6.md
│   ├── final_report.md                  # [Nhóm trưởng] tổng hợp
│   └── slide_prompts/
│       ├── prompt_log.md                # [F, G]
│       └── final_slides.pptx
│
├── .gitignore
└── README.md
```

### 2.3 API contract — chốt trước khi ai cũng bắt đầu code

C viết `docs/api_contract.md` với nội dung kiểu:

```json
// POST /api/simulate
// Request
{
  "algorithm": "classic" | "mixed",
  "n_hot": 5,
  "n_cold": 9995,
  "gap_factor": 100,
  "table_size": 5000,
  "total_packets": 10000000
}

// Response
{
  "elephant_detected": 5,
  "elephant_total": 5,
  "mice_avg_error": 0.12,
  "top10": [
    {"ip": "10.0.0.1", "true_count": 95283, "estimate": 96100, "is_elephant": true},
    ...
  ]
}
```

E dùng đúng schema này để viết `sample_response.json`, B code thẳng vào đó, không phải đợi A+C xong thuật toán thật.

### 2.4 Git workflow gợi ý

```
main (protected)
 ├── feature/algorithm-cms        → A
 ├── feature/data-generator       → D
 ├── feature/data-mock            → E
 ├── feature/frontend-ui          → B
 └── feature/backend-integration  → C
```

- Mỗi người code trong nhánh riêng theo đúng thư mục mình sở hữu (giảm conflict gần như về 0 vì khác folder).
- C merge `feature/algorithm-cms` + `feature/data-generator` vào `feature/backend-integration` trước, test xong mới merge `main`.
- B merge riêng, dùng mock data — khi C báo API thật đã xong thì B chỉ đổi `mock_data.js` → `api.js` (1 dòng), gần như không phải sửa code UI.

### 2.5 Thứ tự ưu tiên (để tránh nghẽn)

1. **Ngày 1**: C chốt API contract → cả nhóm đồng ý.
2. **Ngày 1–2 (song song)**: A code `cms.py` + `cms_mixed.py` (có pytest riêng, không cần FastAPI) | D code `data_generator.py` | E viết `sample_response.json` | B code UI với mock data.
3. **Ngày 3**: C nối A + D vào FastAPI, test bằng Postman/curl so với contract.
4. **Ngày 4**: B đổi từ mock sang API thật, debug chung (đây là lúc C cần follow sát cả 2 bên).
5. **Ngày 5**: Chạy preset thật (bảng mục 4.5 trong file này) để lấy số liệu thật thay placeholder `3/5`, `340%`...
6. Song song suốt quá trình: mỗi người tự viết `docs/slides_6x6/X_6x6.md`, nhóm trưởng gom lại, F+G bắt đầu prompt slide ngay khi có 6x6 đầu tiên, không cần chờ đủ 5 bài.

---

## 3. Lưu đồ hướng chạy (Flow Diagram)

```
┌─────────────────────────────────────────────────────────────┐
│                     BẮT ĐẦU DEMO                              │
└───────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 1: SINH DỮ LIỆU GIẢ LẬP                                 │
│  ─────────────────────────────                                │
│  data_generator.generate_step()                               │
│  → 5 Elephant IPs   (hot, count cao)                          │
│  → 9,995 Mice IPs   (cold, count thấp)                        │
│  → Trộn ngẫu nhiên thành 1 stream 10 triệu packets            │
└───────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 2: KHỞI TẠO 2 SKETCH SONG SONG                          │
│  ─────────────────────────────────                            │
│  ┌──────────────────────┐    ┌──────────────────────┐        │
│  │ CMS Conservative      │    │ CMS Mixed             │        │
│  │ k = 3 (đồng nhất)     │    │ k_hot = 2, k_cold = 5  │        │
│  │ n = 5000 ô đếm        │    │ n = 5000 ô đếm         │        │
│  └──────────────────────┘    └──────────────────────┘        │
└───────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 3: NẠP STREAM VÀO CẢ 2 SKETCH                            │
│  ─────────────────────────────────                            │
│  for packet in stream:                                        │
│      cms_classic.insert(packet.ip)                             │
│      cms_mixed.insert(packet.ip, is_hot=packet.is_elephant)    │
└───────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 4: TRUY VẤN & TÍNH LỖI                                   │
│  ───────────────────────                                      │
│  for ip in all_ips:                                            │
│      estimate_classic = cms_classic.query(ip)                  │
│      estimate_mixed   = cms_mixed.query(ip)                    │
│      error = (estimate - true_count) / true_count              │
└───────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 5: TỔNG HỢP & TRẢ KẾT QUẢ JSON                           │
│  ─────────────────────────────────                            │
│  - % Elephant phát hiện đúng (top-5 theo estimate)             │
│  - Lỗi trung bình của Mice (classic vs mixed)                  │
│  - Bảng top-10 IP: estimate vs true count                      │
└───────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 6: FRONTEND HIỂN THỊ                                     │
│  ───────────────────────                                      │
│  app.js nhận JSON → Chart.js vẽ:                                │
│  - Bar chart: error rate Mice (classic vs mixed)                │
│  - Bar chart: Elephant detection rate                           │
│  - Bảng: top-10 IP so sánh                                       │
└───────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      KẾT THÚC DEMO                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Kịch bản demo chi tiết — Từng bước thuyết trình

> Các con số `3/5`, `340%`, `5/5`, `12%` dưới đây là **placeholder minh họa** —
> phải thay bằng số liệu thật sau khi chạy code thực nghiệm (xem cảnh báo mục 4.5).

### Bước trình bày 1 — Đặt vấn đề (1 phút)

> *"Một router xử lý 10 triệu packets mỗi giây. Trong số hàng chục nghìn IP kết nối, chỉ có vài IP là nguồn tấn công DDoS hoặc tải file nặng (Elephant), còn lại là traffic bình thường (Mice). Router chỉ có 40KB RAM để đếm — không thể lưu hết. CMS truyền thống có giải quyết được bài toán này không?"*

### Bước trình bày 2 — Chạy CMS truyền thống trước (2 phút)

Trên giao diện web, chọn:
```
Thuật toán: CMS gốc (k=3)
Số Elephant: 5
Số Mice: 9,995
Gap factor: 100
Table size: 5,000 ô (40KB)
```

Nhấn "Run" → hiển thị kết quả:
```
Elephant phát hiện đúng: 3/5
Lỗi Mice trung bình: ~340%
```

**Giải thích trực tiếp trên màn hình**: chỉ ra IP nào bị nhận sai (Mice bị estimate cao bất thường do va chạm hash với Elephant).

### Bước trình bày 3 — Chạy Mixed CMS (2 phút)

Đổi thuật toán sang:
```
Thuật toán: Mixed CMS k=(2,5)
(Giữ nguyên các tham số khác)
```

Nhấn "Run" → hiển thị kết quả:
```
Elephant phát hiện đúng: 5/5  
Lỗi Mice trung bình: ~12%      
```

### Bước trình bày 4 — So sánh trực quan (1 phút)

Chuyển sang tab "So sánh" → biểu đồ bar chart 2 cột cạnh nhau, người xem thấy ngay khoảng cách giữa 340% và 12%.

### Bước trình bày 5 — Kết luận liên hệ lý thuyết (1 phút)

> *"Đây chính là điều bài báo Fusy & Kucherov 2023 chứng minh ở Section 3.2: gán ít hash hơn cho phần tử hot, nhiều hash hơn cho phần tử cold, giúp cold elements dễ tìm được ô đếm 'sạch' hơn — giảm nhiễu chéo giữa hai nhóm."*

---

## 4. Hướng dẫn sinh dữ liệu demo

### 4.1 Nguyên lý sinh dữ liệu Step Distribution

Theo Section 3.2 bài báo, Step distribution có 2 nhóm phần tử với xác suất khác nhau theo tỷ lệ **gap factor G**:

```
P(hot element) = G × P(cold element)
```

### 4.2 Công thức tính số lần xuất hiện

Với tổng N packets, n_hot Elephant IPs, n_cold Mice IPs, gap factor G:

```python
# Tổng "trọng số" = n_hot × G + n_cold × 1
total_weight = n_hot * G + n_cold

# Số packets cho mỗi Elephant IP
packets_per_elephant = N * G / total_weight

# Số packets cho mỗi Mice IP
packets_per_mice = N * 1 / total_weight
```

**Ví dụ cụ thể với N=10,000,000, n_hot=5, n_cold=9995, G=100:**

```python
total_weight = 5 * 100 + 9995 * 1 = 500 + 9995 = 10495

packets_per_elephant = 10_000_000 * 100 / 10495 ≈ 95,283
packets_per_mice     = 10_000_000 * 1   / 10495 ≈ 953

# Kiểm chứng tổng: 5×95,283 + 9995×953 ≈ 10,001,050 ≈ 10,000,000 
# Kiểm chứng tỉ lệ: 95,283 / 953 ≈ 100 = G  (đúng định nghĩa per-element ratio)
```

> Công thức này khớp chính xác với định nghĩa gap factor trong bài báo (Section 3.2):
> ph/pc = G·λh/λc, với ph, pc là tổng xác suất khối hot/cold. Quy đổi sang số packets
> trên mỗi phần tử cho ra đúng tỉ lệ G giữa 1 Elephant và 1 Mice — đây chính là cách
> bài báo mô tả: *"each hot element is G times more frequent than a cold one"*.

### 4.3 Code mẫu sinh dữ liệu (Python)

```python
import random

def generate_step_distribution(n_hot=5, n_cold=9995, gap=100, total_packets=10_000_000, seed=42):
    """
    Sinh dữ liệu Step Distribution mô phỏng Elephant/Mice flows.
    Trả về: dict {ip: true_count}, list các (ip, is_hot) theo thứ tự ngẫu nhiên
    """
    random.seed(seed)

    # Tạo danh sách IP giả lập
    elephant_ips = [f"10.0.0.{i}" for i in range(1, n_hot + 1)]
    mice_ips = [f"192.168.{i//255}.{i%255}" for i in range(1, n_cold + 1)]

    # Tính trọng số
    total_weight = n_hot * gap + n_cold

    # Số packets mỗi nhóm
    packets_per_elephant = int(total_packets * gap / total_weight)
    packets_per_mice = max(1, int(total_packets * 1 / total_weight))

    true_counts = {}
    stream = []

    for ip in elephant_ips:
        true_counts[ip] = packets_per_elephant
        stream.extend([ip] * packets_per_elephant)

    for ip in mice_ips:
        true_counts[ip] = packets_per_mice
        stream.extend([ip] * packets_per_mice)

    random.shuffle(stream)  # trộn ngẫu nhiên giống traffic thực tế

    return true_counts, stream, set(elephant_ips)
```

### 4.4 [NGOÀI PHẠM VI DEMO] Hàm sinh dữ liệu Zipf — chỉ tham khảo cho Chương 3

> Nhóm đã quyết định **không demo tương tác cho Zipf distribution** — phần này sẽ
> được trình bày bằng số liệu/đồ thị có sẵn từ bài báo gốc (Figure 7, 8) trong Chương 3
> — Kết quả thực nghiệm. Hàm dưới đây chỉ giữ lại làm tài liệu tham khảo, **không cần
> code/tích hợp vào FastAPI**.

```python
import numpy as np

def generate_zipf_distribution(n_elements=10000, beta=0.8, total_packets=10_000_000, seed=42):
    """
    [Tham khảo — không dùng trong demo chính]
    Sinh dữ liệu theo phân phối Zipf — mô phỏng traffic mạng thực tế.
    beta: tham số skewness (càng lớn càng dốc, beta=0 ~ uniform)
    """
    np.random.seed(seed)

    ranks = np.arange(1, n_elements + 1)
    weights = 1 / (ranks ** beta)
    probabilities = weights / weights.sum()

    ips = [f"172.16.{i//255}.{i%255}" for i in range(n_elements)]

    # Sinh stream theo phân phối
    stream_indices = np.random.choice(n_elements, size=total_packets, p=probabilities)
    stream = [ips[i] for i in stream_indices]

    true_counts = {}
    for idx in stream_indices:
        ip = ips[idx]
        true_counts[ip] = true_counts.get(ip, 0) + 1

    return true_counts, stream
```

### 4.5 Bảng tham số gợi ý cho demo (chỉ Mode 3 — Step Distribution)

| Kịch bản | n_hot | n_cold | Gap (G) | Table size (n) | RAM ước tính |
|---|---|---|---|---|---|
| Demo chính (rõ ràng) | 5 | 9,995 | 100 | 5,000 | 40 KB |
| Demo khó (G nhỏ) | 5 | 9,995 | 5 | 5,000 | 40 KB |
| Demo stress test | 20 | 49,980 | 200 | 10,000 | 80 KB |

> ~~Demo Zipf~~ — đã loại khỏi phạm vi demo, xem ghi chú mục 4.4.

> **Gợi ý khi thuyết trình**: Chạy "Demo khó (G nhỏ)" sau "Demo chính" để cho thấy khi gap factor nhỏ, CMS truyền thống gần như thất bại hoàn toàn, trong khi Mixed CMS vẫn giữ được độ chính xác tương đối tốt — đây là điểm nhấn mạnh nhất.

> **Số liệu chưa verify**: Các con số "Elephant phát hiện đúng 3/5", "lỗi Mice ~340%/~12%" xuất hiện trong mục 3 của file này là **ước tính minh họa** dựa theo xu hướng mô tả trong Section 3.2.1/3.2.2 của bài báo (cold elements tạo background noise ~7× overestimate khi λc=5 — theo đúng số liệu bài báo nêu), **chưa phải số liệu đã chạy thực tế**. Khi code xong `cms.py` và `cms_mixed.py`, nhóm phải chạy lại với bộ tham số ở bảng trên và **thay bằng số liệu thật** trước khi đưa vào slide/báo cáo.

---

## 5. Checklist chuẩn bị trước khi demo

```
[ ] Backend chạy ổn định, không lỗi 500
[ ] Dữ liệu demo đã test trước (không sinh random lúc thuyết trình)
[ ] Có 2-3 bộ tham số chuẩn bị sẵn (chính, khó, stress test)
[ ] Biểu đồ Chart.js render đúng trên máy sẽ dùng để demo
[ ] Có bản backup: screenshot/video demo phòng khi lỗi mạng/server
[ ] Đã thử cả 2 cấu hình (CMS gốc + Mixed) trước, ghi lại số liệu cụ thể
[ ] Chuẩn bị câu trả lời cho câu hỏi: "Nếu không biết trước phần tử nào hot/cold thì sao?"
```

---

## 6. Câu hỏi thường gặp khi demo (chuẩn bị trước)

**Q: Làm sao biết trước IP nào là Elephant để gán k=2?**
A: Trong demo này, biết trước để minh họa lý thuyết rõ ràng. Trong thực tế, có thể dùng kỹ thuật ước lượng sơ bộ (sampling) hoặc heuristic (IP gửi packet liên tục trong N giây đầu được coi là candidate hot) — đây là hướng mở rộng, bài báo gốc không đề cập sâu (thuộc Open Problems).

**Q: Tại sao không dùng k=(3,14;0.885) như bài báo đề xuất ban đầu?**
A: Vì k=(2,5;0.5) cho kết quả thực nghiệm gần tương đương nhưng đơn giản hơn nhiều để cài đặt — đây cũng chính là điều bài báo ghi nhận ở Section 3.1.1.

**Q: Demo này có dùng dữ liệu mạng thực tế không?**
A: Không, dữ liệu được sinh giả lập theo đúng mô hình Step Distribution mà bài báo dùng để thực nghiệm (Section 3.2), đảm bảo tái hiện chính xác điều kiện trong bài báo gốc.

---

*Tài liệu kịch bản demo — dựa trên Fusy, É., & Kucherov, G. (2023), Section 3.2 (Step Distribution)*
*Link bài báo gốc: http://igm.univ-mlv.fr/~fusy/Articles/countmin-exp.pdf*
