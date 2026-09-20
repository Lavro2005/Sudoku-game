"""Unit-тести для графічної логіки Sudoku."""

import os

import pytest

# Вмикає headless-режим, щоб тести не вимагали графічного дисплея.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()


# Імпортує GUI.py без запуску гри завдяки захисту main-модуля.
from GUI import (
    Grid,
    check_game_over,
    draw_end_screen,
    find_empty,
    format_time,
    move_selection,
    reset_game,
    valid,
)


@pytest.fixture
def board_template():
    """Повертає незалежну копію початкової дошки Sudoku."""
    return [row[:] for row in Grid.board]


@pytest.fixture
def pygame_window():
    """Створює тестову поверхню Pygame без відкриття реального вікна."""
    return pygame.Surface((540, 600))


@pytest.fixture
def grid(board_template, pygame_window):
    """Створює тестову ігрову сітку з початковим шаблоном."""
    return Grid(9, 9, 540, 540, pygame_window, board_template)


# Перевіряє пошук першої порожньої клітинки та випадок заповненої дошки.
def test_find_empty_returns_first_empty_or_none():
    assert find_empty([[1, 2], [3, 0]]) == (1, 1)
    assert find_empty([[1, 2], [3, 4]]) is None


# Перевіряє коректні та конфліктні значення Sudoku.
def test_valid_checks_row_column_and_box(board_template):
    assert valid(board_template, 3, (0, 2)) is True
    assert valid(board_template, 7, (0, 2)) is False
    assert valid(board_template, 6, (0, 2)) is False
    assert valid(board_template, 8, (0, 2)) is False


# Перевіряє навігацію та обмеження вибору межами дошки.
def test_move_selection_clamps_to_grid_edges(grid):
    assert move_selection(grid, 1, 0) == (0, 1)
    assert move_selection(grid, -10, -10) == (0, 0)
    assert move_selection(grid, 10, 10) == (8, 8)


# Перевіряє порогове значення та відхилення некоректних аргументів.
def test_check_game_over_handles_limit_and_invalid_values():
    assert check_game_over(2) is False
    assert check_game_over(3) is True
    assert check_game_over(5, max_strikes=5) is True
    with pytest.raises(ValueError):
        check_game_over(-1)
    with pytest.raises(ValueError):
        check_game_over(1, max_strikes=0)


# Перевіряє валідацію параметрів конструктора Grid.
def test_grid_rejects_invalid_dimensions(pygame_window, board_template):
    with pytest.raises(ValueError):
        Grid(0, 9, 540, 540, pygame_window, board_template)
    with pytest.raises(ValueError):
        Grid(9, 9, 540, 540, pygame_window, [[0]])


# Перевіряє тимчасове число, вибір і очищення клітинки.
def test_grid_sketch_select_and_clear(grid):
    grid.select(0, 2)
    grid.sketch(5)
    assert grid.cubes[0][2].temp == 5
    grid.clear()
    assert grid.cubes[0][2].temp == 0
    assert grid.cubes[0][2].selected is True


# Перевіряє прийняття правильного числа та відхилення неправильного.
def test_grid_place_accepts_valid_and_rejects_invalid_values(grid):
    grid.select(0, 2)
    assert grid.place(5) is True
    assert grid.cubes[0][2].value == 5

    grid.select(0, 4)
    assert grid.place(5) is False
    assert grid.cubes[0][4].value == 0


# Перевіряє створення нового стану гри та скидання лічильників.
def test_reset_game_returns_fresh_state(board_template, pygame_window):
    board, start, strikes, victory, game_over = reset_game(
        board_template, pygame_window
    )
    assert isinstance(board, Grid)
    assert start > 0
    assert strikes == 0
    assert victory is False
    assert game_over is False
    assert board.cubes[0][0].value == board_template[0][0]


# Перевіряє помилки функції рестарту для порожнього шаблону та відсутнього вікна.
def test_reset_game_rejects_invalid_input():
    with pytest.raises(ValueError):
        reset_game([])
    pygame.display.quit()
    with pytest.raises(RuntimeError):
        reset_game([[0] * 9 for _ in range(9)])
    pygame.display.init()


# Перевіряє малювання фінального екрана та його валідацію.
def test_draw_end_screen_draws_overlay(pygame_window):
    draw_end_screen(
        pygame_window, "VICTORY!\nЧас: 1:20\nНатисніть R для рестарту", (0, 180, 0)
    )
    assert pygame_window.get_at((0, 0))[:3] == (0, 0, 0)
    with pytest.raises(ValueError):
        draw_end_screen(pygame_window, "", (0, 0, 0))
    with pytest.raises(TypeError):
        draw_end_screen(None, "GAME OVER", (220, 0, 0))


# Перевіряє форматування часу для секунд і хвилин.
def test_format_time_formats_seconds_and_minutes():
    assert format_time(5) == " 0:5"
    assert format_time(65) == " 1:5"
