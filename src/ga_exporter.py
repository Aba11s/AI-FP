import os
import csv
import json
from datetime import datetime

class GAExporter:
    
    @staticmethod
    def export_history_to_csv(history, best_gene, best_fitness, baseline_fitness, output_dir="ga_results"):
        """Export complete GA history to CSV files"""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Export Generation Summary
        GAExporter._export_generation_summary(history, output_dir, timestamp)
        
        # 2. Export Individual Evaluations
        GAExporter._export_individual_evaluations(history, output_dir, timestamp)
        
        # 3. Export Final Results
        GAExporter._export_final_results(
            history, best_gene, best_fitness, baseline_fitness, output_dir, timestamp
        )
        
        print(f"\nResults exported to: {output_dir}/")
        
        # Optional: Export as JSON for easy loading
        GAExporter._export_to_json(history, best_gene, best_fitness, output_dir, timestamp)
    
    @staticmethod
    def _export_generation_summary(history, output_dir, timestamp):
        """Export generation-level summary"""
        filename = f"{output_dir}/generation_summary_{timestamp}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow([
                'generation', 'best_fitness', 'avg_fitness',
                'best_waiting_time', 'best_queue_length',
                'avg_waiting_time', 'avg_queue_length',
                'best_gene', 'departed_count_best', 'arrived_count_best',
                'total_waiting_time_best', 'total_time_loss_best',
                'total_queue_length_best'
            ])
            
            # Data
            for gen in history['generations']:
                # Calculate averages for population
                avg_waiting = sum(gen['waiting_times']) / len(gen['waiting_times'])
                avg_queue = sum(gen['queue_lengths']) / len(gen['queue_lengths'])
                
                writer.writerow([
                    gen['generation'],
                    gen['best_fitness'],
                    gen['avg_fitness'],
                    gen['waiting_times'][gen['best_idx']],
                    gen['queue_lengths'][gen['best_idx']],
                    avg_waiting,
                    avg_queue,
                    str(gen['best_gene']),
                    # Note: You'll need to add these to your history collection
                    # 'departed_count_best', 'arrived_count_best', etc.
                    # Add if you track them, otherwise leave as empty
                ])
        
        print(f"✓ Generation summary: {filename}")
    
    @staticmethod
    def _export_individual_evaluations(history, output_dir, timestamp):
        """Export all individual evaluations"""
        filename = f"{output_dir}/individual_evaluations_{timestamp}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'generation', 'individual_id', 'gene', 'fitness',
                'waiting_time', 'queue_length', 'is_best'
            ])
            
            for gen in history['generations']:
                for idx, (gene, fitness, wt, ql) in enumerate(
                    zip(gen['genes'], gen['delays'], 
                        gen['waiting_times'], gen['queue_lengths'])
                ):
                    is_best = (idx == gen['best_idx'])
                    writer.writerow([
                        gen['generation'], idx, str(gene), fitness, wt, ql, is_best
                    ])
        
        print(f"✓ Individual evaluations: {filename}")
    
    @staticmethod
    def _export_final_results(history, best_gene, best_fitness, baseline_fitness, output_dir, timestamp):
        """Export baseline vs optimized comparison"""
        filename = f"{output_dir}/final_results_{timestamp}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'type', 'gene', 'fitness', 'waiting_time', 
                'queue_length', 'improvement_percent'
            ])
            
            # Baseline
            writer.writerow([
                'baseline',
                str(history['baseline']['gene']),
                history['baseline']['delay'],
                history['baseline']['waiting_time'],
                history['baseline']['queue_length'],
                0.0  # No improvement for baseline
            ])
            
            # Optimized
            last_gen = history['generations'][-1]
            improvement = ((baseline_fitness - best_fitness) / baseline_fitness * 100)
            
            writer.writerow([
                'optimized',
                str(best_gene),
                best_fitness,
                last_gen['waiting_times'][last_gen['best_idx']],
                last_gen['queue_lengths'][last_gen['best_idx']],
                improvement
            ])
        
        print(f"✓ Final results: {filename}")
    
    @staticmethod
    def _export_to_json(history, best_gene, best_fitness, output_dir, timestamp):
        """Export complete data as JSON for easy analysis"""
        filename = f"{output_dir}/ga_history_{timestamp}.json"
        
        export_data = {
            'metadata': {
                'timestamp': timestamp,
                'generations': len(history['generations']),
                'population_size': len(history['generations'][0]['genes']) if history['generations'] else 0
            },
            'baseline': history['baseline'],
            'best_solution': {
                'gene': best_gene,
                'fitness': best_fitness
            },
            'generations': history['generations']
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✓ Complete history (JSON): {filename}")