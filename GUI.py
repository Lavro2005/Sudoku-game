# GUI.py
import pygame
import time
from typing import Optional, Tuple, Union
pygame.font.init()


class Grid:
    board = [
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 7, 4, 0, 0],
        [0, 4, 9, 2, 0, 6, 0, 0, 7]
    ]

    def __init__(self, rows, cols, width, height, win):
        self.rows = rows
        self.cols = cols
        self.cubes = [[Cube(self.board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
        self.width = width
        self.height = height
        self.model = None
        self.update_model()
        self.selected = None
        self.win = win

    def update_model(self):
        self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    def place(self, val):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model()

            if valid(self.model, val, (row,col)) and self.solve():
                return True
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.update_model()
                return False

    def sketch(self, val):
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    def draw(self):
        # Draw Grid Lines
        gap = self.width / 9
        for i in range(self.rows+1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(self.win, (0,0,0), (0, i*gap), (self.width, i*gap), thick)
            pygame.draw.line(self.win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

        # Draw Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(self.win)

    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    def click(self, pos):
        """
        :param: pos
        :return: (row, col)
        """
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y),int(x))
        else:
            return None

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True

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

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, (128,128,128))
            win.blit(text, (x+5, y+5))
        elif not(self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + (gap/2 - text.get_width()/2), y + (gap/2 - text.get_height()/2)))

        if self.selected:
            pygame.draw.rect(win, (255,0,0), (x,y, gap ,gap), 3)

    def draw_change(self, win, g=True):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        pygame.draw.rect(win, (255, 255, 255), (x, y, gap, gap), 0)

        text = fnt.render(str(self.value), 1, (0, 0, 0))
        win.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))
        if g:
            pygame.draw.rect(win, (0, 255, 0), (x, y, gap, gap), 3)
        else:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val


def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)  # row, col

    return None


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

    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x * 3, box_x*3 + 3):
            if bo[i][j] == num and (i,j) != pos:
                return False

    return True


def redraw_window(win, board, time, strikes):
    win.fill((255,255,255))
    # Draw time
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (0,0,0))
    win.blit(text, (540 - 160, 560))
    # Draw Strikes
    text = fnt.render("X " * strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    # Draw grid and board
    board.draw()


def format_time(secs):
    sec = secs%60
    minute = secs//60
    hour = minute//60

    mat = " " + str(minute) + ":" + str(sec)
    return mat

def move_selection(grid: Grid, dx: int, dy: int) -> bool:
    """
    Зміщує поточний вибір клітинки в сітці Sudoku на заданий зсув (dx, dy).
    
    :param grid: Екземпляр класу Grid.
    :param dx: Зсув по горизонталі (-1 — вліво, 1 — вправо, 0 — без змін).
    :param dy: Зсув по вертикалі (-1 — вгору, 1 — вниз, 0 — без змін).
    :return: True, якщо переміщення або початковий вибір успішно здійснено, інакше False.
    :raises TypeError: Якщо grid, dx або dy мають неправильний тип даних.
    :raises ValueError: Якщо grid знаходиться в некоректному стані (наприклад, 0 рядків/стовпців).
    """
    # 1. Валідація типів вхідних даних
    if not isinstance(grid, Grid):
        raise TypeError(f"Очікувався об'єкт Grid, отримано: {type(grid).__name__}")
    
    # Перевірка типів зсувів (bool є підтипом int у Python, тому відсікаємо його окремо)
    if isinstance(dx, bool) or not isinstance(dx, int):
        raise TypeError(f"Параметр dx повинен бути цілим числом (int), отримано: {type(dx).__name__}")
    if isinstance(dy, bool) or not isinstance(dy, int):
        raise TypeError(f"Параметр dy повинен бути цілим числом (int), отримано: {type(dy).__name__}")

    # 2. Перевірка цілісності стану об'єкта Grid
    if not hasattr(grid, 'rows') or not hasattr(grid, 'cols') or grid.rows <= 0 or grid.cols <= 0:
        raise ValueError("Об'єкт Grid має некоректні розміри рядків або стовпців.")

    try:
        # Якщо наразі жодної клітинки не вибрано — вибираємо ліву верхню (0, 0)
        if grid.selected is None:
            grid.select(0, 0)
            return True

        current_row, current_col = grid.selected

        # Обчислюємо нові координати з обмеженням у межах сітки [0, max - 1]
        # max(0, min(new_val, limit - 1)) запобігає виходу за межі поля
        new_row = max(0, min(current_row + dy, grid.rows - 1))
        new_col = max(0, min(current_col + dx, grid.cols - 1))

        # Оновлюємо вибір лише за потреби зміни координати
        if (new_row, new_col) != (current_row, current_col):
            grid.select(new_row, new_col)
            return True

        return False

    except (IndexError, AttributeError) as exc:
        # Обробка неочікуваних внутрішніх збоїв структури grid.cubes або методу select
        print(f"[Помилка навігації] Не вдалося змінити вибір: {exc}")
        return False

def check_game_over(strikes: int, max_strikes: int = 5) -> bool:
    """
    Перевіряє, чи перевищила кількість помилок гравця встановлений ліміт.

    :param strikes: Поточна кількість зроблених помилок.
    :param max_strikes: Максимально дозволена кількість помилок (за замовчуванням 5).
    :return: True, якщо ліміт помилок досягнуто або перевищено, інакше False.
    :raises TypeError: Якщо значення параметрів не є цілими числами.
    :raises ValueError: Якщо значення strikes або max_strikes є від'ємними.
    """
    # Захист від передачі boolean (bool є підтипом int у Python)
    if isinstance(strikes, bool) or not isinstance(strikes, int):
        raise TypeError(f"Параметр strikes має бути цілим числом (int), отримано: {type(strikes).__name__}")
    if isinstance(max_strikes, bool) or not isinstance(max_strikes, int):
        raise TypeError(f"Параметр max_strikes має бути цілим числом (int), отримано: {type(max_strikes).__name__}")

    if strikes < 0:
        raise ValueError(f"strikes не може бути від'ємним числом: {strikes}")
    if max_strikes <= 0:
        raise ValueError(f"max_strikes має бути більшим за 0: {max_strikes}")

    return strikes >= max_strikes

def draw_end_screen(
    win: pygame.Surface,
    message: str,
    color: Union[Tuple[int, int, int], Tuple[int, int, int, int]],
    play_time: Optional[int] = None
) -> None:
    """
    Малює банер кінця гри поверх основного вікна з повідомленням та фінальним часом.

    :param win: Головна поверхня вікна pygame (pygame.Surface).
    :param message: Повідомлення для відображення (наприклад, "VICTORY!" або "GAME OVER").
    :param color: Колір тексту повідомлення у форматі RGB або RGBA кортежу.
    :param play_time: Загальний витрачений час у секундах (необов'язковий).
    :raises TypeError: Якщо вхідні параметри не відповідають очікуваним типам.
    :raises ValueError: Якщо передано порожнє повідомлення або некоректні значення кольору.
    """
    if not isinstance(win, pygame.Surface):
        raise TypeError(f"win має бути об'єктом pygame.Surface, отримано: {type(win).__name__}")
    if not isinstance(message, str):
        raise TypeError(f"message має бути рядком (str), отримано: {type(message).__name__}")
    if not message.strip():
        raise ValueError("Повідомлення message не може бути порожнім.")

    if not isinstance(color, (tuple, list)) or len(color) not in (3, 4):
        raise TypeError("color має бути послідовністю з 3 (RGB) або 4 (RGBA) компонентів.")
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
        raise ValueError("Усі компоненти кольору мають бути цілими числами в діапазоні [0, 255].")

    if play_time is not None:
        if isinstance(play_time, bool) or not isinstance(play_time, int):
            raise TypeError(f"play_time має бути цілим числом, отримано: {type(play_time).__name__}")
        if play_time < 0:
            raise ValueError(f"play_time не може бути від'ємним: {play_time}")

    try:
        width, height = win.get_size()

        # 1. Створення напівпрозорого оверлею на все вікно
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((20, 20, 20, 185))  # Напівпрозорий темно-сірий фон
        win.blit(overlay, (0, 0))

        # 2. Плашка (банер) під текст по центру
        banner_width = int(width * 0.82)
        banner_height = 190
        banner_x = (width - banner_width) // 2
        banner_y = (height - banner_height) // 2 - 20

        banner_rect = pygame.Rect(banner_x, banner_y, banner_width, banner_height)
        pygame.draw.rect(win, (255, 255, 255), banner_rect, border_radius=12)
        pygame.draw.rect(win, color[:3], banner_rect, width=4, border_radius=12)

        # 3. Рендеринг основного повідомлення
        title_font = pygame.font.SysFont("comicsans", 50, bold=True)
        title_surf = title_font.render(message, True, color[:3])
        title_x = banner_x + (banner_width - title_surf.get_width()) // 2
        title_y = banner_y + 25
        win.blit(title_surf, (title_x, title_y))

        # 4. Рендеринг підсумкового часу
        sub_font = pygame.font.SysFont("comicsans", 30)
        time_str = f"Final Time: {format_time(play_time)}" if play_time is not None else "Game Finished"
        time_surf = sub_font.render(time_str, True, (60, 60, 60))
        time_x = banner_x + (banner_width - time_surf.get_width()) // 2
        time_y = title_y + title_surf.get_height() + 10
        win.blit(time_surf, (time_x, time_y))

        # 5. Підказка для виходу
        hint_font = pygame.font.SysFont("comicsans", 20)
        hint_surf = hint_font.render("Press any key to exit", True, (130, 130, 130))
        hint_x = banner_x + (banner_width - hint_surf.get_width()) // 2
        hint_y = banner_y + banner_height - hint_surf.get_height() - 15
        win.blit(hint_surf, (hint_x, hint_y))

    except pygame.error as pg_err:
        print(f"[Помилка відмальовки екрана закінчення гри]: {pg_err}")

def main():
    win = pygame.display.set_mode((540, 600))
    pygame.display.set_caption("Sudoku")
    board = Grid(9, 9, 540, 540, win)
    key = None
    run = True
    start = time.time()
    strikes = 0
    
    game_over = False
    game_won = False
    final_time = 0

    while run:
        # Таймер оновлюється лише поки гра триває
        if not game_over and not game_won:
            play_time = round(time.time() - start)
        else:
            play_time = final_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # Якщо гра завершена — будь-яка клавіша закриває гру
                if game_over or game_won:
                    run = False
                    break

                # Навігація стрілочками / WASD
                try:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        move_selection(board, dx=0, dy=-1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        move_selection(board, dx=0, dy=1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        move_selection(board, dx=-1, dy=0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        move_selection(board, dx=1, dy=0)
                except (TypeError, ValueError) as err:
                    print(f"Помилка навігації: {err}")

                # Введення цифр
                if event.key in (pygame.K_1, pygame.K_KP1): key = 1
                if event.key in (pygame.K_2, pygame.K_KP2): key = 2
                if event.key in (pygame.K_3, pygame.K_KP3): key = 3
                if event.key in (pygame.K_4, pygame.K_KP4): key = 4
                if event.key in (pygame.K_5, pygame.K_KP5): key = 5
                if event.key in (pygame.K_6, pygame.K_KP6): key = 6
                if event.key in (pygame.K_7, pygame.K_KP7): key = 7
                if event.key in (pygame.K_8, pygame.K_KP8): key = 8
                if event.key in (pygame.K_9, pygame.K_KP9): key = 9
                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None

                if event.key == pygame.K_SPACE:
                    if board.solve_gui():
                        game_won = True
                    else:
                        game_over = True
                    final_time = round(time.time() - start)

                if event.key == pygame.K_RETURN:
                    if board.selected:
                        i, j = board.selected
                        if board.cubes[i][j].temp != 0:
                            if board.place(board.cubes[i][j].temp):
                                print("Success")
                            else:
                                print("Wrong")
                                strikes += 1
                                # Перевірка ліміту помилок через check_game_over
                                if check_game_over(strikes, max_strikes=5):
                                    game_over = True
                                    final_time = round(time.time() - start)
                            key = None

                            if board.is_finished() and not game_over:
                                game_won = True
                                final_time = round(time.time() - start)

            if event.type == pygame.MOUSEBUTTONDOWN and not (game_over or game_won):
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key is not None and not (game_over or game_won):
            board.sketch(key)

        # Малюємо сітку та поточний стан
        redraw_window(win, board, play_time, strikes)

        # Якщо настала поразка чи перемога — виводимо банер поверх
        if game_over:
            draw_end_screen(win, message="GAME OVER", color=(220, 20, 60), play_time=play_time)
        elif game_won:
            draw_end_screen(win, message="VICTORY!", color=(34, 139, 34), play_time=play_time)
        

        pygame.display.update()

    pygame.quit()

main()
pygame.quit()
