import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from matplotlib.gridspec import GridSpec
import seaborn as sns

class GAVisualizer:
    """Visualize GA convergence and gene statistics"""
    
    @staticmethod
    def visualize_convergence(convergence_csv_path, output_dir="ga_plots"):
        """
        Visualize GA convergence metrics
        
        Args:
            convergence_csv_path: Path to convergence CSV file
            output_dir: Directory to save plots
        """
        # Read data
        df = pd.read_csv(convergence_csv_path)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(15, 10))
        gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
        
        # Plot 1: Best Fitness over Generations
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.plot(df['generation'], df['best_fitness'], 'b-', linewidth=2, marker='o', markersize=4)
        ax1.set_xlabel('Generation')
        ax1.set_ylabel('Best Fitness (s)')
        ax1.set_title('Best Fitness Convergence')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(bottom=0)
        
        # Add improvement annotation
        if len(df) > 1:
            improvement = df['best_fitness'].iloc[0] - df['best_fitness'].iloc[-1]
            ax1.annotate(f'Improvement: {improvement:.1f}s\n({df["improvement_pct"].iloc[-1]:.1f}%)',
                        xy=(df['generation'].iloc[-1], df['best_fitness'].iloc[-1]),
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5))
        
        # Plot 2: Average Fitness over Generations
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.plot(df['generation'], df['avg_fitness'], 'g-', linewidth=2, marker='s', markersize=4)
        ax2.set_xlabel('Generation')
        ax2.set_ylabel('Average Fitness (s)')
        ax2.set_title('Average Fitness Convergence')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(bottom=0)
        
        # Shaded area showing std
        ax2.fill_between(df['generation'], 
                        df['avg_fitness'] - df['fitness_std'],
                        df['avg_fitness'] + df['fitness_std'],
                        alpha=0.2, color='green', label='±1 std')
        ax2.legend()
        
        # Plot 3: Fitness Comparison (Best vs Average)
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.plot(df['generation'], df['best_fitness'], 'b-', linewidth=2, label='Best')
        ax3.plot(df['generation'], df['avg_fitness'], 'g-', linewidth=2, label='Average')
        ax3.set_xlabel('Generation')
        ax3.set_ylabel('Fitness (s)')
        ax3.set_title('Best vs Average Fitness')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        ax3.set_ylim(bottom=0)
        
        # Plot 4: Population Diversity
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.plot(df['generation'], df['diversity'], 'r-', linewidth=2, marker='^', markersize=4)
        ax4.set_xlabel('Generation')
        ax4.set_ylabel('Diversity')
        ax4.set_title('Population Diversity')
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim([0, 1.1])
        
        # Plot 5: Improvement Percentage
        ax5 = fig.add_subplot(gs[2, 0])
        ax5.plot(df['generation'], df['improvement_pct'], 'm-', linewidth=2, marker='D', markersize=4)  # Fixed: 'm' for magenta/purple
        ax5.set_xlabel('Generation')
        ax5.set_ylabel('Improvement (%)')
        ax5.set_title('Improvement Over Baseline')
        ax5.grid(True, alpha=0.3)
        ax5.set_ylim(bottom=0)
        
        # Add final value annotation
        if len(df) > 0:
            final_improvement = df['improvement_pct'].iloc[-1]
            ax5.annotate(f'{final_improvement:.1f}%',
                        xy=(df['generation'].iloc[-1], df['improvement_pct'].iloc[-1]),
                        xytext=(10, 10), textcoords='offset points',
                        fontweight='bold', color='darkred')
        
        # Plot 6: Fitness Standard Deviation
        ax6 = fig.add_subplot(gs[2, 1])
        ax6.plot(df['generation'], df['fitness_std'], color='orange', linewidth=2, marker='v', markersize=4)  # Fixed: color='orange'
        ax6.set_xlabel('Generation')
        ax6.set_ylabel('Fitness Std Dev')
        ax6.set_title('Fitness Standard Deviation')
        ax6.grid(True, alpha=0.3)
        ax6.set_ylim(bottom=0)
        
        plt.suptitle('Genetic Algorithm Convergence Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Save plot
        output_path = f"{output_dir}/convergence_analysis.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.show()
        
        print(f"✓ Convergence plots saved to: {output_path}")
        
        # Also create individual plots
        GAVisualizer._create_individual_plots(df, output_dir)
        
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