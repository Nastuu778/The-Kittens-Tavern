import pygame
from settings import *

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.scale = MAP_SCALE
        
    def apply_rect(self, rect):
        """Применяет смещение камеры и масштаб"""
        scaled_rect = pygame.Rect(
            rect.x * self.scale + self.camera.x,
            rect.y * self.scale + self.camera.y,
            rect.width * self.scale,
            rect.height * self.scale
        )
        return scaled_rect
    
    def apply_point(self, x, y):
        """Применяет камеру к точке"""
        return (x * self.scale + self.camera.x, y * self.scale + self.camera.y)
    
    def update(self, target):
        """Обновляет камеру с центром на игроке"""
        # Игрок остается в центре экрана (без масштабирования его размера)
        target_center_x = target.x * self.scale + target.width * self.scale // 2
        target_center_y = target.y * self.scale + target.height * self.scale // 2
        
        # Камера следует за игроком
        x = -target_center_x + WIDTH // 2
        y = -target_center_y + HEIGHT // 2
        
        # Ограничения камеры
        scaled_width = self.width * self.scale
        scaled_height = self.height * self.scale
        
        x = min(0, max(-(scaled_width - WIDTH), x))
        y = min(0, max(-(scaled_height - HEIGHT), y))
        
        self.camera.x = x
        self.camera.y = y
    
    def change_size(self, width, height):
        self.width = width
        self.height = height