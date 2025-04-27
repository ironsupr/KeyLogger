# StealthOps - Advanced Keylogger Documentation

## Overview

This is a sophisticated monitoring tool that captures various types of system data and sends it securely via Telegram. The tool runs continuously and collects data at regular intervals.

## Features

- Keyboard logging
- Screenshot capture
- Webcam capture
- Audio recording
- System information gathering
- Clipboard monitoring
- Encrypted file storage
- Secure data transmission via Telegram
- Automatic cleanup

## Components

### 1. Data Collection

- **Keyboard Logging**: Records all keystrokes
- **Screenshots**: Captures full screen images
- **Webcam**: Takes photos using system webcam
- **Microphone**: Records audio (20-second clips)
- **System Info**: Collects:
  - Public/Private IP
  - Processor details
  - OS information
  - Hostname
  - Machine specifications
- **Clipboard**: Monitors clipboard content

### 2. Security Features

- File encryption using Fernet (symmetric encryption)
- Secure transmission via Telegram API
- Automatic file cleanup
- Error handling and logging

### 3. Timing & Intervals

- Data collection every 60 seconds
- Audio recording: 20 seconds
- Continuous operation until shutdown signal

## File Structure

```
Files/
├── key_log.txt         # Keystroke logs
├── systeminfo.txt      # System information
├── clipboard.txt       # Clipboard data
├── audio.wav          # Audio recordings
├── screenshot.png     # Screen captures
├── webCamera.png      # Webcam images
├── e_key_log.txt      # Encrypted keystroke logs
├── e_systeminfo.txt   # Encrypted system information
└── e_clipboard.txt    # Encrypted clipboard data
```

## Operation Flow

1. **Initialization**

   - Validate configuration
   - Create necessary files
   - Set up encryption
   - Initialize Telegram bot

2. **Continuous Monitoring Loop**

   - Monitor keystrokes
   - Every 60 seconds:
     - Capture screenshot
     - Take webcam photo
     - Record 20s audio
     - Check clipboard
     - Gather system info
     - Encrypt sensitive data
     - Send data via Telegram

3. **Cleanup Process**
   - Encrypt sensitive files
   - Send encrypted files
   - Remove original files
   - Clear traces

## Configuration

- Telegram Bot Token
- Chat ID
- File paths
- Timing intervals
- Encryption keys

## Security Considerations

- Files are encrypted before transmission
- Local files are securely deleted
- Data is sent via Telegram's secure API
- Error handling prevents data leakage

## Error Handling

- Logging of all operations
- Fallback mechanisms for failed operations
- Exception handling for each component
- Graceful shutdown capability

## Dependencies

- telegram-python-bot
- pynput
- sounddevice
- opencv-python
- cryptography
- PIL (Python Imaging Library)
- pywin32

## Usage

1. Configure Telegram bot credentials
2. Set desired file paths
3. Run main.py
4. Monitor received data in Telegram

## Shutdown

- Use Ctrl+C for graceful shutdown
- Automatic cleanup of all generated files
- Logging of shutdown process
