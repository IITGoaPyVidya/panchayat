#!/bin/bash
# Start both backend and frontend in Railway (single service)

# Create necessary directories
mkdir -p data/uploads data/vector_store

# Start backend on port 8000
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend on the PORT provided by Railway (Streamlit will be the public-facing service)
streamlit run frontend/app.py --server.port ${PORT:-8501} --server.address 0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false --server.headless=true &
FRONTEND_PID=$!

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGTERM SIGINT

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
