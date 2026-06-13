import pygame
from settings import *
from player import Player
from wall import Wall
from zone import InteractionZone
from dialog_system import DialogSystem
from location import Location, TransitionZone
from npc import NPC
from camera import Camera
from location_builder import VillageBuilder, ForestBuilder, LakeBuilder
from map_loader import MapLoader


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Adventure Game - Учебный Проект")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Система диалогов
        self.dialog_system = DialogSystem()
        
        # Загрузчик карт Tiled
        self.map_loader = MapLoader()
        
        # Сначала создаем камеру с временными размерами
        self.camera = Camera(1000, 1000)  # Временные размеры
        
        # Создаем локации (теперь self.camera существует)
        self.locations = self.create_locations()
        self.current_location_id = "location_1"
        self.current_location = self.locations[self.current_location_id]
        
        # Игрок
        self.player = Player(200, 400)
        
        # Обновляем камеру с правильными размерами текущей локации
        self.camera.change_size(self.current_location.width, self.current_location.height)
        self.camera.update(self.player)
        
        # Для анимации текста
        self.dt = 0
        
    def create_locations(self):
        """Создание всех локаций игры"""
        locations = {}
        
        # === ЛОКАЦИЯ 1: Деревня (из Tiled карты) ===
        try:
            map_data = self.map_loader.load_map('village.tmj')
            
            # Размеры карты из Tiled
            map_width = map_data['width'] * map_data['tilewidth']
            map_height = map_data['height'] * map_data['tileheight']
            
            # Ищем слой коллизий (любого типа!)
            collision_walls = []
            for layer in map_data['layers']:
                print(f"Слой: {layer['name']} (тип: {layer['type']})")
                
                # Если это Object Layer
                # Если это Object Layer
                if layer['name'] == 'Collision' and layer['type'] == 'objectgroup':
                    collision_walls = self.map_loader.load_collision_layer(layer)  # 🔧 Убрали scale
                    print(f"✅ Загружено {len(collision_walls)} хитбоксов из objectgroup!")
                    break

                # Если это Tile Layer
                elif layer['name'] == 'Collision' and layer['type'] == 'tilelayer':
                    collision_walls = self.map_loader.load_collision_from_tiles(layer, map_data)  # 🔧 Убрали scale=1
                    print(f"✅ Загружено {len(collision_walls)} хитбоксов из tilelayer!")
                    break
                            
            if not collision_walls:
                print("❌ Хитбоксы НЕ загружены! Проверь слой 'Collision' в Tiled")
            
            village = Location(
                name="Деревня",
                bg_color=TEX_GRASS,
                walls=collision_walls,
                zones=[],
                npcs=[],
                entities=[],
                width=map_width,
                height=map_height
            )
            village.map_data = map_data
            village.transitions = [
                TransitionZone(1454, 500, 50, 100, "location_2", 50, 500),
            ]
            locations["location_1"] = village
            
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")
            import traceback
            traceback.print_exc()
            print("⚠️ Используем резервную генерацию деревни")
            # Fallback на старый builder
            village = VillageBuilder()
            locations["location_1"] = village.build()
        
        # === ЛОКАЦИЯ 2: Лес (пока через builder) ===
        forest = ForestBuilder()
        locations["location_2"] = forest.build()
        
        # === ЛОКАЦИЯ 3: Озеро (пока через builder) ===
        lake = LakeBuilder()
        locations["location_3"] = lake.build()
        
        return locations
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if not self.dialog_system.active:
                        for zone in self.current_location.zones:
                            if zone.active:
                                self.dialog_system.start_dialog(zone.npc_id)
                                break
                
                if event.key == pygame.K_SPACE:
                    if self.dialog_system.active:
                        self.dialog_system.next_line()
                
                if event.key == pygame.K_ESCAPE:
                    if self.dialog_system.active:
                        self.dialog_system.end_dialog()
    
    def update(self):
        if not self.dialog_system.active:
            keys = pygame.key.get_pressed()
            
            # Получаем стены и проверяем
            walls = self.current_location.get_walls()
            
            self.player.move(
                keys, 
                walls,
                self.current_location.width,
                self.current_location.height
            )
            
            player_rect = self.player.get_rect()
            for zone in self.current_location.zones:
                zone.active = zone.check_interaction(player_rect)
            
            for transition in self.current_location.transitions:
                if transition.check_transition(player_rect):
                    self.change_location(transition.target_location, 
                                       transition.target_x, 
                                       transition.target_y)
                    break
        
        self.camera.update(self.player)
        self.dialog_system.update(self.dt)
    
    def change_location(self, location_id, player_x, player_y):
        """Переход между локациями"""
        if location_id in self.locations:
            self.current_location_id = location_id
            self.current_location = self.locations[location_id]
            self.player.x = player_x
            self.player.y = player_y
            
            self.camera.change_size(self.current_location.width, self.current_location.height)
            
            print(f"Переход на локацию: {self.current_location.name} ({self.current_location.width}x{self.current_location.height})")
    
    def draw_tiled_layer(self, layer_data):
        """Рисует слой (рекурсивно, с поддержкой групп)"""
        layer_type = layer_data.get('type')
        
        if layer_type == 'group':
            for child_layer in layer_data.get('layers', []):
                self.draw_tiled_layer(child_layer)
            return
        
        if layer_type != 'tilelayer':
            return
        
        if not layer_data.get('visible', True):
            return
        
        # Пропускаем слой Collision (это хитбоксы, не рисуем)
        if layer_data.get('name') == 'Collision':
            return
        
        map_width = self.current_location.map_data['width']
        tile_width = self.current_location.map_data['tilewidth']
        tile_height = self.current_location.map_data['tileheight']
        data = layer_data.get('data', [])
        scale = self.camera.scale
        
        if not data:
            return
        
        for i, gid in enumerate(data):
            if gid == 0:
                continue
            
            x = (i % map_width) * tile_width
            y = (i // map_width) * tile_height
            
            tile = self.map_loader.get_tile(gid)
            if tile:
                scaled_tile = pygame.transform.scale(tile, (tile_width * scale, tile_height * scale))
                
                screen_x = x * scale + self.camera.camera.x
                screen_y = y * scale + self.camera.camera.y
                
                if (screen_x + tile_width * scale >= 0 and screen_x <= WIDTH and
                    screen_y + tile_height * scale >= 0 and screen_y <= HEIGHT):
                    self.screen.blit(scaled_tile, (screen_x, screen_y))

    def draw(self):
        # Очищаем экран
        self.screen.fill(TEX_GRASS)
        
        # Проверяем, есть ли map_data
        if hasattr(self.current_location, 'map_data') and self.current_location.map_data:
            # Рисуем все слои карты
            for layer in self.current_location.map_data['layers']:
                # Пропускаем невидимые слои
                if not layer.get('visible', True):
                    continue
                
                # 🔧 ИСПРАВЛЕНО: рисуем ВСЕ слои (включая группы)
                # draw_tiled_layer сам разберётся с типом слоя
                self.draw_tiled_layer(layer)
        else:
            # Fallback на старую систему отрисовки
            self.current_location.draw(self.screen, self.camera, self.player)
        
        # Рисуем переходы между локациями
        for transition in self.current_location.transitions:
            transition.draw(self.screen, self.camera)
        
        # Рисуем NPC
        for npc in self.current_location.npcs:
            npc.draw(self.screen, self.camera)
        
        # Рисуем игрока
        self.player.draw(self.screen, self.camera)
        
        # Рисуем зоны взаимодействия
        for zone in self.current_location.zones:
            zone.draw(self.screen, self.camera)
        
        # Рисуем интерфейс и диалоги
        self.draw_ui()
        self.dialog_system.draw(self.screen)
        
        # Обновляем экран
        pygame.display.flip()
    
    def draw_ui(self):
        """Отрисовка интерфейса"""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 28)
        
        location_text = font.render(f"Локация: {self.current_location.name}", True, BLACK)
        pygame.draw.rect(self.screen, WHITE, (10, 10, 250, 40))
        pygame.draw.rect(self.screen, BLACK, (10, 10, 250, 40), 2)
        self.screen.blit(location_text, (20, 18))
        
        coords_text = small_font.render(
            f"X: {int(self.player.x)} Y: {int(self.player.y)} | "
            f"Map: {self.current_location.width}x{self.current_location.height}", 
            True, BLACK
        )
        self.screen.blit(coords_text, (10, 60))
        
        if not self.dialog_system.active:
            controls_text = small_font.render("WASD - движение, E - диалог, SPACE - далее", True, BLACK)
            self.screen.blit(controls_text, (10, HEIGHT - 200))
            
            for zone in self.current_location.zones:
                if zone.active:
                    hint_text = font.render("Нажмите E для разговора", True, (0, 128, 0))
                    pygame.draw.rect(self.screen, WHITE, (10, HEIGHT - 240, 300, 40))
                    self.screen.blit(hint_text, (20, HEIGHT - 232))
        else:
            hint_text = small_font.render("SPACE - следующая реплика, ESC - закрыть", True, BLACK)
            pygame.draw.rect(self.screen, WHITE, (10, HEIGHT - DIALOG_BOX_HEIGHT - 50, 350, 35))
            self.screen.blit(hint_text, (15, HEIGHT - DIALOG_BOX_HEIGHT - 43))
    
    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()