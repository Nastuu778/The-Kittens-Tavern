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
        
        # Границы мира (без масштаба, логические координаты)
        self.x = max(0, min(self.x, world_width - self.width))
        self.y = max(0, min(self.y, world_height - self.height))

    def check_collision(self, wall):
        # Проверяем коллизию в логических координатах
        wall_rect = wall.get_collision_rect() if hasattr(wall, 'get_collision_rect') else wall.get_rect()
        
        if wall_rect is None:
            return False
        
        return (self.x < wall_rect.x + wall_rect.width and
                self.x + self.width > wall_rect.x and
                self.y < wall_rect.y + wall_rect.height and
                self.y + self.height > wall_rect.y)
    
    def draw(self, screen, camera):
        # Игрок остаётся 50x50, просто сдвигаем по камере
        screen_x = self.x * camera.scale + camera.camera.x
        screen_y = self.y * camera.scale + camera.camera.y
        
        rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)