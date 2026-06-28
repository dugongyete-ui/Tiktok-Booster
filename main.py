import time
import configparser
import subprocess
import os
import sys
import argparse

_parser = argparse.ArgumentParser(add_help=False)
_parser.add_argument('--url', type=str, default='')
_cli_args, _ = _parser.parse_known_args()
_PRESET_URL = _cli_args.url.strip()

# ── distutils shim (Python 3.12 removed distutils; setuptools provides it) ──
try:
    import distutils  # noqa: F401
except ImportError:
    try:
        import setuptools as _st
        sys.modules['distutils'] = _st._distutils
        sys.modules['distutils.version'] = _st._distutils.version
    except Exception:
        pass
# ─────────────────────────────────────────────────────────────────────────────

import cv2
import zipfile
import tempfile
import webbrowser
try:
    from pyvirtualdisplay import Display as VirtualDisplay
    _VDISPLAY_AVAILABLE = True
except ImportError:
    _VDISPLAY_AVAILABLE = False
from Static.Static import Static
from Modules.Usage import ProgramUsage
from Modules.BannersHandler import Handler
from Static.InitialInfo import InitialInfo
from Modules.Session import Session
import platform
try:
    import hashlib
    import requests
    from tqdm import tqdm
    from selenium import webdriver
    from selenium_stealth import stealth
    from selenium.webdriver.common.by import By
    import pytesseract
    from PIL import Image
    from fake_headers import Headers
    import re
    from colorama import Fore, Style
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as ec
    from selenium.common.exceptions import TimeoutException
    from selenium.common.exceptions import NoSuchElementException
    from selenium.common.exceptions import ElementNotInteractableException
    from selenium.common.exceptions import SessionNotCreatedException
    from datetime import datetime, timedelta
    from discordwebhook import Discord
    from Modules.VideoInfo import TikTokVideoInfo
    from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
    from selenium.webdriver.common.alert import Alert
    import uuid
except Exception as e:
    print(e)
    input()

# Configurations
config = configparser.ConfigParser()
config.read('config.cfg')

TYPE = config.get('Settings', 'TYPE')
VIDEO = config.get('Settings', 'VIDEO_URL')
if re.match(r'^https://tiktok\.com/', VIDEO):
    VIDEO = VIDEO.replace('https://tiktok.com/', 'https://www.tiktok.com/')
AMOUNT = config.getint('Settings', 'AMOUNT')
WEBHOOK = config.get('Settings', 'WEBHOOK')
EACH_VIEWS = config.getint('Settings', 'EACH_VIEWS')
MESSAGE = config.get('Settings', 'MESSAGE')

WAITING = f"{Fore.YELLOW}[WAITING] "
SUCCESS = f"{Fore.GREEN}[SUCCESS] "
INFO = f"{Fore.BLUE}[INFO] "
WARNING = f"{Fore.RED}[WARNING] "

SLEEP = 15
SKIP_WEBHOOK_VERIFICATION = config.getboolean('Settings', 'SKIP_WEBHOOK_CONFIGURATION')
AUTO_START = config.getboolean('Settings', 'AUTO_START', fallback=False)

OPERATING_SYSTEM = platform.system()

VERSION = "2.14.3"

def  is_first_run():
    """Check if it's the first run of the program"""
    file_path = os.path.join(tempfile.gettempdir(), 'Ttkbooster.txt')
    if not os.path.isfile(file_path):
        with open(file_path, "w") as file:
            file.write("Don't Worry, this isn't a virus, just a check to see if it's your first time. :)")
        print(f"{INFO}First Time Detected. Welcome! (This won't appear anymore){Style.RESET_ALL}")
        webbrowser.open("https://discord.gg/nAa5PyxubF")

def show_credits():
    """Display program credits"""
    print(f"{INFO}{Fore.BLUE}{ProgramUsage.Translations("credits",0)}{Fore.CYAN}Sneezedip.{Style.RESET_ALL}")
    print(f"{INFO}{Fore.BLUE}{ProgramUsage.Translations("credits",1)}{Fore.GREEN}"
          f"https://discord.gg/nAa5PyxubF{Style.RESET_ALL}")


def parse_cooldown(text):
    """Parse cooldown time from text"""
    minutes = 0
    seconds = 0

    minute_match = re.search(r'(\d+)\s*minute', text)
    if minute_match:
        minutes = int(minute_match.group(1))

    second_match = re.search(r'(\d+)\s*second', text)
    if second_match:
        seconds = int(second_match.group(1))

    return minutes * 60 + seconds

def check_issues():
    major, minor = sys.version_info[:2]
    if (major, minor) < (3, 12):
        os.system("cls") if os.name == 'nt' else os.system("clear")
        print(Fore.RED + Style.BRIGHT + "[ERROR] TikTok Booster requires Python 3.12 or higher!")
        print(Fore.YELLOW + f"         You are using Python {major}.{minor}. Please update it.")
        print(Fore.CYAN + "\n➡ You can update Python from:")
        print(Fore.GREEN + "   - Microsoft Store: Search for 'Python' and update.")
        print(Fore.GREEN + "   - Official Website: https://www.python.org/downloads/")
        sys.exit(1) 

def check_version(current_version):
    """Check if a new version of the program is available"""
    response = requests.get("https://pastebin.com/raw/GG3Rh0SW")
    if response.text.strip() != current_version:
        while True:
            u = input(f"{datetime.now().strftime('%H:%M:%S')} {WARNING}{Fore.WHITE}"
                      f"{ProgramUsage.Translations("updates",0)}{Style.RESET_ALL}").lower()
            if u == "y":
                ProgramUsage.download(INFO,WAITING,SUCCESS,WARNING,"https://drive.usercontent.google.com/download?id=1zzIcdY50OwbgxM3NMINmdmzHI5oEdnJA&export=download&authuser=0&confirm=t&uuid=4cef67ba-b2ca-4965-87ff-24a84dec12ba&at=APvzH3rjUbDr7ciPn_4IxSS73ohB%3A1736186209268", "./")
                sys.exit()
            elif u == "n":
                return

if OPERATING_SYSTEM == "Windows" or OPERATING_SYSTEM == "Darwin":
    if not os.path.exists('Tesseract'):
        print(f'{INFO}{Fore.WHITE}{ProgramUsage.Translations("credits",1)}{Style.RESET_ALL}', end="\r")
        url = 'https://drive.usercontent.google.com/download?id=10X_TEAwUic4v3pt7TT4w3QNRcS1DNq87&export=download&authuser=0&confirm=t&uuid=19bcdcbd-e7ce-4617-8f41-caca15b5ab17&at=APZUnTWgmGxytaTOOxw-o87dMp8z%3A1720311459869'
        extract_to = './'
        ProgramUsage.download(INFO,WAITING,SUCCESS,WARNING,url, extract_to)
elif OPERATING_SYSTEM == "Linux":
    if not os.path.exists("/usr/bin/tesseract") and not os.path.exists("/nix/store") and not subprocess.run(["which", "tesseract"], capture_output=True).returncode == 0:
        print(f'{INFO}{Fore.WHITE}{ProgramUsage.Translations("credits",1)}{Style.RESET_ALL}', end="\r")
        os.system("sudo apt install tesseract-ocr")
else:
    print(f"{WARNING}Unsupported Operating System ({platform.system()})! Exiting...")
    sys.exit()


class TikTokBooster:
    def __init__(self):
        # ublock_path = os.path.abspath("Extensions/ub.crx")
        # if ProgramUsage.is_down():
        #     print(f"{WARNING}https://www.zefoy.com is currently down for maintenance. Please try again later..")
        #     sys.exit()
        self.User_Session = Session(VERSION)
        self.User_Session.send_heartbeat()
        global VIDEO
        self.elements = []

        os.system("cls") if os.name == 'nt' else os.system("clear")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'─' * 50}")
        print(f"  TikTok Booster v{VERSION}")
        print(f"{'─' * 50}{Style.RESET_ALL}\n")

        while True:
            if _PRESET_URL:
                VIDEO = _PRESET_URL
                print(f"{INFO}URL: {Fore.WHITE}{VIDEO}{Style.RESET_ALL}")
            else:
                print(f"{INFO}Tempel link video TikTok yang ingin di-boost:\n"
                      f"  {Fore.LIGHTBLACK_EX}Contoh: https://www.tiktok.com/@username/video/1234567890{Style.RESET_ALL}\n")
                VIDEO = input(f"{Fore.GREEN}➜ {Fore.WHITE}Link Video: {Style.RESET_ALL}").strip()
            if not VIDEO:
                print(f"{WARNING}Link tidak boleh kosong. Coba lagi.{Style.RESET_ALL}")
                continue
            if re.match(r'^https://tiktok\.com/', VIDEO):
                VIDEO = VIDEO.replace('https://tiktok.com/', 'https://www.tiktok.com/')
            VIDEO = VIDEO.split('?')[0].rstrip('/')
            try:
                self.tiktok_info = TikTokVideoInfo(VIDEO)
                print(f"\n{SUCCESS}Link valid! Memproses...{Style.RESET_ALL}\n")
                break
            except ValueError:
                print(f"{WARNING}Link tidak valid. Contoh: https://www.tiktok.com/@username/video/123456{Style.RESET_ALL}")
                if _PRESET_URL:
                    sys.exit(1)
        self.counter = 0
        self.webhook = WEBHOOK
        self.webhook_text = WEBHOOK
        self.each_views = EACH_VIEWS
        try:
            self.message = MESSAGE.format(self.each_views)
        except KeyError:
            self.message = MESSAGE
        if WEBHOOK.strip():  # Só cria se webhook válido
            try:
                self.webhook = Discord(url=WEBHOOK)
                self.webhook.post(content="Tiktok-Booster Started!") # Quick check
                self.is_webhook_valid = True
            except Exception:
                self.is_webhook_valid = False
                # print(f"{WARNING}Webhook inválido, desabilitado{Style.RESET_ALL}")
        else:
            self.is_webhook_valid = False
            # print(f"{INFO}Webhook vazio, desabilitado{Style.RESET_ALL}")
        
        if not SKIP_WEBHOOK_VERIFICATION and self.is_webhook_valid:
            self._menu()
        self.index = 0
        self.video = VIDEO
        self.video_id = VIDEO.split("/")[5] if ProgramUsage.check_video(VIDEO) == "www" else ProgramUsage.get_vmid(VIDEO)
        self.initial_views = self._get_initial_views()

        is_headless = config.getboolean('Settings', 'HEADLESS')

        # ── Virtual display (Xvfb) setup ──────────────────────────────────────
        # Running Chromium in true non-headless mode via Xvfb bypasses most
        # Cloudflare Turnstile bot-detection that rejects headless browsers.
        self._vdisplay = None
        self._xvfb_display = None  # tracks the actual :N display number
        xvfb_bin = "/nix/store/ykck7gdd6szwrb3qnpb5y5fvjlnmzhz0-xorg-server-21.1.18/bin/Xvfb"
        use_virtual_display = (
            OPERATING_SYSTEM == "Linux"
            and (_VDISPLAY_AVAILABLE or os.path.exists(xvfb_bin))
        )
        if use_virtual_display:
            try:
                if _VDISPLAY_AVAILABLE:
                    self._vdisplay = VirtualDisplay(visible=False, size=(1920, 1080))
                    self._vdisplay.start()
                    # pyvirtualdisplay sets DISPLAY env automatically; record it
                    self._xvfb_display = os.environ.get("DISPLAY", ":1")
                    print(f"{INFO}Virtual display started (pyvirtualdisplay) on {self._xvfb_display}{Style.RESET_ALL}")
                else:
                    # Fallback: launch Xvfb manually
                    self._xvfb_proc = subprocess.Popen(
                        [xvfb_bin, ":99", "-screen", "0", "1920x1080x24"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    os.environ["DISPLAY"] = ":99"
                    self._xvfb_display = ":99"
                    time.sleep(1)
                    print(f"{INFO}Virtual display started (Xvfb manual){Style.RESET_ALL}")
                # Override: don't add headless flag — real display is available
                is_headless = False
            except Exception as ex:
                print(f"{WARNING}Virtual display failed ({ex}), falling back to headless{Style.RESET_ALL}")
                use_virtual_display = False
                is_headless = config.getboolean('Settings', 'HEADLESS')
        # ─────────────────────────────────────────────────────────────────────

        # ── Try undetected_chromedriver first (best Cloudflare bypass) ────────
        _uc_driver = None
        try:
            import undetected_chromedriver as uc
            import shutil as _shutil
            uc_options = uc.ChromeOptions()
            uc_safe = [
                "--window-size=1920,1080",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--enable-unsafe-swiftshader",
                "--log-level=3",
                "--disable-notifications",
                "--disable-popup-blocking",
            ]
            for opt in uc_safe:
                uc_options.add_argument(opt)
            if is_headless:
                uc_options.add_argument("--headless=new")
            if OPERATING_SYSTEM == "Linux" and os.path.exists(Static.ChromeBinaryPath):
                uc_options.binary_location = Static.ChromeBinaryPath
            # UC patches the chromedriver binary; nix store is read-only so copy first
            driver_path = None
            if OPERATING_SYSTEM == "Linux" and os.path.exists(Static.ChromeDriverPath):
                _tmp_driver = os.path.join(tempfile.gettempdir(), "chromedriver_uc")
                if not os.path.exists(_tmp_driver):
                    _shutil.copy2(Static.ChromeDriverPath, _tmp_driver)
                    os.chmod(_tmp_driver, 0o755)
                driver_path = _tmp_driver
            _uc_driver = uc.Chrome(
                options=uc_options,
                driver_executable_path=driver_path,
                use_subprocess=False,
                version_main=Static.ChromeMajorVersion,
            )
            self.driver = _uc_driver
            self._use_uc = True
            self._uc_options = uc_options
            self._uc_driver_path = driver_path
            print(f"{INFO}Using undetected_chromedriver (best Cloudflare bypass){Style.RESET_ALL}")
        except Exception as uc_err:
            print(f"{WARNING}undetected_chromedriver failed ({uc_err}), falling back to selenium-stealth{Style.RESET_ALL}")
            self._use_uc = False
            self.options = webdriver.ChromeOptions()
            safe_options = [
                "--window-size=1920,1080",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--enable-unsafe-swiftshader",
                "--log-level=3",
                "--disable-blink-features=AutomationControlled",
                "--exclude-switches=enable-automation",
                "--disable-extensions",
            ]
            for option in safe_options:
                self.options.add_argument(option)
            if is_headless:
                self.options.add_argument("--headless=new")
            else:
                if use_virtual_display and "DISPLAY" not in os.environ:
                    os.environ.setdefault("DISPLAY", self._xvfb_display or ":1")
            if OPERATING_SYSTEM == "Linux" and os.path.exists(Static.ChromeBinaryPath):
                self.options.binary_location = Static.ChromeBinaryPath
            if OPERATING_SYSTEM == "Linux" and os.path.exists(Static.ChromeDriverPath):
                from selenium.webdriver.chrome.service import Service
                service = Service(executable_path=Static.ChromeDriverPath)
                self.driver = webdriver.Chrome(service=service, options=self.options)
            else:
                self.driver = webdriver.Chrome(options=self.options)
            stealth(
                self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
        # ─────────────────────────────────────────────────────────────────────


        self.driver.get('https://zefoy.com/')

        # Wait for Cloudflare to resolve before doing anything else
        self._wait_for_cloudflare(timeout=150)

        if OPERATING_SYSTEM == "Windows":
            pytesseract.pytesseract.tesseract_cmd = r'Tesseract/tesseract.exe'
        elif OPERATING_SYSTEM == "Linux":
            nix_tesseract = subprocess.run(["which", "tesseract"], capture_output=True, text=True).stdout.strip()
            if nix_tesseract:
                pytesseract.pytesseract.tesseract_cmd = nix_tesseract
            else:
                pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
        else:
            print(f"{WARNING}Unsupported Operating System ({platform.system()})! Exiting...")
            sys.exit()
        try:
            WebDriverWait(self.driver, 5).until(ec.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
        except (NoAlertPresentException, TimeoutException):
            pass
        try:
            WebDriverWait(self.driver, SLEEP).until(ec.presence_of_element_located(
                (By.XPATH, '/html/body/div[8]/div[2]/div[2]/div[3]/div[2]/button[1]'))).click()
        except (TimeoutException, NoSuchElementException):
            pass
        
        # try:
        #     self.webhook.post(content="Tiktok-Booster Started!") # Quick check on webhook
        #     self.is_webhook_valid = True    
        # except (TimeoutException):
        #     self.is_webhook_valid = False

        max_captcha_attempts = 3
        attempt = 1
        while attempt <= max_captcha_attempts:
            if self._handle_captcha():
                print("Captcha passed successfully!")
                break
            print(f"Attempt #{attempt} failed, refreshing... ({max_captcha_attempts - attempt + 1} left)")
            self.driver.refresh()
            time.sleep(2)
            attempt += 1
        else:
            print(f"{WARNING}Max captcha attempts ({max_captcha_attempts}) reached. Resetting browser or manual intervention needed.")
            self._reset_browser()
        
        self.driver.save_screenshot('Captcha/debug_page.png')
        print(f"{INFO}Page URL: {self.driver.current_url}{Style.RESET_ALL}")
        print(f"{INFO}Page title: {self.driver.title}{Style.RESET_ALL}")
        self._check_available()
        self._show_typeconfig()
        self._show_menu()
        time.sleep(1)
        self._select_type()

    def remove_modal(self):
        time.sleep(1)
        try:
            # Wait for the modal to appear (optional, adjust timeout if needed)
            WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.CLASS_NAME, "fc-list-container"))
            )
            self.driver.execute_script("""
                            (() => {
                function removeFcMessages() {
                    document.querySelectorAll('.fc-message-root, .fc-dialog-overlay, .fc-monetization-dialog')
                        .forEach(el => el.remove());
                }
                setInterval(removeFcMessages, 500);
            })();
            """)
        except Exception as e:
            pass
    def remove_ads_vignette(self):
        """Remove Google vignette, ads, overlays with multiple fallback strategies."""
        if "#google_vignette" not in self.driver.current_url:
            return
        
        print(f"{WAITING}Ad/vignette detected. Attempting removal...")
        
        # Common dismiss selectors (prioritized)
        dismiss_selectors = [
            (By.XPATH, '//*[@id="dismiss-button"]'),
            (By.XPATH, '//*[@id="dismiss-button"]//div'),
            (By.XPATH, '//button[contains(@class, "close") or contains(@aria-label, "close")]'),
            (By.XPATH, '//div[contains(@class, "close") or @role="button"]//span[text()="×" or text()="✕" or text()="X"]'),
            (By.CSS_SELECTOR, '[data-dismiss="modal"], .close, .dismiss, [aria-label*="close"]'),
            (By.XPATH, '//button[contains(text(), "Close") or contains(text(), "Dismiss")]'),
        ]
        
        original_url = self.driver.current_url
        removed = False
        
        for by, selector in dismiss_selectors:
            try:
                elem = WebDriverWait(self.driver, 3).until(ec.element_to_be_clickable((by, selector)))
                self.driver.execute_script("arguments[0].click();", elem)
                time.sleep(1)
                
                # Verify success
                if "#google_vignette" not in self.driver.current_url or original_url != self.driver.current_url:
                    print(f"{SUCCESS}Ad removed via: {selector}")
                    removed = True
                    break
                    
            except (TimeoutException, NoSuchElementException):
                continue  # Try next selector
        
        # Fallback: JS overlay removal
        if not removed:
            self.driver.execute_script("""
                // Remove common ad overlays
                document.querySelectorAll('[id*="google"], .fc-above-fold-separator, .ad-overlay, iframe[src*="google"], #google_vignette ~ *').forEach(el => {
                    el.style.display = 'none';
                    el.remove();
                });
                // Focus main content
                const mainContent = document.querySelector('main, #main, body > *:nth-child(1)');
                if (mainContent) mainContent.scrollIntoView();
                // Force URL clean
                if (window.location.hash === "#google_vignette") {
                    history.replaceState(null, "", window.location.pathname + window.location.search);
                }
            """)
            print(f"{INFO}JS fallback applied for ad removal.")
        
        if "#google_vignette" in self.driver.current_url:
            print(f"{WARNING}Ad/vignette persists - may need manual intervention.")

    # ─────────────────────── JS DOM HELPERS ───────────────────────────────────

    def _try_click_turnstile(self):
        """
        Try to click the Cloudflare Turnstile checkbox.
        Strategy order:
          1. xdotool — real X11 mouse events (hardest to detect, no tkinter dep)
          2. Selenium ActionChains — coordinate click on body
          3. JS elementFromPoint
        """
        from selenium.webdriver.common.action_chains import ActionChains

        # ── Strategy 1: xdotool (X11 events — most human-like, no tkinter) ───
        try:
            disp = getattr(self, '_xvfb_display', None) or os.environ.get("DISPLAY", ":1")
            xdotool = "/nix/store/k9h3c1q6cvl819cl933wss1nbl58wqcw-xdotool-3.20211022.1/bin/xdotool"
            if not os.path.exists(xdotool):
                xdotool = "xdotool"
            env = dict(os.environ, DISPLAY=disp)
            # Capture current screenshot to detect real checkbox position
            # Fallback: known coords at 1920x1080 — checkbox center ~(577, 452)
            cx, cy = 577, 452
            try:
                import tempfile as _tf, cv2 as _cv2
                _ss = os.path.join(_tf.gettempdir(), "cf_pos_check.png")
                subprocess.run(["scrot", _ss], env=env, timeout=5, capture_output=True)
                _img = _cv2.imread(_ss, _cv2.IMREAD_GRAYSCALE)
                if _img is not None:
                    h, w = _img.shape
                    # checkbox is in top-left quadrant, scan for it
                    roi = _img[int(h*0.3):int(h*0.6), int(w*0.1):int(w*0.6)]
                    _, _thresh = _cv2.threshold(roi, 200, 255, _cv2.THRESH_BINARY)
                    _cnts, _ = _cv2.findContours(_thresh, _cv2.RETR_EXTERNAL, _cv2.CHAIN_APPROX_SIMPLE)
                    _sq = [c for c in _cnts if 200 < _cv2.contourArea(c) < 5000]
                    if _sq:
                        _M = _cv2.moments(_sq[0])
                        if _M["m00"]:
                            rx = int(_M["m10"]/_M["m00"]) + int(w*0.1)
                            ry = int(_M["m01"]/_M["m00"]) + int(h*0.3)
                            cx, cy = rx, ry
                            print(f"{INFO}Turnstile: detected checkbox at ({cx},{cy}){Style.RESET_ALL}")
            except Exception:
                pass
            # Move mouse naturally then click at Turnstile checkbox position
            subprocess.run([xdotool, "mousemove", "--sync", "100", "100"],
                           env=env, timeout=3, capture_output=True)
            time.sleep(0.3)
            subprocess.run([xdotool, "mousemove", "--sync", str(cx), str(cy)],
                           env=env, timeout=3, capture_output=True)
            time.sleep(0.2)
            subprocess.run([xdotool, "click", "1"],
                           env=env, timeout=3, capture_output=True)
            print(f"{INFO}Turnstile: xdotool click at ({cx},{cy}) on {disp}{Style.RESET_ALL}")
            return True
        except Exception as xde:
            print(f"{INFO}xdotool failed: {xde}{Style.RESET_ALL}")

        try:
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            if iframes:
                srcs = [f.get_attribute('src') or '(no src)' for f in iframes]
                print(f"{INFO}Iframes on page ({len(iframes)}): {srcs}{Style.RESET_ALL}")
            else:
                print(f"{INFO}No iframes found on page{Style.RESET_ALL}")

            # Selectors to try inside iframe
            SELECTORS = [
                'input[type="checkbox"]',
                'label',
                '.ctp-checkbox-label',
                '[id*="checkbox"]',
                'div[role="checkbox"]',
                'span.mark',
                'div.mark',
                '#cf-stage input',
                '.checkbox-widget',
                'body',          # last resort: click body of iframe
            ]

            for i, iframe in enumerate(iframes):
                src = iframe.get_attribute('src') or ''
                try:
                    self.driver.switch_to.frame(iframe)
                    time.sleep(0.5)
                    # Try CSS selectors
                    clicked = False
                    for sel in SELECTORS:
                        try:
                            el = self.driver.find_element(By.CSS_SELECTOR, sel)
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block:'center'});", el)
                            time.sleep(0.2)
                            # Use ActionChains for more human-like click
                            ac = ActionChains(self.driver)
                            ac.move_to_element(el).pause(0.1).click().perform()
                            print(f"{INFO}Turnstile: clicked '{sel}' in iframe {i} ({src[:60]}){Style.RESET_ALL}")
                            clicked = True
                            break
                        except Exception:
                            continue
                    if not clicked:
                        # Fallback: click center of iframe via ActionChains (from main content)
                        self.driver.switch_to.default_content()
                        try:
                            rect = self.driver.execute_script(
                                "var r=arguments[0].getBoundingClientRect();"
                                "return {x:r.x,y:r.y,w:r.width,h:r.height};", iframe)
                            cx = int(rect['x'] + rect['w'] / 2)
                            cy = int(rect['y'] + rect['h'] / 2)
                            ac = ActionChains(self.driver)
                            ac.move_by_offset(cx, cy).click().perform()
                            print(f"{INFO}Turnstile: clicked iframe {i} at ({cx},{cy}){Style.RESET_ALL}")
                            clicked = True
                        except Exception as ec2:
                            print(f"{WARNING}ActionChains iframe click failed: {ec2}{Style.RESET_ALL}")
                    else:
                        self.driver.switch_to.default_content()
                    if clicked:
                        return True
                except Exception as ef:
                    print(f"{WARNING}Iframe {i} error: {ef}{Style.RESET_ALL}")
                    try:
                        self.driver.switch_to.default_content()
                    except Exception:
                        pass

            # Fallback A: try clicking the widget in the main document (no iframe)
            try:
                self.driver.switch_to.default_content()
                # Cloudflare Turnstile widget selectors in main doc
                MAIN_DOC_SELECTORS = [
                    'input[type="checkbox"]',
                    '[id*="turnstile"]',
                    '[class*="turnstile"]',
                    '[id*="cf-chl"]',
                    '[class*="cf-"]',
                    'div[role="checkbox"]',
                    'label',
                    '.ctp-checkbox-label',
                ]
                for sel in MAIN_DOC_SELECTORS:
                    try:
                        el = self.driver.find_element(By.CSS_SELECTOR, sel)
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block:'center'});", el)
                        time.sleep(0.2)
                        from selenium.webdriver.common.action_chains import ActionChains
                        ac = ActionChains(self.driver)
                        ac.move_to_element(el).pause(0.1).click().perform()
                        print(f"{INFO}Turnstile: clicked main-doc '{sel}'{Style.RESET_ALL}")
                        break
                    except Exception:
                        continue
            except Exception:
                pass

            # Fallback B: ActionChains absolute coordinate click at Turnstile position
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                # Turnstile checkbox appears at approx (280, 175) in the window
                ac = ActionChains(self.driver)
                ac.move_by_offset(0, 0)  # reset
                ac.perform()
                ac = ActionChains(self.driver)
                ac.move_to_element_with_offset(
                    self.driver.find_element(By.TAG_NAME, 'body'), 280, 175
                ).click().perform()
                print(f"{INFO}Turnstile: ActionChains click at body offset (280, 175){Style.RESET_ALL}")
            except Exception as ex:
                print(f"{INFO}ActionChains offset click: {ex}{Style.RESET_ALL}")

            # Fallback C: JS coordinate click
            try:
                self.driver.execute_script("""
                    var el = document.elementFromPoint(280, 175);
                    if (el) { el.click(); }
                    var el2 = document.elementFromPoint(283, 177);
                    if (el2) { el2.click(); }
                """)
                print(f"{INFO}Turnstile: JS elementFromPoint click at (280, 175){Style.RESET_ALL}")
            except Exception:
                pass

        except Exception as e:
            print(f"{WARNING}Turnstile click error: {e}{Style.RESET_ALL}")
            try:
                self.driver.switch_to.default_content()
            except Exception:
                pass
        return False

    def _wait_for_cloudflare(self, timeout=120):
        """
        Block until Cloudflare challenge is resolved.
        Every 5 seconds, attempt to click the Turnstile checkbox if it is visible.
        """
        print(f"{WAITING}Waiting for Cloudflare to resolve…{Style.RESET_ALL}")
        deadline = time.time() + timeout
        attempt = 0
        while time.time() < deadline:
            try:
                # Dismiss any unexpected alerts (e.g. notification prompts)
                try:
                    alert = self.driver.switch_to.alert
                    alert.dismiss()
                    print(f"{INFO}Dismissed browser alert{Style.RESET_ALL}")
                except Exception:
                    pass
                title = self.driver.title
                url   = self.driver.current_url
                if ("just a moment" not in title.lower()
                        and "challenges.cloudflare.com" not in url):
                    print(f"{INFO}Cloudflare passed ✔  Page: {title}{Style.RESET_ALL}")
                    return True
            except UnexpectedAlertPresentException:
                try:
                    self.driver.switch_to.alert.dismiss()
                except Exception:
                    pass
                time.sleep(1)
                continue
            except Exception as we:
                print(f"{WARNING}Cloudflare check error: {we}{Style.RESET_ALL}")
                time.sleep(2)
                continue
            # Every ~5 s try clicking the Turnstile
            if attempt % 3 == 0:
                self._try_click_turnstile()
            attempt += 1
            time.sleep(2)
        print(f"{WARNING}Cloudflare still blocking after {timeout}s — continuing anyway{Style.RESET_ALL}")
        return False

    def _js_find_button(self, keywords):
        """Return the first <button> whose text contains any of the keywords (JS DOM)."""
        if isinstance(keywords, str):
            keywords = [keywords]
        kws = [k.lower() for k in keywords]
        script = """
        var kws = arguments[0];
        var buttons = document.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            var txt = buttons[i].textContent.trim().toLowerCase();
            for (var j = 0; j < kws.length; j++) {
                if (txt.indexOf(kws[j]) !== -1) return buttons[i];
            }
        }
        return null;
        """
        return self.driver.execute_script(script, kws)

    def _js_click_button(self, keywords, timeout=10):
        """Wait up to `timeout` seconds for a button matching keywords, then JS-click it."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            btn = self._js_find_button(keywords)
            if btn:
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                self.driver.execute_script("arguments[0].click();", btn)
                return True
            time.sleep(1)
        return False

    def _js_find_active_panel(self):
        """Return the currently-visible service panel (has input + button, not hidden)."""
        script = """
        var divs = document.querySelectorAll('div');
        for (var i = 0; i < divs.length; i++) {
            var d = divs[i];
            var st = window.getComputedStyle(d);
            if (st.display === 'none' || st.visibility === 'hidden' || st.opacity === '0') continue;
            if (d.querySelector('input') && d.querySelector('button')) {
                // must not be deeply nested — require it contains a form or direct input
                if (d.querySelector('form') || d.querySelectorAll('input').length > 0) {
                    // skip tiny wrappers: must have reasonable height
                    if (d.getBoundingClientRect().height > 40) return d;
                }
            }
        }
        return null;
        """
        return self.driver.execute_script(script)

    def _js_dump_inputs(self):
        """Debug helper — dump all inputs with their type, visibility, and parent context."""
        return self.driver.execute_script("""
        var result = [];
        document.querySelectorAll('input').forEach(function(inp) {
            var st = window.getComputedStyle(inp);
            var p = inp.parentElement;
            var parents = [];
            while (p && parents.length < 4) {
                parents.push((p.tagName||'').toLowerCase() + (p.className ? '.' + p.className.split(' ')[0] : ''));
                p = p.parentElement;
            }
            result.push({
                type: inp.type || '(no type)',
                display: st.display,
                visibility: st.visibility,
                opacity: st.opacity,
                value: inp.value,
                placeholder: inp.placeholder,
                parents: parents.join(' > ')
            });
        });
        return result;
        """)

    def _js_fill_input(self, value, timeout=10):
        """Clear and fill the first visible URL-like input inside the active Zefoy panel.

        Three-pass strategy:
          Pass 1 — non-captcha, non-hidden inputs (all types except hidden/checkbox/radio).
          Pass 2 — fallback: any visible input including those inside plain forms.
          Pass 3 — last resort: try even partially-hidden inputs (opacity/clip tricks).
        """
        script = """
        var val = arguments[0];

        function isCaptchaForm(el) {
            var p = el.parentElement;
            while (p) {
                if (p.tagName && p.tagName.toLowerCase() === 'form') {
                    if (p.querySelector('img, canvas')) return true;
                    return false;
                }
                p = p.parentElement;
            }
            return false;
        }

        function fillInput(inp) {
            inp.scrollIntoView({block:'center'});
            inp.focus();
            inp.value = val;
            inp.dispatchEvent(new Event('input',  {bubbles: true}));
            inp.dispatchEvent(new Event('change', {bubbles: true}));
            inp.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true}));
            return inp;
        }

        var skipTypes = ['hidden', 'checkbox', 'radio', 'file', 'submit', 'button', 'reset', 'image'];
        var inputs = Array.from(document.querySelectorAll('input'));

        // Pass 1: non-captcha, fully visible
        for (var i = 0; i < inputs.length; i++) {
            var inp = inputs[i];
            if (skipTypes.indexOf((inp.type||'').toLowerCase()) !== -1) continue;
            var st = window.getComputedStyle(inp);
            if (st.display === 'none' || st.visibility === 'hidden') continue;
            if (isCaptchaForm(inp)) continue;
            return fillInput(inp);
        }

        // Pass 2: any visible input (including captcha-form ones)
        for (var i = 0; i < inputs.length; i++) {
            var inp = inputs[i];
            if (skipTypes.indexOf((inp.type||'').toLowerCase()) !== -1) continue;
            var st = window.getComputedStyle(inp);
            if (st.display === 'none' || st.visibility === 'hidden') continue;
            return fillInput(inp);
        }

        // Pass 3: try inputs that might have opacity:0 or are off-screen
        for (var i = 0; i < inputs.length; i++) {
            var inp = inputs[i];
            if (skipTypes.indexOf((inp.type||'').toLowerCase()) !== -1) continue;
            var st = window.getComputedStyle(inp);
            if (st.display === 'none') continue;
            return fillInput(inp);
        }

        return null;
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            el = self.driver.execute_script(script, value)
            if el:
                return True
            time.sleep(1)
        return False

    def _js_get_cooldown_text(self):
        """Scan the page for a cooldown / timer text (mm:ss or words like minute/second)."""
        script = """
        var spans = document.querySelectorAll('span, p, div');
        for (var i = 0; i < spans.length; i++) {
            var txt = spans[i].textContent.trim();
            if (/\\d+:\\d+/.test(txt) ||
                /\\d+\\s*(minute|second|min|sec)/i.test(txt)) {
                return txt;
            }
        }
        return null;
        """
        return self.driver.execute_script(script)

    def _js_scan_available_types(self):
        """Return list of type-names whose service buttons are found in the DOM."""
        keywords_map = {
            'views':     ['video views', 'views'],
            'hearts':    ['hearts',  'likes'],
            'shares':    ['shares'],
            'favorites': ['favorites', 'favourite'],
            'followers': ['followers'],
            'repost':    ['repost'],
        }
        found = []
        for type_key, kws in keywords_map.items():
            btn = self._js_find_button(kws)
            if btn:
                found.append(type_key)
        return found

    def _js_dump_buttons(self):
        """Debug helper — print all visible button texts found on the page."""
        script = """
        var result = [];
        document.querySelectorAll('button').forEach(function(b){
            var txt = b.textContent.trim();
            if (txt) result.push(txt);
        });
        return result;
        """
        return self.driver.execute_script(script)

    # ──────────────────────────────────────────────────────────────────────────

    def _get_initial_views(self):
        """Get initial views based on the type"""
        if TYPE == 'views':
            return ProgramUsage.get_numeric_value(self.tiktok_info.get_video_info(Views=True))
        elif TYPE == 'shares':
            return ProgramUsage.get_numeric_value(self.tiktok_info.get_video_info(Shares=True))
        elif TYPE == 'hearts':
            return ProgramUsage.get_numeric_value(self.tiktok_info.get_video_info(Likes=True))
        elif TYPE == 'favorites':
            return 0

    def _check_available(self):
        self.User_Session.send_heartbeat()
        self.remove_modal()
        self.remove_ads_vignette()
        """Check if the required features are available — uses JS DOM scan."""
        print(f"{INFO}Scanning available service buttons via DOM…{Style.RESET_ALL}")
        # Dump all buttons for debug
        btns = self._js_dump_buttons()
        print(f"{INFO}Buttons found on page: {btns}{Style.RESET_ALL}")
        found_types = self._js_scan_available_types()
        for t in found_types:
            if t not in self.elements:
                self.elements.append(t)
                print(f"{INFO}  ✔ '{t}' available{Style.RESET_ALL}")
        # Fallback: if nothing found via JS, try XPATH briefly
        if not self.elements:
            SHORT = 3
            for type_key, xpath in Static.typeValues.items():
                try:
                    if WebDriverWait(self.driver, SHORT).until(
                            ec.presence_of_element_located((By.XPATH, xpath))).is_enabled():
                        self.elements.append(type_key)
                except Exception:
                    pass
        if not self.elements:
            print(f"{WARNING}No service buttons found — Cloudflare may still be active{Style.RESET_ALL}")
        else:
            print(f"{INFO}Available services: {self.elements}{Style.RESET_ALL}")

    def _find_element_flexible(self, selectors, timeout=SLEEP):
        """Try multiple selectors and return first found element.
        Uses a short per-selector probe, then one full wait on the first that responds."""
        probe = 2
        for by, selector in selectors:
            try:
                el = WebDriverWait(self.driver, probe).until(
                    ec.presence_of_element_located((by, selector)))
                return el
            except (TimeoutException, NoSuchElementException):
                continue
        return None

    def _handle_captcha(self):
        self.User_Session.send_heartbeat()
        self.remove_modal()
        self.remove_ads_vignette()
        print(f"{datetime.now().strftime('%H:%M:%S')} {WAITING}Passing Captcha{Style.RESET_ALL}")
        """Handle the captcha on the page"""

        captcha_img_selectors = [
            (By.XPATH, '/html/body/div[5]/div[2]/form/div/div/img'),
            (By.XPATH, '/html/body/div[4]/div[2]/form/div/div/img'),
            (By.XPATH, '/html/body/div[6]/div[2]/form/div/div/img'),
            (By.CSS_SELECTOR, 'form img'),
            (By.XPATH, '//form//img'),
        ]
        captcha_img = self._find_element_flexible(captcha_img_selectors)
        if captcha_img is None:
            print(f"{WARNING}Captcha image not found, assuming already passed{Style.RESET_ALL}")
            return True

        with open('Captcha/captcha.png', 'wb') as file:
            file.write(captcha_img.screenshot_as_png)
        time.sleep(3)
        
        captcha_text = pytesseract.image_to_string(Image.open('Captcha/captcha.png')).strip()
        if len(captcha_text) <= 0:
            captcha_text = ''

        input_selectors = [
            (By.XPATH, '/html/body/div[5]/div[2]/form/div/div/div/input'),
            (By.XPATH, '/html/body/div[4]/div[2]/form/div/div/div/input'),
            (By.XPATH, '/html/body/div[6]/div[2]/form/div/div/div/input'),
            (By.CSS_SELECTOR, 'form input[type="text"]'),
            (By.XPATH, '//form//input'),
        ]
        input_field = self._find_element_flexible(input_selectors)
        if input_field is None:
            print(f"Captcha input error: field not found")
            return False
        try:
            input_field.clear()
            input_field.send_keys(captcha_text)
            time.sleep(1)
        except Exception as input_err:
            print(f"Captcha input error: {input_err}")
            return False

        print(f"{Fore.CYAN}About to click submit button...{Style.RESET_ALL}")

        # Force-remove any modal overlays that may block the click
        self.driver.execute_script("""
            // Remove all modal backdrops and visible modals blocking the form
            document.querySelectorAll(
                '.modal-backdrop, .fc-dialog-overlay, [id="zbcd"], .modal.show, .modal.fade.show'
            ).forEach(function(el) {
                el.style.display = 'none';
                el.remove();
            });
            // Also restore body scroll which Bootstrap modals disable
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
        """)
        time.sleep(0.5)
        self.remove_modal()
        self.remove_ads_vignette()

        submit_selectors = [
            (By.XPATH, '/html/body/div[5]/div[2]/form/div/div/div/div/button'),
            (By.XPATH, '/html/body/div[4]/div[2]/form/div/div/div/div/button'),
            (By.XPATH, '/html/body/div[6]/div[2]/form/div/div/div/div/button'),
            (By.CSS_SELECTOR, 'form button[type="submit"]'),
            (By.XPATH, '//form//button'),
        ]
        submit_btn = self._find_element_flexible(submit_selectors, timeout=5)

        try:
            if WebDriverWait(self.driver, 3).until(
                ec.presence_of_element_located((By.XPATH, '//*[@id="qewarjh"]/div/div/div[3]/button'))):
                self.driver.refresh()
                return False
        except Exception:
            pass

        if submit_btn is None:
            self.driver.refresh()
            return False
            
        try:
            time.sleep(2)
            # Use JS click to bypass any remaining overlay interception
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit_btn)
            self.driver.execute_script("arguments[0].click();", submit_btn)
            print(f"{Fore.GREEN}✅ Submit clicked successfully, verifying...{Style.RESET_ALL}") 
        except Exception as click_err:
            print(f"{Fore.RED}❌ Click failed: {Fore.WHITE}{click_err}{Style.RESET_ALL}")
            return False
            
        captcha_success = self._is_captcha_passed()
            
        # except Exception as e:
        #     print(f"Error in captcha handling: {e}")
        #     self._reset_browser()
        #     captcha_success = False
        
        print("Captcha Finished?", captcha_success)
        return captcha_success

    def _is_captcha_passed(self):
        self.User_Session.send_heartbeat()
        """Check if captcha was passed successfully"""
        print("Verifying captcha success...")
        self.remove_modal()
        self.remove_ads_vignette()
        time.sleep(5)
        

        fail_selectors = [
            (By.CLASS_NAME, 'btn btn-secondary col-sm'),  # New captcha button
            (By.XPATH, '//*[@id="qewarjh"]/div/div/div[3]/button')
        ]
        for by, selector in fail_selectors:
            try:
                WebDriverWait(self.driver, SLEEP).until(
                    ec.presence_of_element_located((by, selector))
                )
                self.driver.refresh()
                return False
            except Exception:
                continue
        return True

    def _reset_browser(self):
        self.User_Session.send_heartbeat()
        """Closes and restarts the browser, then re-logs in to zefoy."""
        try:
            self.driver.quit()
        except Exception as e:
            print(f"{WARNING}Error while closing the browser: {e}")

        if getattr(self, '_use_uc', False):
            try:
                import undetected_chromedriver as uc
                self.driver = uc.Chrome(
                    options=self._uc_options,
                    driver_executable_path=getattr(self, '_uc_driver_path', None),
                    use_subprocess=False,
                    version_main=138,
                )
                print(f"{INFO}Browser reset via undetected_chromedriver{Style.RESET_ALL}")
            except Exception as e:
                print(f"{WARNING}UC reset failed ({e}), falling back to stealth{Style.RESET_ALL}")
                self._use_uc = False
                self._init_stealth_driver()
        else:
            self._init_stealth_driver()

        self.driver.get('https://zefoy.com/')
        self._wait_for_cloudflare(timeout=150)
        while not self._handle_captcha():
            self.driver.refresh()
            time.sleep(1)
        time.sleep(1)
        self._check_available()

    def _init_stealth_driver(self):
        """Create a new Selenium + stealth Chrome driver."""
        if not hasattr(self, 'options') or self.options is None:
            self.options = webdriver.ChromeOptions()
            for opt in ["--window-size=1920,1080","--disable-gpu","--no-sandbox",
                        "--disable-dev-shm-usage","--enable-unsafe-swiftshader","--log-level=3",
                        "--disable-blink-features=AutomationControlled","--disable-extensions"]:
                self.options.add_argument(opt)
            if OPERATING_SYSTEM == "Linux" and os.path.exists(Static.ChromeBinaryPath):
                self.options.binary_location = Static.ChromeBinaryPath
        if OPERATING_SYSTEM == "Linux" and os.path.exists(Static.ChromeDriverPath):
            from selenium.webdriver.chrome.service import Service
            service = Service(executable_path=Static.ChromeDriverPath)
            self.driver = webdriver.Chrome(service=service, options=self.options)
        else:
            self.driver = webdriver.Chrome(options=self.options)
        stealth(self.driver, languages=["en-US","en"], vendor="Google Inc.",
                platform="Win32", webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine", fix_hairline=True)

    def _click_type_button(self):
        """Click the service-type button using multiple strategies."""
        type_keywords = {
            'views':     ['video views', 'views'],
            'hearts':    ['hearts', 'likes'],
            'shares':    ['shares'],
            'favorites': ['favorites', 'favourite'],
            'followers': ['followers'],
            'repost':    ['repost'],
        }
        kws = type_keywords.get(TYPE, [TYPE])
        print(f"{INFO}Looking for '{TYPE}' button (keywords: {kws})…{Style.RESET_ALL}")

        # Strategy 1: button text matches keyword
        if self._js_click_button(kws, timeout=5):
            print(f"{INFO}Clicked '{TYPE}' button via button-text match{Style.RESET_ALL}")
            return True

        # Strategy 2: find any clickable element whose PARENT CONTAINER has keyword text
        # Covers cases where text is in a label above the → arrow button
        found = self.driver.execute_script("""
            var kws = arguments[0];
            // Search buttons whose nearest ancestor card contains any keyword
            var btns = document.querySelectorAll('button, [role="button"], a[onclick]');
            for (var i = 0; i < btns.length; i++) {
                var btn = btns[i];
                // Walk up to 5 parent levels
                var el = btn;
                for (var d = 0; d < 5; d++) {
                    if (!el || !el.parentElement) break;
                    el = el.parentElement;
                    var txt = el.textContent.trim().toLowerCase();
                    for (var j = 0; j < kws.length; j++) {
                        if (txt.indexOf(kws[j]) !== -1) {
                            btn.scrollIntoView({block:'center'});
                            btn.click();
                            return kws[j];
                        }
                    }
                }
            }
            return null;
        """, kws)
        if found:
            print(f"{INFO}Clicked '{TYPE}' button via parent-container text ('{found}'){Style.RESET_ALL}")
            return True

        # Strategy 3: try legacy XPATH
        try:
            btn = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((By.XPATH, Static.typeValues[TYPE])))
            self.driver.execute_script("arguments[0].click();", btn)
            print(f"{INFO}Clicked '{TYPE}' button via XPATH{Style.RESET_ALL}")
            return True
        except Exception:
            pass

        # Last resort: dump all buttons for debug info
        all_btns = self._js_dump_buttons()
        print(f"{WARNING}Button '{TYPE}' not found. Buttons on page: {all_btns}{Style.RESET_ALL}")
        return False

    def _select_type(self):
        self.remove_modal()
        self.remove_ads_vignette()
        """Select the type of action to perform"""
        max_retries = 3
        retries = 0

        while retries < max_retries:
            try:
                if self._click_type_button():
                    time.sleep(2.0)
                    self._get_views()
                    break
                else:
                    raise NoSuchElementException(f"Button for '{TYPE}' not found")
            except (TimeoutException, NoSuchElementException) as e:
                retries += 1
                print(f"{WARNING}Unable to find the button for {TYPE}.. Retrying.. (retry {retries}/{max_retries})")
                time.sleep(2 ** retries)
                if retries >= max_retries:
                    print(f"{WARNING} Max retries reached. Resetting the browser...")
                    self._reset_browser()
                    retries = 0

    def _get_views(self):
        """
        Main send loop — fully JS DOM-based, no hardcoded XPATHs.

        Flow per iteration:
          1. Fill the URL input field in the active panel
          2. Click the Search/Check button (Step 2)
          3. Read cooldown timer (Step 3) and wait if needed
          4. Click the Send button (Step 4 / finalButton)
        """
        self.User_Session.send_heartbeat()
        self.remove_modal()
        self.remove_ads_vignette()
        max_retries = 3
        retries = 0

        # Keywords to find the send/submit button after cooldown
        SEND_KEYWORDS = ['send', 'submit', 'go', 'boost', 'start']
        SEARCH_KEYWORDS = ['search', 'check', 'find', 'look']

        def js_click_any_button(keyword_lists, timeout=15):
            """Try each list of keywords in turn; click first matching button."""
            deadline = time.time() + timeout
            while time.time() < deadline:
                for kws in keyword_lists:
                    btn = self._js_find_button(kws)
                    if btn:
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block:'center'});", btn)
                        self.driver.execute_script("arguments[0].click();", btn)
                        return True
                # Also try: just click any submit-type button inside active panel
                clicked = self.driver.execute_script("""
                    var divs = document.querySelectorAll('div');
                    for (var i = 0; i < divs.length; i++) {
                        var d = divs[i];
                        var st = window.getComputedStyle(d);
                        if (st.display === 'none' || st.visibility === 'hidden') continue;
                        var inp = d.querySelector('input');
                        if (!inp) continue;
                        var btns = d.querySelectorAll('button');
                        if (btns.length > 0) {
                            btns[0].scrollIntoView({block:'center'});
                            btns[0].click();
                            return true;
                        }
                    }
                    return false;
                """)
                if clicked:
                    return True
                time.sleep(1)
            return False

        while retries < max_retries:
            try:
                time.sleep(0.5)

                # ── Step 1: fill the video URL input ──────────────────────────
                print(f"{INFO}[Step 1] Filling video URL via JS DOM…{Style.RESET_ALL}")
                filled = self._js_fill_input(self.video, timeout=20)
                if not filled:
                    # Try XPATH fallback
                    try:
                        el = WebDriverWait(self.driver, 10).until(
                            ec.presence_of_element_located(
                                (By.XPATH, Static.firstStep[TYPE])))
                        el.clear()
                        el.send_keys(self.video)
                        filled = True
                    except Exception:
                        pass
                if not filled:
                    all_inputs = self._js_dump_inputs()
                    print(f"{WARNING}[DEBUG] Inputs on page after click: {all_inputs}{Style.RESET_ALL}")
                    raise NoSuchElementException("Could not fill video URL input")
                print(f"{INFO}[Step 1] URL filled ✔{Style.RESET_ALL}")

                for _ in range(AMOUNT):
                    self.User_Session.send_heartbeat()
                    self.remove_ads_vignette()

                    # ── Mid-session captcha check ──────────────────────────────
                    captcha_visible = self.driver.execute_script("""
                        var imgs = document.querySelectorAll('form img');
                        for (var i = 0; i < imgs.length; i++) {
                            var st = window.getComputedStyle(imgs[i]);
                            if (st.display !== 'none' && st.visibility !== 'hidden') return true;
                        }
                        return false;
                    """)
                    if captcha_visible:
                        print(f"{WARNING}[CAPTCHA] Mid-session captcha detected — solving...{Style.RESET_ALL}")
                        self._handle_captcha()
                        time.sleep(2)
                        self.remove_modal()
                        # Re-click the Views button after captcha
                        self._click_type_button()
                        time.sleep(1)
                        # Re-fill URL
                        self._js_fill_input(self.video, timeout=15)

                    # Only clear screen when not headless (so logs aren't wiped)
                    if not AUTO_START and os.name == 'nt':
                        os.system("cls")
                    elif not AUTO_START:
                        os.system("clear")
                    self._show_banner(self.index)
                    time.sleep(0.5)

                    # ── Step 2: click Search/Check button ─────────────────────
                    print(f"{INFO}[Step 2] Clicking search button…{Style.RESET_ALL}")
                    clicked2 = js_click_any_button([SEARCH_KEYWORDS, SEND_KEYWORDS], timeout=15)
                    if not clicked2:
                        # XPATH fallback
                        try:
                            WebDriverWait(self.driver, 10).until(
                                ec.presence_of_element_located(
                                    (By.XPATH, Static.secondStep[TYPE]))).click()
                            clicked2 = True
                        except Exception:
                            pass
                    if not clicked2:
                        print(f"{WARNING}[Step 2] Could not click search button{Style.RESET_ALL}")
                    time.sleep(3)

                    # ── Step 3: read cooldown timer ────────────────────────────
                    try:
                        cooldown_text = None
                        # Try JS DOM first
                        deadline_cd = time.time() + SLEEP
                        while time.time() < deadline_cd:
                            cooldown_text = self._js_get_cooldown_text()
                            if cooldown_text:
                                break
                            # XPATH fallback
                            try:
                                el = self.driver.find_element(
                                    By.XPATH, Static.thirdStep[TYPE])
                                cooldown_text = el.text
                                if cooldown_text:
                                    break
                            except Exception:
                                pass
                            time.sleep(1)

                        if cooldown_text:
                            total_seconds = parse_cooldown(cooldown_text)
                            if total_seconds > 0:
                                while total_seconds > 0:
                                    minutes, seconds = divmod(total_seconds, 60)
                                    print(
                                        f"\r{WAITING} {ProgramUsage.Translations('main', 1)} "
                                        f"{minutes} {ProgramUsage.Translations('main', 2)} "
                                        f"{seconds} {ProgramUsage.Translations('main', 3)} "
                                        f"{Style.RESET_ALL}", end='')
                                    time.sleep(1)
                                    total_seconds -= 1
                                print()
                        self.remove_ads_vignette()
                    except Exception as e:
                        print(f"{WARNING}[Step 3] Cooldown read error: {e}{Style.RESET_ALL}")

                    # ── Step 4: click Send button ──────────────────────────────
                    self.remove_ads_vignette()
                    time.sleep(2)
                    print(f"{INFO}[Step 4] Clicking send button…{Style.RESET_ALL}")
                    clicked4 = js_click_any_button([SEND_KEYWORDS, SEARCH_KEYWORDS], timeout=15)
                    if not clicked4:
                        try:
                            WebDriverWait(self.driver, 10).until(
                                ec.presence_of_element_located(
                                    (By.XPATH, Static.fourthStep[TYPE]))).click()
                            clicked4 = True
                        except Exception:
                            pass
                    time.sleep(2)

                    # ── Final button (some sites have 2-step send) ─────────────
                    try:
                        self.remove_ads_vignette()
                        if not ProgramUsage.vk():
                            sys.exit()
                        # Try final send button via JS, then XPATH
                        final_clicked = js_click_any_button([SEND_KEYWORDS], timeout=8)
                        if not final_clicked:
                            try:
                                WebDriverWait(self.driver, 8).until(
                                    ec.presence_of_element_located(
                                        (By.XPATH, Static.finalButton[TYPE]))).click()
                            except Exception:
                                pass

                        increments = {'views': 1000, 'shares': 50,
                                      'favorites': 100, 'hearts': 10}
                        msg_keys   = {'views': 4, 'shares': 5,
                                      'favorites': 6, 'hearts': 7}

                        # ── Verify Zefoy accepted the request ─────────────────
                        time.sleep(2)
                        zefoy_response = self.driver.execute_script("""
                            var texts = [];
                            document.querySelectorAll('div,p,span,h1,h2,h3,h4,h5,h6,small').forEach(function(el) {
                                var st = window.getComputedStyle(el);
                                if (st.display === 'none' || st.visibility === 'hidden') return;
                                var t = el.innerText ? el.innerText.trim() : '';
                                if (t.length > 3 && t.length < 200 &&
                                    el.children.length === 0) {
                                    texts.push(t);
                                }
                            });
                            return texts.slice(0, 20).join(' | ');
                        """) or ""
                        zr_lower = zefoy_response.lower()
                        sent_ok = any(w in zr_lower for w in [
                            'success', 'sent', 'submitted', 'processing',
                            'added', 'complete', 'done', 'thank'
                        ])
                        failed = any(w in zr_lower for w in [
                            'error', 'invalid', 'failed', 'not found', 'wrong'
                        ])

                        if TYPE in increments:
                            ts = datetime.now().strftime('%H:%M:%S')
                            if not failed:
                                print(
                                    f"{ts} "
                                    f"{SUCCESS}{Fore.WHITE}"
                                    f"{ProgramUsage.Translations('main', msg_keys[TYPE])}"
                                    f"{Style.RESET_ALL}", flush=True)
                                self.counter += increments[TYPE]
                            else:
                                print(f"{ts} {WARNING}[Submit] Zefoy returned error — "
                                      f"response: {zefoy_response[:120]}{Style.RESET_ALL}", flush=True)

                        print(f"{INFO}[Zefoy response] {zefoy_response[:150]}{Style.RESET_ALL}", flush=True)

                        if self.is_webhook_valid and self.counter >= self.each_views:
                            self.webhook.post(content=self.message)
                            self.counter = 0

                    except Exception as e:
                        if "element click intercepted" in str(e).lower():
                            print(f"{Fore.RED}[Error] Click intercepted — "
                                  f"try HEADLESS=False in config.cfg (ERROR 000){Style.RESET_ALL}", flush=True)
                        else:
                            print(f"{Fore.RED}[Error] {e}{Style.RESET_ALL}", flush=True)
                        self.driver.refresh()
                        time.sleep(2)
                        self._select_type()

                    self.index += 1
                    time.sleep(3)

                break  # loop finished cleanly

            except TypeError as te:
                print(f"{WARNING} TypeError: {te}. Retrying… ({retries + 1}/{max_retries})")
                retries += 1
                if retries >= max_retries:
                    print(f"{WARNING} Failed after {max_retries} attempts. Exiting.")
                    sys.exit(1)

    def _is_ready(self):
        """Check if the system is ready to perform the action"""
        return WebDriverWait(self.driver, SLEEP).until(
            ec.presence_of_element_located((By.XPATH, Static.readyValues[TYPE]))).text.__contains__('READY') or len(
            WebDriverWait(self.driver, SLEEP).until(
                ec.presence_of_element_located((By.XPATH, Static.readyValues[TYPE]))).text) <= 0
    def _show_typeconfig(self):
        global TYPE
        def available_color(t):
            if t in self.elements:
                return Fore.GREEN
            return Fore.RED
        os.system("cls") if os.name == 'nt' else os.system("clear")
        print("Type Configuration : \n")
        _sel = ProgramUsage.Translations('main', 9)
        print(f"{available_color('views')}[{'1' if available_color('views') == Fore.GREEN else '-'}] Views {f'[{_sel}]' if TYPE.lower() == 'views' else ''}")
        print(f"{available_color('followers')}[{'2' if available_color('followers') == Fore.GREEN else '-'}] Followers {f'[{_sel}]' if TYPE.lower() == 'followers' else ''}")
        print(f"{available_color('favorites')}[{'3' if available_color('favorites') == Fore.GREEN else '-'}] Favorites {f'[{_sel}]' if TYPE.lower() == 'favorites' else ''}")
        print(f"{available_color('shares')}[{'4' if available_color('shares') == Fore.GREEN else '-'}] Shares {f'[{_sel}]' if TYPE.lower() == 'shares' else ''}")
        print(f"{available_color('hearts')}[{'5' if available_color('hearts') == Fore.GREEN else '-'}] Hearts {f'[{_sel}]' if TYPE.lower() == 'hearts' else ''}")
        print(f"{available_color('repost')}[{'6' if available_color('repost') == Fore.GREEN else '-'}] Repost {Fore.YELLOW}[NEW!!]{Style.RESET_ALL} {f'[{_sel}]' if TYPE.lower() == 'repost' else ''}")

        if AUTO_START:
            print(f"{INFO}AUTO_START enabled — using TYPE from config: {Fore.WHITE}{TYPE}{Style.RESET_ALL}")
            return

        print(Fore.CYAN, f"\n[99] - {ProgramUsage.Translations('main',8)}!", Style.RESET_ALL)
        print("\n")
        us = 0
        while True:
            try:
                us = int(input(f"{WAITING}Select an option \n-> {Style.RESET_ALL}").lower())
                if us >= 1 and us <= 99:
                    if us >= 7 and us <= 98:
                        pass
                    else:
                        break
            except Exception:
                pass
        type_map = {1: 'views', 2: 'followers', 3: 'favorites', 4: 'shares', 5: 'hearts', 6: 'repost'}
        if us == 99:
            return
        if us in type_map:
            TYPE = type_map[us]
        self._show_typeconfig()

    def _show_menu(self):
        """Show the program configuration menu"""
        os.system("cls") if os.name == 'nt' else os.system("clear")
        print(f"{datetime.now().strftime('%H:%M:%S')} {WAITING}{Fore.WHITE}Gathering Video Info...", end="\r")

        def _gather_info(info_type):
            try:
                if info_type == 'views':
                    return int(self.tiktok_info.get_video_info(Views=True))
                elif info_type == 'likes':
                    return int(self.tiktok_info.get_video_info(Likes=True))
                elif info_type == 'shares':
                    return int(self.tiktok_info.get_video_info(Shares=True))
                elif info_type == 'creator':
                    return self.tiktok_info.get_video_info(Creator=True)
            except ValueError:
                return 0
        InitialInfo.CREATOR = self.tiktok_info.get_video_info(Creator=True)
        InitialInfo.VIEWS_BEFORE = self.tiktok_info.get_video_info(Views=True)
        Handler.info_banner(_gather_info('views'),_gather_info('shares'),_gather_info('likes'),AMOUNT,INFO,_gather_info('creator'),TYPE) # Show Info Banner

        if AUTO_START:
            print(f"{INFO}AUTO_START enabled — starting automatically...{Style.RESET_ALL}")
            return

        while True:
            us = input(f"{WAITING}Want to start? (y/n)\n-> {Style.RESET_ALL}").lower()
            if us == 'y':
                return
            elif us == 'n':
                sys.exit()

    def _show_banner(self, index):
        """Show the progress banner"""
        temp = TikTokVideoInfo(self.video)
        ProgramUsage.save_or_replace_history(self.video_id,InitialInfo.CREATOR,InitialInfo.VIEWS_BEFORE,ProgramUsage.get_numeric_value(temp.get_video_info(Views=True)),ProgramUsage.get_numeric_value(temp.get_video_info(Likes=True)),ProgramUsage.get_numeric_value(temp.get_video_info(Shares=True)))
        if TYPE == 'views':
            views = ProgramUsage.get_numeric_value(temp.get_video_info(Views=True))
            print(f"{INFO}[{round((index / AMOUNT) * 100, 1)}%] {Fore.WHITE}Video Views : {Fore.WHITE}{views} {Fore.GREEN}[+{int(views - self.initial_views)}] {Style.BRIGHT}{Fore.MAGENTA}(Est. {ProgramUsage.convert_hours(round((AMOUNT - index) * 2 / 60, 2))} Remaining.{Style.RESET_ALL})")
        if TYPE == 'shares':
            shares = ProgramUsage.get_numeric_value(temp.get_video_info(Shares=True))
            print(f"{INFO}[{round((index / AMOUNT) * 100, 1)}%] {Fore.WHITE}Video Shares : {Fore.WHITE}{shares} {Fore.GREEN}[+{int(shares - self.initial_views)}] {Style.BRIGHT}{Fore.MAGENTA}(Est. {ProgramUsage.convert_hours(round((AMOUNT - index) * 2 / 60, 2))} Remaining.{Style.RESET_ALL})")
        if TYPE == 'favorites':
            favorites = 0
            print(f"{INFO}[{round((index / AMOUNT) * 100, 1)}%] {Fore.WHITE}Video Favorites : {Fore.WHITE}{favorites} {Fore.GREEN}[+{self.counter}] {Style.BRIGHT}{Fore.MAGENTA}(Est. {ProgramUsage.convert_hours(round((AMOUNT - index) * 2 / 60, 2))} Remaining.{Style.RESET_ALL})")
        if TYPE == 'hearts':
            hearts = ProgramUsage.get_numeric_value(temp.get_video_info(Likes=True))
            print(
                f"{INFO}[{round((index / AMOUNT) * 100, 1)}%] {Fore.WHITE}Video Hearts : {Fore.WHITE}{hearts} {Fore.GREEN}[+{int(hearts - self.initial_views)}] {Style.BRIGHT}{Fore.MAGENTA}(Est. {ProgramUsage.convert_hours(round((AMOUNT - index) * 2 / 60, 2))} Remaining.{Style.RESET_ALL})")

    def _menu(self):
        """Program configuration menu"""
        while True:
            try:
                msg = self.message.format(self.each_views)
            except KeyError:
                msg = self.message
            os.system("cls") if os.name == 'nt' else os.system("clear")

            Handler.webhook_banner(self.webhook_text,self.each_views,TYPE,msg)

            try:
                user_input = int(input("-> "))

                if user_input in range(1, 6) or user_input == 99:
                    if user_input == 1:
                        self.webhook_text = input("Insert new -> ")
                        self.webhook = Discord(url=self.webhook_text)
                    if user_input == 2:
                        try:
                            self.webhook.post(content="**Test Message To Webhook From TikTok Booster**")
                            print(Fore.GREEN + "Valid!")
                        except (TimeoutException, NoSuchElementException):
                            print(Fore.RED + "Invalid Webhook!" + Style.RESET_ALL)
                            time.sleep(0.5)
                    if user_input == 3:
                        try:
                            self.each_views = int(input("Insert new -> "))
                        except ValueError:
                            pass
                    if user_input == 4:
                        self.message = input("Insert new -> ")
                        try:
                            msg = self.message.format(self.each_views)
                        except KeyError:
                            msg = self.message
                    if user_input == 5:
                        try:
                            config.set("Settings", "WEBHOOK", str(self.webhook))
                            config.set("Settings", "EACH_VIEWS", str(self.each_views))
                            config.set("Settings", "MESSAGE", str(self.message))
                            with open("config.cfg", "w") as configfile:
                                config.write(configfile)
                            print("Saved!")
                            time.sleep(1)
                        except Exception as e:
                            print(e)
                            input()
                    if user_input == 99:
                        break
            except ValueError:
                pass


if __name__ == "__main__":
    check_issues()
    check_version(VERSION)
    if not ProgramUsage.vk():
        sys.exit()
    os.system("cls") if os.name == 'nt' else os.system("clear")
    show_credits()
    is_first_run()
    try:
        TikTokBooster()
    except SessionNotCreatedException:
        print("Session was not created")
