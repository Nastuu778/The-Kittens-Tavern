import pygame
import json
from settings import *

class DialogSystem:
    def __init__(self, dialog_file="data/dialogs.json"):
        self.dialogs = self.load_dialogs(dialog_file)
        self.active = False
        self.current_npc = None
        self.current_dialog_key = None
        self.current_line_index = 0
        self.current_text = ""
        self.full_text = ""
        self.text_timer = 0
        self.font = pygame.font.Font(None, DIALOG_FONT_SIZE)
        self.name_font = pygame.font.Font(None, 28)
        
    def load_dialogs(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Файл {filepath} не найден!")
            return {}
    
    def start_dialog(self, npc_id, dialog_key="greeting"):
        if npc_id not in self.dialogs:
            return False
            
        self.active = True
        self.current_npc = self.dialogs[npc_id]
        self.current_dialog_key = dialog_key
        self.current_line_index = 0
        self.set_line(self.current_npc["dialogs"][dialog_key][0])
        return True
    
    def set_line(self, text):
        self.full_text = text
        self.current_text = ""
        self.text_timer = 0
        
    def next_line(self):
        if not self.active or not self.current_npc:
            return False
            
        dialog_lines = self.current_npc["dialogs"][self.current_dialog_key]
        
        # Если текст еще не полностью отображен - показать весь
        if len(self.current_text) < len(self.full_text):
            self.current_text = self.full_text
            return True
            
        # Переход к следующей строке
        self.current_line_index += 1
        if self.current_line_index < len(dialog_lines):
            self.set_line(dialog_lines[self.current_line_index])
            return True
        else:
            # Диалог окончен
            self.end_dialog()
            return False
    
    def end_dialog(self):
        self.active = False
        self.current_npc = None
        self.current_dialog_key = None
        self.current_line_index = 0
        self.current_text = ""
        
    def update(self, dt):
        if self.active and len(self.current_text) < len(self.full_text):
            self.text_timer += dt
            if self.text_timer >= DIALOG_TEXT_SPEED:
                self.current_text += self.full_text[len(self.current_text)]
                self.text_timer = 0
    
    def draw(self, screen):
        if not self.active:
            return
            
        # Рисуем рамку диалога
        dialog_rect = pygame.Rect(0, HEIGHT - DIALOG_BOX_HEIGHT, WIDTH, DIALOG_BOX_HEIGHT)
        pygame.draw.rect(screen, DARK_GRAY, dialog_rect)
        pygame.draw.rect(screen, WHITE, dialog_rect, 3)
        
        # Рисуем имя персонажа
        if self.current_npc:
            name_surface = self.name_font.render(self.current_npc["name"], True, WHITE)
            screen.blit(name_surface, (DIALOG_PADDING, HEIGHT - DIALOG_BOX_HEIGHT + 10))
        
        # Рисуем текст диалога
        text_surface = self.font.render(self.current_text, True, WHITE)
        screen.blit(text_surface, (DIALOG_PADDING, HEIGHT - DIALOG_BOX_HEIGHT + 50))
        
        # Индикатор продолжения
        if len(self.current_text) == len(self.full_text):
            indicator = self.font.render("▼", True, WHITE)
            screen.blit(indicator, (WIDTH - 50, HEIGHT - 50))