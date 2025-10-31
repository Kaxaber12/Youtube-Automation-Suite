@echo off
REM YouTube Automation Suite - CLI Launcher
REM This batch file starts the CLI version with help information

echo ================================================================================
echo      YouTube Automation Suite - CLI Version
echo ================================================================================
echo.
echo Showing available commands...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    echo.
    pause
    exit /b 1
)

REM Check if src directory exists
if not exist "src\youtube_automation_cli.py" (
    echo ERROR: Cannot find youtube_automation_cli.py
    echo Please make sure you're running this from the project root directory
    echo.
    pause
    exit /b 1
)

REM Show help information
python src\youtube_automation_cli.py --help

echo.
echo ================================================================================
echo.
echo To run automation, use commands like:
echo   python src\youtube_automation_cli.py --action like --file likes.txt
echo   python src\youtube_automation_cli.py --action comment --file comments.txt --video VIDEO_ID
echo   python src\youtube_automation_cli.py --action subscribe --file channels.txt
echo.
echo For more information, see docs/USER_GUIDE.md
echo.
echo ================================================================================
echo.
pause
