@echo off
cd /d "%~dp0"
git add data/travel_daily.json docs/index.html index.html
git commit -m "2026-08-27: 25国250条旅游要闻" --no-verify
git push origin main
pause
