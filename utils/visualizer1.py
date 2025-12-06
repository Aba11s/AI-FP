import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
import seaborn as sns

# Load your data (assuming it's in a CSV file)
df = pd.read_csv('./output/test1/generation_summary_20251205_190557.csv')

# Or if you have it as a string, use:
# data = """your,csv,data,here..."""
# df = pd.read_csv(pd.compat.StringIO(data))

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create figure with subplots
fig, axes = plt.subplots(3, 2, figsize=(16, 12))
fig.suptitle('Genetic Algorithm Performance Analysis', fontsize=16, fontweight='bold')

# 1. Fitness over generations (top-left)
ax1 = axes[0, 0]
ax1.plot(df['generation'], df['best_fitness'], 'o-', linewidth=2, markersize=6, label='Best Fitness', color='#2E86AB')
ax1.plot(df['generation'], df['avg_fitness'], 's--', linewidth=1.5, markersize=4, label='Average Fitness', color='#A23B72')
ax1.set_xlabel('Generation')
ax1.set_ylabel('Delay (seconds)')
ax1.set_title('Fitness Evolution (Delay)')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_locator(MaxNLocator(integer=True))

# 2. Queue length over generations (top-right)
ax2 = axes[0, 1]
ax2.plot(df['generation'], df['best_queue_length'], 'o-', linewidth=2, markersize=6, label='Best Queue', color='#18A999')
ax2.plot(df['generation'], df['avg_queue_length'], 's--', linewidth=1.5, markersize=4, label='Average Queue', color='#F18F01')
ax2.set_xlabel('Generation')
ax2.set_ylabel('Queue Length (vehicles)')
ax2.set_title('Queue Length Evolution')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_locator(MaxNLocator(integer=True))

# 3. Waiting time over generations (middle-left)
ax3 = axes[1, 0]
ax3.plot(df['generation'], df['best_waiting_time'], 'o-', linewidth=2, markersize=6, label='Best Waiting', color='#C73E1D')
ax3.plot(df['generation'], df['avg_waiting_time'], 's--', linewidth=1.5, markersize=4, label='Average Waiting', color='#6A8EAE')
ax3.set_xlabel('Generation')
ax3.set_ylabel('Waiting Time (seconds)')
ax3.set_title('Waiting Time Evolution')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.xaxis.set_major_locator(MaxNLocator(integer=True))

# 4. Improvement rate (middle-right)
ax4 = axes[1, 1]
improvement = df['best_fitness'].pct_change() * 100
improvement[0] = 0  # First generation has no previous to compare
ax4.bar(df['generation'], improvement, color=['#5C7E82' if x < 0 else '#E4572E' for x in improvement])
ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax4.set_xlabel('Generation')
ax4.set_ylabel('Improvement (%)')
ax4.set_title('Generation-over-Generation Improvement')
ax4.grid(True, alpha=0.3, axis='y')
ax4.xaxis.set_major_locator(MaxNLocator(integer=True))

# 5. Gene value evolution (bottom-left)
ax5 = axes[2, 0]
# Parse gene strings into lists
genes = df['best_gene'].apply(lambda x: eval(x) if isinstance(x, str) else x)
gene1 = [g[0] for g in genes]
gene2 = [g[1] for g in genes]
gene3 = [g[2] for g in genes]
gene4 = [g[3] for g in genes]

ax5.plot(df['generation'], gene1, 'o-', label='Gene 1', linewidth=2, markersize=5)
ax5.plot(df['generation'], gene2, 's-', label='Gene 2', linewidth=2, markersize=5)
ax5.plot(df['generation'], gene3, '^-', label='Gene 3', linewidth=2, markersize=5)
ax5.plot(df['generation'], gene4, 'd-', label='Gene 4', linewidth=2, markersize=5)
ax5.set_xlabel('Generation')
ax5.set_ylabel('Gene Value (seconds)')
ax5.set_title('Best Gene Evolution')
ax5.legend()
ax5.grid(True, alpha=0.3)
ax5.xaxis.set_major_locator(MaxNLocator(integer=True))
ax5.set_ylim([5, 35])  # Adjust based on your MIN/MAX_GREEN

# 6. Combined metrics (bottom-right)
ax6 = axes[2, 1]
# Normalize metrics for comparison
norm_best = (df['best_fitness'] - df['best_fitness'].min()) / (df['best_fitness'].max() - df['best_fitness'].min())
norm_queue = (df['best_queue_length'] - df['best_queue_length'].min()) / (df['best_queue_length'].max() - df['best_queue_length'].min())
norm_wait = (df['best_waiting_time'] - df['best_waiting_time'].min()) / (df['best_waiting_time'].max() - df['best_waiting_time'].min())

ax6.plot(df['generation'], norm_best, 'o-', label='Delay (norm)', linewidth=2, markersize=5)
ax6.plot(df['generation'], norm_queue, 's-', label='Queue (norm)', linewidth=2, markersize=5)
ax6.plot(df['generation'], norm_wait, '^-', label='Waiting (norm)', linewidth=2, markersize=5)
ax6.set_xlabel('Generation')
ax6.set_ylabel('Normalized Value (0-1)')
ax6.set_title('Normalized Metrics Comparison')
ax6.legend()
ax6.grid(True, alpha=0.3)
ax6.xaxis.set_major_locator(MaxNLocator(integer=True))

plt.tight_layout()
plt.show()

# Additional specialized plots
fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))

# 7. Convergence analysis
ax7 = axes2[0, 0]
convergence = (df['best_fitness'] - df['best_fitness'].min()) / df['best_fitness'].max()
ax7.plot(df['generation'], convergence, 'o-', linewidth=2, markersize=6, color='#2A9D8F')
ax7.axhline(y=0.05, color='red', linestyle='--', alpha=0.5, label='5% threshold')
ax7.set_xlabel('Generation')
ax7.set_ylabel('Convergence Ratio')
ax7.set_title('Convergence Analysis')
ax7.legend()
ax7.grid(True, alpha=0.3)

# 8. Diversity plot (avg vs best spread)
ax8 = axes2[0, 1]
spread = df['avg_fitness'] - df['best_fitness']
ax8.bar(df['generation'], spread, color='#E9C46A', alpha=0.7)
ax8.set_xlabel('Generation')
ax8.set_ylabel('Avg - Best (seconds)')
ax8.set_title('Population Diversity (Fitness Spread)')
ax8.grid(True, alpha=0.3, axis='y')

# 9. 3D gene evolution (if you have 3+ genes)
ax9 = axes2[1, 0]
ax9.scatter(gene1, gene2, c=df['generation'], cmap='viridis', s=50, alpha=0.7)
ax9.set_xlabel('Gene 1')
ax9.set_ylabel('Gene 2')
ax9.set_title('Gene 1 vs Gene 2 Evolution')
# Add generation colorbar
scatter = ax9.scatter(gene1, gene2, c=df['generation'], cmap='viridis', s=50, alpha=0.7)
plt.colorbar(scatter, ax=ax9, label='Generation')

# 10. Performance summary
ax10 = axes2[1, 1]
metrics = ['Initial', 'Final', 'Improvement']
values = [
    df['best_fitness'].iloc[0],
    df['best_fitness'].iloc[-1],
    (df['best_fitness'].iloc[0] - df['best_fitness'].iloc[-1]) / df['best_fitness'].iloc[0] * 100
]
bars = ax10.bar(metrics, values, color=['#E76F51', '#2A9D8F', '#E9C46A'])
ax10.set_ylabel('Delay (seconds) / %')
ax10.set_title('Performance Summary')
# Add value labels on bars
for bar, value in zip(bars, values):
    height = bar.get_height()
    ax10.text(bar.get_x() + bar.get_width()/2., height,
              f'{value:.1f}' if metrics[bars.index(bar)] != 'Improvement' else f'{value:.1f}%',
              ha='center', va='bottom')
ax10.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.show()

# Single comprehensive timeline
fig3, ax11 = plt.subplots(figsize=(12, 6))
ax11.plot(df['generation'], df['best_fitness'], 'o-', label='Best Delay', linewidth=2, markersize=6)
ax11.fill_between(df['generation'], df['best_fitness'], df['avg_fitness'], alpha=0.2, label='Population Range')
ax11.set_xlabel('Generation')
ax11.set_ylabel('Delay (seconds)', color='blue')
ax11.tick_params(axis='y', labelcolor='blue')
ax11.set_title('GA Evolution Timeline')

# Add second y-axis for queue length
ax12 = ax11.twinx()
ax12.plot(df['generation'], df['best_queue_length'], 's-', color='red', label='Best Queue', linewidth=2, markersize=4)
ax12.set_ylabel('Queue Length', color='red')
ax12.tick_params(axis='y', labelcolor='red')

# Combine legends
lines1, labels1 = ax11.get_legend_handles_labels()
lines2, labels2 = ax12.get_legend_handles_labels()
ax11.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Print key statistics
print("\n=== GA RUN STATISTICS ===")
print(f"Generations: {len(df)}")
print(f"Initial Best Delay: {df['best_fitness'].iloc[0]:.2f}s")
print(f"Final Best Delay: {df['best_fitness'].iloc[-1]:.2f}s")
print(f"Improvement: {((df['best_fitness'].iloc[0] - df['best_fitness'].iloc[-1]) / df['best_fitness'].iloc[0] * 100):.1f}%")
print(f"Best Solution Found at Generation: {df['best_fitness'].idxmin()}")
print(f"Best Gene: {df['best_gene'].iloc[df['best_fitness'].idxmin()]}")
print(f"Final Best Gene: {df['best_gene'].iloc[-1]}")
print("=========================\n")