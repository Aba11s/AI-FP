# simulates with traCi

import traci
import sys
import os
from datetime import datetime

from config import Config as c

class Simulator:
    network_file = c.PATH_TO_NETWORK
    route_file = c.PATH_TO_ROUTE
    config_file = c.PATH_TO_SUMOCONFIG
    tl_id = c.JUNCTION_ID
    steps = c.MAX_EVAL_STEPS

    def apply_new_tlogic(self, gene):
        logics = traci.trafficlight.getAllProgramLogics(self.tl_id)
        original_logic = logics[0]
        original_phases = original_logic.phases

        # create new phases
        new_phases = []
        for i, duration in enumerate(gene):
            old_phase = original_phases[i]

            new_phase = traci.trafficlight.Phase(
                duration=float(duration),  # Your gene duration
                state=old_phase.state,     # Keep original light pattern
                minDur=old_phase.minDur,   # Keep original min duration
                maxDur=old_phase.maxDur    # Keep original max duration
            )
            new_phases.append(new_phase)

        new_logic = traci.trafficlight.Logic(
            programID=f"optimized_{traci.simulation.getTime()}",
            type=original_logic.type,           # Keep original program type
            currentPhaseIndex=original_logic.currentPhaseIndex,
            phases=new_phases,
            subParameter=original_logic.subParameter
        )

        traci.trafficlight.setProgramLogic(self.tl_id, new_logic)
        current_phases = traci.trafficlight.getAllProgramLogics(self.tl_id)[0].phases
        applied_durations = [phase.duration for phase in current_phases]
        
        print(f"Applied gene {gene} to {self.tl_id}")

    def simulate(self, gene=None):
        
        # Command parameters
        sumo_cmd = [
            "sumo",
            "-c", self.config_file,
            "--no-step-log",
            "--quit-on-end",
            "--no-warnings", 
            "--time-to-teleport", "300",  # Teleport stuck vehicles after 300 seconds
        ]

        # define stats
        stats = {
            'total_steps': 0,
            'vehicle_stats': {}, # key: veh_id, value: dictionary of vehicle stats
            'total_waiting_time': 0,
            'departed_count': 0,
            'arrived_count': 0,
            'running_vehicles': 0,
        }

        print("Running Simulation")

        # Track vehicles that have departed and arrived
        departed_vehicles = set()
        arrived_vehicles = set()

        traci.start(sumo_cmd)

        # Get traffic light info
        programs = traci.trafficlight.getAllProgramLogics(self.tl_id)
        program = programs[0]
        
        phase_gene = []
        for phase in program.phases:
            phase_gene.append(phase.duration)

        print(phase_gene)

        # apply new tlogic if any
        if gene != None:
            self.apply_new_tlogic(gene)

        step = 0
        start_time = datetime.now()
        for _ in range(self.steps):
            traci.simulationStep() # runs a sim step
            current_time = traci.simulation.getTime()
            step += 1
            stats["total_steps"] = step

            # get list of vehicles this step
            departed_this_step = traci.simulation.getDepartedIDList()
            arrived_this_step = traci.simulation.getArrivedIDList()

            # update vehicles stats
            for id in departed_this_step:
                departed_vehicles.add(id)

                stats['vehicle_stats'][id] = {
                    'departure_time': current_time,
                    'waiting_time': 0,
                    'arrived': False,
                }

            for id in arrived_this_step:
                arrived_vehicles.add(id)
                if id in stats['vehicle_stats']:
                    stats['vehicle_stats'][id]['arrived'] = True
                    stats['vehicle_stats'][id]['arrival_time'] = current_time
                    stats['vehicle_stats'][id]['travel_time'] = (
                        current_time - stats['vehicle_stats'][id]['departure_time']
                    )

            # updates vehicles currently on the network
            current_vehicle_ids = traci.vehicle.getIDList()
            stats['running_vehicles'] = len(current_vehicle_ids)

            step_waiting = 0
            for id in current_vehicle_ids:
                if id in stats['vehicle_stats']:
                    # Update waiting time
                    speed = traci.vehicle.getSpeed(id)
                    if speed < 0.1:  # Vehicle is waiting
                        waiting_increment = 1
                        stats['vehicle_stats'][id]['waiting_time'] += waiting_increment
                        stats['total_waiting_time'] += waiting_increment
                        step_waiting += waiting_increment

            # show traffic light

            # Show progress every 100 steps
            if step % 100 == 0:
                print(f"  Step {current_time:.0f}s: "
                      f"Running: {len(current_vehicle_ids)}, "
                      f"Departed: {len(departed_vehicles)}, "
                      f"Arrived: {len(arrived_vehicles)}")
                
            # Safety stop
            if current_time > 86400:  # 24 hours
                print("Warning: Simulation exceeded 24 hours, stopping.")
                break
        
        # END OF LOOP #
        end_time = datetime.now()
        elapsed_time = (end_time-start_time).total_seconds()

        # Finalize stats
        stats['departed_count'] = len(departed_vehicles)
        stats['arrived_count'] = len(arrived_vehicles)
        
        # Calculate total waiitng time
        total_waiting_time = 0
        for id in arrived_vehicles:
            if id in stats['vehicle_stats']:
                total_waiting_time += stats['vehicle_stats'][id].get('waiting_time',0)

        stats['total_waiting_time'] = total_waiting_time
        stats['average_waiting_time'] = total_waiting_time / stats['departed_count']
        
        traci.close()
        print(f"DONE at: {elapsed_time}s")
        print(f"total waiting time: {stats['total_waiting_time']}s")
        print(f"average waiting time: {stats['average_waiting_time']}")
        print(f"arrived total: {stats['arrived_count']}")
        print(f"departed total: {stats['departed_count']}")

        return stats['average_waiting_time']