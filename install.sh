#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}     TikTok Booster - Auto Installer        ${NC}"
echo -e "${BLUE}============================================${NC}"

OS="$(uname -s)"

# ── Detect correct Python ─────────────────────────────────────────────────────
detect_python() {
    for candidate in \
        "$(pwd)/.pythonlibs/bin/python3" \
        "$HOME/.pythonlibs/bin/python3" \
        "python3" \
        "python"; do
        if [ -x "$candidate" ] || command -v "$candidate" &>/dev/null; then
            if "$candidate" -c "import sys" &>/dev/null 2>&1; then
                echo "$candidate"
                return 0
            fi
        fi
    done
    echo "python3"
}

# Determine pip flags: on NixOS/Replit use --break-system-packages
detect_pip_flags() {
    local py="$1"
    local test_out
    test_out=$("$py" -m pip install --dry-run pip 2>&1 || true)
    if echo "$test_out" | grep -q "externally-managed\|EXTERNALLY-MANAGED"; then
        echo "--break-system-packages"
    else
        echo ""
    fi
}

PYTHON=$(detect_python)
PIP_FLAGS=$(detect_pip_flags "$PYTHON")

echo -e "${CYAN}  Python: $PYTHON${NC}"
[ -n "$PIP_FLAGS" ] && echo -e "${CYAN}  Pip flags: $PIP_FLAGS${NC}"

# ── Step 1: Python version ────────────────────────────────────────────────────
echo -e "\n${YELLOW}[1/4] Checking Python version...${NC}"
PY_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$("$PYTHON" -c "import sys; print(sys.version_info.major)")
PY_MINOR=$("$PYTHON" -c "import sys; print(sys.version_info.minor)")
echo -e "  ${GREEN}Python $PY_VERSION found.${NC}"
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 12 ]; }; then
    echo -e "  ${RED}ERROR: Python 3.12+ required. You have $PY_VERSION.${NC}"
    exit 1
fi

# ── Step 2: System dependencies ───────────────────────────────────────────────
echo -e "\n${YELLOW}[2/4] Checking system dependencies...${NC}"

check_system_dep() {
    local name="$1" cmd="$2"
    if command -v "$cmd" &>/dev/null; then
        echo -e "  ${GREEN}✓ $name: $(command -v $cmd)${NC}"; return 0
    fi
    local nixpath
    nixpath=$(ls /nix/store 2>/dev/null | grep "^[^-]*-${name}" | head -1)
    if [ -n "$nixpath" ] && [ -x "/nix/store/$nixpath/bin/$cmd" ]; then
        echo -e "  ${GREEN}✓ $name (nix store)${NC}"; return 0
    fi
    echo -e "  ${YELLOW}⚠ $name not found${NC}"; return 1
}

MISSING_SYS=0
check_system_dep "tesseract" "tesseract"        || MISSING_SYS=1
check_system_dep "chromium"  "chromium"         || check_system_dep "chromium" "chromium-browser" || MISSING_SYS=1
check_system_dep "Xvfb"      "Xvfb"             || MISSING_SYS=1

if [ $MISSING_SYS -eq 1 ]; then
    echo ""
    if [ -n "$REPL_ID" ] || [ -d "/nix/store" ]; then
        echo -e "  ${CYAN}Replit detected: system deps are managed via replit.nix.${NC}"
    elif [ "$OS" = "Linux" ]; then
        command -v apt-get &>/dev/null && \
            echo -e "  ${YELLOW}Run: sudo apt-get install -y tesseract-ocr chromium-browser xvfb${NC}"
        command -v dnf &>/dev/null && \
            echo -e "  ${YELLOW}Run: sudo dnf install -y tesseract chromium xorg-x11-server-Xvfb${NC}"
        command -v pacman &>/dev/null && \
            echo -e "  ${YELLOW}Run: sudo pacman -S --noconfirm tesseract chromium xorg-server-xvfb${NC}"
    elif [ "$OS" = "Darwin" ]; then
        echo -e "  ${YELLOW}Run: brew install tesseract chromium${NC}"
    fi
fi

# ── Step 3: Python packages ───────────────────────────────────────────────────
echo -e "\n${YELLOW}[3/4] Installing Python packages...${NC}"

# Upgrade pip quietly
"$PYTHON" -m pip install --upgrade pip -q $PIP_FLAGS 2>/dev/null || true

# Map: "install-name~=version" => "import_name"
declare -A PKG_IMPORT=(
    ["selenium"]="selenium"
    ["pytesseract"]="pytesseract"
    ["pillow"]="PIL"
    ["fake_headers"]="fake_headers"
    ["colorama"]="colorama"
    ["discordwebhook"]="discordwebhook"
    ["fake_useragent"]="fake_useragent"
    ["tqdm"]="tqdm"
    ["requests"]="requests"
    ["bs4"]="bs4"
    ["beautifulsoup4"]="bs4"
    ["uuid"]="uuid"
    ["pyperclip"]="pyperclip"
    ["halo"]="halo"
    ["websocket-client"]="websocket"
    ["opencv-python"]="cv2"
    ["undetected-chromedriver"]="undetected_chromedriver"
    ["selenium-stealth"]="selenium_stealth"
    ["pyvirtualdisplay"]="pyvirtualdisplay"
    ["pyautogui"]="pyautogui"
    ["python-xlib"]="Xlib"
    ["setuptools"]="setuptools"
)

PACKAGES=(
    "selenium~=4.23.1"
    "pytesseract~=0.3.13"
    "pillow~=10.4.0"
    "fake_headers"
    "colorama~=0.4.6"
    "discordwebhook~=1.0.3"
    "fake_useragent"
    "tqdm~=4.66.5"
    "requests~=2.32.3"
    "beautifulsoup4~=4.12.3"
    "pyperclip"
    "halo"
    "websocket-client"
    "opencv-python"
    "undetected-chromedriver"
    "selenium-stealth"
    "pyvirtualdisplay"
    "pyautogui"
    "python-xlib"
    "setuptools"
)

patch_uc_distutils() {
    local uc_patcher
    uc_patcher=$("$PYTHON" -c "
import importlib.util, pathlib
spec = importlib.util.find_spec('undetected_chromedriver')
if spec: print(pathlib.Path(spec.origin).parent / 'patcher.py')
" 2>/dev/null)
    [ -z "$uc_patcher" ] && return

    # Only patch if the bare (unguarded) import still exists — skip if already patched
    if grep -qP "^from distutils\.version import LooseVersion" "$uc_patcher" 2>/dev/null; then
        "$PYTHON" - "$uc_patcher" <<'PYEOF'
import sys, pathlib, re
p = pathlib.Path(sys.argv[1])
src = p.read_text()
bare = "from distutils.version import LooseVersion"
patched_block = (
    "try:\n"
    "    from distutils.version import LooseVersion\n"
    "except ImportError:\n"
    "    from packaging.version import Version as _V\n"
    "    class LooseVersion:\n"
    "        def __init__(self, v): self.version = str(v); self._v = _V(str(v))\n"
    "        def __lt__(self, o): return self._v < _V(str(o.version if hasattr(o, 'version') else o))\n"
    "        def __le__(self, o): return self._v <= _V(str(o.version if hasattr(o, 'version') else o))\n"
    "        def __gt__(self, o): return self._v > _V(str(o.version if hasattr(o, 'version') else o))\n"
    "        def __ge__(self, o): return self._v >= _V(str(o.version if hasattr(o, 'version') else o))\n"
    "        def __eq__(self, o): return self._v == _V(str(o.version if hasattr(o, 'version') else o))"
)
# Replace only the bare top-level import line
new_src = re.sub(r'^from distutils\.version import LooseVersion\s*$',
                 patched_block, src, count=1, flags=re.MULTILINE)
if new_src != src:
    p.write_text(new_src)
    print("patched")
else:
    print("already patched")
PYEOF
    else
        echo "already patched"
    fi
}

FAILED_PKGS=()
for pkg in "${PACKAGES[@]}"; do
    pkg_name=$(echo "$pkg" | sed 's/[~>=!].*//')
    import_mod="${PKG_IMPORT[$pkg_name]:-}"
    printf "  %-36s" "$pkg_name..."

    # If already importable, skip install
    if [ -n "$import_mod" ] && "$PYTHON" -c "import $import_mod" 2>/dev/null; then
        echo -e "${GREEN}already installed${NC}"
        continue
    fi

    # Try install with version pin
    if "$PYTHON" -m pip install "$pkg" -q $PIP_FLAGS 2>/dev/null; then
        echo -e "${GREEN}OK${NC}"
    elif "$PYTHON" -m pip install "$pkg_name" -q $PIP_FLAGS 2>/dev/null; then
        echo -e "${YELLOW}OK (latest)${NC}"
    else
        echo -e "${RED}FAILED${NC}"
        FAILED_PKGS+=("$pkg_name")
    fi
done

# Patch undetected-chromedriver distutils compat (Python 3.12+)
printf "  %-36s" "patching undetected-chromedriver..."
patch_uc_distutils
echo -e "${GREEN}done${NC}"

# ── Step 4: Verify ────────────────────────────────────────────────────────────
echo -e "\n${YELLOW}[4/4] Verifying installation...${NC}"
mkdir -p Captcha
echo -e "  ${GREEN}✓ Captcha/ directory ready${NC}"

FAIL=0
check_py() {
    local mod="$1" label="$2"
    if "$PYTHON" -c "import $mod" 2>/dev/null; then
        echo -e "  ${GREEN}✓ $label${NC}"
    else
        echo -e "  ${RED}✗ $label${NC}"
        FAIL=1
    fi
}

check_py "selenium"                "selenium"
check_py "cv2"                     "opencv-python"
check_py "pytesseract"             "pytesseract"
check_py "PIL"                     "pillow"
check_py "requests"                "requests"
check_py "colorama"                "colorama"
check_py "undetected_chromedriver" "undetected-chromedriver"
check_py "selenium_stealth"        "selenium-stealth"
check_py "pyvirtualdisplay"        "pyvirtualdisplay"
check_py "fake_useragent"          "fake-useragent"
check_py "bs4"                     "beautifulsoup4"
check_py "tqdm"                    "tqdm"
check_py "halo"                    "halo"

echo ""
if [ ${#FAILED_PKGS[@]} -gt 0 ]; then
    echo -e "${YELLOW}  Could not install:${NC}"
    for p in "${FAILED_PKGS[@]}"; do
        echo -e "    ${RED}- $p${NC}"
    done
    echo -e "\n  Retry: ${YELLOW}$PYTHON -m pip install $PIP_FLAGS ${FAILED_PKGS[*]}${NC}"
fi

echo ""
if [ $FAIL -eq 0 ] && [ ${#FAILED_PKGS[@]} -eq 0 ]; then
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  ✓ All dependencies installed successfully!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo -e "\n${BLUE}Run the program:${NC} ${YELLOW}python3 main.py${NC}"
else
    echo -e "${YELLOW}============================================${NC}"
    echo -e "${YELLOW}  Done — check issues above before running.${NC}"
    echo -e "${YELLOW}============================================${NC}"
    echo -e "\n${BLUE}Fallback:${NC} ${YELLOW}$PYTHON -m pip install $PIP_FLAGS -r requirements.txt${NC}"
fi
