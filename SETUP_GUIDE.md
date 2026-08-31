# Face Swap Avatar Virtual Webcam 🎭

A real-time face-swapping application that works as a virtual webcam for video conferencing apps like Zoom, Google Meet, Microsoft Teams, and more.

## Features ✨

- **Multi-Angle Avatar Support**: Use different avatar images based on head rotation (yaw, pitch)
- **Pose-Aware Routing**: Automatically selects the best avatar angle to match the user's head position
- **Temporal Smoothing**: Exponential Moving Average filter for natural, jitter-free head movements
- **Virtual Webcam Integration**: Works seamlessly with Zoom, Google Meet, Teams, Discord, etc.
- **GPU Acceleration**: CUDA support for fast processing (falls back to CPU)
- **Configurable Settings**: JSON configuration system for customization
- **Live Preview**: Optional preview window to see the output in real-time
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Cross-Platform**: Runs on Windows, Linux, and macOS

## System Requirements 📋

### Minimum Specifications
- **OS**: Windows 10+, Linux (Ubuntu 18.04+), or macOS 10.14+
- **CPU**: Intel i5/AMD Ryzen 5 (or equivalent)
- **RAM**: 8 GB minimum, 16 GB recommended
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Webcam**: Standard USB webcam or built-in camera

### Software Requirements
- Python 3.9+
- pip package manager
- Virtual camera driver (see platform-specific setup)

## Installation 🚀

### Step 1: Clone or Download
```bash
git clone <repository-url>
cd build_environment
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Download Required Models

#### Face Swap Model
Download `inswapper_128.onnx` from InsightFace Model Zoo:
1. Visit: https://github.com/insightface/insightface/releases
2. Download the model file
3. Place it in the project root directory

#### Avatar Images
Create an `avatars/` folder with 7 images (at least 640x640 resolution):
```
avatars/
├── center.jpg       # Face looking straight (~0°)
├── left_30.jpg      # Head turned left (~-25 to -35°)
├── left_45.jpg      # Head turned more left (~-40 to -60°)
├── right_30.jpg     # Head turned right (~25 to 35°)
├── right_45.jpg     # Head turned more right (~40 to 60°)
├── up_20.jpg        # Head tilted up (~20°)
└── down_20.jpg      # Head tilted down (~-20°)
```

**Tips for Avatar Images:**
- Use consistent lighting and background
- Ensure faces fill ~70% of the frame
- Keep expressions neutral or consistent
- All images should be high quality (no blurriness)
- 640x640 or higher resolution recommended

### Step 4: Platform-Specific Virtual Camera Setup

#### Windows
1. Install **OBS Studio** (free): https://obsproject.com
2. In OBS, go to Tools → VirtualCam and click "Start Virtual Camera"
3. Or install **VB-Cable** or **VirtualCam** drivers

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install v4l2loopback-dkms
sudo modprobe v4l2loopback
```

#### macOS
Install **CamTwist** or **Snap Camera** from their official websites

## Usage 🎬

### Quick Start
```bash
python face_swap_avatar_enhanced.py
```

### With Configuration File
```bash
python face_swap_avatar_enhanced.py --config config.json
```

### Command Line Options
```bash
python face_swap_avatar_enhanced.py --help

Options:
  --config FILE        Path to JSON configuration file
  --model PATH         Path to face swap model (default: inswapper_128.onnx)
  --avatars PATH       Path to avatars directory (default: avatars)
  --camera INDEX       Camera index to use (default: 0)
  --fps N              Target FPS (default: 30)
  --no-preview         Disable preview window
  --no-gpu             Force CPU-only mode
  --save-config FILE   Save default config template
```

### Example Usage
```bash
# Generate a config template
python face_swap_avatar_enhanced.py --save-config my_config.json

# Run with custom settings
python face_swap_avatar_enhanced.py --camera 0 --fps 30 --no-preview

# CPU-only mode (if GPU causes issues)
python face_swap_avatar_enhanced.py --no-gpu
```

## Configuration 📝

Create a `config.json` file to customize settings:

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
  "face_detection_confidence": 0.5,
  "use_largest_face": true,
  "enable_pose_smoothing": true
}
```

### Configuration Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_path` | string | `inswapper_128.onnx` | Path to face swap model |
| `avatar_dir` | string | `avatars` | Directory containing avatar images |
| `camera_index` | int | `0` | Webcam index (0 = default camera) |
| `target_fps` | int | `30` | Target frames per second |
| `detection_size` | [int, int] | `[640, 640]` | Face detection resolution |
| `pose_filter_alpha` | float | `0.35` | Smoothing strength (0-1, higher = smoother) |
| `enable_preview` | bool | `true` | Show preview window |
| `gpu_enabled` | bool | `true` | Use GPU if available |
| `enable_pose_smoothing` | bool | `true` | Apply temporal smoothing to head pose |

## Building as .exe (Windows) 🔨

### Method 1: Automated Build Script
```bash
build_windows.bat
```

### Method 2: Manual Build
```bash
pip install pyinstaller
pyinstaller face_swap_avatar.spec
```

The executable will be created in `dist/FaceSwapAvatar/FaceSwapAvatar.exe`

### Distributing the Application
1. Copy the entire `dist/FaceSwapAvatar/` folder
2. Include the `avatars/` folder with your avatar images
3. Include the `inswapper_128.onnx` model file
4. Include `config_default.json` for reference
5. Create a shortcuts/batch file to launch

Example folder structure:
```
FaceSwapAvatar/
├── FaceSwapAvatar.exe
├── avatars/
│   ├── center.jpg
│   ├── left_30.jpg
│   └── ...
├── inswapper_128.onnx
└── config.json
```

## Using with Video Conferencing Apps 💻

### Zoom
1. Start the Face Swap Avatar application
2. Open Zoom
3. Go to Settings → Video → Camera
4. Select the virtual camera output

### Google Meet
1. Start the Face Swap Avatar application
2. Go to meet.google.com
3. Click camera icon → Select virtual camera

### Microsoft Teams
1. Start the Face Swap Avatar application
2. Open Microsoft Teams
3. Settings → Devices → Audio devices
4. Camera → Select virtual camera

### OBS Studio (for streaming)
1. Start the Face Swap Avatar application
2. In OBS, add Video Capture Device as source
3. Select the virtual camera
4. Use in your streaming setup

## Troubleshooting 🔧

### No face detected
- Ensure good lighting
- Position face fully in frame
- Make sure avatar images have clear faces
- Check camera is working with other apps

### Virtual camera not appearing
- Ensure virtual camera driver is installed
- Restart the application
- Restart the conferencing app
- Check if virtual camera needs to be enabled in settings

### Low performance / High CPU usage
- Reduce `detection_size` to `[480, 480]`
- Reduce `target_fps` to 15-20
- Enable `--no-preview` to reduce overhead
- Use `--no-gpu` to switch to CPU (may be faster on some systems)

### GPU issues
- Ensure NVIDIA drivers are up to date
- Try `--no-gpu` to force CPU mode
- Check that CUDA toolkit is compatible

### Avatar mismatch
- Ensure all 7 avatar images are present
- Check image file names match exactly
- Verify images have clear faces
- Ensure faces are roughly same size in all images

## Performance Tips ⚡

1. **Lighting**: Use well-lit environments for better detection
2. **Camera Quality**: Use higher resolution cameras (720p+)
3. **Avatar Quality**: High-quality avatar images improve results
4. **Frame Rate**: 25-30 FPS is usually sufficient for video calls
5. **GPU**: If available, using GPU significantly improves performance
6. **Smoothing**: Increase `pose_filter_alpha` (0.35-0.5) for smoother but slower tracking

## Advanced Features 🎯

### Pose Filtering
The application uses Exponential Moving Average (EMA) smoothing to reduce jitter:
- **Alpha = 0.2**: Smoother but slower response (lag)
- **Alpha = 0.35**: Balanced smoothing (recommended)
- **Alpha = 0.5**: Faster response but more jitter

### Avatar Selection Algorithm
The application intelligently routes to the best avatar based on:
1. Yaw (horizontal rotation): -60° to +60°
2. Pitch (vertical nod): -20° to +20°
3. Fallback to center/default when needed

### Multi-Processing (Advanced)
For maximum performance, you can run the application in the background and use OBS for additional effects.

## Logs and Debugging 📊

Logs are saved to `face_swap_avatar.log`. Check this file for:
- Initialization status
- Face detection statistics
- Performance metrics
- Error messages

View in real-time:
```bash
# Linux/Mac
tail -f face_swap_avatar.log

# Windows (PowerShell)
Get-Content face_swap_avatar.log -Wait
```

## API / Integration 🔌

If you want to integrate this into other applications:

```python
from face_swap_avatar_enhanced import Config, LiveFaceProcessor, get_available_providers
import cv2

# Initialize
config = Config()
providers = get_available_providers()
processor = LiveFaceProcessor(config, providers)

# Process frames
frame = cv2.imread("image.jpg")
processed_frame, has_face, stats = processor.process_frame(frame)
```

## Licensing & Credits 📜

This project uses:
- **InsightFace**: Face detection and embedding (by Dlib team)
- **OpenCV**: Computer vision library
- **ONNX Runtime**: Neural network inference
- **PyVirtualCam**: Virtual camera integration

## Frequently Asked Questions ❓

**Q: Is this real-time?**
A: Yes, it runs at ~25-30 FPS on modern hardware.

**Q: Does it work with multiple people?**
A: Currently detects and processes one face at a time (the largest in frame).

**Q: Can I use my own avatar?**
A: Yes, as long as you create the 7 pose variations and place them in the avatars folder.

**Q: Does it require internet?**
A: No, everything runs locally on your machine.

**Q: Can I use this for streaming?**
A: Yes, integrate with OBS or other streaming software.

**Q: Will this work on Mac?**
A: Yes, with appropriate virtual camera setup (CamTwist, etc.).

## Support & Issues 💬

For issues, questions, or feature requests, please create an issue on the GitHub repository.

## Disclaimer ⚠️

This software is provided for educational and entertainment purposes. Ensure you have proper consent from all parties before using face-swapping technology. Follow your platform's terms of service when using virtual cameras in video calls.

---

**Happy face-swapping! 🎭**
