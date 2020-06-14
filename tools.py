import asyncio
import itertools
import os
import random

from curses_tools import read_controls, get_frame_size, draw_frame
from phisics import update_speed


async def sleep(seconds):
    for _ in range(int(seconds * 10)):
        await asyncio.sleep(0)


def get_rand_coordinates(x, y):
    return random.randint(1, x - 2), random.randint(1, y - 2)


def read_spaceship_frames():
    with open('frames/spaceship/rocket_frame_1.txt') as f1, open('frames/spaceship/rocket_frame_2.txt') as f2:
        return [f1.read(), f2.read()]


def read_gameover_frame():
    with open('frames/game_over.txt', 'r') as f:
        return f.read()


def read_garbage_frames():
    frames = []
    for dir_path, _, filenames in os.walk('frames/garbage'):
        for f in filenames:
            with open(os.path.join(dir_path, f)) as garbage_file:
                frames.append(garbage_file.read())

    return frames


def get_frame_sequence(frames):
    return itertools.cycle(itertools.chain(*zip(frames, frames)))


def multiplied_offset(x_offset, y_offset, space_button, multiplier=2):
    return x_offset * multiplier, y_offset * multiplier, space_button


def get_updated_coordinates(canvas, frame, row, column, row_speed, column_speed):
    row_direction, column_direction, space_pressed = read_controls(canvas)
    row_speed, column_speed = update_speed(row_speed, column_speed, row_direction, column_direction)

    frame_row, frame_col = get_frame_size(frame)
    rows_number, columns_number = canvas.getmaxyx()

    if row_speed < 0:
        row = max(row + row_speed, 0)
    elif row_speed > 0:
        row = min(row + row_speed, rows_number - frame_row)

    if column_speed < 0:
        column = max(column + column_speed, 0)
    elif column_speed > 0:
        column = min(column + column_speed, columns_number - frame_col)

    return row, column, row_speed, column_speed, space_pressed


async def show_gameover(canvas):
    gameover_frame = read_gameover_frame()

    go_rows, go_columns = get_frame_size(gameover_frame)
    rows_number, columns_number = canvas.getmaxyx()

    r_pos = (rows_number - go_rows) // 2
    c_pos = (columns_number - go_columns) // 2
    while True:
        draw_frame(canvas, r_pos, c_pos, gameover_frame)
        await sleep(0.1)
        draw_frame(canvas, r_pos, c_pos, gameover_frame, negative=True)
