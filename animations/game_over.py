import asyncio
from animations.curses_tools import draw_frame

TEXT = """               ('-.     _   .-')       ('-.                           (`-.      ('-.  _  .-')   
              ( OO ).-.( '.( OO )_   _(  OO)                        _(OO  )_  _(  OO)( \( -O )  
  ,----.      / . --. / ,--.   ,--.)(,------.       .-'),-----. ,--(_/   ,. \(,------.,------.  
 '  .-./-')   | \-.  \  |   `.'   |  |  .---'      ( OO'  .-.  '\   \   /(__/ |  .---'|   /`. ' 
 |  |_( O- ).-'-'  |  | |         |  |  |          /   |  | |  | \   \ /   /  |  |    |  /  | | 
 |  | .--, \ \| |_.'  | |  |'.'|  | (|  '--.       \_) |  |\|  |  \   '   /, (|  '--. |  |_.' | 
(|  | '. (_/  |  .-.  | |  |   |  |  |  .--'         \ |  | |  |   \     /__) |  .--' |  .  '.' 
 |  '--'  |   |  | |  | |  |   |  |  |  `---.         `'  '-'  '    \   /     |  `---.|  |\  \  
  `------'    `--' `--' `--'   `--'  `------'           `-----'      `-'      `------'`--' '--' """


async def show_gameover(canvas, screen_height, screen_width):
    """Отображает надпись Game Over в центре экрана постоянно, чтобы не затиралась"""

    lines = TEXT.splitlines()
    frame_height = len(lines)
    frame_width = max(len(line) for line in lines)

    row = (screen_height - frame_height) // 2
    column = (screen_width - frame_width) // 2

    while True:
        draw_frame(canvas, row, column, TEXT)
        await asyncio.sleep(0)
