import pygame
from settings import *

class Wall:
    def __init__(self, x, y, width, height, color=RED):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        # 🔧 Добавляем rect для коллизий
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self, screen, camera):
        """Рисует стену с применением масштаба через камеру"""
        rect = camera.apply_rect(self.get_rect())
        pygame.draw.rect(screen, self.color, rect)
        
    def get_rect(self):
        """Возвращает хитбокс в ЛОГИЧЕСКИХ координатах (без масштаба)"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_collision_rect(self):
        """Для коллизий используем тот же rect (не масштабируем)"""
        return self.get_rect()