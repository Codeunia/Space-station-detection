import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTextEdit, QGroupBox, QGridLayout, QSlider)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor
from ultralytics import YOLO
import os
import json
from datetime import datetime

# Equipment class names (order must match training)
CLASS_NAMES = ["FireExtinguisher", "ToolBox", "OxygenTank"]

class DetectionThread(QThread):
    """Thread for running YOLOv8 detection"""
    detection_signal = pyqtSignal(list, np.ndarray)
    alert_signal = pyqtSignal(str, str)
    
    def __init__(self, model_path):
        super().__init__()
        self.model = YOLO(model_path)
        self.running = False
        self.frame = None
        
    def run(self):
        self.running = True
        while self.running:
            if self.frame is not None:
                results = self.model(self.frame, conf=0.5)
                detections = []
                
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            conf = box.conf[0].cpu().numpy()
                            cls = int(box.cls[0].cpu().numpy())
                            class_name = result.names[cls]
                            
                            detections.append({
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'confidence': float(conf),
                                'class': class_name,
                                'class_id': cls
                            })
                
                self.detection_signal.emit(detections, self.frame.copy())
            
            self.msleep(100)  # 10 FPS
    
    def stop(self):
        self.running = False
    
    def update_frame(self, frame):
        self.frame = frame

class SpaceStationScanner(QMainWindow):
    """Main application window for Space Station Object Detection"""
    
    def __init__(self):
        super().__init__()
        # Get the absolute path to the original model file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        self.model_path = os.path.join(project_root, "runs", "detect", "train", "weights", "best.pt")
        self.conf_threshold = 0.5
        self.detection_thread = None
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # Equipment status tracking
        self.equipment_status = {
            'FireExtinguisher': {'detected': False, 'last_seen': None, 'location': None},
            'ToolBox': {'detected': False, 'last_seen': None, 'location': None},
            'OxygenTank': {'detected': False, 'last_seen': None, 'location': None}
        }
        
        self.init_ui()
        self.load_model()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Space Station Safety Scanner")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set dark theme
        self.set_dark_theme()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Video feed and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Video display
        self.video_label = QLabel("No video feed")
        self.video_label.setMinimumSize(800, 600)
        self.video_label.setStyleSheet("border: 2px solid #444; background-color: #1a1a1a;")
        self.video_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.video_label)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.camera_btn = QPushButton("Start Camera")
        self.camera_btn.clicked.connect(self.toggle_camera)
        self.camera_btn.setStyleSheet(self.get_button_style())
        
        self.upload_btn = QPushButton("Upload Image")
        self.upload_btn.clicked.connect(self.upload_image)
        self.upload_btn.setStyleSheet(self.get_button_style())
        
        self.screenshot_btn = QPushButton("Take Screenshot")
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        self.screenshot_btn.setStyleSheet(self.get_button_style())
        
        control_layout.addWidget(self.camera_btn)
        control_layout.addWidget(self.upload_btn)
        control_layout.addWidget(self.screenshot_btn)
        left_layout.addLayout(control_layout)
        
        main_layout.addWidget(left_panel)
        
        # Right panel - Status and alerts
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Equipment status
        status_group = QGroupBox("Equipment Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; color: white; }")
        status_layout = QGridLayout(status_group)
        
        self.status_labels = {}
        row = 0
        for equipment in self.equipment_status.keys():
            # Equipment name
            name_label = QLabel(equipment)
            name_label.setStyleSheet("color: #00ff00; font-weight: bold;")
            status_layout.addWidget(name_label, row, 0)
            
            # Status indicator
            status_label = QLabel("❌ Not Detected")
            status_label.setStyleSheet("color: #ff4444; font-weight: bold;")
            self.status_labels[equipment] = status_label
            status_layout.addWidget(status_label, row, 1)
            
            row += 1
        
        right_layout.addWidget(status_group)
        
        # Detection settings
        settings_group = QGroupBox("Detection Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; color: white; }")
        settings_layout = QVBoxLayout(settings_group)
        
        # Confidence threshold
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(QLabel("Confidence:"))
        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setRange(10, 100)
        self.conf_slider.setValue(50)
        self.conf_slider.setStyleSheet("QSlider::groove:horizontal { background: #444; }")
        conf_layout.addWidget(self.conf_slider)
        self.conf_label = QLabel("50%")
        self.conf_slider.valueChanged.connect(lambda v: self.conf_label.setText(f"{v}%"))
        conf_layout.addWidget(self.conf_label)
        settings_layout.addLayout(conf_layout)
        
        right_layout.addWidget(settings_group)
        
        # Alert log
        alert_group = QGroupBox("Alert Log")
        alert_group.setStyleSheet("QGroupBox { font-weight: bold; color: white; }")
        alert_layout = QVBoxLayout(alert_group)
        
        self.alert_log = QTextEdit()
        self.alert_log.setMaximumHeight(200)
        self.alert_log.setStyleSheet("background-color: #1a1a1a; color: #ffffff; border: 1px solid #444;")
        alert_layout.addWidget(self.alert_log)
        
        right_layout.addWidget(alert_group)
        
        # System info
        info_group = QGroupBox("System Information")
        info_group.setStyleSheet("QGroupBox { font-weight: bold; color: white; }")
        info_layout = QVBoxLayout(info_group)
        
        self.info_label = QLabel("Model: YOLOv8s\nStatus: Ready")
        self.info_label.setStyleSheet("color: #cccccc;")
        info_layout.addWidget(self.info_label)
        
        right_layout.addWidget(info_group)
        
        self.add_ota_update_button(right_layout)
        
        main_layout.addWidget(right_panel)
        
    def set_dark_theme(self):
        """Apply dark theme to the application"""
        self.setStyleSheet("""
            QMainWindow { background-color: #181818; }
            QLabel, QTextEdit, QGroupBox { color: #f0f0f0; font-size: 16px; }
            QPushButton { background-color: #222; color: #fff; border-radius: 6px; padding: 8px 16px; }
            QPushButton:hover { background-color: #444; }
            QSlider::groove:horizontal { background: #444; height: 8px; }
            QSlider::handle:horizontal { background: #00bfff; width: 18px; border-radius: 9px; }
        """)
        
    def load_model(self):
        """Load the trained YOLOv8 model"""
        try:
            if os.path.exists(self.model_path):
                self.detection_thread = DetectionThread(self.model_path)
                self.detection_thread.detection_signal.connect(self.process_detections)
                self.detection_thread.alert_signal.connect(self.add_alert)
                self.detection_thread.start()
                self.alert_log.append(f"<b>{datetime.now().strftime('%H:%M:%S')}</b>: Model loaded successfully.")
            else:
                self.alert_log.append("<span style='color:red'>Error: Model file not found. Please train the model first.</span>")
        except Exception as e:
            self.alert_log.append(f"<span style='color:red'>Error: Failed to load model: {str(e)}</span>")
            
    def toggle_camera(self):
        """Toggle camera on/off"""
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.alert_log.append("<span style='color:red'>Error: Cannot open camera.</span>")
                self.camera = None
                return
            self.timer.start(30)
            self.camera_btn.setEnabled(False)
            self.upload_btn.setEnabled(False)
            self.screenshot_btn.setEnabled(False)
            self.alert_log.append(f"<b>{datetime.now().strftime('%H:%M:%S')}</b>: Camera started.")
        else:
            self.stop_camera()
            
    def stop_camera(self):
        """Stop the camera"""
        if self.camera:
            self.timer.stop()
            self.camera.release()
            self.camera = None
            self.video_label.setText("No video feed")
            self.camera_btn.setEnabled(True)
            self.upload_btn.setEnabled(True)
            self.screenshot_btn.setEnabled(True)
            self.alert_log.append(f"<b>{datetime.now().strftime('%H:%M:%S')}</b>: Camera stopped.")
            
    def update_frame(self):
        """Update video frame from camera"""
        if self.camera:
            ret, frame = self.camera.read()
            if not ret:
                self.alert_log.append("<span style='color:red'>Error: Failed to read frame.</span>")
                self.stop_camera()
                return
            self.current_frame = frame
            detections = self.detect_equipment(frame)
            self.display_frame(frame, detections)
            self.update_status(detections)
            self.log_alerts(detections)
            
    def detect_equipment(self, frame):
        """Detect equipment in the frame"""
        if not hasattr(self, 'detection_thread') or self.detection_thread is None:
            return []
        
        # YOLO expects RGB
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.detection_thread.model(img, conf=self.conf_threshold)
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    cls = int(box.cls[0].cpu().numpy())
                    if conf >= self.conf_threshold and 0 <= cls < len(CLASS_NAMES):
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(conf),
                            'class': CLASS_NAMES[cls],
                            'class_id': cls
                        })
        return detections

    def display_frame(self, frame, detections):
        """Display frame with detected equipment"""
        # Draw bounding boxes
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            label = f"{det['class']} {det['confidence']*100:.1f}%"
            color = (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        # Convert to QImage
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))

    def update_confidence(self, value):
        """Update confidence threshold"""
        self.conf_threshold = value / 100.0
        self.conf_label.setText(f"{value}%")

    def update_status(self, detections):
        """Update equipment status"""
        detected = {name: False for name in CLASS_NAMES}
        for det in detections:
            detected[det['class']] = True
        for name in CLASS_NAMES:
            if detected[name]:
                self.status_labels[name].setText(f"{name}: ✅ Detected")
                self.status_labels[name].setStyleSheet("color: #00ff00;")
            else:
                self.status_labels[name].setText(f"{name}: ❌ Not Detected")
                self.status_labels[name].setStyleSheet("color: #ff4444;")
        self.equipment_status = detected

    def log_alerts(self, detections):
        """Log alerts for detected or missing equipment"""
        now = datetime.now().strftime('%H:%M:%S')
        for name in CLASS_NAMES:
            if self.equipment_status[name] and not getattr(self, f'was_{name}_detected', False):
                self.alert_log.append(f"<b>{now}</b>: <span style='color:lime'>{name} detected.</span>")
            if not self.equipment_status[name] and getattr(self, f'was_{name}_detected', True):
                self.alert_log.append(f"<b>{now}</b>: <span style='color:orange'>{name} missing!</span>")
            setattr(self, f'was_{name}_detected', self.equipment_status[name])

    def add_alert(self, level, message):
        """Add alert to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = {
            "INFO": "#00ff00",
            "WARNING": "#ffff00", 
            "ERROR": "#ff4444"
        }.get(level, "#ffffff")
        
        self.alert_log.append(f'<span style="color: {color}">[{timestamp}] {level}: {message}</span>')

    def closeEvent(self, event):
        """Handle application close event"""
        if self.detection_thread:
            self.detection_thread.stop()
            self.detection_thread.wait()
        if self.camera:
            self.camera.release()
        event.accept()

    def get_button_style(self):
        return (
            "QPushButton { background-color: #222; color: #fff; border-radius: 6px; padding: 8px 16px; } "
            "QPushButton:hover { background-color: #444; }"
        )

    def upload_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_path:
            image = cv2.imread(file_path)
            if image is not None:
                self.current_frame = image
                detections = self.detect_equipment(image)
                self.display_frame(image, detections)
                self.update_status(detections)
                self.log_alerts(detections)
                self.alert_log.append(f"<b>{datetime.now().strftime('%H:%M:%S')}</b>: Image loaded: {os.path.basename(file_path)}")
            else:
                self.alert_log.append(f"<span style='color:red'>Error: Failed to load image.</span>")

    def add_ota_update_button(self, right_layout):
        self.ota_btn = QPushButton("Reload Model Weights (OTA Update)")
        self.ota_btn.setStyleSheet(self.get_button_style())
        self.ota_btn.clicked.connect(self.reload_model)
        right_layout.addWidget(self.ota_btn)

    def reload_model(self):
        try:
            if self.detection_thread:
                self.detection_thread.stop()
                self.detection_thread.wait()
            self.detection_thread = DetectionThread(self.model_path)
            self.detection_thread.detection_signal.connect(self.process_detections)
            self.detection_thread.alert_signal.connect(self.add_alert)
            self.detection_thread.start()
            self.alert_log.append(f"<b>{datetime.now().strftime('%H:%M:%S')}</b>: Model reloaded from {self.model_path}")
        except Exception as e:
            self.alert_log.append(f"<span style='color:red'>Error: Failed to reload model: {str(e)}</span>")

    def take_screenshot(self):
        if hasattr(self, 'current_frame') and self.current_frame is not None:
            now = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'screenshot_{now}.png'
            cv2.imwrite(filename, self.current_frame)
            self.alert_log.append(f"<b>{datetime.now().strftime('%H:%M:%S')}</b>: Screenshot saved as {filename}")
        else:
            self.alert_log.append(f"<b>{datetime.now().strftime('%H:%M:%S')}</b>: <span style='color:orange'>No frame to save!</span>")

    def process_detections(self, detections, frame):
        self.current_frame = frame
        self.display_frame(frame, detections)
        self.update_status(detections)
        self.log_alerts(detections)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Space Station Equipment Scanner")
    
    window = SpaceStationScanner()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 