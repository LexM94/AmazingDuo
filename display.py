from maze_generator import MazeGenerator, NORTH, EAST, SOUTH, WEST
from config import load_config

config = load_config("config.txt")

RESET = "\033[0m"
WALL_COLORS = [15, 226, 51, 208]

def _bloc(couleur: int) -> str:
    return f"\033[48;5;{couleur}m  {RESET}"


def render_ascii(maze, wall_color):
    rows = 2 * maze.height + 1
    cols = 2 * maze.width + 1
    canvas = [[_bloc(0) for _ in range(cols)] for _ in range(rows)]  # 0 = noir (vide)

    for row in range(rows):
        for col in range(cols):
            if row % 2 == 0 and col % 2 == 0:
                canvas[row][col] = _bloc(wall_color)

    for y in range(maze.height):
        for x in range(maze.width):
            row, col = 2 * y + 1, 2 * x + 1
            if maze.has_wall(x, y, NORTH):
                canvas[row - 1][col] = _bloc(wall_color)
            if maze.has_wall(x, y, SOUTH):
                canvas[row + 1][col] = _bloc(wall_color)
            if maze.has_wall(x, y, WEST):
                canvas[row][col - 1] = _bloc(wall_color)
            if maze.has_wall(x, y, EAST):
                canvas[row][col + 1] = _bloc(wall_color)

            if (x, y) == maze.entry:
                canvas[row][col] = _bloc(201)  # magenta
            elif (x, y) == maze.exit:
                canvas[row][col] = _bloc(196)  # rouge

    return "\n".join("".join(line) for line in canvas)

m = MazeGenerator(config.width, config.height, config.entry, config.exit)
index_colors = 0

while True:
    print(render_ascii(m, WALL_COLORS[index_colors]))
    print("=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show/Hide path from entry to exit")
    print("3. Rotate maze colors")
    print("4. Quit")
    choix = input("Choix ?\n")
    if choix == "1":
        m = MazeGenerator(config.width, config.height, config.entry, config.exit)
    if choix == "2":
        pass
    if choix == "3":
        index_colors = (index_colors + 1) % len(WALL_COLORS)
    if choix == "4":
        break