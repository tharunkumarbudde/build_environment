# ⚙️ SETUP GUIDE - Before Running the App

**🚨 IMPORTANT: Read this BEFORE trying to run anything!**

---

## Step 1: Prerequisites

You need:
- ✅ Python 3.9+ (download from python.org if you don't have it)
- ✅ This project folder
- ✅ ~30 MB of disk space for dependencies

---

## Step 2: Install Dependencies

Open a terminal/command prompt in the project folder and run:

### Windows (PowerShell):
```powershell
python -m pip install -r requirements.txt
```

### Linux/Mac (Terminal):
```bash
pip3 install -r requirements.txt
```

This will download and install all required libraries. **This may take 5-15 minutes the first time.**

### Expected output:
```
Successfully installed opencv-python numpy insightface onnxruntime pyvirtualcam PyQt5 ...
```

### If you get an error:
- Make sure Python is in your PATH: `python --version` or `python3 --version`
- Make sure you have internet connection
- Make sure pip is installed: `python -m pip --version`

---

## Step 3: Run the App

After dependencies are installed, run:

### Windows:
```cmd
python face_swap_avatar_gui.py
```

### Linux/Mac:
```bash
python3 face_swap_avatar_gui.py
```

### If the GUI window doesn't open:
- Wait 10-15 seconds (first run is slow while it loads the models)
- Check that all dependencies installed correctly: `python -m pip list | grep -i opencv`

---

## Step 4: Create Your First Avatar

1. The GUI window will open
2. Click "Start Capture Wizard"
3. Follow the 7-step guide:
   - **Step 1-7**: Take photos at different angles (center, left 30°, left 45°, right 30°, right 45°, up, down)
   - Click "Capture" for each pose
4. Wait for avatar to be created
5. Avatar appears in the list on the left

---

## Step 5: Use in Video Call

1. Click **ENABLE** button in the GUI (should turn green)
2. Open Zoom / Google Meet / Microsoft Teams
3. Go to camera settings
4. Select **"FaceSwapAvatar"** from camera list
5. Done! Your avatar will appear in the video call

---

## Troubleshooting

### "No module named 'cv2'"
→ You skipped Step 2. Run: `pip install -r requirements.txt`

### GUI doesn't open
→ Wait 15 seconds (first run loads models from disk)
→ Check: `python -c "import cv2; print('OK')"`

### Avatar capture doesn't work
→ Make sure webcam is working and has permission
→ Try: `python face_swap_avatar_enhanced.py --camera 0` to test camera

### Can't select virtual camera in Zoom
→ You need to install a virtual camera driver first:
   - Windows: [OBS VirtualCam](https://obsproject.com/)
   - Linux: `sudo apt install v4l2loopback-dkms`
   - Mac: [CamTwist](http://camtwiststudio.com/) or OBS VirtualCam

---

## What Gets Downloaded?

When you run `pip install -r requirements.txt`, these libraries are installed (~500 MB total):

- **OpenCV** (cv2) - Computer vision
- **NumPy** - Array processing
- **InsightFace** - Face detection/recognition
- **ONNX Runtime** - ML inference engine
- **PyVirtualCam** - Virtual camera support
- **PyQt5** - GUI framework
- **psutil** - System monitoring
- Plus 7 more support libraries

**Note**: The actual face-swap model (`inswapper_128.onnx`) is downloaded on first run (~70 MB).

---

## Next Steps

✅ Once setup is complete:

1. Read: [00_START_HERE.md](00_START_HERE.md)
2. Use: Run the GUI and create your avatar
3. Share: Follow [BUILD_GUIDE.md](BUILD_GUIDE.md) to create a .exe for others

---

## Got stuck?

Check these files for more help:
- [GUI_USER_GUIDE.md](GUI_USER_GUIDE.md) - Step-by-step usage
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed troubleshooting
- [README.md](README.md) - General project info

**Questions?** Make sure you followed Steps 1-3 above first!
