import os
import sys
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import pyvirtualcam
from pyvirtualcam import PixelFormat

# ==========================================
# 1. Configuration & Multi-View Setup
# ==========================================
SWAPPER_MODEL_PATH = "inswapper_128.onnx"
CAM_INDEX = 0
TARGET_FPS = 30
DET_SIZE = (640, 640)

# Multi-angle reference gallery for the target avatar
# Capture or render images of the avatar at these standard angles:
AVATAR_MULTI_VIEW = {
    "center": "avatars/center.jpg",       # ~0 deg
    "left_mid": "avatars/left_30.jpg",    # ~-25 to -35 deg
    "left_wide": "avatars/left_45.jpg",   # ~-40 to -60 deg
    "right_mid": "avatars/right_30.jpg",  # ~+25 to +35 deg
    "right_wide": "avatars/right_45.jpg", # ~+40 to +60 deg
    "pitch_up": "avatars/up_20.jpg",      # Head tilted up
    "pitch_down": "avatars/down_20.jpg"   # Head tilted down
}

# ==========================================
# 2. Multi-View Avatar Bank Loader & Selector
# ==========================================
class MultiViewAvatarBank:
    def __init__(self, analyzer: FaceAnalysis, avatar_paths: dict):
        self.bank = {}
        print("[+] Loading & pre-calculating embeddings for multi-view avatar bank...")
        
        for angle_key, path in avatar_paths.items():
            if not os.path.exists(path):
                print(f"[!] Warning: Path '{path}' not found for key '{angle_key}'. Skipping.")
                continue
            
            img = cv2.imread(path)
            if img is None:
                continue

            faces = analyzer.get(img)
            if faces:
                # Sort by bounding box area to get the dominant face
                faces = sorted(
                    faces, 
                    key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), 
                    reverse=True
                )
                self.bank[angle_key] = faces[0]
                print(f"    - Loaded angle '{angle_key}' successfully.")
            else:
                print(f"[!] Warning: No face detected in reference image: {path}")

        if not self.bank:
            sys.exit("[-] Critical: No avatar images could be loaded. Please verify your avatar directory.")
        
        # Fallback reference
        self.default_face = self.bank.get("center", list(self.bank.values())[0])

    def get_best_avatar(self, smoothed_yaw: float, smoothed_pitch: float):
        """
        Dynamically routes to the best avatar embedding matching the 
        live caller's 3D head rotation.
        """
        # Yaw checks (Horizontal rotation)
        if smoothed_yaw < -38 and "left_wide" in self.bank:
            return self.bank["left_wide"]
        elif -38 <= smoothed_yaw < -15 and "left_mid" in self.bank:
            return self.bank["left_mid"]
        elif smoothed_yaw > 38 and "right_wide" in self.bank:
            return self.bank["right_wide"]
        elif 15 < smoothed_yaw <= 38 and "right_mid" in self.bank:
            return self.bank["right_mid"]

        # Pitch checks (Vertical nod)
        if smoothed_pitch < -18 and "pitch_down" in self.bank:
            return self.bank["pitch_down"]
        elif smoothed_pitch > 18 and "pitch_up" in self.bank:
            return self.bank["pitch_up"]

        return self.default_face


# ==========================================
# 3. Temporal Pose Smoothing Filter (EMA)
# ==========================================
class PoseFilter:
    def __init__(self, alpha=0.35):
        self.alpha = alpha
        self.smoothed_pitch = None
        self.smoothed_yaw = None
        self.smoothed_roll = None

    def update(self, pitch, yaw, roll):
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
# 4. Main Execution Pipeline
# ==========================================
def main():
    # 1. Initialize Face Analyzer with GPU acceleration
    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    app = FaceAnalysis(name="buffalo_l", providers=providers)
    app.prepare(ctx_id=0, det_size=DET_SIZE)

    # 2. Load Face Swapper Model
    if not os.path.exists(SWAPPER_MODEL_PATH):
        sys.exit(f"[-] Error: '{SWAPPER_MODEL_PATH}' not found in working directory.")

    swapper = insightface.model_zoo.get_model(SWAPPER_MODEL_PATH, providers=providers)

    # 3. Load Multi-Angle Gallery
    avatar_bank = MultiViewAvatarBank(app, AVATAR_MULTI_VIEW)
    pose_smoother = PoseFilter(alpha=0.35)

    # 4. Open Physical Camera
    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        sys.exit(f"[-] Error: Could not access webcam at index {CAM_INDEX}")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[+] Webcam connected: {frame_width}x{frame_height} @ {TARGET_FPS} FPS")

    # 5. Connect to Virtual Camera Pipeline
    try:
        with pyvirtualcam.Camera(
            width=frame_width, 
            height=frame_height, 
            fps=TARGET_FPS, 
            fmt=PixelFormat.BGR
        ) as vcam:
            print(f"[+] Virtual camera device online: {vcam.device}")
            print("[+] Live stream running. Select this virtual camera in Zoom/Teams/Meet.")

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Detect faces on the current webcam frame
                live_faces = app.get(frame)

                if live_faces:
                    # Select largest detected face in view
                    live_face = max(
                        live_faces, 
                        key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
                    )

                    # Extract 3D head pose angles [pitch, yaw, roll]
                    pitch, yaw, roll = live_face.pose
                    s_pitch, s_yaw, s_roll = pose_smoother.update(pitch, yaw, roll)

                    # Pick the best matching 3D avatar angle
                    target_face = avatar_bank.get_best_avatar(s_yaw, s_pitch)

                    # Execute neural face swap
                    frame = swapper.get(frame, live_face, target_face, paste_back=True)

                    # Optional visual diagnostics
                    cv2.putText(
                        frame, 
                        f"Yaw: {s_yaw:.1f} | Pitch: {s_pitch:.1f}", 
                        (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, 
                        (0, 255, 0), 
                        2
                    )

                # Send frame directly into Virtual Webcam pipe
                vcam.send(frame)
                vcam.sleep_until_next_frame()

                # Local GUI preview
                cv2.imshow("Multi-Angle Live Avatar Preview (Press 'q' to exit)", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[+] Webcam and preview windows closed.")

if __name__ == "__main__":
    main()
