#!/usr/bin/env python3
"""
Fixed SUMO simulation runner using TraCI
Accurate vehicle counting and statistics
"""

import traci
import sys
import os
from datetime import datetime

def run_simulation_with_traci(config_path):
    """
    Run SUMO simulation using TraCI and collect accurate statistics
    """
    
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        return None
    
    print(f"Starting simulation with config: {config_path}")
    print("=" * 60)
    
    try:
        # Start SUMO with TraCI
        sumo_cmd = [
            "sumo",
            "-c", config_path,
            "--no-step-log",
            "--quit-on-end",
            "--no-warnings", 
            "--time-to-teleport", "300",  # Teleport stuck vehicles after 300 seconds
        ]
        
        traci.start(sumo_cmd)
        
        # Initialize statistics
        stats = {
            'start_time': datetime.now(),
            'total_steps': 0,
            'vehicle_stats': {},
            'waiting_time': 0,
            'total_travel_time': 0,
            'total_distance': 0,
            'departed_count': 0,
            'arrived_count': 0,
            'teleported_count': 0,
            'collisions': 0,
            'loaded_count': 0,
            'running_vehicles': 0,
            'step_by_step_counts': []  # For debugging
        }
        
        print("Simulation running...")
        
        # Track vehicles that have departed and arrived
        departed_vehicles = set()
        arrived_vehicles = set()
        teleported_vehicles = set()
        
        # Main simulation loop
        step = 0
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            current_time = traci.simulation.getTime()
            step += 1
            stats['total_steps'] = step
            
            # Get vehicles that departed in this step
            try:
                departed_this_step = traci.simulation.getDepartedIDList()
            except:
                try:
                    departed_this_step = traci.simulation.getDepartedIDs()
                except:
                    departed_this_step = []
            
            # Get vehicles that arrived in this step
            try:
                arrived_this_step = traci.simulation.getArrivedIDList()
            except:
                try:
                    arrived_this_step = traci.simulation.getArrivedIDs()
                except:
                    arrived_this_step = []
            
            # Get vehicles that teleported in this step
            try:
                teleported_this_step = traci.simulation.getStartingTeleportIDList()
            except:
                try:
                    teleported_this_step = traci.simulation.getTeleportStartingIDs()
                except:
                    teleported_this_step = []
            
            # Update sets
            for veh_id in departed_this_step:
                departed_vehicles.add(veh_id)
                # Initialize tracking for new vehicle
                stats['vehicle_stats'][veh_id] = {
                    'departure_time': current_time,
                    'waiting_time': 0,
                    'distance': 0,
                    'arrived': False,
                    'teleported': False
                }
            
            for veh_id in arrived_this_step:
                arrived_vehicles.add(veh_id)
                if veh_id in stats['vehicle_stats']:
                    stats['vehicle_stats'][veh_id]['arrived'] = True
                    stats['vehicle_stats'][veh_id]['arrival_time'] = current_time
                    stats['vehicle_stats'][veh_id]['travel_time'] = (
                        current_time - stats['vehicle_stats'][veh_id]['departure_time']
                    )
            
            for veh_id in teleported_this_step:
                teleported_vehicles.add(veh_id)
                if veh_id in stats['vehicle_stats']:
                    stats['vehicle_stats'][veh_id]['teleported'] = True
            
            # Collect statistics for currently running vehicles
            current_vehicle_ids = traci.vehicle.getIDList()
            stats['running_vehicles'] = len(current_vehicle_ids)
            
            step_waiting = 0
            for veh_id in current_vehicle_ids:
                if veh_id in stats['vehicle_stats']:
                    # Update waiting time
                    speed = traci.vehicle.getSpeed(veh_id)
                    if speed < 0.1:  # Vehicle is waiting
                        waiting_increment = 1
                        stats['vehicle_stats'][veh_id]['waiting_time'] += waiting_increment
                        stats['waiting_time'] += waiting_increment
                        step_waiting += waiting_increment
                    
                    # Update distance
                    try:
                        stats['vehicle_stats'][veh_id]['distance'] = traci.vehicle.getDistance(veh_id)
                    except:
                        pass  # Some vehicles might not have distance yet
            
            # Store step counts for debugging
            stats['step_by_step_counts'].append({
                'time': current_time,
                'running': len(current_vehicle_ids),
                'departed_this_step': len(departed_this_step),
                'arrived_this_step': len(arrived_this_step),
                'waiting': step_waiting
            })
            
            # Show progress
            if step % 100 == 0:
                print(f"  Step {current_time:.0f}s: "
                      f"Running: {len(current_vehicle_ids)}, "
                      f"Departed: {len(departed_vehicles)}, "
                      f"Arrived: {len(arrived_vehicles)}")
            
            # Safety stop
            if current_time > 86400:  # 24 hours
                print("Warning: Simulation exceeded 24 hours, stopping.")
                break
        
        # Final calculations
        stats['end_time'] = datetime.now()
        stats['simulation_duration'] = (stats['end_time'] - stats['start_time']).total_seconds()
        
        # Calculate final statistics
        stats['departed_count'] = len(departed_vehicles)
        stats['arrived_count'] = len(arrived_vehicles)
        stats['teleported_count'] = len(teleported_vehicles)
        stats['loaded_count'] = stats['departed_count']  # In TraCI, loaded = departed
        
        # Calculate total travel time and distance from arrived vehicles
        total_travel_time = 0
        total_distance = 0
        arrived_with_stats = 0
        
        for veh_id in arrived_vehicles:
            if veh_id in stats['vehicle_stats']:
                veh_stats = stats['vehicle_stats'][veh_id]
                if 'travel_time' in veh_stats:
                    total_travel_time += veh_stats['travel_time']
                    total_distance += veh_stats.get('distance', 0)
                    arrived_with_stats += 1
        
        stats['total_travel_time'] = total_travel_time
        stats['total_distance'] = total_distance
        stats['arrived_with_stats'] = arrived_with_stats
        
        # Calculate average waiting time from all vehicles that completed trips
        completed_vehicles = arrived_vehicles.union(teleported_vehicles)
        total_waiting_completed = 0
        for veh_id in completed_vehicles:
            if veh_id in stats['vehicle_stats']:
                total_waiting_completed += stats['vehicle_stats'][veh_id].get('waiting_time', 0)
        
        stats['waiting_time_completed'] = total_waiting_completed
        
        traci.close()
        
        print("\n" + "=" * 60)
        print("SIMULATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        return stats
        
    except Exception as e:
        print(f"Error during simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def print_summary(stats):
    """Print accurate summary"""
    
    if not stats:
        print("No statistics to display")
        return
    
    print("\n" + "=" * 60)
    print("ACCURATE SIMULATION SUMMARY")
    print("=" * 60)
    
    print(f"\n1. SIMULATION OVERVIEW:")
    print(f"   - Simulation duration: {stats['simulation_duration']:.2f} real seconds")
    print(f"   - Simulation steps: {stats['total_steps']}")
    
    print(f"\n2. VEHICLE COUNTS (ACCURATE):")
    print(f"   - Loaded vehicles: {stats['loaded_count']}")
    print(f"   - Departed vehicles: {stats['departed_count']}")
    print(f"   - Arrived vehicles: {stats['arrived_count']}")
    print(f"   - Teleported vehicles: {stats['teleported_count']}")
    print(f"   - Total completed: {stats['arrived_count'] + stats['teleported_count']}")
    
    print(f"\n3. PERFORMANCE METRICS:")
    print(f"   - Total waiting time (all steps): {stats['waiting_time']:.2f} seconds")
    print(f"   - Waiting time (completed vehicles): {stats['waiting_time_completed']:.2f} seconds")
    
    if stats['arrived_count'] > 0:
        print(f"\n4. ARRIVED VEHICLE STATISTICS:")
        print(f"   - Arrived with complete stats: {stats['arrived_with_stats']}")
        print(f"   - Total travel time: {stats['total_travel_time']:.2f} seconds")
        print(f"   - Total distance: {stats['total_distance']:.2f} meters")
        
        if stats['arrived_with_stats'] > 0:
            avg_travel = stats['total_travel_time'] / stats['arrived_with_stats']
            avg_waiting = stats['waiting_time_completed'] / stats['arrived_count']
            avg_distance = stats['total_distance'] / stats['arrived_with_stats']
            
            print(f"   - Average travel time: {avg_travel:.2f} seconds")
            print(f"   - Average waiting time: {avg_waiting:.2f} seconds")
            print(f"   - Average distance: {avg_distance:.2f} meters")
            if avg_travel > 0:
                print(f"   - Waiting percentage: {(avg_waiting/avg_travel*100):.1f}%")
    
    # Show vehicle stats sample
    print(f"\n5. VEHICLE DETAILS (sample of completed vehicles):")
    vehicle_stats = stats['vehicle_stats']
    completed_count = 0
    sample_count = 0
    
    for veh_id, veh_data in vehicle_stats.items():
        if veh_data.get('arrived', False) or veh_data.get('teleported', False):
            completed_count += 1
            if sample_count < 5:  # Show first 5 completed
                status = "Arrived" if veh_data.get('arrived') else "Teleported"
                travel_time = veh_data.get('travel_time', 'N/A')
                waiting = veh_data.get('waiting_time', 0)
                distance = veh_data.get('distance', 0)
                
                if sample_count == 0:
                    print("   ID          | Status    | Travel Time | Waiting Time | Distance")
                    print("   " + "-" * 65)
                
                if travel_time != 'N/A':
                    print(f"   {veh_id:12} | {status:9} | {travel_time:11.1f} | {waiting:12.1f} | {distance:.1f}m")
                else:
                    print(f"   {veh_id:12} | {status:9} | {'N/A':11} | {waiting:12.1f} | {distance:.1f}m")
                
                sample_count += 1
    
    if completed_count > 5:
        print(f"   ... and {completed_count - 5} more completed vehicles")
    
    # Debug: Show step-by-step counts if needed
    debug_option = input("\nShow detailed step counts? (y/n, can be large): ").strip().lower()
    if debug_option == 'y' and stats['step_by_step_counts']:
        print(f"\nFirst 10 steps:")
        for i, step_data in enumerate(stats['step_by_step_counts'][:10]):
            print(f"  Step {step_data['time']:.1f}s: "
                  f"Running: {step_data['running']}, "
                  f"Departed: {step_data['departed_this_step']}, "
                  f"Arrived: {step_data['arrived_this_step']}")
    
    print("\n" + "=" * 60)
    print("Note: Counts tracked using TraCI's getDepartedIDList/getArrivedIDList")
    print("=" * 60)

def main():
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = input("Enter path to SUMO configuration file: ").strip()
    
    stats = run_simulation_with_traci(config_path)
    
    if stats:
        print_summary(stats)
        
        # For GA: This is the total waiting time to minimize
        print(f"\nFOR GENETIC ALGORITHM FITNESS FUNCTION:")
        print(f"Total waiting time to minimize: {stats['waiting_time']:.2f}")
        print(f"Alternative: Waiting time of completed vehicles: {stats['waiting_time_completed']:.2f}")
        
        save_option = input("\nSave results for GA? (y/n): ").strip().lower()
        if save_option == 'y':
            import json
            filename = f"ga_fitness_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Prepare data for GA
            ga_data = {
                'fitness': stats['waiting_time'],  # Primary fitness value
                'waiting_time': stats['waiting_time'],
                'waiting_time_completed': stats['waiting_time_completed'],
                'arrived_vehicles': stats['arrived_count'],
                'departed_vehicles': stats['departed_count'],
                'simulation_steps': stats['total_steps'],
                'simulation_duration': stats['simulation_duration']
            }
            
            with open(filename, 'w') as f:
                json.dump(ga_data, f, indent=2)
            print(f"GA fitness data saved to {filename}")

if __name__ == "__main__":
    main()