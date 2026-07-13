# ADA_PJ - Mixed Hypergraph CMS Demo

## Tổng quan dự án

Dự án này xây dựng một demo tương tác để so sánh hiệu quả phát hiện lưu lượng “Elephant flow” giữa hai thuật toán:

- Conservative Count-Min Sketch (CMS) truyền thống
- Mixed Hypergraph CMS với cấu hình hot/cold riêng: hot dùng $k=2$, cold dùng $k=5$

Mục tiêu chính là minh họa rằng, với cùng một lượng bộ nhớ cố định, phương pháp mixed có thể phát hiện các flow lớn (Elephant) tốt hơn trong bối cảnh có nhiều flow nhỏ (Mice) đi kèm, đồng thời cho phép thử nghiệm trên cả dữ liệu giả lập và dữ liệu thực tế từ NASA HTTP access logs.

Dự án gồm 3 phần chính:

1. Backend Python xử lý dữ liệu, chạy thuật toán CMS và tính métrics.
2. Frontend tĩnh bằng HTML/CSS/JavaScript để người dùng chạy demo và xem kết quả trực quan.
3. Tập hợp tài liệu, yêu cầu và quy tắc phát triển để duy trì tính nhất quán giữa code và mục tiêu học thuật.

---

## Mục tiêu kinh doanh và học thuật

- So sánh trực tiếp classic CMS và mixed CMS trên cùng một stream dữ liệu.
- Minh họa cách hot/cold phân tách giúp giảm nhiễu từ mice flow lên elephant flow.
- Cung cấp một demo có thể chạy nhanh trên máy cá nhân mà không cần cài đặt phức tạp.
- Hỗ trợ việc kiểm chứng thêm trên dữ liệu thực tế từ log truy cập web.

---

## Công nghệ sử dụng

- Backend: Python 3.11+, FastAPI, Pydantic, Uvicorn
- Frontend: HTML, CSS, JavaScript thuần, Chart.js qua CDN
- Tests: pytest
- Data: dữ liệu giả lập và dữ liệu thực tế từ NASA log
- Container: Docker (tùy chọn)

---

## Cấu trúc thư mục

```text
ADA_PJ/
├── README.md
├── requirement.md
├── rules.md
├── project_ovr.md
├── ai_agents.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── algorithms/
│   │   │   ├── __init__.py
│   │   │   ├── cms.py
│   │   │   ├── cms_mixed.py
│   │   │   └── hash_utils.py
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── data_generator.py
│   │   │   ├── presets.py
│   │   │   ├── real_loader.py
│   │   │   └── real/
│   │   ├── schemas/
│   │   │   ├── request_models.py
│   │   │   └── response_models.py
│   │   ├── services/
│   │   │   └── simulation_service.py
│   │   └── utils/
│   │       └── metrics.py
│   ├── scripts/
│   │   ├── build_cms_demo_data.py
│   │   ├── build_real_cache.py
│   │   ├── download_kaggle_nasa.py
│   │   ├── download_nasa_log.py
│   │   └── run_full_experiments.py
│   └── tests/
│       ├── test_cms.py
│       ├── test_cms_mixed.py
│       ├── test_data_generator.py
│       ├── test_real_loader.py
│       └── test_run_full_experiments.py
├── data/
│   └── mock/
│       └── sample_response.json
├── data_real/
│   ├── analyze_nasa_log.py
│   ├── huongdan_keo_data_access_log.md
│   ├── processed_cache.json
│   ├── backend/
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── algorithms/
│   │   │   └── data/
│   │   │       └── real_loader.py
│   │   └── tests/
│   │       └── test_real_loader.py
└── frontend/
    ├── index.html
    ├── README.md
    ├── assets/
    ├── css/
    │   └── style.css
    ├── data/
    │   ├── real_summary.json
    │   └── synthetic_summary.json
    └── js/
        ├── api.js
        ├── app.js
        ├── charts.js
        ├── cms_demo.js
        ├── cms_real_data.js
        └── mock_data.js
```

---

## Vai trò từng thư mục

### Thư mục gốc
- README.md: tài liệu tổng quan cho người mới bắt đầu.
- requirement.md: tiêu chí nghiệm thu và checklist chức năng.
- rules.md: quy tắc kỹ thuật, chuẩn dữ liệu, API và các định nghĩa chính.
- project_ovr.md: tổng quan kiến trúc và mục tiêu học thuật của dự án.
- ai_agents.md: mô tả vai trò của từng thành viên/agent trong quá trình phát triển.

### backend/
Thư mục chứa toàn bộ logic nghiệp vụ và API server.

- app/: mã nguồn chính của hệ thống.
  - algorithms/: triển khai các thuật toán CMS.
    - cms.py: Conservative CMS truyền thống.
    - cms_mixed.py: Mixed CMS cho hot/cold flow.
    - hash_utils.py: các hàm băm và sinh index cho sketch.
  - data/: công cụ sinh dữ liệu và loader dữ liệu thực tế.
    - data_generator.py: sinh stream dữ liệu giả lập.
    - presets.py: các preset tham số demo.
    - real_loader.py: đọc và tiền xử lý NASA log.
  - schemas/: định nghĩa request/response DTO bằng Pydantic.
  - services/: orchestration logic cho việc chạy simulation.
  - utils/: các hàm hỗ trợ tính toán metrics.
- scripts/: các script chạy thử, xây dựng dữ liệu và thí nghiệm quy mô lớn.
- tests/: test cho thuật toán, data pipeline và endpoint.

### frontend/
Thư mục chứa giao diện demo.

- index.html: giao diện chính.
- css/style.css: bố cục và giao diện trực quan.
- js/: logic frontend để gọi backend, render bảng, biểu đồ và kết quả demo.
- data/: dữ liệu tóm tắt dùng cho demo và kiểm thử UI.
- assets/: hình ảnh và tài nguyên phụ trợ.

### data/
Chứa dữ liệu mẫu và mock response phục vụ phát triển ban đầu hoặc phục vụ demo nhanh.

### data_real/
Chứa dữ liệu và công cụ liên quan đến việc xử lý log thật.

- analyze_nasa_log.py: phân tích dữ liệu NASA log.
- processed_cache.json: cache dữ liệu đã xử lý để tránh phải parse lại mỗi lần chạy.
- backend/: bản phụ của backend dùng cho dữ liệu thực tế.

---

## Luồng hoạt động chính

1. Người dùng chọn nguồn dữ liệu: synthetic hoặc real.
2. Frontend gửi yêu cầu đến backend thông qua API.
3. Backend sinh hoặc nạp stream dữ liệu.
4. Cả classic CMS và mixed CMS chạy trên cùng một stream.
5. Backend tính các metric như lỗi trung bình, precision và phát hiện elephant flow.
6. Frontend hiển thị kết quả dưới dạng bảng và biểu đồ.

---

## Cách chạy nhanh

### Chạy backend

```bash
cd ADA_PJ/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Chạy frontend

Mở file frontend/index.html bằng trình duyệt, hoặc dùng một static server đơn giản nếu cần.

---

## Ghi chú phát triển

- Dữ liệu synthetic và real nên được xử lý theo cùng một schema để đảm bảo so sánh công bằng.
- Các thay đổi về API, preset hoặc cấu trúc dữ liệu cần đồng bộ với các tài liệu ở requirement.md, rules.md và project_ovr.md.
- Khi làm việc với thuật toán CMS, cần giữ nguyên logic so sánh giữa classic và mixed trên cùng một seed và cùng một stream đầu vào.

---

## Kết luận

Project này không chỉ là một demo kỹ thuật đơn thuần, mà còn là một nền tảng để minh họa, kiểm chứng và trình bày một ý tưởng nghiên cứu về Count-Min Sketch và Mixed Hypergraph CMS một cách trực quan và có hệ thống.