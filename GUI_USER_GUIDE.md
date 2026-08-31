# Face Swap Avatar GUI - User Guide 🎭

Complete guide to using the new Face Swap Avatar GUI application with avatar management, auto-detection, and meeting detection.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Creating Your First Avatar](#creating-your-first-avatar)
3. [Avatar Management](#avatar-management)
4. [Settings & Configuration](#settings--configuration)
5. [Using in Video Calls](#using-in-video-calls)
6. [Auto-Detection Features](#auto-detection-features)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the GUI application
python face_swap_avatar_gui.py
```

### First Launch

When you first launch the application:

1. **Main Window Opens** with 3 tabs:
   - Avatar Management
   - Settings
   - Information

2. **Status Display** at top shows:
   - Current status (DISABLED/ENABLED)
   - Selected avatar name
   - Big ENABLE button for quick access

3. **System Tray Icon** appears for minimizing to background

---

## Creating Your First Avatar

### Method 1: Capture from Webcam (Recommended)

1. Go to **"Avatar Management"** tab
2. Click **"Start Capture Wizard"**
3. Follow on-screen instructions:
   - **Step 1**: Center pose (face straight) → Click "Capture"
   - **Step 2**: Left 30° → Turn head left, click "Capture"
   - **Step 3**: Left 45° → Turn head more left, click "Capture"
   - **Step 4**: Right 30° → Turn head right, click "Capture"
   - **Step 5**: Right 45° → Turn head more right, click "Capture"
   - **Step 6**: Up tilt → Tilt head up, click "Capture"
   - **Step 7**: Down tilt → Tilt head down, click "Capture"
4. Enter avatar name (e.g., "My Avatar")
5. Click "Save Avatar"

**Tips:**
- Use good lighting
- Keep face centered and clear
- Maintain consistent expression
- Don't move too quickly

### Method 2: Import Existing Images

1. Go to **"Avatar Management"** tab
2. Click **"Import Avatar Images"**
3. Select folder containing your 7 avatar images:
   ```
   my_avatars/
   ├── center.jpg
   ├── left_30.jpg
   ├── left_45.jpg
   ├── right_30.jpg
   ├── right_45.jpg
   ├── up_20.jpg
   └── down_20.jpg
   ```
4. Enter avatar name
5. Click "Import"

**Image Requirements:**
- Resolution: 640×640 or higher
- Format: JPG or PNG
- Clear, well-lit face
- Consistent expression

---

## Avatar Management

### View Available Avatars

**Avatar List** section shows all your avatars:
- Avatar name
- Creation date
- Available angles

**Avatar Preview** shows the selected avatar's center pose.

### Switch Between Avatars

1. Click avatar name in dropdown or list
2. Preview updates immediately
3. Click **ENABLE** to start using this avatar

### Delete Avatar

1. Click avatar in "Available Avatars" list
2. Click **"Delete Selected Avatar"**
3. Confirm deletion
4. Avatar is permanently removed

### Update Avatar

To change an avatar:
1. Delete the existing one
2. Create a new one with same name or different name

---

## Settings & Configuration

### Camera Settings

| Setting | Default | Options |
|---------|---------|---------|
| Webcam | Auto-detected | Dropdown list of connected cameras |

**To change camera:**
1. Go to **"Settings"** tab
2. Select different camera from dropdown
3. Click **"Save Settings"**

### Processing Settings

#### Target FPS
- **Default**: 30 FPS
- **Range**: 10-60
- **Recommendation**: 30 for video calls, 15 for slow computers

#### Smoothing (EMA)
- **Default**: 0.35
- **Range**: 0.1-0.5
- **Lower values** = smoother but more lag
- **Higher values** = faster response but more jitter

#### GPU Acceleration
- **Default**: Enabled (if GPU available)
- **Benefits**: 3-5x faster processing
- **Disable if**: GPU causes instability

#### Preview Window
- **Default**: Disabled
- **Enable if**: You want to see output in real-time
- **Note**: Disabling improves performance

### Auto-Detection Settings

#### Auto-detect Virtual Camera
- **Default**: Enabled
- **Function**: Automatically finds available virtual camera
- **Useful for**: Using with any video conferencing app

#### Auto-start on Meeting Detection
- **Default**: Enabled
- **Function**: Automatically starts face swap when it detects a meeting
- **Supported Apps**: Zoom, Teams, Discord, Google Meet (browser)
- **Example**: Opening Zoom → Service auto-starts

#### Minimize to System Tray
- **Default**: Enabled
- **Function**: Closing window minimizes to tray instead of exiting
- **Useful for**: Running in background

### Saving Settings

After changing any settings:
1. Modify desired values
2. Click **"Save Settings"**
3. Settings saved to `settings.json`
4. Settings loaded automatically on next launch

---

## Using in Video Calls

### Step-by-Step

**Before the Meeting:**

1. Launch Face Swap Avatar GUI
2. Select your avatar
3. Go to Settings tab, adjust if needed
4. Click **ENABLE** button
5. Status changes to "Status: ENABLED - Avatar: [name]"
6. Minimize to tray if desired

**In Zoom/Teams/Meet:**

1. Open video conferencing app
2. Go to Camera/Video settings
3. Look for "FaceSwapAvatar" or virtual camera in dropdown
4. Select it
5. Your avatar appears in the video preview
6. Join the meeting - you're now using your avatar!

**Ending the Meeting:**

1. Leave the video meeting normally
2. (Optional) Click DISABLE to stop the service
3. Or just close the app (if auto-start enabled, it stops automatically)

---

## Auto-Detection Features

### Meeting Detection

The application automatically detects when you're in a video meeting by:
- Monitoring running processes (Zoom, Teams, Discord)
- Checking system for active video calls
- Runs in background without user interaction

**How it works:**
1. Service monitors for meeting apps
2. When meeting detected → Face swap automatically starts
3. When meeting ends → Face swap automatically stops
4. User can still manually enable/disable anytime

**Supported Apps:**
- ✅ Zoom
- ✅ Microsoft Teams
- ✅ Discord
- ✅ Google Meet (browser)
- ✅ Skype
- ✅ OBS Studio
- ✅ Slack Calls
- ✅ Webex

### Virtual Camera Detection

The application automatically finds your virtual camera:
- Scans for available cameras on startup
- Updates every 5 seconds
- Selects correct virtual camera output

**If not detected:**
1. Ensure virtual camera driver installed
2. Restart application
3. Manually select in Settings

---

## Advanced Features

### System Tray Integration

**Right-click tray icon:**
- Show → Opens main window
- Hide → Minimizes to tray
- Exit → Closes application

**Left-click tray icon:** Toggles show/hide

### Logging

Logs saved to `face_swap_avatar_gui.log`:
- Application events
- Errors and warnings
- Performance statistics
- Avatar captures

**View logs:**
```bash
# Linux/Mac
tail -f face_swap_avatar_gui.log

# Windows PowerShell
Get-Content face_swap_avatar_gui.log -Wait
```

### Background Service

The application can run in the background:
1. Enable service
2. Minimize to tray
3. Application runs with minimal resource usage
4. Auto-starts with meetings

---

## Troubleshooting

### "No avatars available"

**Problem:** Avatar list is empty

**Solution:**
1. Click "Start Capture Wizard" or "Import Avatar Images"
2. Follow steps to create first avatar
3. Avatar appears in list

### "Cannot access camera"

**Problem:** Camera dropdown empty or says "Camera not found"

**Solution:**
1. Verify webcam is connected
2. Test in other app (e.g., Skype, browser)
3. Restart application
4. Restart computer if needed
5. Update camera drivers

### "Virtual camera not found"

**Problem:** Virtual camera not available in Zoom/Teams

**Solution:**
1. Verify virtual camera driver installed
2. Options:
   - **Windows**: Install OBS Studio with VirtualCam plugin
   - **Linux**: `sudo modprobe v4l2loopback`
   - **Mac**: Install CamTwist or Snap Camera
3. Restart application
4. Manually select virtual camera in Settings

### "Face not detected"

**Problem:** Capture wizard says "No face detected"

**Solution:**
1. Improve lighting (move to brighter area)
2. Move closer to camera
3. Ensure face fills ~60% of frame
4. Remove sunglasses or obstructions
5. Try different angle

### "Low performance / High CPU usage"

**Problem:** Application using too much CPU

**Solution:**
1. Reduce target FPS to 15-20
2. Disable preview window
3. Use CPU-only mode (disable GPU)
4. Close other applications
5. Reduce detection size in advanced settings

### "GPU not being used"

**Problem:** Even with GPU enabled, using CPU

**Solution:**
1. Verify NVIDIA driver installed: `nvidia-smi`
2. Check CUDA compatibility
3. Try CPU-only mode to verify app works
4. Update GPU drivers
5. Check GPU memory availability

### "Auto-start not working"

**Problem:** Service doesn't auto-start with Zoom/Teams

**Solution:**
1. Verify "Auto-start on Meeting Detection" is enabled in Settings
2. Check that meeting app is running
3. View logs for errors: `face_swap_avatar_gui.log`
4. Restart application
5. Try manual Enable/Disable first

### Application crashes on startup

**Problem:** App crashes immediately after launch

**Solution:**
1. Check system meets minimum requirements
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Delete old settings: `rm settings.json`
4. Check logs: `face_swap_avatar_gui.log`
5. Ensure model file exists: `inswapper_128.onnx`

---

## Tips & Tricks

### Performance Tips
1. **Best FPS**: Use GPU if available (3-5x faster)
2. **Good Performance**: 30 FPS at 1080p with modern GPU
3. **Acceptable**: 15-20 FPS works fine for video calls
4. **Smooth Tracking**: Use smoothing value around 0.35

### Avatar Tips
1. **Quality Matters**: Higher resolution avatars = better results
2. **Consistent Lighting**: All 7 images should have similar lighting
3. **Clear Face**: Ensure face is visible and takes up ~60% of frame
4. **Neutral Expression**: Keeps avatar looking natural
5. **Multiple Avatars**: Create several, switch based on context

### Meeting Tips
1. **Test First**: Do a test call before important meeting
2. **Good Lighting**: Well-lit room = better detection
3. **Center Face**: Keep face centered in frame
4. **Still Background**: Helps with focus
5. **Backup Ready**: Have system camera as fallback

---

## Building as Windows Installer

### Automated Build

```bash
# Generate .exe
python -m PyInstaller face_swap_avatar_gui.spec

# Result
dist/FaceSwapAvatar/FaceSwapAvatar.exe
```

### Create Installer (Optional)

```bash
# Install NSIS
# https://nsis.sourceforge.io/

# Build installer
makensis installer.nsi

# Result
FaceSwapAvatar_Setup.exe
```

---

## Performance Specifications

### Minimum Requirements
- **CPU**: Intel i5 / AMD Ryzen 5
- **RAM**: 8 GB
- **GPU**: Optional (falls back to CPU)
- **Webcam**: Standard USB webcam

### Recommended
- **CPU**: Intel i7 / AMD Ryzen 7
- **RAM**: 16 GB
- **GPU**: NVIDIA GTX 1660 or better
- **Camera**: 720p or higher

### Expected Performance
| Hardware | Resolution | FPS | CPU | GPU |
|----------|-----------|-----|-----|-----|
| CPU Only (i7) | 1280×720 | 20-25 | 40% | - |
| GTX 1660 | 1920×1080 | 30 | 15% | 45% |
| RTX 3070 | 1920×1080 | 60 | 10% | 30% |

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Q | Quit application |
| Ctrl+E | Toggle enable/disable |
| Ctrl+S | Save settings |
| Tab | Switch between tabs |

---

## FAQ

**Q: Can I use multiple avatars?**
A: Yes! Create as many as you want, switch between them instantly.

**Q: Is this real-time?**
A: Yes, processes at 25-30 FPS on modern hardware.

**Q: Does it work in Zoom?**
A: Yes, and Teams, Meet, Discord, OBS, etc.

**Q: Can I modify avatars?**
A: Delete and recreate with new images.

**Q: Does it require internet?**
A: No, everything runs locally.

**Q: Can I use AI-generated avatars?**
A: Yes! Works with any portrait images.

**Q: Will it slow down my computer?**
A: Minimal impact with GPU (2-3% baseline), uses 20-40% with CPU.

**Q: How do I uninstall?**
A: Delete folder or use Windows Add/Remove Programs.

---

## Support & Resources

- **Issues?** Check logs: `face_swap_avatar_gui.log`
- **Setup help?** See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Building?** See [BUILD_GUIDE.md](BUILD_GUIDE.md)
- **General info?** See [README.md](README.md)

---

**Enjoy your avatar! 🎭**
