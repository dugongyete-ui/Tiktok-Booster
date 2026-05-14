#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}     TikTok Booster - Auto Installer        ${NC}"
echo -e "${BLUE}============================================${NC}"

OS="$(uname -s)"

# ── Detect package manager ────────────────────────────────────────────────────
if command -v apt-get &>/dev/null; then
    PKG_MANAGER="apt"
elif command -v dnf &>/dev/null; then
    PKG_MANAGER="dnf"
elif command -v pacman &>/dev/null; then
    PKG_MANAGER="pacman"
elif command -v brew &>/dev/null; then
    PKG_MANAGER="brew"
else
    PKG_MANAGER="unknown"
fi

echo -e "\n${YELLOW}[1/5] Checking Python version...${NC}"
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo -e "${GREEN}  Python $PY_VERSION found.${NC}"
    PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
    PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
    if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 12 ]; }; then
        echo -e "${RED}  ERROR: Python 3.12+ is required (you have $PY_VERSION).${NC}"
        echo -e "${YELLOW}  Please install Python 3.12 from https://www.python.org/downloads/${NC}"
        exit 1
    fi
else
    echo -e "${RED}  Python3 not found. Please install Python 3.12+.${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[2/5] Installing system dependencies (Tesseract, Chromium, Xvfb)...${NC}"

if [ "$OS" = "Linux" ]; then
    if [ "$PKG_MANAGER" = "apt" ]; then
        echo -e "${BLUE}  Using apt package manager...${NC}"
        sudo apt-get update -qq
        sudo apt-get install -y \
            tesseract-ocr \
            chromium-browser \
            chromium-chromedriver \
            xvfb \
            xdotool \
            libxi6 \
            libxtst6 \
            libxrender1 \
            libxext6 \
            libx11-6 \
            scrot \
            libgl1 \
            libglu1-mesa \
            2>/dev/null || \
        sudo apt-get install -y \
            tesseract-ocr \
            chromium \
            chromedriver \
            xvfb \
            xdotool \
            libxi6 \
            libxtst6 \
            2>/dev/null || true
    elif [ "$PKG_MANAGER" = "dnf" ]; then
        echo -e "${BLUE}  Using dnf package manager...${NC}"
        sudo dnf install -y \
            tesseract \
            chromium \
            xorg-x11-server-Xvfb \
            xdotool \
            scrot \
            mesa-libGL \
            2>/dev/null || true
    elif [ "$PKG_MANAGER" = "pacman" ]; then
        echo -e "${BLUE}  Using pacman package manager...${NC}"
        sudo pacman -S --noconfirm \
            tesseract \
            chromium \
            xorg-server-xvfb \
            xdotool \
            scrot \
            mesa \
            2>/dev/null || true
    else
        echo -e "${YELLOW}  Unknown package manager. Skipping system deps — install manually:${NC}"
        echo -e "  tesseract-ocr, chromium, chromedriver, xvfb, xdotool, scrot, libGL"
    fi
elif [ "$OS" = "Darwin" ]; then
    if [ "$PKG_MANAGER" = "brew" ]; then
        echo -e "${BLUE}  Using Homebrew...${NC}"
        brew install tesseract chromium 2>/dev/null || true
    else
        echo -e "${YELLOW}  Homebrew not found. Install from https://brew.sh/ then re-run this script.${NC}"
    fi
else
    echo -e "${YELLOW}  Unsupported OS: $OS — skipping system dependencies.${NC}"
fi

echo -e "${GREEN}  System dependencies done.${NC}"

echo -e "\n${YELLOW}[3/5] Upgrading pip & installing Python packages...${NC}"

python3 -m pip install --upgrade pip --quiet

# Clean up duplicates in requirements.txt then install unique packages
UNIQUE_REQS=$(sort -u requirements.txt | grep -v '^#' | grep -v '^$')

echo "$UNIQUE_REQS" | while IFS= read -r pkg; do
    echo -e "  ${BLUE}Installing:${NC} $pkg"
    python3 -m pip install "$pkg" --quiet 2>/dev/null || \
    python3 -m pip install "$(echo "$pkg" | sed 's/~=.*//' | sed 's/==.*//' | sed 's/>=//')" --quiet 2>/dev/null || \
    echo -e "  ${YELLOW}  Warning: Could not install $pkg (may already exist or have conflicts)${NC}"
done

echo -e "${GREEN}  Python packages installed.${NC}"

echo -e "\n${YELLOW}[4/5] Creating required directories...${NC}"
mkdir -p Captcha
echo -e "${GREEN}  Directories ready.${NC}"

echo -e "\n${YELLOW}[5/5] Verifying installation...${NC}"
FAILED=0

python3 -c "import selenium" 2>/dev/null && echo -e "  ${GREEN}✓ selenium${NC}" || { echo -e "  ${RED}✗ selenium${NC}"; FAILED=1; }
python3 -c "import cv2" 2>/dev/null && echo -e "  ${GREEN}✓ opencv-python${NC}" || { echo -e "  ${RED}✗ opencv-python${NC}"; FAILED=1; }
python3 -c "import pytesseract" 2>/dev/null && echo -e "  ${GREEN}✓ pytesseract${NC}" || { echo -e "  ${RED}✗ pytesseract${NC}"; FAILED=1; }
python3 -c "import PIL" 2>/dev/null && echo -e "  ${GREEN}✓ pillow${NC}" || { echo -e "  ${RED}✗ pillow${NC}"; FAILED=1; }
python3 -c "import requests" 2>/dev/null && echo -e "  ${GREEN}✓ requests${NC}" || { echo -e "  ${RED}✗ requests${NC}"; FAILED=1; }
python3 -c "import colorama" 2>/dev/null && echo -e "  ${GREEN}✓ colorama${NC}" || { echo -e "  ${RED}✗ colorama${NC}"; FAILED=1; }
python3 -c "import undetected_chromedriver" 2>/dev/null && echo -e "  ${GREEN}✓ undetected-chromedriver${NC}" || { echo -e "  ${RED}✗ undetected-chromedriver${NC}"; FAILED=1; }
python3 -c "import selenium_stealth" 2>/dev/null && echo -e "  ${GREEN}✓ selenium-stealth${NC}" || { echo -e "  ${RED}✗ selenium-stealth${NC}"; FAILED=1; }
python3 -c "from pyvirtualdisplay import Display" 2>/dev/null && echo -e "  ${GREEN}✓ pyvirtualdisplay${NC}" || { echo -e "  ${RED}✗ pyvirtualdisplay${NC}"; FAILED=1; }
python3 -c "import fake_useragent" 2>/dev/null && echo -e "  ${GREEN}✓ fake-useragent${NC}" || { echo -e "  ${RED}✗ fake-useragent${NC}"; FAILED=1; }

command -v tesseract &>/dev/null && echo -e "  ${GREEN}✓ tesseract (system)${NC}" || echo -e "  ${YELLOW}  tesseract not in PATH (may be in nix store or /usr/bin)${NC}"

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  All dependencies installed successfully!  ${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo -e "\n${BLUE}Run the program with:${NC}"
    echo -e "  ${YELLOW}python3 main.py${NC}"
else
    echo -e "${YELLOW}============================================${NC}"
    echo -e "${YELLOW}  Installation completed with some warnings.${NC}"
    echo -e "${YELLOW}  Some packages above failed to install.    ${NC}"
    echo -e "${YELLOW}============================================${NC}"
    echo -e "\n${BLUE}Try running manually:${NC}"
    echo -e "  ${YELLOW}python3 -m pip install -r requirements.txt${NC}"
fi
