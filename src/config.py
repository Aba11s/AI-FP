class Config:
    # GA Parameters
    POPULATION = 20
    GENERATIONS = 25
    TOURNAMENT_SIZE = 3
    SELECT_COUNT = POPULATION  # Or POPULATION // 2 for less pressure
    MUTATION_RATE = 0.5
    MUTATION_SIGMA = 4.0
    MUTATION_DECAY = 0.99
    MIN_MUTATION_RATE = 0.2
    
    # Signal Constraints
    NUM_SIGNALS = 4
    MIN_GREEN = 10
    MAX_GREEN = 60
    
    # Initialization
    INIT_VARIATION_MIN = 0.5
    INIT_VARIATION_MAX = 1.5
    MAX_INIT_ATTEMPTS = 1000
    
    # Simulation (add if not already there)
    SIM_STEPS = 900
    JUNCTION_ID = "J4"

    # Paths
    PATH_TO_NETWORK = "data/cibubur.net.xml"
    PATH_TO_ROUTE = "data/cibubur_mixed2.rou.xml"
    PATH_TO_SUMOCONFIG = "data/cibubur.sumocfg"