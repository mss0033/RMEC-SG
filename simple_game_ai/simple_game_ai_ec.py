import random
import copy
from deap import base, creator, algorithms, tools 

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X' 

    def make_move(self, index, player):
        self.board[index] = player
        self.current_player = 'O' if player == 'X' else 'X'

    def available_moves(self):
        return [i for i, spot in enumerate(self.board) if spot == ' ']

    def is_winner(self, player):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]

        for condition in win_conditions:
            if self.board[condition[0]] == self.board[condition[1]] == self.board[condition[2]] == player:
                return True
        return False

    def is_game_over(self):
        return self.is_winner('X') or self.is_winner('O') or len(self.available_moves()) == 0

def random_ai(board):
    moves = board.available_moves()
    return random.choice(moves)

def decision_tree_ai(board):
    if board.available_moves()[4] == 4:  # If center is open, take it
        return 4
    elif len(board.available_moves()) == 8:  # First move, take a corner
        return random.choice([0, 2, 6, 8])
    else:
        # ... Some more basic logic here ...
        return random.choice(board.available_moves())  # Fallback

def play_game(player1, player2):
    game = TicTacToe()
    while not game.is_game_over():
        if game.current_player == 'X':
            move = player1(copy.deepcopy(game))
        else:
            move = player2(copy.deepcopy(game))
        game.make_move(move, game.current_player)

    if game.is_winner('X'):
        return 1  # Win for AI 
    elif game.is_winner('O'):
        return -1  # Loss for AI
    else:
        return 0  # Draw 

def evaluate_ai(individual):
    # Play multiple games against random_ai to get average score
    total_score = 0
    for _ in range(5): 
        total_score += play_game(decision_tree_ai, random_ai)
    return total_score / 5,

# Simple AI Representation
creator.create("FitnessMax", base.Fitness, weights=(1.0,)) 
creator.create("Individual", list, fitness=creator.FitnessMax)  

# AI Representation (Adjust priorities if needed)
PRIORITIES = ['center', 'corner', 'random']  

def init_individual(n=5):
    return [random.choice(PRIORITIES) for _ in range(n)]

toolbox = base.Toolbox()
toolbox.register("individual", init_individual) 
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate_ai)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)

# Basic Evolutionary Loop
NUM_GENERATIONS = 20 
POPULATION_SIZE = 50

pop = toolbox.population(n=POPULATION_SIZE)

for gen in range(NUM_GENERATIONS):
    offspring = tools.selTournament(pop, len(pop), tournsize=3)
    offspring = [toolbox.clone(ind) for ind in offspring]

    # Apply crossover and mutation
    for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < 0.7:  # Sample crossover probability
            toolbox.mate(ind1, ind2)
            del ind1.fitness.values
            del ind2.fitness.values

    for mutant in offspring:
        if random.random() < 0.2:  # Sample mutation probability
            toolbox.mutate(mutant)
            del mutant.fitness.values

    # Evaluate fitness of the new individuals
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    pop[:] = offspring

# Placeholder for Examining Results 
best_individual = tools.selBest(pop, 1)[0]
print("Best Individual:", best_individual)
print("Fitness:", best_individual.fitness.values[0])

# *** Placeholder for HITL Integration ***
# You'll add code to:
# 1. Present solutions to human reviewers
# 2. Capture feedback 
# 3. Modify the evolution process (e.g., fitness, selection) based on feedback 