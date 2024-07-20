#!/bin/bash
export LD_LIBRARY_PATH=:./voice_service_env/lib/python3.11/site-packages/nvidia/cudnn/lib/
# Exit immediately if a command exits with a non-zero status
set -e

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Define the path to the virtual environment
VENV_PATH="./voice_service_env"

# Check if the virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}Error: Virtual environment not found at $VENV_PATH${NC}"
    echo "Please ensure you have set up the voice_service_env correctly."
    exit 1
fi

# Activate the virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate virtual environment.${NC}"
    exit 1
fi

# Set LD_LIBRARY_PATH
CUDA_LIB_PATH="$VENV_PATH/lib/python3.11/site-packages/nvidia"
export LD_LIBRARY_PATH="$CUDA_LIB_PATH:$LD_LIBRARY_PATH"

echo "LD_LIBRARY_PATH set to: $LD_LIBRARY_PATH"

# Run the Python test script
echo -e "${GREEN}Running OpenVoice test script...${NC}"
python test_openvoice.py

# Deactivate the virtual environment
deactivate

echo -e "${GREEN}Test complete. Virtual environment deactivated.${NC}"
