import os
import sys
import time
import random

from config import Config as c
from simulator import Simulator
from crossover import Crossover

class GA:
    def __init__(self):
        print("Initializing Systems. . .")
        time.sleep(2)
        print("Compiling Dependencies. . .")
        time.sleep(3)
        print("Establishing Satellite Link. . .")
        time.sleep(1)
        print("ALL SYSTEMS INITIALIZED")
        time.sleep(1)

    def create_initial_population(self, base_gene):
        popsize = c.POPULATION - 1

        population = [base_gene]

        for _ in range(popsize):
            gene = []
            for base_duration in base_gene:
                variation = random.uniform(0.7, 1.3)
                new_duration = int(base_duration * variation)
                new_duration = max(10, min(90, new_duration))
                gene.append(new_duration)
            
            population.append(gene)

        return population
    
    def tournament_selection(self, fitnesses, tournament_size=3, select_count=None):
        if select_count is None:
            select_count = len(fitnesses)
        
        selected_indices = []
        
        for _ in range(select_count):
            # Pick random tournament participants
            tournament_indices = random.sample(range(len(fitnesses)), tournament_size)
            
            # Find the best (lowest fitness for minimization)
            tournament_fitness = [fitnesses[i] for i in tournament_indices]
            winner_idx = tournament_indices[tournament_fitness.index(min(tournament_fitness))]
            
            selected_indices.append(winner_idx)
        
        return selected_indices

    def run_ga(self):
        '''
        fitness: average_waiting_time
        gene: traffic light phase signals. example: [30,45,20,30]
        '''
        simulator = Simulator()
        baseline_fitness, baseline_gene = simulator.simulate() # Evaluate baseline fitness
        population = self.create_initial_population(baseline_gene)

        best_genes = None
        best_fitness = float('inf')

        # GA LOOP
        for generation in c.GENERATIONS:

            # EVALUATION
            fitness_scores = []
            for gene in population:
                fitness = simulator.simulate(gene)
                fitness_scores.append(fitness)

            # TRACK BEST
            gen_best_idx = fitness_scores.index(min(fitness_scores))
            gen_best_genes = population[gen_best_idx]
            gen_best_fitness = fitness_scores[gen_best_idx]
            
            if gen_best_fitness < best_fitness:
                best_genes = gen_best_genes.copy()
                best_fitness = gen_best_fitness

            # TOURNAMENT SELECTION
            selected_indecies = self.tournament_selection(fitness_scores)

            # CROSSOVER
            children = []
            for i in range(0, c.POPULATION, 2):
                child1, child2 = Crossover.single_point(selected_indecies[i], selected_indecies[i+1])
                children.extend([child1, child2])



