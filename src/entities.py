import pygame
from settings import *

class Entity:
    """Базовый класс для всех объектов на карте"""
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_collision_rect(self):
        """Зона коллизии (может отличаться от визуальной)"""
        return self.get_rect()
    
    def draw(self, screen, camera):
        rect = camera.apply_rect(self.get_rect())
        pygame.draw.rect(screen, self.color, rect)


class Path(Entity):
    """Дорога - можно ходить, рисуется под игроком"""
    def __init__(self, x, y, width, height, color=TEX_DIRT_PATH):
        super().__init__(x, y, width, height, color)
        self.is_background = True
    
    def get_collision_rect(self):
        """Дорога НЕ блокирует движение"""
        return None


class Tree(Entity):
    """Дерево - ДВА блока. Верхний проходимый, нижний нет"""
    def __init__(self, x, y, block_width=40, block_height=40, color=TEX_TREE):
        # Позиция (верхний блок)
        self.x = x
        self.y = y
        self.block_width = block_width
        self.block_height = block_height
        self.color = color
        
        # Нижний блок (ствол)
        self.bottom_block_x = x
        self.bottom_block_y = y + block_height
        
        # Общий размер для сортировки
        self.width = block_width
        self.height = block_height * 2
    
    def get_collision_rect(self):
        """НИЖНИЙ блок полностью блокирует движение"""
        return pygame.Rect(self.bottom_block_x, self.bottom_block_y, self.block_width, self.block_height)
    
    def get_crown_rect(self):
        """Зона верхнего блока (для проверки невидимости игрока)"""
        return pygame.Rect(self.x, self.y, self.block_width, self.block_height)
    
    def draw(self, screen, camera):
        # Верхний блок (крона) - проходимый
        top_rect = camera.apply_rect(
            pygame.Rect(self.x, self.y, self.block_width, self.block_height)
        )
        pygame.draw.rect(screen, self.color, top_rect)
        
        # Нижний блок (ствол) - непроходимый
        bottom_rect = camera.apply_rect(
            pygame.Rect(self.bottom_block_x, self.bottom_block_y, self.block_width, self.block_height)
        )
        pygame.draw.rect(screen, self.color, bottom_rect)