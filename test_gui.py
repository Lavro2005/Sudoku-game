import time
from unittest.mock import MagicMock, patch

import pytest

# Імпортуємо функції та класи з GUI.py для тестування
import GUI


# Фікстура для створення тестової дошки
@pytest.fixture
def sample_board():
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

# Фікстура для створення повністю заповненої дошки
@pytest.fixture
def full_board():
    return [
        [7, 8, 5, 4, 3, 9, 1, 2, 6],
        [6, 1, 2, 8, 7, 5, 3, 4, 9],
        [4, 9, 3, 6, 2, 1, 5, 7, 8],
        [8, 5, 7, 9, 4, 3, 2, 6, 1],
        [2, 6, 1, 7, 5, 8, 9, 3, 4],
        [9, 3, 4, 1, 6, 2, 7, 8, 5],
        [5, 7, 8, 3, 9, 4, 6, 1, 2],
        [1, 2, 6, 5, 8, 7, 4, 9, 3],
        [3, 4, 9, 2, 1, 6, 8, 5, 7]
    ]

# Фікстура для мок-об'єкта сітки
@pytest.fixture
def mock_grid():
    grid = MagicMock()
    grid.rows = 9
    grid.cols = 9
    grid.selected = (4, 4)
    # Метод select просто оновлює вибрану клітинку
    def mock_select(row, col):
        grid.selected = (row, col)
    grid.select.side_effect = mock_select
    return grid

# 1. Тест форматування часу
def test_format_time():
    # Нормальні значення
    assert GUI.format_time(0) == " 0:0"
    assert GUI.format_time(59) == " 0:59"
    assert GUI.format_time(60) == " 1:0"
    assert GUI.format_time(3665) == " 61:5"  # В даній реалізації відображає лише хвилини та секунди

# 2. Тест для перевірки завершення гри за кількістю помилок
def test_check_game_over():
    # Нормальні та граничні значення
    assert GUI.check_game_over(0, 3) is False
    assert GUI.check_game_over(2, 3) is False
    assert GUI.check_game_over(3, 3) is True
    assert GUI.check_game_over(5, 3) is True
    
    # Виняткова ситуація (наприклад, передано невірний тип, але функція містить try-except)
    assert GUI.check_game_over("invalid", 3) is False

# 3. Тест функції пошуку порожньої клітинки
def test_find_empty(sample_board, full_board):
    # Дошка з порожніми місцями (повинна знайти перше порожнє місце - (0, 2))
    assert GUI.find_empty(sample_board) == (0, 2)
    # Повністю заповнена дошка (повинна повернути None)
    assert GUI.find_empty(full_board) is None

# 4. Тест валідації ходу
def test_valid(sample_board):
    # Валідний хід у порожню клітинку (0, 2)
    assert GUI.valid(sample_board, 5, (0, 2)) is True
    
    # Невалідний хід через конфлікт у рядку (спроба поставити 8, яке вже є в рядку 0)
    assert GUI.valid(sample_board, 8, (0, 2)) is False
    
    # Невалідний хід через конфлікт у колонці (спроба поставити 1, яке є у 7-му рядку, 2-й колонці)
    assert GUI.valid(sample_board, 1, (0, 2)) is False
    
    # Невалідний хід через конфлікт у блоці 3x3
    assert GUI.valid(sample_board, 7, (0, 2)) is False

# 5. Тест переміщення вибору (навігація стрілками)
def test_move_selection(mock_grid):
    # Нормальне переміщення вгору
    GUI.move_selection(mock_grid, 0, -1)
    assert mock_grid.selected == (3, 4)
    
    # Переміщення за межі сітки (вгору з рядка 0)
    mock_grid.selected = (0, 4)
    GUI.move_selection(mock_grid, 0, -1)
    assert mock_grid.selected == (0, 4) # Вибір не повинен змінитися
    
    # Переміщення за межі сітки (вправо з колонки 8)
    mock_grid.selected = (4, 8)
    GUI.move_selection(mock_grid, 1, 0)
    assert mock_grid.selected == (4, 8)
    
    # Виняткова ситуація: grid.selected дорівнює None
    mock_grid.selected = None
    GUI.move_selection(mock_grid, 1, 0)
    assert mock_grid.selected == (0, 0) # Повинно вибрати (0, 0)

# 6. Тест функції скидання гри (reset_game)
@patch('GUI.Grid') # Мокаємо Grid щоб не залежати від Pygame під час ініціалізації
def test_reset_game(mock_grid_class, sample_board):
    # Налаштовуємо мок для класу Grid
    mock_grid_instance = MagicMock()
    mock_grid_class.return_value = mock_grid_instance
    mock_grid_instance.rows = 9
    mock_grid_instance.cols = 9
    mock_grid_instance.cubes = [[MagicMock() for _ in range(9)] for _ in range(9)]
    
    mock_win = object()
    new_grid, start, strikes, game_over, victory = GUI.reset_game(sample_board, mock_win)
    
    # Перевірки
    assert new_grid is mock_grid_instance
    assert strikes == 0
    assert game_over is False
    assert victory is False
    # Переконуємось, що час був скинутий (start близьке до поточного часу)
    assert abs(time.time() - start) < 1.0 

