import pygame
from settings import *

class PickupMenu:
    def __init__(self):
        self.active = False
        self.current_item = None
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
    
    def open(self, item):
        """Открывает меню подбора"""
        self.active = True
        self.current_item = item
    
    def confirm(self):
        """Подтверждает подбор"""
        if self.current_item:
            self.current_item.picked_up = True
            print(f"✅ Подобрano: {self.current_item.name}")
            # 🔧 НЕ вызываем self.close() здесь - оставим current_item для инвентаря
            return True
        return False
    
    def close(self):
        """Закрывает меню и очищает текущий предмет"""
        self.active = False
        self.current_item = None
    
    def draw(self, screen):
        """Рисует меню подбора"""
        if not self.active or not self.current_item:
            return
        
        # Затемнение фона
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        # Окно меню
        box_width = 400
        box_height = 120
        box_x = (WIDTH - box_width) // 2
        box_y = (HEIGHT - box_height) // 2
        
        # Фон окна
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 3)
        
        # Текст вопроса
        text = self.font.render(f"Взять {self.current_item.name}?", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, box_y + 45))
        screen.blit(text, text_rect)
        
        # Подсказки
        # 🔧 Обновлённые подсказки (Q/R вместо Y/N)
        hint = self.small_font.render("Q - Да, R - Нет", True, (100, 100, 100))
        hint_rect = hint.get_rect(center=(WIDTH // 2, box_y + 85))
        screen.blit(hint, hint_rect)