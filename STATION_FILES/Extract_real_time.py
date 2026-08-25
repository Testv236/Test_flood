from datetime import datetime, timedelta
import json
from pathlib import Path

BASE_DIR = Path.cwd()

STATION_FILES = [BASE_DIR / f"station_{i}.json" for i in range(1, 10)]

raw_stations_data = []
for i, file_path in enumerate(STATION_FILES, start=1):
  if file_path.exists():
    with open(file_path, "r", encoding="utf-8") as f:
      data = json.load(f)
      # Gán tên trạm chuẩn hóa[cite: 5]
      data["station_name"] = data.get("station", f"Station {i}")
      raw_stations_data.append(data)

# Giả sử 00:00 tương ứng t=0
base_start_time = datetime(2026, 8, 1, 0, 0, 0) # 00:00 1/8/2026

# Scan từng phút t từ 600 đến 720
T_START = 0
T_END = 1440

# Thư mục lưu các file JSON
output_dir = BASE_DIR / "snapshots_by_minute"
output_dir.mkdir(exist_ok=True)

for t in range(T_START, T_END + 1):
  # Tính thời gian thực tế (VD: t=600 -> 10:00, t=720 -> 12:00)
  current_time = base_start_time + timedelta(minutes=t)
  timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

  # Gom dữ liệu 9 trạm tại mốc t
  minute_snapshot = {
      "time_min": t,
      "simulation_time": current_time.strftime("%H:%M"),
      "timestamp": timestamp_str,
      "stations_data": [],
  }

  for station in raw_stations_data:
    # Lấy đúng bản ghi ở vị trí t (hoặc lọc theo time_min == t)
    if t < len(station["data"]):
      row = station["data"][t]
      minute_snapshot["stations_data"].append({
          "station_name": station["station_name"],
          "H_tide": float(row["H_tide"]),
          "R": float(row["R(t)"]),  # Đọc R(t)
          "D": float(row["D(t)"]),  # Đọc D(t) 
      })

  # Xuất ra file JSON cho từng phút (VD: snapshot_t600.json, snapshot_t601.json...)
  file_name = output_dir / f"snapshot_t{t}.json"
  with open(file_name, "w", encoding="utf-8") as f:
    json.dump(minute_snapshot, f, ensure_ascii=False, indent=2)


print(
    f"\n Đã tạo xong {T_END - T_START + 1} file JSON snapshot theo từng phút"
    f" trong thư mục: {output_dir.name}"
)