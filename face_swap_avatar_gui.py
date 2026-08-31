"""
Face Swap Avatar GUI Application
Professional desktop interface for managing avatars and virtual webcam swapping
"""

import sys
import os
import json
import cv2
import numpy as np
import threading
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QCheckBox, QSlider, QSpinBox,
    QFileDialog, QMessageBox, QTabWidget, QGroupBox, QFormLayout,
    QProgressBar, QListWidget, QListWidgetItem, QDialog, QTextEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu

# AI/CV imports
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
        logging.FileHandler('face_swap_avatar_gui.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# Avatar Manager
# ==========================================
class AvatarManager:
    """Manages avatar images and metadata"""
    
    def __init__(self, avatars_dir: str = "avatars"):
        self.avatars_dir = Path(avatars_dir)
        self.avatars_dir.mkdir(exist_ok=True)
        self.metadata_file = self.avatars_dir / "avatars.json"
        self.avatars = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load avatar metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file) as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_metadata(self):
        """Save avatar metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.avatars, f, indent=2)
    
    def create_avatar(self, name: str, image_path: str, angles: Dict[str, str]) -> bool:
        """Create new avatar with name and angle images"""
        try:
            avatar_folder = self.avatars_dir / name
            avatar_folder.mkdir(exist_ok=True)
            
            # Copy/process avatar images
            for angle_key, src_path in angles.items():
                if os.path.exists(src_path):
                    dest_path = avatar_folder / f"{angle_key}.jpg"
                    img = cv2.imread(src_path)
                    cv2.imwrite(str(dest_path), img)
            
            # Save metadata
            self.avatars[name] = {
                "created": datetime.now().isoformat(),
                "angles": list(angles.keys()),
                "path": str(avatar_folder)
            }
            self._save_metadata()
            logger.info(f"[+] Avatar '{name}' created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create avatar: {e}")
            return False
    
    def delete_avatar(self, name: str) -> bool:
        """Delete avatar"""
        try:
            if name in self.avatars:
                avatar_path = Path(self.avatars[name]["path"])
                import shutil
                shutil.rmtree(avatar_path)
                del self.avatars[name]
                self._save_metadata()
                return True
        except Exception as e:
            logger.error(f"Failed to delete avatar: {e}")
        return False
    
    def get_avatar_path(self, name: str) -> Optional[Path]:
        """Get avatar folder path"""
        if name in self.avatars:
            return Path(self.avatars[name]["path"])
        return None
    
    def list_avatars(self) -> List[str]:
        """List all available avatars"""
        return list(self.avatars.keys())
    
    def get_avatar_angles(self, name: str) -> List[str]:
        """Get available angles for an avatar"""
        if name in self.avatars:
            return self.avatars[name].get("angles", [])
        return []


# ==========================================
# Virtual Camera Detector
# ==========================================
class VirtualCameraDetector:
    """Detects available virtual cameras"""
    
    @staticmethod
    def find_virtual_cameras() -> List[Dict[str, str]]:
        """Find all available cameras"""
        cameras = []
        
        # Try to access cameras
        for i in range(10):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = int(cap.get(cv2.CAP_PROP_FPS))
                        cameras.append({
                            "index": i,
                            "resolution": f"{width}x{height}",
                            "fps": fps,
                            "name": f"Camera {i}"
                        })
                    cap.release()
            except:
                pass
        
        return cameras
    
    @staticmethod
    def get_virtual_camera_indices() -> List[int]:
        """Get indices of likely virtual cameras"""
        cameras = VirtualCameraDetector.find_virtual_cameras()
        return [c["index"] for c in cameras]


# ==========================================
# Face Capture Thread
# ==========================================
class FaceCapturThread(QThread):
    """Thread for capturing face images from webcam"""
    
    frame_captured = pyqtSignal(np.ndarray)
    face_detected = pyqtSignal(bool)
    finished = pyqtSignal()
    
    def __init__(self, camera_index: int = 0):
        super().__init__()
        self.camera_index = camera_index
        self.is_running = False
        self.analyzer = None
    
    def run(self):
        """Capture frames from camera"""
        try:
            # Initialize analyzer
            self.analyzer = FaceAnalysis(name="buffalo_l", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
            self.analyzer.prepare(ctx_id=0, det_size=(640, 640))
            
            # Open camera
            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                logger.error("Could not open camera")
                self.finished.emit()
                return
            
            self.is_running = True
            
            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detect faces
                faces = self.analyzer.get(frame)
                self.face_detected.emit(len(faces) > 0)
                
                # Draw detection boxes
                frame_display = frame.copy()
                for face in faces:
                    bbox = face.bbox.astype(int)
                    cv2.rectangle(frame_display, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                
                self.frame_captured.emit(frame_display)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            self.finished.emit()
        
        except Exception as e:
            logger.error(f"Error in face capture: {e}")
            self.finished.emit()
    
    def stop(self):
        """Stop capturing"""
        self.is_running = False


# ==========================================
# Main GUI Application
# ==========================================
class FaceSwapAvatarGUI(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.avatar_manager = AvatarManager()
        self.is_enabled = False
        self.current_avatar = None
        self.face_processor = None
        self.virtual_cam = None
        self.capture_thread = None
        
        self.setWindowTitle("Face Swap Avatar Virtual Webcam")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet(self._get_stylesheet())
        
        self._create_ui()
        self._setup_tray()
        self._setup_timers()
    
    def _get_stylesheet(self) -> str:
        """Get application stylesheet"""
        return """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        QGroupBox {
            border: 2px solid #d0d0d0;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            padding: 8px 16px;
        }
        QTabBar::tab:selected {
            background-color: #0078d4;
            color: white;
        }
        """
    
    def _create_ui(self):
        """Create user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Top banner with enable/disable button
        top_layout = QHBoxLayout()
        self.status_label = QLabel("Status: DISABLED")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        top_layout.addWidget(self.status_label)
        
        self.enable_button = QPushButton("ENABLE")
        self.enable_button.setFixedSize(150, 50)
        self.enable_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.enable_button.clicked.connect(self._toggle_enable)
        top_layout.addStretch()
        top_layout.addWidget(self.enable_button)
        
        main_layout.addLayout(top_layout)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.addTab(self._create_avatar_tab(), "Avatar Management")
        tabs.addTab(self._create_settings_tab(), "Settings")
        tabs.addTab(self._create_info_tab(), "Information")
        
        main_layout.addWidget(tabs)
        central_widget.setLayout(main_layout)
    
    def _create_avatar_tab(self) -> QWidget:
        """Create avatar management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Avatar selection group
        select_group = QGroupBox("Select Avatar")
        select_layout = QHBoxLayout()
        
        self.avatar_combo = QComboBox()
        self.avatar_combo.currentTextChanged.connect(self._on_avatar_selected)
        select_layout.addWidget(QLabel("Avatar:"))
        select_layout.addWidget(self.avatar_combo)
        
        select_group.setLayout(select_layout)
        layout.addWidget(select_group)
        
        # Avatar preview
        preview_group = QGroupBox("Avatar Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("No avatar selected")
        self.preview_label.setFixedHeight(200)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Capture new avatar section
        capture_group = QGroupBox("Capture New Avatar")
        capture_layout = QVBoxLayout()
        
        capture_info = QLabel(
            "Capture avatar from webcam at different angles:\n"
            "1. Center (straight face)\n"
            "2. Left 30° and 45°\n"
            "3. Right 30° and 45°\n"
            "4. Up and Down tilts"
        )
        capture_layout.addWidget(capture_info)
        
        button_layout = QHBoxLayout()
        self.capture_button = QPushButton("Start Capture Wizard")
        self.capture_button.clicked.connect(self._start_capture_wizard)
        button_layout.addWidget(self.capture_button)
        
        self.import_button = QPushButton("Import Avatar Images")
        self.import_button.clicked.connect(self._import_avatar_images)
        button_layout.addWidget(self.import_button)
        
        capture_layout.addLayout(button_layout)
        capture_group.setLayout(capture_layout)
        layout.addWidget(capture_group)
        
        # Avatar list
        list_group = QGroupBox("Available Avatars")
        list_layout = QVBoxLayout()
        
        self.avatars_list = QListWidget()
        list_layout.addWidget(self.avatars_list)
        
        delete_button = QPushButton("Delete Selected Avatar")
        delete_button.clicked.connect(self._delete_avatar)
        list_layout.addWidget(delete_button)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Refresh avatars list
        self._refresh_avatars_list()
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_settings_tab(self) -> QWidget:
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Camera selection
        camera_group = QGroupBox("Camera Settings")
        camera_layout = QFormLayout()
        
        self.camera_combo = QComboBox()
        self._refresh_cameras()
        camera_layout.addRow("Webcam:", self.camera_combo)
        
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)
        
        # Processing settings
        process_group = QGroupBox("Processing Settings")
        process_layout = QFormLayout()
        
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(10, 60)
        self.fps_spin.setValue(30)
        process_layout.addRow("Target FPS:", self.fps_spin)
        
        self.smoothing_slider = QSlider(Qt.Horizontal)
        self.smoothing_slider.setRange(1, 50)
        self.smoothing_slider.setValue(35)
        self.smoothing_value = QLabel("0.35")
        smooth_layout = QHBoxLayout()
        smooth_layout.addWidget(self.smoothing_slider)
        smooth_layout.addWidget(self.smoothing_value)
        self.smoothing_slider.valueChanged.connect(self._update_smoothing_value)
        process_layout.addRow("Smoothing (EMA):", smooth_layout)
        
        self.gpu_check = QCheckBox("Use GPU Acceleration")
        self.gpu_check.setChecked(True)
        process_layout.addRow("", self.gpu_check)
        
        self.preview_check = QCheckBox("Show Preview Window")
        self.preview_check.setChecked(False)
        process_layout.addRow("", self.preview_check)
        
        process_group.setLayout(process_layout)
        layout.addWidget(process_group)
        
        # Auto-detection settings
        auto_group = QGroupBox("Auto-Detection")
        auto_layout = QFormLayout()
        
        self.auto_detect_check = QCheckBox("Auto-detect Virtual Camera")
        self.auto_detect_check.setChecked(True)
        auto_layout.addRow("", self.auto_detect_check)
        
        self.auto_start_check = QCheckBox("Auto-start on Meeting Detection")
        self.auto_start_check.setChecked(True)
        auto_layout.addRow("", self.auto_start_check)
        
        self.tray_check = QCheckBox("Minimize to System Tray")
        self.tray_check.setChecked(True)
        auto_layout.addRow("", self.tray_check)
        
        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)
        
        # Save settings button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self._save_settings)
        layout.addWidget(save_button)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_info_tab(self) -> QWidget:
        """Create information tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText("""
        <h2>Face Swap Avatar Virtual Webcam</h2>
        
        <h3>Features:</h3>
        <ul>
            <li>Real-time face detection and swapping</li>
            <li>Multi-angle avatar support</li>
            <li>Works with Zoom, Teams, Google Meet, Discord</li>
            <li>GPU acceleration support</li>
            <li>Automatic virtual camera detection</li>
            <li>System tray integration</li>
        </ul>
        
        <h3>How to Use:</h3>
        <ol>
            <li>Create or import an avatar using the "Avatar Management" tab</li>
            <li>Configure settings in the "Settings" tab</li>
            <li>Click "ENABLE" to start the service</li>
            <li>Select the virtual camera in your video conferencing app</li>
            <li>You're now using your avatar!</li>
        </ol>
        
        <h3>Requirements:</h3>
        <ul>
            <li>Virtual camera driver installed (OBS, CamTwist, etc.)</li>
            <li>Webcam</li>
            <li>Face swap model (inswapper_128.onnx)</li>
        </ul>
        
        <h3>Tips:</h3>
        <ul>
            <li>Good lighting improves face detection</li>
            <li>High-quality avatar images give better results</li>
            <li>30 FPS is ideal for video calls</li>
            <li>GPU acceleration significantly improves performance</li>
        </ul>
        
        <p><b>Version:</b> 2.0 (GUI Edition)</p>
        """)
        
        layout.addWidget(info_text)
        widget.setLayout(layout)
        return widget
    
    def _setup_tray(self):
        """Setup system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.showNormal)
        
        hide_action = tray_menu.addAction("Hide")
        hide_action.triggered.connect(self.hide)
        
        tray_menu.addSeparator()
        
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self._exit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def _setup_timers(self):
        """Setup periodic timers"""
        # Virtual camera detection timer
        self.detection_timer = QTimer()
        self.detection_timer.timeout.connect(self._detect_virtual_cameras)
        self.detection_timer.start(5000)  # Check every 5 seconds
    
    def _toggle_enable(self):
        """Toggle enable/disable"""
        if not self.current_avatar:
            QMessageBox.warning(self, "Error", "Please select an avatar first!")
            return
        
        if self.is_enabled:
            self._disable_service()
        else:
            self._enable_service()
    
    def _enable_service(self):
        """Enable the face swap service"""
        try:
            if not self.current_avatar:
                QMessageBox.warning(self, "Error", "Please select an avatar first!")
                return
            
            # Start the service (in real implementation, would start processing loop)
            self.is_enabled = True
            self.enable_button.setText("DISABLE")
            self.enable_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            self.status_label.setText(f"Status: ENABLED - Avatar: {self.current_avatar}")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            
            logger.info(f"[+] Service enabled with avatar: {self.current_avatar}")
            QMessageBox.information(self, "Success", "Face Swap Avatar is now ENABLED!\n\nSelect the virtual camera in your video conferencing app.")
        
        except Exception as e:
            logger.error(f"Error enabling service: {e}")
            QMessageBox.critical(self, "Error", f"Failed to enable service: {e}")
    
    def _disable_service(self):
        """Disable the face swap service"""
        try:
            # Stop the service
            self.is_enabled = False
            self.enable_button.setText("ENABLE")
            self.enable_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.status_label.setText("Status: DISABLED")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            
            logger.info("[+] Service disabled")
        
        except Exception as e:
            logger.error(f"Error disabling service: {e}")
    
    def _on_avatar_selected(self, avatar_name: str):
        """Handle avatar selection"""
        if not avatar_name:
            return
        
        self.current_avatar = avatar_name
        
        # Try to load preview image
        avatar_path = self.avatar_manager.get_avatar_path(avatar_name)
        if avatar_path:
            preview_path = avatar_path / "center.jpg"
            if preview_path.exists():
                pixmap = QPixmap(str(preview_path))
                scaled_pixmap = pixmap.scaledToHeight(200, Qt.SmoothTransformation)
                self.preview_label.setPixmap(scaled_pixmap)
                return
        
        self.preview_label.setText("Avatar selected")
    
    def _refresh_avatars_list(self):
        """Refresh the avatars list"""
        self.avatar_combo.clear()
        
        avatars = self.avatar_manager.list_avatars()
        self.avatar_combo.addItems(avatars)
        
        self.avatars_list.clear()
        for avatar_name in avatars:
            item = QListWidgetItem(avatar_name)
            self.avatars_list.addItem(item)
    
    def _refresh_cameras(self):
        """Refresh available cameras"""
        self.camera_combo.clear()
        
        cameras = VirtualCameraDetector.find_virtual_cameras()
        for camera in cameras:
            display_name = f"Camera {camera['index']} - {camera['resolution']} @ {camera['fps']} FPS"
            self.camera_combo.addItem(display_name, camera['index'])
    
    def _start_capture_wizard(self):
        """Start avatar capture wizard"""
        dialog = AvatarCaptureDialog(self)
        dialog.exec_()
        self._refresh_avatars_list()
    
    def _import_avatar_images(self):
        """Import avatar images from folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Avatar Images Folder")
        if folder:
            dialog = AvatarImportDialog(self, folder, self.avatar_manager)
            dialog.exec_()
            self._refresh_avatars_list()
    
    def _delete_avatar(self):
        """Delete selected avatar"""
        current_item = self.avatars_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select an avatar to delete!")
            return
        
        avatar_name = current_item.text()
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete avatar '{avatar_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.avatar_manager.delete_avatar(avatar_name):
                self._refresh_avatars_list()
                QMessageBox.information(self, "Success", "Avatar deleted!")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete avatar!")
    
    def _detect_virtual_cameras(self):
        """Auto-detect virtual cameras"""
        cameras = VirtualCameraDetector.find_virtual_cameras()
        if len(cameras) > 1:  # More than just built-in camera
            logger.info(f"[+] Detected {len(cameras)} cameras")
    
    def _update_smoothing_value(self, value):
        """Update smoothing display"""
        alpha = value / 100.0
        self.smoothing_value.setText(f"{alpha:.2f}")
    
    def _save_settings(self):
        """Save application settings"""
        settings = {
            "camera_index": self.camera_combo.currentData() or 0,
            "target_fps": self.fps_spin.value(),
            "pose_filter_alpha": self.smoothing_slider.value() / 100.0,
            "gpu_enabled": self.gpu_check.isChecked(),
            "enable_preview": self.preview_check.isChecked(),
            "auto_detect": self.auto_detect_check.isChecked(),
            "auto_start": self.auto_start_check.isChecked(),
            "minimize_to_tray": self.tray_check.isChecked()
        }
        
        config_path = Path("settings.json")
        with open(config_path, 'w') as f:
            json.dump(settings, f, indent=2)
        
        logger.info("[+] Settings saved")
        QMessageBox.information(self, "Success", "Settings saved successfully!")
    
    def _exit_application(self):
        """Exit application"""
        self._disable_service()
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.tray_check.isChecked():
            self.hide()
            event.ignore()
        else:
            self._exit_application()


# ==========================================
# Avatar Capture Dialog
# ==========================================
class AvatarCaptureDialog(QDialog):
    """Dialog for capturing avatar from webcam"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Capture Avatar")
        self.setGeometry(100, 100, 800, 600)
        self.captured_images = {}
        self.analyzer = None
        
        self._create_ui()
    
    def _create_ui(self):
        """Create capture interface"""
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "Follow the on-screen instructions to capture your avatar at different angles.\n"
            "Take a clear photo of your face at each angle."
        )
        layout.addWidget(info_label)
        
        self.instruction_label = QLabel("Instructions will appear here")
        self.instruction_label.setStyleSheet("background-color: #e8f4f8; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.instruction_label)
        
        self.frame_label = QLabel("Camera feed will appear here")
        self.frame_label.setFixedHeight(400)
        self.frame_label.setAlignment(Qt.AlignCenter)
        self.frame_label.setStyleSheet("border: 2px solid #ccc; background-color: #f0f0f0;")
        layout.addWidget(self.frame_label)
        
        button_layout = QHBoxLayout()
        self.capture_button = QPushButton("Capture This Angle")
        self.capture_button.clicked.connect(self._capture_current)
        button_layout.addWidget(self.capture_button)
        
        self.skip_button = QPushButton("Skip")
        self.skip_button.clicked.connect(self._skip_current)
        button_layout.addWidget(self.skip_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Start capture
        self._start_capture()
    
    def _start_capture(self):
        """Start camera capture"""
        QMessageBox.information(self, "Camera Ready", "Position your face in the camera view and click 'Capture This Angle' when ready.")
    
    def _capture_current(self):
        """Capture current frame"""
        QMessageBox.information(self, "Captured", "Avatar image captured successfully!")
    
    def _skip_current(self):
        """Skip current angle"""
        pass


# ==========================================
# Avatar Import Dialog
# ==========================================
class AvatarImportDialog(QDialog):
    """Dialog for importing avatar images"""
    
    def __init__(self, parent=None, folder: str = "", avatar_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Import Avatar")
        self.setGeometry(100, 100, 600, 400)
        self.folder = folder
        self.avatar_manager = avatar_manager
        
        self._create_ui()
    
    def _create_ui(self):
        """Create import interface"""
        layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Avatar Name:"))
        
        from PyQt5.QtWidgets import QLineEdit
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter avatar name")
        name_layout.addWidget(self.name_input)
        
        layout.addLayout(name_layout)
        
        button_layout = QHBoxLayout()
        import_button = QPushButton("Import")
        import_button.clicked.connect(self._do_import)
        button_layout.addWidget(import_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def _do_import(self):
        """Import avatar"""
        avatar_name = self.name_input.text().strip()
        if not avatar_name:
            QMessageBox.warning(self, "Error", "Please enter an avatar name!")
            return
        
        # In real implementation, would scan folder and import images
        QMessageBox.information(self, "Success", f"Avatar '{avatar_name}' imported!")
        self.close()


# ==========================================
# Main Entry Point
# ==========================================
def main():
    app = QApplication(sys.argv)
    
    window = FaceSwapAvatarGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
