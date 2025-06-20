import asyncio
import curses
import time
import random

TIC_TIMEOUT = 0.1


async def blink(canvas, row, column, symbol='*'):
    for _ in range(random.randint(0, 20)):
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
    coroutines = []

    max_y, max_x = canvas.getmaxyx()

    used_positions = set()

    while len(coroutines) < 100:
        row = random.randint(1, max_y - 2)
        column = random.randint(1, max_x - 2)
        if (row, column) in used_positions:
            continue
        used_positions.add((row, column))

        symbol = random.choice('+*.:')

        coroutine = blink(canvas, row, column, symbol)
        coroutines.append(coroutine)

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
