import pygame
from settings import *
from entities import Tree  # <-- ДОБАВЬ ЭТУ СТРОКУ!

class Location:
    def __init__(self, name, bg_color, walls=[], zones=[], npcs=[], entities=[], width=2000, height=1500):
        self.name = name
        self.bg_color = bg_color
        self.walls = walls
        self.zones = zones
        self.npcs = npcs
        self.entities = entities  # Новые сущности (деревья, дороги и т.д.)
        self.width = width
        self.height = height
        
    def draw(self, screen, camera, player):
        """Отрисовка с сортировкой по Y (z-ordering)"""
        # Рисуем фон
        screen.fill(self.bg_color)
        
        # РИСУЕМ ДОРОГИ (как фон, под всем)
        for entity in self.entities:
            if hasattr(entity, 'is_background') and entity.is_background:
                entity.draw(screen, camera)
        
        # Собираем все объекты для сортировки (БЕЗ дорог)
        render_list = []
        
        # Добавляем стены
        for wall in self.walls:
            render_list.append((wall.y + wall.height, wall))
        
        # Добавляем сущности (КРОМЕ фоновых)
        for entity in self.entities:
            if not (hasattr(entity, 'is_background') and entity.is_background):
                render_list.append((entity.y + entity.height, entity))
        
        # Добавляем NPC
        for npc in self.npcs:
            render_list.append((npc.y + npc.height, npc))
        
        # Добавляем игрока (БЕЗ проверки невидимости)
        render_list.append((player.y + player.height, player))
        
        # Сортируем по Y (от дальнего к ближнему)
        render_list.sort(key=lambda x: x[0])
        
        # Рисуем в правильном порядке
        for _, obj in render_list:
            if hasattr(obj, 'draw'):
                obj.draw(screen, camera)
        
        # Рисуем зоны (всегда поверх всего)
        for zone in self.zones:
            zone.draw(screen, camera)
        
    def get_walls(self):
        """Возвращает все объекты с коллизией"""
        collision_objects = []
        
        # Обычные стены
        collision_objects.extend(self.walls)
        
        # Сущности с коллизией (например, стволы деревьев)
        for entity in self.entities:
            if hasattr(entity, 'get_collision_rect') and entity.get_collision_rect() is not None:
                collision_objects.append(entity)
        
        return collision_objects
    
    def get_zones(self):
        return self.zones


class TransitionZone:
    """Зона перехода между локациями"""
    def __init__(self, x, y, width, height, target_location, target_x, target_y, color=(100, 100, 255)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.target_location = target_location
        self.target_x = target_x
        self.target_y = target_y
        self.color = color
        self.active = False
        
    def check_transition(self, player_rect):
        """Проверяет, вошел ли игрок в зону перехода"""
        # Убедимся, что player_rect - это Rect
        if not isinstance(player_rect, pygame.Rect):
            player_rect = player_rect.get_rect()
            
        zone_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # 🔧 Отладка
        if player_rect.colliderect(zone_rect):
            print(f"✅ Пересечение! Игрок: {player_rect}, Зона: {zone_rect}")
            return True
        
        return False
    
    def draw(self, screen, camera):
        """Отрисовка зоны перехода"""
        # Применяем камеру
        screen_rect = pygame.Rect(
            self.x * camera.scale + camera.camera.x,
            self.y * camera.scale + camera.camera.y,
            self.width * camera.scale,
            self.height * camera.scale
        )
        
        # Рисуем полупрозрачную зону
        surface = pygame.Surface((screen_rect.width, screen_rect.height), pygame.SRCALPHA)
        surface.fill((100, 100, 255, 128))  # Синий с прозрачностью
        screen.blit(surface, screen_rect.topleft)
        
        # Рисуем границу
        pygame.draw.rect(screen, WHITE, screen_rect, 3)
        
        # Рисуем текст
        font = pygame.font.Font(None, 24)
        text = font.render("ВЫХОД", True, WHITE)
        text_rect = text.get_rect(center=screen_rect.center)
        screen.blit(text, text_rect)