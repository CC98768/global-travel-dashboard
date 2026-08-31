@echo off
chcp 65001 >nul
echo ==========================================
echo   GitHub 数据看板恢复脚本
echo   回滚今日定时任务的垃圾数据
echo ==========================================
echo.

cd /d "%~dp0"
echo 当前目录: %CD%

echo.
echo [1/5] 恢复 travel_daily.json ...
git checkout HEAD -- data/travel_daily.json

echo [2/5] 恢复 docs/index.html ...
git checkout HEAD -- data/docs/index.html

echo [3/5] 恢复 index.html ...
git checkout HEAD -- data/index.html

echo [4/5] 清理 agent 产生的垃圾文件 ...
del /f /q data\group4.json data\test2.json data\test_write.txt 2>nul

echo.
echo [5/5] 强制推送到 GitHub ...
git push origin master --force

echo.
echo ==========================================
echo   ✅ 恢复完成！请刷新 GitHub 网页确认
echo ==========================================
pause
