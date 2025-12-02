#!/usr/bin/env python3
import os

def create_config():
    print("SUMO Config Generator")
    print(f"Current directory: {os.getcwd()}")
    print("-" * 40)
    
    # Show files in data/ directory
    if os.path.exists("data"):
        files = os.listdir("data")
        net_files = [f for f in files if f.endswith('.net.xml')]
        route_files = [f for f in files if f.endswith('.rou.xml')]
        
        if net_files:
            print("Network files in data/:")
            for f in net_files:
                print(f"  {f}")
            print()
        
        if route_files:
            print("Route files in data/:")
            for f in route_files:
                print(f"  {f}")
            print()
    
    # Get just the filenames (no path)
    net_file = input("Network filename (e.g., 6l_4w_4p.net.xml): ").strip()
    route_file = input("Route filename (e.g., 6l_4w_4p_mixed.rou.xml): ").strip()
    
    config_file = input("Config filename (e.g., 6l_4w_4p.sumocfg): ").strip()
    if not config_file:
        config_file = net_file.replace('.net.xml', '.sumocfg')
    
    # Ensure output goes to data/ folder
    if not config_file.startswith("data/"):
        config_file = f"data/{config_file}"
    
    # Build config - paths are relative to config file location (same folder)
    config = f'''<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <!-- All files are in the same folder -->
        <net-file value="{net_file}"/>
        <route-files value="{route_file}"/>
    </input>
    <processing>
        <lateral-resolution value="0.25"/>
    </processing>
    <time>
        <begin value="0"/>
        <end value="3600"/>
    </time>
</configuration>'''
    
    with open(config_file, 'w') as f:
        f.write(config)
    
    print(f"Created: {config_file}")

if __name__ == "__main__":
    create_config()