from animations.curses_tools import draw_frame, get_frame_size
import asyncio
import curses


from animations.curses_tools import draw_frame
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


async def fly_garbage(canvas, column, garbage_frame, obstacle, obstacles, obstacles_in_last_collisions, speed=0.5):
    """Animate garbage, flying from top to bottom. Column position stays constant."""
    rows_number, columns_number = canvas.getmaxyx()
    frame_height, _ = get_frame_size(garbage_frame)
    max_row_for_garbage = rows_number - 4 - frame_height

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    try:
        while row < max_row_for_garbage:
            draw_frame(canvas, int(row), column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, int(row), column, garbage_frame, negative=True)

            row += speed
            obstacle.row = row

            for obstacle_in_last_collisions in obstacles_in_last_collisions:
                if obstacle_in_last_collisions.row == obstacle.row:
                    await explode(canvas, obstacle.row, obstacle.column)
                    obstacles_in_last_collisions.remove(
                        obstacle_in_last_collisions)
                    return None
    finally:
        if obstacle in obstacles:
            obstacles.remove(obstacle)
