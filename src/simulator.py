import traci
import sys
import os
from datetime import datetime
from config import Config as c

class Simulator:
    """SUMO traffic simulator with TraCI interface"""
    
    # Configuration from config.py
    network_file = c.PATH_TO_NETWORK
    route_file = c.PATH_TO_ROUTE
    config_file = c.PATH_TO_SUMOCONFIG
    tl_id = c.JUNCTION_ID
    steps = c.SIM_STEPS

    def apply_new_tlogic(self, gene, debug=False):
        """Apply new traffic light timing to SUMO"""
        logics = traci.trafficlight.getAllProgramLogics(self.tl_id)
        original_logic = logics[0]
        original_phases = original_logic.phases
        
        # Filter out yellow phases
        non_yellow_phases = []
        for phase in original_phases:
            if not any(c in 'yY' for c in phase.state):
                non_yellow_phases.append(phase)
        
        # Apply gene durations to non-yellow phases
        new_phases = []
        gene_idx = 0
        
        for old_phase in original_phases:
            if any(c in 'yY' for c in old_phase.state):
                # Keep yellow phase with original duration
                new_phases.append(old_phase)
            else:
                # Apply gene duration to green phases
                new_phase = traci.trafficlight.Phase(
                    duration=float(gene[gene_idx]),
                    state=old_phase.state,
                    minDur=old_phase.minDur,
                    maxDur=old_phase.maxDur
                )
                new_phases.append(new_phase)
                gene_idx += 1
        
        # Create and apply new logic
        new_logic = traci.trafficlight.Logic(
            programID=f"optimized_{traci.simulation.getTime()}",
            type=original_logic.type,
            currentPhaseIndex=original_logic.currentPhaseIndex,
            phases=new_phases,
            subParameter=original_logic.subParameter
        )
        
        traci.trafficlight.setProgramLogic(self.tl_id, new_logic)
        
        if debug:
            print(f"Applied gene {gene} to {self.tl_id}")

    def simulate(self, gene=None, debug=False):
        """Run simulation with optional traffic light timing"""
        
        # SUMO command parameters
        sumo_cmd = [
            "sumo",
            "-c", self.config_file,
            "--no-step-log",
            "--quit-on-end",
            "--no-warnings",
            "--time-to-teleport", "300",
        ]

        # Statistics tracking
        stats = {
            'total_steps': 0,
            'vehicle_stats': {},
            'total_waiting_time': 0,
            'total_time_loss': 0,
            'total_queue_length': 0,
            'departed_count': 0,
            'arrived_count': 0,
            'running_vehicles': 0,
        }

        # Vehicle tracking sets
        departed_vehicles = set()
        arrived_vehicles = set()

        # Start SUMO simulation
        traci.start(sumo_cmd)

        # Apply new traffic light timing if provided
        if gene is not None:
            self.apply_new_tlogic(gene)

        # Simulation timing
        cum_steps = 0
        start_time = datetime.now()

        # Main simulation loop
        for _ in range(self.steps):
            traci.simulationStep()
            current_time = traci.simulation.getTime()
            cum_steps += 1
            stats["total_steps"] = cum_steps

            # Track vehicle departures and arrivals
            departed_this_step = traci.simulation.getDepartedIDList()
            arrived_this_step = traci.simulation.getArrivedIDList()

            for veh_id in departed_this_step:
                departed_vehicles.add(veh_id)
                stats['vehicle_stats'][veh_id] = {
                    'departure_time': current_time,
                    'waiting_time': 0,
                    'time_loss': 0,
                    'arrived': False,
                }

            for veh_id in arrived_this_step:
                arrived_vehicles.add(veh_id)
                if veh_id in stats['vehicle_stats']:
                    stats['vehicle_stats'][veh_id]['arrived'] = True
                    stats['vehicle_stats'][veh_id]['arrival_time'] = current_time
                    stats['vehicle_stats'][veh_id]['travel_time'] = (
                        current_time - stats['vehicle_stats'][veh_id]['departure_time']
                    )
            
            # Update current vehicles
            current_vehicle_ids = traci.vehicle.getIDList()
            stats['running_vehicles'] = len(current_vehicle_ids)

            # Calculate waiting time and time loss
            step_waiting = 0
            for veh_id in current_vehicle_ids:
                if veh_id in stats['vehicle_stats']:
                    speed = traci.vehicle.getSpeed(veh_id)
                    if speed < 0.1:  # Vehicle is waiting
                        waiting_increment = 1
                        stats['vehicle_stats'][veh_id]['waiting_time'] += waiting_increment
                        stats['total_waiting_time'] += waiting_increment
                        step_waiting += waiting_increment

                    stats['vehicle_stats'][veh_id]['time_loss'] = traci.vehicle.getTimeLoss(veh_id)

            # Calculate queue length
            step_queue_length = sum(
                1 for veh_id in traci.vehicle.getIDList() 
                if traci.vehicle.getSpeed(veh_id) < 0.1
            )
            stats['total_queue_length'] += step_queue_length

            # Debug progress
            if (cum_steps % 100 == 0) and debug:
                print(f"  Step {current_time:.0f}s: "
                      f"Running: {len(current_vehicle_ids)}, "
                      f"Departed: {len(departed_vehicles)}, "
                      f"Arrived: {len(arrived_vehicles)}")
                
            # Safety stop
            if current_time > 86400:
                print("Warning: Simulation exceeded 24 hours, stopping.")
                break
        
        # End simulation timing
        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()

        # Finalize statistics
        stats['departed_count'] = len(departed_vehicles)
        stats['arrived_count'] = len(arrived_vehicles)
        
        # Calculate averages
        stats['average_waiting_time'] = (
            stats['total_waiting_time'] / stats['departed_count'] 
            if stats['departed_count'] > 0 else 0
        )
        
        for veh_id in arrived_vehicles:
            if veh_id in stats['vehicle_stats']:
                stats['total_time_loss'] += stats['vehicle_stats'][veh_id]['time_loss']
        
        stats['average_time_loss'] = (
            stats['total_time_loss'] / stats['arrived_count'] 
            if stats['arrived_count'] > 0 else 0
        )
        
        stats['average_queue_length'] = stats['total_queue_length'] / cum_steps

        # Close TraCI connection
        traci.close()

        # Debug output
        if debug:
            print("\n=== SIMULATION RESULTS ===")
            print(f"Simulation time: {elapsed_time:.1f}s real, {cum_steps}s simulated")
            print(f"Vehicles: {stats['departed_count']} departed, {stats['arrived_count']} arrived")
            print(f"Average waiting time: {stats['average_waiting_time']:.2f}s")
            print(f"Average time loss: {stats['average_time_loss']:.2f}s")
            print(f"Average queue length: {stats['average_queue_length']:.2f} vehicles")
            print(f"Total waiting time: {stats['total_waiting_time']}s")
            print("==========================\n")

        return stats