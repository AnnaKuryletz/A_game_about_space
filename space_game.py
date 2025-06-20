import asyncio
import curses
import time
import random

from fire_animation import fire

MAX_STARS = 60
MIN_STARS = 15
SIMBOLS_OF_STARS = ['+', '*', '.', ':']
OFFSET_OF_ANIMATION = 10
TIC_TIMEOUT = 0.1


async def blink(canvas, row, column, symbol='*'):
    for _ in range(random.randint(0, OFFSET_OF_ANIMATION)):
        await asyncio.sleep(0)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


def draw(canvas):
    canvas.border('|', '|')
    curses.curs_set(False)

    rows, columns = canvas.getmaxyx()
    quantity_of_stars = random.randint(MIN_STARS, MAX_STARS)

    coroutine_of_shot = fire(canvas, rows // 2, columns // 2)
    coroutines = [coroutine_of_shot]

    used_positions = set()

    for _ in range(quantity_of_stars):
        for _ in range(100):
            row = random.randint(1, rows - 2)
            column = random.randint(1, columns - 2)
            if (row, column) not in used_positions:
                used_positions.add((row, column))
                symbol = random.choice(SIMBOLS_OF_STARS)
                coroutines.append(blink(canvas, row, column, symbol=symbol))
                break

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)

        if len(coroutines) == 0:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
