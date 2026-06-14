import pygame

class Item:
    def __init__(self, x, y, name, interaction_zone=None):
        self.x = x
        self.y = y
        self.name = name
        self.picked_up = False
        self.width = 16
        self.height = 24
        
        # Зона взаимодействия (если не задана — создаём вокруг предмета)
        if interaction_zone:
            self.interaction_zone = pygame.Rect(*interaction_zone)
        else:
            self.interaction_zone = pygame.Rect(
                x - 20, y - 20,
                self.width + 40, self.height + 40
            )
    
    def check_interaction(self, player_rect):
        """Проверяет, находится ли игрок в зоне взаимодействия"""
        if self.picked_up:
            return False
        return self.interaction_zone.colliderect(player_rect)
    
    def draw(self, screen, camera):
        """Рисует предмет (бутылку с зельем)"""
        if self.picked_up:
            return
        
        screen_x = self.x * camera.scale + camera.camera.x
        screen_y = self.y * camera.scale + camera.camera.y
        
        # Рисуем бутылку (зелёный прямоугольник с пробкой)
        bottle_w = int(self.width * camera.scale)
        bottle_h = int(self.height * camera.scale)
        
        # Тело бутылки (зелёное)
        bottle_rect = pygame.Rect(int(screen_x), int(screen_y), bottle_w, bottle_h)
        pygame.draw.rect(screen, (0, 200, 100), bottle_rect)
        pygame.draw.rect(screen, (0, 0, 0), bottle_rect, 2)
        
        # Пробка (коричневая)
        cork_rect = pygame.Rect(int(screen_x), int(screen_y - 4 * camera.scale), bottle_w, int(4 * camera.scale))
        pygame.draw.rect(screen, (139, 69, 19), cork_rect)
        pygame.draw.rect(screen, (0, 0, 0), cork_rect, 2)