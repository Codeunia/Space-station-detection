import os
import subprocess
import json
import time
from datetime import datetime

def run_optimization_experiment(exp_name, epochs=30, mosaic=0.5, optimizer='AdamW', lr0=0.001):
    """Run a single optimization experiment"""
    print(f"\n{'='*60}")
    print(f"RUNNING EXPERIMENT: {exp_name}")
    print(f"{'='*60}")
    
    # Create backup of original train.py
    if not os.path.exists('train.py.backup'):
        os.system('copy train.py train.py.backup')
    
    # Modify train.py for this experiment
    with open('train.py', 'r') as f:
        content = f.read()
    
    # Update parameters
    content = content.replace('EPOCHS = 5', f'EPOCHS = {epochs}')
    content = content.replace('MOSAIC = 0.1', f'MOSAIC = {mosaic}')
    content = content.replace("OPTIMIZER = 'AdamW'", f"OPTIMIZER = '{optimizer}'")
    content = content.replace('LR0 = 0.001', f'LR0 = {lr0}')
    
    with open('train.py', 'w') as f:
        f.write(content)
    
    # Run training
    start_time = time.time()
    try:
        result = subprocess.run(['python', 'train.py'], 
                              capture_output=True, text=True, timeout=36000)  # 10 hour timeout
        
        if result.returncode == 0:
            # Extract metrics
            metrics = extract_metrics()
            training_time = (time.time() - start_time) / 3600
            
            print(f"✅ Experiment {exp_name} completed successfully!")
            print(f"   mAP@0.5: {metrics['mAP50']:.3f} ({metrics['mAP50']*100:.1f}%)")
            print(f"   Training time: {training_time:.2f} hours")
            
            return {
                'name': exp_name,
                'success': True,
                'metrics': metrics,
                'training_time': training_time,
                'config': {'epochs': epochs, 'mosaic': mosaic, 'optimizer': optimizer, 'lr0': lr0}
            }
        else:
            print(f"❌ Experiment {exp_name} failed!")
            return {'name': exp_name, 'success': False, 'error': result.stderr}
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Experiment {exp_name} timed out!")
        return {'name': exp_name, 'success': False, 'error': 'Timeout'}

def extract_metrics():
    """Extract metrics from the latest training run"""
    try:
        import pandas as pd
        df = pd.read_csv('runs/detect/train/results.csv')
        return {
            'mAP50': df['metrics/mAP50(B)'].iloc[-1],
            'mAP50-95': df['metrics/mAP50-95(B)'].iloc[-1],
            'Precision': df['metrics/precision(B)'].iloc[-1],
            'Recall': df['metrics/recall(B)'].iloc[-1]
        }
    except:
        return {'mAP50': 0.0, 'mAP50-95': 0.0, 'Precision': 0.0, 'Recall': 0.0}

def main():
    """Run optimization experiments"""
    experiments = [
        {'name': 'Extended_Baseline', 'epochs': 50, 'mosaic': 0.1, 'optimizer': 'AdamW', 'lr0': 0.001},
        {'name': 'High_Mosaic', 'epochs': 30, 'mosaic': 0.7, 'optimizer': 'AdamW', 'lr0': 0.001},
        {'name': 'Low_LR', 'epochs': 30, 'mosaic': 0.1, 'optimizer': 'AdamW', 'lr0': 0.0001},
        {'name': 'SGD_Optimizer', 'epochs': 30, 'mosaic': 0.1, 'optimizer': 'SGD', 'lr0': 0.01}
    ]
    
    results = []
    best_mAP = 0.0
    best_config = None
    
    print("Starting optimization experiments...")
    print(f"Total experiments: {len(experiments)}")
    
    for i, exp in enumerate(experiments, 1):
        print(f"\nProgress: {i}/{len(experiments)}")
        result = run_optimization_experiment(**exp)
        results.append(result)
        
        if result['success'] and result['metrics']['mAP50'] > best_mAP:
            best_mAP = result['metrics']['mAP50']
            best_config = exp['name']
        
        # Save progress
        with open('optimization_results.json', 'w') as f:
            json.dump({
                'experiments': results,
                'best_mAP': best_mAP,
                'best_config': best_config
            }, f, indent=2)
        
        time.sleep(5)  # Brief pause between experiments
    
    # Print final summary
    print(f"\n{'='*60}")
    print("OPTIMIZATION COMPLETE")
    print(f"{'='*60}")
    
    successful = [r for r in results if r['success']]
    if successful:
        print(f"Best Configuration: {best_config}")
        print(f"Best mAP@0.5: {best_mAP:.3f} ({best_mAP*100:.1f}%)")
        
        print(f"\nAll Results:")
        for result in successful:
            print(f"  {result['name']}: mAP@0.5 = {result['metrics']['mAP50']:.3f} "
                  f"({result['metrics']['mAP50']*100:.1f}%)")
    else:
        print("No successful experiments completed.")
    
    print(f"\nResults saved to: optimization_results.json")

if __name__ == "__main__":
    main() 