import asyncio
import curses

TEXT = """
  _____                         ____                 
 / ____|                       / __ \                
| |  __  __ _ _ __ ___   ___  | |  | |_   _____ _ __ 
| | |_ |/ _` | '_ ` _ \ / _ \ | |  | \ \ / / _ \ '__|
| |__| | (_| | | | | | |  __/ | |__| |\ V /  __/ |   
 \_____|\__,_|_| |_| |_|\___|  \____/  \_/ \___|_|   
                                                    
"""


async def show_gameover(canvas, screen_height, screen_width):
    lines = TEXT.strip('\n').split('\n')
    height = len(lines)
    width = max(len(line) for line in lines)

    top = screen_height // 2 - height // 2
    left = screen_width // 2 - width // 2

    while True:
        for i, line in enumerate(lines):
            canvas.addstr(top + i, left, line, curses.A_BOLD)
        await asyncio.sleep(0)
