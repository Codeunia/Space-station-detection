import os
import subprocess
import json
import time
from datetime import datetime

class IterativeTrainer:
    def __init__(self):
        self.experiments = []
        self.best_mAP = 0.0
        self.best_config = None
        
    def run_experiment(self, config_name, **kwargs):
        """Run a training experiment with given configuration"""
        print(f"\n{'='*60}")
        print(f"RUNNING EXPERIMENT: {config_name}")
        print(f"{'='*60}")
        
        # Create experiment config
        experiment_config = {
            'name': config_name,
            'timestamp': datetime.now().isoformat(),
            'config': kwargs
        }
        
        # Modify train.py for this experiment
        self.modify_train_script(**kwargs)
        
        # Run training
        start_time = time.time()
        try:
            result = subprocess.run(['python', 'train.py'], 
                                  capture_output=True, text=True, timeout=72000)  # 20 hour timeout
            
            if result.returncode == 0:
                # Extract results
                metrics = self.extract_metrics()
                experiment_config['metrics'] = metrics
                experiment_config['success'] = True
                experiment_config['training_time'] = (time.time() - start_time) / 3600
                
                # Update best model
                if metrics['mAP50'] > self.best_mAP:
                    self.best_mAP = metrics['mAP50']
                    self.best_config = config_name
                    
                print(f"✅ Experiment {config_name} completed successfully!")
                print(f"   mAP@0.5: {metrics['mAP50']:.3f} ({metrics['mAP50']*100:.1f}%)")
                print(f"   Training time: {experiment_config['training_time']:.2f} hours")
                
            else:
                experiment_config['success'] = False
                experiment_config['error'] = result.stderr
                print(f"❌ Experiment {config_name} failed!")
                print(f"Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            experiment_config['success'] = False
            experiment_config['error'] = 'Training timeout'
            print(f"⏰ Experiment {config_name} timed out!")
            
        self.experiments.append(experiment_config)
        self.save_experiments()
        
        return experiment_config
    
    def modify_train_script(self, **kwargs):
        """Modify train.py with new parameters"""
        with open('train.py', 'r') as f:
            content = f.read()
        
        # Update parameters
        for key, value in kwargs.items():
            if key == 'epochs':
                content = content.replace('EPOCHS = 5', f'EPOCHS = {value}')
            elif key == 'mosaic':
                content = content.replace('MOSAIC = 0.1', f'MOSAIC = {value}')
            elif key == 'optimizer':
                content = content.replace("OPTIMIZER = 'AdamW'", f"OPTIMIZER = '{value}'")
            elif key == 'lr0':
                content = content.replace('LR0 = 0.001', f'LR0 = {value}')
            elif key == 'momentum':
                content = content.replace('MOMENTUM = 0.2', f'MOMENTUM = {value}')
        
        with open('train.py', 'w') as f:
            f.write(content)
    
    def extract_metrics(self):
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
    
    def save_experiments(self):
        """Save experiment results"""
        with open('experiment_results.json', 'w') as f:
            json.dump({
                'experiments': self.experiments,
                'best_mAP': self.best_mAP,
                'best_config': self.best_config
            }, f, indent=2)
    
    def run_optimization_experiments(self):
        """Run a series of optimization experiments"""
        experiments = [
            {
                'name': 'Baseline_Extended',
                'epochs': 50,
                'mosaic': 0.1,
                'optimizer': 'AdamW',
                'lr0': 0.001,
                'momentum': 0.2
            },
            {
                'name': 'Higher_Mosaic',
                'epochs': 30,
                'mosaic': 0.7,
                'optimizer': 'AdamW',
                'lr0': 0.001,
                'momentum': 0.2
            },
            {
                'name': 'Lower_Learning_Rate',
                'epochs': 30,
                'mosaic': 0.1,
                'optimizer': 'AdamW',
                'lr0': 0.0001,
                'momentum': 0.2
            },
            {
                'name': 'SGD_Optimizer',
                'epochs': 30,
                'mosaic': 0.1,
                'optimizer': 'SGD',
                'lr0': 0.01,
                'momentum': 0.9
            }
        ]
        
        print("Starting iterative optimization experiments...")
        print(f"Total experiments to run: {len(experiments)}")
        
        for i, exp in enumerate(experiments, 1):
            print(f"\nProgress: {i}/{len(experiments)}")
            self.run_experiment(**exp)
            
            # Brief pause between experiments
            time.sleep(5)
        
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print final summary of all experiments"""
        print(f"\n{'='*60}")
        print("FINAL EXPERIMENT SUMMARY")
        print(f"{'='*60}")
        
        successful_experiments = [exp for exp in self.experiments if exp['success']]
        
        if successful_experiments:
            print(f"Best Configuration: {self.best_config}")
            print(f"Best mAP@0.5: {self.best_mAP:.3f} ({self.best_mAP*100:.1f}%)")
            
            print(f"\nAll Successful Experiments:")
            for exp in successful_experiments:
                print(f"  {exp['name']}: mAP@0.5 = {exp['metrics']['mAP50']:.3f} "
                      f"({exp['metrics']['mAP50']*100:.1f}%)")
        else:
            print("No successful experiments completed.")
        
        print(f"\nDetailed results saved to: experiment_results.json")

if __name__ == "__main__":
    trainer = IterativeTrainer()
    trainer.run_optimization_experiments() 