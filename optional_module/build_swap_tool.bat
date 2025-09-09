@echo off
echo ========================================
echo       MBB Data Swap Tool Builder
echo ========================================
echo.

:: ตรวจสอบ Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python first.
    pause
    exit /b 1
)

:: ตรวจสอบ PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyInstaller...
    pip install pyinstaller
)

:: ตรวจสอบ PyQt5
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyQt5...
    pip install PyQt5
)

echo [INFO] Building MBB Data Swap Tool...
echo.

:: สร้าง exe ด้วย PyInstaller
pyinstaller --onefile ^
    --windowed ^
    --name="MBB_Data_Swap_Tool" ^
    --icon="..\app_icon.ico" ^
    --add-data="Manager.py;." ^
    --distpath="dist" ^
    --workpath="build" ^
    --specpath="." ^
    swap_data.py

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Build completed!
echo Location: %~dp0dist\MBB_Data_Swap_Tool.exe
echo.

:: เปิดโฟลเดอร์ dist
if exist "dist\MBB_Data_Swap_Tool.exe" (
    echo [INFO] Opening dist folder...
    explorer dist
) else (
    echo [WARNING] Executable not found in dist folder
)

pause
