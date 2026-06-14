import pygame
import json
from settings import *

class DialogSystem:
    def __init__(self, dialog_file="data/dialogs.json"):
        self.dialogs = self.load_dialogs(dialog_file)
        self.active = False
        self.current_npc = None
        self.current_npc_id = None
        self.current_dialog_key = None
        self.current_line_index = 0
        self.current_text = ""
        self.full_text = ""
        self.text_timer = 0
        self.font = pygame.font.Font(None, DIALOG_FONT_SIZE)
        self.name_font = pygame.font.Font(None, 28)
        self.button_font = pygame.font.Font(None, 32)
        
        # Кнопки действий
        self.give_button = None
        self.exit_button = None
        self.can_continue = False
        self.current_quest_item = None
        
    def load_dialogs(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ Диалоги загружены из {filepath}")
                # 🔧 Проверяем, есть ли quest_items
                for npc_id, npc_data in data.items():
                    if "quest_items" in npc_data:
                        print(f"   {npc_id}: quest_items = {npc_data['quest_items']}")
                return data
        except FileNotFoundError:
            print(f"❌ Файл {filepath} не найден!")
            return {}
    
    def start_dialog(self, npc_id, dialog_key="greeting", inventory=None, quest_system=None):
        print(f"\n🗨️  Начало диалога с {npc_id} (диалог: {dialog_key})")
        
        if npc_id not in self.dialogs:
            print(f"   ❌ NPC {npc_id} не найден в диалогах!")
            return False
            
        self.active = True
        self.current_npc = self.dialogs[npc_id]
        self.current_npc_id = npc_id
        self.current_dialog_key = dialog_key
        self.current_line_index = 0
        self.inventory = inventory
        self.quest_system = quest_system
        
        print(f"   Инвентарь: {inventory}")
        print(f"   Система квестов: {quest_system}")
        
        # Загружаем первую реплику
        if dialog_key in self.current_npc.get("dialogs", {}):
            dialog_lines = self.current_npc["dialogs"][dialog_key]
            if dialog_lines:
                self.set_line(dialog_lines[0])
            else:
                print(f"   ⚠️  Диалог {dialog_key} пуст!")
        else:
            print(f"   ⚠️  Диалог {dialog_key} не найден, используем greeting")
            if "greeting" in self.current_npc.get("dialogs", {}):
                self.set_line(self.current_npc["dialogs"]["greeting"][0])
        
        # 🔧 Проверяем предметы
        self._check_quest_item()
        
        return True
    
    def _check_quest_item(self):
        """🔧 Проверяет, есть ли предмет для квеста"""
        print(f"   🔍 Проверка предметов для {self.current_npc_id}...")
        
        if not self.inventory or not self.quest_system:
            print(f"      ⚠️  Нет инвентаря или системы квестов")
            self.can_continue = True
            self.current_quest_item = None
            return
        
        # Получаем информацию о предмете из JSON
        npc_data = self.current_npc
        quest_items = npc_data.get("quest_items", {})
        
        print(f"      quest_items из JSON: {quest_items}")
        
        # Ищем активный квест
        for quest_id, item_info in quest_items.items():
            print(f"      Проверка квеста {quest_id}...")
            
            quest = self.quest_system.quests.get(quest_id)
            if not quest:
                print(f"         ❌ Квест {quest_id} не найден")
                continue
            
            print(f"         Состояние квеста: {quest.state.name}")
            
            if quest.state.name == "IN_PROGRESS":
                item_name = item_info.get("item_name")
                show_at_line = item_info.get("show_at_line", 0)
                
                print(f"         Нужен предмет: {item_name}")
                print(f"         Показать на строке: {show_at_line}")
                
                # Проверяем инвентарь
                for inv_item in self.inventory.items:
                    print(f"         Предмет в инвентаре: {inv_item.name} (x{inv_item.count})")
                    
                    if inv_item.name == item_name and inv_item.count > 0:
                        print(f"         ✅ НАЙДЕН предмет {item_name}!")
                        
                        self.current_quest_item = {
                            "quest_id": quest_id,
                            "item_name": item_name,
                            "show_at_line": show_at_line
                        }
                        self.can_continue = False
                        
                        # Сразу создаём кнопку если мы уже на нужной строке
                        if self.current_line_index >= show_at_line:
                            self.give_button = pygame.Rect(WIDTH - 250, HEIGHT - DIALOG_BOX_HEIGHT + 50, 200, 50)
                            print(f"         ✅ Кнопка 'Отдать' СОЗДАНА!")
                        else:
                            self.give_button = None
                            print(f"         ⏳ Ждём строку {show_at_line} (сейчас {self.current_line_index})")
                        
                        return
        
        print(f"         ❌ Предметов для отдачи нет")
        self.current_quest_item = None
        self.give_button = None
        self.can_continue = True
    
    def set_line(self, text):
        self.full_text = text
        self.current_text = ""
        self.text_timer = 0
        
        print(f"   📝 Строка {self.current_line_index}: {text[:50]}...")
        
        # Проверяем, нужно ли показать кнопку
        self._update_buttons()
    
    def _update_buttons(self):
        """🔧 Обновляет видимость кнопок"""
        if self.current_quest_item:
            show_at = self.current_quest_item["show_at_line"]
            print(f"      🔘 Проверка кнопки: строка {self.current_line_index} >= {show_at}?")
            
            if self.current_line_index >= show_at:
                self.give_button = pygame.Rect(WIDTH - 250, HEIGHT - DIALOG_BOX_HEIGHT + 50, 200, 50)
                self.can_continue = False
                print(f"      ✅ Кнопка 'Отдать: {self.current_quest_item['item_name']}' ПОКАЗАНА")
            else:
                self.give_button = None
                self.can_continue = True
                print(f"      ⏳ Кнопка скрыта (ждем строку {show_at})")
        else:
            self.give_button = None
            self.can_continue = True
    
    def next_line(self):
        if not self.active or not self.current_npc:
            return False
        
        # Если есть кнопка "Отдать" — нельзя продолжить
        if self.give_button and not self.can_continue:
            print("   ⛔ Нельзя продолжить, пока не отдашь предмет!")
            return False
            
        dialog_lines = self.current_npc["dialogs"].get(self.current_dialog_key, [])
        
        # Если текст еще не полностью отображен — показать весь
        if len(self.current_text) < len(self.full_text):
            self.current_text = self.full_text
            return True
        
        # Переход к следующей строке
        self.current_line_index += 1
        print(f"\n   ⏭️  Переход к строке {self.current_line_index}")
        
        if self.current_line_index < len(dialog_lines):
            self.set_line(dialog_lines[self.current_line_index])
            return True
        else:
            print("   🔚 Диалог окончен")
            self.end_dialog()
            return False
    
    def give_item(self):
        """🔧 Отдаёт предмет NPC"""
        print(f"\n   💝 Попытка отдать предмет...")
        
        if not self.give_button or not self.current_quest_item:
            print("      ❌ Нет кнопки или предмета")
            return False
        
        if self.inventory and self.quest_system:
            quest_id = self.current_quest_item["quest_id"]
            item_name = self.current_quest_item["item_name"]
            
            # Находим предмет в инвентаре
            for inv_item in self.inventory.items:
                if inv_item.name == item_name and inv_item.count > 0:
                    # 🔧 УМЕНЬШАЕМ количество
                    inv_item.count -= 1
                    print(f"      Предмет {item_name}: было {inv_item.count + 1}, стало {inv_item.count}")
                    
                    # 🔧 Если количество 0 — удаляем из списка
                    if inv_item.count <= 0:
                        self.inventory.items.remove(inv_item)
                        print(f"      ✅ Предмет {item_name} УДАЛЁН из инвентаря")
                    else:
                        print(f"      Осталось {inv_item.count} шт. {item_name}")
                    
                    # Обновляем квест
                    quest = self.quest_system.quests.get(quest_id)
                    if quest:
                        quest.add_item(item_name)
                        print(f"      ✅ Отдан предмет: {item_name}")
                        print(f"         Прогресс квеста: {quest.collected}/{quest.target_count}")
                        
                        if quest.state.name == "COMPLETED":
                            print(f"         🎉 КВЕСТ ЗАВЕРШЁН!")
                    
                    # Убираем кнопку
                    self.current_quest_item = None
                    self.give_button = None
                    self.can_continue = True
                    print("      ✅ Кнопка убрана, можно продолжить диалог")
                    return True
        
        print("      ❌ Не удалось отдать предмет")
        return False
    
    def end_dialog(self):
        print("   🚪 Диалог закрыт\n")
        self.active = False
        self.current_npc = None
        self.current_npc_id = None
        self.current_dialog_key = None
        self.current_line_index = 0
        self.current_text = ""
        self.give_button = None
        self.exit_button = None
        self.can_continue = False
        self.current_quest_item = None
        self.inventory = None
        self.quest_system = None
    
    def update(self, dt):
        if self.active and len(self.current_text) < len(self.full_text):
            self.text_timer += dt
            if self.text_timer >= DIALOG_TEXT_SPEED:
                self.current_text += self.full_text[len(self.current_text)]
                self.text_timer = 0
    
    def check_button_click(self, pos):
        """🔧 Проверка клика по кнопкам"""
        if self.give_button and self.give_button.collidepoint(pos):
            print(f"   🖱️  Клик по кнопке 'Отдать'")
            return self.give_item()
        if self.exit_button and self.exit_button.collidepoint(pos):
            print(f"   🖱️  Клик по кнопке 'Выйти'")
            self.end_dialog()
            return True
        return False
    
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
        
        # Рисуем кнопки действий
        if self.give_button:
            # Кнопка "Отдать [предмет]"
            pygame.draw.rect(screen, (0, 200, 100), self.give_button, border_radius=8)
            pygame.draw.rect(screen, WHITE, self.give_button, 2, border_radius=8)
            
            item_name = self.current_quest_item["item_name"] if self.current_quest_item else "Предмет"
            give_text = self.button_font.render(f"Отдать: {item_name}", True, BLACK)
            text_rect = give_text.get_rect(center=self.give_button.center)
            screen.blit(give_text, text_rect)
            print(f"   🎨 Отрисована кнопка 'Отдать: {item_name}'")
        else:
            # Кнопка "Выйти"
            exit_button = pygame.Rect(WIDTH - 250, HEIGHT - DIALOG_BOX_HEIGHT + 50, 200, 50)
            self.exit_button = exit_button
            pygame.draw.rect(screen, (200, 50, 50), exit_button, border_radius=8)
            pygame.draw.rect(screen, WHITE, exit_button, 2, border_radius=8)
            exit_text = self.button_font.render("Выйти", True, WHITE)
            text_rect = exit_text.get_rect(center=exit_button.center)
            screen.blit(exit_text, text_rect)
        
        # Индикатор продолжения
        if self.can_continue and len(self.current_text) == len(self.full_text):
            indicator = self.font.render("▼ SPACE", True, WHITE)
            screen.blit(indicator, (WIDTH - 150, HEIGHT - 50))