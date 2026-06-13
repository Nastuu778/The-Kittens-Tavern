import pygame
from settings import *
from player import Player
from wall import Wall
from zone import InteractionZone
from dialog_system import DialogSystem
from location import Location, TransitionZone
from npc import NPC
from camera import Camera  # Импортируем камеру!
from location_builder import VillageBuilder, ForestBuilder, LakeBuilder


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
        
        # Игрок - ПОДВИНУЛИ подальше от дерева!
        self.player = Player(200, 400)  # Было (100, 100)
        
        # КАМЕРА
        self.camera = Camera(self.current_location.width, self.current_location.height)
        self.camera.update(self.player)
        
        self.dt = 0
        
    def create_locations(self):
        """Создание всех локаций игры"""
        locations = {}
        
        # Создаём builders
        village = VillageBuilder()
        forest = ForestBuilder()
        lake = LakeBuilder()
        
        # Строим локации
        locations["location_1"] = village.build()
        locations["location_2"] = forest.build()
        locations["location_3"] = lake.build()
    
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
            # Передаем стены И РАЗМЕРЫ текущей локации
            self.player.move(
                keys, 
                self.current_location.get_walls(),
                self.current_location.width,
                self.current_location.height
            )
            
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
        
        # ОБНОВЛЯЕМ КАМЕРУ
        self.camera.update(self.player)
        
        # Обновление диалогов
        self.dialog_system.update(self.dt)
    
    def change_location(self, location_id, player_x, player_y):
        """Переход между локациями"""
        if location_id in self.locations:
            self.current_location_id = location_id
            self.current_location = self.locations[location_id]
            self.player.x = player_x
            self.player.y = player_y
            
            # ВАЖНО: Меняем размер камеры под новую локацию!
            self.camera.change_size(self.current_location.width, self.current_location.height)
            
            print(f"Переход на локацию: {self.current_location.name} ({self.current_location.width}x{self.current_location.height})")
    
    def draw(self):
         # Рисуем текущую локацию С УЧЕТОМ КАМЕРЫ И ИГРОКА
        self.current_location.draw(self.screen, self.camera, self.player)
        
        # Рисуем переходы
        for transition in self.current_location.transitions:
            transition.draw(self.screen, self.camera)
        
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
        
        # Координаты игрока и размер локации (для отладки)
        coords_text = small_font.render(
            f"X: {int(self.player.x)} Y: {int(self.player.y)} | "
            f"Map: {self.current_location.width}x{self.current_location.height}", 
            True, BLACK
        )
        self.screen.blit(coords_text, (10, 60))
        
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