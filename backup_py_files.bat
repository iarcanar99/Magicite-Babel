@echo off
setlocal enabledelayedexpansion

:: --- Configuration ---
set MAX_VERSIONS=10

:: --- Get Current Date (DD-MM-YYYY) ---
echo Getting current date...
for /f %%a in ('wmic os get LocalDateTime ^| findstr \.') do set datetime=%%a
set year=%datetime:~0,4%
set month=%datetime:~4,2%
set day=%datetime:~6,2%
set formatted_date=%day%-%month%-%year%
echo Today's Date: %formatted_date%

:: --- Define Backup Folder Name ---
set base_folder=MBB_backup_%formatted_date%_v1
set backup_folder=%base_folder%
echo Base backup name: %base_folder%

:: --- Check for Existing Backup and Handle Versioning ---
set version=1
:check_version
set versioned_folder=MBB_backup_%formatted_date%_v!version!
if exist "%versioned_folder%" (
    set /a version+=1
    if !version! gtr %MAX_VERSIONS% (
        echo ERROR: Maximum versions ^(%MAX_VERSIONS%^) reached for today ^(%formatted_date%^). Cannot create new backup.
        goto :end
    )
    goto :check_version
)
set backup_folder=!versioned_folder!
echo Selected backup folder: !backup_folder!

:: --- Create Backup Folder ---
echo Creating backup folder: "%backup_folder%"
mkdir "%backup_folder%"
if errorlevel 1 (
    echo ERROR: Failed to create backup folder '%backup_folder%'. Check permissions or path.
    goto :end
)

:: --- Initialize Counters ---
set py_count=0
set json_count=0
set md_count=0
set html_count=0
set before_start_count=0
set structure_manuals_count=0
set total_count=0

echo.
echo Starting file backup process into "%backup_folder%"...
echo Current Directory: "%cd%"
echo.

:: --- Backup Python files (.py) in current directory ONLY ---
echo --- Backing up .py files ---
for %%f in (*.py) do (
    if /i "%%~nxf" neq "%~nx0" ( :: Exclude this script itself
        echo   Copying %%f...
        copy "%%f" "%backup_folder%" > nul
        set /a py_count+=1
        set /a total_count+=1
    ) else (
        echo   Skipping script file: %%f
    )
)

:: --- Backup before_start folder (if exists) ---
echo --- Backing up before_start folder ---
if exist "before_start" (
    echo   Creating before_start directory in backup...
    mkdir "%backup_folder%\before_start" 2>nul
    
    :: Copy all .py files from before_start root
    for %%f in (before_start\*.py) do (
        if exist "%%f" (
            echo   Copying %%f...
            copy "%%f" "%backup_folder%\before_start\" > nul
            set /a before_start_count+=1
            set /a total_count+=1
        )
    )
    
    :: Copy all .md files from before_start root
    for %%f in (before_start\*.md) do (
        if exist "%%f" (
            echo   Copying %%f...
            copy "%%f" "%backup_folder%\before_start\" > nul
            set /a before_start_count+=1
            set /a total_count+=1
        )
    )
    
    :: Copy all .py files from before_start\checkers (if exists)
    if exist "before_start\checkers" (
        echo   Creating checkers directory in backup...
        mkdir "%backup_folder%\before_start\checkers" 2>nul
        
        for %%f in (before_start\checkers\*.py) do (
            if exist "%%f" (
                echo   Copying %%f...
                copy "%%f" "%backup_folder%\before_start\checkers\" > nul
                set /a before_start_count+=1
                set /a total_count+=1
            )
        )
    ) else (
        echo   before_start\checkers folder not found, skipping...
    )
    
    :: Copy any other .py files from subdirectories in before_start
    for /d %%d in (before_start\*) do (
        if /i "%%~nxd" neq "checkers" (
            echo   Checking directory %%d for .py files...
            for %%f in (%%d\*.py) do (
                if exist "%%f" (
                    echo   Creating directory %%~nxd in backup...
                    mkdir "%backup_folder%\before_start\%%~nxd" 2>nul
                    echo   Copying %%f...
                    copy "%%f" "%backup_folder%\before_start\%%~nxd\" > nul
                    set /a before_start_count+=1
                    set /a total_count+=1
                )
            )
        )
    )
) else (
    echo   before_start folder not found, skipping...
)

:: --- Backup Structure_Manuals folder (if exists) ---
echo --- Backing up Structure_Manuals folder ---
if exist "Structure_Manuals" (
    echo   Creating Structure_Manuals directory in backup...
    mkdir "%backup_folder%\Structure_Manuals" 2>nul
    
    :: Copy all .md files from Structure_Manuals
    for %%f in (Structure_Manuals\*.md) do (
        if exist "%%f" (
            echo   Copying %%f...
            copy "%%f" "%backup_folder%\Structure_Manuals\" > nul
            set /a structure_manuals_count+=1
            set /a total_count+=1
        )
    )
    
    :: Copy any other files that might be in Structure_Manuals
    for %%f in (Structure_Manuals\*.py) do (
        if exist "%%f" (
            echo   Copying %%f...
            copy "%%f" "%backup_folder%\Structure_Manuals\" > nul
            set /a structure_manuals_count+=1
            set /a total_count+=1
        )
    )
    
    for %%f in (Structure_Manuals\*.json) do (
        if exist "%%f" (
            echo   Copying %%f...
            copy "%%f" "%backup_folder%\Structure_Manuals\" > nul
            set /a structure_manuals_count+=1
            set /a total_count+=1
        )
    )
    
    for %%f in (Structure_Manuals\*.html) do (
        if exist "%%f" (
            echo   Copying %%f...
            copy "%%f" "%backup_folder%\Structure_Manuals\" > nul
            set /a structure_manuals_count+=1
            set /a total_count+=1
        )
    )
    
    :: Handle any subdirectories in Structure_Manuals
    for /d %%d in (Structure_Manuals\*) do (
        echo   Creating subdirectory %%~nxd in Structure_Manuals backup...
        mkdir "%backup_folder%\Structure_Manuals\%%~nxd" 2>nul
        
        for %%f in (%%d\*.*) do (
            if exist "%%f" (
                echo   Copying %%f...
                copy "%%f" "%backup_folder%\Structure_Manuals\%%~nxd\" > nul
                set /a structure_manuals_count+=1
                set /a total_count+=1
            )
        )
    )
) else (
    echo   Structure_Manuals folder not found, skipping...
)

:: --- Backup specific JSON file (npc.json - case insensitive) ---
echo --- Backing up npc.json file ---
for %%f in (*) do (
    set filename=%%~nxf
    echo !filename! | findstr /i "^npc\.json$" >nul
    if !errorlevel! equ 0 (
        echo   Copying %%f...
        copy "%%f" "%backup_folder%" > nul
        set /a json_count+=1
        set /a total_count+=1
    )
)

:: --- Backup Markdown files (.md) in current directory ---
echo --- Backing up .md files ---
for %%f in (*.md) do (
    echo   Copying %%f...
    copy "%%f" "%backup_folder%" > nul
    set /a md_count+=1
    set /a total_count+=1
)

:: --- Backup index.html from main directory ---
echo --- Backing up index.html ---
if exist "index.html" (
    echo   Copying index.html...
    copy "index.html" "%backup_folder%" > nul
    set /a html_count+=1
    set /a total_count+=1
) else (
    echo   index.html not found, skipping...
)

:: --- Display Summary ---
echo.
echo ======================================
echo         Backup Complete!
echo ======================================
echo Target Folder : %backup_folder%
echo --------------------------------------
echo Python files (.py) : %py_count%
echo NPC JSON (npc.json): %json_count%
echo Markdown files (.md): %md_count%
echo HTML file (index.html): %html_count%
echo before_start files: %before_start_count%
echo Structure_Manuals files: %structure_manuals_count%
echo --------------------------------------
echo Total files backed up: %total_count%
echo ======================================
echo.

:end
echo Press any key to exit...
pause > nul
endlocal