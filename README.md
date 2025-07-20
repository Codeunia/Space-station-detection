# 🚀 Space Station Object Detection with YOLOv8

**Duality AI Space Station Hackathon Project**  
**Team: Code Warrior**  
**DEMO video(LINKEDIN ):https://www.linkedin.com/in/sandeep-kumar-303bbb25a/**

**Team Members:Sandeep Kumar,Rachit Pachauri,Samyak Jain**

**Date: 25 June 2025**

---

## 📁 Complete Project Files

**📦 Google Drive Repository**: [Download Complete Project Files](https://drive.google.com/drive/folders/1goXFMBTSp_FAVyi22TOElSoHal358VSw?usp=sharing)

The Google Drive contains:
- **Dataset**: Complete training, validation, and test data
- **Model Weights**: Trained YOLOv8 models (`.pt` files)
- **Training Results**: Full training logs and visualizations
- **Demo Video**: Application demonstration video
- **Additional Resources**: All project files and documentation

---

## 🎯 Project Overview

This project implements a robust YOLOv8 object detection model for identifying critical objects in space station environments using synthetic data from Duality AI's Falcon digital twin platform. The model detects three essential objects:

- **ToolBox** - Essential maintenance equipment
- **Oxygen Tank** - Life support systems  
- **Fire Extinguisher** - Safety equipment

## 📊 Performance Metrics

**Baseline Results (YOLOv8s):**
- **mAP@0.5: 89.7%** ⭐
- **Precision: 93.2%**
- **Recall: 84.8%**
- **Training Time: 4.76 hours (CPU)**

**Per-class Performance:**
- Fire Extinguisher: 94.7% mAP@0.5
- ToolBox: 91.1% mAP@0.5
- Oxygen Tank: 83.2% mAP@0.5

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/RachitPachauri2005/space-station-object-detection.git
cd space-station-object-detection

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Dataset Preparation

Place your dataset in the following structure:
```
data/
├── train/
│   ├── images/
│   └── labels/
├── val/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

### 3. Training

```bash
# Run baseline training
python train.py

# Train with custom parameters
python train.py --epochs 30 --batch 16
```

### 4. Run the Application

```bash
# Run the Space Station Safety Scanner
python bonus_app/space_scanner.py
```

## 📁 Project Structure

```
space-station-object-detection/
├── bonus_app/                 # PyQt5 Desktop Application
│   ├── space_scanner.py      # Main application
│   ├── requirements.txt      # App dependencies
│   └── README.md            # App documentation
├── data/                     # Dataset (not included in repo)
├── runs/                     # Training results (not included in repo)
├── train.py                  # Main training script
├── check_dataset.py          # Dataset verification
├── evaluate_baseline.py      # Results analysis
├── optimize_model.py         # Hyperparameter optimization
├── yolo_params.yaml          # YOLO configuration
├── requirements.txt          # Project dependencies
└── README.md                # This file
```

## 🔧 Configuration

### Training Parameters

The model can be configured via `train.py` or `yolo_params.yaml`:

- **Model**: YOLOv8s (11.1M parameters)
- **Input Size**: 640x640
- **Optimizer**: AdamW
- **Learning Rate**: 0.001
- **Batch Size**: 16
- **Epochs**: 5 (baseline), 30-50 (optimized)

### Dataset Configuration

- **Classes**: 3 (ToolBox, Oxygen Tank, Fire Extinguisher)
- **Training Images**: 846
- **Validation Images**: 154
- **Test Images**: 397
- **Format**: YOLO format with normalized coordinates

## 🖥️ Desktop Application

The project includes a modern PyQt5 desktop application with:

- **Real-time Detection**: Live camera feed with object detection
- **Image Upload**: Test detection on static images
- **Equipment Status**: Real-time monitoring of detected objects
- **Alert System**: Notifications for missing or detected equipment
- **Screenshot Feature**: Save detection results
- **Dark Theme**: Modern, space-themed UI

### Features:
- ✅ Real-time object detection
- ✅ Equipment status tracking
- ✅ Alert logging system
- ✅ Confidence threshold adjustment
- ✅ Screenshot functionality
- ✅ Modern dark-themed UI

## 📈 Training Results

### Baseline Training
- **Duration**: 4.76 hours on CPU
- **Final mAP@0.5**: 89.7%
- **Convergence**: Stable after 5 epochs

### Optimization Experiments
- Extended training (50 epochs)
- Higher mosaic augmentation (0.7)
- Lower learning rate (0.0001)
- SGD optimizer comparison

## 🎯 Model Performance

### Strengths
- Excellent overall accuracy (89.7% mAP@0.5)
- High precision (93.2%) indicating low false positives
- Good recall (84.8%) for comprehensive detection
- Robust performance across all three object classes

### Areas for Improvement
- Oxygen Tank detection (83.2% mAP) could be enhanced
- Consider larger models (YOLOv8m, YOLOv8l) for better accuracy
- Implement ensemble methods for further improvement

## 🔬 Technical Details

### Model Architecture
- **Backbone**: CSPDarknet53
- **Neck**: PANet with FPN
- **Head**: YOLOv8 detection head
- **Parameters**: 11.1M
- **GFLOPs**: 28.7

### Training Configuration
- **Device**: CPU (Intel Core i7-3632QM)
- **Optimizer**: AdamW with weight decay (0.0005)
- **Learning Rate**: 0.001 with cosine decay scheduling
- **Batch Size**: 16 (optimized for CPU training)
- **Epochs**: 5 (baseline), 30-50 (optimized)

## 🚀 Future Enhancements

1. **Real-world Testing**: Validate on actual space station imagery
2. **Larger Models**: Experiment with YOLOv8m/l for better accuracy
3. **Ensemble Methods**: Combine multiple models for improved performance
4. **Real-time Integration**: Deploy on space station hardware
5. **Continuous Learning**: Implement online learning with new data

## 📝 License

This project is developed for the Duality AI Space Station Hackathon.

## 🤝 Contributing

This is a hackathon project. For questions or collaboration, please contact the team.

## 📞 Contact

**Team**: Code Warrior  
**Project**: Space Station Object Detection  
**Hackathon**: Duality AI Space Station Hackathon

---

**Ready for space station deployment! 🚀** 
