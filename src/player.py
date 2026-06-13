import pygame
from settings import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.color = BLUE
        
    def move(self, keys, walls=[], world_width=2000, world_height=1500):
        old_x, old_y = self.x, self.y
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            
        for wall in walls:
            if self.check_collision(wall):
                self.x = old_x
                
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
            
        for wall in walls:
            if self.check_collision(wall):
                self.y = old_y
                
        # Ограничиваем ГРАНИЦАМИ ТЕКУЩЕЙ ЛОКАЦИИ
        self.x = max(0, min(self.x, world_width - self.width))
        self.y = max(0, min(self.y, world_height - self.height))
    
    def check_collision(self, rect):
        return (self.x < rect.x + rect.width and
                self.x + self.width > rect.x and
                self.y < rect.y + rect.height and
                self.y + self.height > rect.y)
    
    def draw(self, screen, camera):
        # Применяем камеру
        rect = camera.apply_rect(self.get_rect())
        pygame.draw.rect(screen, self.color, rect)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)