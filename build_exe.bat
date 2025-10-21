@echo off
echo ================================================
echo Voice Dictation MVP - Build Executable
echo ================================================
echo.

REM Check if in virtual environment
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo Step 1: Installing/upgrading PyInstaller...
pip install --upgrade pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo Step 2: Preserving config.json if exists...
if exist dist\config\config.json (
    echo Config found, backing up...
    copy dist\config\config.json config_backup.json >nul
    set CONFIG_BACKUP=1
) else (
    set CONFIG_BACKUP=0
)

echo.
echo Step 3: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Step 4: Building executable...
pyinstaller VoiceDictation.spec
if errorlevel 1 (
    echo ERROR: Build failed
    if %CONFIG_BACKUP%==1 (
        echo Restoring config backup...
        mkdir dist\config 2>nul
        copy config_backup.json dist\config\config.json >nul
        del config_backup.json
    )
    pause
    exit /b 1
)

echo.
echo Step 5: Restoring config.json if backed up...
if %CONFIG_BACKUP%==1 (
    echo Restoring your config...
    mkdir dist\config 2>nul
    copy config_backup.json dist\config\config.json >nul
    del config_backup.json
    echo Config restored!
) else (
    echo No previous config found
    echo You need to create dist\config\config.json
)

echo.
echo ================================================
echo Build completed successfully!
echo ================================================
echo.
echo Executable location: dist\VoiceDictation.exe
echo.
if %CONFIG_BACKUP%==1 (
    echo Config: Already configured - ready to use!
) else (
    echo Next steps:
    echo 1. Create dist\config\config.json from template
    echo 2. Add your API keys
)
echo.
echo Run: dist\VoiceDictation.exe
echo.
pause
