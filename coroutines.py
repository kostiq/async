import asyncio
import curses

from cursed_tools import draw_frame
from tools import read_frames, get_updated_spaceship_coordinates, get_frame_sequence


async def async_sleep(seconds):
    for _ in range(int(seconds * 10)):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*', offset=0):
    while True:
        await async_sleep(offset / 10)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        await async_sleep(2)

        canvas.addstr(row, column, symbol)
        await async_sleep(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await async_sleep(0.5)

        canvas.addstr(row, column, symbol)
        await async_sleep(0.3)


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
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, row, column):
    frames = read_frames()

    for frame in get_frame_sequence(frames):
        draw_frame(canvas, row, column, frame)

        await asyncio.sleep(0)

        draw_frame(canvas, row, column, frame, negative=True)

        row, column = get_updated_spaceship_coordinates(canvas, row, column, frame)
