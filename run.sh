#!/bin/bash

# Set LD_LIBRARY_PATH
export LD_LIBRARY_PATH=:./voice_service_env/lib/python3.11/site-packages/nvidia/cudnn/lib/

# Function for logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Clean up old request and output files
log "Cleaning up old files..."
rm -rf tts_requests tts_output
mkdir tts_requests tts_output

# Start LLM service
log "Starting LLM service..."
source voice_service_env/bin/activate
python llm_service.py &
LLM_PID=$!
deactivate
log "LLM service started with PID $LLM_PID"

# Start voice service
log "Starting voice service..."
source voice_service_env/bin/activate
python voice_service/run_voice_service.py &
VOICE_PID=$!
deactivate
log "Voice service started with PID $VOICE_PID"

# Run the main script
log "Running main project..."
source voice_service_env/bin/activate
python main.py
deactivate

# Clean up
log "Cleaning up..."
kill $LLM_PID
kill $VOICE_PID

log "All done!"
