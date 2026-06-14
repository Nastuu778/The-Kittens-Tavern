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
        """Проверка в логических координатах"""
        player_rect_obj = player_rect if isinstance(player_rect, pygame.Rect) else player_rect.get_rect()
        zone_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.active = player_rect_obj.colliderect(zone_rect)
        return self.active
    
    def draw(self, screen, camera):
        """Рисует зону с масштабом через камеру"""
        rect = camera.apply_rect(self.get_rect())
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 255, 0, 100), (0, 0, rect.width, rect.height))
        screen.blit(surface, rect.topleft)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)