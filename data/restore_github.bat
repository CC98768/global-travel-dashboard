@echo off
chcp 65001 >nul
echo ==========================================
echo  GitHub 数据看板恢复脚本
echo ==========================================
echo.

cd /d "%~dp0"

echo [1] 恢复 travel_daily.json 到 Git 原版...
git checkout HEAD -- travel_daily.json
echo [2] 恢复 docs/index.html 到 Git 原版...
git checkout HEAD -- docs/index.html
echo [3] 恢复 index.html 到 Git 原版...
git checkout HEAD -- index.html

echo.
echo [4] 清理垃圾文件...
del /f /q group4.json test2.json test_write.txt 2>nul

echo.
echo [5] 强制推送到 GitHub（回滚垃圾数据）...
git push origin master --force

echo.
echo ==========================================
echo  恢复完成！请检查 GitHub 网页确认
echo ==========================================
pause
