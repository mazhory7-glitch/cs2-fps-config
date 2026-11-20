@echo off
setlocal
where py.exe >nul 2>&1
if errorlevel 1 (
    python.exe "%~dp0rollback_cs2.py"
) else (
    py.exe -3 "%~dp0rollback_cs2.py"
)
set "rollback_status=%errorlevel%"
pause
exit /b %rollback_status%
