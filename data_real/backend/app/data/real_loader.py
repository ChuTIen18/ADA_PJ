"""
real_loader.py — Nạp + tiền xử lý NASA HTTP Access Log cho nhánh data_source="real".

Module này thuộc vai trò [D] (Tiên) — xem ai_agents.md.
Regex parse dùng đúng NASA_LOG_PATTERN từ rules.md §5.
Field chuẩn: "ip" (dù giá trị có thể là hostname), "is_hot" (không dùng "is_elephant").

Tham khảo:
- rules.md §5: regex, cache, gán nhãn hot/cold
- ai_agents.md [D]: signature 3 hàm public
- project_ovr.md §6.2: replay log gốc khi insert vào CMS
- huongdan_keo_data_access_log.md: EDA kết quả (74,957 IP, 1,566,461 dòng parsed)
"""

import json
import logging
import os
import re
from collections import Counter
from typing import Generator

# ── Regex chính xác từ rules.md §5 ──────────────────────────────────────────
# Không tự viết regex khác — rules.md là nguồn chân lý.
NASA_LOG_PATTERN = re.compile(
    r'^(\S+) \S+ \S+ \[([^\]]+)\] "([^"]*)" (\d{3}) (\S+)$'
)
# group(1) = host (hostname HOẶC ip thô)
# group(2) = timestamp
# group(3) = request line
# group(4) = status code
# group(5) = bytes (có thể là "-")

logger = logging.getLogger(__name__)


# ── Hàm public 1: parse 1 dòng ──────────────────────────────────────────────

def parse_nasa_log_line(line: str) -> str | None:
    """Parse 1 dòng Apache Common Log Format, trả host (group 1) hoặc None.

    Theo rules.md §5: dòng không khớp pattern → bỏ qua (trả None).
    CMS chỉ cần host string để hash, không cần phân biệt hostname vs IP
    (rules.md §2 — field "ip" giữ tên chung dù giá trị có thể là hostname).

    Args:
        line: Một dòng raw từ file log NASA.

    Returns:
        Host string nếu parse thành công, None nếu dòng lỗi/thiếu field.
    """
    match = NASA_LOG_PATTERN.match(line.strip())
    if match:
        return match.group(1)
    return None


# ── Hàm public 2: parse toàn bộ file + cache ────────────────────────────────

def load_and_aggregate(filepath: str, cache_path: str) -> dict[str, int]:
    """Parse file log NASA, đếm {host: count}, cache kết quả ra JSON.

    Nếu cache_path đã tồn tại → đọc cache, trả luôn (không parse lại).
    Nếu chưa → đọc từng dòng filepath, parse bằng parse_nasa_log_line(),
    đếm {host: count}, đếm số dòng skip, ghi ra cache_path (JSON), trả kết quả.

    Theo rules.md §5: "Tiền xử lý 1 lần, cache lại" — mỗi request /api/simulate
    với data_source=real chỉ đọc cache, không parse lại log thô.

    Cache format (JSON):
        {
            "counts": {host: int, ...},
            "stats": {
                "total_lines": int,
                "parsed_lines": int,
                "skipped_lines": int
            }
        }

    Args:
        filepath: Đường dẫn tới file log NASA (vd: access.log).
        cache_path: Đường dẫn file JSON để lưu/đọc cache
                    (vd: backend/app/data/real/processed_cache.json).

    Returns:
        dict[str, int]: {host_string: request_count} — đếm thật (ground truth).

    Raises:
        FileNotFoundError: Nếu filepath không tồn tại và chưa có cache.
    """
    # ── Nếu cache đã tồn tại → đọc và trả luôn ──
    if os.path.exists(cache_path):
        logger.info("Đọc cache từ %s (không parse lại log thô)", cache_path)
        with open(cache_path, "r", encoding="utf-8") as f:
            cached = json.load(f)
        stats = cached.get("stats", {})
        logger.info(
            "Cache stats: total=%s, parsed=%s, skipped=%s",
            stats.get("total_lines", "?"),
            stats.get("parsed_lines", "?"),
            stats.get("skipped_lines", "?"),
        )
        return cached["counts"]

    # ── Chưa có cache → parse file log thô ──
    logger.info("Bắt đầu parse log thô từ %s ...", filepath)

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Không tìm thấy file log: {filepath}. "
            f"Hãy tải từ Kaggle và đặt vào đúng đường dẫn — xem README."
        )

    host_counter: Counter[str] = Counter()
    total_lines = 0
    parsed_lines = 0
    skipped_lines = 0

    # Dùng errors="replace" để tránh crash khi gặp ký tự encoding lỗi
    # (theo huongdan_keo_data_access_log.md §4.2)
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            total_lines += 1

            host = parse_nasa_log_line(line)
            if host is not None:
                host_counter[host] += 1
                parsed_lines += 1
            else:
                skipped_lines += 1

            # Progress log mỗi 500K dòng
            if total_lines % 500_000 == 0:
                logger.info("  ... đã đọc %s dòng", f"{total_lines:,}")

    logger.info(
        "Parse xong: total=%s, parsed=%s, skipped=%s (%.2f%% skip)",
        f"{total_lines:,}",
        f"{parsed_lines:,}",
        f"{skipped_lines:,}",
        (skipped_lines / total_lines * 100) if total_lines > 0 else 0,
    )

    counts = dict(host_counter)

    # ── Ghi cache ──
    cache_data = {
        "counts": counts,
        "stats": {
            "total_lines": total_lines,
            "parsed_lines": parsed_lines,
            "skipped_lines": skipped_lines,
        },
    }

    # Tạo thư mục cha nếu chưa có
    cache_dir = os.path.dirname(cache_path)
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False)

    logger.info("Đã ghi cache ra %s", cache_path)

    return counts


# ── Hàm public 3: gán nhãn hot/cold ─────────────────────────────────────────

def label_hot_cold(
    counts: dict[str, int], hot_threshold_percent: float
) -> list[dict]:
    """Gán nhãn is_hot cho từng host dựa trên phân vị tần suất.

    Sort giảm dần theo count. Top hot_threshold_percent% đầu → is_hot=True,
    còn lại → is_hot=False.

    Theo rules.md §5: "Gắn nhãn hot/cold: sort giảm dần theo count,
    top hot_threshold_percent% đầu = is_hot: true."
    Theo ai_agents.md [D]: validate hot_threshold_percent quá nhỏ/lớn.
    Theo rules.md §4.4: 0 < hot_threshold_percent < 100.

    Args:
        counts: {host: request_count} từ load_and_aggregate().
        hot_threshold_percent: Phần trăm host tần suất cao nhất coi là hot.
                               Ví dụ: 1.0 = top 1%.

    Returns:
        list[dict]: Mỗi dict có {"ip": str, "true_count": int, "is_hot": bool}.
                    Sắp xếp giảm dần theo true_count.

    Raises:
        ValueError: Nếu hot_threshold_percent ngoài khoảng (0, 100)
                    hoặc counts rỗng.
    """
    # ── Validate ──
    if not counts:
        raise ValueError("counts rỗng — không có dữ liệu để gán nhãn.")

    if not (0 < hot_threshold_percent < 100):
        raise ValueError(
            f"hot_threshold_percent phải trong khoảng (0, 100), "
            f"nhận được: {hot_threshold_percent}. "
            f"Xem rules.md §4.4."
        )

    # ── Sort giảm dần theo count ──
    sorted_hosts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    # ── Tính số host thuộc nhóm hot ──
    n_hot = max(1, int(len(sorted_hosts) * hot_threshold_percent / 100.0))

    # Nếu n_hot >= tổng số host → cảnh báo (gần hết là hot = vô nghĩa)
    if n_hot >= len(sorted_hosts):
        raise ValueError(
            f"hot_threshold_percent={hot_threshold_percent}% chọn ra "
            f"{n_hot}/{len(sorted_hosts)} host — gần hết là hot, "
            f"kết quả sẽ vô nghĩa. Hãy giảm ngưỡng."
        )

    hot_hosts = set(host for host, _ in sorted_hosts[:n_hot])

    # ── Build result list ──
    result = [
        {
            "ip": host,
            "true_count": count,
            "is_hot": host in hot_hosts,
        }
        for host, count in sorted_hosts
    ]

    logger.info(
        "Gán nhãn: %s hot (%s%%) / %s cold trong tổng %s host",
        n_hot,
        f"{hot_threshold_percent:.2f}",
        len(sorted_hosts) - n_hot,
        len(sorted_hosts),
    )

    return result


# ── Hàm tiện ích: replay stream từ file log gốc ─────────────────────────────

def build_real_stream(
    filepath: str,
    hot_ips: set[str],
) -> Generator[dict, None, None]:
    """Generator yield từng packet {"ip": str, "is_hot": bool} theo thứ tự log gốc.

    Phục vụ simulation_service.py: replay đúng thứ tự dòng log khi insert
    vào CMS, để CMS "trải nghiệm" đúng phân phối thời gian thực của traffic
    thật — không chỉ đếm tổng (theo project_ovr.md §6.2).

    Dùng yield — không dựng list toàn bộ stream trong RAM
    (theo rules.md §4.3 / ai_agents.md [D] tinh thần generator).

    Args:
        filepath: Đường dẫn tới file log NASA.
        hot_ips: Tập host đã được gán nhãn hot (từ label_hot_cold).

    Yields:
        dict: {"ip": str, "is_hot": bool} cho mỗi dòng log hợp lệ.
    """
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            host = parse_nasa_log_line(line)
            if host is not None:
                yield {"ip": host, "is_hot": host in hot_ips}
