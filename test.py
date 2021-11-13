from battlesnake.battlesnake import *

state = json.loads('''{"height": 11, "width": 11, "snakes": [{"id": "gs_YfjCRBv9MWqw7KQJxwjggpXQ", "name": "Calabariidae", "latency": "310", "health": 99, "body": [{"x": 9, "y": 10}, {"x": 9, "y": 9}, {"x": 9, "y": 9}], "head": {"x": 9, "y": 10}, "length": 3, "shout": "Moving up!", "squad": ""}, {"id": "gs_4q6dRgFqr39kYjWqxb3DT8G7", "name": "ANIRUDH", "latency": "184", "health": 99, "body": [{"x": 5, "y": 8}, {"x": 5, "y": 9}, {"x": 5, "y": 9}], "head": {"x": 5, "y": 8}, "length": 3, "shout": "", "squad": ""}, {"id": "gs_Sdh9jMRhyttFMvDKr9jWCgxR", "name": "snek", "latency": "82", "health": 99, "body": [{"x": 9, "y": 4}, {"x": 9, "y": 5}, {"x": 9, "y": 5}], "head": {"x": 9, "y": 4}, "length": 3, "shout": "", "squad": ""}, {"id": "gs_JtM7Tq6mFJbb4fmxQTH4MvqQ", "name": "TestSnake", "latency": "63", "health": 99, "body": [{"x": 1, "y": 6}, {"x": 1, "y": 5}, {"x": 1, "y": 5}], "head": {"x": 1, "y": 6}, "length": 3, "shout": "", "squad": ""}], "food": [{"x": 10, "y": 10}, {"x": 4, "y": 8}, {"x": 8, "y": 4}, {"x": 2, "y": 6}, {"x": 5, "y": 5}], "hazards": []}''')

while len(state['snakes']) > 0:
    moves = [random.choice(['up', 'down', 'left', 'right']) for i in range(len(state['snakes']))]
    print(moves)
    display_state(state)
    state = next_state(state, moves)
