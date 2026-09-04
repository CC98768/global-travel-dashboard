@echo off
chcp 65001 >nul
echo ========================================
echo  全球旅游看板 v4.0 - 推送到GitHub
echo  8.6-9.4 全部数据 | 30天×250条=7500条
echo ========================================
echo.

cd /d "%~dp0"

git add data/travel_daily.json docs/index.html validate_quality.py
git commit -m "v4.0: 重写8.6-9.4全部数据 | 30天×250条=7500条 | 0违规 | 验证脚本v4.0"
git push origin main

echo.
echo ✅ 推送完成！
pause
