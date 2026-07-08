# Mục lục Báo cáo & Slide
## Đồ án môn ADA — Count-Min Sketch with Variable Hash Functions
> Nguồn gốc: Fusy, É., & Kucherov, G. (2023). *Count-min sketch with variable number of hash functions: an experimental study*. LIGM, CNRS, Univ. Gustave Eiffel.
> Link PDF: http://igm.univ-mlv.fr/~fusy/Articles/countmin-exp.pdf

---

# PHẦN A — MỤC LỤC BÁO CÁO (Word/Docs)

---

## Chương 1: Giới thiệu
> Nguồn: Section 1 — Introduction (trang 1-2, bài báo)

### 1.1 Bối cảnh và động lực nghiên cứu
- Count-Min Sketch là gì và ứng dụng trong thực tế
- Các bài toán thực tế: network traffic monitoring, heavy hitters detection, bioinformatics
- Hạn chế của Count-Min Sketch truyền thống với k cố định
- Tại sao Conservative Count-Min ra đời và vẫn còn vấn đề chưa giải quyết được

### 1.2 Mục tiêu nghiên cứu của bài báo
- Mục tiêu 1: Phân tích chi tiết hành vi lỗi của Conservative Count-Min
- Mục tiêu 2: Cải tiến bằng số lượng hash function biến đổi (variable number of hash functions)

### 1.3 Phạm vi và giới hạn của báo cáo này
- Những gì nhóm tái hiện được
- Những gì nhóm không đề cập (phần toán học thuần túy)

---

## Chương 2: Cơ sở lý thuyết
> Nguồn: Section 2 — Background and Related Work (trang 2-5, bài báo)

### 2.1 Count-Min Sketch — Định nghĩa và cơ chế
> Nguồn: Section 2.1 — Conservative Count-Min: definitions

- Cấu trúc dữ liệu: mảng đếm A kích thước n + tập hash functions
- Cơ chế insert: cập nhật k ô bằng hash functions h₁...hₖ
- Cơ chế query: trả về MIN của k ô tương ứng
- Conservative update: chỉ tăng ô nhỏ nhất thay vì tất cả k ô
- Định nghĩa lỗi tương đối: errH,I(e) = (c(e) − occ(e)) / occ(e)
- Định nghĩa load factor: λ = |E| / n

### 2.2 Các công trình liên quan trước đây
> Nguồn: Section 2.2 — Analysis of conservative Count-Min: prior works

- Bianchi et al. [8] — phân tích growth rate bằng Markov chains
- Approx bằng hierarchy of Bloom filters [20]
- Recent works [5, 4] — error bounds theo element probabilities
- Fusy & Kucherov 2022 [24] — kết nối với random hypergraphs (nền tảng bài báo này)

### 2.3 Hash Hypergraph — Mô hình hóa Count-Min
> Nguồn: Section 2.3 — Hash hypergraph

- Định nghĩa hypergraph H = (V, E): V = ô đếm, E = phần tử
- Ký hiệu Hₙ,ₘ và Hᵏₙ,ₘ (k-uniform hypergraph)
- Erdős-Rényi random hypergraph model
- Tại sao hypergraph lại mô hình hóa được Count-Min

### 2.4 Peelability và Phase Transition
> Nguồn: Section 2.4 — Hypergraph peelability and phase transition of error

- Định nghĩa peelability: xóa đỉnh degree ≤ 1 cho đến khi rỗng
- Peelability threshold λₖ: ngưỡng phase transition
  - k=2: λ₂ = 0.5
  - k=3: λ₃ ≈ 0.818 (cao nhất trong uniform hypergraph)
  - k=4: λ₄ ≈ 0.772
- **Theorem 1** [Fusy & Kucherov 2022]: nếu λ < λₖ → lỗi o(1) w.h.p.
- Subcritical regime (λ < λₖ): lỗi → 0
- Supercritical regime (λ > λₖ): lỗi = Θ(1)

### 2.5 Mixed Hypergraph — Ý tưởng cốt lõi
> Nguồn: Section 2.5 — Variable number of hash functions: mixed hypergraphs

- Ý tưởng: gán số hash function khác nhau cho các phần tử khác nhau
- Ký hiệu k=(k₁,k₂) và k=(k₁,k₂;α): α là tỉ lệ cạnh cardinality k₁
- Kết quả từ [32]: mixed hypergraph có thể đạt ngưỡng peelability cao hơn
  - Ví dụ: k=(3,21; 0.887) → ngưỡng ≈ 0.920 > 0.818
- So sánh với weighted Bloom filters [9] — ý tưởng tương tự

---

## Chương 3: Kết quả thực nghiệm
> Nguồn: Section 3 — Results (trang 5-15, bài báo)

### 3.1 Phân phối đều (Uniform Distribution)
> Nguồn: Section 3.1 — Uniform distribution

#### 3.1.1 Subcritical Regime
> Nguồn: Section 3.1.1 + Theorem 2

- **Theorem 2**: mở rộng Theorem 1 sang mixed cardinalities
- Minh họa qua Figure 1: so sánh k=2, k=3, mixed k=(3,14;0.885)
- Phase transition của mixed hypergraph tại λ ≈ 0.898
- Thực tế: k=(2,5;0.5) cho kết quả tương đương k=(3,14;0.885)
- Ý nghĩa: tăng load factor trong khi giữ lỗi nhỏ → tiết kiệm bộ nhớ

#### 3.1.2 Supercritical Regime
> Nguồn: Section 3.1.2

- Hành vi khi λ vượt ngưỡng: saturation phenomenon
- Figure 2: so sánh k=1, k=2 trong supercritical regime
- Power of choice effect: k=2 phân bố đều hơn k=1
- Saturation: k=3 đạt saturation tại λ ≈ 6

#### 3.1.3 Mixed Hypergraph trong Supercritical Regime
> Nguồn: Section 3.1.3

- Figure 3: k=1 vs mixed k=(1,3;0.8) trong supercritical
- Mixed vẫn cải thiện được lỗi trước khi đạt saturation point (λ < 50)

### 3.2 Phân phối Step — Hot/Cold Elements
> Nguồn: Section 3.2 — Step distribution

#### 3.2.1 Tương tác giữa Hot và Cold Elements
> Nguồn: Section 3.2.1

- Định nghĩa gap factor G = tỉ lệ xác suất hot/cold
- Cold elements tạo "background noise" ảnh hưởng đến hot elements
- Figure 4a (G=20): cold gây lỗi đáng kể ngay cả khi λₕ nhỏ
- Figure 4b (G=50): gap lớn hơn → cold ảnh hưởng ít hơn
- Figure 4c (G=5): background level của cold > true count hot → overestimate nặng

#### 3.2.2 Mixed Hypergraph với Step Distribution
> Nguồn: Section 3.2.2

- Gán k nhỏ hơn cho hot (k=2), k lớn hơn cho cold (k=5)
- Figure 5: k=3 đồng nhất vs k=(2,5) mixed — vùng lỗi nhỏ mở rộng rõ rệt
- Giải thích: cold edge cardinality cao → xác suất cao tìm ô không bị hot chiếm

#### 3.2.3 Saturation trong Supercritical Regime
> Nguồn: Section 3.2.3

- Figure 6: convergence của hot và cold estimates theo tổng load λ
- So sánh: 2-uniform, 3-uniform, (2,5)-mixed
- Mixed: convergence xảy ra ngay sau vùng lỗi nhỏ của hot

### 3.3 Phân phối Zipf
> Nguồn: Section 3.3 — Zipf's distribution

- Định nghĩa: xác suất phần tử rank i ∝ 1/iᵝ, β là skewness parameter
- β=0: giảm về uniform; β lớn: phân phối dốc
- **Waterfall-type behavior** [quan sát từ Bianchi et al. 8]:
  - Error floor do heavy tail tạo ra
  - Heavy hitters "nổi lên" trên error floor → ước lượng gần chính xác
- Figure 7: β=0.7, 0.5, 0.3 — waterfall rõ hơn khi β tăng
- Figure 8: mixed k=(2,5;0.2) mở rộng vùng heavy hitters được ước đúng

---

## Chương 4: Ứng dụng thực tế — Elephant & Mice Flow Detection

### 4.1 Bài toán Elephant & Mice Flows trong mạng
- Định nghĩa Elephant Flows: 1-10% IP tạo 80-90% bandwidth
- Định nghĩa Mice Flows: 90-99% IP chỉ gửi vài packets
- Ánh xạ: Elephant = Hot elements, Mice = Cold elements, Gap factor G ≈ 100

### 4.2 Vấn đề của CMS truyền thống trong kịch bản này
- Va chạm hash giữa Mice và Elephant → overestimate Mice
- Cold elements tạo background noise → sai lệch ước lượng Elephant

### 4.3 Giải pháp Mixed Hypergraph k=(2,5)
- k=2 cho Elephant IPs: chiếm ít ô hơn, giảm nhiễu sang Mice
- k=5 cho Mice IPs: xác suất cao tìm ô "sạch" hơn
- Kết quả: lỗi Mice giảm từ ~340% xuống ~12%

---

## Chương 5: Kết luận và Hướng phát triển
> Nguồn: Section 4 — Conclusions (trang 15-16, bài báo)

### 5.1 Tổng kết đóng góp
- Đóng góp 1: Phân tích chi tiết hành vi lỗi Conservative Count-Min với 3 phân phối
- Đóng góp 2: Chứng minh mixed hypergraph cải thiện lỗi và tiết kiệm bộ nhớ

### 5.2 Open Problems — Vấn đề còn để ngỏ
> Nguồn: phần cuối Section 4

- Chứng minh lý thuyết (không chỉ thực nghiệm) cho Theorem 2 trong supercritical regime
- Phân tích saturation phenomenon cho phân phối Zipf tổng quát
- Mở rộng sang mixed hypergraph với nhiều hơn 2 loại cardinality
- Phân tích chính xác "intermediate regime" ngay sau phase transition

### 5.3 Hướng phát triển của nhóm
- Tái hiện thực nghiệm với dataset network traffic thực tế
- Cài đặt giao diện visualize phase transition động
- So sánh với các biến thể CMS khác (Learned CMS [26])

---

## Tài liệu tham khảo chính
> Từ References của bài báo

- [15] Cormode & Muthukrishnan (2005) — Count-Min gốc
- [24] Fusy & Kucherov (2022) — Hypergraph & peelability analysis
- [32] Theyssier et al. — Mixed hypergraph peelability threshold
- [8]  Bianchi et al. (2012) — Growth rate analysis, waterfall behavior
- [21] Estan & Varghese — Conservative update, network monitoring
- [9]  Bruck et al. — Weighted Bloom filters

---
---

# PHẦN B — MỤC LỤC SLIDE (6×6 rule — tối đa 6 dòng, 6 từ/dòng)

> Quy tắc 6×6: mỗi slide tối đa 6 bullet, mỗi bullet tối đa 6 từ.
> Slide chỉ chứa từ khóa + hình — nội dung đầy đủ nằm trong docs và lời thuyết trình.

---

### SLIDE 1 — Trang bìa
```
Tiêu đề:  Count-Min Sketch — Variable Hash Functions
Phụ đề:   Fusy & Kucherov, 2023
Nhóm:     [Tên nhóm] — Môn ADA
Trường:   [Tên trường]
```

---

### SLIDE 2 — Vấn đề nghiên cứu
> Nguồn: Section 1, trang 1
```
• Data stream: đếm tần suất realtime
• HashMap: tốn bộ nhớ khi dữ liệu lớn
• Count-Min Sketch: giải pháp tiết kiệm
• Nhưng: hành vi lỗi chưa được hiểu rõ
• Câu hỏi: khi nào lỗi nhỏ? Khi nào lớn?
• Giải pháp: variable hash functions
```

---

### SLIDE 3 — Count-Min Sketch là gì
> Nguồn: Section 2.1, trang 2
```
• Bảng n ô đếm + k hash functions
• Insert: hash → tăng k ô tương ứng
• Query: trả về MIN của k ô
• Conservative: chỉ tăng ô nhỏ nhất
• Lỗi: chỉ overestimate, không underestimate
• Load factor: λ = số phần tử / số ô
```
> [Hình minh họa: bảng CMS + mũi tên hash]

---

### SLIDE 4 — Hash Hypergraph Model
> Nguồn: Section 2.3–2.4, trang 3-4
```
• Ô đếm = đỉnh (vertex)
• Phần tử = cạnh siêu (hyperedge)
• Peelability: xóa đỉnh degree ≤ 1
• k=2: ngưỡng λ = 0.5
• k=3: ngưỡng λ ≈ 0.818 (tốt nhất)
• Vượt ngưỡng → lỗi bùng lên
```
> [Hình: hypergraph peelable vs non-peelable]

---

### SLIDE 5 — Hai chế độ lỗi (Phase Transition)
> Nguồn: Theorem 1 [24] + Section 3.1, trang 5-6
```
• Subcritical (λ < λₖ): lỗi → 0 ✅
• Supercritical (λ > λₖ): lỗi tăng ❌
• Saturation: toàn bộ counter cùng mức
• k=3: saturation tại λ ≈ 6
• Đây là "giải phẫu" cốt lõi bài báo
• [Figure 1 từ bài báo]
```
> [Hình: Figure 1 — error vs load factor]

---

### SLIDE 6 — Đóng góp chính: Mixed Hypergraph
> Nguồn: Section 2.5 + Theorem 2, trang 4-6
```
• Ký hiệu: k=(k₁, k₂; α)
• α phần tử dùng k₁ hash functions
• k=(3,14;0.885): ngưỡng ≈ 0.920
• So với k=3 thuần: chỉ đạt 0.818
• Thực tế: k=(2,5;0.5) tương đương
• Tiết kiệm ~11% bộ nhớ, cùng lỗi
```
> [Hình: Figure 1 — đường mixed vs uniform]

---

### SLIDE 7 — Tại sao Mixed hoạt động?
> Nguồn: Section 3.1.3, trang 7-8
```
• Power of choice effect
• Cạnh cardinality cao "san phẳng" counters
• Giảm tập trung vào một số ô đếm
• Hypergraph khó bị kẹt hơn
• Ngưỡng peelability được đẩy lên cao
• [Figure 3 từ bài báo]
```
> [Hình: Figure 3 — k=1 vs mixed k=(1,3;0.8)]

---

### SLIDE 8 — Step Distribution: Hot vs Cold
> Nguồn: Section 3.2, trang 8-12
```
• Hot: ít loại, xuất hiện nhiều lần
• Cold: nhiều loại, xuất hiện ít lần
• Gap factor G = tỉ lệ tần suất hot/cold
• Cold tạo "background noise" cho hot
• G nhỏ: cold làm sai lệch hot nghiêm trọng
• [Figure 4 từ bài báo]
```
> [Hình: Figure 4c — G=5, hot bị overestimate]

---

### SLIDE 9 — Mixed Hypergraph giải quyết Hot/Cold
> Nguồn: Section 3.2.2, trang 11
```
• k=2 cho hot: chiếm ít ô hơn
• k=5 cho cold: dễ tìm ô "sạch"
• Vùng lỗi nhỏ của hot mở rộng rõ
• Cold ít ảnh hưởng hot hơn
• [Figure 5 từ bài báo]
• Áp dụng trực tiếp: Elephant/Mice flows
```
> [Hình: Figure 5 — k=3 vs k=(2,5) mixed]

---

### SLIDE 10 — Phân phối Zipf & Waterfall Behavior
> Nguồn: Section 3.3, trang 12-14
```
• Zipf: xác suất rank i ∝ 1/iᵝ
• Thực tế: network traffic, web search
• Heavy tail tạo "error floor"
• Heavy hitters nổi lên trên error floor
• Được ước lượng gần chính xác ✅
• Mixed mở rộng vùng heavy hitters
```
> [Hình: Figure 7 — waterfall behavior]

---

### SLIDE 11 — Demo: Elephant & Mice Flow Detection
```
• Elephant = Hot: 5 IPs, 500K packets/IP
• Mice = Cold: 9,995 IPs, 500 packets/IP
• Gap factor G = 100
• Bộ nhớ cố định: 40KB (n=5,000 ô)
• CMS gốc k=3: phát hiện 3/5 Elephant
• Mixed k=(2,5): phát hiện 5/5 Elephant ✅
```

---

### SLIDE 12 — Kết quả Demo So sánh
```
• CMS gốc: lỗi Mice trung bình ~340%
• Mixed CMS: lỗi Mice trung bình ~12%
• Cùng kích thước bảng 40KB
• Elephant detection: 60% → 100%
• Mice accuracy: cải thiện 28× lần
• [Biểu đồ so sánh từ demo]
```
> [Hình: biểu đồ bar chart CMS gốc vs Mixed]

---

### SLIDE 13 — Kết luận
> Nguồn: Section 4 — Conclusions, trang 15
```
• Đóng góp 1: giải phẫu hành vi lỗi CMS
• Đóng góp 2: mixed hypergraph cải thiện
• Ngưỡng: 0.818 → 0.920 (+12.5%)
• Bộ nhớ: tiết kiệm ~11% cùng mức lỗi
• Ứng dụng: network monitoring, DDoS
• Phù hợp phân phối: Step, Zipf, Uniform
```

---

### SLIDE 14 — Open Problems & Hướng phát triển
> Nguồn: Section 4, phần cuối bài báo
```
• Chứng minh lý thuyết supercritical regime
• Saturation với Zipf distribution tổng quát
• Mixed hypergraph > 2 loại cardinality
• Kết hợp với Learned CMS [26]
• Dataset thực tế: CAIDA network traces
• Mở rộng: streaming với deletion support
```

---

## Ghi chú phân công slide theo thành viên

| Slide | Nội dung | Thành viên phụ trách |
|---|---|---|
| 1, 2 | Bìa + Vấn đề | TV5 (Trưởng nhóm) |
| 3, 4 | CMS gốc + Hypergraph | TV1 + TV2 |
| 5, 6, 7 | Phase Transition + Mixed | TV2 + TV3 |
| 8, 9 | Step Distribution | TV4 |
| 10 | Zipf Distribution | TV4 |
| 11, 12 | Demo | TV5 |
| 13, 14 | Kết luận + Open Problems | TV5 |

---

*Mục lục tổng hợp từ: Fusy, É., & Kucherov, G. (2023). Count-min sketch with variable number of hash functions: an experimental study.*
*Link bài báo gốc: http://igm.univ-mlv.fr/~fusy/Articles/countmin-exp.pdf*
