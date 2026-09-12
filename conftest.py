"""
conftest.py
-----------
GUI.py — це pygame-скрипт, який під час імпорту одразу викликає main()
(нескінченний ігровий цикл `while run:`). Щоб безпечно та без "зависань"
імпортувати модуль у headless-середовищі (без реального дисплея), тут
виконується наступне:

1. Встановлюється "фіктивний" відео/аудіо драйвер SDL (SDL_VIDEODRIVER=dummy),
   що дозволяє pygame.display.set_mode() працювати без реального екрана.
2. pygame.event.get() тимчасово підміняється так, щоб одразу повернути
   подію QUIT — тоді main() виконає рівно одну ітерацію циклу (проходячи
   при цьому майже весь код модуля: створення Grid/Cube, update_model,
   redraw_window, draw і т.д.) і коректно завершиться, а не зависне.

Це дає змогу imропоuvat GUI один раз на всю тестову сесію та отримати
доступ до всіх класів/функцій модуля (Grid, Cube, valid, find_empty,
format_time, move_selection, check_game_over, draw_end_screen) для
подальшого модульного тестування.
"""

import os
import sys
from unittest.mock import MagicMock

import pytest

# --- Headless-режим для pygame (без реального дисплея) ---
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session")
def gui_module():
    """
    Безпечно імпортує GUI.py один раз за сесію тестів і повертає модуль.
    """
    import pygame  # локальний імпорт, щоб змінні середовища встигли застосуватися

    quit_event = pygame.event.Event(pygame.QUIT)
    original_event_get = pygame.event.get

    # Одразу після старту головного циклу "надсилаємо" подію QUIT,
    # щоб main() не зациклився назавжди в headless-середовищі.
    pygame.event.get = MagicMock(return_value=[quit_event])

    try:
        import GUI
    finally:
        # Повертаємо оригінальну поведінку pygame.event.get для решти тестів
        pygame.event.get = original_event_get

    # GUI.py у кінці файлу викликає pygame.quit(), що деініціалізує
    # усі підсистеми pygame (у т.ч. шрифти). Повторно ініціалізуємо їх,
    # щоб функції на кшталт draw_end_screen(), які рендерять текст,
    # коректно працювали під час подальших тестів.
    pygame.font.init()
    pygame.display.init()
    pygame.display.set_mode((540, 600))

    return GUI


@pytest.fixture
def mock_win():
    """
    Мок-об'єкт вікна pygame: імітує поверхню з методами fill/blit/get_size,
    без потреби у реальному дисплеї. Використовується для тестів,
    де важлива лише коректна поведінка функцій малювання, а не піксельний
    результат.
    """
    win = MagicMock(name="MockWindow")
    win.get_size.return_value = (540, 600)
    return win


@pytest.fixture
def mock_grid():
    """
    Мок-об'єкт сітки Grid для ізольованого тестування move_selection()
    без залежності від реального Grid/Cube/pygame.
    """
    grid = MagicMock(name="MockGrid")
    grid.rows = 9
    grid.cols = 9
    grid.selected = (4, 4)
    return grid


@pytest.fixture
def solved_board():
    """Повністю заповнена (без нулів) коректна дошка 9x9 — граничний випадок."""
    return [
        [7, 8, 5, 4, 3, 9, 1, 2, 6],
        [6, 1, 2, 8, 7, 5, 3, 4, 9],
        [4, 9, 3, 6, 2, 1, 5, 7, 8],
        [8, 5, 7, 9, 4, 3, 2, 6, 1],
        [2, 6, 1, 7, 5, 8, 9, 3, 4],
        [9, 3, 4, 1, 6, 2, 7, 8, 5],
        [5, 7, 8, 3, 9, 4, 6, 1, 2],
        [1, 2, 6, 5, 8, 7, 4, 9, 3],
        [3, 4, 9, 2, 1, 6, 8, 5, 7],
    ]


@pytest.fixture
def board_with_one_empty_cell(solved_board):
    """Дошка, де рівно одна клітинка порожня — нормальний випадок для find_empty()."""
    board = [row[:] for row in solved_board]
    board[0][2] = 0
    return board
