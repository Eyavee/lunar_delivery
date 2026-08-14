import pygame
import math

# Размеры экрана
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800

# Размеры карты (увеличили левый отступ)
MAP_LEFT = 260  # было 220
MAP_TOP = 50
MAP_WIDTH = 1090  # было 1130 (скорректировано под новую ширину)
MAP_HEIGHT = 700
MAP_RIGHT = MAP_LEFT + MAP_WIDTH
MAP_BOTTOM = MAP_TOP + MAP_HEIGHT

# Цвета (без изменений)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
DARK_BLUE = (0, 50, 150)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
LUNAR_GRAY = (180, 180, 190)
CRATER_COLOR = (120, 120, 130)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

# Зоны риска на карте (сдвинуты с учётом нового MAP_LEFT)
RISK_ZONES = [
    (MAP_LEFT + 80, MAP_TOP + 80, 160, 120, 1.5),
    (MAP_LEFT + 780, MAP_TOP + 480, 200, 150, 2.0),
    (MAP_LEFT + 380, MAP_TOP + 580, 120, 120, 1.8),
]

# Параметры роверов (без изменений)
ROVER_TYPES = {
    "light": {"battery": 100, "capacity": 5, "speed": 1.5, "color": (100, 200, 100)},
    "medium": {"battery": 150, "capacity": 15, "speed": 1.0, "color": (100, 150, 255)},
    "heavy": {"battery": 200, "capacity": 30, "speed": 0.7, "color": (255, 180, 50)},
}

# Настройки анимации
ANIMATION_SPEED = 3
ROVER_SIZE = 40

# База в центре карты (пересчитано)
BASE_POSITION = (MAP_LEFT + MAP_WIDTH // 2, MAP_TOP + MAP_HEIGHT // 2)

# Позиции роверов вокруг базы
ROVER_POSITIONS = [
    (BASE_POSITION[0] - 80, BASE_POSITION[1] - 50),
    (BASE_POSITION[0] + 80, BASE_POSITION[1] - 50),
    (BASE_POSITION[0], BASE_POSITION[1] + 80),
]

# Цвета для лунохода (без изменений)
ROVER_BODY = (200, 200, 210)
ROVER_WHEEL = (50, 50, 50)
ROVER_ANTENNA = (255, 200, 50)
ROVER_LIGHT = (255, 255, 200)
ROVER_SHADOW = (80, 80, 80)
ROVER_DETAIL = (150, 150, 160)
SOLAR_PANEL = (50, 150, 255)

# Игровые параметры
MAX_DAYS = 10
STARTING_MONEY = 100

# Размеры меню (увеличено)
MENU_WIDTH = 240
MENU_LEFT = 10
MENU_TOP = 10
