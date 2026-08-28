#!/bin/bash
cd "$(dirname "$0")"
# Remove stale lock file if it exists
rm -f .git/index.lock
git add data/travel_daily.json docs/index.html generate_dashboard.py
git commit -m "📊 2026-08-28 | 25国×250条 | 🔥爆25 热50 新100 常规75"
git push origin main
echo "✅ Push complete!"
