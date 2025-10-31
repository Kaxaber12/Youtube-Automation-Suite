#!/bin/bash
# YouTube Automation Suite - CLI Launcher
# This script starts the CLI version with help information

echo "================================================================================"
echo "     YouTube Automation Suite - CLI Version"
echo "================================================================================"
echo ""
echo "Showing available commands..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    echo ""
    exit 1
fi

# Check if src directory exists
if [ ! -f "src/youtube_automation_cli.py" ]; then
    echo "ERROR: Cannot find youtube_automation_cli.py"
    echo "Please make sure you're running this from the project root directory"
    echo ""
    exit 1
fi

# Show help information
python3 src/youtube_automation_cli.py --help

echo ""
echo "================================================================================"
echo ""
echo "To run automation, use commands like:"
echo "  python3 src/youtube_automation_cli.py --action like --file likes.txt"
echo "  python3 src/youtube_automation_cli.py --action comment --file comments.txt --video VIDEO_ID"
echo "  python3 src/youtube_automation_cli.py --action subscribe --file channels.txt"
echo ""
echo "For more information, see docs/USER_GUIDE.md"
echo ""
echo "================================================================================"
echo ""
read -p "Press Enter to continue..."
