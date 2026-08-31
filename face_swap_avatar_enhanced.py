"""
Multi-View Avatar Face Swap Virtual Webcam
A real-time face swap application that works as a virtual webcam for video conferencing.

Features:
- Multi-angle avatar support with pose-aware routing
- Temporal smoothing for natural head movements
- Virtual camera integration for Zoom/Teams/Meet
- Robust error handling and logging
- Configurable settings
- Optional preview window
"""

import os
import sys
import cv2
import numpy as np
import logging
import json
import argparse
from pathlib import Path
from typing import Dict, Optional, Tuple, List

# Import required AI/CV libraries
try:
    import insightface
    from insightface.app import FaceAnalysis
except ImportError:
    print("ERROR: insightface not installed. Run: pip install insightface")
    sys.exit(1)

try:
    import pyvirtualcam
    from pyvirtualcam import PixelFormat
except ImportError:
    print("ERROR: pyvirtualcam not installed. Run: pip install pyvirtualcam")
    sys.exit(1)

# ==========================================
# Setup Logging
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('face_swap_avatar.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# Configuration Manager
# ==========================================
class Config:
    def __init__(self, config_path: Optional[str] = None):
        self.defaults = {
            "model_path": "inswapper_128.onnx",
            "avatar_dir": "avatars",
            "camera_index": 0,
            "target_fps": 30,
            "detection_size": [640, 640],
            "pose_filter_alpha": 0.35,
            "enable_preview": True,
            "gpu_enabled": True,
            "face_detection_confidence": 0.5,
            "use_largest_face": True,
            "enable_pose_smoothing": True,
        }
        
        self.config = self.defaults.copy()
        
        if config_path and os.path.exists(config_path):
            self._load_from_file(config_path)
            logger.info(f"[+] Configuration loaded from {config_path}")
        else:
            logger.info("[+] Using default configuration")
    
    def _load_from_file(self, path: str):
        try:
            with open(path, 'r') as f:
                loaded = json.load(f)
                self.config.update(loaded)
        except Exception as e:
            logger.warning(f"Failed to load config from {path}: {e}. Using defaults.")
    
    def save_template(self, path: str = "config_template.json"):
        """Save a template configuration file"""
        try:
            with open(path, 'w') as f:
                json.dump(self.defaults, f, indent=2)
            logger.info(f"[+] Config template saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save config template: {e}")
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        self.config[key] = value


# ==========================================
# Provider Detection
# ==========================================
def get_available_providers() -> List[str]:
    """Safely detect available ONNX Runtime providers"""
    providers = []
    
    try:
        import onnxruntime as ort
        available = ort.get_available_providers()
        
        # Prefer CUDA if available
        if "CUDAExecutionProvider" in available:
            providers.append("CUDAExecutionProvider")
            logger.info("[+] GPU (CUDA) provider detected")
        
        # Always include CPU as fallback
        if "CPUExecutionProvider" in available:
            providers.append("CPUExecutionProvider")
            logger.info("[+] CPU provider available")
        
        if not providers:
            providers = ["CPUExecutionProvider"]
            logger.warning("[!] No ONNX providers detected, falling back to CPU")
    
    except ImportError:
        logger.warning("[!] onnxruntime not found, using default providers")
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    
    return providers


# ==========================================
# Temporal Pose Smoothing Filter (EMA)
# ==========================================
class PoseFilter:
    """Exponential Moving Average filter for head pose smoothing"""
    
    def __init__(self, alpha: float = 0.35):
        self.alpha = alpha
        self.smoothed_pitch = None
        self.smoothed_yaw = None
        self.smoothed_roll = None
    
    def update(self, pitch: float, yaw: float, roll: float) -> Tuple[float, float, float]:
        """Apply EMA smoothing to pose angles"""
        if self.smoothed_pitch is None:
            self.smoothed_pitch = pitch
            self.smoothed_yaw = yaw
            self.smoothed_roll = roll
        else:
            self.smoothed_pitch = self.alpha * pitch + (1.0 - self.alpha) * self.smoothed_pitch
            self.smoothed_yaw = self.alpha * yaw + (1.0 - self.alpha) * self.smoothed_yaw
            self.smoothed_roll = self.alpha * roll + (1.0 - self.alpha) * self.smoothed_roll
        
        return self.smoothed_pitch, self.smoothed_yaw, self.smoothed_roll


# ==========================================
# Multi-View Avatar Bank Loader & Selector
# ==========================================
class MultiViewAvatarBank:
    """Manages multi-angle avatar references and pose-aware selection"""
    
    AVATAR_ANGLES = {
        "center": "center.jpg",
        "left_mid": "left_30.jpg",
        "left_wide": "left_45.jpg",
        "right_mid": "right_30.jpg",
        "right_wide": "right_45.jpg",
        "pitch_up": "up_20.jpg",
        "pitch_down": "down_20.jpg"
    }
    
    def __init__(self, analyzer: FaceAnalysis, avatar_dir: str):
        self.bank = {}
        self.avatar_dir = avatar_dir
        logger.info("[+] Loading multi-view avatar bank...")
        
        self._load_avatars(analyzer)
        
        if not self.bank:
            logger.error("[-] No avatar images could be loaded!")
            raise RuntimeError("Critical: Avatar bank is empty. Please verify your avatar directory.")
        
        self.default_face = self.bank.get("center", list(self.bank.values())[0])
        logger.info(f"[+] Avatar bank loaded: {len(self.bank)} angles available")
    
    def _load_avatars(self, analyzer: FaceAnalysis):
        """Load and pre-analyze all avatar images"""
        for angle_key, filename in self.AVATAR_ANGLES.items():
            path = os.path.join(self.avatar_dir, filename)
            
            if not os.path.exists(path):
                logger.warning(f"[!] Avatar not found: {path}")
                continue
            
            try:
                img = cv2.imread(path)
                if img is None:
                    logger.warning(f"[!] Could not read image: {path}")
                    continue
                
                faces = analyzer.get(img)
                if faces:
                    # Get the largest face in the image
                    face = max(
                        faces,
                        key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1])
                    )
                    self.bank[angle_key] = face
                    logger.info(f"    ✓ Loaded '{angle_key}' from {filename}")
                else:
                    logger.warning(f"[!] No face detected in: {path}")
            
            except Exception as e:
                logger.error(f"[!] Error loading avatar '{angle_key}': {e}")
    
    def get_best_avatar(self, smoothed_yaw: float, smoothed_pitch: float):
        """
        Select the best avatar angle based on head pose.
        Uses a prioritized routing based on yaw (horizontal rotation) and pitch (vertical tilt).
        """
        # Check yaw (horizontal rotation) first
        if smoothed_yaw < -38 and "left_wide" in self.bank:
            return self.bank["left_wide"]
        elif -38 <= smoothed_yaw < -15 and "left_mid" in self.bank:
            return self.bank["left_mid"]
        elif smoothed_yaw > 38 and "right_wide" in self.bank:
            return self.bank["right_wide"]
        elif 15 < smoothed_yaw <= 38 and "right_mid" in self.bank:
            return self.bank["right_mid"]
        
        # Check pitch (vertical nod) as secondary criterion
        if smoothed_pitch < -18 and "pitch_down" in self.bank:
            return self.bank["pitch_down"]
        elif smoothed_pitch > 18 and "pitch_up" in self.bank:
            return self.bank["pitch_up"]
        
        # Fallback to center/default
        return self.default_face


# ==========================================
# Live Face Detector & Swapper
# ==========================================
class LiveFaceProcessor:
    """Handles face detection and swapping in video frames"""
    
    def __init__(self, config: Config, providers: List[str]):
        self.config = config
        logger.info("[+] Initializing face analyzer...")
        
        try:
            det_size = tuple(config.get("detection_size", [640, 640]))
            self.analyzer = FaceAnalysis(name="buffalo_l", providers=providers)
            self.analyzer.prepare(ctx_id=0, det_size=det_size)
            logger.info(f"[+] Face analyzer ready (detection size: {det_size})")
        except Exception as e:
            logger.error(f"Failed to initialize FaceAnalysis: {e}")
            raise
        
        # Load face swapper model
        model_path = config.get("model_path")
        if not os.path.exists(model_path):
            logger.error(f"[-] Model not found: {model_path}")
            raise FileNotFoundError(f"Model file required: {model_path}")
        
        try:
            self.swapper = insightface.model_zoo.get_model(model_path, providers=providers)
            logger.info(f"[+] Face swapper model loaded: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load face swapper: {e}")
            raise
        
        # Load avatar bank
        avatar_dir = config.get("avatar_dir")
        if not os.path.exists(avatar_dir):
            logger.error(f"[-] Avatar directory not found: {avatar_dir}")
            raise FileNotFoundError(f"Avatar directory required: {avatar_dir}")
        
        self.avatar_bank = MultiViewAvatarBank(self.analyzer, avatar_dir)
        
        # Initialize pose smoother
        alpha = config.get("pose_filter_alpha", 0.35)
        self.pose_smoother = PoseFilter(alpha=alpha)
        
        self.frame_count = 0
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, bool, Dict]:
        """
        Process a single video frame: detect faces, swap, and return result.
        
        Returns:
            frame: Processed frame
            has_face: Whether a face was detected and swapped
            stats: Statistics about the processing
        """
        self.frame_count += 1
        stats = {"faces_detected": 0, "swap_applied": False, "yaw": 0, "pitch": 0}
        
        try:
            # Detect faces in frame
            live_faces = self.analyzer.get(frame)
            stats["faces_detected"] = len(live_faces)
            
            if not live_faces:
                return frame, False, stats
            
            # Select the largest face (most prominent)
            if self.config.get("use_largest_face", True):
                live_face = max(
                    live_faces,
                    key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
                )
            else:
                live_face = live_faces[0]
            
            # Extract head pose
            pitch, yaw, roll = live_face.pose
            
            # Apply smoothing if enabled
            if self.config.get("enable_pose_smoothing", True):
                s_pitch, s_yaw, s_roll = self.pose_smoother.update(pitch, yaw, roll)
            else:
                s_pitch, s_yaw, s_roll = pitch, yaw, roll
            
            stats["yaw"] = round(s_yaw, 1)
            stats["pitch"] = round(s_pitch, 1)
            
            # Select best avatar angle
            target_face = self.avatar_bank.get_best_avatar(s_yaw, s_pitch)
            
            # Perform face swap
            frame = self.swapper.get(frame, live_face, target_face, paste_back=True)
            stats["swap_applied"] = True
            
            # Add optional diagnostic overlay
            if self.frame_count % 30 == 0:  # Update every 30 frames
                cv2.putText(
                    frame,
                    f"Yaw: {s_yaw:.1f}° | Pitch: {s_pitch:.1f}° | Faces: {len(live_faces)}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
            
            return frame, True, stats
        
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return frame, False, stats


# ==========================================
# Virtual Webcam Manager
# ==========================================
class VirtualWebcamPipeline:
    """Manages video capture, processing, and virtual camera output"""
    
    def __init__(self, config: Config):
        self.config = config
        self.running = False
    
    def run(self):
        """Main execution loop"""
        logger.info("[+] Starting Virtual Webcam Pipeline")
        
        # Get ONNX providers
        providers = get_available_providers() if config.get("gpu_enabled", True) else ["CPUExecutionProvider"]
        
        # Initialize processor
        try:
            processor = LiveFaceProcessor(self.config, providers)
        except Exception as e:
            logger.error(f"Failed to initialize processor: {e}")
            return False
        
        # Open physical camera
        cam_index = self.config.get("camera_index", 0)
        cap = cv2.VideoCapture(cam_index)
        
        if not cap.isOpened():
            logger.error(f"[-] Could not open camera at index {cam_index}")
            return False
        
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        target_fps = self.config.get("target_fps", 30)
        
        logger.info(f"[+] Camera opened: {frame_width}x{frame_height} @ {target_fps} FPS")
        
        self.running = True
        enable_preview = self.config.get("enable_preview", True) and self._can_display()
        stats_buffer = {"avg_faces": 0, "swaps": 0}
        frame_buffer = []
        
        try:
            # Connect to virtual camera
            with pyvirtualcam.Camera(
                width=frame_width,
                height=frame_height,
                fps=target_fps,
                fmt=PixelFormat.BGR
            ) as vcam:
                logger.info(f"[+] Virtual camera active: {vcam.device}")
                logger.info("[+] Ready to use in Zoom/Teams/Google Meet")
                logger.info("[+] Press Ctrl+C to exit")
                
                while self.running:
                    ret, frame = cap.read()
                    if not ret:
                        logger.warning("[!] Failed to read frame from camera")
                        break
                    
                    # Process frame
                    processed_frame, has_face, stats = processor.process_frame(frame)
                    frame_buffer.append((processed_frame, stats))
                    
                    # Keep only last 30 frames for stats
                    if len(frame_buffer) > 30:
                        frame_buffer.pop(0)
                    
                    # Send to virtual camera
                    vcam.send(processed_frame)
                    vcam.sleep_until_next_frame()
                    
                    # Optional preview
                    if enable_preview:
                        cv2.imshow(
                            "Face Swap Avatar Virtual Webcam (Press 'q' to exit)",
                            processed_frame
                        )
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    
                    # Log stats periodically
                    if processor.frame_count % 300 == 0:
                        avg_faces = np.mean([s["faces_detected"] for _, s in frame_buffer]) if frame_buffer else 0
                        swap_ratio = sum(1 for _, s in frame_buffer if s["swap_applied"]) / len(frame_buffer) if frame_buffer else 0
                        logger.info(f"[Stats] Frames: {processor.frame_count} | Avg Faces: {avg_faces:.1f} | Swap Rate: {swap_ratio*100:.0f}%")
        
        except KeyboardInterrupt:
            logger.info("[+] Shutdown requested by user")
        except Exception as e:
            logger.error(f"Runtime error: {e}", exc_info=True)
            return False
        finally:
            self.running = False
            cap.release()
            cv2.destroyAllWindows()
            logger.info("[+] Resources cleaned up. Goodbye!")
        
        return True
    
    def _can_display(self) -> bool:
        """Check if a display is available (for preview window)"""
        if sys.platform == "linux":
            return os.environ.get("DISPLAY") is not None
        return True


# ==========================================
# Main Entry Point
# ==========================================
def main():
    parser = argparse.ArgumentParser(
        description="Multi-View Avatar Face Swap Virtual Webcam",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python face_swap_avatar_enhanced.py                    # Use defaults
  python face_swap_avatar_enhanced.py --config config.json
  python face_swap_avatar_enhanced.py --no-preview --camera 1
  python face_swap_avatar_enhanced.py --save-config config_template.json
        """
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to JSON configuration file"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="inswapper_128.onnx",
        help="Path to face swap model"
    )
    parser.add_argument(
        "--avatars",
        type=str,
        default="avatars",
        help="Path to avatar images directory"
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Camera index (default: 0)"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Target FPS (default: 30)"
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="Disable preview window"
    )
    parser.add_argument(
        "--no-gpu",
        action="store_true",
        help="Force CPU-only mode (disable GPU)"
    )
    parser.add_argument(
        "--save-config",
        type=str,
        default=None,
        help="Save default configuration template to file and exit"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config(args.config)
    
    # Override with command-line arguments
    if args.model:
        config.set("model_path", args.model)
    if args.avatars:
        config.set("avatar_dir", args.avatars)
    if args.camera is not None:
        config.set("camera_index", args.camera)
    if args.fps:
        config.set("target_fps", args.fps)
    if args.no_preview:
        config.set("enable_preview", False)
    if args.no_gpu:
        config.set("gpu_enabled", False)
    
    # Handle config save
    if args.save_config:
        config.save_template(args.save_config)
        return
    
    # Run the pipeline
    pipeline = VirtualWebcamPipeline(config)
    success = pipeline.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
