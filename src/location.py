import pygame
from settings import *

class Location:
    def __init__(self, name, bg_color, walls=[], zones=[], npcs=[]):
        self.name = name
        self.bg_color = bg_color
        self.walls = walls
        self.zones = zones
        self.npcs = npcs  # Список NPC на локации
        
    def draw(self, screen):
        screen.fill(self.bg_color)
        
        # Рисуем зоны
        for zone in self.zones:
            zone.draw(screen)
        
        # Рисуем стены
        for wall in self.walls:
            wall.draw(screen)
            
        # Рисуем NPC (пока просто кружочки)
        for npc in self.npcs:
            npc.draw(screen)
    
    def get_walls(self):
        return self.walls
    
    def get_zones(self):
        return self.zones


class TransitionZone:
    """Зона перехода между локациями"""
    def __init__(self, x, y, width, height, target_location, target_x, target_y, color=(100, 100, 255)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.target_location = target_location  # Идентификатор локации
        self.target_x = target_x  # Позиция игрока после перехода
        self.target_y = target_y
        self.color = color
        self.active = False
        
    def check_transition(self, player_rect):
        player_rect_obj = player_rect if isinstance(player_rect, pygame.Rect) else player_rect.get_rect()
        zone_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect_obj.colliderect(zone_rect)
    
    def draw(self, screen):
        # Рисуем зону перехода (дверь/портал)
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)
        
        # Добавляем текст "ВЫХОД"
        font = pygame.font.Font(None, 24)
        text = font.render("ВЫХОД", True, WHITE)
        text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        screen.blit(text, text_rect)