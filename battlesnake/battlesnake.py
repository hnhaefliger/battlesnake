import random
import copy
import uuid


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

        snake['body'] = [copy.deepcopy(snake['head'])] + snake['body']
        del snake['body'][-1]
        snake['health'] -= 1

        # feed snake
        if snake['head'] in state['food']:
            snake['health'] += 1
            snake['body'].append(snake['body'][-1])
            state['food'].remove(snake['head'])

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
    for snake in copy.deepcopy(state['snakes']):
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
    for snake_a in copy.deepcopy(state['snakes']):
        for snake_b in copy.deepcopy(state['snakes']):
            if snake_a['id'] != snake_b['id']:
                # head-on-head collision
                if snake_a['head'] == snake_b['head']:
                    if snake_a['health'] > snake_b['health']:
                        state['snakes'].remove(snake_b)

                    elif snake_a['health'] < snake_b['health']:
                        state['snakes'].remove(snake_b)

                # head-on-body collision
                else:
                    if snake_a['head'] in snake_b['body']:
                        try:
                            state['snakes'].remove(snake_a)

                        except: pass

                    if snake_b['head'] in snake_a['body']:
                        try:
                            state['snakes'].remove(snake_b)

                        except: pass

    return state
                

def next_state_and_scores(state, moves, food_chance=50, min_food=2):
    old_state = copy.deepcopy(state)
    new_state = next_state(state, moves, food_chance=food_chance, min_food=min_food)
    scores = []

    for snake_a in old_state['snakes']:
        found = False

        for snake_b in new_state['snakes']:
            if snake_b['id'] == snake_a['id']:
                if snake_b['health'] < snake_a['health']:
                    scores.append(1)

                else:
                    scores.append(2)

                break

        else:
            scores.append(0)

    done = 0

    if len(new_state['snakes']) == 0:
        new_state = create_random_state(state['width'], state['height'])
        done = 1

    return new_state, scores, done, None


def create_random_state(width, height, n_snakes=4, n_food=5):
    empty = [{'x': i, 'y': j} for i in range(width) for j in range(height)]

    state = {
        "height": width, 
        "width": height, 
        "snakes": [],
        "food": [],
        "hazards": []
    }

    for _ in range(n_snakes):
        snake = random.choice(empty)
        empty.remove(snake)
        state['snakes'].append({
            "id": str(uuid.uuid4()),
            "name": "",
            "latency": "",
            "health": 99,
            "body": [copy.deepcopy(snake) for _ in range(3)],
            "head": copy.deepcopy(snake),
            "length": 3,
            "shout": "",
            "squad": ""
        })

    for _ in range(n_food):
        food = random.choice(empty)
        empty.remove(food)
        state['food'].append(copy.deepcopy(food))

    return state
