import time
from typing import ClassVar

import pygame

pygame.font.init()


class Grid:
    board: ClassVar[list[list[int]]] = [
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 7, 4, 0, 0],
        [0, 4, 9, 2, 0, 6, 0, 0, 7],
    ]

    # Ініціалізує ігрову сітку та її стан.
    def __init__(self, rows, cols, width, height, win, board_template=None):
        if rows <= 0 or cols <= 0 or width <= 0 or height <= 0:
            raise ValueError("Розміри дошки та вікна мають бути додатними")

        template = board_template if board_template is not None else self.board
        if len(template) != rows or any(len(row) != cols for row in template):
            raise ValueError("Шаблон дошки має відповідати її розмірам")

        self.rows = rows
        self.cols = cols
        self.cubes = [
            [Cube(template[i][j], i, j, width, height) for j in range(cols)]
            for i in range(rows)
        ]
        self.width = width
        self.height = height
        self.model = None
        self.update_model()
        self.selected = None
        self.win = win

    # Синхронізує модель із поточними значеннями клітинок.
    def update_model(self):
        self.model = [
            [self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)
        ]

    # Перевіряє та фіксує число у вибраній клітинці.
    def place(self, val):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model()

            if valid(self.model, val, (row, col)) and self.solve():
                return True
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.update_model()
                return False

    # Відображає тимчасове число у вибраній клітинці.
    def sketch(self, val):
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    # Малює лінії сітки та всі клітинки на екрані.
    def draw(self):
        # Draw Grid Lines
        gap = self.width / 9
        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(
                self.win, (0, 0, 0), (0, i * gap), (self.width, i * gap), thick
            )
            pygame.draw.line(
                self.win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick
            )

        # Draw Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(self.win)

    # Вибирає клітинку та скасовує попередній вибір.
    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        self.cubes[row][col].selected = True
        self.selected = (row, col)

    # Видаляє тимчасове число з порожньої клітинки.
    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    # Перетворює координати миші на координати клітинки.
    def click(self, pos):
        """
        :param: pos
        :return: (row, col)
        """
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y), int(x))
        else:
            return None

    # Перевіряє, чи заповнена вся дошка.
    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True

    # Розв'язує дошку методом пошуку з поверненням.
    def solve(self):
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i

                if self.solve():
                    return True

                self.model[row][col] = 0

        return False

    # Розв'язує дошку з покроковою анімацією у вікні.
    def solve_gui(self):
        self.update_model()
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i
                self.cubes[row][col].set(i)
                self.cubes[row][col].draw_change(self.win, True)
                self.update_model()
                pygame.display.update()
                pygame.time.delay(100)

                if self.solve_gui():
                    return True

                self.model[row][col] = 0
                self.cubes[row][col].set(0)
                self.update_model()
                self.cubes[row][col].draw_change(self.win, False)
                pygame.display.update()
                pygame.time.delay(100)

        return False


class Cube:
    rows = 9
    cols = 9

    # Ініціалізує одну клітинку дошки.
    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    # Малює значення та стан вибору клітинки.
    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, (128, 128, 128))
            win.blit(text, (x + 5, y + 5))
        elif self.value != 0:
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(
                text,
                (
                    x + (gap / 2 - text.get_width() / 2),
                    y + (gap / 2 - text.get_height() / 2),
                ),
            )

        if self.selected:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    # Малює зміну клітинки під час розв'язання.
    def draw_change(self, win, g=True):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        pygame.draw.rect(win, (255, 255, 255), (x, y, gap, gap), 0)

        text = fnt.render(str(self.value), 1, (0, 0, 0))
        win.blit(
            text,
            (
                x + (gap / 2 - text.get_width() / 2),
                y + (gap / 2 - text.get_height() / 2),
            ),
        )
        if g:
            pygame.draw.rect(win, (0, 255, 0), (x, y, gap, gap), 3)
        else:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    # Встановлює постійне значення клітинки.
    def set(self, val):
        self.value = val

    # Встановлює тимчасове значення клітинки.
    def set_temp(self, val):
        self.temp = val


# Знаходить першу порожню позицію на дошці.
def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)  # row, col

    return None


# Перевіряє допустимість числа у вказаній позиції.
def valid(bo, num, pos):
    # Check row
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and pos[1] != i:
            return False

    # Check column
    for i in range(len(bo)):
        if bo[i][pos[1]] == num and pos[0] != i:
            return False

    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if bo[i][j] == num and (i, j) != pos:
                return False

    return True


# Оновлює вікно гри, час, помилки та дошку.
def redraw_window(win, board, time, strikes):
    win.fill((255, 255, 255))
    # Draw time
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (0, 0, 0))
    win.blit(text, (540 - 160, 560))
    # Draw Strikes
    text = fnt.render("X " * strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    # Draw grid and board
    board.draw()


# Перетворює кількість секунд у текстовий формат часу.
def format_time(secs):
    sec = secs % 60
    minute = secs // 60

    mat = " " + str(minute) + ":" + str(sec)
    return mat


# Переміщує вибір клітинки за допомогою клавіш зі стрілками.
def move_selection(grid, dx, dy):
    if not isinstance(grid, Grid):
        raise TypeError("grid має бути екземпляром Grid")
    if isinstance(dx, bool) or not isinstance(dx, int):
        raise TypeError("dx має бути цілим числом")
    if isinstance(dy, bool) or not isinstance(dy, int):
        raise TypeError("dy має бути цілим числом")

    row, col = grid.selected if grid.selected is not None else (0, 0)
    new_row = max(0, min(grid.rows - 1, row + dy))
    new_col = max(0, min(grid.cols - 1, col + dx))
    grid.select(new_row, new_col)
    return grid.selected


# Перевіряє, чи досягнуто максимальної кількості помилок.
def check_game_over(strikes, max_strikes=3):
    if isinstance(strikes, bool) or not isinstance(strikes, int) or strikes < 0:
        raise ValueError("Кількість помилок має бути невід'ємним цілим числом")
    if (
        isinstance(max_strikes, bool)
        or not isinstance(max_strikes, int)
        or max_strikes <= 0
    ):
        raise ValueError("Ліміт помилок має бути додатним цілим числом")
    return strikes >= max_strikes


# Малює екран завершення гри поверх дошки.
def draw_end_screen(win, message, color):
    if win is None or not hasattr(win, "get_size"):
        raise TypeError("win має бути коректною поверхнею Pygame")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Повідомлення не може бути порожнім")
    if not isinstance(color, tuple) or len(color) != 3:
        raise ValueError("color має бути кортежем із трьох компонентів")

    overlay = pygame.Surface(win.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    win.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont("comicsans", 48, bold=True)
    text_font = pygame.font.SysFont("comicsans", 28)
    lines = message.splitlines()
    total_height = title_font.get_height() + len(lines) * text_font.get_height() + 30
    y = (win.get_height() - total_height) // 2

    title = title_font.render(lines[0], True, color)
    win.blit(title, ((win.get_width() - title.get_width()) // 2, y))
    y += title.get_height() + 15

    for line in lines[1:]:
        text = text_font.render(line, True, (255, 255, 255))
        win.blit(text, ((win.get_width() - text.get_width()) // 2, y))
        y += text.get_height()


# Створює нову гру з початковим шаблоном дошки.
def reset_game(board_template, win=None):
    if not isinstance(board_template, (list, tuple)) or not board_template:
        raise ValueError("Шаблон дошки має бути непорожнім списком")
    if win is None:
        win = pygame.display.get_surface()
    if win is None:
        raise RuntimeError("Для рестарту потрібне активне вікно Pygame")

    board = Grid(9, 9, 540, 540, win, board_template)
    return board, time.time(), 0, False, False


# Запускає головний цикл графічної гри.
def main():
    win = pygame.display.set_mode((540, 600))
    pygame.display.set_caption("Sudoku")
    board_template = [row[:] for row in Grid.board]
    board = Grid(9, 9, 540, 540, win, board_template)
    key = None
    run = True
    start = time.time()
    final_time = start
    strikes = 0
    victory = False
    game_over = False
    while run:
        play_time = (
            round(time.time() - start)
            if not victory and not game_over
            else round(final_time - start)
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (victory or game_over):
                    board, start, strikes, victory, game_over = reset_game(
                        board_template, win
                    )
                    key = None
                    continue
                if victory or game_over:
                    continue
                if event.key == pygame.K_LEFT:
                    move_selection(board, -1, 0)
                    key = None
                if event.key == pygame.K_RIGHT:
                    move_selection(board, 1, 0)
                    key = None
                if event.key == pygame.K_UP:
                    move_selection(board, 0, -1)
                    key = None
                if event.key == pygame.K_DOWN:
                    move_selection(board, 0, 1)
                    key = None
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_KP1:
                    key = 1
                if event.key == pygame.K_KP2:
                    key = 2
                if event.key == pygame.K_KP3:
                    key = 3
                if event.key == pygame.K_KP4:
                    key = 4
                if event.key == pygame.K_KP5:
                    key = 5
                if event.key == pygame.K_KP6:
                    key = 6
                if event.key == pygame.K_KP7:
                    key = 7
                if event.key == pygame.K_KP8:
                    key = 8
                if event.key == pygame.K_KP9:
                    key = 9
                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None

                if event.key == pygame.K_SPACE:
                    board.solve_gui()

                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            print("Success")
                        else:
                            print("Wrong")
                            strikes += 1
                            if check_game_over(strikes):
                                game_over = True
                                final_time = time.time()
                        key = None

                        if board.is_finished():
                            victory = True
                            final_time = time.time()
                            print("Victory")

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key != None:
            board.sketch(key)

        redraw_window(win, board, play_time, strikes)
        if victory:
            draw_end_screen(
                win,
                "VICTORY!\nЧас: "
                + format_time(play_time)
                + "\nНатисніть R для рестарту",
                (0, 180, 0),
            )
        elif game_over:
            draw_end_screen(
                win,
                "GAME OVER\nЧас: "
                + format_time(play_time)
                + "\nНатисніть R для рестарту",
                (220, 0, 0),
            )
        pygame.display.update()


if __name__ == "__main__":
    main()
    pygame.quit()
