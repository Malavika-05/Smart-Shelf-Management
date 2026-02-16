#!/bin/bash

# Start script for Smart Shelf Management Backend

echo "Starting Smart Shelf Management Backend API..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if model file exists
if [ ! -f "models/best.pt" ]; then
    echo "WARNING: Model file not found at models/best.pt"
    echo "Please ensure the YOLO model file is in the models directory"
fi

# Start the server
echo ""
echo "Starting FastAPI server on http://localhost:8000"
echo "API documentation available at http://localhost:8000/docs"
echo ""
uvicorn app:app --reload --host 0.0.0.0 --port 8000
