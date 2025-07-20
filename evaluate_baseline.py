import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

def analyze_baseline_results():
    """Analyze baseline training results and generate documentation"""
    
    # Read results
    results_path = "runs/detect/train/results.csv"
    if not os.path.exists(results_path):
        print("Results file not found!")
        return
    
    df = pd.read_csv(results_path)
    
    # Extract final metrics
    final_metrics = {
        'mAP50': df['metrics/mAP50(B)'].iloc[-1],
        'mAP50-95': df['metrics/mAP50-95(B)'].iloc[-1],
        'Precision': df['metrics/precision(B)'].iloc[-1],
        'Recall': df['metrics/recall(B)'].iloc[-1],
        'Training_Time_Hours': df['time'].iloc[-1] / 3600,
        'Epochs': len(df)
    }
    
    # Generate performance summary
    print("="*60)
    print("BASELINE YOLOv8 TRAINING RESULTS")
    print("="*60)
    print(f"Model: YOLOv8s")
    print(f"Training Time: {final_metrics['Training_Time_Hours']:.2f} hours")
    print(f"Epochs: {final_metrics['Epochs']}")
    print(f"mAP@0.5: {final_metrics['mAP50']:.3f} ({final_metrics['mAP50']*100:.1f}%)")
    print(f"mAP@0.5:0.95: {final_metrics['mAP50-95']:.3f} ({final_metrics['mAP50-95']*100:.1f}%)")
    print(f"Precision: {final_metrics['Precision']:.3f} ({final_metrics['Precision']*100:.1f}%)")
    print(f"Recall: {final_metrics['Recall']:.3f} ({final_metrics['Recall']*100:.1f}%)")
    
    # Performance assessment
    if final_metrics['mAP50'] >= 0.8:
        performance_level = "EXCELLENT"
    elif final_metrics['mAP50'] >= 0.6:
        performance_level = "GOOD"
    else:
        performance_level = "NEEDS IMPROVEMENT"
    
    print(f"\nPerformance Level: {performance_level}")
    
    # Save results for documentation
    results_summary = {
        'timestamp': datetime.now().isoformat(),
        'model': 'YOLOv8s',
        'dataset': 'Duality AI Space Station Synthetic Data',
        'classes': ['Toolbox', 'Oxygen Tank', 'Fire Extinguisher'],
        'metrics': final_metrics,
        'performance_level': performance_level,
        'training_config': {
            'epochs': final_metrics['Epochs'],
            'device': 'CPU',
            'optimizer': 'AdamW',
            'learning_rate': 0.001
        }
    }
    
    with open('baseline_results.json', 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    print(f"\nResults saved to: baseline_results.json")
    
    return results_summary

def generate_improvement_suggestions():
    """Generate suggestions for model improvement"""
    
    suggestions = {
        'hyperparameter_tuning': [
            'Increase epochs to 50-100 for better convergence',
            'Experiment with different learning rates (0.01, 0.0001)',
            'Try different optimizers (SGD, Adam)',
            'Adjust batch size based on available memory'
        ],
        'data_augmentation': [
            'Increase mosaic augmentation (0.5-0.9)',
            'Add more HSV augmentation',
            'Experiment with mixup and cutmix',
            'Add rotation and perspective transforms'
        ],
        'model_architecture': [
            'Try larger models (YOLOv8m, YOLOv8l)',
            'Experiment with different input sizes (416, 832)',
            'Consider ensemble methods'
        ],
        'training_strategy': [
            'Implement learning rate scheduling',
            'Use early stopping to prevent overfitting',
            'Add validation-based model selection',
            'Implement cross-validation'
        ]
    }
    
    print("\n" + "="*60)
    print("SUGGESTIONS FOR MODEL IMPROVEMENT")
    print("="*60)
    
    for category, items in suggestions.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for i, item in enumerate(items, 1):
            print(f"  {i}. {item}")
    
    return suggestions

if __name__ == "__main__":
    results = analyze_baseline_results()
    suggestions = generate_improvement_suggestions()
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Review baseline results and performance")
    print("2. Implement suggested improvements")
    print("3. Run iterative training experiments")
    print("4. Document findings for hackathon report")
    print("5. Prepare README and application proposal") 