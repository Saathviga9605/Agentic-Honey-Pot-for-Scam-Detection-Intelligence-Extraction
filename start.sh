#!/bin/bash
# Startup script for Agentic Honeypot System

echo "============================================================"
echo "  Agentic Honeypot for Scam Detection System"
echo "============================================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    exit 1
fi

echo "[1/3] Checking Python installation..."
python3 --version
echo ""

# Install dependencies
echo "[2/3] Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo ""

# Run the application
echo "[3/3] Starting the application..."
echo ""
echo "API will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""
python3 app.py
