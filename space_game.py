import asyncio
import curses
import os
import random
import time
from itertools import cycle

from animations.curses_tools import draw_frame, get_frame_size, read_controls
from animations.game_over import show_gameover
from animations.obstacles import Obstacle
from animations.physics import update_speed
from animations.script import PHRASES, get_garbage_delay_tics
from animations.space_animations import fire, fly_garbage


MAX_STARS = 16
MIN_STARS = 15
SYMBOLS_OF_STARS = ['+', '*', '.', ':']
OFFSET_OF_ANIMATION = 10
TIC_TIMEOUT = 0.1
GAME_BORDER_MARGIN = 1
CHANGE_YEAR_AFTER = 10
SHIFT_YEAR_STEP = 10

coroutines = []
obstacles = []
obstacles_in_last_collisions = []
year = 1957


async def restore_frame(canvas):
    while True:
        canvas.border('|', '|')
        await sleep(1)


async def timer(tiks):
    await sleep(tiks)
    return SHIFT_YEAR_STEP


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


def get_frame(path):
    with open(path, "r") as file:
        file_content = file.read()
    return file_content


async def run_spaceship(canvas, start_row, start_column, sub_window, *frames):
    """Animate spaceship, read input, fire when space is pressed."""
    rows_canvas, columns_canvas = canvas.getmaxyx()
    row_speed = column_speed = 0
    frames_cycle = cycle(frames)

    for frame in frames_cycle:
        rows_spaceship, columns_spaceship = get_frame_size(frame)

        for _ in range(2):
            sub_window.refresh()
            sub_window.addstr(
                1, 2, f'year - {year} ---- {PHRASES.get(year) or ""}')
            rows_direction, columns_direction, fire_on = read_controls(canvas)

            row_speed, column_speed = update_speed(
                row_speed, column_speed, rows_direction, columns_direction)

            start_row += row_speed
            start_column += column_speed

            start_row = min(max(start_row, 1), rows_canvas -
                            2 - rows_spaceship - 1)
            start_column = min(max(start_column, 1),
                               columns_canvas - columns_spaceship - 1)

            for obstacle in obstacles:
                if obstacle.has_collision(start_row, start_column, rows_spaceship, columns_spaceship):
                    coroutines.append(show_gameover(
                        canvas, rows_canvas, columns_canvas))
                    return

            if fire_on:
                coroutines.append(
                    fire(canvas, start_row, start_column + 2, obstacles, obstacles_in_last_collisions))

            draw_frame(canvas, start_row, start_column, frame)

            if year >= 2020:
                draw_frame(canvas, start_row - 1, start_column + 2, "^")

            await asyncio.sleep(0)

            draw_frame(canvas, start_row, start_column, frame, negative=True)

            if year >= 2020:
                draw_frame(canvas, start_row - 1,
                           start_column + 2, "^", negative=True)


async def fill_orbit_with_garbage(canvas, garbage_filenames, columns):
    global year
    while True:
        time = get_garbage_delay_tics(year)
        if time is None:
            year = year + await timer(CHANGE_YEAR_AFTER)
            continue
        await sleep(time)
        garbage_filename = random.choice(garbage_filenames)
        garbage_frame = get_frame(f'animations/garbage/{garbage_filename}')
        column = random.randint(2, columns - 2)

        frame_row, frame_column = get_frame_size(garbage_frame)

        obstacle = Obstacle(0, column, frame_row, frame_column)
        obstacles.append(obstacle)

        coroutines.append(
            fly_garbage(canvas, column=column, garbage_frame=garbage_frame, obstacle=obstacle, obstacles=obstacles,
                        obstacles_in_last_collisions=obstacles_in_last_collisions))
        year = year + await timer(CHANGE_YEAR_AFTER)


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

    sub_window = canvas.derwin(3, columns, rows - 3, 0)
    sub_window.border('|', '|')

    coroutines.append(restore_frame(canvas))
    coroutines.append(restore_frame(sub_window))

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
    coroutines.append(run_spaceship(canvas, 0, columns // 2, sub_window,
                                    spaceship_first_frame, spaceship_second_frame))

    garbage_filenames = os.listdir('animations/garbage')
    coroutines.append(fill_orbit_with_garbage(
        canvas, garbage_filenames, columns))

    for _ in range(quantity_of_stars):
        for _ in range(MAX_STARS):
            row = random.randint(GAME_BORDER_MARGIN,
                                 rows - GAME_BORDER_MARGIN - 4)
            column = random.randint(
                GAME_BORDER_MARGIN, columns - GAME_BORDER_MARGIN)
            if (row, column) not in used_positions:
                used_positions.add((row, column))
                symbol = random.choice(SYMBOLS_OF_STARS)
                offset_tics = random.randint(0, OFFSET_OF_ANIMATION)
                coroutines.append(
                    blink(canvas, row, column, symbol=random.choice(SYMBOLS_OF_STARS), offset_tics=offset_tics))

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
