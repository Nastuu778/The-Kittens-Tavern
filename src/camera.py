import pygame
from settings import *

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        
    def apply(self, entity):
        """Применяет смещение камеры к объекту"""
        return entity.get_rect().move(self.camera.topleft)
    
    def apply_rect(self, rect):
        """Применяет смещение к прямоугольнику"""
        return rect.move(self.camera.topleft)
    
    def update(self, target):
        """Обновляет камеру, чтобы следить за целью (игроком)"""
        x = -target.x + WIDTH // 2 - target.width // 2
        y = -target.y + HEIGHT // 2 - target.height // 2
        
        # Ограничиваем камеру границами мира
        x = min(0, max(-(self.width - WIDTH), x))
        y = min(0, max(-(self.height - HEIGHT), y))
        
        self.camera = pygame.Rect(x, y, self.width, self.height)
    
    def change_size(self, width, height):
        """Меняет размер камеры при переходе на новую локацию"""
        self.width = width
        self.height = height
        self.camera = pygame.Rect(0, 0, width, height)