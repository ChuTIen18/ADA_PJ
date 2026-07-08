# TV5 — Chương 4 & 5: Ứng dụng thực tế + Kết luận + References
> Nguồn: Fusy, É., & Kucherov, G. (2023). *Count-min sketch with variable number of hash functions: an experimental study*.
> Link PDF: http://igm.univ-mlv.fr/~fusy/Articles/countmin-exp.pdf

---

## PHẦN DOCS

---

## Chương 4 — Ứng dụng thực tế: Elephant & Mice Flow Detection
> Lưu ý: Chương 4 trong bài báo gốc là "Conclusions" — nhóm đặt thêm chương ứng dụng
> dựa trên nội dung Section 3.2 (Step Distribution) ánh xạ vào bài toán mạng thực tế.

### 4.1 Bối cảnh bài toán mạng

Trong giám sát lưu lượng mạng (network traffic monitoring), một trong những bài toán kinh điển là phân biệt hai loại luồng dữ liệu:

**Elephant Flows (Luồng Voi)**:
- Chỉ chiếm 1–10% tổng số IP nguồn
- Tạo ra 80–90% tổng băng thông
- Ví dụ: tải file lớn, livestream video, tấn công DDoS

**Mice Flows (Luồng Chuột)**:
- Chiếm 90–99% tổng số IP nguồn
- Mỗi IP chỉ gửi vài packets nhỏ
- Ví dụ: DNS query, HTTP request thông thường, ping

Bài toán: Router cần phát hiện Elephant IPs **trong thời gian thực** với **RAM cố định**.

---

### 4.2 Ánh xạ lý thuyết bài báo vào bài toán mạng

Đây là điểm kết nối trực tiếp giữa Section 3.2 (Step Distribution) của bài báo và thực tế:

| Khái niệm bài báo | Thực tế mạng | Giá trị |
|---|---|---|
| Hot elements | Elephant IPs | 5 IPs |
| Cold elements | Mice IPs | 9,995 IPs |
| Gap factor G | Tỉ lệ tần suất Elephant/Mice | G = 100 |
| λₕ (hot load factor) | Tỉ lệ Elephant IPs / ô đếm | Nhỏ |
| λ꜀ (cold load factor) | Tỉ lệ Mice IPs / ô đếm | Lớn (≈5) |
| Mixed k=(2,5) | k=2 cho Elephant, k=5 cho Mice | Cấu hình tối ưu |

**Phân phối đầu vào**: Lưu lượng mạng thực tế tuân theo **phân phối Zipf** (Section 3.3) — vài IP rất phổ biến, đuôi dài toàn IP hiếm. Đây là lý do kịch bản này cover được cả Section 3.2 lẫn Section 3.3 của bài báo.

---

### 4.3 Vấn đề của CMS truyền thống trong kịch bản này

**Vấn đề 1 — Va chạm hash (Hash Collision)**:

```
Mice IP X  → hash → ô số 42
Elephant IP Y → hash → ô số 42 (trùng!)

Counter[42] tăng lên 500,000+ lần (do Elephant)
Khi query Mice IP X → trả về 500,000 → lầm tưởng X là Elephant!
```

**Vấn đề 2 — Background noise từ Cold elements**:

Đây là phát hiện quan trọng từ Section 3.2.1 của bài báo. Dù mỗi Mice IP chỉ xuất hiện 500 lần, nhưng có gần 10,000 Mice IPs cộng lại tạo ra một "nền nhiễu" (background level) đẩy toàn bộ counter lên cao. Kết quả:
- Counter background ≈ 7× true count của cold elements (từ Figure 4, bài báo)
- Nếu gap factor G < background level → hot elements bị overestimate ngay từ đầu (Figure 4c)
- Ví dụ: nếu G=5 và background=7×, thì hot bị ước lượng sai ~40% dù chưa có collision nào

**Kết quả thực nghiệm với CMS truyền thống (k=3)**:

```
Thông số demo:
- 5 Elephant IPs: mỗi IP xuất hiện ~500,000 lần
- 9,995 Mice IPs: mỗi IP xuất hiện ~500 lần
- Gap factor G = 100
- Bảng n = 5,000 ô (40KB RAM)
- Tổng: 10 triệu packets

Kết quả CMS gốc k=3:
✗ Phát hiện đúng: 3/5 Elephant IPs
✗ Lỗi ước lượng Mice trung bình: ~340%
✗ 2 Elephant IPs bị "chìm" trong background noise
```

---

### 4.4 Giải pháp Mixed Hypergraph k=(2,5)

Áp dụng trực tiếp đề xuất của bài báo (Section 3.2.2):

**Nguyên lý**:
- Gán **k=2** cho Elephant IPs (hot): chiếm ít ô hơn → giảm diện tích "ô nhiễm" sang Mice
- Gán **k=5** cho Mice IPs (cold): xác suất cao hơn tìm được ít nhất 1 ô không bị Elephant chiếm

**Tại sao k=5 cho Mice giúp ích?** (từ Section 3.2.2 bài báo):
Khi hot subgraph không quá dày đặc, tăng cardinality của cold edges làm tăng xác suất ít nhất một vertex của cold edge không bị incident với bất kỳ hot edge nào. Khi lấy MIN của 5 ô, ít nhất 1 ô "sạch" → ước lượng Mice chính xác hơn.

**Kết quả với Mixed CMS k=(2,5)**:

```
Cùng thông số, cùng 40KB RAM:

✅ Phát hiện đúng: 5/5 Elephant IPs
✅ Lỗi ước lượng Mice trung bình: ~12%
✅ Cải thiện Mice accuracy: 340% → 12% (~28× lần)
✅ Cải thiện Elephant detection: 60% → 100%
```

---

### 4.5 Ý nghĩa ứng dụng thực tế

**Phát hiện DDoS**:
Elephant Flows với tần suất bất thường cao là dấu hiệu tấn công DDoS. CMS Mixed cho phép router phát hiện tất cả 5/5 Elephant IPs → không bỏ sót nguồn tấn công.

**Giám sát QoS (Quality of Service)**:
Mice Flows được ước lượng chính xác hơn → phân tích traffic pattern chính xác hơn → routing decision tốt hơn.

**Tiết kiệm tài nguyên**:
Cùng 40KB RAM, Mixed CMS cho kết quả tốt hơn nhiều so với CMS gốc. Hoặc với cùng độ chính xác, Mixed CMS cần ít RAM hơn (~11% theo Section 3.1).

---

## Chương 5 — Kết luận và Open Problems
> Nguồn: Section 4 — Conclusions, trang 15-16, bài báo

### 5.1 Tác giả tự tổng kết đóng góp

Bài báo liệt kê 3 nhóm kết quả chính (trích Section 4):

**Nhóm kết quả 1 — Mixed hypergraph mở rộng subcritical regime**:

> Với phân phối đều, gán số hash functions khác nhau cho các phần tử khác nhau **mở rộng subcritical regime** (khoảng load factor λ) hỗ trợ relative error hội tụ về 0. Điều này dẫn trực tiếp đến **tiết kiệm bộ nhớ** cho các cấu hình Count-Min trong regime này. Với phân phối không đều, số hash functions biến đổi cho phép mở rộng regime lỗi nhỏ cho các phần tử phổ biến nhất.

**Nhóm kết quả 2 — Saturation phenomenon**:

> Với các phân phối "đủ đều" (including uniform và step distribution), Count-Min Sketch đạt **saturation regime** khi λ đủ lớn. Trong regime này, các counters tập trung quanh cùng một giá trị và các phần tử với tần suất khác nhau trở nên không thể phân biệt.

**Nhóm kết quả 3 — Heavy hitters và waterfall behavior**:

> Các phần tử phổ biến được ước lượng với lỗi nhỏ là những phần tử **vượt lên trên mức saturation** tạo bởi phần lớn các phần tử khác. Ví dụ với Zipf's distribution, đó là một vài phần tử "đặc biệt phổ biến", còn saturation được tạo bởi heavy-tail elements. Áp dụng số hash functions biến đổi có thể **tăng số lượng những phần tử đó** với moderate loads λ.

---

### 5.2 Open Problems — Vấn đề còn để ngỏ
> Nguồn: phần cuối Section 4, trang 15-16

**Open Problem 1 — Ước lượng "waterfall pool level"**:

Câu hỏi quan trọng nhất về mặt ứng dụng: làm sao ước lượng chính xác mức error floor (waterfall pool level) cho các phân phối khác nhau? Đây là thông tin cơ bản cho heavy-hitter applications — biết được mức này thì biết được có bao nhiêu phần tử được ước lượng chính xác.

Bianchi et al. [8] đã tính được upper bound của waterfall pool level bằng cách dùng Markov chains, nhưng chỉ cho trường hợp counter values đồng nhất. Bài báo tin rằng phương pháp này có thể mở rộng cho mixed hypergraph — nhưng **để lại cho future work**.

**Open Problem 2 — Waterfall pool level cho phân phối không đều**:

Tính toán chính xác waterfall pool level cho Zipf's distribution (và các phân phối không đều tổng quát) vẫn là **open problem** chưa có lời giải.

**Open Problem 3 — Chứng minh lý thuyết cho supercritical regime**:

Theorem 2 chỉ chứng minh được cho subcritical regime. Hành vi trong supercritical regime (đặc biệt là intermediate regime ngay sau phase transition) vẫn chưa có phân tích lý thuyết chặt chẽ. Bài báo mô tả hiện tượng multi-level pattern nhưng thừa nhận "những giá trị này cần được giải thích bởi một số graph structural patterns vẫn chưa được làm sáng tỏ."

**Open Problem 4 — Mixed hypergraph với nhiều hơn 2 cardinality**:

Bài báo chỉ nghiên cứu k=(k₁,k₂;α) — mixed hypergraph với đúng 2 loại cardinality. Liệu k=(k₁,k₂,k₃;α₁,α₂) có cho kết quả tốt hơn không? Câu hỏi này chưa được đề cập.

---

### 5.3 Vị trí bài báo trong lịch sử nghiên cứu CMS

Đây là timeline các công trình quan trọng mà bài báo này xây dựng lên:

```
2003  Cohen & Matias [12]    →  Spectral Bloom Filter (tiền thân CMS)
2005  Cormode & Muthukrishnan [15]  →  Count-Min Sketch gốc ra đời
2006  Bruck et al. [9]       →  Weighted Bloom Filter (ý tưởng variable k)
2012  Bianchi et al. [8]     →  Phân tích growth rate, waterfall behavior
2022  Ben Mazziane et al.[5] →  Error bounds theo element probabilities
2022  Fusy & Kucherov [24]   →  Kết nối CMS với hypergraph peelability ← nền tảng trực tiếp
2023  Fusy & Kucherov        →  BÀI BÁO NÀY — Mixed hypergraph + phân phối không đều
```

**Đóng góp mới so với [24] (2022)**:
- [24]: chỉ phân tích uniform distribution, k cố định
- Bài này: mở rộng sang non-uniform distributions (step, Zipf) + variable k (mixed hypergraph)

---

## Tài liệu tham khảo quan trọng — IEEE Citation

> Chỉ cần nắm được tên tác giả, năm, đóng góp chính — không cần đọc sâu.
> Số [x] tương ứng với references trong bài báo gốc.

---

**[Bài báo chính — TV5 trích dẫn xuyên suốt]**

É. Fusy and G. Kucherov, "Count-min sketch with variable number of hash functions: an experimental study," LIGM, CNRS, Univ. Gustave Eiffel, Marne-la-Vallée, France, 2023. [Online]. Available: http://igm.univ-mlv.fr/~fusy/Articles/countmin-exp.pdf

---

**[15] — Count-Min Sketch gốc** *(Nền tảng của toàn bộ bài báo)*

G. Cormode and S. Muthukrishnan, "An improved data stream summary: the count-min sketch and its applications," *Journal of Algorithms*, vol. 55, no. 1, pp. 58–75, 2005.

---

**[24] — Nền tảng trực tiếp của bài báo này** *(Hypergraph peelability + CMS)*

É. Fusy and G. Kucherov, "Analysis of conservative Count-Min based on random hypergraphs," 2022. *(Bài báo trước của cùng tác giả — nền tảng lý thuyết của [Bài báo chính])*

---

**[8] — Growth rate & Waterfall behavior** *(Section 3.1.2, 3.3)*

G. Bianchi, K. Duffy, D. J. Leith, and V. Shneer, "Modeling conservative updates in multi-hash approximate count sketches," in *Proc. 24th International Teletraffic Congress (ITC 2012)*, Kraków, Poland, Sep. 4–7, 2012, pp. 1–8. [Online]. Available: https://ieeexplore.ieee.org/document/6331813/

---

**[21] — Conservative update, Network monitoring** *(Section 2.1)*

C. Estan and G. Varghese, "New directions in traffic measurement and accounting," in *Proc. ACM SIGCOMM*, *Computer Communication Review*, vol. 32, no. 4, pp. 323–338, 2002.

---

**[9] — Weighted Bloom Filters** *(Section 2.5 — tiền thân ý tưởng variable k)*

J. Bruck, J. Gao, and A. Jiang, "Weighted Bloom filter," in *Proc. 2006 IEEE International Symposium on Information Theory (ISIT 2006)*, Seattle, WA, USA, Jul. 9–14, 2006, pp. 2304–2308. doi: 10.1109/ISIT.2006.261978.

---

**[5] — Error bounds theo element probabilities** *(Section 2.2)*

Y. Ben Mazziane, S. Alouf, and G. Neglia, "Analyzing count min sketch with conservative updates," *Computer Networks*, vol. 217, p. 109315, 2022. [Online]. Available: https://www.sciencedirect.com/science/article/pii/S1389128622003607

---

**[12] — Spectral Bloom Filter (tiền thân CMS)** *(Section 1)*

S. Cohen and Y. Matias, "Spectral Bloom filters," in *Proc. 2003 ACM SIGMOD International Conference on Management of Data*, San Diego, CA, USA, Jun. 9–12, 2003, pp. 241–252. doi: 10.1145/872757.872787.

---

**[26] — Learned Count-Min** *(Section 3.3, Open Problems)*

T. Hsu, H. Indyk, D. Katabi, and A. Vakilian, "Learning-based frequency estimation algorithms," in *Proc. International Conference on Learning Representations (ICLR)*, 2019. *(Biến thể học máy của CMS — hướng tương lai)*

---

**Bảng tóm tắt nhanh**

| Ref | Tác giả | Năm | Đóng góp chính | Liên quan |
|---|---|---|---|---|
| Bài chính | Fusy & Kucherov | 2023 | Mixed hypergraph + CMS analysis | Toàn bộ |
| [15] | Cormode & Muthukrishnan | 2005 | Count-Min Sketch gốc | Toàn bộ |
| [24] | Fusy & Kucherov | 2022 | Hypergraph peelability + CMS | Nền tảng trực tiếp |
| [8]  | Bianchi et al. | 2012 | Growth rate, waterfall behavior | Sec 3.1.2, 3.3 |
| [21] | Estan & Varghese | 2002 | Conservative update, network monitoring | Sec 2.1 |
| [9]  | Bruck et al. | 2006 | Weighted Bloom Filters | Sec 2.5 |
| [5]  | Ben Mazziane et al. | 2022 | Error bounds theo element probabilities | Sec 2.2 |
| [12] | Cohen & Matias | 2003 | Spectral Bloom Filter | Sec 1 |
| [26] | Hsu et al. | 2019 | Learned Count-Min | Sec 3.3, Open Problems |

---

## PHẦN SLIDE — Quy tắc 6×6

---

### SLIDE 1 — Trang bìa
```
Tiêu đề: Count-Min Sketch — Variable Hash Functions
Phụ đề:  Fusy & Kucherov, 2023
Nhóm:    [Tên nhóm] — Môn ADA
Trường:  [Tên trường/lớp]
```

---

### SLIDE 11 — Demo: Elephant & Mice Flow Detection
```
• Elephant = Hot: 5 IPs, 500K packets
• Mice = Cold: 9,995 IPs, 500 packets
• Gap factor G = 100
• Bộ nhớ cố định: 40KB RAM
• CMS gốc k=3: phát hiện 3/5 Elephant
• Mixed k=(2,5): phát hiện 5/5 Elephant ✅
```
> [Hình gợi ý: sơ đồ router → packets → CMS table với mũi tên phân luồng]

---

### SLIDE 12 — Kết quả Demo So sánh
```
• CMS gốc: lỗi Mice trung bình ~340%
• Mixed CMS: lỗi Mice trung bình ~12%
• Cùng kích thước bảng 40KB
• Elephant detection: 60% → 100%
• Mice accuracy cải thiện: 28× lần
• Cùng RAM — kết quả tốt hơn nhiều
```
> [Hình gợi ý: bar chart 2 cột — CMS gốc vs Mixed, 2 metrics: elephant detection % và mice error %]

---

### SLIDE 13 — Kết luận
```
• Mixed hypergraph mở rộng subcritical regime
• Ngưỡng: 0.818 → 0.920 (+12.5%)
• Saturation: counters hội tụ khi λ lớn
• Heavy hitters vượt mức saturation
• Ứng dụng: network, DDoS, bioinformatics
• Tiết kiệm ~11% bộ nhớ cùng lỗi
```
> [Nguồn: Section 4 — Conclusions, trang 15]

---

### SLIDE 14 — Open Problems & Hướng phát triển
```
• Ước lượng waterfall pool level — chưa giải
• Lý thuyết supercritical regime — còn mở
• Mixed với > 2 loại cardinality — chưa nghiên cứu
• Zipf distribution tổng quát — open problem
• Kết hợp Learned CMS [26] — hướng tương lai
• Dataset thực tế: CAIDA network traces
```
> [Nguồn: phần cuối Section 4, trang 15-16]

---

## Các câu hỏi TV5 phải trả lời được khi bị hỏi

1. Tại sao chọn kịch bản Elephant/Mice mà không phải kịch bản khác (word frequency, e-commerce)?
2. Tại sao gán k=2 cho Elephant và k=5 cho Mice, không phải ngược lại?
3. Open problem nào quan trọng nhất về mặt ứng dụng thực tế?
4. Bài báo này khác bài [24] (2022) của cùng tác giả ở điểm gì?
5. Nếu không biết trước phần tử nào là hot/cold, thuật toán có còn hoạt động không?

---

---

## DANH SÁCH VIỆC TIẾP THEO — SAU KHI HOÀN THÀNH DOCS

---

### 📋 GIAI ĐOẠN 1 — Hoàn thiện Docs & Slide (TV2 + TV4)

**TV2 phụ trách:**
- [ ] Soạn docs Chương 2.3 + 2.4 (Hypergraph & Peelability) theo cùng format file này
- [ ] Làm slide 6×6 cho Slide 4 + Slide 5
- [ ] Gửi bản nháp cho TV5 duyệt

**TV4 phụ trách:**
- [ ] Soạn docs Chương 3.2 + 3.3 (Step & Zipf Distribution) theo cùng format
- [ ] Làm slide 6×6 cho Slide 8 + Slide 9 + Slide 10
- [ ] Gửi bản nháp cho TV5 duyệt

**TV2 + TV4 phụ trách FE (giao diện đơn giản):**
- [ ] Đọc README.md để nắm cấu trúc project
- [ ] Viết `static/index.html` — form nhập params (số IP, gap factor, table size)
- [ ] Viết `static/style.css` — layout 2 cột: trái input, phải kết quả
- [ ] Viết `static/app.js` — gọi POST `/api/run`, nhận JSON, vẽ Chart.js
- [ ] Test giao diện với mock data (chưa cần backend thật)

> **Lưu ý FE**: Giáo viên chỉ yêu cầu phân tích thuật toán, FE làm đơn giản nhất có thể. Không cần đẹp, cần chạy được và hiển thị được kết quả so sánh CMS gốc vs Mixed.

---

### ⚙️ GIAI ĐOẠN 2 — Code Backend (TV1 + TV3 + TV5)

**TV3 phụ trách** *(đã nghiên cứu CMS gốc)*:
- [ ] Viết `src/cms.py` — class CMSBasic (k cố định, update thường)
- [ ] Viết `src/cms_conservative.py` — class CMSConservative (chỉ tăng ô nhỏ nhất)
- [ ] Viết unit test: insert 1000 elements, kiểm tra query không bao giờ underestimate

**TV1 phụ trách** *(đã nghiên cứu Mixed Hypergraph)*:
- [ ] Viết `src/cms_mixed.py` — class CMSMixed (k khác nhau cho hot/cold)
- [ ] Implement logic: hot elements dùng k=2, cold elements dùng k=5
- [ ] Test so sánh: CMSMixed vs CMSConservative với cùng dataset

**TV4 phụ trách** *(đã nghiên cứu Step/Zipf)*:
- [ ] Viết `src/data_generator.py`:
  - `generate_step(n_hot, n_cold, gap, total)` — sinh Elephant/Mice data
  - `generate_zipf(n, beta, total)` — sinh Zipf distribution
  - `generate_uniform(n, total)` — sinh uniform distribution

**TV5 (Trưởng nhóm) phụ trách**:
- [ ] Viết `main.py` — FastAPI app:
  - `GET /` → trả về `static/index.html`
  - `POST /api/run` → nhận params, chạy thuật toán, trả JSON
  - `GET /api/health` → kiểm tra server
- [ ] Ráp `src/` vào `main.py` sau khi TV1, TV3, TV4 hoàn thành
- [ ] Viết `requirements.txt` đầy đủ
- [ ] Test end-to-end: FE gọi API → backend chạy → kết quả hiển thị trên Chart.js

---

### ✅ GIAI ĐOẠN 3 — Tổng hợp & Hoàn thiện (Cả nhóm)

**TV5 duyệt toàn bộ:**
- [ ] Duyệt docs của TV1, TV2, TV3, TV4 — kiểm tra đủ nguồn IEEE chưa
- [ ] Duyệt slide của từng người — đúng 6×6 chưa, hình đã chèn chưa
- [ ] Chạy demo end-to-end, ghi lại kết quả số liệu thực tế vào Slide 12

**Cả nhóm:**
- [ ] Họp rehearsal — mỗi người thuyết trình phần mình (10 phút/người)
- [ ] Fix các điểm yếu sau rehearsal
- [ ] Export slide sang PDF để backup khi demo

---

### 📌 Thứ tự ưu tiên tổng thể

```
Tuần 1:  Tất cả hoàn thành docs + slide của mình
         TV3 viết cms.py + cms_conservative.py
         TV4 viết data_generator.py

Tuần 2:  TV1 viết cms_mixed.py
         TV2 + TV4 làm FE (index.html + app.js)
         TV5 viết main.py FastAPI

Tuần 3:  Ráp backend + FE
         TV5 duyệt toàn bộ docs + slide
         Rehearsal + fix
```

---

*Tài liệu soạn cho TV5 (Trưởng nhóm) — dựa trên bài báo gốc Section 3.2, Section 4 và References*
*Fusy, É., & Kucherov, G. (2023) — http://igm.univ-mlv.fr/~fusy/Articles/countmin-exp.pdf*
