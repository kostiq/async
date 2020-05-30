import random

from cursed_tools import read_controls, get_frame_size


def get_stars(stars):
    return random.choice(stars)


def get_rand_coordinates(y, x):
    return random.randint(1, x - 2), random.randint(1, y - 2)


def get_spaceship_frames():
    with open('frames/rocket_frame_1.txt') as f1, open('frames/rocket_frame_2.txt') as f2:
        return [f1.read(), f2.read()]


def modified_coordinates(canvas, row, column, frame):
    row_delta, column_delta, _ = read_controls(canvas, multiplier=10)
    frame_row, frame_col = get_frame_size(frame)
    rows_number, columns_number = canvas.getmaxyx()

    if row_delta < 0:
        row = max(row + row_delta, 1)
    elif row_delta > 0:
        row = min(row + row_delta, rows_number - frame_row - 1)

    if column_delta < 0:
        column = max(column + column_delta, 1)
    elif column_delta > 0:
        column = min(column + column_delta, columns_number - frame_col - 1)

    return row, column
