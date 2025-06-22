import asyncio
import curses
import time
import random

from animations.fire_animation import fire
from animations.space_ship import animate_spaceship

MAX_STARS = 60
MIN_STARS = 15
SYMBOLS_OF_STARS = ['+', '*', '.', ':']
OFFSET_OF_ANIMATION = 10
TIC_TIMEOUT = 0.1
GAME_BORDER_MARGIN = 1  # отступ от границы из-за рамки border


def get_frame(path):
    with open(path, "r") as file:
        file_content = file.read()
    return file_content


async def blink(canvas, row, column, symbol='*', offset_tics=0):
    for _ in range(offset_tics):
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
    canvas.nodelay(True)
    canvas.border('|', '|')
    curses.curs_set(False)

    rows, columns = canvas.getmaxyx()
    quantity_of_stars = random.randint(MIN_STARS, MAX_STARS)
    center_row = rows // 2
    center_col = columns // 2

    coroutine_of_shot = fire(canvas, center_row, center_col)
    used_positions = set()
    spaceship_first_frame = get_frame('animations/rocket_frame_1.txt')
    spaceship_second_frame = get_frame('animations/rocket_frame_2.txt')
    frame_lines = spaceship_first_frame.splitlines()
    frame_height = len(frame_lines)
    frame_width = max(len(line) for line in frame_lines)
    max_start_row = rows - frame_height
    start_row = min(center_row + OFFSET_OF_ANIMATION, max_start_row)
    start_col = center_col
    spaceship_area = set(
        (start_row + dy, start_col + dx)
        for dy in range(frame_height)
        for dx in range(frame_width)
    )
    used_positions = set(spaceship_area)
    coroutine_of_spaceship = animate_spaceship(
        canvas, start_row, start_col, spaceship_first_frame, spaceship_second_frame)

    coroutines = [coroutine_of_spaceship, coroutine_of_shot]
    for _ in range(quantity_of_stars):
        for _ in range(MAX_STARS):
            row = random.randint(GAME_BORDER_MARGIN, rows - GAME_BORDER_MARGIN)
            column = random.randint(
                GAME_BORDER_MARGIN, columns - GAME_BORDER_MARGIN)
            if (row, column) not in used_positions:
                used_positions.add((row, column))
                symbol = random.choice(SYMBOLS_OF_STARS)
                offset_tics = random.randint(0, OFFSET_OF_ANIMATION)
                coroutines.append(
                    blink(canvas, row, column, symbol=symbol,
                          offset_tics=offset_tics)
                )
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
