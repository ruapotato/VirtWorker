#!/bin/bash

# Function for logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}


# Add parent directory to PYTHONPATH for virtworker module
export PYTHONPATH=$PYTHONPATH:$(dirname $(pwd))

# Start simulation service using virtual environment
source ../venv/bin/activate


python main.py
APP_PID=$!


# Clean up
log "Cleaning up..."
wait $APP_PID 2>/dev/null

deactivate
log "All done!"
