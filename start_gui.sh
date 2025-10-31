#!/bin/bash
# YouTube Automation Suite - GUI Launcher
# This script starts the GUI version of the application

echo "================================================================================"
echo "     YouTube Automation Suite - GUI Version"
echo "================================================================================"
echo ""
echo "Starting the GUI application..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    echo ""
    exit 1
fi

# Check if src directory exists
if [ ! -f "src/youtube_automation_gui.py" ]; then
    echo "ERROR: Cannot find youtube_automation_gui.py"
    echo "Please make sure you're running this from the project root directory"
    echo ""
    exit 1
fi

# Run the GUI application
python3 src/youtube_automation_gui.py

# Check if there was an error
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Application failed to start"
    echo "Check the error message above for details"
    echo ""
    read -p "Press Enter to continue..."
fi
