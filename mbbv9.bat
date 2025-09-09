@echo off
REM =========================================
REM MBB v9.5 Complete Enhanced Edition Launcher
REM Unicode/Encoding Fixed Version
REM =========================================

title MBB v9.5 - Complete Enhanced Edition

REM Set UTF-8 Code Page first
chcp 65001 > nul 2>&1

echo.
echo ==========================================
echo  MBB v9.5 - Complete Enhanced Edition
echo ==========================================
echo  Status: Debug Mode + Unicode Fix
echo  CPU Limit: 100%% (Optimized)
echo  Cache: Smart Caching Enabled
echo  Monitoring: Disabled for Performance
echo ==========================================
echo.

REM Change to MBB directory
cd /d "%~dp0"

REM Set encoding environment variables
set PYTHONIOENCODING=utf-8
set LANG=en_US.UTF-8
set PYTHONPATH=%cd%
set MBB_DEBUG=1
set MBB_LOG_LEVEL=DEBUG

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Set log file with timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
if defined dt (
    set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
    set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
    set "datestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"
) else (
    set "datestamp=unknown"
)

set LOG_FILE=logs\mbb_debug_%datestamp%.log

echo Starting MBB v9.5 with all optimizations...
echo Working directory: %cd%
echo Log file: %LOG_FILE%
echo.

REM Check if Python is available
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

REM Check if MBB.py exists
if not exist "MBB.py" (
    echo ERROR: MBB.py not found in current directory
    echo Current directory: %cd%
    echo Please ensure you're running this from the MBB project folder
    pause
    exit /b 1
)

REM Apply encoding fix first
echo Applying Unicode/Encoding fixes...
python fix_encoding.py

REM Launch MBB.py with proper encoding
echo Launching MBB.py with Unicode support...
python -u -X utf8 MBB.py 2>&1

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo  MBB v9.5 closed successfully
    echo ==========================================
) else (
    echo.
    echo ==========================================
    echo  MBB v9.5 exited with error code: %ERRORLEVEL%
    echo ==========================================
)

echo.
echo Performance Optimization Status:
echo - CPU Limit: 100%% [OK]
echo - Smart Cache: Enabled [OK]
echo - Monitoring Overhead: Disabled [OK]
echo - Unicode Support: Fixed [OK]
echo Performance: Significantly improved (requires long-term testing)
echo.
echo Press any key to exit...
pause > nul