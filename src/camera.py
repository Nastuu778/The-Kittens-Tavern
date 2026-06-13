import pygame
from settings import *

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.scale = MAP_SCALE
        
    def apply_rect(self, rect):
        """Применяет смещение камеры С МАСШТАБОМ"""
        scaled_rect = pygame.Rect(
            rect.x * self.scale,
            rect.y * self.scale,
            rect.width * self.scale,
            rect.height * self.scale
        )
        return scaled_rect.move(self.camera.topleft)
    
    def update(self, target):
        """Обновляет камеру (игрок НЕ масштабируется)"""
        # Игрок остаётся 50x50, карта масштабируется
        x = -target.x * self.scale + WIDTH // 2 - target.width // 2
        y = -target.y * self.scale + HEIGHT // 2 - target.height // 2
        
        scaled_width = self.width * self.scale
        scaled_height = self.height * self.scale
        
        x = min(0, max(-(scaled_width - WIDTH), x))
        y = min(0, max(-(scaled_height - HEIGHT), y))
        
        self.camera = pygame.Rect(x, y, self.width, self.height)
    
    def change_size(self, width, height):
        self.width = width
        self.height = height
        self.camera = pygame.Rect(0, 0, width, height)