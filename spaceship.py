import asyncio
import curses
import random
import time
import uuid

from curses_tools import draw_frame, get_frame_size
from explosion import explode
from game_scenario import PHRASES, get_garbage_delay_tics
from obstacles import Obstacle
from tools import get_rand_coordinates, read_garbage_frames, read_spaceship_frames, get_frame_sequence, \
    get_updated_coordinates, show_gameover, sleep

TIC_TIMEOUT = 0.1
STARS = '+*.:'
STARS_COUNT = 500

coroutines = []
obstacles = dict()
obstacles_in_last_collisions = set()
year = 1957
year_speed = 15


async def blink(canvas, row, column, symbol='*', offset=0):
    while True:
        await sleep(offset / 10)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(2)

        canvas.addstr(row, column, symbol)
        await sleep(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(0.5)

        canvas.addstr(row, column, symbol)
        await sleep(0.3)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 1 < row < max_row and 1 < column < max_column:
        colliding_obstacles = {uid for uid, obs in obstacles.items() if obs.has_collision(row, column)}
        if colliding_obstacles:
            obstacles_in_last_collisions.update(colliding_obstacles)
            return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    frame_rows, frame_columns = get_frame_size(garbage_frame)
    column = max(column, 0)
    column = min(column, columns_number - 1)

    uid = uuid.uuid4()

    row = 0

    while row < rows_number:
        if uid in obstacles_in_last_collisions:
            obstacles_in_last_collisions.remove(uid)
            await explode(canvas, row, column)
            return

        obstacles[uid] = Obstacle(row, column, frame_rows, frame_columns, uid=uid)

        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def fill_orbit_with_garbage(canvas):
    frames = read_garbage_frames()
    rows_number, columns_number = canvas.getmaxyx()

    while True:
        garbage_delay = get_garbage_delay_tics(year)

        if garbage_delay:
            await sleep(garbage_delay / 10)
        else:
            await sleep(0.1)
            continue

        garbage = fly_garbage(canvas, column=random.randint(0, columns_number), garbage_frame=random.choice(frames))
        coroutines.append(garbage)


async def run_spaceship(canvas, row, column):
    frames = read_spaceship_frames()
    row_speed = column_speed = 0
    for frame in get_frame_sequence(frames):
        frame_raws, frame_columns = get_frame_size(frame)
        draw_frame(canvas, row, column, frame)

        await asyncio.sleep(0)

        draw_frame(canvas, row, column, frame, negative=True)

        row, column, row_speed, column_speed, space_pressed = get_updated_coordinates(canvas, frame,
                                                                                      row, column,
                                                                                      row_speed, column_speed)
        if space_pressed and year > 2020:
            coroutines.append(fire(canvas, row, column + frame_columns // 2))

        if any(obs.has_collision(row, column) for obs in obstacles.values()):
            coroutines.append(show_gameover(canvas))
            return


async def print_info(canvas):
    phrase = PHRASES.get(year)
    while True:
        phrase = PHRASES.get(year) or phrase
        canvas.addstr(1, 1, '{}: {}'.format(year, phrase))
        await sleep(0.1)


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    rows_number, columns_number = canvas.getmaxyx()

    coroutines.extend([
        print_info(canvas),
        run_spaceship(canvas, rows_number // 2, columns_number // 2),
        fill_orbit_with_garbage(canvas),
    ])
    for i in range(STARS_COUNT):
        offset = random.randint(1, 10)
        star = blink(canvas, *get_rand_coordinates(rows_number, columns_number), random.choice(STARS), offset=offset)
        coroutines.append(star)

    game_tics = 0
    while True:
        canvas.border()

        for c in coroutines.copy():
            try:
                c.send(None)
            except StopIteration:
                coroutines.remove(c)

        game_tics += 1
        global year
        if game_tics % year_speed == 0:
            year += 1

        canvas.refresh()

        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
