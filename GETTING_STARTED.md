# Getting Started - Step-by-Step 🎬

Follow these steps to get Face Swap Avatar running in minutes!

## Prerequisites Checklist

Before you start, make sure you have:
- [ ] Python 3.9+ installed ([python.org](https://python.org))
- [ ] Git installed (optional)
- [ ] Webcam connected and working
- [ ] Virtual camera driver installed (see Step 1)
- [ ] ~500 MB free disk space

## STEP 1: Install Virtual Camera Driver (Platform-Specific)

### Windows
**Option A: OBS Studio + VirtualCam (Recommended)**
```
1. Download OBS Studio: https://obsproject.com
2. Install OBS
3. Open OBS → Tools → VirtualCam → Start Virtual Camera
4. Done! Virtual camera is now available
```

**Option B: VB-Cable**
```
1. Download: https://vb-audio.com/Cable/
2. Install and restart computer
3. Virtual camera "CABLE Output" will appear
```

### Linux (Ubuntu/Debian)
```bash
# Install virtual camera driver
sudo apt-get install v4l2loopback-dkms

# Load the module
sudo modprobe v4l2loopback

# Verify
ls /dev/video*
```

### macOS
```
1. Install CamTwist: https://www.camtasia.com/camtwist
   OR
2. Install Snap Camera: https://snapcamera.snapchat.com
```

---

## STEP 2: Get the Project Files

### Option A: Download ZIP
```
1. Go to repository
2. Click "Code" → "Download ZIP"
3. Extract to desired location
4. Open terminal in extracted folder
```

### Option B: Git Clone
```bash
git clone <repository-url>
cd build_environment
```

---

## STEP 3: Install Python Dependencies

```bash
# Navigate to project directory
cd path/to/build_environment

# Install requirements
pip install -r requirements.txt

# Verify installation
python face_swap_avatar_enhanced.py --help
```

If you get "command not found", use `python3` instead of `python`.

---

## STEP 4: Download Face Swap Model

The AI model that performs the face swapping:

```bash
# Go to releases page
# https://github.com/insightface/insightface/releases

# Download: inswapper_128.onnx
# Place it in your project root directory
```

**Expected location:**
```
build_environment/
├── face_swap_avatar_enhanced.py
├── inswapper_128.onnx          ← Model file
└── ...
```

---

## STEP 5: Prepare Avatar Images

Create folder: `avatars` (if it doesn't exist)

```bash
mkdir avatars
```

Add 7 avatar images to this folder:

| Filename | Description | Example |
|----------|-------------|---------|
| `center.jpg` | Face looking straight | 👤 |
| `left_30.jpg` | Head turned left | ↙️ |
| `left_45.jpg` | Head turned more left | ⬅️ |
| `right_30.jpg` | Head turned right | ↗️ |
| `right_45.jpg` | Head turned more right | ➡️ |
| `up_20.jpg` | Head tilted up | ⬆️ |
| `down_20.jpg` | Head tilted down | ⬇️ |

### Image Requirements
- **Resolution**: 640×640 or higher
- **Quality**: High quality, no blurriness
- **Face**: Clear, well-lit face
- **Expression**: Neutral or consistent
- **Format**: JPG, PNG

### How to Get Avatar Images

**Option 1: AI-Generated**
- Midjourney
- Stable Diffusion
- DALL-E 3
- Prompt: "Professional headshot of [character name] at different angles"

**Option 2: Photography**
- Professional headshots
- Rendered 3D models
- Video game characters
- Anime/art styles

**Option 3: Use Existing Photos**
- Your own photos at different angles
- Celebrity or character images
- Social media profile pictures

### Folder Structure
```
build_environment/
├── face_swap_avatar_enhanced.py
├── inswapper_128.onnx
├── avatars/
│   ├── center.jpg
│   ├── left_30.jpg
│   ├── left_45.jpg
│   ├── right_30.jpg
│   ├── right_45.jpg
│   ├── up_20.jpg
│   └── down_20.jpg
└── ...
```

---

## STEP 6: Run the Application

### Start the application:

```bash
# Basic run
python face_swap_avatar_enhanced.py

# Or with Python 3
python3 face_swap_avatar_enhanced.py
```

You should see output like:
```
[+] Webcam connected: 1920x1080 @ 30 FPS
[+] Virtual camera active: /dev/video2
[+] Ready to use in Zoom/Teams/Google Meet
[+] Live stream running. Select this virtual camera in Zoom/Teams/Meet.
```

### Options:
```bash
# Disable preview window (faster)
python face_swap_avatar_enhanced.py --no-preview

# Use different camera
python face_swap_avatar_enhanced.py --camera 1

# CPU-only mode (no GPU)
python face_swap_avatar_enhanced.py --no-gpu

# Custom config
python face_swap_avatar_enhanced.py --config my_config.json

# Show all options
python face_swap_avatar_enhanced.py --help
```

---

## STEP 7: Use in Video Call

### Zoom
```
1. Open Zoom
2. Settings (gear icon)
3. Video
4. Camera dropdown
5. Select "OBS Virtual Camera" or "FaceSwapAvatar"
6. Done! You now show as your avatar
```

### Google Meet
```
1. Go to meet.google.com
2. Start or join a meeting
3. Bottom left: Click camera icon
4. Select virtual camera
5. You're now using your avatar
```

### Microsoft Teams
```
1. Open Microsoft Teams
2. Settings (gear icon)
3. Devices
4. Camera dropdown
5. Select virtual camera
6. Join meeting as avatar
```

### Discord
```
1. Open Discord
2. Settings (gear icon)
3. Voice & Video
4. Camera dropdown
5. Select virtual camera
6. Ready for video chat
```

### OBS Studio (Streaming)
```
1. Add "Video Capture Device" source
2. Select virtual camera
3. Add to streaming scene
4. Stream your avatar
```

---

## Troubleshooting 🔧

### "ModuleNotFoundError: No module named 'cv2'"
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### "inswapper_128.onnx not found"
```bash
# Download the model from GitHub releases
# https://github.com/insightface/insightface/releases
# Place in project root directory
```

### "No face detected"
- ✓ Check lighting (bright environment)
- ✓ Move closer to webcam
- ✓ Ensure avatars have clear faces
- ✓ Check camera works (test in other apps)

### "Virtual camera not available"
- ✓ Restart virtual camera driver
- ✓ Restart application
- ✓ Restart video conferencing app
- ✓ Check correct camera driver installed

### "Low performance / High CPU"
```bash
# Use CPU-only and disable preview
python face_swap_avatar_enhanced.py --no-gpu --no-preview

# Or reduce FPS
python face_swap_avatar_enhanced.py --fps 15
```

### "GPU not being used"
```bash
# Check if NVIDIA drivers installed
nvidia-smi

# If not found, update GPU drivers

# Test CPU mode first
python face_swap_avatar_enhanced.py --no-gpu
```

---

## Advanced: Custom Configuration

Create `config.json`:
```json
{
  "model_path": "inswapper_128.onnx",
  "avatar_dir": "avatars",
  "camera_index": 0,
  "target_fps": 30,
  "detection_size": [640, 640],
  "pose_filter_alpha": 0.35,
  "enable_preview": true,
  "gpu_enabled": true,
  "enable_pose_smoothing": true
}
```

Then run:
```bash
python face_swap_avatar_enhanced.py --config config.json
```

### Configuration Options
- `target_fps`: 15-60 (higher = smoother but slower)
- `pose_filter_alpha`: 0.1-0.5 (higher = smoother but more lag)
- `detection_size`: [480, 480] or [640, 640] (higher = more accurate but slower)
- `enable_preview`: true/false (disable for better performance)

---

## Building Windows .exe (Optional)

Want to share with others who don't have Python?

```bash
# Automated build (Windows)
build_windows.bat

# Or manual
pip install pyinstaller
pyinstaller face_swap_avatar.spec
```

Result: `dist/FaceSwapAvatar/FaceSwapAvatar.exe`

---

## Tips for Best Results ✨

1. **Lighting**: Good lighting = better face detection
2. **Camera Quality**: Higher resolution = more accurate
3. **Avatar Quality**: Good quality avatars = better results
4. **Head Positioning**: Keep face centered in frame
5. **Smooth Movements**: Move head slowly for natural avatar
6. **FPS**: 25-30 FPS is ideal (25 works fine)
7. **GPU**: Use GPU if available (3-5x faster)
8. **Test First**: Test in a test call before important meeting

---

## Logs and Debugging

Check logs for issues:
```bash
# View log file
tail -f face_swap_avatar.log

# On Windows (PowerShell)
Get-Content face_swap_avatar.log -Wait
```

Logs show:
- Face detection statistics
- Performance metrics
- Error messages
- Configuration details

---

## Common Settings

### For Slow Computers
```bash
python face_swap_avatar_enhanced.py --fps 15 --no-preview
```

### For Meetings (Best Quality)
```bash
python face_swap_avatar_enhanced.py --fps 30
```

### For Streaming (High Quality)
```bash
python face_swap_avatar_enhanced.py --fps 30
```

### For Testing
```bash
python face_swap_avatar_enhanced.py --no-preview
```

---

## Next Steps

✓ **Working?** - You're done! Enjoy your avatar!

✗ **Not working?** - Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed troubleshooting

🔨 **Want to customize?** - Edit `face_swap_avatar_enhanced.py` or modify config

📦 **Want to share?** - Read [BUILD_GUIDE.md](BUILD_GUIDE.md) for .exe distribution

📚 **Need help?** - Read documentation or check script with `--help`

---

## Quick Reference

```bash
# Show all options
python face_swap_avatar_enhanced.py --help

# Start normally
python face_swap_avatar_enhanced.py

# No preview (faster)
python face_swap_avatar_enhanced.py --no-preview

# Different camera
python face_swap_avatar_enhanced.py --camera 1

# Custom config
python face_swap_avatar_enhanced.py --config config.json

# CPU only
python face_swap_avatar_enhanced.py --no-gpu

# Generate config template
python face_swap_avatar_enhanced.py --save-config my_config.json

# Low performance mode
python face_swap_avatar_enhanced.py --fps 15 --no-preview --no-gpu
```

---

**Enjoying your avatar? Share it with friends! 🎭**

**Having issues?** Reference the complete guides:
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup
- [BUILD_GUIDE.md](BUILD_GUIDE.md) - Building .exe
- [README.md](README.md) - Full documentation
