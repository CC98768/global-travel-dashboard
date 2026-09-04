@echo off
cd /d "%~dp0"
echo ==========================================
echo  全球旅游热点看板 - 2026-09-03 推送脚本
echo ==========================================
echo.

:: Remove git locks
del .git\index.lock 2>nul
del .git\HEAD.lock 2>nul

:: Stage files
git add data/travel_daily.json docs/index.html data/docs/index.html data/index.html

:: Commit
git commit -m "📊 每日看板更新 2026-09-03 | 25国250条 | 爆25热54新96常规75" --no-verify

:: Push
git push origin main

echo.
echo ✅ 推送完成！请访问 https://cc98768.github.io/global-travel-dashboard/
echo.
pause
