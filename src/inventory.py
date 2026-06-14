import pygame
from settings import *

class InventoryItem:
    """Класс предмета в инвентаре с поддержкой количества"""
    def __init__(self, name):
        self.name = name
        self.count = 1
    
    def add(self):
        """Увеличивает количество предмета на 1"""
        self.count += 1
    
    def get_display_name(self):
        """Возвращает название с количеством (если > 1)"""
        if self.count > 1:
            return f"{self.name} x{self.count}"
        return self.name


class Inventory:
    def __init__(self):
        self.items = []  # Список объектов InventoryItem
        self.open = False
        
        # 🔧 Кнопка открытия инвентаря (жёлтая с "i") - ИНТЕРАКТИВНАЯ
        self.button_rect = pygame.Rect(20, HEIGHT // 2 + 50, 50, 50)
        self.button_color = (255, 215, 0)  # Золотой/жёлтый
        self.button_hover = False
        
        # 🔧 Панель инвентаря
        self.panel_width = 300
        self.panel_height = 400
        self.panel_rect = pygame.Rect(20, HEIGHT // 2 - self.panel_height // 2, 
                                      self.panel_width, self.panel_height)
        self.panel_padding = 15
        
        # 🔧 Кнопка закрытия (крестик)
        self.close_button_size = 25
        self.close_button_rect = pygame.Rect(
            self.panel_rect.right - self.close_button_size - 10,
            self.panel_rect.top + 10,
            self.close_button_size,
            self.close_button_size
        )
        
        # Шрифты
        self.title_font = pygame.font.Font(None, 32)
        self.item_font = pygame.font.Font(None, 26)
        self.empty_font = pygame.font.Font(None, 24)
        self.count_font = pygame.font.Font(None, 22)  # 🔧 Для количества
        
        # 🔧 Цвета UI (светло-оранжевый фон)
        self.panel_bg = (255, 200, 150)      # Светло-оранжевый / персиковый
        self.panel_border = (255, 140, 50)   # Тёмно-оранжевая рамка
        self.text_color = (50, 30, 10)       # Тёмно-коричневый текст
        self.empty_text_color = (100, 80, 60)
        self.count_color = (200, 50, 50)     # 🔧 Красный цвет для количества
        
    def add_item(self, item_name):
        """
        Добавляет предмет в инвентарь по имени.
        Если предмет уже есть — увеличивает счётчик.
        """
        if not item_name:
            print("⚠️ Предмет без имени!")
            return False
        
        # 🔧 Ищем существующий предмет с таким именем
        for existing_item in self.items:
            if existing_item.name == item_name:
                existing_item.add()
                return True
        
        # 🔧 Создаём новый предмет
        new_item = InventoryItem(item_name)
        self.items.append(new_item)
        return True
    
    def toggle(self):
        """Переключает состояние инвентаря"""
        self.open = not self.open
    
    def close(self):
        """Закрывает инвентарь"""
        self.open = False
    
    def check_button_click(self, pos):
        """Проверяет клик по кнопке открытия"""
        if self.button_rect.collidepoint(pos):
            self.toggle()
            return True
        return False
    
    def check_close_click(self, pos):
        """Проверяет клик по крестику закрытия"""
        if self.close_button_rect.collidepoint(pos):
            self.close()
            return True
        return False
    
    def handle_event(self, event):
        """Обработка событий мыши (КЛИКИ)"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            
            if self.open:
                if self.check_close_click(pos):
                    return True
            else:
                if self.check_button_click(pos):
                    return True
        return False
    
    def handle_key_event(self, event):
        """Обработка нажатия клавиши B"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                self.toggle()
                return True
        return False
    
    def update(self):
        """Обновление (эффекты наведения)"""
        mouse_pos = pygame.mouse.get_pos()
        self.button_hover = self.button_rect.collidepoint(mouse_pos)
    
    def draw_button(self, screen):
        """Рисует кнопку открытия инвентаря"""
        color = (255, 235, 100) if self.button_hover else self.button_color
        border_width = 3 if self.button_hover else 2
        
        pygame.draw.rect(screen, color, self.button_rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.button_rect, border_width, border_radius=8)
        
        text = self.title_font.render("i", True, BLACK)
        text_rect = text.get_rect(center=self.button_rect.center)
        screen.blit(text, text_rect)
    
    def draw_panel(self, screen):
        """Рисует панель инвентаря"""
        # Затемнение фона
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        # Фон панели (светло-оранжевый)
        pygame.draw.rect(screen, self.panel_bg, self.panel_rect, border_radius=10)
        pygame.draw.rect(screen, self.panel_border, self.panel_rect, 3, border_radius=10)
        
        # Заголовок
        title = self.title_font.render("📦 Инвентарь", True, self.text_color)
        screen.blit(title, (self.panel_rect.x + self.panel_padding, 
                           self.panel_rect.y + self.panel_padding))
        
        # Кнопка закрытия (крестик)
        self._draw_close_button(screen)
        
        # Список предметов
        self._draw_items_list(screen)
    
    def _draw_close_button(self, screen):
        """Рисует крестик закрытия"""
        pygame.draw.circle(screen, (200, 50, 50), 
                          self.close_button_rect.center, 
                          self.close_button_size // 2)
        pygame.draw.circle(screen, WHITE, 
                          self.close_button_rect.center, 
                          self.close_button_size // 2, 2)
        
        center = self.close_button_rect.center
        offset = self.close_button_size // 4
        pygame.draw.line(screen, WHITE, 
                        (center[0] - offset, center[1] - offset),
                        (center[0] + offset, center[1] + offset), 2)
        pygame.draw.line(screen, WHITE, 
                        (center[0] + offset, center[1] - offset),
                        (center[0] - offset, center[1] + offset), 2)
    
    def _draw_items_list(self, screen):
        """Рисует список предметов в инвентаре с количеством"""
        start_y = self.panel_rect.y + self.panel_padding + 40
        item_height = 35
        
        # 🔧 УБРАНЫ логи отладки
        
        if not self.items:
            empty_text = self.empty_font.render("Инвентарь пуст", True, self.empty_text_color)
            screen.blit(empty_text, (self.panel_rect.x + self.panel_padding, 
                                    self.panel_rect.centery))
            return
        
        for i, item in enumerate(self.items):
            y_pos = start_y + i * item_height
            
            # Фон строки
            row_color = (255, 180, 120) if i % 2 == 0 else (255, 165, 100)
            pygame.draw.rect(screen, row_color, 
                           (self.panel_rect.x + 10, y_pos - 5, 
                            self.panel_width - 20, item_height),
                           border_radius=4)
            
            # Иконка предмета
            icon_size = 20
            icon_rect = pygame.Rect(self.panel_rect.x + self.panel_padding, 
                                   y_pos, icon_size, icon_size)
            pygame.draw.rect(screen, (0, 200, 100), icon_rect, border_radius=3)
            pygame.draw.rect(screen, BLACK, icon_rect, 1, border_radius=3)
            
            # Название предмета
            item_text = self.item_font.render(item.name, True, self.text_color)
            screen.blit(item_text, (icon_rect.right + 10, y_pos + 5))
            
            # Количество (если больше 1)
            if item.count > 1:
                count_text = self.count_font.render(f"x{item.count}", True, self.count_color)
                count_x = self.panel_rect.x + self.panel_width - self.panel_padding - count_text.get_width() - 10
                screen.blit(count_text, (count_x, y_pos + 7))
    
    def draw(self, screen):
        """Основной метод отрисовки"""
        if not self.open:
            self.draw_button(screen)
        else:
            self.draw_panel(screen)