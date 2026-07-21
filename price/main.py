import subprocess
import json
import jdatetime

# Run command
result = subprocess.run(
    [
        "toobit",
        "market",
        "klines",
        "--symbol", "BTCUSDT",
        "--interval", "4h",
        "--limit", "120",
        "--json"
    ],
    capture_output=True,
    text=True,
    check=True
)

# Parse JSON
data = json.loads(result.stdout)

# Iran (Jalali) date
iran_date = jdatetime.datetime.now().strftime("%Y-%m-%d")

# Filename
filename = f"{iran_date}.json"

# Save JSON
with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Saved: {filename}")