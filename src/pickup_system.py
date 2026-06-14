import pygame
from settings import *

class PickupSystem:
    def __init__(self):
        self.active = False
        self.current_item = None
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        
        # Инвентарь (пока просто список)
        self.inventory = []
    
    def start_pickup(self, item):
        """Начинает процесс подбора предмета"""
        self.active = True
        self.current_item = item
    
    def confirm_pickup(self):
        """Подтверждает подбор предмета"""
        if self.current_item:
            self.current_item.picked_up = True
            self.inventory.append(self.current_item)
            print(f"✅ Предмет подобран: {self.current_item.name}")
            self.active = False
            self.current_item = None
            return True
        return False
    
    def cancel_pickup(self):
        """Отменяет подбор предмета"""
        self.active = False
        self.current_item = None
    
    def draw(self, screen):
        """Рисует меню подбора предмета"""
        if not self.active or not self.current_item:
            return
        
        # Затемнение фона
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        # Окно меню
        box_width = 400
        box_height = 150
        box_x = (WIDTH - box_width) // 2
        box_y = (HEIGHT - box_height) // 2
        
        # Фон окна
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 3)
        
        # Текст вопроса
        text = self.font.render(f"Взять {self.current_item.name}?", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, box_y + 50))
        screen.blit(text, text_rect)
        
        # Подсказки
        hint = self.small_font.render("Y - Да, N - Нет", True, (100, 100, 100))
        hint_rect = hint.get_rect(center=(WIDTH // 2, box_y + 100))
        screen.blit(hint, hint_rect)