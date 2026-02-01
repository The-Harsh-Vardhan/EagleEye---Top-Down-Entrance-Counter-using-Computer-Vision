# EagleEye Installation Guide

Comprehensive installation instructions for all platforms, including troubleshooting.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Installation](#quick-installation)
- [Platform-Specific Instructions](#platform-specific-instructions)
  - [Windows](#windows)
  - [Linux (Ubuntu/Debian)](#linux-ubuntudebian)
  - [macOS](#macos)
- [GPU Acceleration (CUDA)](#gpu-acceleration-cuda)
- [Development Installation](#development-installation)
- [Hardware Setup](#hardware-setup)
- [Troubleshooting](#troubleshooting)
- [Verification](#verification)

---

## System Requirements

### Minimum Requirements

- **Python**: 3.8 or higher (3.10+ recommended)
- **RAM**: 4 GB
- **Disk Space**: 500 MB for dependencies + models
- **CPU**: Any modern processor (Intel i3/AMD Ryzen 3 or better)

### Recommended Requirements

- **Python**: 3.10 or 3.11
- **RAM**: 8 GB or more
- **CPU**: Intel i5/AMD Ryzen 5 or better
- **GPU**: NVIDIA GPU with CUDA support (for real-time performance)
  - GTX 1650 or better
  - 4GB+ VRAM
  - CUDA 11.8 or 12.x

### Supported Platforms

- ✅ Windows 10/11
- ✅ Ubuntu 20.04/22.04
- ✅ Debian 11/12
- ✅ macOS 11+ (Big Sur and later)
- ✅ Raspberry Pi 4 (with limitations)

---

## Quick Installation

For most users on Windows/Linux/macOS with Python already installed:

```bash
# 1. Clone repository
git clone https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision.git
cd EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Run
python main.py --source 0
```

If this works, you're done! If not, see platform-specific instructions below.

---

## Platform-Specific Instructions

### Windows

#### Prerequisites

1. **Install Python 3.10+**
   - Download from [python.org](https://www.python.org/downloads/)
   - ⚠️ **Important**: Check "Add Python to PATH" during installation
   - Verify: Open PowerShell and run `python --version`

2. **Install Microsoft Visual C++ Redistributable** (if not already installed)
   - Download from [Microsoft](https://aka.ms/vs/17/release/vc_redist.x64.exe)
   - Required for OpenCV

#### Installation Steps

```powershell
# Open PowerShell (not CMD)

# 1. Navigate to your projects folder
cd "C:\My Drive\Projects"

# 2. Clone repository
git clone https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision.git
cd EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision

# 3. Create virtual environment
python -m venv .venv

# 4. Activate virtual environment
.venv\Scripts\Activate.ps1

# If you get "execution policy" error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.venv\Scripts\Activate.ps1

# 5. Upgrade pip
python -m pip install --upgrade pip

# 6. Install dependencies
pip install -r requirements.txt

# 7. Test installation
python main.py --source 0
```

#### Windows Troubleshooting

**Issue: "python is not recognized"**
```powershell
# Add Python to PATH manually
# 1. Find Python installation: C:\Users\YourName\AppData\Local\Programs\Python\Python310
# 2. Add to PATH in Environment Variables
# 3. Restart PowerShell
```

**Issue: "Activate.ps1 cannot be loaded"**
```powershell
# Use alternative activation
.venv\Scripts\activate.bat
```

**Issue: OpenCV import error**
```powershell
pip uninstall opencv-python opencv-python-headless
pip install opencv-python
```

---

### Linux (Ubuntu/Debian)

#### Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+ (if not installed)
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install system dependencies for OpenCV
sudo apt install -y \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

# Install Git (if not installed)
sudo apt install git -y
```

#### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision.git
cd EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Test installation
python main.py --source 0
```

#### Linux Troubleshooting

**Issue: "libGL.so.1: cannot open shared object file"**
```bash
sudo apt install libgl1-mesa-glx -y
```

**Issue: Webcam permission denied**
```bash
# Add user to video group
sudo usermod -aG video $USER
# Log out and log back in
```

**Issue: "No module named 'cv2'"**
```bash
pip uninstall opencv-python
sudo apt install python3-opencv -y
# OR
pip install opencv-python --no-cache-dir
```

---

### macOS

#### Prerequisites

1. **Install Homebrew** (if not installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python 3.10+**
   ```bash
   brew install python@3.10
   ```

3. **Install system dependencies**
   ```bash
   brew install opencv
   ```

#### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision.git
cd EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Test installation
python main.py --source 0
```

#### macOS Troubleshooting

**Issue: Camera permission denied**
```
Go to System Preferences > Security & Privacy > Privacy > Camera
Enable camera access for Terminal or your IDE
```

**Issue: "zsh: command not found: python"**
```bash
# Use python3 instead
alias python=python3
```

**Issue: SSL certificate error during pip install**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## GPU Acceleration (CUDA)

For significantly faster inference (3-5x speedup), install CUDA support:

### Windows CUDA Installation

1. **Check GPU compatibility**
   ```powershell
   nvidia-smi
   ```
   Should show NVIDIA GPU info. If not, CUDA won't work.

2. **Install NVIDIA Driver** (latest)
   - Download from [NVIDIA](https://www.nvidia.com/Download/index.aspx)

3. **Install CUDA Toolkit 11.8**
   - Download from [NVIDIA CUDA](https://developer.nvidia.com/cuda-11-8-0-download-archive)
   - Follow installation wizard

4. **Install cuDNN**
   - Download from [NVIDIA cuDNN](https://developer.nvidia.com/cudnn) (requires account)
   - Extract and copy files to CUDA installation directory

5. **Install PyTorch with CUDA**
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

6. **Verify CUDA**
   ```python
   python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
   ```

### Linux CUDA Installation

```bash
# 1. Install NVIDIA driver
sudo ubuntu-drivers autoinstall
sudo reboot

# 2. Install CUDA toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2204-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2204-11-8-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt update
sudo apt install cuda-11-8 -y

# 3. Add to PATH (add to ~/.bashrc)
echo 'export PATH=/usr/local/cuda-11.8/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# 4. Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 5. Verify
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

---

## Development Installation

For contributing or development:

```bash
# Install with development dependencies
pip install -r requirements.txt

# Install development tools
pip install \
    pytest \
    black \
    flake8 \
    mypy \
    ipython

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

---

## Hardware Setup

### Camera Mounting

1. **Position**: Mount camera directly above entrance (top-down view)
2. **Height**: 2.5-3.5 meters recommended
3. **Angle**: Perpendicular to floor (90° downward)
4. **Coverage**: Ensure counting line area is clearly visible

### ESP32-CAM Setup

For using ESP32-CAM as video source:

1. **Flash ESP32-CAM** with CameraWebServer sketch
2. **Configure WiFi** credentials in sketch
3. **Note the IP address** (shown in Serial Monitor)
4. **Use MJPEG stream**:
   ```bash
   python main.py --source http://192.168.1.100:81/stream
   ```

### IP Camera Setup

For RTSP/MJPEG IP cameras:

```bash
# RTSP
python main.py --source rtsp://username:password@192.168.1.100:554/stream

# MJPEG
python main.py --source http://192.168.1.100/mjpeg
```

---

## Troubleshooting

### Installation Issues

#### "No module named 'ultralytics'"

```bash
pip install ultralytics --upgrade
```

#### "Could not find a version that satisfies the requirement"

```bash
# Update pip
pip install --upgrade pip setuptools wheel

# Try again
pip install -r requirements.txt
```

#### "ERROR: Failed building wheel for ..."

```bash
# Install build tools
# Windows:
# Install Visual Studio Build Tools from https://visualstudio.microsoft.com/downloads/

# Linux:
sudo apt install build-essential python3-dev -y

# macOS:
xcode-select --install
```

### Runtime Issues

#### Low FPS

1. Use smaller model: `yolov8n.pt`
2. Reduce resolution: `--processing-width 640`
3. Enable GPU acceleration
4. Close other applications

#### High CPU usage

```python
# In config.py, add frame skipping
FRAME_SKIP = 2  # Process every 2nd frame
```

#### Memory errors

```bash
# Reduce model size
# config.py: YOLO_MODEL = 'yolov8n.pt'

# Or limit detection area
# Crop frame before detection
```

### Database Issues

#### "Database is locked"

```bash
# Close all EagleEye instances
# If persists:
rm eagle_eye.db
```

#### "SQL syntax error"

```bash
# Backup and recreate database
mv eagle_eye.db eagle_eye.db.backup
python main.py --reset-db --source 0
```

---

## Verification

After installation, verify everything works:

### 1. Test Installation

```bash
python -c "import cv2, ultralytics, supervision; print('All imports OK')"
```

### 2. Check Python Version

```bash
python --version
# Should show 3.8 or higher
```

### 3. Test Webcam

```bash
python main.py --source 0
# Should open webcam and show detections
```

### 4. Test Model Download

```bash
# Should automatically download yolov8n.pt (~6MB)
python main.py --source 0
# Look for "Downloading yolov8n.pt..." message
```

### 5. Check Database

```bash
# After running for a few seconds, check database
sqlite3 eagle_eye.db "SELECT COUNT(*) FROM crossing_events;"
# Should show event count
```

---

## Getting Help

If you're still having issues:

1. **Check [GitHub Issues](https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision/issues)** for similar problems
2. **Read [API Reference](API_REFERENCE.md)** for usage details
3. **Open a new issue** with:
   - Your OS and Python version
   - Full error message
   - Steps to reproduce
   - Output of `pip list`

---

## Next Steps

After successful installation:

- Read the [README](README.md) for usage examples
- Review [Configuration](README.md#configuration) options
- Check [API Reference](API_REFERENCE.md) for advanced usage
- See [CONTRIBUTING](CONTRIBUTING.md) to contribute

---

**Installation successful?** Star the repo ⭐ and start counting! 🦅


