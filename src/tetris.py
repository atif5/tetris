

from .cells import *
import pygame_gui
import time

from random import randint

pygame.font.init()

BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (221, 160, 221)
ORANGE = (255, 69, 0)


class Tetris:
    def __init__(self, grid, screen, ghost=True):
        self.grid = grid
        self.screen = screen
        self.ghost = ghost
        self.lines = self.grid.lines

        self.manager = pygame_gui.UIManager(screen.get_size())

        cell_height = self.grid.cells[0].size[0]

        self.logo = pygame.image.load('./src/logo.png')
        pygame.display.set_icon(self.logo)
        pygame.display.set_caption('Tetris')

        self.font_ = pygame.font.SysFont('main', 30)
        self.score = 0

        self.tetrominos = ['I', 'Square', 'T',
                           'S', 'Reverse S', 'Reverse L', 'L']

        self.bag = self.tetrominos.copy()
        self.color_map = {

            'I': CYAN,
            'Square': YELLOW,
            'T': PURPLE,
            'S': RED,
            'Reverse S': GREEN,
            'Reverse L': BLUE,
            'L': ORANGE

        }

        self.input_action = {

            pygame.K_LEFT: lambda tetromino: tetromino.go_left(),
            pygame.K_RIGHT: lambda tetromino: tetromino.go_right(),
            pygame.K_DOWN: lambda tetromino: tetromino.fall(),
            pygame.K_UP: lambda tetromino: tetromino.rotate(),
            pygame.K_SPACE: lambda tetromino: tetromino.hard_drop()
        }

        self.popped = False
        self.popped_lines = list()

        self.tbutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 275), (100, 50)),
                                             text='Try Again',
                                            manager=self.manager)
        self.qbutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 425), (150, 50)),
                                             text='I wanna quit!',
                                            manager=self.manager)

    def text(self):
        if self.popped:
            if len(self.popped_lines) == 4:
                t_surface = self.font_.render(
                    f'TETRIS!', False, WHITE)
            else:
                t_surface = self.font_.render(
                    f'{len(self.popped_lines)} line(s)!', False, WHITE)
        else:
            t_surface = self.font_.render(f'Score: {self.score}', False, WHITE)

        r = pygame.rect.Rect((0, 0), (600, 30))
        self.screen.fill(WHITE, r)
        self.screen.fill(BLACK, r)

        return t_surface

    def new_tetromino(self):
        if self.bag == []:
            self.bag = self.tetrominos.copy()

        current_shape = self.bag.pop(randint(0, len(self.bag)-1))

        current_tetromino = Tetromino(
            self.grid, current_shape, self.color_map[current_shape],
            self.grid.cells[5+self.grid.width])

        return current_tetromino

    def handle_drawing(self):
        self.grid.exist(self.screen)
        if self.ghost:
            self.current_tetromino.project(self.screen)

    def handle_lines(self):
        self.popped = False
        self.popped_lines = list()

        for line in self.lines[::-1]:
            occupied_cells = [cell for cell in line if cell.occupied]
            if len(occupied_cells) == self.grid.width:
                self.popped_lines.append(self.lines[::-1].index(line))

                for cell in occupied_cells:
                    cell.unoccupy()
                    self.handle_drawing()
                    pygame.display.flip()
                    time.sleep(0.01)

                self.popped = True

        if self.popped:
            self.handle_popping()

    def handle_popping(self):
        self.score += 10000*len(self.popped_lines)

        lines_to_fall = [line for line in self.lines[::-1][self.popped_lines[0]:] if len(
            [cell for cell in line if cell.occupied]) != 0]

        for line in lines_to_fall:
            depth = 0

            try:
                unoccupied_downcells = [
                    cell.down() for cell in line if not cell.down().occupied]
            except IndexError:
                continue

            while len(unoccupied_downcells) == self.grid.width:
                depth += 1

                try:
                    unoccupied_downcells = [
                        cell.down() for cell in unoccupied_downcells
                        if not cell.down().occupied]
                except IndexError:
                    break

            for cell in line:
                if cell.occupied:
                    cell.fall(depth)
                    self.handle_drawing()
                    pygame.display.flip()
                    time.sleep(0.02)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                try:
                    self.input_action[event.key](self.current_tetromino)
                except KeyError:
                    pass

            elif event.type == pygame.QUIT:
                exit()

    def let_player_adjust(self, clock, time):
        for _ in range(time):
            self.handle_drawing()
            self.handle_input()

            clock.tick(18)

            pygame.display.flip()

    def end(self, clock):
        for i, line in enumerate(self.grid.lines):
            if not i % 2:
                line.reverse()

            for cell in line:
                cell.occupy(RED)
                cell.exist(self.screen)
                clock.tick(50)
                pygame.display.flip()

        for i, line in enumerate(self.grid.lines):
            if not i % 2:
                line.reverse()

            for cell in line:
                cell.unoccupy()
                cell.exist(self.screen)
                clock.tick(100)
                pygame.display.flip()

        

        while True:
            for event in pygame.event.get():
                self.manager.process_events(event)
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.tbutton:
                            break
                        elif event.ui_element == self.qbutton:
                            return
            else:
                self.manager.update(60)
                self.manager.draw_ui(self.screen)
                pygame.display.flip()
                continue

            break

        self.score = 0
        self.main_loop()

    def main_loop(self):
        game_over = False

        self.current_tetromino = self.new_tetromino()
        clock = pygame.time.Clock()
        frames = 0

        while not game_over:

            if not frames % 3:
                self.current_tetromino.fall()
                self.score += 5

            self.handle_drawing()
            self.screen.blit(self.text(), (0, 0))
            self.handle_input()

            if self.current_tetromino.is_in_contact():
                if self.current_tetromino.hard_dropped:
                    self.current_tetromino.sit()

                else:
                    self.let_player_adjust(clock, 7)

                    if self.current_tetromino.is_in_contact():
                        self.current_tetromino.sit()

            if self.current_tetromino.sat:
                if self.current_tetromino.center_cell in self.lines[1]:
                    game_over = True
                    self.handle_drawing()
                    time.sleep(1)

                else:
                    self.handle_lines()
                    self.current_tetromino = self.new_tetromino()

            clock.tick(18)
            frames += 1

            if frames > 18:
                frames -= 19

            pygame.display.flip()

        self.end(clock)
