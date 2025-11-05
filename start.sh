#!/bin/bash

echo "===================================="
echo "FreshConnect - Starting Application"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file and add your GEMINI_API_KEY"
    echo ""
    echo "Copy .env.example to .env and edit it:"
    echo "  cp .env.example .env"
    echo ""
    exit 1
fi

# Check if database exists
if [ ! -f "marketplace.db" ]; then
    echo "Database not found. Initializing..."
    python seed_data.py
    echo ""
fi

# Start the application
echo "Starting FreshConnect..."
echo ""
echo "Open your browser at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "===================================="
echo ""
python run.py
