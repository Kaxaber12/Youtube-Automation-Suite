@echo off
REM YouTube Automation Suite - GUI Launcher
REM This batch file starts the GUI version of the application

echo ================================================================================
echo      YouTube Automation Suite - GUI Version
echo ================================================================================
echo.
echo Starting the GUI application...
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
if not exist "src\youtube_automation_gui.py" (
    echo ERROR: Cannot find youtube_automation_gui.py
    echo Please make sure you're running this from the project root directory
    echo.
    pause
    exit /b 1
)

REM Run the GUI application
python src\youtube_automation_gui.py

REM If there was an error, pause to see the message
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Application failed to start
    echo Check the error message above for details
    echo.
    pause
)

exit /b %errorlevel%
