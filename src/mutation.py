# mutation.py
import random

class Mutation:
    
    def gaussian_mutate(gene, mutation_rate=0.25, sigma=5.0):
        mutated = []
        for value in gene:
            if random.random() < mutation_rate:
                # Gaussian mutation
                new_value = value + random.gauss(0, sigma)
                new_value = max(10, min(30, int(new_value)))
                mutated.append(new_value)
            else:
                mutated.append(value)
        return mutated
    
    def random_reset_mutate(gene, mutation_rate=0.25):
        mutated = []
        for value in gene:
            if random.random() < mutation_rate:
                # Random reset within bounds
                new_value = random.randint(10, 30)
                mutated.append(new_value)
            else:
                mutated.append(value)
        return mutated
    
    def creep_mutate(gene, mutation_rate=0.25):
        mutated = []
        for value in gene:
            if random.random() < mutation_rate:
                # Small random change (-5 to +5)
                change = random.randint(-5, 5)
                new_value = value + change
                new_value = max(10, min(30, new_value))
                mutated.append(new_value)
            else:
                mutated.append(value)
        return mutated