@echo off
:: 以管理员身份启动 (当 Tappo 以管理员权限运行时, 普通权限的模拟点击会被系统拦截)
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
chcp 65001 >nul
cd /d "%~dp0"
python tappo_auto.py
pause
