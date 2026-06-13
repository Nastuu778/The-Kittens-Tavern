import pygame
import random
from settings import *
from location import Location, TransitionZone
from wall import Wall
from npc import NPC
from zone import InteractionZone
from entities import Path, Tree  # Импортируем новые сущности

class LocationBuilder:
    """Базовый класс для создания локаций"""
    
    def __init__(self):
        self.walls = []
        self.zones = []
        self.npcs = []
        self.transitions = []
        self.entities = []  # Новые сущности
        self.name = ""
        self.bg_color = WHITE
        self.width = 2000
        self.height = 1500
    
    def build(self):
        """Создаёт и возвращает локацию"""
        location = Location(
            name=self.name,
            bg_color=self.bg_color,
            walls=self.walls,
            zones=self.zones,
            npcs=self.npcs,
            entities=self.entities,  # Передаём сущности
            width=self.width,
            height=self.height
        )
        location.transitions = self.transitions
        return location


class VillageBuilder(LocationBuilder):
    """Строитель деревни"""
    
    def __init__(self):
        super().__init__()
        self.name = "Деревня"
        self.bg_color = TEX_GRASS
        self.width = 1500
        self.height = 1000
        self._build_village()
    
    def _build_village(self):
        """Добавляем объекты деревни"""
        # Дороги (можно ходить, рисуется под игроком)
        self.entities.append(Path(0, 650, 2000, 100))
        self.entities.append(Path(400, 200, 60, 450))
        
        # Дома (обычные стены)
        self.walls.append(Wall(250, 50, 200, 150, color=TEX_WOOD_WALL))
        self.walls.append(Wall(240, 40, 220, 20, color=TEX_ROOF))
        
        # Деревья (ствол блокирует, крона нет, игрок под кроной)
        self.entities.append(Tree(100, 100))
        self.entities.append(Tree(600, 200))
        self.entities.append(Tree(1200, 150))
        self.entities.append(Tree(1700, 300))
        
        # NPC
        self.npcs.append(NPC(320, 100, "NPC_1", (139, 69, 19)))
        self.zones.append(InteractionZone(320, 100, 60, 60, "NPC_1"))
        
        # Переходы
        self.transitions.append(
            TransitionZone(1950, 650, 50, 100, "location_2", 50, 650)
        )


class ForestBuilder(LocationBuilder):
    """Строитель леса"""
    
    def __init__(self):
        super().__init__()
        self.name = "Лес"
        self.bg_color = (34, 139, 34)
        self.width = 1200
        self.height = 800
        self._build_forest()
    
    def _build_forest(self):
        """Добавляем объекты леса"""
        # Много деревьев
        for i in range(20):
            x = random.randint(50, self.width - 100)
            y = random.randint(50, self.height - 100)
            self.entities.append(Tree(x, y))
        
        # Переходы
        self.transitions.append(
            TransitionZone(0, 650, 50, 100, "location_1", 1900, 650)
        )
        self.transitions.append(
            TransitionZone(1150, 400, 50, 100, "location_3", 50, 200)
        )


class LakeBuilder(LocationBuilder):
    """Строитель озера"""
    
    def __init__(self):
        super().__init__()
        self.name = "Озеро"
        self.bg_color = (135, 206, 235)
        self.width = 500
        self.height = 400
        self._build_lake()
    
    def _build_lake(self):
        """Добавляем объекты озера"""
        # Скалы (обычные стены)
        self.walls.append(Wall(100, 100, 80, 80, color=TEX_STONE))
        self.walls.append(Wall(300, 200, 100, 60, color=TEX_STONE))
        
        # NPC
        self.npcs.append(NPC(200, 150, "NPC_1", (0, 100, 200)))
        self.zones.append(InteractionZone(200, 150, 40, 40, "NPC_1"))
        
        # Переход
        self.transitions.append(
            TransitionZone(0, 200, 50, 100, "location_2", 1100, 400)
        )