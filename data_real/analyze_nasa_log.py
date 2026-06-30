"""
Script phân tích NASA HTTP Access Log
Chạy: python analyze_nasa_log.py
Sau đó copy toàn bộ output paste cho Claude
"""

import re
import numpy as np
from collections import Counter


def parse_log_line(line):
    """Parse 1 dòng Apache log format."""
    pattern = r'^(\S+) \S+ \S+ \[.*?\] "(\S+) (\S+) \S+" (\d+) (\S+)'
    m = re.match(pattern, line)
    if m:
        return {
            "ip":     m.group(1),
            "method": m.group(2),
            "url":    m.group(3),
            "status": int(m.group(4)),
        }
    return None


def parse_csv_line(line, header):
    """Parse 1 dòng CSV nếu file đã được format sẵn."""
    parts = line.strip().split(",")
    if len(parts) < len(header):
        return None
    return dict(zip(header, parts))


# ── CẤU HÌNH ────────────────────────────────────────────────
FILE_PATH = "access.log"   

# Xem thử cấu trúc file
print("=== XEM THỬ CẤU TRÚC FILE ===")
with open(FILE_PATH, "r", errors="replace") as f:
    for i, line in enumerate(f):
        if i >= 5:  # chỉ xem 5 dòng đầu
            break
        print(f"Dòng {i+1} RAW: {repr(line)}")
        record = parse_log_line(line)
        print(f"  → Parse được: {record}")
        if record:
            for key, val in record.items():
                print(f"     {key:10s}: {repr(val):30s} type={type(val).__name__}")
        print()
        
# Nếu file là CSV (có header), đổi IS_CSV = True
IS_CSV = False
# ─────────────────────────────────────────────────────────────


print("=" * 60)
print("PHÂN TÍCH NASA HTTP ACCESS LOG")
print("=" * 60)

ips   = []
urls  = []
total_lines  = 0
parsed_lines = 0
error_lines  = 0

try:
    with open(FILE_PATH, "r", errors="replace") as f:
        header = None

        for i, line in enumerate(f):
            total_lines += 1

            # Bỏ qua header nếu là CSV
            if IS_CSV and i == 0:
                header = [c.strip() for c in line.split(",")]
                print(f"CSV Header: {header}")
                continue

            line = line.strip()
            if not line:
                continue

            if IS_CSV and header:
                record = parse_csv_line(line, header)
                if record:
                    ip  = record.get("ip",  record.get("IP",  record.get("host", "")))
                    url = record.get("url", record.get("URL", record.get("path", "")))
                    if ip and url:
                        ips.append(ip.strip())
                        urls.append(url.strip())
                        parsed_lines += 1
                    else:
                        error_lines += 1
            else:
                record = parse_log_line(line)
                if record:
                    ips.append(record["ip"])
                    urls.append(record["url"])
                    parsed_lines += 1
                else:
                    error_lines += 1

            # Progress mỗi 500K dòng
            if total_lines % 500_000 == 0:
                print(f"  ... đã đọc {total_lines:,} dòng")

except FileNotFoundError:
    print(f"\n❌ Không tìm thấy file: {FILE_PATH}")
    print("   Hãy đổi FILE_PATH ở đầu script thành đường dẫn đúng.")
    exit(1)


# ── PHÂN TÍCH ────────────────────────────────────────────────
print(f"\n{'='*60}")
print("1. TỔNG QUAN")
print(f"{'='*60}")
print(f"Tổng dòng trong file  : {total_lines:,}")
print(f"Dòng parse được       : {parsed_lines:,}")
print(f"Dòng lỗi / bỏ qua     : {error_lines:,}")

print(f"\n{'='*60}")
print("2. PHÂN TÍCH IP")
print(f"{'='*60}")
ip_counts = Counter(ips)
n_unique_ip = len(ip_counts)
top10_ip = ip_counts.most_common(10)
least5_ip = ip_counts.most_common()[:-6:-1]

print(f"Số IP phân biệt       : {n_unique_ip:,}")
print(f"IP xuất hiện nhiều nhất: {top10_ip[0][1]:,} lần")
print(f"IP xuất hiện ít nhất  : {min(ip_counts.values())} lần")
print(f"Trung bình mỗi IP     : {np.mean(list(ip_counts.values())):.1f} lần")

print(f"\nTop 10 IP:")
for rank, (ip, cnt) in enumerate(top10_ip, 1):
    pct = cnt / parsed_lines * 100
    print(f"  #{rank:2d}  {ip:45s}  {cnt:>8,}  ({pct:.2f}%)")

print(f"\n5 IP ít nhất:")
for ip, cnt in least5_ip:
    print(f"       {ip:45s}  {cnt:>8,}")

# Zipf beta cho IP
if n_unique_ip >= 5:
    sorted_counts = sorted(ip_counts.values(), reverse=True)
    ranks = np.arange(1, len(sorted_counts) + 1)
    log_r = np.log(ranks)
    log_c = np.log(np.array(sorted_counts, dtype=float))
    beta_ip = -np.polyfit(log_r, log_c, 1)[0]
    print(f"\nBeta Zipf (IP)        : {beta_ip:.3f}")
    print(f"  (0 = uniform, ~1 = Zipf điển hình, >1 = rất dốc)")


print(f"\n{'='*60}")
print("3. PHÂN TÍCH URL")
print(f"{'='*60}")
url_counts = Counter(urls)
n_unique_url = len(url_counts)
top10_url = url_counts.most_common(10)

print(f"Số URL phân biệt      : {n_unique_url:,}")
print(f"URL xuất hiện nhiều nhất: {top10_url[0][1]:,} lần")
print(f"Trung bình mỗi URL    : {np.mean(list(url_counts.values())):.1f} lần")

print(f"\nTop 10 URL:")
for rank, (url, cnt) in enumerate(top10_url, 1):
    pct = cnt / parsed_lines * 100
    print(f"  #{rank:2d}  {cnt:>8,}  ({pct:.2f}%)  {url[:60]}")

# Zipf beta cho URL
sorted_url = sorted(url_counts.values(), reverse=True)
ranks_url  = np.arange(1, len(sorted_url) + 1)
beta_url   = -np.polyfit(np.log(ranks_url),
                         np.log(np.array(sorted_url, dtype=float)), 1)[0]
print(f"\nBeta Zipf (URL)       : {beta_url:.3f}")


print(f"\n{'='*60}")
print("4. KIỂM TRA HOT/COLD (Elephant/Mice) — THEO IP")
print(f"{'='*60}")
all_counts = sorted(ip_counts.values(), reverse=True)
mean_count = np.mean(all_counts)
threshold  = mean_count

hot  = [(ip, c) for ip, c in ip_counts.items() if c > threshold]
cold = [(ip, c) for ip, c in ip_counts.items() if c <= threshold]

hot_total  = sum(c for _, c in hot)
cold_total = sum(c for _, c in cold)

print(f"Ngưỡng phân chia      : {threshold:,.0f} requests")
print(f"Hot IPs  (> ngưỡng)   : {len(hot):,} IPs  | {hot_total:,} req ({hot_total/parsed_lines*100:.1f}%)")
print(f"Cold IPs (<= ngưỡng)  : {len(cold):,} IPs  | {cold_total:,} req ({cold_total/parsed_lines*100:.1f}%)")

if cold:
    hot_mean  = np.mean([c for _, c in hot])  if hot  else 0
    cold_mean = np.mean([c for _, c in cold]) if cold else 1
    print(f"Gap factor thực tế    : {hot_mean/cold_mean:.1f}x")
    print(f"  (hot avg={hot_mean:.0f} req/IP, cold avg={cold_mean:.0f} req/IP)")


print(f"\n{'='*60}")
print("5. ĐÁNH GIÁ PHÂN PHỐI")
print(f"{'='*60}")

# Phân vị
counts_arr = np.array(sorted(ip_counts.values(), reverse=True))
p50  = np.percentile(counts_arr, 50)
p90  = np.percentile(counts_arr, 90)
p99  = np.percentile(counts_arr, 99)
p999 = np.percentile(counts_arr, 99.9)

print(f"Phân vị IP counts:")
print(f"  P50  : {p50:,.0f}   (median)")
print(f"  P90  : {p90:,.0f}")
print(f"  P99  : {p99:,.0f}")
print(f"  P99.9: {p999:,.0f}")
print(f"  Max  : {max(counts_arr):,.0f}")

top1pct   = int(n_unique_ip * 0.01) or 1
top1_sum  = sum(sorted(ip_counts.values(), reverse=True)[:top1pct])
print(f"\nTop 1% IP ({top1pct} IPs) chiếm {top1_sum/parsed_lines*100:.1f}% tổng traffic")

print(f"\n{'='*60}")
print("✅ XONG — Copy toàn bộ output này gửi cho Claude!")
print(f"{'='*60}")
