# Run Backend Server Script
# This script activates the virtual environment and starts the FastAPI backend

# Navigate to the project directory
Set-Location $PSScriptRoot

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Start the backend server
uvicorn backend.main:app --reload --port 8000
