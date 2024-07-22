#!/bin/bash

# Function to check if CUDA is available
check_cuda() {
    if command -v nvcc &> /dev/null; then
        echo "CUDA is available."
        CUDA_VERSION=$(nvcc --version | grep "release" | sed 's/.*release //' | sed 's/,.*//') 
        echo "CUDA version: $CUDA_VERSION"
        return 0
    else
        echo "CUDA is not available. Please ensure CUDA is installed and in your PATH."
        return 1
    fi
}

# Create and set up the main virtual environment
echo "Setting up main virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Check CUDA availability
if check_cuda; then
    # Extract major and minor version
    CUDA_MAJOR_VERSION=$(echo $CUDA_VERSION | cut -d. -f1)
    CUDA_MINOR_VERSION=$(echo $CUDA_VERSION | cut -d. -f2)
    CUDA_VERSION_TAG="${CUDA_MAJOR_VERSION}${CUDA_MINOR_VERSION}"

    # Install PyTorch with CUDA support
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu${CUDA_VERSION_TAG}
else
    # Install CPU-only version of PyTorch
    pip install torch torchvision torchaudio
fi

# Install other required packages
pip install transformers accelerate datasets evaluate scikit-learn \
            requests beautifulsoup4 feedparser pyzmq

# Install specific version of bitsandbytes compatible with the installed CUDA version
if check_cuda; then
    pip install bitsandbytes
else
    pip install bitsandbytes-cpu
fi

deactivate

# Setup for voice service
echo "Setting up environment for voice service..."
python3 -m venv voice_service_env
source voice_service_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Uninstall potentially problematic packages
pip uninstall -y numpy scipy librosa

# Install latest stable versions of NumPy, SciPy, and librosa
pip install numpy scipy librosa

# Install PyTorch and other dependencies
if check_cuda; then
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu${CUDA_VERSION_TAG}
else
    pip install torch torchvision torchaudio
fi

# Install other dependencies
pip install pandas scikit-learn BeautifulSoup4 feedparser dtw pyzmq

# Clone and install OpenVoice
git clone https://github.com/myshell-ai/OpenVoice.git voice_service/openvoice
cd voice_service/openvoice
pip install -r requirements.txt
cd ../..

# Install MeloTTS
pip install git+https://github.com/myshell-ai/MeloTTS.git
python -m unidic download

# Download OpenVoice checkpoints
mkdir -p voice_service/checkpoints_v2
wget https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip
unzip checkpoints_v2_0417.zip -d voice_service/checkpoints_v2
rm checkpoints_v2_0417.zip

# Bug fix. 
pip install numpy==1.24.3 scipy==1.10.1 librosa==0.10.0

deactivate

# Install Ollama
echo "Installing Ollama..."
curl https://ollama.ai/install.sh | sh

# Pull the gemma2:latest model
echo "Pulling gemma2:latest model..."
ollama pull gemma2:latest

echo "Virtual environments have been set up and dependencies installed."
echo "Ollama has been installed and the gemma2:latest model has been pulled."
echo "To activate the voice service environment, run: source voice_service_env/bin/activate"
echo "To start Ollama, run: ollama serve"
