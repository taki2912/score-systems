@echo off
echo ========================================
echo   数据库自动备份 - 每10分钟一次
echo ========================================
echo.

cd /d "%~dp0"

:loop
echo [%date% %time%] 执行备份...
python auto_backup.py

echo.
echo 等待 10 分钟...
timeout /t 600 /nobreak > nul
goto loop
