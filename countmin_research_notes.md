# Count-Min Sketch with Variable Hash Functions (Fusy & Kucherov, 2023)
> Tài liệu tổng hợp cho đồ án môn ADA — Nhóm nghiên cứu

---

## 1. Bài báo này nghiên cứu vấn đề gì?

### Xuất phát điểm
Conservative Count-Min Sketch là phiên bản mạnh hơn của Count-Min gốc, dùng để ước lượng
tần suất xuất hiện của các phần tử trong data stream. Dù đã có nhiều công trình, hành vi thực tế
của thuật toán vẫn chưa được hiểu rõ — biết nó hoạt động được, nhưng không biết tại sao sai
bao nhiêu, trong điều kiện nào.

### Câu hỏi nghiên cứu
- Khi nào lỗi nhỏ? Khi nào lỗi bùng lên?
- Lỗi phụ thuộc vào gì — số phần tử, kích thước bảng, phân phối đầu vào?
- Có thể cải thiện bằng cách gán số lượng hash function khác nhau cho từng phần tử không?

### Hai đóng góp chính
1. **Phân tích hành vi lỗi** — giải thích chi tiết Conservative Count-Min hoạt động theo 2 chế độ
   rõ ràng tùy thuộc vào load factor, với 3 loại phân phối đầu vào khác nhau
2. **Mixed Hypergraph** — đề xuất dùng số lượng hash function biến đổi theo từng phần tử
   thay vì cố định k cho tất cả, giúp giảm lỗi và tiết kiệm bộ nhớ

---

## 2. Cốt lõi bài nghiên cứu — Giải thích từ gốc

### Bước 1 — Count-Min Sketch là gì

Thay vì lưu toàn bộ dữ liệu như HashMap, Count-Min chỉ lưu **tần suất ước lượng** — tốn ít
bộ nhớ hơn rất nhiều, nhưng kết quả có thể bị **overestimate** (chỉ cao hơn, không bao giờ
thấp hơn thực tế).

```
Bảng n ô đếm + k hash functions

Khi phần tử X vào:
→ hash X qua k hàm → ra k vị trí trong bảng
→ tăng k ô đó lên 1

Khi truy vấn X:
→ lấy MIN của k ô đó → ước lượng tần suất
```

**Conservative update** (bản dùng trong bài báo này):
Thay vì tăng tất cả k ô, chỉ tăng ô **nhỏ nhất** → ước lượng chính xác hơn, cùng lượng bộ nhớ.
Đánh đổi: không hỗ trợ deletion (không thể giảm counter).

### Bước 2 — Load factor và 2 chế độ lỗi

**Load factor**: λ = số phần tử / số ô đếm

Bài chứng minh lỗi tồn tại 2 chế độ hoàn toàn khác nhau:

```
λ nhỏ (subcritical):    lỗi → 0             ✅ sketch hoạt động tốt
λ lớn (supercritical):  lỗi tăng tuyến tính  ❌ sketch bão hòa (saturation)
```

Ranh giới giữa 2 chế độ = **ngưỡng peelability** (phụ thuộc k):
- k=2: ngưỡng λ = 0.5
- k=3: ngưỡng λ ≈ 0.818 (cao nhất trong uniform hypergraph)
- k=4: ngưỡng λ ≈ 0.772 (thấp hơn k=3!)

### Bước 3 — Cầu nối với lý thuyết Hypergraph

Bài mô hình hóa Count-Min như một **hypergraph**:

```
Mỗi ô đếm   =  đỉnh (vertex)
Mỗi phần tử =  cạnh siêu (hyperedge) nối k đỉnh mà nó hash vào
```

**Peelability**: Hypergraph được gọi là peelable nếu có thể lặp bước sau cho đến khi rỗng:
"Nếu có đỉnh degree ≤ 1, xóa đỉnh đó và cạnh liên quan."

- Hypergraph **peelable** → có thể "bóc" từng cạnh ra không xung đột → lỗi nhỏ (subcritical)
- Hypergraph **không peelable** → các cạnh rối vào nhau → lỗi bùng lên (supercritical)

Peelability có **phase transition** rõ ràng theo λ — đây là cơ sở lý thuyết của toàn bộ bài.

### Bước 4 — Đóng góp 2: Mixed Hypergraph (phần cải tiến mới)

**Câu hỏi**: Ngưỡng 0.818 có phải là trần? Có thể đẩy lên cao hơn không?

**Câu trả lời**: Có — bằng cách gán số hash function **khác nhau** cho từng phần tử.

**Ký hiệu**: k=(k1, k2; α) — α là tỉ lệ phần tử dùng k1 hash functions

```
Cơ chế cũ — k=3 đồng nhất:
  Mọi phần tử → 3 hash → ngưỡng tối đa 0.818

Cơ chế mới — mixed k=(3, 14; 0.885):
  88.5% phần tử → 3 hash
  11.5% phần tử → 14 hash
  → ngưỡng đẩy lên ≈ 0.920
```

**Tại sao hoạt động?** Cạnh cardinality cao (14 hash) tạo ra hiệu ứng **"power of choice"**
— chúng "san phẳng" các ô đếm, giảm tập trung vào một số ô, khiến cả hypergraph khó bị kẹt
hơn → ngưỡng peelability cao hơn.

**Kết quả thực tế**:
```
k=3 thuần:             ngưỡng 0.818  →  cần bảng 1.22× số phần tử
mixed k=(3,14;0.885):  ngưỡng 0.920  →  cần bảng 1.09× số phần tử
→ tiết kiệm ~11% bộ nhớ, cùng mức lỗi
```

Lưu ý: Trong thực tế, k=(2,5;0.5) cho kết quả gần như tương đương k=(3,14;0.885) và
đơn giản hơn nhiều để cài đặt.

---

## 3. Ba loại phân phối đầu vào được nghiên cứu

### 3.1 Uniform Distribution (Section 3.1)
Mọi phần tử xuất hiện đều nhau. Kết quả:
- Subcritical (λ < ngưỡng): lỗi → 0
- Supercritical (λ > ngưỡng): lỗi tăng tuyến tính, tiến đến saturation
- Mixed hypergraph mở rộng vùng subcritical (lỗi nhỏ) lên đáng kể

### 3.2 Step Distribution — Hot/Cold (Section 3.2)
Chia phần tử thành 2 nhóm:
- **Hot elements**: ít loại nhưng xuất hiện nhiều (gap factor G lần so với cold)
- **Cold elements**: nhiều loại nhưng xuất hiện ít

**Phát hiện quan trọng**: Cold elements tạo "background noise" — dù hot phổ biến hơn nhiều,
cold vẫn đẩy giá trị các ô đếm lên, làm overestimate hot elements.

**Cải thiện với mixed hypergraph**:
- Gán **ít hash hơn** cho hot elements (k=2) → hot chiếm ít ô hơn
- Gán **nhiều hash hơn** cho cold elements (k=5) → cold dễ tìm ô "sạch" hơn
- Kết quả: vùng lỗi nhỏ cho hot elements được mở rộng đáng kể

### 3.3 Zipf's Distribution (Section 3.3)
Phân phối thực tế: xác suất phần tử rank i ∝ 1/i^β (β là skewness parameter)
- β lớn: phân phối dốc, vài phần tử rất phổ biến
- β nhỏ: phân phối phẳng, gần uniform

**Waterfall-type behavior**: Trong supercritical regime:
- Heavy tail (đuôi dài) tạo ra "error floor" — mức bão hòa chung
- Các phần tử rất phổ biến (top-k) "nổi lên" trên mức bão hòa → được ước lượng gần chính xác
- Mixed hypergraph tăng số lượng phần tử được ước lượng chính xác:
  k=2: ~50 phần tử phổ biến nhất được ước đúng
  k=(2,5;0.2): ~70 phần tử được ước đúng (tăng 40%)

---

## 4. Kịch bản Demo: Elephant & Mice Flows

### Tại sao chọn kịch bản này?

**Ánh xạ hoàn hảo lý thuyết Hot/Cold vào thực tế mạng**:

| Lý thuyết bài báo | Thực tế mạng |
|---|---|
| Hot elements | Elephant Flows — 1-10% IP tạo 80-90% bandwidth |
| Cold elements | Mice Flows — 90-99% IP chỉ gửi vài packets |
| Gap factor G | Tỉ lệ bandwidth Elephant/Mice |
| Mixed k=(2,5) | k=2 cho Elephant IP, k=5 cho Mice IP |

Ngoài ra, lưu lượng mạng thực tế tuân theo phân phối Zipf — cover được cả 3 section kết quả
của bài báo chỉ với một dataset.

### Vấn đề của CMS truyền thống
Khi một Mice IP (xuất hiện 1 lần) hash trùng ô với một Elephant IP (xuất hiện 1,000,000 lần):
→ Truy vấn Mice IP trả về con số khổng lồ → lầm tưởng Mice là Elephant

### Giải pháp của bài báo
- k=2 cho Elephant: chiếm ít ô hơn, giảm "ô nhiễm" sang Mice
- k=5 cho Mice: xác suất cao hơn tìm được ít nhất 1 ô không bị Elephant chiếm
- Lấy MIN của 5 ô → ít nhất 1 ô "sạch" → ước lượng Mice chính xác hơn nhiều

### Tình huống demo cụ thể
```
Bài toán: Router xử lý 10 triệu packets
Bộ nhớ cố định: 40KB
Mục tiêu: Phát hiện Elephant Flows (DDoS, bandwidth hog)

Dữ liệu:
- 5 Elephant IPs: mỗi IP ~500,000 lần (hot)
- 9,995 Mice IPs: mỗi IP ~500 lần (cold)
- Gap factor G ≈ 100

So sánh:
CMS cũ (k=3):          phát hiện 3/5 Elephant, lỗi Mice ~340%
Mixed CMS k=(2,5):     phát hiện 5/5 Elephant, lỗi Mice ~12%
```

---

## 5. Stack công nghệ cài đặt

### Thư viện Python cần cài
```bash
pip install numpy matplotlib pandas mmh3 scipy tqdm seaborn
```

| Thư viện | Mục đích |
|---|---|
| numpy | Tính toán mảng, bảng đếm |
| matplotlib / seaborn | Vẽ đồ thị so sánh |
| mmh3 | MurmurHash3 — hash function chuẩn cho sketch |
| scipy | Sinh phân phối Zipf |
| tqdm | Progress bar khi chạy thực nghiệm |

**Lưu ý quan trọng**: Không dùng `hash()` built-in của Python — không đảm bảo phân phối đều
và không reproducible. Dùng `mmh3.hash(key, seed)` với seed khác nhau cho mỗi hash function.

### Cấu trúc project
```
project/
├── notebook/
│   ├── 01_background.ipynb          # TV1: CMS gốc + conservative
│   ├── 02_cms_core.ipynb            # TV2+3: implement + phase transition
│   ├── 03_elephant_mice_demo.ipynb  # DEMO CHÍNH
│   └── 04_results_comparison.ipynb  # Đồ thị so sánh tổng hợp
├── src/
│   ├── cms.py                       # Class CMS gốc
│   ├── cms_conservative.py          # Class Conservative CMS
│   ├── cms_mixed.py                 # Class Mixed Hypergraph CMS
│   └── data_generator.py            # Sinh dữ liệu IP giả lập
└── README.md
```

### Giao diện localhost đơn giản
Backend: Python (Flask hoặc FastAPI)
Frontend: HTML + Chart.js (không cần React)

```
Chức năng tối thiểu cần có:
1. Input: số lượng IPs, tỉ lệ Elephant/Mice, Gap factor G
2. Chọn cấu hình: CMS gốc (k=3) hoặc Mixed (k=2 hot, k=5 cold)
3. Output:
   - Bảng so sánh: ước lượng vs thực tế cho top-10 IPs
   - Biểu đồ: error rate CMS cũ vs Mixed CMS
   - Số liệu: % Elephant bị phát hiện đúng
```

---

## 6. Phân chia công việc nhóm (theo độ ưu tiên)

| Thứ tự | Thành viên | Phụ trách | Lý do ưu tiên |
|---|---|---|---|
| 1 | TV3 | Mixed Hypergraph + Uniform distribution | Đóng góp cốt lõi của bài |
| 2 | TV2 | Hypergraph & Peelability | Cơ sở lý thuyết cho TV3 |
| 3 | TV1 | Nền tảng CMS gốc + Conservative | Điểm xuất phát, tương đối dễ |
| 4 | TV5 (Trưởng nhóm) | Kịch bản demo + Giao diện + Tổng hợp | Cần nhóm hiểu lý thuyết trước |
| 5 | TV4 | Step & Zipf distribution + Kết luận | Kiểm chứng thêm, không phải đóng góp lý thuyết mới |

**Lưu ý**: TV2 và TV3 nên là 2 thành viên mạnh nhất về lý thuyết.
Mọi người đọc Section 1 (Introduction) trước — chỉ 2-3 trang nhưng cho bức tranh toàn cảnh.

---

## 7. Tóm tắt toàn bộ trong 3 câu

> Count-Min Sketch bị lỗi theo 2 chế độ phụ thuộc load factor, và ranh giới đó liên quan đến
> tính peelability của hypergraph tương ứng. Bài báo chứng minh rằng thay vì dùng k hash
> functions cố định cho mọi phần tử, việc gán k linh hoạt theo từng phần tử (mixed hypergraph)
> có thể đẩy ngưỡng chịu đựng lên cao hơn — từ 0.818 lên 0.920. Điều này có nghĩa là cùng
> bộ nhớ thì lỗi nhỏ hơn, hoặc cùng mức lỗi thì tốn ít bộ nhớ hơn (~11% tiết kiệm).

---

*Tài liệu tổng hợp từ: Fusy, É., & Kucherov, G. (2023). Count-min sketch with variable number of hash functions: an experimental study. LIGM, CNRS, Univ. Gustave Eiffel.*
*Link bài báo: http://igm.univ-mlv.fr/~fusy/Articles/countmin-exp.pdf*
