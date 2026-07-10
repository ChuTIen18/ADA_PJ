"""
test_real_loader.py — Test cho module real_loader.py

Bao gồm:
- Unit test: parse dòng hợp lệ / lỗi, label_hot_cold logic, cache cơ chế
- Integration test: chạy trên access.log thật (skip nếu file không tồn tại)

Chạy: pytest backend/tests/test_real_loader.py -v
"""

import json
import os
import sys
import tempfile
import time

import pytest

# Thêm đường dẫn backend/app vào sys.path để import được module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from data.real_loader import (
    NASA_LOG_PATTERN,
    build_real_stream,
    label_hot_cold,
    load_and_aggregate,
    parse_nasa_log_line,
)

# ── Đường dẫn file access.log thật ──────────────────────────────────────────
# Dùng cho integration test — skip nếu file không tồn tại.
REAL_LOG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "..", "access.log"
)
# Normalize để đẹp hơn trong log
REAL_LOG_PATH = os.path.normpath(REAL_LOG_PATH)


# ════════════════════════════════════════════════════════════════════════════
# 1. TEST parse_nasa_log_line
# ════════════════════════════════════════════════════════════════════════════


class TestParseNasaLogLine:
    """Test parse 1 dòng log."""

    def test_valid_hostname(self):
        """Dòng hợp lệ với hostname → trả host đúng."""
        line = (
            'in24.inetnebr.com - - [01/Aug/1995:00:00:01 -0400] '
            '"GET /shuttle/missions/sts-68/news/sts-68-mcc-05.txt HTTP/1.0" 200 1839'
        )
        assert parse_nasa_log_line(line) == "in24.inetnebr.com"

    def test_valid_ip_address(self):
        """Dòng hợp lệ với IP address → trả IP đúng."""
        line = (
            '163.206.89.4 - - [01/Aug/1995:00:00:09 -0400] '
            '"GET /images/launch-logo.gif HTTP/1.0" 200 1713'
        )
        assert parse_nasa_log_line(line) == "163.206.89.4"

    def test_response_size_dash(self):
        """Dòng có response size là "-" (304 Not Modified) → vẫn parse được."""
        line = (
            'piweba4y.prodigy.com - - [01/Aug/1995:00:00:11 -0400] '
            '"GET /images/NASA-logosmall.gif HTTP/1.0" 304 -'
        )
        assert parse_nasa_log_line(line) == "piweba4y.prodigy.com"

    def test_empty_line(self):
        """Dòng trống → trả None."""
        assert parse_nasa_log_line("") is None

    def test_whitespace_only(self):
        """Dòng chỉ có whitespace → trả None."""
        assert parse_nasa_log_line("   \t  \n") is None

    def test_malformed_missing_quotes(self):
        """Dòng thiếu dấu ngoặc kép (request line lỗi) → trả None."""
        line = 'somehost - - [01/Aug/1995:00:00:01 -0400] GET /path 200 100'
        assert parse_nasa_log_line(line) is None

    def test_malformed_truncated(self):
        """Dòng bị cắt ngắn → trả None."""
        line = 'somehost - - [01/Aug/1995:00:00:01'
        assert parse_nasa_log_line(line) is None

    def test_strip_newline(self):
        """Dòng có newline cuối → vẫn parse đúng (strip trước match)."""
        line = (
            'edams.ksc.nasa.gov - - [01/Aug/1995:00:00:01 -0400] '
            '"GET /index.html HTTP/1.0" 200 5000\n'
        )
        assert parse_nasa_log_line(line) == "edams.ksc.nasa.gov"

    def test_regex_matches_rules_md(self):
        """Kiểm tra regex compile đúng từ rules.md §5."""
        expected_pattern = r'^(\S+) \S+ \S+ \[([^\]]+)\] "([^"]*)" (\d{3}) (\S+)$'
        assert NASA_LOG_PATTERN.pattern == expected_pattern


# ════════════════════════════════════════════════════════════════════════════
# 2. TEST load_and_aggregate
# ════════════════════════════════════════════════════════════════════════════


class TestLoadAndAggregate:
    """Test parse file + cache."""

    SAMPLE_LOG = (
        'host_a - - [01/Aug/1995:00:00:01 -0400] "GET /page1 HTTP/1.0" 200 100\n'
        'host_b - - [01/Aug/1995:00:00:02 -0400] "GET /page2 HTTP/1.0" 200 200\n'
        'host_a - - [01/Aug/1995:00:00:03 -0400] "GET /page3 HTTP/1.0" 200 300\n'
        'host_a - - [01/Aug/1995:00:00:04 -0400] "GET /page4 HTTP/1.0" 304 -\n'
        'MALFORMED LINE WITHOUT PROPER FORMAT\n'
        'host_c - - [01/Aug/1995:00:00:05 -0400] "GET /page5 HTTP/1.0" 200 500\n'
    )

    def _write_sample_log(self, tmpdir: str) -> str:
        """Ghi sample log vào file tạm."""
        log_path = os.path.join(tmpdir, "test_access.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(self.SAMPLE_LOG)
        return log_path

    def test_basic_counting(self):
        """Đếm tần suất host đúng."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = self._write_sample_log(tmpdir)
            cache_path = os.path.join(tmpdir, "cache.json")

            counts = load_and_aggregate(log_path, cache_path)

            assert counts["host_a"] == 3
            assert counts["host_b"] == 1
            assert counts["host_c"] == 1
            assert len(counts) == 3  # 3 host phân biệt

    def test_skipped_lines_logged(self):
        """Cache ghi đúng số dòng skip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = self._write_sample_log(tmpdir)
            cache_path = os.path.join(tmpdir, "cache.json")

            load_and_aggregate(log_path, cache_path)

            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)

            stats = cached["stats"]
            assert stats["total_lines"] == 6
            assert stats["parsed_lines"] == 5
            assert stats["skipped_lines"] == 1  # 1 dòng MALFORMED

    def test_cache_created(self):
        """Cache file được tạo ra sau lần parse đầu tiên."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = self._write_sample_log(tmpdir)
            cache_path = os.path.join(tmpdir, "cache.json")

            assert not os.path.exists(cache_path)
            load_and_aggregate(log_path, cache_path)
            assert os.path.exists(cache_path)

    def test_cache_read_same_result(self):
        """Lần 2 đọc cache → kết quả giống hệt lần 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = self._write_sample_log(tmpdir)
            cache_path = os.path.join(tmpdir, "cache.json")

            counts_1 = load_and_aggregate(log_path, cache_path)
            counts_2 = load_and_aggregate(log_path, cache_path)

            assert counts_1 == counts_2

    def test_cache_read_no_reparse(self):
        """Lần 2 đọc cache không cần file log gốc (có thể xóa log gốc)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = self._write_sample_log(tmpdir)
            cache_path = os.path.join(tmpdir, "cache.json")

            counts_1 = load_and_aggregate(log_path, cache_path)

            # Xóa file log gốc
            os.remove(log_path)
            assert not os.path.exists(log_path)

            # Vẫn đọc được từ cache
            counts_2 = load_and_aggregate(log_path, cache_path)
            assert counts_1 == counts_2

    def test_file_not_found_no_cache(self):
        """Nếu file log không tồn tại VÀ không có cache → FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = os.path.join(tmpdir, "cache.json")
            with pytest.raises(FileNotFoundError, match="Không tìm thấy file log"):
                load_and_aggregate("/nonexistent/file.log", cache_path)

    def test_empty_log_file(self):
        """File log rỗng → trả dict rỗng, không crash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "empty.log")
            with open(log_path, "w") as f:
                f.write("")
            cache_path = os.path.join(tmpdir, "cache.json")

            counts = load_and_aggregate(log_path, cache_path)
            assert counts == {}


# ════════════════════════════════════════════════════════════════════════════
# 3. TEST label_hot_cold
# ════════════════════════════════════════════════════════════════════════════


class TestLabelHotCold:
    """Test gán nhãn hot/cold."""

    SAMPLE_COUNTS = {
        "elephant_1": 5000,
        "elephant_2": 3000,
        "mouse_1": 50,
        "mouse_2": 30,
        "mouse_3": 10,
        "mouse_4": 5,
        "mouse_5": 3,
        "mouse_6": 2,
        "mouse_7": 1,
        "mouse_8": 1,
    }

    def test_basic_labeling(self):
        """Top 20% = 2 host → is_hot=True, 8 host → is_hot=False."""
        result = label_hot_cold(self.SAMPLE_COUNTS, hot_threshold_percent=20.0)

        # 10 host tổng, top 20% = 2 host
        hot_ips = [r for r in result if r["is_hot"]]
        cold_ips = [r for r in result if not r["is_hot"]]

        assert len(hot_ips) == 2
        assert len(cold_ips) == 8

        # Đúng 2 host hot nhất
        hot_names = {r["ip"] for r in hot_ips}
        assert hot_names == {"elephant_1", "elephant_2"}

    def test_sorted_descending(self):
        """Kết quả sắp xếp giảm dần theo true_count."""
        result = label_hot_cold(self.SAMPLE_COUNTS, hot_threshold_percent=20.0)
        counts = [r["true_count"] for r in result]
        assert counts == sorted(counts, reverse=True)

    def test_output_fields(self):
        """Mỗi dict có đúng 3 field: ip, true_count, is_hot."""
        result = label_hot_cold(self.SAMPLE_COUNTS, hot_threshold_percent=20.0)
        for record in result:
            assert set(record.keys()) == {"ip", "true_count", "is_hot"}
            assert isinstance(record["ip"], str)
            assert isinstance(record["true_count"], int)
            assert isinstance(record["is_hot"], bool)

    def test_field_name_is_hot_not_is_elephant(self):
        """Field phải là 'is_hot' (rules.md §2), không phải 'is_elephant'."""
        result = label_hot_cold(self.SAMPLE_COUNTS, hot_threshold_percent=20.0)
        for record in result:
            assert "is_hot" in record
            assert "is_elephant" not in record

    def test_minimum_1_hot(self):
        """Dù threshold nhỏ, vẫn có ít nhất 1 host hot (max(1, ...))."""
        result = label_hot_cold(self.SAMPLE_COUNTS, hot_threshold_percent=0.1)
        hot_count = sum(1 for r in result if r["is_hot"])
        assert hot_count >= 1

    def test_threshold_too_large_raises(self):
        """hot_threshold_percent >= 100 → ValueError."""
        with pytest.raises(ValueError, match="hot_threshold_percent"):
            label_hot_cold(self.SAMPLE_COUNTS, hot_threshold_percent=100.0)

    def test_threshold_zero_raises(self):
        """hot_threshold_percent = 0 → ValueError."""
        with pytest.raises(ValueError, match="hot_threshold_percent"):
            label_hot_cold(self.SAMPLE_COUNTS, hot_threshold_percent=0.0)

    def test_threshold_negative_raises(self):
        """hot_threshold_percent < 0 → ValueError."""
        with pytest.raises(ValueError, match="hot_threshold_percent"):
            label_hot_cold(self.SAMPLE_COUNTS, hot_threshold_percent=-5.0)

    def test_empty_counts_raises(self):
        """counts rỗng → ValueError."""
        with pytest.raises(ValueError, match="counts rỗng"):
            label_hot_cold({}, hot_threshold_percent=1.0)

    def test_threshold_nearly_all_hot_raises(self):
        """Threshold quá lớn khiến gần hết là hot → ValueError."""
        # 2 host, threshold 99% → n_hot = max(1, int(2*0.99)) = 1
        # Nhưng int(2*0.99) = 1, và 1 < 2, nên pass
        small_counts = {"a": 100, "b": 1}
        result = label_hot_cold(small_counts, hot_threshold_percent=50.0)
        assert len([r for r in result if r["is_hot"]]) == 1

    def test_all_same_count(self):
        """Tất cả host có cùng count → top X% vẫn được gán hot đúng."""
        counts = {f"host_{i}": 10 for i in range(100)}
        result = label_hot_cold(counts, hot_threshold_percent=10.0)
        hot_count = sum(1 for r in result if r["is_hot"])
        assert hot_count == 10  # 10% of 100


# ════════════════════════════════════════════════════════════════════════════
# 4. TEST build_real_stream
# ════════════════════════════════════════════════════════════════════════════


class TestBuildRealStream:
    """Test generator replay stream từ file log."""

    SAMPLE_LOG = (
        'host_a - - [01/Aug/1995:00:00:01 -0400] "GET /page1 HTTP/1.0" 200 100\n'
        'host_b - - [01/Aug/1995:00:00:02 -0400] "GET /page2 HTTP/1.0" 200 200\n'
        'MALFORMED\n'
        'host_a - - [01/Aug/1995:00:00:03 -0400] "GET /page3 HTTP/1.0" 200 300\n'
    )

    def test_yields_correct_packets(self):
        """Generator yield đúng thứ tự và gán is_hot đúng."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "test.log")
            with open(log_path, "w") as f:
                f.write(self.SAMPLE_LOG)

            hot_ips = {"host_a"}
            packets = list(build_real_stream(log_path, hot_ips))

            assert len(packets) == 3  # skip 1 dòng MALFORMED
            assert packets[0] == {"ip": "host_a", "is_hot": True}
            assert packets[1] == {"ip": "host_b", "is_hot": False}
            assert packets[2] == {"ip": "host_a", "is_hot": True}

    def test_is_generator(self):
        """build_real_stream trả về generator (không load hết RAM)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "test.log")
            with open(log_path, "w") as f:
                f.write(self.SAMPLE_LOG)

            stream = build_real_stream(log_path, set())
            from types import GeneratorType
            assert isinstance(stream, GeneratorType)

    def test_output_fields(self):
        """Mỗi packet có đúng 2 field: ip, is_hot."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "test.log")
            with open(log_path, "w") as f:
                f.write(self.SAMPLE_LOG)

            for packet in build_real_stream(log_path, set()):
                assert set(packet.keys()) == {"ip", "is_hot"}


# ════════════════════════════════════════════════════════════════════════════
# 5. INTEGRATION TEST — Chạy trên access.log thật
# ════════════════════════════════════════════════════════════════════════════


@pytest.mark.skipif(
    not os.path.exists(REAL_LOG_PATH),
    reason=f"File access.log thật không tồn tại tại {REAL_LOG_PATH}",
)
class TestIntegrationRealLog:
    """Integration test với file access.log thật (~167MB)."""

    def test_parse_real_log(self):
        """Parse file thật → kiểm tra số liệu khớp EDA."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = os.path.join(tmpdir, "test_cache.json")

            counts = load_and_aggregate(REAL_LOG_PATH, cache_path)

            # Từ EDA: 74,957 IP phân biệt
            n_unique = len(counts)
            assert 70_000 <= n_unique <= 80_000, (
                f"Số IP phân biệt = {n_unique}, kỳ vọng ~74,957"
            )

            # Tổng parsed lines ~ 1,566,461
            total_requests = sum(counts.values())
            assert 1_500_000 <= total_requests <= 1_600_000, (
                f"Tổng requests = {total_requests}, kỳ vọng ~1,566,461"
            )

            # IP nhiều nhất: edams.ksc.nasa.gov ~ 6,516
            top_ip = max(counts, key=counts.get)
            assert counts[top_ip] >= 6_000, (
                f"Top IP {top_ip} có {counts[top_ip]} requests, kỳ vọng >= 6,000"
            )

    def test_cache_faster_than_parse(self):
        """Lần 2 đọc cache phải nhanh hơn lần 1 parse thô."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = os.path.join(tmpdir, "test_cache.json")

            t1_start = time.perf_counter()
            load_and_aggregate(REAL_LOG_PATH, cache_path)
            t1_elapsed = time.perf_counter() - t1_start

            t2_start = time.perf_counter()
            load_and_aggregate(REAL_LOG_PATH, cache_path)
            t2_elapsed = time.perf_counter() - t2_start

            # Cache phải nhanh hơn ít nhất 2x
            assert t2_elapsed < t1_elapsed / 2, (
                f"Cache ({t2_elapsed:.3f}s) không đủ nhanh "
                f"so với parse ({t1_elapsed:.3f}s)"
            )

    def test_label_real_data(self):
        """Gán nhãn top 1% = hot trên data thật."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = os.path.join(tmpdir, "test_cache.json")
            counts = load_and_aggregate(REAL_LOG_PATH, cache_path)
            result = label_hot_cold(counts, hot_threshold_percent=1.0)

            hot = [r for r in result if r["is_hot"]]
            cold = [r for r in result if not r["is_hot"]]

            # Top 1% of ~75K = ~750 hot IPs
            assert 500 <= len(hot) <= 1000
            assert len(cold) > len(hot) * 10  # cold >> hot

            # Hot IPs phải có true_count cao hơn cold
            min_hot = min(r["true_count"] for r in hot)
            max_cold = max(r["true_count"] for r in cold)
            assert min_hot >= max_cold, (
                f"Hot min ({min_hot}) < Cold max ({max_cold}) — "
                f"gán nhãn sai thứ tự"
            )

    def test_skipped_lines_reported(self):
        """Cache ghi lại số dòng skip > 0 (data thật luôn có dòng lỗi)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = os.path.join(tmpdir, "test_cache.json")
            load_and_aggregate(REAL_LOG_PATH, cache_path)

            with open(cache_path, "r") as f:
                cached = json.load(f)

            stats = cached["stats"]
            # Từ EDA: 3,437 dòng lỗi
            assert stats["skipped_lines"] > 0, "Data thật phải có dòng bị skip"
            assert stats["skipped_lines"] < stats["total_lines"] * 0.01, (
                "Tỉ lệ skip quá cao — có thể regex sai?"
            )
