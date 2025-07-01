# Android_Solitaire_Bot

An automated bot that plays the Solitaire card game on Android devices using simple game logic and computer vision.

---

## Requirements

- Windows 10  
- Python 3.13 or later  
- Android Platform SDK Tools  
- Android phone with a screen resolution of **720 x 1600**

---

## Installation

1. **Install Python**  
   Download and install Python 3.13 or the latest version from the official website:  
   [https://www.python.org/downloads](https://www.python.org/downloads)  
   > ✅ Make sure to add Python to your PATH during installation.

2. **Install project dependencies**  
   Open a terminal and run:
   ```bash
   pip install -r requirements.txt

3. **Download Android SDKK Platform Tools**
   Download from:
   [https://developer.android.com/tools/releases/platform-tools](https://developer.android.com/tools/releases/platform-tools)
   Extract the ZIP file into your working directory.

4. **Add android_bridge.dll**
   Copy `android_bridge.dll` into the extracted SDK tools folder.

5. **Prepare your Android phone**
   - Connect your phone to the PC via USB
   - Enable Developer Options and USB Debugging

6. **Update configuration paths**
   - In `game_ui.py`, set the correct paths for:
   ```bash
   AndroidBridgePath = "path/to/your/platform-tools"

7. Install the Solitaire game on your phone
   [Solitaire - Classic Card Games (Google Play Store)](https://play.google.com/store/apps/details?id=com.mobilityware.solitaire)

## Running the Bot
1. Ensure your Android phone’s screen resolution is 720 x 1600.
2. Launch the Solitaire app on the phone.
3. Run the bot by executing:
   ```bash
   python main.py


