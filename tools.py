import itertools
import random

from cursed_tools import read_controls, get_frame_size


def get_rand_coordinates(x, y):
    return random.randint(1, x - 2), random.randint(1, y - 2)


def read_frames():
    with open('frames/rocket_frame_1.txt') as f1, open('frames/rocket_frame_2.txt') as f2:
        return [f1.read(), f2.read()]


def get_frame_sequence(frames):
    return itertools.cycle(itertools.chain(*zip(frames, frames)))


def multiplied_offset(x_offset, y_offset, space_button, multiplier=10):
    return x_offset * multiplier, y_offset * multiplier, space_button


def get_updated_spaceship_coordinates(canvas, row, column, frame):
    row_delta, column_delta, _ = multiplied_offset(*read_controls(canvas))

    frame_row, frame_col = get_frame_size(frame)
    rows_number, columns_number = canvas.getmaxyx()

    if row_delta < 0:
        row = max(row + row_delta, 0)
    elif row_delta > 0:
        row = min(row + row_delta, rows_number - frame_row)

    if column_delta < 0:
        column = max(column + column_delta, 0)
    elif column_delta > 0:
        column = min(column + column_delta, columns_number - frame_col)

    return row, column
