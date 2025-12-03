from genetic_algorithm import GA
from config import Config as c
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
    for phase in tl_logic.findall('phase'):
        duration = phase.get('duration')
        if duration:
            gene.append(float(duration))
    
    if not gene:
        print(f"Error: No phases found for '{junction_id}'")
        return None
    
    return gene

# ================================ #
# ENTRY
# ================================ #
gene = get_gene_from_network(c.PATH_TO_NETWORK, c.JUNCTION_ID)
ga = GA()
ga.run_ga([15,15,15,15])