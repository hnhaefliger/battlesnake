from battlesnake import *
import json
import random

done = False
test = Environment()

while not(done):

    tensors = test.tensors

    moves = [random.choice(['up', 'down', 'left', 'right']) for i in range(len(tensors))]
    print(moves)
    #test.show()

    scores, done = test.step(moves)
    print(scores)

test.replay()
