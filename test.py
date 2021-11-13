from battlesnake import *
import json
import random

state = create_random_state(11, 11)

while len(state['snakes']) > 0:
    moves = [random.choice(['up', 'down', 'left', 'right']) for i in range(len(state['snakes']))]
    print(moves)
    display_state(state)
    state, scores = next_state_and_scores(state, moves)
    print(scores)
