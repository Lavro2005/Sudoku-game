# GUI.py
import time

import pygame

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

    # Ініціалізація сітки
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

    # Оновлення моделі сітки
    def update_model(self):
        self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    # Розміщення значення в клітинці
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

    # Тимчасове розміщення значення в клітинці (ескіз)
    def sketch(self, val):
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    # Малювання сітки

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

    # Вибір клітинки

    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        self.cubes[row][col].selected = True
        self.selected = (row, col)

    # Очищення клітинки

    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    # Обробка кліку

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

    # Перевірка чи гра завершена

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True

    # Вирішення судоку

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

    # Вирішення судоку з візуалізацією

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

    # Ініціалізація клітинки

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    # Малювання клітинки

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

    # Малювання зміни в клітинці

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

    # Встановлення значення

    def set(self, val):
        self.value = val

    # Встановлення тимчасового значення

    def set_temp(self, val):
        self.temp = val


# Пошук порожньої клітинки
def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)  # row, col

    return None


# Перевірка валідності ходу
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


# Перемальовування вікна
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


# Форматування часу
def format_time(secs):
    sec = secs%60
    minute = secs//60
    hour = minute//60

    mat = " " + str(minute) + ":" + str(sec)
    return mat


# Функція для переміщення вибору клавішами зі стрілками
def move_selection(grid, dx, dy):
    try:
        if not grid.selected:
            grid.select(0, 0)
            return

        row, col = grid.selected
        new_row = row + dy
        new_col = col + dx

        if 0 <= new_row < grid.rows and 0 <= new_col < grid.cols:
            grid.select(new_row, new_col)
    except Exception as e:
        print(f"Помилка під час переміщення вибору: {e}")

# Функція для перевірки кількості помилок
def check_game_over(strikes, max_strikes=3):
    try:
        return strikes >= max_strikes
    except Exception as e:
        print(f"Помилка під час перевірки кількості помилок: {e}")
        return False

# Функція для малювання екрану завершення гри
def draw_end_screen(win, message, color, play_time):
    try:
        overlay = pygame.Surface((540, 600))
        overlay.set_alpha(200)
        overlay.fill((255, 255, 255))
        win.blit(overlay, (0, 0))

        fnt_large = pygame.font.SysFont("comicsans", 60, bold=True)
        text = fnt_large.render(message, 1, color)
        win.blit(text, (270 - text.get_width() / 2, 250 - text.get_height() / 2))

        fnt_small = pygame.font.SysFont("comicsans", 30)
        time_text = fnt_small.render(f"Час: {format_time(play_time)}", 1, (0, 0, 0))
        win.blit(time_text, (270 - time_text.get_width() / 2, 320))

        restart_text = fnt_small.render("Натисніть R для рестарту", 1, (0, 0, 0))
        win.blit(restart_text, (270 - restart_text.get_width() / 2, 360))

        pygame.display.update()
    except Exception as e:
        print(f"Помилка під час малювання екрану завершення: {e}")

# Функція для скидання стану гри
def reset_game(board_template, win):
    try:
        import time
        start = time.time()
        strikes = 0
        game_over = False
        victory = False
        
        # Створення нового екземпляра сітки
        new_grid = Grid(9, 9, 540, 540, win)
        # Примусово встановлюємо значення з шаблону
        for i in range(new_grid.rows):
            for j in range(new_grid.cols):
                new_grid.cubes[i][j].set(board_template[i][j])
                new_grid.cubes[i][j].set_temp(0)
        new_grid.update_model()
        new_grid.selected = None
        
        return new_grid, start, strikes, game_over, victory
    except Exception as e:
        print(f"Помилка під час скидання гри: {e}")
        import time
        # Повертаємо хоча б поточний час, щоб уникнути помилок розпакування
        return None, time.time(), 0, False, False

# Головна функція
def main():
    try:
        win = pygame.display.set_mode((540,600))
        pygame.display.set_caption("Sudoku")
        board = Grid(9, 9, 540, 540, win)
        
        # Збереження початкового масиву
        board_template = [row[:] for row in Grid.board]
        
        key = None
        run = True
        start = time.time()
        strikes = 0
        
        game_over = False
        victory = False
        final_time = 0
        
        while run:
            if not game_over and not victory:
                play_time = round(time.time() - start)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                
                if event.type == pygame.KEYDOWN:
                    if game_over or victory:
                        if event.key == pygame.K_r:
                            res = reset_game(board_template, win)
                            if res[0] is not None:
                                board, start, strikes, game_over, victory = res
                                key = None
                        continue
                    
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                        key = 1
                    if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                        key = 2
                    if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        key = 3
                    if event.key == pygame.K_4 or event.key == pygame.K_KP4:
                        key = 4
                    if event.key == pygame.K_5 or event.key == pygame.K_KP5:
                        key = 5
                    if event.key == pygame.K_6 or event.key == pygame.K_KP6:
                        key = 6
                    if event.key == pygame.K_7 or event.key == pygame.K_KP7:
                        key = 7
                    if event.key == pygame.K_8 or event.key == pygame.K_KP8:
                        key = 8
                    if event.key == pygame.K_9 or event.key == pygame.K_KP9:
                        key = 9
                    if event.key == pygame.K_DELETE:
                        if board.selected:
                            board.clear()
                        key = None
                    if event.key == pygame.K_SPACE:
                        board.solve_gui()
                    if event.key == pygame.K_UP:
                        move_selection(board, 0, -1)
                        key = None
                    if event.key == pygame.K_DOWN:
                        move_selection(board, 0, 1)
                        key = None
                    if event.key == pygame.K_LEFT:
                        move_selection(board, -1, 0)
                        key = None
                    if event.key == pygame.K_RIGHT:
                        move_selection(board, 1, 0)
                        key = None

                    if event.key == pygame.K_RETURN:
                        if board.selected:
                            i, j = board.selected
                            if board.cubes[i][j].temp != 0:
                                if board.place(board.cubes[i][j].temp):
                                    print("Success")
                                else:
                                    print("Wrong")
                                    strikes += 1
                                    if check_game_over(strikes, 3):
                                        game_over = True
                                        final_time = play_time
                                key = None

                                if board.is_finished():
                                    print("Game over")
                                    victory = True
                                    final_time = play_time

                if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not victory:
                    pos = pygame.mouse.get_pos()
                    clicked = board.click(pos)
                    if clicked:
                        board.select(clicked[0], clicked[1])
                        key = None

            if not game_over and not victory:
                if board.selected and key != None:
                    board.sketch(key)

                redraw_window(win, board, play_time, strikes)
                pygame.display.update()
            else:
                if victory:
                    draw_end_screen(win, "VICTORY!", (0, 200, 0), final_time)
                elif game_over:
                    draw_end_screen(win, "GAME OVER", (200, 0, 0), final_time)

    except Exception as e:
        print(f"Критична помилка у головному циклі: {e}")

main()
pygame.quit()
if __name__ == "__main__":
    main()
    pygame.quit()
