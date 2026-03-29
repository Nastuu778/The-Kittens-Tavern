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
        
    def move(self, keys, walls=[]):
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
                
        self.x = max(0, min(self.x, WIDTH - self.width))
        self.y = max(0, min(self.y, HEIGHT - self.height - DIALOG_BOX_HEIGHT))
    
    def check_collision(self, rect):
        return (self.x < rect.x + rect.width and
                self.x + self.width > rect.x and
                self.y < rect.y + rect.height and
                self.y + self.height > rect.y)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)