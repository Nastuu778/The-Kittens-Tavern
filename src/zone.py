import pygame
from settings import *

class InteractionZone:
    def __init__(self, x, y, width, height, npc_id="NPC_1"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.npc_id = npc_id
        self.active = False
        
    def check_interaction(self, player_rect):
        player_rect_obj = player_rect if isinstance(player_rect, pygame.Rect) else player_rect.get_rect()
        zone_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect_obj.colliderect(zone_rect)
    
    def draw(self, screen):
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 255, 0, 100), (0, 0, self.width, self.height))
        screen.blit(surface, (self.x, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)