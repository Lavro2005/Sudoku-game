"""Sudoku implemented with pygame.

The module is split into two layers:

* pure game-logic helpers (:func:`find_empty`, :func:`valid`,
  :func:`solve_board`) that operate on plain 2D lists of ints and have no
  pygame dependency, so they can be unit-tested in isolation;
* presentation classes (:class:`Cube`, :class:`Grid`) that render the board
  with pygame and forward user input to the model above.

Importing this module has no side effects (no window is opened, no game
loop is started) - run it as a script to actually play::

    python GUI.py
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field

import pygame

LOGGER = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
BOARD_SIZE = 9
BOX_SIZE = 3

WINDOW_WIDTH = 540
WINDOW_HEIGHT = 600
BOARD_WIDTH = 540
BOARD_HEIGHT = 540

FPS = 30
MAX_STRIKES = 5
ANIMATION_DELAY_MS = 100

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 200, 0)
COLOR_GRAY = (128, 128, 128)

FONT_NAME = "comicsans"
CELL_FONT_SIZE = 40
BANNER_FONT_SIZE = 60

THIN_LINE = 1
THICK_LINE = 4

# The starting puzzle. Treated as read-only: Grid always makes a defensive
# copy of it, so multiple Grid instances never share mutable state.
PUZZLE: list[list[int]] = [
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

# Maps both top-row and numpad digit keys to their numeric value, replacing
# 18 near-identical `if event.key == pygame.K_N: key = N` branches.
NUMBER_KEYS: dict[int, int] = {
    pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3,
    pygame.K_4: 4, pygame.K_5: 5, pygame.K_6: 6,
    pygame.K_7: 7, pygame.K_8: 8, pygame.K_9: 9,
    pygame.K_KP1: 1, pygame.K_KP2: 2, pygame.K_KP3: 3,
    pygame.K_KP4: 4, pygame.K_KP5: 5, pygame.K_KP6: 6,
    pygame.K_KP7: 7, pygame.K_KP8: 8, pygame.K_KP9: 9,
}

# Maps both arrow keys and WASD to a (dx, dy) move, so keyboard navigation
# can be handled by a single dict lookup instead of eight if-statements.
DIRECTION_KEYS: dict[int, tuple[int, int]] = {
    pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
}

_FONT_CACHE: dict[int, pygame.font.Font] = {}


def _get_font(size: int) -> pygame.font.Font:
    """Return a cached ``comicsans`` font of the given size.

    pygame.font.SysFont() is relatively expensive; the original code created
    a brand-new font object on every single cell redraw (81 times per
    frame). Caching by size means each size is only ever built once.
    """
    font = _FONT_CACHE.get(size)
    if font is None:
        font = pygame.font.SysFont(FONT_NAME, size)
        _FONT_CACHE[size] = font
    return font


# --------------------------------------------------------------------------
# Pure Sudoku logic (no pygame dependency)
# --------------------------------------------------------------------------
def find_empty(board: list[list[int]]) -> tuple[int, int] | None:
    """Return the (row, col) of the first empty (0) cell, or None if full."""
    for row_idx, row in enumerate(board):
        for col_idx, value in enumerate(row):
            if value == 0:
                return row_idx, col_idx
    return None


def valid(board: list[list[int]], num: int, pos: tuple[int, int]) -> bool:
    """Whether placing ``num`` at ``pos`` keeps the board Sudoku-valid.

    :raises ValueError: if ``pos`` is outside the 9x9 board.
    """
    row, col = pos
    if not 0 <= row < BOARD_SIZE or not 0 <= col < BOARD_SIZE:
        raise ValueError(f"Position {pos} is outside the {BOARD_SIZE}x{BOARD_SIZE} board")

    if any(board[row][c] == num and c != col for c in range(BOARD_SIZE)):
        return False
    if any(board[r][col] == num and r != row for r in range(BOARD_SIZE)):
        return False

    box_row, box_col = (row // BOX_SIZE) * BOX_SIZE, (col // BOX_SIZE) * BOX_SIZE
    for r in range(box_row, box_row + BOX_SIZE):
        for c in range(box_col, box_col + BOX_SIZE):
            if board[r][c] == num and (r, c) != pos:
                return False

    return True


def _solve_with_callback(
    board: list[list[int]],
    on_assign: Callable[[int, int, int, bool], None] | None = None,
) -> bool:
    """Backtracking Sudoku solver shared by :func:`solve_board` and the
    animated :meth:`Grid.solve_gui`, so the algorithm only exists once.

    :param board: mutable 9x9 board, solved in place.
    :param on_assign: optional ``(row, col, value, placed)`` callback fired
        whenever a candidate is placed or rolled back - used to animate the
        solver without duplicating its logic.
    """
    empty = find_empty(board)
    if empty is None:
        return True
    row, col = empty

    for candidate in range(1, BOARD_SIZE + 1):
        if valid(board, candidate, (row, col)):
            board[row][col] = candidate
            if on_assign is not None:
                on_assign(row, col, candidate, True)

            if _solve_with_callback(board, on_assign):
                return True

            board[row][col] = 0
            if on_assign is not None:
                on_assign(row, col, 0, False)

    return False


def solve_board(board: list[list[int]]) -> bool:
    """Solve ``board`` in place via backtracking. Returns True if solvable."""
    return _solve_with_callback(board)


# --------------------------------------------------------------------------
# Presentation layer
# --------------------------------------------------------------------------
class Cube:
    """A single Sudoku cell: its value, pencil mark, and selection state."""

    def __init__(self, value: int, row: int, col: int, width: int, height: int) -> None:
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, win: pygame.Surface) -> None:
        """Render the cell's value/pencil mark and its selection outline."""
        gap = self.width / BOARD_SIZE
        x_pos = self.col * gap
        y_pos = self.row * gap
        font = _get_font(CELL_FONT_SIZE)

        if self.temp != 0 and self.value == 0:
            text = font.render(str(self.temp), True, COLOR_GRAY)
            win.blit(text, (x_pos + 5, y_pos + 5))
        elif self.value != 0:
            text = font.render(str(self.value), True, COLOR_BLACK)
            win.blit(
                text,
                (
                    x_pos + gap / 2 - text.get_width() / 2,
                    y_pos + gap / 2 - text.get_height() / 2,
                ),
            )

        if self.selected:
            pygame.draw.rect(win, COLOR_RED, (x_pos, y_pos, gap, gap), 3)

    def draw_change(self, win: pygame.Surface, correct: bool = True) -> None:
        """Flash the cell green/red while the animated solver fills it in."""
        gap = self.width / BOARD_SIZE
        x_pos = self.col * gap
        y_pos = self.row * gap
        font = _get_font(CELL_FONT_SIZE)

        pygame.draw.rect(win, COLOR_WHITE, (x_pos, y_pos, gap, gap), 0)
        text = font.render(str(self.value), True, COLOR_BLACK)
        win.blit(
            text,
            (
                x_pos + gap / 2 - text.get_width() / 2,
                y_pos + gap / 2 - text.get_height() / 2,
            ),
        )
        outline_color = COLOR_GREEN if correct else COLOR_RED
        pygame.draw.rect(win, outline_color, (x_pos, y_pos, gap, gap), 3)

    def set_value(self, val: int) -> None:
        """Set the committed value of the cell."""
        self.value = val

    def set_temp(self, val: int) -> None:
        """Set the pencil-mark (draft) value of the cell."""
        self.temp = val


class Grid:  # pylint: disable=too-many-instance-attributes
    """The 9x9 Sudoku board: owns the cells, the model, and the rendering.

    ``too-many-instance-attributes`` is disabled deliberately: the eight
    attributes below (rows, cols, width, height, win, cubes, model,
    selected) are exactly the board's state - splitting them into a
    sub-object would not make the class easier to understand.
    """

    def __init__(
        self,
        rows: int,
        cols: int,
        size: tuple[int, int],
        win: pygame.Surface,
        puzzle: list[list[int]] | None = None,
    ) -> None:
        self.rows = rows
        self.cols = cols
        self.width, self.height = size
        self.win = win

        source_puzzle = puzzle if puzzle is not None else PUZZLE
        self.cubes = [
            [Cube(source_puzzle[i][j], i, j, self.width, self.height) for j in range(cols)]
            for i in range(rows)
        ]

        self.model: list[list[int]] = []
        self.update_model()
        self.selected: tuple[int, int] | None = None

    def update_model(self) -> None:
        """Rebuild the plain-list model from the current cell values."""
        self.model = [[cube.value for cube in row] for row in self.cubes]

    def place(self, val: int) -> bool:
        """Try to commit ``val`` into the selected cell.

        Only Sudoku-rule compliance is checked here. Re-running the full
        backtracking solver on every single move (as the original code did)
        is unnecessary - the starting puzzle is guaranteed solvable, so a
        rule-valid move can never make it unsolvable - and is far more
        expensive than a plain :func:`valid` check.
        """
        if self.selected is None:
            LOGGER.warning("place() called without a selected cell")
            return False

        row, col = self.selected
        if self.cubes[row][col].value != 0:
            return False

        self.cubes[row][col].set_value(val)
        self.update_model()

        if valid(self.model, val, (row, col)):
            return True

        self.cubes[row][col].set_value(0)
        self.cubes[row][col].set_temp(0)
        self.update_model()
        return False

    def sketch(self, val: int) -> None:
        """Set a pencil-mark on the selected cell, if one is selected."""
        if self.selected is None:
            return
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    def draw(self) -> None:
        """Draw the grid lines and every cell onto the window."""
        gap = self.width / self.rows
        for i in range(self.rows + 1):
            thickness = THICK_LINE if i % BOX_SIZE == 0 and i != 0 else THIN_LINE
            pygame.draw.line(self.win, COLOR_BLACK, (0, i * gap), (self.width, i * gap), thickness)
            pygame.draw.line(self.win, COLOR_BLACK, (i * gap, 0), (i * gap, self.height), thickness)

        for row in self.cubes:
            for cube in row:
                cube.draw(self.win)

    def select(self, row: int, col: int) -> None:
        """Select ``(row, col)``, clearing the highlight everywhere else."""
        for cube_row in self.cubes:
            for cube in cube_row:
                cube.selected = False
        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def clear(self) -> None:
        """Clear the pencil-mark of the selected empty cell, if any."""
        if self.selected is None:
            return
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    def click(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        """Translate a pixel position into a (row, col) cell, or None."""
        x_pos, y_pos = pos
        if not 0 <= x_pos < self.width or not 0 <= y_pos < self.height:
            return None
        gap = self.width / self.rows
        return int(y_pos // gap), int(x_pos // gap)

    def is_finished(self) -> bool:
        """Whether every cell currently holds a non-zero value."""
        return all(cube.value != 0 for row in self.cubes for cube in row)

    def solve(self) -> bool:
        """Check/solve the current model in place, without touching the UI."""
        return solve_board(self.model)

    def solve_gui(self) -> bool:
        """Animate the backtracking solver directly on the pygame window."""
        self.update_model()

        def _on_assign(row: int, col: int, value: int, placed: bool) -> None:
            self.cubes[row][col].set_value(value)
            self.cubes[row][col].draw_change(self.win, placed)
            self.update_model()
            pygame.display.update()
            pygame.time.delay(ANIMATION_DELAY_MS)

        return _solve_with_callback(self.model, on_assign=_on_assign)


# --------------------------------------------------------------------------
# Standalone UI helpers (keyboard navigation, end-of-game condition/banner)
# --------------------------------------------------------------------------
def move_selection(grid: Grid, dx: int, dy: int) -> bool:
    """Move the selected cell by ``(dx, dy)``, clamped to the board's bounds.

    Enables keyboard navigation (arrow keys / WASD) as an alternative to
    mouse clicks.

    :param grid: the :class:`Grid` whose selection should change.
    :param dx: horizontal offset: -1 (left), 0, or 1 (right).
    :param dy: vertical offset: -1 (up), 0, or 1 (down).
    :return: True if the selection changed successfully, False otherwise.
    """
    if grid is None:
        raise ValueError("Об'єкт grid не може бути None")

    if (
        isinstance(dx, bool)
        or isinstance(dy, bool)
        or not isinstance(dx, int)
        or not isinstance(dy, int)
    ):
        raise TypeError("Параметри dx та dy мають бути цілими числами")

    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        raise ValueError("dx та dy можуть приймати лише значення -1, 0 або 1")

    if not hasattr(grid, "rows") or not hasattr(grid, "cols"):
        raise AttributeError("Переданий об'єкт grid не має атрибутів rows/cols")

    try:
        if grid.selected is None:
            new_row, new_col = 0, 0
        else:
            row, col = grid.selected
            new_row = max(0, min(grid.rows - 1, row + dy))
            new_col = max(0, min(grid.cols - 1, col + dx))

        grid.select(new_row, new_col)
        return True

    except (TypeError, ValueError, IndexError) as error:
        LOGGER.warning("Не вдалося перемістити виділення: %s", error)
        return False


def check_game_over(strikes: int, max_strikes: int = MAX_STRIKES) -> bool:
    """Whether the number of mistakes has reached the allowed limit.

    :param strikes: the current number of mistakes made.
    :param max_strikes: the maximum number of mistakes allowed.
    :return: True once the limit is reached (the round should end).
    """
    if isinstance(strikes, bool) or not isinstance(strikes, int):
        raise TypeError("Параметр strikes має бути цілим числом")
    if strikes < 0:
        raise ValueError("Параметр strikes не може бути від'ємним")

    if isinstance(max_strikes, bool) or not isinstance(max_strikes, int):
        raise TypeError("Параметр max_strikes має бути цілим числом")
    if max_strikes <= 0:
        raise ValueError("Параметр max_strikes має бути додатним числом")

    return strikes >= max_strikes


def draw_end_screen(
    win: pygame.Surface,
    message: str,
    color: tuple[int, int, int],
    final_time: float | None = None,
) -> bool:
    """Draw a translucent banner with the end-of-game message and elapsed time.

    :param win: the pygame surface (window) to draw onto.
    :param message: the banner text, e.g. ``"VICTORY!"`` or ``"GAME OVER"``.
    :param color: the message's text color as an ``(R, G, B)`` tuple.
    :param final_time: the final elapsed time in seconds, if any.
    :return: True if the banner was drawn successfully, False otherwise.
    """
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
        isinstance(final_time, bool)
        or not isinstance(final_time, (int, float))
        or final_time < 0
    ):
        raise TypeError("Параметр final_time має бути невід'ємним числом (секунди) або None")

    try:
        width, height = win.get_size()
    except AttributeError as error:
        raise AttributeError("Об'єкт win має підтримувати метод get_size()") from error

    try:
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(200)
        overlay.fill(COLOR_WHITE)
        win.blit(overlay, (0, 0))

        title_font = _get_font(BANNER_FONT_SIZE)
        title_text = title_font.render(message, True, tuple(color))
        win.blit(
            title_text,
            (width / 2 - title_text.get_width() / 2, height / 2 - title_text.get_height()),
        )

        if final_time is not None:
            time_font = _get_font(CELL_FONT_SIZE)
            time_text = time_font.render(f"Time: {format_time(int(final_time))}", True, COLOR_BLACK)
            win.blit(
                time_text,
                (width / 2 - time_text.get_width() / 2, height / 2 + 10),
            )

        pygame.display.update()
        return True

    except pygame.error as error:
        LOGGER.error("Помилка pygame під час малювання екрана завершення гри: %s", error)
        return False


def redraw_window(win: pygame.Surface, board: Grid, elapsed_seconds: int, strikes: int) -> None:
    """Clear the window and redraw the timer, the strikes counter, and the board."""
    win.fill(COLOR_WHITE)
    font = _get_font(CELL_FONT_SIZE)

    time_text = font.render(f"Time: {format_time(elapsed_seconds)}", True, COLOR_BLACK)
    win.blit(time_text, (WINDOW_WIDTH - 160, BOARD_HEIGHT + 20))

    strikes_text = font.render("X " * strikes, True, COLOR_RED)
    win.blit(strikes_text, (20, BOARD_HEIGHT + 20))

    board.draw()


def format_time(total_seconds: float) -> str:
    """Format a duration in seconds as ``H:MM:SS`` (or ``M:SS`` under an hour).

    The original implementation computed ``hour`` but never used it and did
    not zero-pad minutes/seconds, producing ambiguous strings like ``" 1:5"``
    for both 1:05 and 1:50. This version fixes both issues.

    :raises TypeError: if ``total_seconds`` is not a real number.
    :raises ValueError: if ``total_seconds`` is negative.
    """
    if isinstance(total_seconds, bool) or not isinstance(total_seconds, (int, float)):
        raise TypeError("total_seconds має бути числом (секундами)")
    if total_seconds < 0:
        raise ValueError("total_seconds не може бути від'ємним")

    whole_seconds = int(total_seconds)
    hours, remainder = divmod(whole_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


# --------------------------------------------------------------------------
# Game state and the main loop
# --------------------------------------------------------------------------
@dataclass
class GameState:
    """Mutable state of a running game session, kept outside the render loop."""

    strikes: int = 0
    pending_key: int | None = None
    game_over: bool = False
    victory: bool = False
    frozen_time: int = 0
    end_message: str = ""
    end_color: tuple[int, int, int] = COLOR_BLACK
    start_time: float = field(default_factory=time.time)

    @property
    def finished(self) -> bool:
        """Whether the round has ended, by victory or by too many strikes."""
        return self.game_over or self.victory

    def elapsed_seconds(self) -> int:
        """Seconds since the round started; frozen once the round ends."""
        if self.finished:
            return self.frozen_time
        return round(time.time() - self.start_time)

    def end_game(self, *, victory: bool, elapsed: int) -> None:
        """Mark the round as finished and freeze the timer/banner."""
        self.frozen_time = elapsed
        if victory:
            self.victory = True
            self.end_message = "VICTORY!"
            self.end_color = COLOR_GREEN
        else:
            self.game_over = True
            self.end_message = "GAME OVER"
            self.end_color = COLOR_RED


def _try_auto_solve(board: Grid, state: GameState) -> None:
    """Run the animated solver and declare victory if it completes the board."""
    if board.solve_gui() and board.is_finished():
        state.end_game(victory=True, elapsed=state.elapsed_seconds())
        LOGGER.info("Board solved automatically")


def _try_place_pending_value(board: Grid, state: GameState) -> None:
    """Attempt to commit the sketched value of the selected cell."""
    if board.selected is None:
        return

    row, col = board.selected
    sketched = board.cubes[row][col].temp
    if sketched == 0:
        return

    if board.place(sketched):
        LOGGER.info("Correct value placed at (%d, %d)", row, col)
    else:
        LOGGER.info("Incorrect value at (%d, %d)", row, col)
        state.strikes += 1

    state.pending_key = None

    if check_game_over(state.strikes):
        state.end_game(victory=False, elapsed=state.elapsed_seconds())
        LOGGER.info("Game over: too many mistakes")
    elif board.is_finished():
        state.end_game(victory=True, elapsed=state.elapsed_seconds())
        LOGGER.info("Victory: board completed")


def handle_keydown(event: pygame.event.Event, board: Grid, state: GameState) -> None:
    """Handle a single KEYDOWN event, mutating ``board``/``state`` as needed."""
    if state.finished:
        return  # Ignore gameplay input once the round has ended.

    if event.key in NUMBER_KEYS:
        state.pending_key = NUMBER_KEYS[event.key]
        return

    if event.key in DIRECTION_KEYS:
        dx, dy = DIRECTION_KEYS[event.key]
        move_selection(board, dx, dy)
        return

    if event.key == pygame.K_DELETE:
        board.clear()
        state.pending_key = None
    elif event.key == pygame.K_SPACE:
        _try_auto_solve(board, state)
    elif event.key == pygame.K_RETURN:
        _try_place_pending_value(board, state)


def handle_mouse_click(pos: tuple[int, int], board: Grid, state: GameState) -> None:
    """Select the clicked cell, unless the round has already ended."""
    if state.finished:
        return
    clicked = board.click(pos)
    if clicked is not None:
        board.select(*clicked)
        state.pending_key = None


def main() -> None:
    """Initialise pygame and run the Sudoku game loop until the window closes."""
    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Sudoku")

    board = Grid(BOARD_SIZE, BOARD_SIZE, (BOARD_WIDTH, BOARD_HEIGHT), win)
    state = GameState()
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                handle_keydown(event, board, state)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_click(pygame.mouse.get_pos(), board, state)

        if board.selected and state.pending_key is not None:
            board.sketch(state.pending_key)

        redraw_window(win, board, state.elapsed_seconds(), state.strikes)
        if state.finished:
            draw_end_screen(win, state.end_message, state.end_color, final_time=state.frozen_time)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()