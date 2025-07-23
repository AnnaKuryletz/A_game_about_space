import asyncio
import curses
import time
import random
from itertools import cycle
import os

from animations.space_animations import fire, fly_garbage
from animations.physics import update_speed
from animations.curses_tools import get_frame_size, draw_frame, read_controls

MAX_STARS = 16
MIN_STARS = 15
SYMBOLS_OF_STARS = ['+', '*', '.', ':']
OFFSET_OF_ANIMATION = 10
TIC_TIMEOUT = 0.1
GAME_BORDER_MARGIN = 1  # отступ от границы из-за рамки border
COROUTINES = []


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def run_spaceship(canvas, start_row, start_column, *frames):
    """Animate spaceship, read input, fire when space is pressed."""
    rows_canvas, columns_canvas = canvas.getmaxyx()
    row_speed = column_speed = 0
    frames_cycle = cycle(frames)

    for frame in frames_cycle:
        rows_spaceship, columns_spaceship = get_frame_size(frame)

        for _ in range(2):
            rows_direction, columns_direction, space_pressed = read_controls(
                canvas)

            # управление скоростью
            row_speed, column_speed = update_speed(
                row_speed, column_speed, rows_direction, columns_direction)

            # новая позиция
            start_row += row_speed
            start_column += column_speed

            # проверка границ
            start_row = min(max(start_row, 1),
                            rows_canvas - rows_spaceship - 1)
            start_column = min(max(start_column, 1),
                               columns_canvas - columns_spaceship - 1)

            # выстрел
            if space_pressed:
                gun_row = start_row
                gun_column = start_column + columns_spaceship // 2
                COROUTINES.append(fire(canvas, gun_row, gun_column))

            # отрисовка
            draw_frame(canvas, start_row, start_column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, start_row, start_column, frame, negative=True)


def get_frame(path):
    with open(path, "r") as file:
        file_content = file.read()
    return file_content


async def fill_orbit_with_garbage(canvas, garbage_filenames, columns):
    while True:
        await sleep(random.randint(10, 30))
        garbage_filename = random.choice(garbage_filenames)
        garbage_frame = get_frame(f'animations/garbage/{garbage_filename}')
        COROUTINES.append(fly_garbage(canvas, column=random.randint(
            2, columns - 2), garbage_frame=garbage_frame))


async def blink(canvas, row, column, symbol='*', offset_tics=0):
    await sleep(offset_tics)

    max_row, max_col = canvas.getmaxyx()

    while True:
        if 0 < row < max_row - 1 and 0 < column < max_col - 1:
            canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        if 0 < row < max_row - 1 and 0 < column < max_col - 1:
            canvas.addstr(row, column, symbol)
        await sleep(3)

        if 0 < row < max_row - 1 and 0 < column < max_col - 1:
            canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        if 0 < row < max_row - 1 and 0 < column < max_col - 1:
            canvas.addstr(row, column, symbol)
        await sleep(3)


def draw(canvas):
    canvas.nodelay(True)
    canvas.border('|', '|')
    curses.curs_set(False)

    rows, columns = canvas.getmaxyx()
    quantity_of_stars = random.randint(MIN_STARS, MAX_STARS)
    center_row = rows // 2
    center_col = columns // 2

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
    COROUTINES.append(run_spaceship(canvas, 0, columns // 2, spaceship_first_frame,
                                    spaceship_second_frame))

    COROUTINES.append(fire(canvas, center_row, center_col))
    garbage_filenames = os.listdir('animations/garbage')
    COROUTINES.append(fill_orbit_with_garbage(
        canvas, garbage_filenames, columns))

    for _ in range(quantity_of_stars):
        for _ in range(MAX_STARS):
            row = random.randint(GAME_BORDER_MARGIN, rows - GAME_BORDER_MARGIN)
            column = random.randint(
                GAME_BORDER_MARGIN, columns - GAME_BORDER_MARGIN)
            if (row, column) not in used_positions:
                used_positions.add((row, column))
                symbol = random.choice(SYMBOLS_OF_STARS)
                offset_tics = random.randint(0, OFFSET_OF_ANIMATION)
                COROUTINES.append(
                    blink(canvas, row, column, symbol=random.choice(SYMBOLS_OF_STARS), offset_tics=offset_tics))

    while True:
        for coroutine in COROUTINES.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)

        if len(COROUTINES) == 0:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
