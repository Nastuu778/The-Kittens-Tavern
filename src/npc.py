import pygame
from settings import *

class NPC:
    def __init__(self, x, y, npc_id, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.npc_id = npc_id
        self.color = color
        
    def draw(self, screen, camera):
        """🔧 ОТКЛЮЧЕНО — NPC теперь невидимы (только зоны взаимодействия)"""
        # Закомментировано для скрытия NPC
        # scale = camera.scale
        # screen_x = self.x * scale + camera.camera.x
        # screen_y = self.y * scale + camera.camera.y
        # scaled_width = self.width * scale
        # scaled_height = self.height * scale
        # rect = pygame.Rect(screen_x, screen_y, scaled_width, scaled_height)
        # center = rect.center
        # pygame.draw.circle(screen, self.color, center, scaled_width // 2)
        # pygame.draw.circle(screen, BLACK, center, scaled_width // 2, 2)
        pass  # Ничего не рисуем
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)