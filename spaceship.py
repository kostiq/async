import curses
import random
import time

from coroutines import blink, fire, animate_spaceship
from tools import get_rand_coordinates

TIC_TIMEOUT = 0.1
STARS = '+*.:'
STARS_COUNT = 500


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    rows_number, columns_number = canvas.getmaxyx()
    coroutines = [
        fire(canvas, rows_number // 2, columns_number // 2),
        animate_spaceship(canvas, rows_number // 2, columns_number // 2)
    ]
    for i in range(STARS_COUNT):
        offset = random.randint(1, 10)
        star = blink(canvas, *get_rand_coordinates(rows_number, columns_number), random.choice(STARS), offset=offset)
        coroutines.append(star)

    while True:
        canvas.border()

        for c in coroutines.copy():
            try:
                c.send(None)
            except StopIteration:
                coroutines.remove(c)

        canvas.refresh()

        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
