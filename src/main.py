from genetic_algorithm import GA
from config import Config as c
from ga_exporter import GAExporter
from ga_exporter_2 import SimpleGAExporter

import xml.etree.ElementTree as ET

def get_gene_from_network(network_file_path, junction_id="j1"):
    tree = ET.parse(network_file_path)
    root = tree.getroot()
    
    tl_logic = None
    for elem in root.iter('tlLogic'):
        if elem.get('id') == junction_id:
            tl_logic = elem
            break
    
    if tl_logic is None:
        print(f"Error: Traffic light '{junction_id}' not found")
        return None
    
    gene = []
    phases = list(tl_logic.findall('phase'))
    
    # Filter only green phases (typically every other phase, starting from 0)
    for i, phase in enumerate(phases):
        if i % 2 == 0:  # Even indices are green phases
            duration = phase.get('duration')
            if duration:
                gene.append(float(duration))
    
    # Alternative: Filter by state (contains 'G' for green)
    # gene = []
    # for phase in phases:
    #     state = phase.get('state', '')
    #     if 'G' in state:  # This is a green phase
    #         duration = phase.get('duration')
    #         if duration:
    #             gene.append(float(duration))
    
    if not gene:
        print(f"Error: No green phases found for '{junction_id}'")
        return None
    
    print(f"Found {len(gene)} green phases: {gene}")
    return gene

# ================================ #
# ENTRY
# ================================ #
gene = get_gene_from_network(c.PATH_TO_NETWORK, c.JUNCTION_ID)



ga = GA()

# PARALLEL WITH STATS
best_genes, best_fitness, baseline_fitness, history = ga.run_ga_parallel_with_stats(gene)

SimpleGAExporter.export_parallel_results(
    best_genes=best_genes,
    best_fitness=best_fitness,
    baseline_fitness=baseline_fitness,
    history=history,
    output_dir="./output/results/result_3"
)


