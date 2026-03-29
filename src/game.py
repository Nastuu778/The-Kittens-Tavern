import pygame
from settings import *
from player import Player
from wall import Wall
from zone import InteractionZone
from dialog_system import DialogSystem
from location import Location, TransitionZone
from npc import NPC

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Adventure Game - Учебный Проект")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Система диалогов
        self.dialog_system = DialogSystem()
        
        # Создаем локации
        self.locations = self.create_locations()
        self.current_location_id = "location_1"
        self.current_location = self.locations[self.current_location_id]
        
        # Игрок
        self.player = Player(100, 100)
        
        # Для анимации текста
        self.dt = 0
        
    def create_locations(self):
        """Создание всех локаций игры"""
        locations = {}
        
        # === ЛОКАЦИЯ 1: Белая деревня (стартовая) ===
        location_1_walls = [
            Wall(200, 150, 80, 200),   # Дом 1
            Wall(500, 200, 100, 150),  # Дом 2
            Wall(50, 400, 150, 50),    # Забор
        ]
        
        location_1_zones = [
            InteractionZone(220, 180, 40, 40, "NPC_1"),  # Старейшина
            InteractionZone(520, 230, 40, 40, "NPC_2"),  # Торговец
        ]
        
        location_1_npcs = [
            NPC(220, 180, "NPC_1", (139, 69, 19)),   # Коричневый
            NPC(520, 230, "NPC_2", (0, 100, 200)),   # Синий
        ]
        
        location_1_transitions = [
            TransitionZone(750, 250, 50, 100, "location_2", 50, 250),  # Выход направо
        ]
        
        locations["location_1"] = Location(
            name="Деревня",
            bg_color=WHITE,
            walls=location_1_walls,
            zones=location_1_zones,
            npcs=location_1_npcs
        )
        locations["location_1"].transitions = location_1_transitions
        
        # === ЛОКАЦИЯ 2: Зеленый лес ===
        location_2_walls = [
            Wall(150, 100, 100, 100),  # Дерево 1
            Wall(400, 300, 120, 120),  # Дерево 2
            Wall(600, 150, 100, 100),  # Дерево 3
            Wall(250, 450, 150, 80),   # Кусты
        ]
        
        location_2_zones = [
            InteractionZone(300, 150, 40, 40, "NPC_3"),  # Стражник
            InteractionZone(550, 400, 40, 40, "NPC_4"),  # Житель
        ]
        
        location_2_npcs = [
            NPC(300, 150, "NPC_3", (128, 128, 128)),  # Серый
            NPC(550, 400, "NPC_4", (34, 139, 34)),    # Зеленый
        ]
        
        location_2_transitions = [
            TransitionZone(0, 250, 50, 100, "location_1", 700, 250),   # Назад в деревню
            TransitionZone(750, 300, 50, 100, "location_3", 50, 300),  # Вперед к озеру
        ]
        
        locations["location_2"] = Location(
            name="Лес",
            bg_color=(34, 139, 34),  # Зеленый
            walls=location_2_walls,
            zones=location_2_zones,
            npcs=location_2_npcs
        )
        locations["location_2"].transitions = location_2_transitions
        
        # === ЛОКАЦИЯ 3: Голубое озеро ===
        location_3_walls = [
            Wall(100, 200, 80, 150),  # Скала 1
            Wall(450, 100, 100, 120), # Скала 2
            Wall(600, 350, 120, 100), # Скала 3
        ]
        
        location_3_zones = [
            InteractionZone(350, 250, 40, 40, "NPC_1"),  # Рыбак (повторное использование NPC_1)
        ]
        
        location_3_npcs = [
            NPC(350, 250, "NPC_1", (0, 100, 200)),  # Синий (рыбак)
        ]
        
        location_3_transitions = [
            TransitionZone(0, 300, 50, 100, "location_2", 700, 300),  # Назад в лес
        ]
        
        locations["location_3"] = Location(
            name="Озеро",
            bg_color=(135, 206, 235),  # Голубой (Sky Blue)
            walls=location_3_walls,
            zones=location_3_zones,
            npcs=location_3_npcs
        )
        locations["location_3"].transitions = location_3_transitions
        
        return locations
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.KEYDOWN:
                # Начало диалога - кнопка E
                if event.key == pygame.K_e:
                    if not self.dialog_system.active:
                        for zone in self.current_location.zones:
                            if zone.active:
                                self.dialog_system.start_dialog(zone.npc_id)
                                break
                
                # Листание диалога - пробел
                if event.key == pygame.K_SPACE:
                    if self.dialog_system.active:
                        self.dialog_system.next_line()
                
                # Выход из диалога - ESC
                if event.key == pygame.K_ESCAPE:
                    if self.dialog_system.active:
                        self.dialog_system.end_dialog()
    
    def update(self):
        if not self.dialog_system.active:
            keys = pygame.key.get_pressed()
            # Передаем стены текущей локации
            self.player.move(keys, self.current_location.get_walls())
            
            # Проверка активных зон взаимодействия
            player_rect = self.player.get_rect()
            for zone in self.current_location.zones:
                zone.active = zone.check_interaction(player_rect)
            
            # Проверка переходов между локациями
            for transition in self.current_location.transitions:
                if transition.check_transition(player_rect):
                    self.change_location(transition.target_location, 
                                       transition.target_x, 
                                       transition.target_y)
                    break
        
        # Обновление диалогов
        self.dialog_system.update(self.dt)
    
    def change_location(self, location_id, player_x, player_y):
        """Переход между локациями"""
        if location_id in self.locations:
            self.current_location_id = location_id
            self.current_location = self.locations[location_id]
            self.player.x = player_x
            self.player.y = player_y
            print(f"Переход на локацию: {self.current_location.name}")
    
    def draw(self):
        # Рисуем текущую локацию
        self.current_location.draw(self.screen)
        
        # Рисуем переходы
        for transition in self.current_location.transitions:
            transition.draw(self.screen)
            
        # Рисуем игрока
        self.player.draw(self.screen)
        
        # Интерфейс
        self.draw_ui()
        
        # Рисуем диалоги
        self.dialog_system.draw(self.screen)
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Отрисовка интерфейса"""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 28)
        
        # Название локации
        location_text = font.render(f"Локация: {self.current_location.name}", True, BLACK)
        pygame.draw.rect(self.screen, WHITE, (10, 10, 250, 40))
        pygame.draw.rect(self.screen, BLACK, (10, 10, 250, 40), 2)
        self.screen.blit(location_text, (20, 18))
        
        if not self.dialog_system.active:
            # Подсказки управления
            controls_text = small_font.render("WASD - движение, E - диалог, SPACE - далее", True, BLACK)
            self.screen.blit(controls_text, (10, HEIGHT - 200))
            
            # Показываем подсказку о NPC
            for zone in self.current_location.zones:
                if zone.active:
                    hint_text = font.render("Нажмите E для разговора", True, (0, 128, 0))
                    pygame.draw.rect(self.screen, WHITE, (10, HEIGHT - 240, 300, 40))
                    self.screen.blit(hint_text, (20, HEIGHT - 232))
        else:
            # Подсказка во время диалога
            hint_text = small_font.render("SPACE - следующая реплика, ESC - закрыть", True, BLACK)
            pygame.draw.rect(self.screen, WHITE, (10, HEIGHT - DIALOG_BOX_HEIGHT - 50, 350, 35))
            self.screen.blit(hint_text, (15, HEIGHT - DIALOG_BOX_HEIGHT - 43))
    
    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0  # Delta time в секундах
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()