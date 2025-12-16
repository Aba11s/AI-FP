import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from matplotlib.gridspec import GridSpec
import seaborn as sns

class GAVisualizer:
    """Visualize GA convergence and gene statistics"""
    
    @staticmethod
    def visualize_convergence(convergence_csv_path, baseline_fitness=None, output_dir="ga_plots"):
        """
        Visualize GA convergence metrics with baseline comparison
        
        Args:
            convergence_csv_path: Path to convergence CSV file
            baseline_fitness: Baseline fitness value for comparison
            output_dir: Directory to save plots
        """
        # Read data
        df = pd.read_csv(convergence_csv_path)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(15, 10))
        gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
        
        # Plot 1: Best Fitness over Generations with Baseline
        ax1 = fig.add_subplot(gs[0, 0])
        
        # Plot GA best fitness
        ax1.plot(df['generation'], df['best_fitness'], 'b-', linewidth=2, marker='o', markersize=4, label='GA Best')
        
        # Plot baseline if provided
        if baseline_fitness is not None:
            ax1.axhline(y=baseline_fitness, color='r', linestyle='--', linewidth=2, 
                       label=f'Baseline: {baseline_fitness:.1f}s')
            
            # Add improvement annotation
            final_improvement = ((baseline_fitness - df['best_fitness'].iloc[-1]) / baseline_fitness) * 100
            '''ax1.annotate(f'Final: {df["best_fitness"].iloc[-1]:.1f}s\n({final_improvement:.1f}% better)',
                        xy=(df['generation'].iloc[-1], df['best_fitness'].iloc[-1]),
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle="round,pad=0.3", fc="lightgreen", alpha=0.8))'''
        
        ax1.set_xlabel('Generation')
        ax1.set_ylabel('Best Fitness (s)')
        ax1.set_title('Best Fitness Convergence with Baseline')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(bottom=0)
        ax1.legend()
        
        # Plot 2: Average Fitness over Generations with Baseline
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.plot(df['generation'], df['avg_fitness'], 'g-', linewidth=2, marker='s', markersize=4, label='GA Average')
        
        # Plot baseline if provided
        if baseline_fitness is not None:
            ax2.axhline(y=baseline_fitness, color='r', linestyle='--', linewidth=2, 
                       label=f'Baseline: {baseline_fitness:.1f}s')
        
        ax2.set_xlabel('Generation')
        ax2.set_ylabel('Average Fitness (s)')
        ax2.set_title('Average Fitness with Baseline')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(bottom=0)
        ax2.legend()
        
        # Shaded area showing std
        ax2.fill_between(df['generation'], 
                        df['avg_fitness'] - df['fitness_std'],
                        df['avg_fitness'] + df['fitness_std'],
                        alpha=0.2, color='green', label='±1 std')
        ax2.legend()
        
        # Plot 3: Fitness Comparison (Baseline vs GA)
        ax3 = fig.add_subplot(gs[1, 0])
        
        # Plot baseline if provided
        if baseline_fitness is not None:
            ax3.axhline(y=baseline_fitness, color='r', linestyle='--', linewidth=2.5, 
                       label=f'Baseline: {baseline_fitness:.1f}s', alpha=0.7)
        
        ax3.plot(df['generation'], df['best_fitness'], 'b-', linewidth=2, label='GA Best')
        ax3.plot(df['generation'], df['avg_fitness'], 'g-', linewidth=2, label='GA Average', alpha=0.7)
        
        ax3.set_xlabel('Generation')
        ax3.set_ylabel('Fitness (s)')
        ax3.set_title('Baseline vs GA Performance')
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim(bottom=0)
        ax3.legend()
        
        # Plot 4: Population Diversity
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.plot(df['generation'], df['diversity'], 'r-', linewidth=2, marker='^', markersize=4)
        ax4.set_xlabel('Generation')
        ax4.set_ylabel('Diversity')
        ax4.set_title('Population Diversity')
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim([0, 1.1])
        
        # Plot 5: Improvement Percentage (with baseline reference)
        ax5 = fig.add_subplot(gs[2, 0])
        
        # Calculate actual improvement percentage if baseline provided
        if baseline_fitness is not None:
            # Replace df['improvement_pct'] with actual calculation
            actual_improvement = ((baseline_fitness - df['best_fitness']) / baseline_fitness) * 100
            ax5.plot(df['generation'], actual_improvement, 'm-', linewidth=2, marker='D', markersize=4, 
                    label='Actual Improvement')
        else:
            ax5.plot(df['generation'], df['improvement_pct'], 'm-', linewidth=2, marker='D', markersize=4, 
                    label='Improvement')
        
        ax5.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.5)
        ax5.set_xlabel('Generation')
        ax5.set_ylabel('Improvement (%)')
        ax5.set_title('Improvement Over Baseline')
        ax5.grid(True, alpha=0.3)
        ax5.legend()
        
        # Add final value annotation
        if len(df) > 0 and baseline_fitness is not None:
            final_improvement = ((baseline_fitness - df['best_fitness'].iloc[-1]) / baseline_fitness) * 100
            ax5.annotate(f'{final_improvement:.1f}%',
                        xy=(df['generation'].iloc[-1], final_improvement),
                        xytext=(10, 10), textcoords='offset points',
                        fontweight='bold', color='darkred')
        
        # Plot 6: Fitness Standard Deviation
        ax6 = fig.add_subplot(gs[2, 1])
        ax6.plot(df['generation'], df['fitness_std'], color='orange', linewidth=2, marker='v', markersize=4)
        ax6.set_xlabel('Generation')
        ax6.set_ylabel('Fitness Std Dev')
        ax6.set_title('Fitness Standard Deviation')
        ax6.grid(True, alpha=0.3)
        ax6.set_ylim(bottom=0)
        
        # Add baseline text to title if provided
        title_suffix = f" (Baseline: {baseline_fitness:.1f}s)" if baseline_fitness is not None else ""
        plt.suptitle(f'Genetic Algorithm Convergence Analysis{title_suffix}', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Save plot
        output_path = f"{output_dir}/convergence_with_baseline.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.show()
        
        print(f"✓ Convergence plots with baseline saved to: {output_path}")
        
        # Also create a simplified comparison plot
        GAVisualizer._create_baseline_comparison_plot(df, baseline_fitness, output_dir)
        
        return df
    
    @staticmethod
    def _create_baseline_comparison_plot(df, baseline_fitness, output_dir):
        """Create a focused baseline comparison plot"""
        if baseline_fitness is None:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Left: GA vs Baseline fitness
        ax1.plot(df['generation'], df['best_fitness'], 'b-', linewidth=3, marker='o', markersize=6, label='GA Best')
        ax1.axhline(y=baseline_fitness, color='r', linestyle='--', linewidth=3, 
                   label=f'Baseline ({baseline_fitness:.1f}s)', alpha=0.7)
        
        # Fill improvement area
        ax1.fill_between(df['generation'], df['best_fitness'], baseline_fitness,
                        where=(df['best_fitness'] < baseline_fitness),
                        color='lightgreen', alpha=0.3, label='Improvement Area')
        
        ax1.set_xlabel('Generation')
        ax1.set_ylabel('Fitness (s)')
        ax1.set_title('GA Optimization vs Baseline')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Calculate improvement percentage
        improvement = ((baseline_fitness - df['best_fitness']) / baseline_fitness) * 100
        
        # Right: Improvement percentage
        ax2.plot(df['generation'], improvement, 'g-', linewidth=3, marker='s', markersize=6)
        ax2.fill_between(df['generation'], improvement, 0, color='lightgreen', alpha=0.3)
        ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.5)
        
        ax2.set_xlabel('Generation')
        ax2.set_ylabel('Improvement (%)')
        ax2.set_title(f'Improvement Over Baseline\nFinal: {improvement.iloc[-1]:.1f}%')
        ax2.grid(True, alpha=0.3)
        
        # Add milestone annotations
        milestones = [0, 5, 10, 15, 20, df['generation'].iloc[-1]]
        for milestone in milestones:
            if milestone <= df['generation'].iloc[-1]:
                milestone_idx = df[df['generation'] == milestone].index[0]
                milestone_improvement = improvement.iloc[milestone_idx]
                if milestone_improvement > 5:  # Only annotate significant improvements
                    ax2.annotate(f'{milestone_improvement:.1f}%', 
                               xy=(milestone, milestone_improvement),
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/baseline_comparison_focused.png", dpi=150, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def quick_visualize_with_baseline(convergence_csv_path, baseline_fitness=None, output_dir="ga_plots"):
        """Quick visualization with baseline comparison"""
        df = pd.read_csv(convergence_csv_path)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Simple 2x1 plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Left: Fitness convergence with baseline
        ax1.plot(df['generation'], df['best_fitness'], 'b-o', linewidth=2, markersize=5, label='GA Best')
        ax1.plot(df['generation'], df['avg_fitness'], 'g-s', linewidth=2, markersize=5, label='GA Average', alpha=0.7)
        
        if baseline_fitness is not None:
            ax1.axhline(y=baseline_fitness, color='r', linestyle='--', linewidth=2.5, 
                       label=f'Baseline: {baseline_fitness:.1f}s')
            
            # Add final improvement text
            final_improvement = ((baseline_fitness - df['best_fitness'].iloc[-1]) / baseline_fitness) * 100
            ax1.text(0.02, 0.98, f'Final Improvement: {final_improvement:.1f}%',
                    transform=ax1.transAxes, fontsize=10, fontweight='bold',
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax1.set_xlabel('Generation')
        ax1.set_ylabel('Fitness (s)')
        ax1.set_title('GA vs Baseline Fitness')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Right: Improvement and Diversity
        if baseline_fitness is not None:
            improvement = ((baseline_fitness - df['best_fitness']) / baseline_fitness) * 100
            ax2.plot(df['generation'], improvement, 'g-D', linewidth=2, markersize=5, label='Improvement %')
            ax2.set_ylabel('Improvement (%)', color='green')
            ax2.tick_params(axis='y', labelcolor='green')
            ax2.set_ylim(bottom=0)
            
            ax2b = ax2.twinx()
            ax2b.plot(df['generation'], df['diversity'], 'r-^', linewidth=2, markersize=5, label='Diversity')
            ax2b.set_ylabel('Diversity', color='red')
            ax2b.tick_params(axis='y', labelcolor='red')
            ax2b.set_ylim([0, 1.1])
            
            ax2.set_title(f'Improvement & Diversity\nFinal: {improvement.iloc[-1]:.1f}%')
        else:
            ax2.plot(df['generation'], df['diversity'], 'r-^', linewidth=2, markersize=5, label='Diversity')
            ax2.set_ylabel('Diversity')
            ax2.set_title('Population Diversity')
            ax2.set_ylim([0, 1.1])
        
        ax2.set_xlabel('Generation')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        output_path = f"{output_dir}/quick_baseline_comparison.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.show()
        
        print(f"✓ Quick baseline comparison plot saved to: {output_path}")
        return df
    
    @staticmethod
    def _create_individual_plots(df, output_dir):
        """Create individual plots for each metric"""
        metrics = {
            'best_fitness': ('Best Fitness', 'blue', 'o'),
            'avg_fitness': ('Average Fitness', 'green', 's'),
            'diversity': ('Population Diversity', 'red', '^'),
            'improvement_pct': ('Improvement (%)', 'magenta', 'D'),  # Fixed: 'magenta' instead of 'purple'
            'fitness_std': ('Fitness Std Dev', 'orange', 'v')
        }
        
        for metric, (title, color, marker) in metrics.items():
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df['generation'], df[metric], color=color, linestyle='-', 
                   linewidth=2, marker=marker, markersize=6)
            ax.set_xlabel('Generation')
            ax.set_ylabel(title.split('(')[0].strip())
            ax.set_title(title)
            ax.grid(True, alpha=0.3)
            
            if metric == 'diversity':
                ax.set_ylim([0, 1.1])
            elif metric not in ['improvement_pct']:
                ax.set_ylim(bottom=0)
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/{metric}_plot.png", dpi=150)
            plt.close()
    
    @staticmethod
    def visualize_gene_statistics(gene_stats_csv_path, output_dir="ga_plots"):
        """
        Visualize gene statistics over generations
        
        Args:
            gene_stats_csv_path: Path to gene statistics CSV file
            output_dir: Directory to save plots
        """
        # Read data
        df = pd.read_csv(gene_stats_csv_path)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Determine number of genes from columns
        gene_columns = [col for col in df.columns if col.startswith('gene_') and '_mean' in col]
        num_genes = len(gene_columns)
        
        print(f"Found {num_genes} genes to visualize")
        
        # Create a figure for gene means over generations
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()
        
        # Plot each gene's mean value over generations
        for i in range(min(num_genes, 4)):  # Plot first 4 genes
            ax = axes[i]
            
            # Get mean, min, max columns for this gene
            mean_col = f'gene_{i}_mean'
            min_col = f'gene_{i}_min'
            max_col = f'gene_{i}_max'
            std_col = f'gene_{i}_std'
            
            # Plot mean with std shaded area
            ax.plot(df['generation'], df[mean_col], color='blue', linewidth=2, label='Mean')
            ax.fill_between(df['generation'],
                           df[mean_col] - df[std_col],
                           df[mean_col] + df[std_col],
                           alpha=0.2, color='blue', label='±1 std')
            
            # Plot min and max as thin lines
            ax.plot(df['generation'], df[min_col], color='red', linestyle='--', linewidth=1, alpha=0.5, label='Min')
            ax.plot(df['generation'], df[max_col], color='green', linestyle='--', linewidth=1, alpha=0.5, label='Max')
            
            ax.set_xlabel('Generation')
            ax.set_ylabel(f'Gene {i} Value')
            ax.set_title(f'Gene {i} Evolution')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        plt.suptitle('Gene Evolution Over Generations', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        output_path = f"{output_dir}/gene_evolution.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.show()
        
        print(f"✓ Gene evolution plot saved to: {output_path}")
        
        # Create individual gene plots
        GAVisualizer._create_individual_gene_plots(df, num_genes, output_dir)
        
        # Create heatmap of gene values
        GAVisualizer._create_gene_heatmap(df, num_genes, output_dir)
        
        return df
    
    @staticmethod
    def _create_individual_gene_plots(df, num_genes, output_dir):
        """Create individual plots for each gene"""
        os.makedirs(f"{output_dir}/genes", exist_ok=True)
        
        for i in range(num_genes):
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Get columns for this gene
            mean_col = f'gene_{i}_mean'
            min_col = f'gene_{i}_min'
            max_col = f'gene_{i}_max'
            std_col = f'gene_{i}_std'
            
            # Plot 1: Mean value with std
            ax1.plot(df['generation'], df[mean_col], color='blue', linewidth=3, label='Mean Value')
            ax1.fill_between(df['generation'],
                            df[mean_col] - df[std_col],
                            df[mean_col] + df[std_col],
                            alpha=0.3, color='blue', label='Standard Deviation')
            
            ax1.plot(df['generation'], df[min_col], color='red', linestyle=':', linewidth=1.5, label='Minimum')
            ax1.plot(df['generation'], df[max_col], color='green', linestyle=':', linewidth=1.5, label='Maximum')
            
            ax1.set_xlabel('Generation')
            ax1.set_ylabel(f'Gene {i} Value')
            ax1.set_title(f'Gene {i} - Value Range Over Generations')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Plot 2: Standard deviation alone
            ax2.plot(df['generation'], df[std_col], color='orange', linewidth=2, marker='o')
            ax2.set_xlabel('Generation')
            ax2.set_ylabel('Standard Deviation')
            ax2.set_title(f'Gene {i} - Convergence (Lower Std = More Converged)')
            ax2.grid(True, alpha=0.3)
            ax2.fill_between(df['generation'], 0, df[std_col], alpha=0.3, color='orange')
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/genes/gene_{i}_evolution.png", dpi=150)
            plt.close()
    
    @staticmethod
    def _create_gene_heatmap(df, num_genes, output_dir):
        """Create heatmap of gene means across generations"""
        # Extract mean values for heatmap
        heatmap_data = []
        for i in range(num_genes):
            mean_col = f'gene_{i}_mean'
            heatmap_data.append(df[mean_col].values)
        
        heatmap_data = np.array(heatmap_data)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create heatmap
        im = ax.imshow(heatmap_data, aspect='auto', cmap='viridis')
        
        # Set labels
        ax.set_xlabel('Generation')
        ax.set_ylabel('Gene Index')
        ax.set_title('Gene Values Heatmap Across Generations')
        
        # Set tick labels
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df['generation'])
        ax.set_yticks(range(num_genes))
        ax.set_yticklabels([f'Gene {i}' for i in range(num_genes)])
        
        # Add colorbar
        plt.colorbar(im, ax=ax, label='Gene Value')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/gene_heatmap.png", dpi=150)
        plt.show()
    
    @staticmethod
    def visualize_comparison(convergence_csv_path, gene_stats_csv_path=None, output_dir="ga_plots"):
        """
        Create comprehensive comparison visualization
        
        Args:
            convergence_csv_path: Path to convergence CSV
            gene_stats_csv_path: Optional path to gene statistics CSV
            output_dir: Directory to save plots
        """
        # Read convergence data
        conv_df = pd.read_csv(convergence_csv_path)
        
        # Create figure
        fig = plt.figure(figsize=(16, 12))
        
        if gene_stats_csv_path:
            # Read gene stats
            gene_df = pd.read_csv(gene_stats_csv_path)
            num_genes = len([col for col in gene_df.columns if col.startswith('gene_') and '_mean' in col])
            
            # Create 2x2 grid for comprehensive view
            gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.4)
            
            # Plot 1: Fitness convergence
            ax1 = fig.add_subplot(gs[0, :2])
            ax1.plot(conv_df['generation'], conv_df['best_fitness'], color='blue', linewidth=3, label='Best')
            ax1.plot(conv_df['generation'], conv_df['avg_fitness'], color='green', linewidth=2, label='Average')
            ax1.fill_between(conv_df['generation'], 
                            conv_df['avg_fitness'] - conv_df['fitness_std'],
                            conv_df['avg_fitness'] + conv_df['fitness_std'],
                            alpha=0.2, color='green')
            ax1.set_xlabel('Generation')
            ax1.set_ylabel('Fitness (s)')
            ax1.set_title('Fitness Convergence')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Plot 2: Diversity and Improvement
            ax2 = fig.add_subplot(gs[0, 2])
            ax2.plot(conv_df['generation'], conv_df['diversity'], color='red', label='Diversity')
            ax2.set_xlabel('Generation')
            ax2.set_ylabel('Diversity', color='red')
            ax2.tick_params(axis='y', labelcolor='red')
            ax2.set_ylim([0, 1.1])
            ax2.grid(True, alpha=0.3)
            
            ax2b = ax2.twinx()
            ax2b.plot(conv_df['generation'], conv_df['improvement_pct'], color='magenta', label='Improvement %')
            ax2b.set_ylabel('Improvement (%)', color='magenta')
            ax2b.tick_params(axis='y', labelcolor='magenta')
            ax2.set_title('Diversity & Improvement')
            
            # Plot gene evolution for first gene
            ax3 = fig.add_subplot(gs[1, 0])
            mean_col = 'gene_0_mean'
            std_col = 'gene_0_std'
            ax3.plot(gene_df['generation'], gene_df[mean_col], color='blue', label='Mean')
            ax3.fill_between(gene_df['generation'],
                            gene_df[mean_col] - gene_df[std_col],
                            gene_df[mean_col] + gene_df[std_col],
                            alpha=0.3, color='blue')
            ax3.set_xlabel('Generation')
            ax3.set_ylabel('Gene 0 Value')
            ax3.set_title('Gene 0 Evolution')
            ax3.grid(True, alpha=0.3)
            
            # Plot gene evolution for second gene
            ax4 = fig.add_subplot(gs[1, 1])
            mean_col = 'gene_1_mean'
            std_col = 'gene_1_std'
            ax4.plot(gene_df['generation'], gene_df[mean_col], color='blue', label='Mean')
            ax4.fill_between(gene_df['generation'],
                            gene_df[mean_col] - gene_df[std_col],
                            gene_df[mean_col] + gene_df[std_col],
                            alpha=0.3, color='blue')
            ax4.set_xlabel('Generation')
            ax4.set_ylabel('Gene 1 Value')
            ax4.set_title('Gene 1 Evolution')
            ax4.grid(True, alpha=0.3)
            
            # Plot gene std convergence
            ax5 = fig.add_subplot(gs[1, 2])
            colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown']
            for i in range(min(num_genes, 4)):
                std_col = f'gene_{i}_std'
                color = colors[i % len(colors)]
                ax5.plot(gene_df['generation'], gene_df[std_col], color=color, label=f'Gene {i}')
            ax5.set_xlabel('Generation')
            ax5.set_ylabel('Standard Deviation')
            ax5.set_title('Gene Convergence (Lower = Better)')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
            
            # Create heatmap for all genes
            ax6 = fig.add_subplot(gs[2, :])
            heatmap_data = []
            for i in range(num_genes):
                mean_col = f'gene_{i}_mean'
                heatmap_data.append(gene_df[mean_col].values)
            
            heatmap_data = np.array(heatmap_data)
            im = ax6.imshow(heatmap_data, aspect='auto', cmap='viridis')
            ax6.set_xlabel('Generation')
            ax6.set_ylabel('Gene Index')
            ax6.set_title('All Genes - Value Heatmap')
            ax6.set_xticks(range(len(gene_df)))
            ax6.set_xticklabels(gene_df['generation'])
            ax6.set_yticks(range(num_genes))
            ax6.set_yticklabels([f'{i}' for i in range(num_genes)])
            plt.colorbar(im, ax=ax6, label='Gene Value')
            
        else:
            # Simple 2x2 layout without gene stats
            gs = GridSpec(2, 2, figure=fig)
            
            plots = [
                ('best_fitness', 'Best Fitness', 'blue', gs[0, 0]),
                ('avg_fitness', 'Average Fitness', 'green', gs[0, 1]),
                ('diversity', 'Population Diversity', 'red', gs[1, 0]),
                ('improvement_pct', 'Improvement (%)', 'magenta', gs[1, 1])
            ]
            
            for metric, title, color, pos in plots:
                ax = fig.add_subplot(pos)
                ax.plot(conv_df['generation'], conv_df[metric], color=color, linewidth=2)
                ax.set_xlabel('Generation')
                ax.set_ylabel(title)
                ax.set_title(title)
                ax.grid(True, alpha=0.3)
        
        plt.suptitle('Genetic Algorithm - Comprehensive Analysis', fontsize=18, fontweight='bold')
        plt.tight_layout()
        
        output_path = f"{output_dir}/comprehensive_analysis.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.show()
        
        print(f"✓ Comprehensive analysis saved to: {output_path}")
    
    @staticmethod
    def quick_visualize(convergence_csv_path, output_dir="ga_plots"):
        """Quick visualization of convergence data"""
        df = pd.read_csv(convergence_csv_path)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Simple 2x1 plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Left: Fitness convergence
        ax1.plot(df['generation'], df['best_fitness'], 'b-o', linewidth=2, markersize=5, label='Best')
        ax1.plot(df['generation'], df['avg_fitness'], 'g-s', linewidth=2, markersize=5, label='Average')
        ax1.set_xlabel('Generation')
        ax1.set_ylabel('Fitness (s)')
        ax1.set_title('Fitness Convergence')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Right: Diversity and Improvement
        ax2.plot(df['generation'], df['diversity'], 'r-^', linewidth=2, markersize=5, label='Diversity')
        ax2.set_xlabel('Generation')
        ax2.set_ylabel('Diversity', color='red')
        ax2.tick_params(axis='y', labelcolor='red')
        ax2.set_ylim([0, 1.1])
        ax2.grid(True, alpha=0.3)
        
        ax2b = ax2.twinx()
        ax2b.plot(df['generation'], df['improvement_pct'], 'm-D', linewidth=2, markersize=5, label='Improvement %')
        ax2b.set_ylabel('Improvement (%)', color='magenta')
        ax2b.tick_params(axis='y', labelcolor='magenta')
        ax2.set_title('Diversity & Improvement')
        
        plt.tight_layout()
        
        output_path = f"{output_dir}/quick_convergence.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.show()
        
        print(f"✓ Quick convergence plot saved to: {output_path}")
        return df