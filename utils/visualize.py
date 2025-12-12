from ga_visualizer import GAVisualizer

output_path = "./output/results/result_2/"
convergence_csv = "convergence_20251213_004307.csv"
gene_statistics_csv = "gene_statistics_20251213_004307.csv"
plot_output = "ga_plots/plots_2"

# Visualize convergence data
convergence_df = GAVisualizer.visualize_convergence(output_path+convergence_csv, output_dir=plot_output)

# Visualize gene statistics
gene_df = GAVisualizer.visualize_gene_statistics(output_path+gene_statistics_csv, output_dir=plot_output)

# Create comprehensive comparison
'''GAVisualizer.visualize_comparison(
    convergence_csv_path="ga_results/ga_convergence_20241201_143022.csv",
    gene_stats_csv_path="ga_results/gene_statistics_20241201_143022.csv",
    output_dir="ga_plots"
)'''