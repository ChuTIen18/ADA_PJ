## Thể hiện Realtime Data

### Mục tiêu

- Giúp người xem thấy rõ quy trình demo đang chạy ngay lập tức, không phải chỉ nhìn kết quả cuối cùng.
- Thể hiện trên UI cả hai nguồn data: `synthetic` và `real`.
- Tăng độ tin cậy bằng cách hiển thị trạng thái và số liệu tạm trong quá trình tính toán.

### Các thành phần realtime cần hiển thị

1. Trạng thái chung
   - "Đang khởi tạo sketch CMS..."
   - "Đang nạp stream packet vào CMS Classic..."
   - "Đang nạp stream packet vào CMS Mixed..."
   - "Đang truy vấn kết quả và tính lỗi..."
   - "Hoàn tất" khi kết thúc.

2. Progress bar hoặc tiến trình lũy kế
   - Synthetic:
     - `Đã xử lý 1,000,000 / 10,000,000 packet`
     - `Đã xử lý 5,000,000 / 10,000,000 packet`
     - `Đã xử lý 10,000,000 / 10,000,000 packet`
   - Real:
     - `Đang đọc dữ liệu traffic thật...`
     - `Đang tính true_count cho X IP...`
     - `Đang phân loại hot/cold...`

3. Thông tin tạm thời (interim stats)
   - Sau mỗi block packet hoặc sau mỗi bước chính, hiển thị:
     - `CMS Classic: Elephant phát hiện 2/5`
     - `CMS Mixed: Elephant phát hiện 4/5`
     - `Mice avg error (classic): 120%`
     - `Mice avg error (mixed): 18%`
   - Nếu chưa đủ dữ liệu, ghi rõ: "chưa đủ dữ liệu để ước tính chính xác".

4. So sánh trực tiếp trong quá trình chạy
   - Khi phần `top-10` được cập nhật, hiển thị 2 dòng số liệu:
     - `CMS Classic top-10: 3/5 Elephant đúng`
     - `CMS Mixed top-10: 5/5 Elephant đúng`
     - Hiển thị thêm thông tin về một IP bị overestimate do noise, ví dụ:
     - `IP 10.0.0.7: true=20, classic=120, mixed=22`

5. Hiển thị nguồn dữ liệu rõ ràng
   - `Nguồn: Data giả lập` hoặc `Nguồn: Data thực tế`
   - Với data thực tế, thêm dòng:
     - `Phân loại hot/cold bằng top 0.05% IP tần suất cao nhất`

### Gợi ý UI realtime cho demo

- Thêm một vùng status bar trên trang, luôn nằm trên cùng.
- Cập nhật status theo từng bước và kèm icon vòng tròn quay.
- Khi ấn "Chạy Simulation", bật chế độ realtime và disable nút để người xem biết hệ thống đang xử lý.
- Sau khi hoàn tất, bật lại nút và chuyển trạng thái về "Hoàn thành".

### Lưu ý implementation

- Nếu chạy 10 triệu packet từng packet quá chậm, xử lý theo lô nhỏ và cập nhật UI sau mỗi lô.
- Nếu data thực tế chưa có nhãn hot/cold, tiến trình gồm:
  1. `Đang tải file...`
  2. `Đang tính true_count...`
  3. `Đang xác định hot/cold...`
  4. `Đang nạp vào CMS...`
