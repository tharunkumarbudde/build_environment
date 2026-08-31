# Quick Start Guide 🚀

Get Face Swap Avatar running in 5 minutes!

## Prerequisites
- Python 3.9+
- Webcam
- ~500MB disk space

## Step 1: Install (2 minutes)

```bash
# Install dependencies
pip install -r requirements.txt
```

## Step 2: Prepare Assets (2 minutes)

### Download Model
1. Go to: https://github.com/insightface/insightface/releases
2. Download `inswapper_128.onnx`
3. Place in project root directory

### Prepare Avatars
Create folder: `avatars/`

Add these 7 images (recommended: 640x640 or higher):
- `center.jpg` - Face straight
- `left_30.jpg` - Head turned left
- `left_45.jpg` - Head more left
- `right_30.jpg` - Head turned right
- `right_45.jpg` - Head more right
- `up_20.jpg` - Head tilted up
- `down_20.jpg` - Head tilted down

You can use:
- AI-generated avatars (e.g., from Midjourney, Stable Diffusion)
- Photos of yourself in different angles
- Celebrity/character images
- 3D rendered avatars

## Step 3: Run (1 minute)

```bash
python face_swap_avatar_enhanced.py
```

You should see:
```
[+] Camera opened: 1920x1080 @ 30 FPS
[+] Virtual camera active: /dev/video2
[+] Ready to use in Zoom/Teams/Google Meet
```

## Step 4: Use in Zoom

1. Open Zoom
2. Settings → Video → Camera
3. Select your virtual camera
4. Done! You're now using your avatar 🎉

## Common Issues

**"No faces detected"**
- Ensure good lighting
- Move closer to webcam
- Check avatar images have clear faces

**"Model not found"**
- Download `inswapper_128.onnx`
- Place in project root

**"Virtual camera not found"**
- Install virtual camera driver
  - Windows: Use OBS VirtualCam
  - Linux: `sudo modprobe v4l2loopback`
  - Mac: Use CamTwist

## Windows .exe Version

Want a standalone application?

```bash
# Build automated
build_windows.bat

# Or manual
pip install pyinstaller
pyinstaller face_swap_avatar.spec
```

Output: `dist/FaceSwapAvatar/FaceSwapAvatar.exe`

## Next Steps

- Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
- Check [face_swap_avatar_enhanced.py](face_swap_avatar_enhanced.py) for code
- Modify `config_default.json` for custom settings

## Need Help?

```bash
# Show all options
python face_swap_avatar_enhanced.py --help

# Use custom config
python face_swap_avatar_enhanced.py --config my_config.json

# Disable preview (faster)
python face_swap_avatar_enhanced.py --no-preview

# CPU-only mode
python face_swap_avatar_enhanced.py --no-gpu
```

**Enjoy! 🎭**
