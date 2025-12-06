import os
import csv
import json
from datetime import datetime
import numpy as np

class SimpleGAExporter:
    """Simple exporter for parallel GA with stats output"""
    
    @staticmethod
    def export_parallel_results(best_genes, best_fitness, baseline_fitness, history, 
                               output_dir="ga_parallel_results"):
        """
        Export results from run_ga_parallel_with_stats
        
        Args:
            best_genes: Best solution found
            best_fitness: Best fitness value
            baseline_fitness: Baseline fitness
            history: Dictionary from parallel GA (contains generation stats)
            output_dir: Directory to save files
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Main convergence summary (simple CSV)
        SimpleGAExporter._export_convergence_csv(history, output_dir, timestamp)
        
        # 2. Best solution details
        SimpleGAExporter._export_solution_csv(best_genes, best_fitness, baseline_fitness, 
                                            history, output_dir, timestamp)
        
        # 3. Generation statistics (if available)
        if history and 'generations' in history and history['generations']:
            SimpleGAExporter._export_generation_stats(history, output_dir, timestamp)
        
        # 4. Complete JSON (for data science/analysis)
        SimpleGAExporter._export_complete_json(best_genes, best_fitness, baseline_fitness,
                                             history, output_dir, timestamp)
        
        print(f"\nExported parallel GA results to: {output_dir}/")
        print(f"Timestamp: {timestamp}")
        
        return timestamp
    
    @staticmethod
    def _export_convergence_csv(history, output_dir, timestamp):
        """Export main convergence metrics for plotting"""
        filename = f"{output_dir}/convergence_{timestamp}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'generation', 'best_fitness', 'avg_fitness',
                'fitness_std', 'diversity', 'improvement_pct'
            ])
            
            baseline = history.get('baseline_fitness', 0)
            
            # Check if we have generations data
            if 'generations' not in history or not history['generations']:
                print("⚠ No generation data found in history")
                return
            
            for gen in history['generations']:
                # Safely get all values with defaults
                gen_num = gen.get('generation', 0)
                best_fit = gen.get('best_fitness', 0)
                avg_fit = gen.get('avg_fitness', 0)
                fitness_std = gen.get('fitness_std', 0)
                diversity = gen.get('diversity', 0)
                
                improvement = ((baseline - best_fit) / baseline * 100) if baseline > 0 else 0
                
                writer.writerow([
                    gen_num,
                    f"{best_fit:.6f}",
                    f"{avg_fit:.6f}",
                    f"{fitness_std:.6f}",
                    f"{diversity:.6f}",
                    f"{improvement:.2f}"
                ])
        
        print(f"✓ Convergence data: {filename}")
    
    @staticmethod
    def _export_solution_csv(best_genes, best_fitness, baseline_fitness, history, 
                           output_dir, timestamp):
        """Export the best solution found"""
        filename = f"{output_dir}/best_solution_{timestamp}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Summary section
            writer.writerow(["PARALLEL GA RESULTS"])
            writer.writerow(["Export Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            
            # Get total generations safely
            total_gens = 0
            if history and 'generations' in history:
                total_gens = len(history['generations'])
            
            writer.writerow(["Total Generations", total_gens])
            writer.writerow([])
            
            writer.writerow(["PERFORMANCE"])
            writer.writerow(["Metric", "Value", "Unit"])
            writer.writerow(["Baseline Fitness", f"{baseline_fitness:.6f}", "seconds"])
            writer.writerow(["Optimized Fitness", f"{best_fitness:.6f}", "seconds"])
            
            improvement = ((baseline_fitness - best_fitness) / baseline_fitness * 100) if baseline_fitness > 0 else 0
            writer.writerow(["Improvement", f"{improvement:.2f}", "%"])
            
            absolute_gain = baseline_fitness - best_fitness
            writer.writerow(["Absolute Gain", f"{absolute_gain:.6f}", "seconds"])
            writer.writerow([])
            
            # Gene values
            writer.writerow(["BEST SOLUTION GENES"])
            writer.writerow(["Gene Index", "Value"])
            
            # Convert best_genes to list safely
            if best_genes is None:
                genes = []
            elif hasattr(best_genes, 'tolist'):  # Handle numpy arrays
                genes = best_genes.tolist()
            else:
                try:
                    genes = list(best_genes)
                except:
                    genes = [best_genes]  # Single value
                    
            for i, gene in enumerate(genes):
                writer.writerow([i, f"{float(gene):.6f}"])
        
        print(f"✓ Best solution: {filename}")
    
    @staticmethod
    def _export_generation_stats(history, output_dir, timestamp):
        """Export gene statistics for each generation (if available)"""
        # Check if gene_stats exists in the history
        if (not history or 'generations' not in history or 
            not history['generations'] or 
            'gene_stats' not in history['generations'][0]):
            print("⚠ No gene statistics available in history")
            return
        
        filename = f"{output_dir}/gene_statistics_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Get first generation to determine structure
                first_gen = history['generations'][0]
                gene_stats = first_gen.get('gene_stats', [])
                
                if not gene_stats:
                    print("⚠ Gene statistics list is empty")
                    return
                
                # Sort by index to ensure consistent ordering
                sorted_stats = sorted(gene_stats, key=lambda x: x.get('index', 0))
                num_genes = len(sorted_stats)
                
                # Create header
                header = ['generation']
                for i in range(num_genes):
                    header.extend([
                        f'gene_{i}_mean',
                        f'gene_{i}_std',
                        f'gene_{i}_min',
                        f'gene_{i}_max'
                    ])
                writer.writerow(header)
                
                # Write data for each generation
                for gen in history['generations']:
                    row = [gen.get('generation', 0)]
                    
                    # Get and sort gene stats for this generation
                    current_stats = gen.get('gene_stats', [])
                    sorted_current = sorted(current_stats, key=lambda x: x.get('index', 0))
                    
                    for stats in sorted_current:
                        row.extend([
                            f"{stats.get('mean', 0):.6f}",
                            f"{stats.get('std', 0):.6f}",
                            f"{stats.get('min', 0):.6f}",
                            f"{stats.get('max', 0):.6f}"
                        ])
                    
                    writer.writerow(row)
            
            print(f"✓ Gene statistics: {filename}")
            
        except Exception as e:
            print(f"✗ Error exporting gene statistics: {e}")
    
    @staticmethod
    def _export_complete_json(best_genes, best_fitness, baseline_fitness, history, 
                            output_dir, timestamp):
        """Export everything as JSON for easy loading/analysis"""
        filename = f"{output_dir}/complete_results_{timestamp}.json"
        
        def prepare_for_json(obj):
            if obj is None:
                return None
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.float32, np.float64, np.float_)):
                return float(obj)
            elif isinstance(obj, (np.int32, np.int64, np.int_)):
                return int(obj)
            elif isinstance(obj, dict):
                return {k: prepare_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [prepare_for_json(item) for item in obj]
            else:
                try:
                    return float(obj)
                except:
                    return str(obj)
        
        # Convert best_genes to list safely
        if best_genes is None:
            genes_list = []
        elif hasattr(best_genes, 'tolist'):
            genes_list = best_genes.tolist()
        else:
            try:
                genes_list = list(best_genes)
            except:
                genes_list = [best_genes]
        
        # Build export data structure
        export_data = {
            'metadata': {
                'timestamp': timestamp,
                'export_time': datetime.now().isoformat(),
                'algorithm': 'Parallel GA with Statistics'
            },
            'performance': {
                'baseline_fitness': baseline_fitness,
                'best_fitness': best_fitness,
                'improvement_percent': ((baseline_fitness - best_fitness) / baseline_fitness * 100) if baseline_fitness > 0 else 0
            },
            'best_solution': {
                'genes': prepare_for_json(genes_list),
                'fitness': best_fitness
            }
        }
        
        # Add generation data if available
        if history and 'generations' in history:
            export_data['total_generations'] = len(history['generations'])
            export_data['gene_length'] = len(genes_list)
            
            # Add convergence data
            if history['generations']:
                export_data['convergence_data'] = {
                    'generations': [gen.get('generation', i) for i, gen in enumerate(history['generations'])],
                    'best_fitness': [gen.get('best_fitness', 0) for gen in history['generations']],
                    'avg_fitness': [gen.get('avg_fitness', 0) for gen in history['generations']],
                    'diversity': [gen.get('diversity', 0) for gen in history['generations']]
                }
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            print(f"✓ Complete JSON: {filename}")
        except Exception as e:
            print(f"✗ Error exporting JSON: {e}")
    
    @staticmethod
    def quick_export(best_genes, best_fitness, baseline_fitness, filename="ga_results.csv"):
        """
        Quick single-file export for immediate results
        
        Returns:
            str: CSV content as string (also saves to file)
        """
        try:
            # Convert best_genes to list safely
            if best_genes is None:
                genes = []
            elif hasattr(best_genes, 'tolist'):
                genes = best_genes.tolist()
            else:
                try:
                    genes = list(best_genes)
                except:
                    genes = [best_genes]
            
            content = []
            content.append("QUICK GA EXPORT")
            content.append(f"Timestamp,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            content.append(f"Baseline,{baseline_fitness:.6f}")
            content.append(f"Best Found,{best_fitness:.6f}")
            
            improvement = ((baseline_fitness - best_fitness) / baseline_fitness * 100) if baseline_fitness > 0 else 0
            content.append(f"Improvement %,{improvement:.2f}")
            content.append("")
            content.append("Gene Index,Value")
            
            for i, gene in enumerate(genes):
                content.append(f"{i},{float(gene):.6f}")
            
            csv_content = "\n".join(content)
            
            with open(filename, 'w') as f:
                f.write(csv_content)
            
            print(f"✓ Quick export: {filename}")
            return csv_content
            
        except Exception as e:
            print(f"✗ Error in quick export: {e}")
            return ""