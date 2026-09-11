"""Pygame-based Sudoku game with cached rendering and non-blocking solving."""

from __future__ import annotations

from collections.abc import Generator
from copy import deepcopy
from time import monotonic

import pygame

pygame.font.init()


# -----------------------------------------------------------------------------
# Configuration constants
# -----------------------------------------------------------------------------
WINDOW_WIDTH = 540
WINDOW_HEIGHT = 600
GRID_WIDTH = 540
GRID_HEIGHT = 540
GRID_SIZE = 9
BOX_SIZE = 3
MAX_STRIKES = 5
FPS = 60
SOLVE_STEP_DELAY = 0.1

FONT_NAME = "comicsans"
FONT_CELL = pygame.font.SysFont(FONT_NAME, 40)
FONT_TITLE = pygame.font.SysFont(FONT_NAME, 50, bold=True)
FONT_SUBTITLE = pygame.font.SysFont(FONT_NAME, 30)
FONT_HINT = pygame.font.SysFont(FONT_NAME, 20)

COLOR_BG = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GREY = (128, 128, 128)
COLOR_DARK_GREY = (60, 60, 60)
COLOR_HINT = (130, 130, 130)
COLOR_GRID = (0, 0, 0)
COLOR_SELECTION = (255, 0, 0)
COLOR_SUCCESS = (34, 139, 34)
COLOR_ERROR = (220, 20, 60)
COLOR_SOLVER_SUCCESS = (0, 255, 0)

DEFAULT_BOARD = [
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

KEY_MAPPING = {
    pygame.K_1: 1,
    pygame.K_KP1: 1,
    pygame.K_2: 2,
    pygame.K_KP2: 2,
    pygame.K_3: 3,
    pygame.K_KP3: 3,
    pygame.K_4: 4,
    pygame.K_KP4: 4,
    pygame.K_5: 5,
    pygame.K_KP5: 5,
    pygame.K_6: 6,
    pygame.K_KP6: 6,
    pygame.K_7: 7,
    pygame.K_KP7: 7,
    pygame.K_8: 8,
    pygame.K_KP8: 8,
    pygame.K_9: 9,
    pygame.K_KP9: 9,
}


def _box_index(row: int, col: int) -> int:
    """Return the 3x3 box index for a Sudoku cell."""
    return (row // BOX_SIZE) * BOX_SIZE + col // BOX_SIZE


class SudokuSolver:
    """Pure Sudoku solver independent of the Pygame GUI."""

    @staticmethod
    def _prepare_sets(board: list[list[int]]) -> tuple[
        list[set[int]], list[set[int]], list[set[int]]
    ]:
        """Build row, column and 3x3-box value sets for O(1) lookups."""
        rows = [set() for _ in range(GRID_SIZE)]
        cols = [set() for _ in range(GRID_SIZE)]
        boxes = [set() for _ in range(GRID_SIZE)]

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                value = board[row][col]
                if value != 0:
                    rows[row].add(value)
                    cols[col].add(value)
                    boxes[_box_index(row, col)].add(value)

        return rows, cols, boxes

    @staticmethod
    def _can_place(
        value: int,
        row: int,
        col: int,
        rows: list[set[int]],
        cols: list[set[int]],
        boxes: list[set[int]],
    ) -> bool:
        """Check a Sudoku move using constant-time set membership."""
        return (
            value not in rows[row]
            and value not in cols[col]
            and value not in boxes[_box_index(row, col)]
        )

    @classmethod
    def solve(cls, board: list[list[int]]) -> bool:
        """Solve a Sudoku board in place and return whether it was solved."""
        rows, cols, boxes = cls._prepare_sets(board)
        return cls._solve_recursive(board, rows, cols, boxes)

    @classmethod
    def _solve_recursive(
        cls,
        board: list[list[int]],
        rows: list[set[int]],
        cols: list[set[int]],
        boxes: list[set[int]],
    ) -> bool:
        """Recursive backtracking implementation used by solve()."""
        position = find_empty(board)
        if position is None:
            return True

        row, col = position
        box = _box_index(row, col)

        for value in range(1, GRID_SIZE + 1):
            if not cls._can_place(value, row, col, rows, cols, boxes):
                continue

            board[row][col] = value
            rows[row].add(value)
            cols[col].add(value)
            boxes[box].add(value)

            if cls._solve_recursive(board, rows, cols, boxes):
                return True

            board[row][col] = 0
            rows[row].remove(value)
            cols[col].remove(value)
            boxes[box].remove(value)

        return False

    @classmethod
    def solve_steps(
        cls, board: list[list[int]]
    ) -> Generator[tuple[int, int, int], None, bool]:
        """Yield every GUI change while solving the board incrementally."""
        rows, cols, boxes = cls._prepare_sets(board)
        return (yield from cls._solve_steps_recursive(board, rows, cols, boxes))

    @classmethod
    def _solve_steps_recursive(
        cls,
        board: list[list[int]],
        rows: list[set[int]],
        cols: list[set[int]],
        boxes: list[set[int]],
    ) -> Generator[tuple[int, int, int], None, bool]:
        """Generator-based backtracking used for non-blocking GUI animation."""
        position = find_empty(board)
        if position is None:
            return True

        row, col = position
        box = _box_index(row, col)

        for value in range(1, GRID_SIZE + 1):
            if not cls._can_place(value, row, col, rows, cols, boxes):
                continue

            board[row][col] = value
            rows[row].add(value)
            cols[col].add(value)
            boxes[box].add(value)
            yield row, col, value

            solved = yield from cls._solve_steps_recursive(
                board, rows, cols, boxes
            )
            if solved:
                return True

            board[row][col] = 0
            rows[row].remove(value)
            cols[col].remove(value)
            boxes[box].remove(value)
            yield row, col, 0

        return False


class Grid:
    """Stores the Sudoku board and coordinates its interaction with the GUI."""

    def __init__(
        self,
        rows: int,
        cols: int,
        width: int,
        height: int,
        win: pygame.Surface,
        board: list[list[int]] | None = None,
    ) -> None:
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        self.win = win

        # Copy the input so each Grid instance owns its own mutable board.
        source_board = deepcopy(DEFAULT_BOARD if board is None else board)
        self.cubes = [
            [Cube(source_board[row][col], row, col, width, height) for col in range(cols)]
            for row in range(rows)
        ]

        self.model: list[list[int]] = []
        self.selected: tuple[int, int] | None = None
        self.solution = deepcopy(source_board)
        if not SudokuSolver.solve(self.solution):
            raise ValueError("Передана некоректна Sudoku-дошка без розв'язку.")

        self._solve_generator: Generator[tuple[int, int, int], None, bool] | None = None
        self.update_model()

    def update_model(self) -> None:
        """Synchronize the numeric model with the visible cubes."""
        self.model = [
            [self.cubes[row][col].value for col in range(self.cols)]
            for row in range(self.rows)
        ]

    def place(self, val: int) -> bool:
        """Place a value when it matches the precomputed Sudoku solution."""
        if self.selected is None:
            return False

        row, col = self.selected
        cube = self.cubes[row][col]

        if cube.value != 0:
            return False

        if valid(self.model, val, (row, col)) and val == self.solution[row][col]:
            cube.set(val)
            self.update_model()
            return True

        cube.set_temp(0)
        return False

    def sketch(self, val: int) -> None:
        """Show a temporary value in the selected cell."""
        if self.selected is None:
            return
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(val)

    def draw(self) -> None:
        """Draw the Sudoku grid and all cells."""
        # Draw Grid Lines
        gap_x = self.width / self.cols
        gap_y = self.height / self.rows
        for index in range(self.rows + 1):
            thick = 4 if index % BOX_SIZE == 0 and index != 0 else 1
            pygame.draw.line(
                self.win,
                COLOR_GRID,
                (0, index * gap_y),
                (self.width, index * gap_y),
                thick,
            )
            pygame.draw.line(
                self.win,
                COLOR_GRID,
                (index * gap_x, 0),
                (index * gap_x, self.height),
                thick,
            )

        # Draw Cubes
        for row in range(self.rows):
            for col in range(self.cols):
                self.cubes[row][col].draw(self.win)

    def select(self, row: int, col: int) -> None:
        """Select a cell and clear the previous selection."""
        # Reset all other
        for cube_row in self.cubes:
            for cube in cube_row:
                cube.selected = False

        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def clear(self) -> None:
        """Clear the temporary value in the selected cell."""
        if self.selected is None:
            return
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    def click(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        """
        :param: pos
        :return: (row, col)
        """
        if pos[0] < self.width and pos[1] < self.height:
            gap_x = self.width / self.cols
            gap_y = self.height / self.rows
            col = int(pos[0] // gap_x)
            row = int(pos[1] // gap_y)
            return row, col

        return None

    def is_finished(self) -> bool:
        """Return True when no Sudoku cell is empty."""
        return all(cube.value != 0 for row in self.cubes for cube in row)

    def solve(self) -> bool:
        """Solve the current model synchronously when a full solve is required."""
        self.update_model()
        if SudokuSolver.solve(self.model):
            for row in range(self.rows):
                for col in range(self.cols):
                    self.cubes[row][col].set(self.model[row][col])
            return True
        return False

    def start_solve_gui(self) -> None:
        """Prepare a generator-based solver so the main loop stays responsive."""
        self.update_model()
        self._solve_generator = SudokuSolver.solve_steps(self.model)

    def solve_gui(self) -> bool | None:
        """Perform one visual backtracking step without blocking the event loop."""
        if self._solve_generator is None:
            self.start_solve_gui()

        try:
            row, col, value = next(self._solve_generator)
            self.cubes[row][col].set(value)
            self.cubes[row][col].set_temp(0)
            return None
        except StopIteration as result:
            self._solve_generator = None
            if result.value:
                self.update_model()
            return bool(result.value)

    def move_selection(self, dx: int, dy: int) -> bool:
        """
        Зміщує поточний вибір клітинки в сітці Sudoku на заданий зсув (dx, dy).

        :param dx: Зсув по горизонталі (-1 — вліво, 1 — вправо, 0 — без змін).
        :param dy: Зсув по вертикалі (-1 — вгору, 1 — вниз, 0 — без змін).
        :return: True, якщо переміщення або початковий вибір успішно здійснено, інакше False.
        :raises TypeError: Якщо dx або dy мають неправильний тип даних.
        :raises ValueError: Якщо Grid знаходиться в некоректному стані.
        """
        # 1. Валідація типів вхідних даних
        # bool є підтипом int у Python, тому відсікаємо його окремо.
        if isinstance(dx, bool) or not isinstance(dx, int):
            raise TypeError(
                f"Параметр dx повинен бути цілим числом (int), отримано: {type(dx).__name__}"
            )
        if isinstance(dy, bool) or not isinstance(dy, int):
            raise TypeError(
                f"Параметр dy повинен бути цілим числом (int), отримано: {type(dy).__name__}"
            )

        # 2. Перевірка цілісності стану об'єкта Grid
        if self.rows <= 0 or self.cols <= 0:
            raise ValueError("Об'єкт Grid має некоректні розміри рядків або стовпців.")

        try:
            # Якщо наразі жодної клітинки не вибрано — вибираємо ліву верхню (0, 0)
            if self.selected is None:
                self.select(0, 0)
                return True

            current_row, current_col = self.selected

            # Обчислюємо нові координати з обмеженням у межах сітки [0, max - 1]
            # max(0, min(new_val, limit - 1)) запобігає виходу за межі поля
            new_row = max(0, min(current_row + dy, self.rows - 1))
            new_col = max(0, min(current_col + dx, self.cols - 1))

            # Оновлюємо вибір лише за потреби зміни координати
            if (new_row, new_col) != (current_row, current_col):
                self.select(new_row, new_col)
                return True

            return False

        except (IndexError, AttributeError) as exc:
            # Обробка неочікуваних внутрішніх збоїв структури grid.cubes або методу select
            print(f"[Помилка навігації] Не вдалося змінити вибір: {exc}")
            return False


class Cube:
    """Represents one visible Sudoku cell."""

    def __init__(
        self,
        value: int,
        row: int,
        col: int,
        width: int,
        height: int,
    ) -> None:
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, win: pygame.Surface) -> None:
        """Draw the current value or temporary value."""
        gap = self.width / GRID_SIZE
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = FONT_CELL.render(str(self.temp), True, COLOR_GREY)
            win.blit(text, (x + 5, y + 5))
        elif self.value != 0:
            text = FONT_CELL.render(str(self.value), True, COLOR_BLACK)
            win.blit(
                text,
                (
                    x + (gap / 2 - text.get_width() / 2),
                    y + (gap / 2 - text.get_height() / 2),
                ),
            )

        if self.selected:
            pygame.draw.rect(win, COLOR_SELECTION, (x, y, gap, gap), 3)

    def draw_change(self, win: pygame.Surface, good: bool = True) -> None:
        """Draw a solver change and indicate whether it is valid."""
        gap = self.width / GRID_SIZE
        x = self.col * gap
        y = self.row * gap

        pygame.draw.rect(win, COLOR_BG, (x, y, gap, gap), 0)
        text = FONT_CELL.render(str(self.value), True, COLOR_BLACK)
        win.blit(
            text,
            (
                x + (gap / 2 - text.get_width() / 2),
                y + (gap / 2 - text.get_height() / 2),
            ),
        )
        border_color = COLOR_SOLVER_SUCCESS if good else COLOR_SELECTION
        pygame.draw.rect(win, border_color, (x, y, gap, gap), 3)

    def set(self, val: int) -> None:
        """Set the permanent cell value."""
        self.value = val

    def set_temp(self, val: int) -> None:
        """Set the temporary cell value."""
        self.temp = val


def find_empty(board: list[list[int]]) -> tuple[int, int] | None:
    """Return the first empty cell, or None when the board is complete."""
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == 0:
                return row, col  # row, col
    return None


def valid(board: list[list[int]], num: int, pos: tuple[int, int]) -> bool:
    """Check whether a number is valid at the requested position."""
    row, col = pos

    # Check row
    row_values = set(board[row])
    row_values.discard(0)
    row_values.discard(board[row][col])
    if num in row_values:
        return False

    # Check column
    col_values = {board[index][col] for index in range(len(board))}
    col_values.discard(0)
    col_values.discard(board[row][col])
    if num in col_values:
        return False

    # Check box
    box_x = col // BOX_SIZE
    box_y = row // BOX_SIZE
    box_values = {
        board[index][j]
        for index in range(box_y * BOX_SIZE, box_y * BOX_SIZE + BOX_SIZE)
        for j in range(box_x * BOX_SIZE, box_x * BOX_SIZE + BOX_SIZE)
    }
    box_values.discard(0)
    box_values.discard(board[row][col])
    return num not in box_values


def redraw_window(
    win: pygame.Surface,
    board: Grid,
    play_time: int,
    strikes: int,
) -> None:
    """Redraw the complete game window."""
    win.fill(COLOR_BG)

    # Draw time
    text = FONT_CELL.render(f"Time: {format_time(play_time)}", True, COLOR_BLACK)
    win.blit(text, (WINDOW_WIDTH - 160, GRID_HEIGHT + 20))

    # Draw Strikes
    text = FONT_CELL.render("X " * strikes, True, COLOR_SELECTION)
    win.blit(text, (20, GRID_HEIGHT + 20))

    # Draw grid and board
    board.draw()


def format_time(secs: int) -> str:
    """Format a number of seconds as minutes and seconds."""
    sec = secs % 60
    minute = secs // 60
    return f"{minute}:{sec:02d}"


def check_game_over(strikes: int, max_strikes: int = MAX_STRIKES) -> bool:
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
        raise TypeError(
            f"Параметр strikes має бути цілим числом (int), отримано: {type(strikes).__name__}"
        )
    if isinstance(max_strikes, bool) or not isinstance(max_strikes, int):
        raise TypeError(
            f"Параметр max_strikes має бути цілим числом (int), отримано: {type(max_strikes).__name__}"
        )

    if strikes < 0:
        raise ValueError(f"strikes не може бути від'ємним числом: {strikes}")
    if max_strikes <= 0:
        raise ValueError(f"max_strikes має бути більшим за 0: {max_strikes}")

    return strikes >= max_strikes


def draw_end_screen(
    win: pygame.Surface,
    message: str,
    color: tuple[int, int, int] | tuple[int, int, int, int],
    play_time: int | None = None,
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
        raise TypeError(
            f"win має бути об'єктом pygame.Surface, отримано: {type(win).__name__}"
        )
    if not isinstance(message, str):
        raise TypeError(
            f"message має бути рядком (str), отримано: {type(message).__name__}"
        )
    if not message.strip():
        raise ValueError("Повідомлення message не може бути порожнім.")

    if not isinstance(color, (tuple, list)) or len(color) not in (3, 4):
        raise TypeError(
            "color має бути послідовністю з 3 (RGB) або 4 (RGBA) компонентів."
        )
    if not all(isinstance(component, int) and 0 <= component <= 255 for component in color):
        raise ValueError(
            "Усі компоненти кольору мають бути цілими числами в діапазоні [0, 255]."
        )

    if play_time is not None:
        if isinstance(play_time, bool) or not isinstance(play_time, int):
            raise TypeError(
                f"play_time має бути цілим числом, отримано: {type(play_time).__name__}"
            )
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
        pygame.draw.rect(win, COLOR_BG, banner_rect, border_radius=12)
        pygame.draw.rect(win, color[:3], banner_rect, width=4, border_radius=12)

        # 3. Рендеринг основного повідомлення
        title_surf = FONT_TITLE.render(message, True, color[:3])
        title_x = banner_x + (banner_width - title_surf.get_width()) // 2
        title_y = banner_y + 25
        win.blit(title_surf, (title_x, title_y))

        # 4. Рендеринг підсумкового часу
        time_str = (
            f"Final Time: {format_time(play_time)}"
            if play_time is not None
            else "Game Finished"
        )
        time_surf = FONT_SUBTITLE.render(time_str, True, COLOR_DARK_GREY)
        time_x = banner_x + (banner_width - time_surf.get_width()) // 2
        time_y = title_y + title_surf.get_height() + 10
        win.blit(time_surf, (time_x, time_y))

        # 5. Підказка для виходу
        hint_surf = FONT_HINT.render("Press any key to exit", True, COLOR_HINT)
        hint_x = banner_x + (banner_width - hint_surf.get_width()) // 2
        hint_y = banner_y + banner_height - hint_surf.get_height() - 15
        win.blit(hint_surf, (hint_x, hint_y))

    except pygame.error as pg_err:
        print(f"[Помилка відмальовки екрана закінчення гри]: {pg_err}")


def main() -> None:
    """Run the Sudoku game loop."""
    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Sudoku")
    clock = pygame.time.Clock()

    board = Grid(GRID_SIZE, GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, win)
    key: int | None = None
    run = True
    start = monotonic()
    strikes = 0

    game_over = False
    game_won = False
    final_time = 0
    solving = False
    next_solve_step = 0.0

    while run:
        # Таймер оновлюється лише поки гра триває
        if not game_over and not game_won:
            play_time = round(monotonic() - start)
        else:
            play_time = final_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                continue

            if event.type == pygame.KEYDOWN:
                # Якщо гра завершена — будь-яка клавіша закриває гру
                if game_over or game_won:
                    run = False
                    break

                # Під час автоматичного розв'язання приймаємо лише системні події.
                if solving:
                    continue

                # Навігація стрілочками / WASD
                try:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        board.move_selection(dx=0, dy=-1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        board.move_selection(dx=0, dy=1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        board.move_selection(dx=-1, dy=0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        board.move_selection(dx=1, dy=0)
                except (TypeError, ValueError) as err:
                    print(f"Помилка навігації: {err}")

                # Введення цифр
                if event.key in KEY_MAPPING:
                    key = KEY_MAPPING[event.key]

                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None

                if event.key == pygame.K_SPACE:
                    board.start_solve_gui()
                    solving = True
                    next_solve_step = monotonic()
                    key = None

                if event.key == pygame.K_RETURN:
                    if board.selected:
                        row, col = board.selected
                        if board.cubes[row][col].temp != 0:
                            if board.place(board.cubes[row][col].temp):
                                print("Success")
                            else:
                                print("Wrong")
                                strikes += 1
                                # Перевірка ліміту помилок через check_game_over
                                if check_game_over(strikes, max_strikes=MAX_STRIKES):
                                    game_over = True
                                    final_time = round(monotonic() - start)
                            key = None

                            if board.is_finished() and not game_over:
                                game_won = True
                                final_time = round(monotonic() - start)

            if event.type == pygame.MOUSEBUTTONDOWN and not (game_over or game_won):
                if not solving:
                    pos = pygame.mouse.get_pos()
                    clicked = board.click(pos)
                    if clicked:
                        board.select(clicked[0], clicked[1])
                        key = None

        # Один крок backtracking виконується через таймер, а не через delay().
        if solving and monotonic() >= next_solve_step:
            result = board.solve_gui()
            next_solve_step = monotonic() + SOLVE_STEP_DELAY
            if result is not None:
                solving = False
                if result:
                    game_won = True
                else:
                    game_over = True
                final_time = round(monotonic() - start)

        if board.selected and key is not None and not (game_over or game_won or solving):
            board.sketch(key)

        # Малюємо сітку та поточний стан
        redraw_window(win, board, play_time, strikes)

        # Якщо настала поразка чи перемога — виводимо банер поверх
        if game_over:
            draw_end_screen(
                win, message="GAME OVER", color=COLOR_ERROR, play_time=play_time
            )
        elif game_won:
            draw_end_screen(
                win, message="VICTORY!", color=COLOR_SUCCESS, play_time=play_time
            )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()