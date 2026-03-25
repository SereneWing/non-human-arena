@echo off
chcp 65001 >nul
echo ========================================
echo   NonHumanArena - AI双智能体对话系统
echo ========================================
echo.
echo 启动服务中，请稍候...
echo 访问地址: http://127.0.0.1:8000
echo 按 Ctrl+C 停止服务
echo.

cd /d "%~dp0src"
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

pause
