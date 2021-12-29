
from .tetris import *

if __name__ == '__main__':
    grid = TetrisGrid(pos=(0, 30))
    screen = pygame.display.set_mode((300, 660))
    game = Tetris(grid, screen, ghost=True)

    game.main_loop()

    print('thanks for playing!')
