from ga_visualizer import GAVisualizer

output_path = "./output/tests/test1/"
convergence_csv = "convergence_20251206_153834.csv"
gene_statistics_csv = "gene_statistics_20251206_153834.csv"

# Visualize convergence data
convergence_df = GAVisualizer.visualize_convergence(output_path+convergence_csv)

# Visualize gene statistics
gene_df = GAVisualizer.visualize_gene_statistics(output_path+gene_statistics_csv)

# Create comprehensive comparison
'''GAVisualizer.visualize_comparison(
    convergence_csv_path="ga_results/ga_convergence_20241201_143022.csv",
    gene_stats_csv_path="ga_results/gene_statistics_20241201_143022.csv",
    output_dir="ga_plots"
)'''