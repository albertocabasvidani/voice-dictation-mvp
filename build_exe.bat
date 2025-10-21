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
echo Step 2: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Step 3: Building executable...
pyinstaller VoiceDictation.spec
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ================================================
echo Build completed successfully!
echo ================================================
echo.
echo Executable location: dist\VoiceDictation.exe
echo.
echo Next steps:
echo 1. Copy config\config.template.json to config\config.json
echo 2. Edit config.json with your API keys
echo 3. Run dist\VoiceDictation.exe
echo.
pause
