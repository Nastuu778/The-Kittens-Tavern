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
from settings import LAYER_RENDER_ORDER
from item import Item
from pickup_menu import PickupMenu
from inventory import Inventory

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Adventure Game - Учебный Проект")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Система диалогов
        self.dialog_system = DialogSystem()
        
        # 🔧 Инвентарь
        self.inventory = Inventory()
        
        # Меню подбора предметов
        self.pickup_menu = PickupMenu()
        
        # Отдельные загрузчики для каждой карты
        self.map_loader_village = MapLoader()
        self.map_loader_forest = MapLoader()
        self.map_loader_lake = MapLoader()
        
        # Камера (временные размеры, обновятся при загрузке)
        self.camera = Camera(1000, 1000)
        
        # Создаем локации
        self.locations = self.create_locations()
        self.current_location_id = "location_1" 
        self.current_location = self.locations[self.current_location_id]
        
        # Игрок
        self.player = Player(200, 400)
        
        # Обновляем камеру под размер локации
        self.camera.change_size(self.current_location.width, self.current_location.height)
        self.camera.update(self.player)
        
        # Delta time для анимаций
        self.dt = 0

        # Предметы на карте (квестовые)
        self.items = {
            "location_1": [
                Item(195, 168, "Зелье", interaction_zone=(175, 150, 25, 35)),
            ],
            "location_2": [
                Item(300, 200, "Трава", interaction_zone=(280, 180, 40, 40)),
                Item(500, 350, "Трава", interaction_zone=(480, 330, 40, 40)),
                Item(600, 150, "Трава", interaction_zone=(580, 130, 40, 40)),
                Item(400, 400, "Карта", interaction_zone=(380, 380, 40, 40)),
            ],
            "location_3": [
                Item(250, 200, "Кристалл", interaction_zone=(230, 180, 40, 40)),
                Item(350, 300, "Кристалл", interaction_zone=(330, 280, 40, 40)),
            ],
        }
                        
    def create_locations(self):
        """Создание всех локаций игры"""
        locations = {}
        
        # === ЛОКАЦИЯ 1: Деревня ===
        print("\n" + "="*50)
        print("ЗАГРУЗКА ДЕРЕВНИ")
        print("="*50)
        
        try:
            map_data = self.map_loader_village.load_map('village.tmj')
            map_width = map_data['width'] * map_data['tilewidth']
            map_height = map_data['height'] * map_data['tileheight']
            
            collision_walls = []
            for layer in map_data['layers']:
                if layer.get('name') == 'Collision':
                    if layer.get('type') == 'objectgroup':
                        collision_walls = self.map_loader_village.load_collision_layer(layer)
                        break
                    elif layer.get('type') == 'tilelayer':
                        collision_walls = self.map_loader_village.load_collision_from_tiles(layer, map_data)
                        break
            
            transitions = []
            for layer in map_data['layers']:
                if layer.get('type') == 'objectgroup':
                    for obj in layer.get('objects', []):
                        if obj.get('name') == 'Transition' or obj.get('type') == 'Transition':
                            props = obj.get('properties', {})
                            if isinstance(props, list):
                                props_dict = {}
                                for p in props:
                                    props_dict[p['name']] = p.get('value', 0)
                                props = props_dict
                            
                            transitions.append(TransitionZone(
                                obj['x'], obj['y'],
                                obj.get('width', 50) + 10,
                                obj.get('height', 100),
                                props.get('target_location', 'location_2'),
                                props.get('target_x', 40),
                                props.get('target_y', 285)
                            ))
            
            if not transitions:
                transitions = [TransitionZone(720, 230, 20, 80, "location_2", 40, 265)]
            
            village = Location(
                name="Деревня", bg_color=TEX_GRASS, walls=collision_walls,
                zones=[], npcs=[], entities=[], width=map_width, height=map_height
            )
            village.map_data = map_data
            village.transitions = transitions
            locations["location_1"] = village
            print(f"✅ Деревня загружена! Стены: {len(collision_walls)}")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки деревни: {e}")
            village = VillageBuilder()
            locations["location_1"] = village.build()
        
        # === ЛОКАЦИЯ 2: Лес ===
        print("\n" + "="*50)
        print("ЗАГРУЗКА ЛЕСА")
        print("="*50)
        
        try:
            map_data = self.map_loader_forest.load_map('forest.tmj')
            map_width = map_data['width'] * map_data['tilewidth']
            map_height = map_data['height'] * map_data['tileheight']
            
            collision_walls = []
            for layer in map_data['layers']:
                if layer.get('name') == 'Collision':
                    if layer.get('type') == 'objectgroup':
                        collision_walls = self.map_loader_forest.load_collision_layer(layer)
                        break
                    elif layer.get('type') == 'tilelayer':
                        collision_walls = self.map_loader_forest.load_collision_from_tiles(layer, map_data)
                        break
            
            if not collision_walls:
                collision_walls = [
                    Wall(0, 0, map_width, 10), Wall(0, 0, 10, map_height),
                    Wall(map_width - 10, 0, 10, map_height), Wall(0, map_height - 10, map_width, 10),
                ]
            
            transitions = []
            for layer in map_data['layers']:
                if layer.get('type') == 'objectgroup':
                    for obj in layer.get('objects', []):
                        if obj.get('name') == 'Transition' or obj.get('type') == 'Transition':
                            props = obj.get('properties', {})
                            if isinstance(props, list):
                                props_dict = {}
                                for p in props:
                                    props_dict[p['name']] = p.get('value', 0)
                                props = props_dict
                            
                            transitions.append(TransitionZone(
                                obj['x'], obj['y'],
                                obj.get('width', 50) + 10,
                                obj.get('height', 100),
                                props.get('target_location', 'location_1'),
                                props.get('target_x', 700),
                                props.get('target_y', 280)
                            ))
            
            if not transitions:
                transitions = [
                    TransitionZone(0, 200, 20, 180, "location_1", 680, 280),
                    TransitionZone(720, 180, 20, 200, "location_3", 50, 200),
                ]
            
            forest = Location(
                name="Лес", bg_color=FOREST_BG, walls=collision_walls,
                zones=[], npcs=[], entities=[], width=map_width, height=map_height
            )
            forest.map_data = map_data
            forest.transitions = transitions
            locations["location_2"] = forest
            print(f"✅ Лес загружен! Стены: {len(collision_walls)}")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки леса: {e}")
            forest = ForestBuilder()
            locations["location_2"] = forest.build()
        
        # === ЛОКАЦИЯ 3: Озеро ===
        print("\n" + "="*50)
        print("ЗАГРУЗКА ОЗЕРА")
        print("="*50)
        
        try:
            map_data = self.map_loader_lake.load_map('lake.tmj')
            map_width = map_data['width'] * map_data['tilewidth']
            map_height = map_data['height'] * map_data['tileheight']
            
            collision_walls = []
            for layer in map_data['layers']:
                if layer.get('name') == 'Collision':
                    if layer.get('type') == 'objectgroup':
                        collision_walls = self.map_loader_lake.load_collision_layer(layer)
                        break
                    elif layer.get('type') == 'tilelayer':
                        collision_walls = self.map_loader_lake.load_collision_from_tiles(layer, map_data)
                        break
            
            if not collision_walls:
                collision_walls = [
                    Wall(0, 0, map_width, 10), Wall(0, 0, 10, map_height),
                    Wall(map_width - 10, 0, 10, map_height), Wall(0, map_height - 10, map_width, 10),
                ]
            
            transitions = []
            for layer in map_data['layers']:
                if layer.get('type') == 'objectgroup':
                    for obj in layer.get('objects', []):
                        if obj.get('name') == 'Transition' or obj.get('type') == 'Transition':
                            props = obj.get('properties', {})
                            if isinstance(props, list):
                                props_dict = {}
                                for p in props:
                                    props_dict[p['name']] = p.get('value', 0)
                                props = props_dict
                            
                            transitions.append(TransitionZone(
                                obj['x'], obj['y'],
                                obj.get('width', 50) + 10,
                                obj.get('height', 100),
                                props.get('target_location', 'location_2'),
                                props.get('target_x', 700),
                                props.get('target_y', 230)
                            ))
            
            if not transitions:
                transitions = [TransitionZone(0, 220, 20, 130, "location_2", 650, 230)]
            
            lake = Location(
                name="Озеро", bg_color=(135, 206, 235), walls=collision_walls,
                zones=[], npcs=[], entities=[], width=map_width, height=map_height
            )
            lake.map_data = map_data
            lake.transitions = transitions
            locations["location_3"] = lake
            print(f"✅ Озеро загружено! Стены: {len(collision_walls)}")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки озера: {e}")
            lake = LakeBuilder()
            locations["location_3"] = lake.build()
        
        print("\n" + "="*50)
        print(f"ГОТОВО! Доступно локаций: {list(locations.keys())}")
        print("="*50 + "\n")
        
        return locations
    
    def get_nearby_item(self):
        """Возвращает предмет, рядом с которым находится игрок"""
        player_rect = self.player.get_rect()
        current_items = self.items.get(self.current_location_id, [])
        
        for item in current_items:
            if not item.picked_up and item.check_interaction(player_rect):
                return item
        return None
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Обработка клавиши B для инвентаря
            if self.inventory.handle_key_event(event):
                continue
            
            # Обработка кликов по инвентарю (кнопка и крестик)
            if self.inventory.handle_event(event):
                continue
            
            if event.type == pygame.KEYDOWN:
                # Закрытие на ESC
                if event.key == pygame.K_ESCAPE:
                    if self.dialog_system.active:
                        self.dialog_system.end_dialog()
                    elif self.inventory.open:
                        self.inventory.close()
                    elif self.pickup_menu.active:
                        self.pickup_menu.close()
                
                # Диалоги (SPACE - следующая реплика)
                if event.key == pygame.K_SPACE:
                    if self.dialog_system.active:
                        self.dialog_system.next_line()
                
                # Взаимодействие с предметами/NPC (E)
                if event.key == pygame.K_e:
                    if not self.dialog_system.active and not self.inventory.open:
                        if self.pickup_menu.active:
                            self.pickup_menu.close()
                        else:
                            player_rect = self.player.get_rect()
                            current_items = self.items.get(self.current_location_id, [])
                            
                            for item in current_items:
                                if item.check_interaction(player_rect):
                                    self.pickup_menu.open(item)
                                    break
                
                 # ПОДТВЕРЖДЕНИЕ ПОДБОРА (Q)
                if event.key == pygame.K_q:
                    if self.pickup_menu.active:
                        if self.pickup_menu.confirm():
                            # Сохраняем имя ДО закрытия меню
                            item_name = self.pickup_menu.current_item.name if self.pickup_menu.current_item else None
                            
                            if item_name:
                                # 🔧 Передаём только имя (inventory сам создаст объект)
                                self.inventory.add_item(item_name)
                            
                            # Закрываем меню
                            self.pickup_menu.close()
                
                # Отмена подбора (R)
                if event.key == pygame.K_r:
                    if self.pickup_menu.active:
                        self.pickup_menu.close()   

    def update(self):
        # Обновляем инвентарь (для эффектов наведения)
        self.inventory.update()
        
        # Блокируем движение если открыто меню или инвентарь
        if self.pickup_menu.active or self.dialog_system.active or self.inventory.open:
            self.camera.update(self.player)
            self.dialog_system.update(self.dt)
            return
        
        keys = pygame.key.get_pressed()
        walls = self.current_location.get_walls()
        
        self.player.move(keys, walls, self.current_location.width, self.current_location.height)
        
        player_rect = self.player.get_rect()
        
        # Проверка переходов между локациями
        for transition in self.current_location.transitions:
            if transition.check_transition(player_rect):
                print(f"🚪 Переход! Цель: {transition.target_location}")
                self.change_location(transition.target_location, 
                                transition.target_x, 
                                transition.target_y)
                break
        
        self.camera.update(self.player)
        self.dialog_system.update(self.dt)
    
    def change_location(self, location_id, player_x, player_y):
        """Переход между локациями"""
        print(f"🔄 Переход в {location_id}")
        
        if location_id in self.locations:
            self.current_location_id = location_id
            self.current_location = self.locations[location_id]
            self.player.x = player_x
            self.player.y = player_y
            
            self.camera.change_size(self.current_location.width, self.current_location.height)
            
            print(f"✅ Переход в: {self.current_location.name}")
            print(f"   Размер: {self.current_location.width}x{self.current_location.height}")
            print(f"   Игрок на: ({player_x}, {player_y})")
        else:
            print(f"❌ Локация {location_id} не найдена!")
            print(f"   Доступно: {list(self.locations.keys())}")

    def draw_tiled_layer(self, layer_data, map_loader):
        """Рисует слой с кэшированием масштабированных тайлов"""
        layer_type = layer_data.get('type')
        
        if layer_type == 'group':
            for child_layer in layer_data.get('layers', []):
                self.draw_tiled_layer(child_layer, map_loader)
            return
        
        if layer_type != 'tilelayer' or not layer_data.get('visible', True):
            return
        
        if layer_data.get('name') == 'Collision':
            return
        
        map_width = self.current_location.map_data['width']
        tile_width = self.current_location.map_data['tilewidth']
        tile_height = self.current_location.map_data['tileheight']
        data = layer_data.get('data', [])
        scale = self.camera.scale
        
        if not data:
            return
        
        if not hasattr(map_loader, '_scaled_cache'):
            map_loader._scaled_cache = {}
        
        tw_s = tile_width * scale
        th_s = tile_height * scale
        
        for i, gid in enumerate(data):
            if gid == 0:
                continue
            
            tx = i % map_width
            ty = i // map_width
            
            screen_x = tx * tile_width * scale + self.camera.camera.x
            screen_y = ty * tile_height * scale + self.camera.camera.y
            
            # Отсекаем тайлы за пределами экрана
            if screen_x + tw_s < 0 or screen_x > WIDTH or screen_y + th_s < 0 or screen_y > HEIGHT:
                continue
            
            cache_key = (gid, scale)
            if cache_key not in map_loader._scaled_cache:
                orig_tile = map_loader.get_tile(gid)
                if orig_tile:
                    map_loader._scaled_cache[cache_key] = pygame.transform.scale(
                        orig_tile, (int(tw_s), int(th_s))
                    )
                else:
                    continue
            
            self.screen.blit(map_loader._scaled_cache[cache_key], (int(screen_x), int(screen_y)))

    def _draw_layer_by_name(self, layer_name, map_loader):
        """Отрисовка слоя по имени"""
        for layer in self.current_location.map_data['layers']:
            if layer.get('name') == layer_name and layer.get('visible', True):
                self.draw_tiled_layer(layer, map_loader)

    def draw(self):
        self.screen.fill(TEX_GRASS)
        
        if hasattr(self.current_location, 'map_data') and self.current_location.map_data:
            # Выбираем правильный загрузчик для текущей локации
            if self.current_location.name == "Деревня":
                current_loader = self.map_loader_village
            elif self.current_location.name == "Лес":
                current_loader = self.map_loader_forest
            elif self.current_location.name == "Озеро":
                current_loader = self.map_loader_lake
            else:
                current_loader = self.map_loader_village
            
            # Рисуем слои по порядку
            for layer_name in LAYER_RENDER_ORDER['background']:
                self._draw_layer_by_name(layer_name, current_loader)
            
            for layer_name in LAYER_RENDER_ORDER['middle_below']:
                self._draw_layer_by_name(layer_name, current_loader)
            
            # Рисуем игрока
            self.player.draw(self.screen, self.camera)
            
            for layer_name in LAYER_RENDER_ORDER['middle_above']:
                self._draw_layer_by_name(layer_name, current_loader)
            
            for layer_name in LAYER_RENDER_ORDER['foreground']:
                self._draw_layer_by_name(layer_name, current_loader)
        else:
            self.current_location.draw(self.screen, self.camera, self.player)
        
        # Рисуем переходы
        for transition in self.current_location.transitions:
            transition.draw(self.screen, self.camera)
        
        # Рисуем NPC
        for npc in self.current_location.npcs:
            npc.draw(self.screen, self.camera)
        
        # Рисуем зоны взаимодействия
        for zone in self.current_location.zones:
            zone.draw(self.screen, self.camera)
        
        # 🔧 Рисуем предметы на карте
        current_items = self.items.get(self.current_location_id, [])
        for item in current_items:
            if not item.picked_up:
                item.draw(self.screen, self.camera)
        
        # 🔧 Рисуем меню подбора
        self.pickup_menu.draw(self.screen)
        
        # Рисуем интерфейс
        self.draw_ui()
        self.dialog_system.draw(self.screen)
        
        # 🔧 Инвентарь рисуется ПОВЕРХ всего
        self.inventory.draw(self.screen)
        
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
        
        # Координаты игрока
        coords_text = small_font.render(
            f"X: {int(self.player.x)} Y: {int(self.player.y)}", 
            True, BLACK
        )
        self.screen.blit(coords_text, (10, 60))
        
        nearby_item = self.get_nearby_item()
        
        if self.pickup_menu.active:
            # Меню подбора открыто
            hint_text = small_font.render("Q - взять, R/ESC - отмена", True, BLACK)
            pygame.draw.rect(self.screen, WHITE, (10, HEIGHT - DIALOG_BOX_HEIGHT - 50, 350, 35))
            self.screen.blit(hint_text, (15, HEIGHT - DIALOG_BOX_HEIGHT - 43))
        
        elif self.dialog_system.active:
            # Диалог активен
            hint_text = small_font.render("SPACE - далее, ESC - закрыть", True, BLACK)
            pygame.draw.rect(self.screen, WHITE, (10, HEIGHT - DIALOG_BOX_HEIGHT - 50, 350, 35))
            self.screen.blit(hint_text, (15, HEIGHT - DIALOG_BOX_HEIGHT - 43))
        
        elif nearby_item:
            # Предмет рядом — показываем подсказку
            hint_text = font.render(f"Нажмите E, чтобы взять {nearby_item.name}", True, (255, 215, 0))
            
            text_width = hint_text.get_width() + 20
            text_height = 40
            hint_x = (WIDTH - text_width) // 2
            hint_y = HEIGHT - 100
            
            pygame.draw.rect(self.screen, (50, 50, 50), (hint_x - 2, hint_y - 2, text_width + 4, text_height + 4))
            pygame.draw.rect(self.screen, WHITE, (hint_x, hint_y, text_width, text_height))
            pygame.draw.rect(self.screen, BLACK, (hint_x, hint_y, text_width, text_height), 2)
            
            text_rect = hint_text.get_rect(center=(hint_x + text_width // 2, hint_y + text_height // 2))
            self.screen.blit(hint_text, text_rect)
        
        else:
            # Обычная подсказка управления
            #controls_text = small_font.render("WASD - движение, Shift - бег, E - взаимодействие, I - инвентарь", True, BLACK)
            #self.screen.blit(controls_text, (10, HEIGHT - 200))
            
            for zone in self.current_location.zones:
                if zone.active:
                    hint_text = font.render("Нажмите E для разговора", True, (0, 128, 0))
                    pygame.draw.rect(self.screen, WHITE, (10, HEIGHT - 240, 300, 40))
                    self.screen.blit(hint_text, (20, HEIGHT - 232))
    
    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()