@echo off
cd /d "%~dp0"
del .git\index.lock 2>nul
del .git\HEAD.lock 2>nul
git add data/travel_daily.json docs/index.html index.html generate_dashboard.py
git commit -m "2026-08-28: 25国250条 | 恢复8/11-8/27历史原始数据 + 新增今日数据" --no-verify
git push origin main
echo.
echo Push complete! Check cc98768.github.io/global-travel-dashboard/
pause
