# test_gui.py
"""
Комплект Unit-тестів для GUI.py (Sudoku на pygame).

6 тестових сценаріїв:
    1. test_valid_detects_row_column_and_box_conflicts   - normal + boundary
    2. test_find_empty_normal_and_boundary_cases          - normal + boundary
    3. test_format_time_boundary_values                   - boundary
    4. test_check_game_over_normal_boundary_and_exceptions- normal + boundary + exception
    5. test_move_selection_normal_boundary_and_exceptions - normal + boundary + exception
    6. test_draw_end_screen_normal_and_exceptions          - normal + exception

Дані для тестів формуються через fixtures (conftest.py) та mock-об'єкти
(unittest.mock.MagicMock) там, де реальні pygame-об'єкти не потрібні.
"""

import pytest


# ---------------------------------------------------------------------------
# 1. valid() — перевірка правил судоку (рядок / стовпець / блок 3x3)
# ---------------------------------------------------------------------------
def test_valid_detects_row_column_and_box_conflicts(gui_module, solved_board):
    """
    Normal:   число, якого немає в рядку/стовпці/блоці — валідне.
    Boundary: конфлікт рівно на межі блоку 3x3 (кутові клітинки board[2][2]/[0][0]),
              а також випадок "число вже стоїть у цій самій позиції" (не конфлікт).
    """
    board = [row[:] for row in solved_board]

    # Normal case: підставляємо порожню клітинку (0,2)=5, замінюємо на unique num
    board[0][2] = 0
    assert gui_module.valid(board, 5, (0, 2)) is True

    # Boundary case: конфлікт по рядку
    assert gui_module.valid(board, 8, (0, 2)) is False  # 8 вже є в рядку 0

    # Boundary case: конфлікт по стовпцю
    assert gui_module.valid(board, 4, (0, 2)) is False  # 4 вже є у стовпці 2

    # Boundary case: конфлікт у блоці 3x3 (кутова клітинка блоку)
    assert gui_module.valid(board, 3, (0, 2)) is False  # 3 вже є у верхньому лівому блоці

    # Boundary case: значення стоїть саме у поточній позиції — конфліктом не вважається
    board[0][2] = 5
    assert gui_module.valid(board, 5, (0, 2)) is True


# ---------------------------------------------------------------------------
# 2. find_empty() — пошук першої порожньої клітинки
# ---------------------------------------------------------------------------
def test_find_empty_normal_and_boundary_cases(gui_module, board_with_one_empty_cell, solved_board):
    """
    Normal:   на дошці є одна порожня клітинка — має бути знайдена коректно.
    Boundary: повністю заповнена дошка (без нулів) — має повертати None.
    """
    # Normal case
    assert gui_module.find_empty(board_with_one_empty_cell) == (0, 2)

    # Boundary case: дошка без жодного нуля
    assert gui_module.find_empty(solved_board) is None


# ---------------------------------------------------------------------------
# 3. format_time() — форматування часу гри
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0, " 0:0"),      # boundary: нульовий час
        (59, " 0:59"),    # boundary: межа однієї хвилини
        (60, " 1:0"),     # boundary: рівно одна хвилина
        (3661, " 61:1"),  # normal: понад годину
    ],
)
def test_format_time_boundary_values(gui_module, seconds, expected):
    assert gui_module.format_time(seconds) == expected


# ---------------------------------------------------------------------------
# 4. check_game_over() — умова завершення гри за кількістю помилок
# ---------------------------------------------------------------------------
def test_check_game_over_normal_boundary_and_exceptions(gui_module):
    """
    Normal:    кількість помилок менша за ліміт -> False.
    Boundary:  кількість помилок точно дорівнює ліміту -> True.
    Exception: некоректні типи/значення параметрів -> TypeError / ValueError.
    """
    # Normal case
    assert gui_module.check_game_over(strikes=2, max_strikes=5) is False

    # Boundary case: точно на межі ліміту
    assert gui_module.check_game_over(strikes=5, max_strikes=5) is True

    # Exception: strikes не є цілим числом
    with pytest.raises(TypeError):
        gui_module.check_game_over(strikes="3", max_strikes=5)

    # Exception: strikes від'ємне
    with pytest.raises(ValueError):
        gui_module.check_game_over(strikes=-1, max_strikes=5)

    # Exception: max_strikes <= 0
    with pytest.raises(ValueError):
        gui_module.check_game_over(strikes=1, max_strikes=0)


# ---------------------------------------------------------------------------
# 5. move_selection() — навігація по сітці клавіатурою (тест на mock Grid)
# ---------------------------------------------------------------------------
def test_move_selection_normal_boundary_and_exceptions(gui_module, mock_grid):
    """
    Normal:    переміщення виділення в межах поля.
    Boundary:  спроба вийти за межу поля (координата "затискається" в діапазоні 0..8).
    Exception: некоректні dx/dy та відсутній об'єкт grid.
    """
    # Normal case: рух вправо-вниз від клітинки (4, 4)
    mock_grid.selected = (4, 4)
    result = gui_module.move_selection(mock_grid, dx=1, dy=1)
    assert result is True
    mock_grid.select.assert_called_once_with(5, 5)

    # Boundary case: клітинка на верхній лівій межі, рух вгору-вліво не повинен
    # вивести координати за межі 0..8
    mock_grid.reset_mock()
    mock_grid.selected = (0, 0)
    gui_module.move_selection(mock_grid, dx=-1, dy=-1)
    mock_grid.select.assert_called_once_with(0, 0)

    # Exception case: неприпустиме значення dx (поза діапазоном -1..1)
    with pytest.raises(ValueError):
        gui_module.move_selection(mock_grid, dx=5, dy=0)

    # Exception case: dx/dy не є цілими числами
    with pytest.raises(TypeError):
        gui_module.move_selection(mock_grid, dx="1", dy=0)

    # Exception case: grid дорівнює None
    with pytest.raises(ValueError):
        gui_module.move_selection(None, dx=0, dy=1)


# ---------------------------------------------------------------------------
# 6. draw_end_screen() — банер завершення гри (тест на mock-вікні pygame)
# ---------------------------------------------------------------------------
def test_draw_end_screen_normal_and_exceptions(gui_module, mock_win):
    """
    Normal:    коректні вхідні дані -> банер малюється, повертається True,
               викликаються очікувані методи mock-вікна (fill/blit).
    Exception: некоректні message/color/win -> ValueError / AttributeError.
    """
    # Normal case
    result = gui_module.draw_end_screen(mock_win, "GAME OVER", (255, 0, 0), final_time=125)
    assert result is True
    assert mock_win.blit.call_count >= 2  # текст банера + текст часу

    # Exception case: порожній рядок повідомлення
    with pytest.raises(ValueError):
        gui_module.draw_end_screen(mock_win, "", (255, 0, 0))

    # Exception case: некоректний формат кольору (лише 2 канали замість 3)
    with pytest.raises(ValueError):
        gui_module.draw_end_screen(mock_win, "VICTORY!", (255, 0))

    # Exception case: win без методу get_size()
    class WindowWithoutGetSize:
        """Об'єкт, що імітує вікно без обов'язкового методу get_size()."""

    with pytest.raises(AttributeError):
        gui_module.draw_end_screen(WindowWithoutGetSize(), "VICTORY!", (0, 255, 0))

    # Exception case: win дорівнює None
    with pytest.raises(ValueError):
        gui_module.draw_end_screen(None, "VICTORY!", (0, 255, 0))
