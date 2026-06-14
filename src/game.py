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
from quest_system import QuestSystem, QuestState

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Adventure Game - Учебный Проект")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Система диалогов
        self.dialog_system = DialogSystem()
        
        # Инвентарь
        self.inventory = Inventory()

        # Система квестов
        self.quest_system = QuestSystem()
        self.quest_notification = None
        self.quest_notification_timer = 0
        
        # Меню подбора предметов
        self.pickup_menu = PickupMenu()
        
        # Загрузчики карт
        self.map_loader_village = MapLoader()
        self.map_loader_forest = MapLoader()
        self.map_loader_lake = MapLoader()
        
        # Камера
        self.camera = Camera(1000, 1000)
        
        # Создаем локации
        self.locations = self.create_locations()
        self.current_location_id = "location_1" 
        self.current_location = self.locations[self.current_location_id]
        
        # Игрок (Котёнок)
        self.player = Player(200, 400)
        
        # Обновляем камеру
        self.camera.change_size(self.current_location.width, self.current_location.height)
        self.camera.update(self.player)
        
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
            "location_3": [],
        }

        # NPC на локациях (с координатами из задания)
        self._setup_npcs()
                        
    def _setup_npcs(self):
        """Настраивает NPC на локациях с указанными координатами"""
        # Деревня: Продавец Сасаныч (NPC_1) - x=110-140, y=168-178
        if "location_1" in self.locations:
            self.locations["location_1"].npcs.append(NPC(110, 168, "NPC_1", (139, 69, 19)))
            self.locations["location_1"].zones.append(InteractionZone(80, 140, 80, 80, "NPC_1"))
        
        # Лес: Садовод Мишаня (NPC_2) - x=255-300, y=360-400
        if "location_2" in self.locations:
            self.locations["location_2"].npcs.append(NPC(255, 360, "NPC_2", (34, 139, 34)))
            self.locations["location_2"].zones.append(InteractionZone(225, 330, 90, 90, "NPC_2"))
        
        # Озеро: Старичёк Додошка (NPC_3) - x=100-135, y=215-240
        if "location_3" in self.locations:
            self.locations["location_3"].npcs.append(NPC(100, 215, "NPC_3", (128, 128, 128)))
            self.locations["location_3"].zones.append(InteractionZone(70, 185, 80, 80, "NPC_3"))
    
    def create_locations(self):
        """Создание всех локаций игры"""
        locations = {}
        
        # === ЛОКАЦИЯ 1: Деревня ===
        print("\n" + "="*50 + "\nЗАГРУЗКА ДЕРЕВНИ\n" + "="*50)
        
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
                                props_dict = {p['name']: p.get('value', 0) for p in props}
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
        print("\n" + "="*50 + "\nЗАГРУЗКА ЛЕСА\n" + "="*50)
        
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
                                props_dict = {p['name']: p.get('value', 0) for p in props}
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
        print("\n" + "="*50 + "\nЗАГРУЗКА ОЗЕРА\n" + "="*50)
        
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
                                props_dict = {p['name']: p.get('value', 0) for p in props}
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
        
        print("\n" + "="*50 + f"\nГОТОВО! Доступно локаций: {list(locations.keys())}\n" + "="*50)
        return locations
    
    def get_nearby_item(self):
        """Возвращает предмет, рядом с которым находится игрок"""
        player_rect = self.player.get_rect()
        current_items = self.items.get(self.current_location_id, [])
        for item in current_items:
            if not item.picked_up and item.check_interaction(player_rect):
                return item
        return None
    
    def _start_quests_if_needed(self):
        """🔧 Запускает квесты при первом разговоре с Сасанычем"""
        # Проверяем, начаты ли уже квесты
        any_started = any(
            quest.state.name == "IN_PROGRESS" or quest.state.name == "COMPLETED" or quest.state.name == "CLAIMED"
            for quest in self.quest_system.quests.values()
        )
        
        if not any_started:
            print("🎯 Запуск всех трёх квестов от Сасаныча...")
            self.quest_system.start_quest("quest_herbs")
            self.quest_system.start_quest("quest_potion")
            self.quest_system.start_quest("quest_map")
            print("✅ Квесты запущены!")
    
    def _get_dialog_key_for_npc(self, npc_id):
        """Определяет ключ диалога на основе состояния квестов"""
        if npc_id == "NPC_1":  # Сасаныч
            # 🔧 Запускаем квесты при первом разговоре
            self._start_quests_if_needed()
            
            claimed = self.quest_system.get_claimed_quests()
            completed = self.quest_system.get_completed_quests()
            active = self.quest_system.get_active_quests()
            
            if len(claimed) >= 3:
                return "after_reward"
            elif self.quest_system.all_quests_completed():
                return "all_quests_completed"
            elif len(completed) >= 3:
                return "all_quests_completed"
            elif len(active) >= 1:
                for quest in active:
                    if quest.quest_id == "quest_herbs" and quest.collected < quest.target_count:
                        return "quest_herbs_active"
                    elif quest.quest_id == "quest_potion" and quest.collected < quest.target_count:
                        return "quest_potion_active"
                    elif quest.quest_id == "quest_map" and quest.collected < quest.target_count:
                        return "quest_map_active"
                return "quest_offer"
            else:
                return "quest_offer"
        
        elif npc_id == "NPC_2":  # Мишаня
            herbs_quest = self.quest_system.get_quest_state("quest_herbs")
            if herbs_quest == QuestState.COMPLETED:
                return "quest_herbs_delivered"
            elif herbs_quest == QuestState.CLAIMED:
                return "after_quest"
            elif herbs_quest == QuestState.IN_PROGRESS:
                return "quest_herbs_in_progress"
            else:
                return "greeting"
        
        elif npc_id == "NPC_3":  # Додошка
            potion_quest = self.quest_system.get_quest_state("quest_potion")
            if potion_quest == QuestState.COMPLETED:
                return "quest_potion_delivered"
            elif potion_quest == QuestState.CLAIMED:
                return "after_quest"
            elif potion_quest == QuestState.IN_PROGRESS:
                return "quest_potion_in_progress"
            else:
                return "greeting"
        
        elif npc_id == "NPC_4":  # Рыбак
            if self.quest_system.all_quests_completed():
                return "after_all_quests"
            else:
                return "greeting"
        
        return "greeting"
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Обработка кликов по кнопкам диалога (ПРИОРИТЕТ)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.dialog_system.active:
                    if self.dialog_system.check_button_click(event.pos):
                        continue
                if self.inventory.handle_event(event):
                    continue
            
            # Обработка клавиши B для инвентаря
            if self.inventory.handle_key_event(event):
                continue
            
            if event.type == pygame.KEYDOWN:
                # Закрытие на ESC (инвентарь, диалог, меню подбора)
                if event.key == pygame.K_ESCAPE:
                    if self.dialog_system.active:
                        self.dialog_system.end_dialog()
                        # Проверяем выдачу награды после закрытия диалога
                        self._give_reward_if_all_quests_completed()
                    elif self.inventory.open:
                        self.inventory.close()
                    elif self.pickup_menu.active:
                        self.pickup_menu.close()
                
                # Диалоги (SPACE - следующая реплика)
                if event.key == pygame.K_SPACE:
                    if self.dialog_system.active:
                        result = self.dialog_system.next_line()
                        # Если диалог только что завершился
                        if not self.dialog_system.active:
                            self._give_reward_if_all_quests_completed()
                
                # Взаимодействие с предметами/NPC (E)
                if event.key == pygame.K_e:
                    if not self.dialog_system.active and not self.inventory.open:
                        if self.pickup_menu.active:
                            self.pickup_menu.close()
                        else:
                            # Сначала проверяем NPC — диалог + передача предмета
                            for zone in self.current_location.zones:
                                if zone.active:
                                    dialog_key = self._get_dialog_key_for_npc(zone.npc_id)
                                    self.dialog_system.start_dialog(
                                        zone.npc_id, 
                                        dialog_key,
                                        self.inventory,
                                        self.quest_system
                                    )
                                    break
                            
                            # Затем проверяем предметы на земле
                            player_rect = self.player.get_rect()
                            current_items = self.items.get(self.current_location_id, [])
                            for item in current_items:
                                if item.check_interaction(player_rect):
                                    self.pickup_menu.open(item)
                                    break
                
                # Подтверждение подбора предмета (Q)
                if event.key == pygame.K_q:
                    if self.pickup_menu.active:
                        if self.pickup_menu.confirm():
                            item_name = self.pickup_menu.current_item.name if self.pickup_menu.current_item else None
                            if item_name:
                                # Просто добавляем в инвентарь (БЕЗ обновления квестов!)
                                self.inventory.add_item(item_name)
                                print(f" Подобрano: {item_name}")
                            self.pickup_menu.close()
                
                # Отмена подбора предмета (R)
                if event.key == pygame.K_r:
                    if self.pickup_menu.active:
                        self.pickup_menu.close()
    
    def update(self):
        self.inventory.update()
        
        if self.quest_notification_timer > 0:
            self.quest_notification_timer -= self.dt
            if self.quest_notification_timer <= 0:
                self.quest_notification = None
        
        if self.pickup_menu.active or self.dialog_system.active or self.inventory.open:
            self.camera.update(self.player)
            self.dialog_system.update(self.dt)
            return
        
        keys = pygame.key.get_pressed()
        walls = self.current_location.get_walls()
        self.player.move(keys, walls, self.current_location.width, self.current_location.height)
        
        player_rect = self.player.get_rect()
        # 🔧 ОБНОВЛЕНИЕ СОСТОЯНИЯ ЗОН (для подсказки "E")
        for zone in self.current_location.zones:
            zone.check_interaction(player_rect)
        
        for transition in self.current_location.transitions:
            if transition.check_transition(player_rect):
                self.change_location(transition.target_location, transition.target_x, transition.target_y)
                break
        
        self.camera.update(self.player)
        self.dialog_system.update(self.dt)
    
    def change_location(self, location_id, player_x, player_y):
        if location_id in self.locations:
            self.current_location_id = location_id
            self.current_location = self.locations[location_id]
            self.player.x = player_x
            self.player.y = player_y
            self.camera.change_size(self.current_location.width, self.current_location.height)
    
    def draw_tiled_layer(self, layer_data, map_loader):
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
            
            if screen_x + tw_s < 0 or screen_x > WIDTH or screen_y + th_s < 0 or screen_y > HEIGHT:
                continue
            
            cache_key = (gid, scale)
            if cache_key not in map_loader._scaled_cache:
                orig_tile = map_loader.get_tile(gid)
                if orig_tile:
                    map_loader._scaled_cache[cache_key] = pygame.transform.scale(orig_tile, (int(tw_s), int(th_s)))
                else:
                    continue
            self.screen.blit(map_loader._scaled_cache[cache_key], (int(screen_x), int(screen_y)))
    
    def _draw_layer_by_name(self, layer_name, map_loader):
        for layer in self.current_location.map_data['layers']:
            if layer.get('name') == layer_name and layer.get('visible', True):
                self.draw_tiled_layer(layer, map_loader)
    
    def draw(self):
        self.screen.fill(TEX_GRASS)
        
        if hasattr(self.current_location, 'map_data') and self.current_location.map_data:
            if self.current_location.name == "Деревня":
                current_loader = self.map_loader_village
            elif self.current_location.name == "Лес":
                current_loader = self.map_loader_forest
            elif self.current_location.name == "Озеро":
                current_loader = self.map_loader_lake
            else:
                current_loader = self.map_loader_village
            
            for layer_name in LAYER_RENDER_ORDER['background']:
                self._draw_layer_by_name(layer_name, current_loader)
            for layer_name in LAYER_RENDER_ORDER['middle_below']:
                self._draw_layer_by_name(layer_name, current_loader)
            
            self.player.draw(self.screen, self.camera)
            
            for layer_name in LAYER_RENDER_ORDER['middle_above']:
                self._draw_layer_by_name(layer_name, current_loader)
            for layer_name in LAYER_RENDER_ORDER['foreground']:
                self._draw_layer_by_name(layer_name, current_loader)
        else:
            self.current_location.draw(self.screen, self.camera, self.player)
        
        for transition in self.current_location.transitions:
            transition.draw(self.screen, self.camera)
        for npc in self.current_location.npcs:
            npc.draw(self.screen, self.camera)
        for zone in self.current_location.zones:
            zone.draw(self.screen, self.camera)
        
        current_items = self.items.get(self.current_location_id, [])
        for item in current_items:
            if not item.picked_up:
                item.draw(self.screen, self.camera)
        
        self.pickup_menu.draw(self.screen)
        self.draw_ui()
        self.dialog_system.draw(self.screen)
        self.inventory.draw(self.screen)
        
        pygame.display.flip()
    
    def draw_ui(self):
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 28)
        
        # Название локации
        location_text = font.render(f"Локация: {self.current_location.name}", True, BLACK)
        pygame.draw.rect(self.screen, WHITE, (10, 10, 250, 40))
        pygame.draw.rect(self.screen, BLACK, (10, 10, 250, 40), 2)
        self.screen.blit(location_text, (20, 18))
        
        # Координаты
        coords_text = small_font.render(f"X: {int(self.player.x)} Y: {int(self.player.y)}", True, BLACK)
        self.screen.blit(coords_text, (10, 60))
        
        # Активные квесты
        active_quests = self.quest_system.get_active_quests()
        if active_quests:
            quest_y = 100
            for quest in active_quests[:3]:
                quest_text = small_font.render(f"📜 {quest.name}: {quest.get_progress_text()}", True, (139, 69, 19))
                pygame.draw.rect(self.screen, (255, 240, 220), (10, quest_y, 280, 25))
                self.screen.blit(quest_text, (15, quest_y + 5))
                quest_y += 30
        
        # Уведомление о квесте
        if self.quest_notification:
            notify_text = font.render(self.quest_notification, True, (0, 128, 0))
            notify_rect = notify_text.get_rect(center=(WIDTH // 2, 100))
            pygame.draw.rect(self.screen, (240, 255, 240), 
                           (notify_rect.left - 10, notify_rect.top - 5, 
                            notify_rect.width + 20, notify_rect.height + 10))
            self.screen.blit(notify_text, notify_rect)
        
        nearby_item = self.get_nearby_item()
        
        if self.pickup_menu.active:
            hint_text = small_font.render("Q - взять, R/ESC - отмена", True, BLACK)
            pygame.draw.rect(self.screen, WHITE, (10, HEIGHT - DIALOG_BOX_HEIGHT - 50, 350, 35))
            self.screen.blit(hint_text, (15, HEIGHT - DIALOG_BOX_HEIGHT - 43))
        elif self.dialog_system.active:
            hint_text = small_font.render("SPACE - далее, ESC - закрыть", True, BLACK)
            pygame.draw.rect(self.screen, WHITE, (10, HEIGHT - DIALOG_BOX_HEIGHT - 50, 350, 35))
            self.screen.blit(hint_text, (15, HEIGHT - DIALOG_BOX_HEIGHT - 43))
        elif nearby_item:
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
            for zone in self.current_location.zones:
                if zone.active:
                    hint_text = font.render("Нажмите E для разговора", True, (0, 128, 0))
                    # 🔧 УВЕЛИЧЕНА ШИРИНА ФОНА
                    text_width = hint_text.get_width() + 40
                    text_height = 40
                    hint_x = (WIDTH - text_width) // 2
                    hint_y = HEIGHT - 240
                    pygame.draw.rect(self.screen, WHITE, (hint_x, hint_y, text_width, text_height))
                    pygame.draw.rect(self.screen, BLACK, (hint_x, hint_y, text_width, text_height), 2)
                    text_rect = hint_text.get_rect(center=(hint_x + text_width // 2, hint_y + text_height // 2))
                    self.screen.blit(hint_text, text_rect)
    
    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    def _give_reward_if_all_quests_completed(self):
        """🔧 Выдаёт рыбу после завершения всех квестов"""
        # Проверяем, все ли квесты завершены и награда ещё не выдана
        if self.quest_system.all_quests_completed():
            # Проверяем, не выдана ли уже награда
            claimed_quests = self.quest_system.get_claimed_quests()
            if len(claimed_quests) >= 3:
                # Проверяем, нет ли уже рыбы в инвентаре
                has_fish = any(item.name == "Рыба" for item in self.inventory.items)
                
                if not has_fish:
                    print("🎁 Все квесты выполнены! Выдаю награду...")
                    self.inventory.add_item("Рыба")
                    self.quest_notification = "🎉 Награда: 🐟 РЫБА! 🐟"
                    self.quest_notification_timer = 5.0
                    print("✅ Рыба добавлена в инвентарь!")