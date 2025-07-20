# Space Station Safety Scanner (Bonus Application)

A real-time object detection app for space station environments using your trained YOLOv8 model. Detects Toolbox, Oxygen Tank, and Fire Extinguisher with live camera or image upload. Alerts for missing/misplaced equipment. Supports continuous model updates via Falcon integration and OTA updates.

## Features
- Real-time camera feed or image upload
- Bounding box overlays for detected objects
- Equipment status dashboard
- Alert log for safety-critical events
- Screenshot capture
- **OTA model update button** (reloads weights without restarting app)
- **Continuous model update workflow** (Falcon + retraining script)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure your trained YOLOv8 weights are at `runs/detect/train/weights/best.pt`.
3. Run the app:
   ```bash
   python space_scanner.py
   ```

## OTA Model Update
- After retraining or receiving new weights, place the new `best.pt` in `runs/detect/train/weights/`.
- Click **Reload Model Weights (OTA Update)** in the app to load the new model without restarting.

## Falcon Integration & Retraining
- See `retraining_script.py` for how to trigger Falcon synthetic data generation and retrain the model.
- The script validates and (pseudo) deploys the new model for OTA update.

## Demo Video
- See `demo.mp4` for a screen recording of the app in action, including OTA update.

## Update Plan
- See `update_plan/update_workflow.pdf` for the Falcon integration and CI/CD pipeline.
- See `update_plan/retraining_script.py` for the retraining automation.

## Usage
- Click **Start Camera** for live detection, or **Upload Image** to analyze a photo.
- View equipment status and alerts on the right panel.
- Use **Take Screenshot** to save the current view.
- Use **Reload Model Weights (OTA Update)** after a model update.

## Notes
- Requires a webcam for live detection.
- For best results, use the provided synthetic dataset for training.

## License
For hackathon use only. See main project for details. 