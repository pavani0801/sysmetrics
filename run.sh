#!/bin/bash

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "pip not found. Please install Python and pip."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt not found."
    exit 1
fi

# Check if dependencies need to be installed
if ! pip install -r requirements.txt --dry-run &> /dev/null; then
    echo "Installing missing dependencies..."
    pip install -r requirements.txt
else
    echo "All dependencies already satisfied."
fi

echo "Running run.py..."
python run.py
