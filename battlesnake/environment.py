import random
import uuid
import copy
import tkinter as tk
import numpy as np


def random_color():
    color = '#'

    for i in range(3):
        c = hex(random.randint(0, 255))[2:]

        if len(c) < 2:
            c = '0' + c

        color += c

    return color


class Environment:
    def __init__(self, width=11, height=11, n_snakes=4, n_food=4, food_chance=0.5, min_food=2, survive_score=0, eat_score=1, death_score=-10, kill_score=10):
        self.width = width
        self.height = height
        self.n_snakes = n_snakes
        self.n_food = n_food
        self.food_chance = food_chance
        self.min_food = min_food

        self.survive_score = survive_score
        self.eat_score = eat_score
        self.death_score = death_score
        self.kill_score = kill_score

        self.reset()

    def reset(self):
        empty = [{'x': i, 'y': j} for i in range(self.width) for j in range(self.height)]

        self.state = {
            "width": self.width,
            "height": self.height,
            "snakes": [],
            "food": [],
            "hazards": []
        }

        for _ in range(self.n_snakes):
            snake = random.choice(empty)
            empty.remove(snake)
            self.state['snakes'].append({
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

        for _ in range(self.n_food):
            food = random.choice(empty)
            empty.remove(food)
            self.state['food'].append(copy.deepcopy(food))

        self.history = [copy.deepcopy(self.state)]

    def step(self, moves):
        scores = [self.survive_score for i in range(len(self.state['snakes']))]
        
        # move snakes
        for i, (move, snake) in enumerate(zip(moves, self.state['snakes'])):
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
            if snake['head'] in self.state['food']:
                scores[i] += 1
                snake['health'] += self.eat_score
                snake['body'].append(snake['body'][-1])
                self.state['food'].remove(snake['head'])

        # maybe generate new food
        empty = [{'x': i, 'y': j}
                for i in range(self.state['width']) for j in range(self.state['height'])]

        for food in self.state['food']:
            if food in empty:
                empty.remove(food)

        for snake in self.state['snakes']:
            for body in snake['body']:
                if body in empty:
                    empty.remove(body)

        if len(self.state['food']) < self.min_food:
            for _ in range(self.min_food - len(self.state['food'])):
                food = random.choice(empty)
                empty.remove(food)
                self.state['food'].append(food)

        elif random.randint(0, 100) < self.food_chance:
            self.state['food'].append(random.choice(empty))

        # eliminate dead snakes
        for i, snake in enumerate(copy.deepcopy(self.state['snakes'])):
            # out of health
            if snake['health'] < 1:
                scores[i] += self.death_score
                self.state['snakes'].remove(snake)

            # out of bounds
            elif snake['head']['x'] < 0 or snake['head']['x'] >= self.state['width'] or snake['head']['y'] < 0 or snake['head']['y'] >= self.state['height']:
                scores[i] += self.death_score
                self.state['snakes'].remove(snake)

            # self colision
            elif snake['head'] in snake['body'][1:]:
                scores[i] += self.death_score
                self.state['snakes'].remove(snake)

        # now that the self-eliminated snakes are out
        for i, snake_a in enumerate(copy.deepcopy(self.state['snakes'])):
            for j, snake_b in enumerate(copy.deepcopy(self.state['snakes'])):
                if snake_a['id'] != snake_b['id']:
                    # head-on-head collision
                    if snake_a['head'] == snake_b['head']:
                        if snake_a['health'] > snake_b['health']:
                            scores[j] += self.death_score
                            scores[i] += self.kill_score
                            self.state['snakes'].remove(snake_b)

                        elif snake_a['health'] < snake_b['health']:
                            scores[i] += self.death_score
                            scores[j] += self.kill_score
                            self.state['snakes'].remove(snake_b)

                    # head-on-body collision
                    else:
                        if snake_a['head'] in snake_b['body']:
                            try:
                                self.state['snakes'].remove(snake_a)
                                scores[i] += self.death_score
                                scores[j] += self.kill_score

                            except:
                                pass

                        if snake_b['head'] in snake_a['body']:
                            try:
                                self.state['snakes'].remove(snake_b)
                                scores[j] += self.death_score
                                scores[i] += self.kill_score

                            except:
                                pass

        self.history.append(copy.deepcopy(self.state))

        if len(self.state['snakes']) == 0:
            return scores, True

        else:
            return scores, False

    @property
    def tensors(self):
        tensors = []

        for you in self.state['snakes']:
            tensor = [[[0 for i in range(self.state['width'])] for j in range(self.state['height'])] for k in range(5)]

            for food in self.state['food']:
                tensor[0][food['y']][food['x']] = 1

            for snake in self.state['snakes']:
                b, h = 1, 2  # body, head, layers

                if snake == you:
                    b, h = 3, 4

                for body in snake['body']:
                    tensor[b][body['y']][body['x']] = 1

                    tensor[h][snake['head']['y']][snake['head']['x']] = 1

            tensors.append(tensor)

        return np.array(tensors)

    def show(self, width=500, height=500):
        root = tk.Tk()
        root.geometry(f'{str(width)}x{str(height)}')
        root.title('Battlesnakes')

        canvas = tk.Canvas(root, width=width, height=height)
        canvas.pack()

        x_scale = width / self.state['width']
        y_scale = height / self.state['height']

        for food in self.state['food']:
            canvas.create_rectangle(
                food['x'] * x_scale,
                height - (food['y'] * y_scale),
                (food['x'] + 1) * x_scale,
                height - ((food['y'] + 1) * y_scale),
                fill='red'
            )

        for snake in self.state['snakes']:
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

    def replay(self, dt=1000, width=500, height=500):
        root = tk.Tk()
        root.geometry(f'{str(width)}x{str(height)}')
        root.title('Battlesnakes')

        canvas = tk.Canvas(root, width=width, height=height)
        canvas.pack()

        x_scale = width / self.state['width']
        y_scale = height / self.state['height']

        def show(dt, root, canvas, history, i):
            canvas.delete('all')
            state = history[i]

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

            i += 1

            if i < len(history):
                root.after(dt, show, dt, root, canvas, history, i)

        show(dt, root, canvas, self.history, 0)
        root.mainloop()
