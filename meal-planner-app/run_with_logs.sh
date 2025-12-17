#!/bin/bash

# Ensure we are in the script directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Warning: venv directory not found. Trying to run without activation."
fi

# Run the app and pipe output to tee to see it in real-time and save to file
# 2>&1 redirects stderr to stdout so we capture errors too
echo "Starting Meal Planner App with live logs..."
echo "Logs are being saved to application.log"

# Unbuffered output for python to ensure real-time logging
export PYTHONUNBUFFERED=1

python app.py 2>&1 | tee -a application.log
