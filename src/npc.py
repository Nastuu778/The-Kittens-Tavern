import pygame
from settings import *

class NPC:
    """Неигровой персонаж"""
    def __init__(self, x, y, npc_id, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.npc_id = npc_id
        self.color = color
        
    def draw(self, screen):
        # Рисуем персонажа (круг)
        pygame.draw.circle(screen, self.color, (self.x + self.width//2, self.y + self.height//2), self.width//2)
        # Обводка
        pygame.draw.circle(screen, BLACK, (self.x + self.width//2, self.y + self.height//2), self.width//2, 2)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)