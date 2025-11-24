# Converts OSM output file to SUMO readable

import subprocess
import os
from pathlib import Path

def convert_osm_to_sumo(filename):
    # Remove .osm extension if user included it
    filename = filename.replace('.osm', '')
    
    project_root = Path(__file__).parent.parent
    osm_path = project_root / "data" / "osm" / (filename + ".osm")
    network_path = project_root / "data" / "networks" / (filename + ".net.xml")
    
    if not osm_path.exists():
        print(f"Error: cannot find {osm_path}")
        return
    
    os.makedirs(project_root / "data" / "networks", exist_ok=True)

    cmd = [
        "netconvert",
        "--osm-files", str(osm_path),
        "--output-file", str(network_path),
        "--tls.guess-signals", "true",
        "--tls.discard-simple", "true", 
        "--default.lanenumber", "2",
        "--default.speed", "13.89"
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"{filename}.osm converted to SUMO network: {network_path}")
        
        # Verify the file was created
        if network_path.exists():
            print(f"Network file successfully created: {network_path}")
        else:
            print(f"Network file was not created at expected location")
            
    except Exception as e:
        print(f"Failed to convert. Error: {e}")

if __name__ == "__main__":
    filename = input("Enter .osm filename (without extension): ").strip()
    convert_osm_to_sumo(filename)
