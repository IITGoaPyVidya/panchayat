# Run Frontend Server Script
# This script activates the virtual environment and starts the Streamlit frontend

# Navigate to the project directory
Set-Location $PSScriptRoot

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Start the frontend server
streamlit run frontend/app.py --server.port 8501
