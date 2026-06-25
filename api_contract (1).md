# API Contract — Elephant/Mice CMS Demo


---

## Base URL

```
http://localhost:8000
```

---

## Endpoint

### `POST /api/simulate`

Chạy mô phỏng thuật toán CMS (classic hoặc mixed) trên một bộ dữ liệu và trả về kết quả so sánh.

---

## Request

**Content-Type:** `application/json`

| Field | Type | Bắt buộc | Mô tả |
|---|---|---|---|
| `algorithm` | `string` | ✅ | `"classic"` (k=3) hoặc `"mixed"` (k_hot=2, k_cold=5) |
| `data_source` | `string` | ✅ | `"synthetic"` (data giả lập) hoặc `"real"` (data thực tế) |
| `n_hot` | `integer` | ✅ khi `synthetic` | Số lượng Elephant IP (VD: 5) |
| `n_cold` | `integer` | ✅ khi `synthetic` | Số lượng Mice IP (VD: 9995) |
| `gap_factor` | `number` | ✅ khi `synthetic` | Tỉ lệ tần suất hot/cold — G > 1 (VD: 100) |
| `table_size` | `integer` | ✅ | Số ô đếm trong sketch (VD: 5000 ≈ 40KB RAM) |
| `total_packets` | `integer` | ✅ khi `synthetic` | Tổng số packet trong stream (VD: 10000000) |

**Ví dụ — Data giả lập:**

```json
{
  "algorithm": "mixed",
  "data_source": "synthetic",
  "n_hot": 5,
  "n_cold": 9995,
  "gap_factor": 100,
  "table_size": 5000,
  "total_packets": 10000000
}
```

**Ví dụ — Data thực tế:**

```json
{
  "algorithm": "classic",
  "data_source": "real",
  "table_size": 5000
}
```

---

## Response

**Content-Type:** `application/json`  
**Status:** `200 OK`

| Field | Type | Mô tả |
|---|---|---|
| `data_source` | `string` | `"synthetic"` hoặc `"real"` — để FE hiển thị nhãn rõ ràng |
| `algorithm` | `string` | Thuật toán đã chạy (`"classic"` hoặc `"mixed"`) |
| `elephant_detected` | `integer` | Số Elephant IP phát hiện đúng (nằm trong top estimate) |
| `elephant_total` | `integer` | Tổng số Elephant IP thực tế |
| `mice_avg_error` | `float` | Lỗi ước tính trung bình của Mice IP (0.12 = 12%) |
| `top10` | `array` | Danh sách 10 IP có estimate cao nhất |
| `top10[].ip` | `string` | Địa chỉ IP |
| `top10[].true_count` | `integer` | Số lần xuất hiện thực tế |
| `top10[].estimate` | `integer` | Số lần ước tính bởi CMS |
| `top10[].is_elephant` | `boolean` | IP này có phải Elephant không |

**Ví dụ:**

```json
{
  "data_source": "synthetic",
  "algorithm": "mixed",
  "elephant_detected": 5,
  "elephant_total": 5,
  "mice_avg_error": 0.12,
  "top10": [
    {
      "ip": "10.0.0.1",
      "true_count": 95283,
      "estimate": 96100,
      "is_elephant": true
    },
    {
      "ip": "10.0.0.2",
      "true_count": 91047,
      "estimate": 92300,
      "is_elephant": true
    },
    {
      "ip": "192.168.1.44",
      "true_count": 1023,
      "estimate": 1089,
      "is_elephant": false
    }
  ]
}
```

---

## Error Responses

| Status | Mô tả |
|---|---|
| `422 Unprocessable Entity` | Request thiếu field hoặc sai kiểu dữ liệu |
| `500 Internal Server Error` | Lỗi khi chạy thuật toán |

**Ví dụ lỗi 422:**

```json
{
  "detail": [
    {
      "loc": ["body", "algorithm"],
      "msg": "value is not a valid enum value",
      "type": "type_error.enum"
    }
  ]
}
```

---

## Ghi chú cho từng thành viên

**[A] Khoa** — `cms.py`, `cms_mixed.py`, `simulation_service.py`  
Dựa vào schema request để biết input nhận vào là gì. Output của `simulation_service` phải khớp chính xác với response schema trên.

**[B] Mai** — `frontend/js/app.js`, `charts.js`  
Dùng `mock_data.js` (do [E] cung cấp) với đúng schema response trên để code UI. Khi [C] xong API thật, chỉ cần đổi nguồn data — không cần sửa logic hiển thị.

**[C] Hiếu** — `main.py`, `schemas/`, `api.js`  
Pydantic models trong `request_models.py` và `response_models.py` phải map 1-1 với bảng trên.

**[D] Tiên** — `data_generator.py`  
Output của `generate_step()` phải tương thích để `simulation_service.py` chạy được với schema request trên.

**[E] Thịnh** — `mock_data.js`, `sample_response.json`  
Copy đúng ví dụ response ở trên vào `sample_response.json`. Đây là file [B] dùng để dev FE độc lập.

---


