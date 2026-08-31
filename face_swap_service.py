"""
Face Swap Avatar Service Manager
Handles background processing, virtual camera detection, and meeting detection
"""

import os
import sys
import cv2
import numpy as np
import threading
import logging
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

try:
    import insightface
    from insightface.app import FaceAnalysis
except ImportError:
    print("ERROR: insightface not installed")
    sys.exit(1)

try:
    import pyvirtualcam
    from pyvirtualcam import PixelFormat
except ImportError:
    print("ERROR: pyvirtualcam not installed")
    sys.exit(1)

# ==========================================
# Setup Logging
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('face_swap_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# Meeting Detection
# ==========================================
class MeetingDetector:
    """Detects when user is in a video meeting"""
    
    @staticmethod
    def is_in_meeting() -> bool:
        """Check if user is in a video call"""
        # Check for zoom process
        if MeetingDetector._check_process("zoom"):
            return True
        
        # Check for Teams
        if MeetingDetector._check_process("teams"):
            return True
        
        # Check for Google Meet (in browser)
        if MeetingDetector._check_process("chrome") or MeetingDetector._check_process("firefox"):
            # This is a simplification; real implementation would check window title
            return False
        
        # Check for Discord
        if MeetingDetector._check_process("discord"):
            return True
        
        return False
    
    @staticmethod
    def _check_process(process_name: str) -> bool:
        """Check if process is running"""
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                try:
                    if process_name.lower() in proc.info['name'].lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            # psutil not available, try alternative method
            if sys.platform == "win32":
                import subprocess
                try:
                    result = subprocess.run(
                        ["tasklist"],
                        capture_output=True,
                        text=True
                    )
                    return process_name.lower() in result.stdout.lower()
                except:
                    pass
        return False


# ==========================================
# Virtual Camera Manager
# ==========================================
class VirtualCameraManager:
    """Manages virtual camera output"""
    
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.camera = None
        self.is_active = False
    
    def start(self) -> bool:
        """Start virtual camera"""
        try:
            self.camera = pyvirtualcam.Camera(
                width=self.width,
                height=self.height,
                fps=self.fps,
                fmt=PixelFormat.BGR
            )
            self.is_active = True
            logger.info(f"[+] Virtual camera started: {self.width}x{self.height} @ {self.fps} FPS")
            return True
        except Exception as e:
            logger.error(f"Failed to start virtual camera: {e}")
            return False
    
    def send_frame(self, frame: np.ndarray):
        """Send frame to virtual camera"""
        if self.is_active and self.camera:
            try:
                # Ensure frame size matches
                if frame.shape[:2] != (self.height, self.width):
                    frame = cv2.resize(frame, (self.width, self.height))
                
                self.camera.send(frame)
                self.camera.sleep_until_next_frame()
            except Exception as e:
                logger.error(f"Error sending frame: {e}")
    
    def stop(self):
        """Stop virtual camera"""
        if self.camera:
            try:
                self.camera.close()
                self.is_active = False
                logger.info("[+] Virtual camera stopped")
            except Exception as e:
                logger.error(f"Error stopping camera: {e}")


# ==========================================
# Face Swap Service
# ==========================================
class FaceSwapService:
    """Main face swap processing service"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.is_running = False
        self.analyzer = None
        self.swapper = None
        self.virtual_camera = None
        self.input_camera = None
        self.frame_count = 0
        self.stats = {
            "faces_detected": 0,
            "swaps_performed": 0,
            "fps": 0
        }
    
    def initialize(self) -> bool:
        """Initialize service"""
        try:
            logger.info("[+] Initializing Face Swap Service...")
            
            # Setup providers
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if self.config.get("gpu_enabled") else ["CPUExecutionProvider"]
            
            # Initialize face analyzer
            logger.info("[+] Loading face analyzer...")
            self.analyzer = FaceAnalysis(name="buffalo_l", providers=providers)
            self.analyzer.prepare(ctx_id=0, det_size=tuple(self.config.get("detection_size", [640, 640])))
            
            # Load face swapper model
            model_path = self.config.get("model_path", "inswapper_128.onnx")
            if not os.path.exists(model_path):
                logger.error(f"[-] Model not found: {model_path}")
                return False
            
            logger.info("[+] Loading face swapper...")
            self.swapper = insightface.model_zoo.get_model(model_path, providers=providers)
            
            # Initialize virtual camera
            self.virtual_camera = VirtualCameraManager(
                width=self.config.get("width", 1920),
                height=self.config.get("height", 1080),
                fps=self.config.get("target_fps", 30)
            )
            
            if not self.virtual_camera.start():
                logger.error("[-] Failed to start virtual camera")
                return False
            
            logger.info("[+] Face Swap Service initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def start(self, camera_index: int = 0) -> bool:
        """Start processing"""
        if not self.initialize():
            return False
        
        try:
            # Open input camera
            self.input_camera = cv2.VideoCapture(camera_index)
            if not self.input_camera.isOpened():
                logger.error(f"[-] Could not open camera at index {camera_index}")
                return False
            
            logger.info(f"[+] Input camera opened: index {camera_index}")
            
            self.is_running = True
            
            # Start processing thread
            process_thread = threading.Thread(target=self._process_loop, daemon=True)
            process_thread.start()
            
            logger.info("[+] Face Swap Service started")
            return True
        
        except Exception as e:
            logger.error(f"Failed to start service: {e}")
            return False
    
    def _process_loop(self):
        """Main processing loop"""
        try:
            while self.is_running:
                ret, frame = self.input_camera.read()
                if not ret:
                    break
                
                # Process frame
                processed_frame = self._process_frame(frame)
                
                # Send to virtual camera
                self.virtual_camera.send_frame(processed_frame)
                
                self.frame_count += 1
        
        except Exception as e:
            logger.error(f"Error in processing loop: {e}")
        finally:
            self.stop()
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process a single frame"""
        try:
            # Detect faces
            faces = self.analyzer.get(frame)
            self.stats["faces_detected"] = len(faces)
            
            if faces:
                # Select largest face
                live_face = max(
                    faces,
                    key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
                )
                
                # Get target avatar face (from config)
                # In real implementation, would load from avatar folder
                # For now, return original frame
                
                # Perform swap
                # frame = self.swapper.get(frame, live_face, target_face, paste_back=True)
                self.stats["swaps_performed"] += 1
            
            return frame
        
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return frame
    
    def stop(self):
        """Stop processing"""
        self.is_running = False
        
        if self.input_camera:
            self.input_camera.release()
        
        if self.virtual_camera:
            self.virtual_camera.stop()
        
        logger.info("[+] Face Swap Service stopped")
    
    def get_stats(self) -> Dict:
        """Get service statistics"""
        return self.stats


# ==========================================
# Auto-Start Manager
# ==========================================
class AutoStartManager:
    """Manages automatic start/stop based on meeting detection"""
    
    def __init__(self, service: FaceSwapService, check_interval: int = 5):
        self.service = service
        self.check_interval = check_interval
        self.is_monitoring = False
        self.was_in_meeting = False
    
    def start_monitoring(self):
        """Start monitoring for meetings"""
        self.is_monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("[+] Auto-start monitoring enabled")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        logger.info("[+] Auto-start monitoring disabled")
    
    def _monitor_loop(self):
        """Monitor loop"""
        import time
        
        while self.is_monitoring:
            try:
                in_meeting = MeetingDetector.is_in_meeting()
                
                if in_meeting and not self.was_in_meeting:
                    logger.info("[+] Meeting detected! Auto-starting service...")
                    self.service.start()
                    self.was_in_meeting = True
                
                elif not in_meeting and self.was_in_meeting:
                    logger.info("[+] Meeting ended! Auto-stopping service...")
                    self.service.stop()
                    self.was_in_meeting = False
                
                time.sleep(self.check_interval)
            
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")


# ==========================================
# Service Controller
# ==========================================
class ServiceController:
    """Main service controller"""
    
    def __init__(self, config_path: str = "settings.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.service = FaceSwapService(self.config)
        self.auto_start = None
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        # Return defaults
        return {
            "model_path": "inswapper_128.onnx",
            "avatar_dir": "avatars",
            "camera_index": 0,
            "target_fps": 30,
            "detection_size": [640, 640],
            "pose_filter_alpha": 0.35,
            "width": 1920,
            "height": 1080,
            "gpu_enabled": True,
            "enable_preview": False,
            "auto_detect": True,
            "auto_start": True,
        }
    
    def start(self, camera_index: int = 0) -> bool:
        """Start the service"""
        if not self.service.start(camera_index):
            return False
        
        if self.config.get("auto_start"):
            self.auto_start = AutoStartManager(self.service)
            self.auto_start.start_monitoring()
        
        return True
    
    def stop(self):
        """Stop the service"""
        if self.auto_start:
            self.auto_start.stop_monitoring()
        
        self.service.stop()
    
    def get_stats(self) -> Dict:
        """Get service statistics"""
        return self.service.get_stats()


# ==========================================
# Service Entry Point (for running as daemon)
# ==========================================
if __name__ == "__main__":
    logger.info("[+] Face Swap Avatar Service started")
    
    controller = ServiceController()
    
    try:
        camera_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
        
        if controller.start(camera_index):
            logger.info("[+] Service running. Press Ctrl+C to stop...")
            
            # Keep service running
            import time
            while True:
                time.sleep(1)
        else:
            logger.error("[-] Failed to start service")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("[+] Shutdown requested")
        controller.stop()
    
    except Exception as e:
        logger.error(f"Service error: {e}")
        sys.exit(1)
