# Размеры экрана
from enum import Enum
WIDTH = 1480
HEIGHT = 920
FPS = 25

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Цвета-заглушки для текстур (для будущих спрайтов)
TEX_GRASS = (144, 238, 144)      # трава (фон)
TEX_DIRT_PATH = (139, 119, 101)  # земляная дорога
TEX_WOOD_WALL = (101, 67, 33)    # деревянные стены
TEX_ROOF = (139, 69, 19)         # крыша
TEX_TREE = (34, 139, 34)         # дерево
TEX_STONE = (105, 105, 105)      # камень
TEX_DOOR = (0, 0, 0)             # дверь (черный)
TEX_BUSH = (0, 100, 0)           # куст

# Цвета для леса
FOREST_BG = (34, 139, 34)  # Темно-зеленый фон
TEX_FOREST_GROUND = (34, 139, 34)  # Лесная земля
TEX_FOREST_PATH = (101, 67, 33)  # Лесная тропинка

# Игрок
PLAYER_SPEED = 5
PLAYER_SIZE = 64

# Диалоги
DIALOG_BOX_HEIGHT = 180
DIALOG_PADDING = 20
DIALOG_FONT_SIZE = 24
DIALOG_TEXT_SPEED = 0.05  # секунды на символ

# PLAYER_SIZE = 40  # Остаётся неизменным
PLAYER_SPEED = 5  # Можно чуть увеличить
PLAYER_SPRINT_MULTIPLIER = 1.8  # Множитель скорости спринта
MAP_SCALE = 2     # Карта в 2 раза больше

LAYER_RENDER_ORDER = {
    'background': ['Bach', 'Back', 'Вода', 'Земля', 'Дорожка', 'растения'],
    'middle_below': ['Цветочный', 'Кристаллы', 'Слой тайлов 18'],  # Убрал Забор отсюда
    'player': None,  # Игрок рисуется здесь
    'middle_above': ['Middle', 'Деревья', 'Ворота', 'Слой тайлов 9', 'Слой тайлов 23'],
    'foreground': ['Front', 'Слой тайлов 24', 'Забор']  # Добавил Забор сюда
}

# LAYER_RENDER_ORDER = {
#     'background': ['Background', 'Ground', 'Terrain'],
#     'middle_below': ['Paths', 'Decorations_Below'],
#     'middle_above': ['Objects', 'Decorations_Above', 'Trees_Lower'],
#     'foreground': ['Foreground', 'Trees_Upper', 'Effects']
# }