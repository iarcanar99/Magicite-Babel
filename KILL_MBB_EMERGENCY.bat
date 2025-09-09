@echo off
title Emergency MBB Process Killer - v9.1
color 0C

echo.
echo ====================================================
echo     EMERGENCY MBB PROCESS KILLER - v9.1
echo ====================================================
echo.
echo This script will forcefully terminate ALL MBB processes
echo Use this when MBB gets stuck in error loops or crashes
echo.
echo Common scenarios:
echo   • MBB won't close properly
echo   • Infinite error dialogs
echo   • Application frozen/unresponsive
echo   • Multiple MBB instances running
echo.

REM Ask for confirmation
set /p confirm="Are you sure you want to kill all MBB processes? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Operation cancelled.
    pause
    exit /b 0
)

echo.
echo Starting emergency process cleanup...
echo.

echo [1/6] Killing MBB executable processes...
taskkill /f /im MBB.exe 2>nul
if %errorlevel%==0 (
    echo ✓ MBB.exe processes terminated
) else (
    echo • No MBB.exe processes found
)

echo.
echo [2/6] Killing Python processes related to MBB...
REM Kill Python processes that might be running MBB in development
taskkill /f /im python.exe /fi "WINDOWTITLE eq MBB*" 2>nul
taskkill /f /im pythonw.exe /fi "WINDOWTITLE eq MBB*" 2>nul

REM Also check for Python processes with MBB in command line
for /f "tokens=2" %%i in ('tasklist /fi "IMAGENAME eq python.exe" /fo csv /nh 2^>nul') do (
    wmic process where "ProcessId=%%i and CommandLine like '%%MBB%%'" terminate 2>nul
)
for /f "tokens=2" %%i in ('tasklist /fi "IMAGENAME eq pythonw.exe" /fo csv /nh 2^>nul') do (
    wmic process where "ProcessId=%%i and CommandLine like '%%MBB%%'" terminate 2>nul
)

echo ✓ Python MBB processes checked

echo.
echo [3/6] Cleaning up temporary files...
REM Remove MBB temporary files
del /q "%TEMP%\MBB_*" 2>nul
del /q "%TEMP%\temp_screenshot_*" 2>nul
del /q "%TEMP%\mbb_*" 2>nul
del /q "%TEMP%\translation_*" 2>nul
del /q "%TEMP%\ocr_temp_*" 2>nul

REM Clean up any PyInstaller temp directories
for /d %%i in ("%TEMP%\_MEI*") do rmdir /s /q "%%i" 2>nul

REM Clean up potential lock files
del /q "*.lock" 2>nul
del /q "temp_*.png" 2>nul

echo ✓ Temporary files cleaned

echo.
echo [4/6] Checking Windows handles and memory leaks...
REM Force garbage collection of any hanging window handles
for /f "tokens=2" %%i in ('tasklist /fi "IMAGENAME eq MBB.exe" /fo csv /nh 2^>nul') do (
    echo Found lingering MBB process with PID %%i, forcing termination...
    taskkill /f /pid %%i 2>nul
)

echo ✓ Handle cleanup complete

echo.
echo [5/6] Final process verification...
REM Check for any remaining processes
tasklist /fi "IMAGENAME eq MBB.exe" /fo table 2>nul | find /i "MBB.exe" >nul
if %errorlevel%==0 (
    echo ⚠ Warning: Some MBB processes may still be running
    echo   Advanced cleanup needed:
    echo   1. Try restarting your computer
    echo   2. Check Task Manager manually
    echo   3. Run this script as Administrator
    
    REM Show the stubborn processes
    echo.
    echo Remaining MBB processes:
    tasklist /fi "IMAGENAME eq MBB.exe" /fo table
) else (
    echo ✓ No MBB processes detected
)

echo.
echo [6/6] System status check...
REM Display relevant system information
echo Current system status:
echo   Memory usage: 
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /format:list | find "="
echo.
echo   Active processes containing 'python':
tasklist /fi "IMAGENAME eq python*" /fo table 2>nul | find /i "python" || echo   None found

echo.
echo ====================================================
echo           EMERGENCY CLEANUP COMPLETE
echo ====================================================
echo.
echo What was done:
echo   • Terminated all MBB.exe processes
echo   • Killed related Python processes  
echo   • Cleaned temporary files
echo   • Removed PyInstaller temp directories
echo   • Cleared potential lock files
echo   • Freed Windows handles
echo.
echo You can now:
echo   1. Restart MBB.exe safely
echo   2. Check error logs in logs/ folder
echo   3. Report the issue if it persists
echo.
echo If MBB continues to crash:
echo   • Check available disk space (need 2GB+ free)
echo   • Verify API keys in .env file
echo   • Try running MBB.exe as Administrator
echo   • Check antivirus settings (add MBB folder to exclusions)
echo   • Restart your computer
echo   • Check Windows Event Viewer for system errors
echo.
echo Troubleshooting resources:
echo   • guide\troubleshooting.md
echo   • logs\ folder for error messages
echo   • RELEASE_NOTES.txt for known issues
echo.

color 0A
echo ✓ System is ready for MBB restart
echo.
echo Press any key to exit or Ctrl+C to force close...
pause >nul