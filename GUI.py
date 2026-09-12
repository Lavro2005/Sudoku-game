# GUI.py
import pygame
import time
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


def move_selection(grid, dx, dy):
    """
    Переміщує виділену клітинку сітки Sudoku на (dx, dy) клітинок,
    забезпечуючи навігацію клавіатурою (стрілочки / WASD).

    :param grid: об'єкт Grid, у якому потрібно змінити виділену клітинку
    :param dx: зміщення по горизонталі (стовпці): -1 (вліво), 0, 1 (вправо)
    :param dy: зміщення по вертикалі (рядки): -1 (вгору), 0, 1 (вниз)
    :return: True, якщо виділення успішно змінено, інакше False
    """

    # --- Валідація вхідних даних ---
    if grid is None:
        raise ValueError("Об'єкт grid не може бути None")

    if not isinstance(dx, int) or not isinstance(dy, int):
        raise TypeError("Параметри dx та dy мають бути цілими числами")

    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        raise ValueError("dx та dy можуть приймати лише значення -1, 0 або 1")

    if not hasattr(grid, "rows") or not hasattr(grid, "cols"):
        raise AttributeError("Переданий об'єкт grid не має атрибутів rows/cols")

    try:
        # Якщо жодна клітинка ще не вибрана — обираємо клітинку (0, 0)
        if grid.selected is None:
            new_row, new_col = 0, 0
        else:
            row, col = grid.selected
            new_row = row + dy
            new_col = col + dx

            # Обмежуємо координати межами сітки (не даємо вийти за поле)
            new_row = max(0, min(grid.rows - 1, new_row))
            new_col = max(0, min(grid.cols - 1, new_col))

        grid.select(new_row, new_col)
        return True

    except (TypeError, ValueError, IndexError) as error:
        # Обробка виняткових ситуацій: некоректні дані виділення,
        # вихід за межі списку клітинок тощо
        print(f"Не вдалося перемістити виділення: {error}")
        return False


def check_game_over(strikes, max_strikes=5):
    """
    Перевіряє, чи кількість помилок (strikes) перевищила допустимий ліміт.

    :param strikes: поточна кількість допущених помилок
    :param max_strikes: максимально допустима кількість помилок (за замовчуванням 5)
    :return: True, якщо ліміт помилок перевищено (гру потрібно завершити), інакше False
    """

    # --- Валідація вхідних даних ---
    if not isinstance(strikes, int) or isinstance(strikes, bool):
        raise TypeError("Параметр strikes має бути цілим числом")

    if strikes < 0:
        raise ValueError("Параметр strikes не може бути від'ємним")

    if not isinstance(max_strikes, int) or isinstance(max_strikes, bool):
        raise TypeError("Параметр max_strikes має бути цілим числом")

    if max_strikes <= 0:
        raise ValueError("Параметр max_strikes має бути додатним числом")

    try:
        return strikes >= max_strikes
    except TypeError as error:
        # Захист від несподіваних помилок порівняння
        print(f"Не вдалося перевірити умову завершення гри: {error}")
        return False


def draw_end_screen(win, message, color, final_time=None):
    """
    Малює напівпрозорий банер поверх ігрового поля з підсумковим
    повідомленням ("VICTORY!" або "GAME OVER") та, за наявності,
    підсумковим часом гри.

    :param win: поверхня pygame (вікно), на якій потрібно малювати
    :param message: текст банера, наприклад "VICTORY!" або "GAME OVER"
    :param color: колір тексту повідомлення у форматі (R, G, B)
    :param final_time: підсумковий час гри у секундах (необов'язково)
    :return: True, якщо банер намальовано успішно, інакше False
    """

    # --- Валідація вхідних даних ---
    if win is None:
        raise ValueError("Параметр win не може бути None")

    if not isinstance(message, str) or not message.strip():
        raise ValueError("Параметр message має бути непорожнім рядком")

    is_valid_color = (
        isinstance(color, (tuple, list))
        and len(color) == 3
        and all(isinstance(c, int) and 0 <= c <= 255 for c in color)
    )
    if not is_valid_color:
        raise ValueError("Параметр color має бути кортежем із трьох цілих чисел (0-255)")

    if final_time is not None and (
        isinstance(final_time, bool) or not isinstance(final_time, (int, float)) or final_time < 0
    ):
        raise TypeError("Параметр final_time має бути невід'ємним числом (секунди) або None")

    try:
        width, height = win.get_size()
    except AttributeError as error:
        raise AttributeError("Об'єкт win має підтримувати метод get_size()") from error

    try:
        # Напівпрозора підкладка поверх ігрового поля
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(200)
        overlay.fill((255, 255, 255))
        win.blit(overlay, (0, 0))

        # Основний текст банера
        title_fnt = pygame.font.SysFont("comicsans", 60)
        title_text = title_fnt.render(message, 1, tuple(color))
        win.blit(
            title_text,
            (width / 2 - title_text.get_width() / 2, height / 2 - title_text.get_height())
        )

        # Підсумковий час (якщо переданий)
        if final_time is not None:
            time_fnt = pygame.font.SysFont("comicsans", 40)
            time_str = "Time: " + format_time(int(final_time))
            time_text = time_fnt.render(time_str, 1, (0, 0, 0))
            win.blit(
                time_text,
                (width / 2 - time_text.get_width() / 2, height / 2 + 10)
            )

        pygame.display.update()
        return True

    except pygame.error as error:
        print(f"Помилка pygame під час малювання екрана завершення гри: {error}")
        return False
    except Exception as error:
        print(f"Непередбачена помилка під час малювання екрана завершення гри: {error}")
        return False


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


def main():
    win = pygame.display.set_mode((540,600))
    pygame.display.set_caption("Sudoku")
    board = Grid(9, 9, 540, 540, win)
    key = None
    run = True
    start = time.time()
    strikes = 0

    game_over = False
    victory = False
    frozen_time = 0
    end_message = ""
    end_color = (0, 0, 0)

    while run:

        if not game_over and not victory:
            play_time = round(time.time() - start)
        else:
            # Таймер зупинено - показуємо зафіксований підсумковий час
            play_time = frozen_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and not game_over and not victory:
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

                # Навігація клавіатурою: стрілочки
                if event.key == pygame.K_UP:
                    move_selection(board, 0, -1)
                if event.key == pygame.K_DOWN:
                    move_selection(board, 0, 1)
                if event.key == pygame.K_LEFT:
                    move_selection(board, -1, 0)
                if event.key == pygame.K_RIGHT:
                    move_selection(board, 1, 0)

                # Навігація клавіатурою: WASD
                if event.key == pygame.K_w:
                    move_selection(board, 0, -1)
                if event.key == pygame.K_s:
                    move_selection(board, 0, 1)
                if event.key == pygame.K_a:
                    move_selection(board, -1, 0)
                if event.key == pygame.K_d:
                    move_selection(board, 1, 0)

                if event.key == pygame.K_SPACE:
                    if board.solve_gui() and board.is_finished():
                        victory = True
                        frozen_time = play_time
                        end_message = "VICTORY!"
                        end_color = (0, 200, 0)
                        print("Victory")

                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            print("Success")
                        else:
                            print("Wrong")
                            strikes += 1
                        key = None

                        # Перевірка програшу за кількістю помилок
                        if check_game_over(strikes):
                            game_over = True
                            frozen_time = play_time
                            end_message = "GAME OVER"
                            end_color = (255, 0, 0)
                            print("Game over")

                        # Перевірка перемоги (поле заповнене без програшу)
                        elif board.is_finished():
                            victory = True
                            frozen_time = play_time
                            end_message = "VICTORY!"
                            end_color = (0, 200, 0)
                            print("Victory")

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not victory:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key != None:
            board.sketch(key)

        redraw_window(win, board, play_time, strikes)

        if game_over or victory:
            draw_end_screen(win, end_message, end_color, final_time=frozen_time)

        pygame.display.update()


main()
pygame.quit()
