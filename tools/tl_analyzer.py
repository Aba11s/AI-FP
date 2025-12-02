#!/usr/bin/env python3
"""
Simple Traffic Light Analyzer for SUMO networks
"""

import xml.etree.ElementTree as ET
import os
import glob

def find_network_files():
    """Look for network files in common directories"""
    search_paths = [
        ".",
        "data",
        "..",
        "../data",
        "networks"
    ]
    
    network_files = []
    for path in search_paths:
        if os.path.exists(path):
            files = glob.glob(os.path.join(path, "*.net.xml"))
            network_files.extend(files)
    
    return network_files

def analyze_traffic_lights(network_file):
    """
    Analyze traffic lights in a SUMO network file
    """
    print(f"\nAnalyzing: {network_file}")
    print("-" * 50)
    
    try:
        tree = ET.parse(network_file)
        root = tree.getroot()
    except Exception as e:
        print(f"Error: Could not parse file - {e}")
        return
    
    # Find all tlLogic elements
    tl_elements = root.findall(".//tlLogic")
    
    if not tl_elements:
        print("No traffic lights found.")
        return
    
    print(f"Found {len(tl_elements)} traffic light(s)")
    
    for tl in tl_elements:
        tl_id = tl.get('id', 'unknown')
        tl_type = tl.get('type', 'unknown')
        
        print(f"\nTraffic Light ID: {tl_id}")
        print(f"Type: {tl_type}")
        print(f"Program ID: {tl.get('programID', '0')}")
        
        phases = tl.findall('phase')
        print(f"Number of phases: {len(phases)}")
        
        total_cycle = 0
        phase_durations = []
        
        for i, phase in enumerate(phases):
            duration = float(phase.get('duration', '0'))
            state = phase.get('state', '')
            name = phase.get('name', f'Phase {i+1}')
            
            total_cycle += duration
            phase_durations.append(duration)
            
            print(f"\n  Phase {i+1}: {name}")
            print(f"    Duration: {duration}s")
            print(f"    State: {state}")
            
            # Simple signal count
            if state:
                print(f"    Green signals: {state.count('G') + state.count('g')}")
                print(f"    Red signals: {state.count('r')}")
        
        print(f"\n  Total cycle time: {total_cycle}s")
        print(f"  Phase durations: {phase_durations}")
        print("-" * 50)

def main():
    """
    Interactive main function
    """
    print("SUMO Traffic Light Analyzer")
    print("=" * 30)
    
    # First, look for network files automatically
    network_files = find_network_files()
    
    if network_files:
        print("\nFound network files:")
        for i, file in enumerate(network_files, 1):
            print(f"  {i}. {file}")
        print("  0. Enter custom path")
    else:
        print("\nNo network files found automatically.")
    
    # Get user choice
    while True:
        try:
            if network_files:
                choice = input("\nSelect a file (number) or enter custom path: ").strip()
                
                if choice == "0":
                    network_path = input("Enter full path to network file: ").strip()
                else:
                    idx = int(choice) - 1
                    if 0 <= idx < len(network_files):
                        network_path = network_files[idx]
                    else:
                        print("Invalid selection. Try again.")
                        continue
            else:
                network_path = input("\nEnter path to network file (.net.xml): ").strip()
            
            # Check if file exists
            if not os.path.exists(network_path):
                print(f"File not found: {network_path}")
                continue
            
            if not network_path.endswith('.net.xml'):
                print("Warning: File doesn't have .net.xml extension")
                confirm = input("Continue anyway? (y/n): ").lower()
                if confirm != 'y':
                    continue
            
            # Analyze the file
            analyze_traffic_lights(network_path)
            
            # Ask if user wants to analyze another file
            again = input("\nAnalyze another file? (y/n): ").lower()
            if again != 'y':
                break
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()