# Test Results

## Date: 2026-09-19 18:25:43

`	ext
﻿============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\olehl\AppData\Local\Programs\Python\Python313\python.exe
cachedir: .pytest_cache
rootdir: C:\─юъєьхэЄш(ыюъры№э│)\Visual Studio Code projects(ыюъры№э│)\Sudoku-game
plugins: cov-7.1.0
collecting ... collected 6 items

test_gui.py::test_format_time PASSED                                     [ 16%]
test_gui.py::test_check_game_over PASSED                                 [ 33%]
test_gui.py::test_find_empty PASSED                                      [ 50%]
test_gui.py::test_valid PASSED                                           [ 66%]
test_gui.py::test_move_selection PASSED                                  [ 83%]
test_gui.py::test_reset_game PASSED                                      [100%]

=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.13.7-final-0 _______________

Name     Stmts   Miss  Cover
----------------------------
GUI.py     326    243    25%
----------------------------
TOTAL      326    243    25%
============================== 6 passed in 0.38s ==============================

`


## Ruff Code Quality Analysis

`	ext
RUF012 Mutable default value for class attribute
  --> GUI.py:10:13
   |
 9 |   class Grid:
10 |       board = [
   |  _____________^
11 | |         [7, 8, 0, 4, 0, 0, 1, 2, 0],
12 | |         [6, 0, 0, 0, 7, 5, 0, 0, 9],
13 | |         [0, 0, 0, 6, 0, 1, 0, 7, 8],
14 | |         [0, 0, 7, 0, 4, 0, 2, 6, 0],
15 | |         [0, 0, 1, 0, 5, 0, 9, 3, 0],
16 | |         [9, 0, 4, 0, 6, 0, 0, 0, 5],
17 | |         [0, 7, 0, 3, 0, 0, 0, 1, 2],
18 | |         [1, 2, 0, 0, 0, 7, 4, 0, 0],
19 | |         [0, 4, 9, 2, 0, 6, 0, 0, 7]
20 | |     ]
   | |_____^
21 |
22 |       # Р†РЅС–С†С–Р°Р»С–Р·Р°С†С–СЏ СЃС–С‚РєРё
   |
help: Consider initializing in `__init__` or annotating with `typing.ClassVar`

SIM201 Use `self.value != 0` instead of `not self.value == 0`
   --> GUI.py:197:14
    |
195 |             text = fnt.render(str(self.temp), 1, (128,128,128))
196 |             win.blit(text, (x+5, y+5))
197 |         elif not(self.value == 0):
    |              ^^^^^^^^^^^^^^^^^^^^
198 |             text = fnt.render(str(self.value), 1, (0, 0, 0))
199 |             win.blit(text, (x + (gap/2 - text.get_width()/2), y + (gap/2 - text.get_height()/2)))
    |
help: Replace with `!=` operator

F841 Local variable `hour` is assigned to but never used
   --> GUI.py:285:5
    |
283 |     sec = secs%60
284 |     minute = secs//60
285 |     hour = minute//60
    |     ^^^^
286 |
287 |     mat = " " + str(minute) + ":" + str(sec)
    |
help: Remove assignment to unused variable `hour`

BLE001 Do not catch blind exception: `Exception`
   --> GUI.py:304:12
    |
302 |         if 0 <= new_row < grid.rows and 0 <= new_col < grid.cols:
303 |             grid.select(new_row, new_col)
304 |     except Exception as e:
    |            ^^^^^^^^^
305 |         print(f"РџРѕРјРёР»РєР° РїС–Рґ С‡Р°СЃ РїРµСЂРµРјС–С‰РµРЅРЅСЏ РІРёР±РѕСЂСѓ: {e}")
    |

BLE001 Do not catch blind exception: `Exception`
   --> GUI.py:311:12
    |
309 |     try:
310 |         return strikes >= max_strikes
311 |     except Exception as e:
    |            ^^^^^^^^^
312 |         print(f"РџРѕРјРёР»РєР° РїС–Рґ С‡Р°СЃ РїРµСЂРµРІС–СЂРєРё РєС–Р»СЊРєРѕСЃС‚С– РїРѕРјРёР»РѕРє: {e}")
313 |         return False
    |

BLE001 Do not catch blind exception: `Exception`
   --> GUI.py:335:12
    |
334 |         pygame.display.update()
335 |     except Exception as e:
    |            ^^^^^^^^^
336 |         print(f"РџРѕРјРёР»РєР° РїС–Рґ С‡Р°СЃ РјР°Р»СЋРІР°РЅРЅСЏ РµРєСЂР°РЅСѓ Р·Р°РІРµСЂС€РµРЅРЅСЏ: {e}")
    |

BLE001 Do not catch blind exception: `Exception`
   --> GUI.py:358:12
    |
357 |         return new_grid, start, strikes, game_over, victory
358 |     except Exception as e:
    |            ^^^^^^^^^
359 |         print(f"РџРѕРјРёР»РєР° РїС–Рґ С‡Р°СЃ СЃРєРёРґР°РЅРЅСЏ РіСЂРё: {e}")
360 |         import time
    |

SIM102 Use a single `if` statement instead of nested `if` statements
   --> GUI.py:437:21
    |
435 |                           key = None
436 |
437 | /                     if event.key == pygame.K_RETURN:
438 | |                         if board.selected:
    | |__________________________________________^
439 |                               i, j = board.selected
440 |                               if board.cubes[i][j].temp != 0:
    |
help: Combine `if` statements using `and`

BLE001 Do not catch blind exception: `Exception`
   --> GUI.py:475:12
    |
473 |                     draw_end_screen(win, "GAME OVER", (200, 0, 0), final_time)
474 |
475 |     except Exception as e:
    |            ^^^^^^^^^
476 |         print(f"РљСЂРёС‚РёС‡РЅР° РїРѕРјРёР»РєР° Сѓ РіРѕР»РѕРІРЅРѕРјСѓ С†РёРєР»С–: {e}")
    |

I001 [*] Import block is un-sorted or un-formatted
 --> append_ruff.py:1:1
  |
1 | / import subprocess
2 | | import io
  | |_________^
3 |
4 |   try:
  |
help: Organize imports
  |
  - п»їimport subprocess
  - import io
1 + п»їimport io
2 + import subprocess
3 |
  |

PLW1510 `subprocess.run` without explicit `check` argument
 --> append_ruff.py:5:14
  |
4 | try:
5 |     result = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)
  |              ^^^^^^^^^^^^^^
6 |     output = result.stdout + result.stderr
7 | except Exception as e:
  |
help: Add explicit `check=False`

BLE001 Do not catch blind exception: `Exception`
 --> append_ruff.py:7:8
  |
5 |     result = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)
6 |     output = result.stdout + result.stderr
7 | except Exception as e:
  |        ^^^^^^^^^
8 |     output = str(e)
  |

UP020 [*] Use builtin `open`
  --> append_ruff.py:12:6
   |
10 | content = f"\n\n## Ruff Code Quality Analysis\n\n`    ext\n{output}\n`\n"
11 |
12 | with io.open("TEST_RESULTS.md", "a", encoding="utf-8") as f:
   |      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
13 |     f.write(content)
   |
help: Replace with builtin `open`
   |
11 |
   - with io.open("TEST_RESULTS.md", "a", encoding="utf-8") as f:
12 + with open("TEST_RESULTS.md", "a", encoding="utf-8") as f:
13 |     f.write(content)
   |

Found 13 errors.
[*] 2 fixable with the `--fix` option (2 hidden fixes can be enabled with the `--unsafe-fixes` option).

`


## Test Results after Refactoring

### Date: 2026-09-19 18:58:39

`	ext
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\olehl\AppData\Local\Programs\Python\Python313\python.exe
cachedir: .pytest_cache
rootdir: C:\Документи(локальні)\Visual Studio Code projects(локальні)\Sudoku-game
plugins: cov-7.1.0
collecting ... collected 6 items

test_gui.py::test_format_time PASSED                                     [ 16%]
test_gui.py::test_check_game_over PASSED                                 [ 33%]
test_gui.py::test_find_empty PASSED                                      [ 50%]
test_gui.py::test_valid PASSED                                           [ 66%]
test_gui.py::test_move_selection PASSED                                  [ 83%]
test_gui.py::test_reset_game PASSED                                      [100%]

=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.13.7-final-0 _______________

Name     Stmts   Miss  Cover
----------------------------
GUI.py     323    240    26%
----------------------------
TOTAL      323    240    26%
============================== 6 passed in 0.37s ==============================

`


## Ruff Analysis after Refactoring

`	ext
I001 [*] Import block is un-sorted or un-formatted
 --> append_ruff_2.py:1:1
  |
1 | / import subprocess
2 | | import io
  | |_________^
3 |
4 |   try:
  |
help: Organize imports
  |
  - п»їimport subprocess
  - import io
1 + п»їimport io
2 + import subprocess
3 |
  |

PLW1510 `subprocess.run` without explicit `check` argument
 --> append_ruff_2.py:5:14
  |
4 | try:
5 |     result = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)
  |              ^^^^^^^^^^^^^^
6 |     output = result.stdout + result.stderr
7 | except Exception as e:
  |
help: Add explicit `check=False`

BLE001 Do not catch blind exception: `Exception`
 --> append_ruff_2.py:7:8
  |
5 |     result = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)
6 |     output = result.stdout + result.stderr
7 | except Exception as e:
  |        ^^^^^^^^^
8 |     output = str(e)
  |

UP020 [*] Use builtin `open`
  --> append_ruff_2.py:12:6
   |
10 | content = f"\n\n## Ruff Analysis after Refactoring\n\n`    ext\n{output}\n`\n"
11 |
12 | with io.open("TEST_RESULTS.md", "a", encoding="utf-8") as f:
   |      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
13 |     f.write(content)
   |
help: Replace with builtin `open`
   |
11 |
   - with io.open("TEST_RESULTS.md", "a", encoding="utf-8") as f:
12 + with open("TEST_RESULTS.md", "a", encoding="utf-8") as f:
13 |     f.write(content)
   |

I001 [*] Import block is un-sorted or un-formatted
 --> append_tests.py:1:1
  |
1 | / import subprocess
2 | | import io
3 | | import datetime
  | |_______________^
4 |
5 |   now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  |
help: Organize imports
  |
  - п»їimport subprocess
1 + п»їimport datetime
2 | import io
  - import datetime
3 + import subprocess
4 |
  |

DTZ005 `datetime.datetime.now()` called without a `tz` argument
 --> append_tests.py:5:7
  |
3 | import datetime
4 |
5 | now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  |       ^^^^^^^^^^^^^^^^^^^^^^^
6 |
7 | try:
  |
help: Pass a `datetime.timezone` object to the `tz` parameter

PLW1510 `subprocess.run` without explicit `check` argument
  --> append_tests.py:8:14
   |
 7 | try:
 8 |     result = subprocess.run(["pytest", "--cov=GUI", "test_gui.py", "-v", "--tb=short"], capture_output=True, text=True)
   |              ^^^^^^^^^^^^^^
 9 |     output = result.stdout + result.stderr
10 | except Exception as e:
   |
help: Add explicit `check=False`

BLE001 Do not catch blind exception: `Exception`
  --> append_tests.py:10:8
   |
 8 |     result = subprocess.run(["pytest", "--cov=GUI", "test_gui.py", "-v", "--tb=short"], capture_output=True, text=True)
 9 |     output = result.stdout + result.stderr
10 | except Exception as e:
   |        ^^^^^^^^^
11 |     output = str(e)
   |

UP020 [*] Use builtin `open`
  --> append_tests.py:15:6
   |
13 | content = f"\n\n## Test Results after Refactoring\n\n### Date: {now}\n\n`    ext\n{output}\n`\n"
14 |
15 | with io.open("TEST_RESULTS.md", "a", encoding="utf-8") as f:
   |      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
16 |     f.write(content)
   |
help: Replace with builtin `open`
   |
14 |
   - with io.open("TEST_RESULTS.md", "a", encoding="utf-8") as f:
15 + with open("TEST_RESULTS.md", "a", encoding="utf-8") as f:
16 |     f.write(content)
   |

Found 9 errors.
[*] 4 fixable with the `--fix` option.

`
