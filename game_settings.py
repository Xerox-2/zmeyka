import os

# Настройки игрового поля
FIELD_SIZE = 30  # Размер поля 30x30
CELL_SIZE = 10   # Размер клетки в пикселях
WIDTH = FIELD_SIZE * CELL_SIZE  # 300
HEIGHT = FIELD_SIZE * CELL_SIZE  # 300

# Цвета
COLORS = {
    'background': 'black',
    'snake': 'white',
    'apple': 'red',
    'wall': 'purple',
    'wall_outline': 'darkviolet',
    'text': 'white',
    'game_over': 'red',
    'restart_text': 'yellow'
}

# Настройки игры
INITIAL_SNAKE = [[14, 14]]  # Начальная позиция змейки
INITIAL_DIRECTION = "Right"  # Начальное направление
APPLES_COUNT = 5  # Количество яблок на поле
GAME_SPEED = 100  # Скорость игры (мс)

# Путь к базе данных (создаем в папке с игрой)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(CURRENT_DIR, "snake_scores.db")

# Управление
KEYS = {
    'Up': (0, -1),
    'Down': (0, 1),
    'Left': (-1, 0),
    'Right': (1, 0)
}

WASD = {
    'w': 'Up',
    's': 'Down',
    'a': 'Left',
    'd': 'Right'
}