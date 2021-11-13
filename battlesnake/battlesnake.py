import tkinter as tk
import random
import json
import copy


def random_color():
    color = '#'

    for i in range(3):
        c = hex(random.randint(0, 255))[2:]

        if len(c) < 2:
            c = '0' + c

        color += c

    return color


def state_to_tensor(state, you):
  tensor = [[[0 for i in range(state['width'])] for j in range(state['height'])] for k in range(5)]

  for food in state['food']:
    tensor[0][food['y']][food['x']] = 1

  for snake in state['snakes']:
    b, h = 1, 2  # body, head, layers

    if snake == you:
      b, h = 3, 4

    for body in snake['body']:
      tensor[b][body['y']][body['x']] = 1

    tensor[h][snake['head']['y']][snake['head']['x']] = 1

  return tensor


def display_state(state, width=500, height=500):
    root = tk.Tk()
    root.geometry(f'{str(width)}x{str(height)}')
    root.title('Battlesnakes')

    canvas = tk.Canvas(root, width=width, height=height)
    canvas.pack()

    x_scale = width / state['width']
    y_scale = height / state['height']

    for food in state['food']:
        canvas.create_rectangle(
            food['x'] * x_scale, 
            height - (food['y'] * y_scale),
            (food['x'] + 1) * x_scale,
            height - ((food['y'] + 1) * y_scale),
            fill='red'
        )

    for snake in state['snakes']:
        color = random_color()

        for body in snake['body']:
            canvas.create_rectangle(
                body['x'] * x_scale, 
                height - (body['y'] * y_scale),
                (body['x'] + 1) * x_scale,
                height - ((body['y'] + 1) * y_scale),
                fill=color
            )

        canvas.create_rectangle(
            snake['head']['x'] * x_scale,
            height - (snake['head']['y'] * y_scale),
            (snake['head']['x'] + 1) * x_scale,
            height - ((snake['head']['y'] + 1) * y_scale),
            fill=color
        )
        canvas.create_rectangle(
            (snake['head']['x'] + 0.25) * x_scale,
            height - ((snake['head']['y'] + 0.25) * y_scale),
            (snake['head']['x'] + 0.75) * x_scale,
            height - ((snake['head']['y'] + 0.75) * y_scale),
            fill='green'
        )

    root.mainloop()


def next_state(state, moves, food_chance=50, min_food=2):
    # move snakes
    for move, snake in zip(moves, state['snakes']):
        # update snake head and tail
        if move == 'up':
            snake['head']['y'] += 1

        elif move == 'down':
            snake['head']['y'] -= 1

        elif move == 'left':
            snake['head']['x'] -= 1

        elif move == 'right':
            snake['head']['x'] += 1

        snake['body'] = [copy.copy(snake['head'])] + snake['body']
        del snake['body'][-1]
        snake['health'] -= 1

        # feed snake
        if snake['head'] in state['food']:
            snake['health'] += 1
            snake['body'].append(snake['body'][-1])
            state['food'].remove(snake['head'])

    print(json.dumps(state, indent='\t'))

    # maybe generate new food
    empty = [{'x': i, 'y': j} for i in range(state['width']) for j in range(state['height'])]

    for food in state['food']:
        if food in empty:
            empty.remove(food)

    for snake in state['snakes']:
        for body in snake['body']:
            if body in empty:
                empty.remove(body)

    if len(state['food']) < min_food:
        for _ in range(min_food - len(state['food'])):
            food = random.choice(empty)
            empty.remove(food)
            state['food'].append(food)
        
    elif random.randint(0, 100) < food_chance:
        state['food'].append(random.choice(empty))

    # eliminate dead snakes
    for snake in copy.copy(state['snakes']):
        # out of health
        if snake['health'] < 1: 
            state['snakes'].remove(snake)

        # out of bounds
        elif snake['head']['x'] < 0 or snake['head']['x'] >= state['width'] or snake['head']['y'] < 0 or snake['head']['y'] >= state['height']:
            state['snakes'].remove(snake)

        # self colision
        elif snake['head'] in snake['body'][1:]:
            state['snakes'].remove(snake)

    # now that the self-eliminated snakes are out
    for snake_a in copy.copy(state['snakes']):
        for snake_b in copy.copy(state['snakes']):
            if snake_a != snake_b:
                # head-on-head collision
                if snake_a['head'] == snake_b['head']:
                    if snake_a['health'] > snake_b['health']:
                        state['snakes'].remove(snake_b)

                    elif snake_a['health'] < snake_b['health']:
                        state['snakes'].remove(snake_b)

                # head-on-body collision
                else:
                    if snake_a['head'] in snake_b['body']:
                        state['snakes'].remove(snake_a)

                    if snake_b['head'] in snake_a['body']:
                        state['snakes'].remove(snake_b)

    return state
                

state = json.loads('''{"height": 11, "width": 11, "snakes": [{"id": "gs_YfjCRBv9MWqw7KQJxwjggpXQ", "name": "Calabariidae", "latency": "310", "health": 99, "body": [{"x": 9, "y": 10}, {"x": 9, "y": 9}, {"x": 9, "y": 9}], "head": {"x": 9, "y": 10}, "length": 3, "shout": "Moving up!", "squad": ""}, {"id": "gs_4q6dRgFqr39kYjWqxb3DT8G7", "name": "ANIRUDH", "latency": "184", "health": 99, "body": [{"x": 5, "y": 8}, {"x": 5, "y": 9}, {"x": 5, "y": 9}], "head": {"x": 5, "y": 8}, "length": 3, "shout": "", "squad": ""}, {"id": "gs_Sdh9jMRhyttFMvDKr9jWCgxR", "name": "snek", "latency": "82", "health": 99, "body": [{"x": 9, "y": 4}, {"x": 9, "y": 5}, {"x": 9, "y": 5}], "head": {"x": 9, "y": 4}, "length": 3, "shout": "", "squad": ""}, {"id": "gs_JtM7Tq6mFJbb4fmxQTH4MvqQ", "name": "TestSnake", "latency": "63", "health": 99, "body": [{"x": 1, "y": 6}, {"x": 1, "y": 5}, {"x": 1, "y": 5}], "head": {"x": 1, "y": 6}, "length": 3, "shout": "", "squad": ""}], "food": [{"x": 10, "y": 10}, {"x": 4, "y": 8}, {"x": 8, "y": 4}, {"x": 2, "y": 6}, {"x": 5, "y": 5}], "hazards": []}''')

while len(state['snakes']) > 0:
    moves = [random.choice(['up', 'down', 'left', 'right']) for i in range(len(state['snakes']))]
    print(moves)
    display_state(state)
    state = next_state(state, moves)
