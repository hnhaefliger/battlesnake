import random
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


def snake_tensors(state):
    tensors = []

    for snake in state['snakes']:
        tensors.append(state_to_tensor(state, snake))

    return tensors


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
