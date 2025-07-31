import asyncio
import curses

from animations.obstacles import Obstacle
from animations.curses_tools import draw_frame, get_frame_size
from animations.explosion import explode


async def fire(canvas, start_row, start_column, obstacles, obstacles_in_last_collisions, rows_speed=-0.3, columns_speed=0):
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

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                return None


async def fly_garbage(canvas, column, garbage_frame, obstacles, obstacles_in_last_collisions, speed=0.5):
    """Animate garbage falling down. Handles obstacle creation and removal."""
    rows_number, columns_number = canvas.getmaxyx()
    frame_height, frame_width = get_frame_size(garbage_frame)
    max_row_for_garbage = rows_number - 4 - frame_height  # Не залазим на табличку

    column = max(column, 0)
    column = min(column, columns_number - frame_width)

    row = 0
    obstacle = Obstacle(row, column, frame_height, frame_width)
    obstacles.append(obstacle)

    try:
        while row < max_row_for_garbage:
            draw_frame(canvas, int(row), column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, int(row), column, garbage_frame, negative=True)

            row += speed
            obstacle.row = row  # обновляем позицию препятствия

            if obstacle in obstacles_in_last_collisions:
                obstacles_in_last_collisions.remove(obstacle)
                await explode(canvas, int(row), column)
                return
    finally:
        if obstacle in obstacles:
            obstacles.remove(obstacle)
