import pygame
from settings import *

class Wall:
    def __init__(self, x, y, width, height, color=RED):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)