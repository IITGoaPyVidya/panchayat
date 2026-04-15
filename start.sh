#!/bin/bash
# Start both backend and frontend in Railway
uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} &
BACKEND_PID=$!
streamlit run frontend/app.py --server.port ${STREAMLIT_PORT:-8501} --server.address 0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false &
FRONTEND_PID=$!

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
