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
        rect = camera.apply_rect(self.get_rect())
        center = rect.center
        pygame.draw.circle(screen, self.color, center, self.width//2)
        pygame.draw.circle(screen, BLACK, center, self.width//2, 2)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)