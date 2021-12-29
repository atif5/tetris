
import pygame


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SILVER = (192, 192, 192)


class Cell(pygame.Surface):
    def __init__(self, grid, num, size=(30, 30), occupied=False, o_color=None, shift=(0, 0)):

        super().__init__(size)

        self.grid = grid
        self.num = num
        self.handle_sides()
        self.size = size
        self.occupied = occupied
        self.o_color = o_color

        self.position = (
            self.size[0] * (self.num % grid.width)+shift[0],
            self.size[0] * (self.num // grid.width)+shift[1])

        self.rect = self.get_rect()
        self.rect.move_ip(self.position)

    def handle_sides(self):
        if self.num % 10 == 0:
            self.is_sidecell = True
            self.side = 'l'

        elif (self.num+1) % 10 == 0:
            self.is_sidecell = True
            self.side = 'r'
        else:
            self.is_sidecell = False

    def left(self):
        return self.grid.cells[self.num-1]

    def right(self):
        return self.grid.cells[self.num+1]

    def down(self, depth=1):
        return self.grid.cells[self.num+self.grid.width*depth]

    def exist(self, surface, ghost=False):
        if not ghost:
            surface.blit(self, self.position)
            pygame.draw.rect(surface, WHITE, self.rect, width=1)

        else:
            pygame.draw.rect(surface, WHITE, self.rect, width=6)

    def occupy(self, color):
        self.fill(color)
        self.occupied = True

        self.o_color = color

    def unoccupy(self):
        self.occupied = False
        self.fill(BLACK)
        self.o_color = None

    def fall(self, depth):
        down_cell = self.down(depth=depth)

        if not down_cell.occupied:
            down_cell.occupy(self.o_color)

            self.unoccupy()


class TetrisGrid():
    def __init__(self, pos):
        self.width = 10
        self.height = 21
        self.cell_amount = self.width*self.height
        self.size = (self.width, self.height)

        self.cells = [Cell(self, num=i, shift=pos)
                      for i in range(self.cell_amount)]

        self.lines = [self.cells[self.width*i:self.width*(i+1)]
                      for i in range(self.height)]

        self.handle_tetrominos()

    def handle_tetrominos(self):
        w = self.width

        self.tetrominos = {

            'I': [[-2, -1, 0, 1], [-2*w, -1*w, 0, w]],
            'Square': [[0, 1, w, w+1]],
            'Reverse L': [[-1, 0, 1, w+1], [-1*w, 0, w, w-1], [-1*w-1, -1, 0, 1], [-1*w+1, -1*w, 0, w]],
            'L': [[w-1, -1, 0, 1], [-1*w-1, -1*w, 0, w], [-1*w+1, 1, 0, -1], [-1*w, 0, w, w+1]],
            'S': [[1, 0, w, w-1], [-1*w, 0, 1, w+1]],
            'T': [[-1, 0, 1, w], [-1*w, 0, -1, w], [-1*w, -1, 0, 1], [-1*w, 0, 1, w]],
            'Reverse S': [[-1, 0, w, w+1], [-1*w+1, 1, 0, w]]


        }

    def exist(self, screen):
        for cell in self.cells:
            if cell not in self.lines[0]:
                cell.exist(screen)


class Tetromino():
    def __init__(self, tetrisgrid, shape, color, center_cell, rotational_state=0, sat=False, hard_dropped=False):
        self.tetrisgrid = tetrisgrid
        self.shape = shape
        self.r_matrix = self.tetrisgrid.tetrominos[self.shape]
        self.color = color
        self.center_cell = center_cell
        self.rotational_state = rotational_state
        self.sat = sat
        self.hard_dropped = hard_dropped

        self.cells = [self.tetrisgrid.cells[self.center_cell.num+i]
                      for i in self.r_matrix[self.rotational_state]]

        for cell in self.cells:
            if not cell.occupied:
                cell.occupy(self.color)

    def displace(self, old_cells, new_cells):
        for cell in old_cells:
            cell.unoccupy()

        for cell in new_cells:
            cell.occupy(self.color)

    def fall(self):
        old_cells = self.cells

        if self.is_in_contact():
            return

        self.cells = [cell.down() for cell in self.cells]
        self.center_cell = self.center_cell.down()

        new_cells = self.cells

        self.displace(old_cells, new_cells)

    def go_left(self):
        for cell in self.cells:
            if cell.is_sidecell:
                if cell.side == 'l':
                    return
        
        old_cells = self.cells

        self.cells = [cell.left() for cell in self.cells]
        self.center_cell = self.center_cell.left()

        new_cells = self.cells

        for cell in new_cells:
            if cell.occupied and cell not in old_cells:
                self.cells = old_cells
                return

        self.displace(old_cells, new_cells)

    def go_right(self):
        for cell in self.cells:
            if cell.is_sidecell:
                if cell.side == 'r':
                    return

        old_cells = self.cells

        self.cells = [cell.right() for cell in self.cells]
        self.center_cell = self.center_cell.right()

        new_cells = self.cells

        for cell in new_cells:
            if cell.occupied and cell not in old_cells:
                self.cells = old_cells
                return

        self.displace(old_cells, new_cells)

    def rotate(self):
        if self.center_cell.is_sidecell:
            return

        if self.shape == 'I':
            if self.center_cell.left().is_sidecell or self.center_cell.right().is_sidecell:
                return

        if self.rotational_state == len(self.r_matrix)-1:
            self.rotational_state = 0
        else:
            self.rotational_state += 1

        old_cells = self.cells

        try:
            self.cells = [self.tetrisgrid.cells[self.center_cell.num+i]
                          for i in self.r_matrix[self.rotational_state]]
        except IndexError:
            self.cells = old_cells
            return

        new_cells = self.cells

        for cell in new_cells:
            if cell.occupied and cell not in old_cells:
                self.cells = old_cells
                return

        self.displace(old_cells, new_cells)

    def sit(self):
        self.sat = True

    def is_in_contact(self):
        try:
            down_cells = [
                cell.down() for cell in self.cells if cell.down() not in self.cells]

        except IndexError:
            return True

        for cell in down_cells:
            if cell.occupied and cell not in self.cells:
                return True

    def hard_drop(self):
        while not self.is_in_contact():
            self.fall()

        self.hard_dropped = True

    def project(self, screen):
        try:
            self.shadow_cells = [cell for cell in self.cells]
        except IndexError:
            pass

        while True:
            try:
                down_cells = [cell.down(
                ) for cell in self.shadow_cells if cell.down() not in self.shadow_cells]
            except IndexError:
                break

            for cell in down_cells:
                if cell.occupied:
                    break

            else:
                self.shadow_cells = [cell.down() for cell in self.shadow_cells]
                continue

            break

        for cell in self.shadow_cells:
            cell.exist(screen, ghost=True)
