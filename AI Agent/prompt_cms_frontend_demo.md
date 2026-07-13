# Prompt cho AI Agent: Xây dựng Frontend Demo Count-Min Sketch

Dán nguyên văn phần dưới đây cho AI coding agent tại máy (Claude Code, Cline, Cursor...).

---

## Bối cảnh dự án

Tôi đang xây một demo trực quan hoá thuật toán **Count-Min Sketch (CMS)** dựa trên bài báo
"Count-min sketch with variable number of hash functions: an experimental study".
Mục tiêu: một frontend chạy độc lập (hoặc gắn với backend FastAPI có sẵn) cho phép người dùng
xem trực quan quá trình insert/query của CMS theo thời gian thực, tương tự cách Bloom Filter
được minh hoạ (bảng bit 0/1) nhưng ở đây bảng là **mảng 2 chiều d hàng x w cột, mỗi ô là một
counter tăng dần** chứ không chỉ đánh dấu 0/1.

## Yêu cầu chức năng (bắt buộc)

1. **Cấu trúc dữ liệu**: mảng 2D `sketch[d][w]` khởi tạo toàn 0. `d` (số hàng / số hash function)
   và `w` (số cột / độ rộng mỗi hàng) phải là tham số có thể chỉnh (input hoặc slider), không hardcode.
2. **Hash functions**: d hàm băm độc lập (có thể dùng cùng 1 hàm băm với d seed khác nhau kiểu
   `hash(item, seed_i) mod w`). Ghi rõ công thức hash đang dùng trong code comment.
3. **Insert (Add)**: nhập một item (string), tính d chỉ số qua d hàm băm, **tăng +1** vào từng ô
   tương ứng trên từng hàng. Có animation highlight các ô vừa được cập nhật (giống hiệu ứng
   flash/màu nổi bật trong ~0.3-0.5s).
4. **Query (Estimate)**: nhập một item, tính d chỉ số, lấy giá trị tại các ô đó, trả về
   `estimate = min(giá trị các ô)`. Hiển thị rõ công thức min và giải thích ngắn: CMS có thể
   **overestimate** (do hash collision) nhưng **không bao giờ underestimate**.
5. **Reset**: xoá toàn bộ sketch về 0.
6. **Lịch sử thao tác**: log các item đã insert (để người xem đối chiếu true count vs estimate).
7. **So sánh d thay đổi (theo đúng tinh thần bài báo)**: cho phép chạy lại cùng một tập dữ liệu
   với các giá trị d khác nhau (ví dụ d=2,3,4,5) và hiển thị biểu đồ sai số ước lượng
   (estimate - true count) theo d, dùng Chart.js (đã dùng trong dự án Elephant/Mice Flow Detection
   trước đó của tôi, muốn tái sử dụng style/stack tương tự).

## Yêu cầu kỹ thuật / stack

- Frontend: React (function components, hooks), không dùng class component.
- Biểu đồ: Chart.js (đồng bộ với stack FastAPI + Chart.js đã dùng trong project Count-Min Sketch
  Elephant/Mice Flow Detection trước đây — tái sử dụng cấu trúc component chart nếu có thể).
- Nếu có backend: expose API FastAPI dạng
  - `POST /cms/insert {item}` → trả về index đã update + sketch hiện tại
  - `POST /cms/query {item}` → trả về estimate + giá trị từng hàng
  - `POST /cms/reset`
  - `GET /cms/config` → trả về d, w hiện tại
  Backend giữ state sketch trong memory (không cần DB) cho mục đích demo.
- Nếu chỉ cần chạy phía client (không backend): toàn bộ logic hash + sketch nằm trong
  JS/TS state, không cần gọi API.
- Code phải có comment tiếng Việt ngắn gọn ở các đoạn logic chính (hash, insert, query) để tôi
  dễ đối chiếu với công thức trong bài báo khi viết báo cáo.
- Responsive, không cần hỗ trợ mobile phức tạp — demo dùng trên laptop khi thuyết trình.

## Điều KHÔNG cần làm

- Không cần authentication, không cần lưu DB lâu dài.
- Không cần tối ưu hash function cho production (dùng hash đơn giản kiểu FNV/djb2 với seed khác
  nhau là đủ, miễn phản ánh đúng bản chất "d hàm băm độc lập").

## Định dạng bàn giao

- Trả lời bằng cách tạo code trực tiếp trong repo hiện tại (giữ cấu trúc thư mục sẵn có nếu có).
- Sau khi code xong, tóm tắt ngắn gọn: các file đã tạo/sửa, cách chạy demo (`npm run dev` hoặc
  lệnh tương ứng), và cách tôi có thể đổi tham số d, w để thử nghiệm nhanh.

---

*(Hết prompt — bạn có thể chỉnh phần "Bối cảnh dự án" và "Yêu cầu kỹ thuật" nếu agent của bạn
đã biết sẵn cấu trúc repo, để tránh lặp lại thông tin không cần thiết.)*
