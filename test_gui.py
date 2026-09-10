import os
import sys
from unittest.mock import MagicMock, patch
import pytest

# Запобігаємо відкриттю графічного вікна при запуску Pygame в CI/тестовому середовищі
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Безпечний імпорт GUI.py: запобігаємо автоматичному виклику main()
with patch("pygame.display.set_mode", MagicMock()), \
     patch("pygame.time.delay", MagicMock()), \
     patch("time.time", MagicMock(return_value=0)):
    # Підміняємо функцію main перед виконанням тіла скрипта при імпорті
    with patch.dict("sys.modules", {}):
        import GUI


# ==========================================
# FIXTURES (Набори тестових даних та моків)
# ==========================================

@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    """Ініціалізація Pygame у безголовому (headless) режимі для тестування."""
    import pygame
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture
def mock_window():
    """Фікстура для створення тестової поверхні pygame.Surface."""
    import pygame
    return pygame.Surface((540, 600))


@pytest.fixture
def sample_grid(mock_window):
    """Фікстура для створення екземпляра Grid із фіктивним вікном."""
    return GUI.Grid(rows=9, cols=9, width=540, height=540, win=mock_window)


@pytest.fixture
def sample_board():
    """Фікстура з тестовою матрицею 9x9 для перевірки валідності ходів."""
    return [
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


# ==========================================
# 6 ТЕСТОВИХ СЦЕНАРІЇВ
# ==========================================

# Сценарій 1: Нормальні та граничні значення check_game_over
@pytest.mark.parametrize("strikes, max_strikes, expected", [
    (0, 5, False),  # Початок гри (0 помилок)
    (4, 5, False),  # Граничне значення перед поразкою
    (5, 5, True),   # Граничне значення досягнення ліміту
    (6, 5, True),   # Перевищення ліміту
    (3, 3, True),   # Кастомний ліміт
])
def test_check_game_over_normal_and_boundary(strikes, max_strikes, expected):
    """Тестування звичайної поведінки та граничних меж check_game_over."""
    assert GUI.check_game_over(strikes, max_strikes) is expected


# Сценарій 2: Виняткові ситуації check_game_over (невалідні типи та від'ємні значення)
@pytest.mark.parametrize("invalid_strikes, invalid_max, expected_exc", [
    (True, 5, TypeError),      # bool замість int
    (3, "5", TypeError),       # рядок замість int
    (-1, 5, ValueError),       # від'ємна кількість помилок
    (2, 0, ValueError),        # нульовий ліміт max_strikes
    (2, -5, ValueError),       # від'ємний ліміт max_strikes
])
def test_check_game_over_exceptions(invalid_strikes, invalid_max, expected_exc):
    """Перевірка генерації винятків TypeError та ValueError для check_game_over."""
    with pytest.raises(expected_exc):
        GUI.check_game_over(invalid_strikes, invalid_max)


# Сценарій 3: Навігація move_selection — початковий стан та звичайний рух
def test_move_selection_normal_navigation(sample_grid):
    """Тестування переміщення курсору та початкової ініціалізації клітинки."""
    # Початковий стан: жодна клітинка не вибрана
    assert sample_grid.selected is None

    # Будь-який рух при None повинен ініціалізувати вибір на (0, 0)
    res = GUI.move_selection(sample_grid, dx=1, dy=0)
    assert res is True
    assert sample_grid.selected == (0, 0)

    # Звичайний рух вправо (0, 0) -> (0, 1)
    res = GUI.move_selection(sample_grid, dx=1, dy=0)
    assert res is True
    assert sample_grid.selected == (0, 1)

    # Звичайний рух вниз (0, 1) -> (1, 1)
    res = GUI.move_selection(sample_grid, dx=0, dy=1)
    assert res is True
    assert sample_grid.selected == (1, 1)


# Сценарій 4: Граничні умови move_selection (захист від виходу за межі поля)
def test_move_selection_boundary_clamping(sample_grid):
    """Перевірка блокування виходу за межі сітки [0, 8] x [0, 8]."""
    # Встановлюємо вибір у лівий верхній кут (0, 0)
    sample_grid.select(0, 0)

    # Спроба вийти вліво та вгору (за межі 0)
    res_left = GUI.move_selection(sample_grid, dx=-1, dy=0)
    assert res_left is False
    assert sample_grid.selected == (0, 0)

    res_up = GUI.move_selection(sample_grid, dx=0, dy=-1)
    assert res_up is False
    assert sample_grid.selected == (0, 0)

    # Встановлюємо вибір у правий нижній кут (8, 8)
    sample_grid.select(8, 8)

    # Спроба вийти вправо та вниз (за межі rows - 1, cols - 1)
    res_right = GUI.move_selection(sample_grid, dx=1, dy=0)
    assert res_right is False
    assert sample_grid.selected == (8, 8)

    res_down = GUI.move_selection(sample_grid, dx=0, dy=1)
    assert res_down is False
    assert sample_grid.selected == (8, 8)


# Сценарій 5: Виняткові ситуації move_selection та перевірка цілісності типів
def test_move_selection_exceptions(sample_grid):
    """Перевірка обробки некоректних типів даних у move_selection."""
    with pytest.raises(TypeError, match="Очікувався об'єкт Grid"):
        GUI.move_selection("not_a_grid", dx=1, dy=0)

    with pytest.raises(TypeError, match="Параметр dx повинен бути цілим числом"):
        GUI.move_selection(sample_grid, dx=True, dy=0)

    with pytest.raises(TypeError, match="Параметр dy повинен бути цілим числом"):
        GUI.move_selection(sample_grid, dx=0, dy="down")

    # Зламана сітка без параметрів rows/cols
    mock_invalid_grid = MagicMock(spec=GUI.Grid)
    mock_invalid_grid.rows = 0
    mock_invalid_grid.cols = 9
    with pytest.raises(ValueError, match="некоректні розміри"):
        GUI.move_selection(mock_invalid_grid, dx=1, dy=0)


# Сценарій 6: Валідація правил гри valid() та захист методу draw_end_screen()
def test_sudoku_rules_and_draw_end_screen_exceptions(sample_board, mock_window):
    """Тестування правил судоку (valid) та перевірка винятків у draw_end_screen."""
    # 1. Тестування функції valid (правила судоку)
    # Позиція (0, 2) на дошці є порожньою (значення 0)
    # 7 вже є у цьому рядку (позиція (0,0)), тому 7 ставити не можна
    assert GUI.valid(sample_board, 7, (0, 2)) is False

    # 3 немає ні в рядку 0, ні в колонці 2, ні в квадраті 3x3 -> валідний хід
    assert GUI.valid(sample_board, 3, (0, 2)) is True

    # 2. Тестування валідації параметрів у draw_end_screen
    with pytest.raises(TypeError, match="win має бути об'єктом pygame.Surface"):
        GUI.draw_end_screen("not_surface", "GAME OVER", (255, 0, 0))

    with pytest.raises(ValueError, match="Повідомлення message не може бути порожнім"):
        GUI.draw_end_screen(mock_window, "   ", (255, 0, 0))

    with pytest.raises(ValueError, match="Усі компоненти кольору мають бути цілими числами"):
        GUI.draw_end_screen(mock_window, "VICTORY!", (300, 0, 0))  # 300 > 255

    # Успішний виклик без помилок
    GUI.draw_end_screen(mock_window, "VICTORY!", (34, 139, 34), play_time=125)