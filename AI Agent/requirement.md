# requirement.md — Tiêu chí nghiệm thu (LIVING DOCUMENT)

> File này là file **duy nhất** được phép sửa liên tục trong quá trình code để ghi yêu cầu mới. Ba file còn lại (`rules.md`, `ai_agents.md`, `project_ovr.md`) chỉ đổi theo **sau khi** thay đổi đã được ghi và duyệt ở đây.
> Trạng thái hiện tại của dự án tính đến lần cập nhật gần nhất (2026-07-07): **đã dựng khung folder + hoàn thành module `real_loader.py` (34/34 test passed) đặt tại `data_real/backend/`.** Các module khác đang ở trạng thái 🔲.

---

## 0. Giao thức bắt buộc cho AI khi làm việc trên repo này

Bất kỳ AI coding assistant nào (Claude Code, Cursor, v.v.) được giao việc trên 1 file/module của repo, PHẢI theo đúng trình tự sau — không được bỏ bước:

1. **Đọc `requirement.md` (file này) trước tiên**, tìm dòng checklist tương ứng với file đang được giao.
2. Đọc `rules.md` + phần vai trò liên quan trong `ai_agents.md` để biết đúng tên biến/API/signature phải giữ.
3. Đọc code hiện tại của file đó (nếu đã có).
4. Liệt kê rõ 3 nhóm: **Đã đạt** / **Chưa đạt** / **Sai lệch so với rules.md-ai_agents.md** (vd sai tên field, sai công thức, sai signature).
5. Nếu có chỗ chưa đạt hoặc sai lệch → **đề xuất hướng sửa cụ thể** (diff/đoạn code dự kiến), **KHÔNG tự ý sửa ngay**.
6. Trình bày đề xuất cho coder, **chờ xác nhận đồng ý**.
7. Sau khi coder đồng ý và code đã sửa xong → cập nhật ô "Trạng thái" của dòng checklist tương ứng (🔲 → 🟡 → ✅), ghi ngày.
8. Nếu thay đổi này làm lệch một quy ước đã ghi trong `rules.md`/`ai_agents.md`/`project_ovr.md` (đổi tên field, đổi endpoint, đổi công thức...) → **bắt buộc**:
   - Thêm 1 dòng vào mục **2. Changelog** bên dưới.
   - Liệt kê rõ file nào trong 3 file kia cần sửa theo (dùng bảng ở mục 3).
   - Đề xuất nội dung sửa cụ thể cho từng file đó, chờ duyệt.
   - Chỉ sau khi được duyệt mới áp dụng sửa đồng loạt — **không để 1 file đổi mà 3 file kia đứng yên**, vì đó chính xác là kiểu "rời rạc" mà bộ 4 file này sinh ra để tránh.

Trạng thái ký hiệu dùng thống nhất: 🔲 Chưa bắt đầu · 🟡 Đang làm/có khung chưa đủ tiêu chí · ✅ Đạt tiêu chí · ⚠️ Đạt nhưng có ghi chú cần lưu ý (xem cột Ghi chú).

---

## 1. Checklist nghiệm thu theo module

### [A] Thuật toán (Khoa)

| File | Tiêu chí đạt (rút gọn — chi tiết ở `ai_agents.md`) | Trạng thái | Ghi chú |
|---|---|---|---|
| `hash_utils.py` | `get_k_distinct_indices` luôn trả đúng k chỉ số phân biệt, raise lỗi rõ khi `table_size < k` | 🔲 | |
| `cms.py` | Dùng 1 mảng `table_size` dùng chung (không nhân k); conservative update chỉ tăng min-ô; `memory_bytes()` = `table_size*8` | 🔲 | Xem cảnh báo `rules.md §0.2` |
| `cms_mixed.py` | `query()` dùng đúng k theo `is_hot`; hot/cold seed tách namespace | 🔲 | |
| `metrics.py` | `relative_error` xử lý `true_count=0`; `average_error` lọc đúng theo `only_hot` | 🔲 | |
| `test_cms.py`, `test_cms_mixed.py` | Pass 100%, có test riêng cho conservative update & tách k theo is_hot | 🔲 | |

### [B] Frontend (Mai)

| File | Tiêu chí đạt | Trạng thái | Ghi chú |
|---|---|---|---|
| `index.html`, `style.css` | Đủ layout: 2 nút nguồn data, panel classic/mixed, tab so sánh | 🔲 | |
| `app.js` | Cache response, không gọi API 2 lần cho progressive reveal; đọc field `is_hot` (không phải field khác) | 🔲 | |
| `charts.js` | 3 hàm render đúng chữ ký ở `ai_agents.md` | 🔲 | |
| — | Đã chạy được hoàn chỉnh bằng `mock_data.js` trước khi có backend thật | 🔲 | |
| — | Đã swap sang `api.js` thật, test lại toàn luồng | 🔲 | |

### [C] Kết nối Backend–Frontend (Hiếu)

| File | Tiêu chí đạt | Trạng thái | Ghi chú |
|---|---|---|---|
| `request_models.py` | Khớp 100% `rules.md §3.4`; `model_validator` bắt thiếu field theo `data_source` | 🔲 | |
| `response_models.py` | Khớp 100% `rules.md §3.4` | 🔲 | |
| `main.py` | 3 route đúng `rules.md §3.2-3.4`; CORS chạy được từ frontend thật; lỗi trả đúng khuôn `§3.5` | 🔲 | |
| `api.js` | 2 hàm đúng chữ ký; throw Error rõ khi response có `error` | 🔲 | |
| `README.md` | Người mới clone chạy được backend+frontend trong < 5 phút | 🔲 | |
| `requirements.txt`, `Dockerfile` | Cài đặt chạy được từ đầu | 🔲 | |

### [D] Data + hỗ trợ Backend (Tiên)

| File | Tiêu chí đạt | Trạng thái | Ghi chú |
|---|---|---|---|
| `data_generator.py` | Generator (không load hết RAM); cùng seed → cùng stream; tỉ lệ hot/cold khớp `ph`/`pc` lý thuyết trong sai số chấp nhận được | 🔲 | |
| `real_loader.py` | Parse đúng regex `rules.md §5`; có cache; log số dòng skip | ✅ | 2026-07-07. Hoàn thành 3 hàm public + 1 generator `build_real_stream`. Parse đúng regex rules.md. Cache JSON lưu tại `data_real/processed_cache.json` kèm stats. |
| `presets.py` | Khớp chính xác số liệu `project_ovr.md §7` | 🔲 | |
| `simulation_service.py` (đồng sở hữu A+D) | Consume stream 1 lần duy nhất cho cả 2 sketch; `true_count` từ đếm thật, không suy lý thuyết | 🔲 | File dễ conflict nhất — 2 người phải trao đổi trực tiếp trước khi code (`ai_agents.md`) |
| `test_data_generator.py` | Pass 100% | 🔲 | |
| `test_real_loader.py` | Pass 100% | ✅ | 2026-07-07. 34/34 passed (7.56s). Đã chỉnh path trỏ đến log thô ngoài repo. |
| `data_real/backend/scripts/run_full_experiments.py` | Quét đủ tham số, `total_packets=10,000,000`, xuất số liệu thay placeholder trong `Kịch bản DEMO` | 🔲 | Mốc cuối timeline (`project_ovr.md §9`) |

### [E] Data + hỗ trợ Frontend / Mock (Thịnh)

| File | Tiêu chí đạt | Trạng thái | Ghi chú |
|---|---|---|---|
| `mock_data.js` | Đúng 100% schema `rules.md §3.4`; số liệu hợp lý (không mâu thuẫn logic) | 🔲 | |
| `sample_response.json` | Khớp cấu trúc `mock_data.js` | 🔲 | |

---

## 2. Definition of Done — tổng thể toàn bộ demo

Chỉ tính "xong" khi TẤT CẢ các mục sau đều ✅ (số liệu cụ thể sẽ thay khi chạy `run_full_experiments.py` xong, hiện là mục tiêu tối thiểu):

- [ ] Preset `main`: Mixed phát hiện Elephant ≥ Classic, lỗi trung bình Mice của Mixed < lỗi của Classic (số liệu thật thay cho placeholder `3/5` / `340%` / `5/5` / `12%`)
- [ ] Preset `paper_faithful`: xu hướng cải thiện vẫn giữ được, có thể đối chiếu bằng mắt với hình Figure 5 trong PDF gốc
- [ ] Preset `stress`: thể hiện được rằng ở tải cao, khoảng cách cải thiện thu hẹp lại (không overclaim)
- [ ] Data thật (NASA logs): xu hướng cải thiện tương tự vẫn giữ được (hoặc nếu không, có giải thích hợp lý dựa trên đặc điểm phân phối thật)
- [ ] Toàn bộ 6 tính năng ở `project_ovr.md §8` chạy được trên UI thật (không mock)
- [ ] `POST /api/simulate` với preset `main`, `total_packets=500,000` phản hồi trong vài giây (ghi số đo thật)

## 3. Bảng đồng bộ chéo — file nào cần cập nhật khi requirement.md đổi

| Loại thay đổi | rules.md | ai_agents.md | project_ovr.md |
|---|---|---|---|
| Đổi/thêm field request-response | ✅ bắt buộc (§3.4) | ✅ nếu đổi signature liên quan | — |
| Đổi công thức/tham số preset | ✅ bắt buộc (§3.3) | — | ✅ bắt buộc (§7) |
| Đổi vai trò/file sở hữu | — | ✅ bắt buộc | ✅ nếu ảnh hưởng timeline |
| Đổi endpoint/port/CORS | ✅ bắt buộc (§3) | ✅ nếu ảnh hưởng chữ ký `api.js` | — |
| Đổi kiến trúc/luồng data | — | — | ✅ bắt buộc (§3, §6) |

Quy ước version: mỗi lần 1 trong 3 file trên được sửa theo 1 dòng changelog, thêm ghi chú `(đã đồng bộ theo changelog #N)` ở cuối phần bị sửa trong file đó, để AI đọc sau biết dòng đó khớp changelog nào.

## 4. Changelog — Nhật ký thay đổi yêu cầu

| # | Ngày | Người đề xuất | Yêu cầu mới / thay đổi | File bị ảnh hưởng | Trạng thái duyệt |
|---|---|---|---|---|---|
| 0 | 2026-07-06 | Claude (khởi tạo) | Tạo baseline 4 file từ `Rules_Code_Demo` + `Kịch bản DEMO` + bài báo gốc; bổ sung: mô hình bộ nhớ hypergraph 1 mảng, chuẩn hoá `is_hot`, contract trả cả classic+mixed cùng seed, 3 preset (main/paper_faithful/stress), `real_loader.py` mới, `run_full_experiments.py` mới | Cả 3 file | ✅ (baseline) |
| 1 | 2026-07-07 | AI (Antigravity) | Thiết lập `real_loader.py` + `test_real_loader.py` + `requirements.txt` nằm gọn trong `data_real/backend/` và tạo `data_real/processed_cache.json` (~1.9MB). Đồng bộ hóa lại cấu trúc thư mục mới này trong 3 file `rules.md`, `project_ovr.md`, `ai_agents.md`. | Cả 4 file | ✅ (hoàn thành) |
| 2 | | | | | 🔲 |

*(Thêm dòng mới mỗi khi có thay đổi — không xoá dòng cũ, kể cả khi bị từ chối, ghi rõ "Từ chối — lý do..." ở cột Trạng thái để giữ lịch sử quyết định.)*
