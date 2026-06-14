import pygame
import json
import os
from wall import Wall

class MapLoader:
    def __init__(self):
        self.tilesets = {}
        self.tileset_list = []
        
    def load_tileset(self, tileset_data, map_dir):
        """Загружает тайлсет из JSON"""
        image_path = tileset_data['image']
        
        possible_paths = [
            os.path.join(map_dir, image_path),
            image_path,
            os.path.join('assets', 'tilesets', os.path.basename(image_path)),
            os.path.join('..', 'assets', 'tilesets', os.path.basename(image_path)),
        ]
        
        tile_width = tileset_data['tilewidth']
        tile_height = tileset_data['tileheight']
        first_gid = tileset_data['firstgid']
        columns = tileset_data.get('columns', 0)
        
        # Получаем количество тайлов
        if 'tilecount' in tileset_data:
            tile_count = tileset_data['tilecount']
        else:
            found_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    found_path = path
                    break
            if found_path:
                img = pygame.image.load(found_path)
                rows = img.get_height() // tile_height
                cols = img.get_width() // tile_width
                tile_count = rows * cols
            else:
                tile_count = 0
        
        found_path = None
        for path in possible_paths:
            if os.path.exists(path):
                found_path = path
                break
        
        if not found_path:
            print(f"❌ Файл тайлсета не найден: {image_path}")
            return
        
        try:
            image = pygame.image.load(found_path).convert_alpha()
            print(f"✅ Загружен тайлсет: {os.path.basename(found_path)} (firstGID: {first_gid})")
            
            tiles = []
            rows = (tile_count + columns - 1) // columns if columns > 0 else 0
            
            for row in range(rows):
                for col in range(columns):
                    x = col * tile_width
                    y = row * tile_height
                    
                    if (x + tile_width <= image.get_width() and 
                        y + tile_height <= image.get_height() and
                        len(tiles) < tile_count):
                        tile = image.subsurface(x, y, tile_width, tile_height)
                        tiles.append(tile)
            
            self.tilesets[first_gid] = {
                'tiles': tiles,
                'width': tile_width,
                'height': tile_height,
                'first_gid': first_gid,
                'columns': columns,
                'tilecount': tile_count
            }
            
            self.tileset_list = sorted(self.tilesets.items())
            
            print(f"   Нарезано {len(tiles)} тайлов (GID {first_gid}-{first_gid + len(tiles) - 1})")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки {found_path}: {e}")
    
    def get_tile(self, gid):
        """Получает тайл по его gid"""
        if gid == 0:
            return None
        
        original_gid = gid
        gid = gid & 0x0FFFFFFF  # Убираем флаги
        
        selected_tileset = None
        for first_gid, tileset in self.tileset_list:
            if gid >= first_gid:
                selected_tileset = tileset
            else:
                break
        
        if selected_tileset:
            tile_index = gid - selected_tileset['first_gid']
            if 0 <= tile_index < len(selected_tileset['tiles']):
                return selected_tileset['tiles'][tile_index]
        
        # Возвращаем заглушку
        surface = pygame.Surface((16, 16))
        surface.fill((255, 0, 255))
        return surface
    
    def load_map(self, map_path):
        """Загружает карту из JSON/TMJ"""
        print(f"🗺️  Загрузка карты: {map_path}")
        
        map_dir = os.path.dirname(os.path.abspath(map_path))
        print(f"   Директория карты: {map_dir}")
        
        with open(map_path, 'r', encoding='utf-8') as f:
            map_data = json.load(f)
        
        print(f"   Размер: {map_data['width']}x{map_data['height']} тайлов")
        print(f"   Размер тайла: {map_data['tilewidth']}x{map_data['tileheight']}")
        print(f"   Тайлсетов: {len(map_data['tilesets'])}")
        
        self.tilesets = {}
        self.tileset_list = []
        
        for tileset in map_data['tilesets']:
            print(f"   Загрузка тайлсета: {tileset.get('name', 'unknown')}")
            self.load_tileset(tileset, map_dir)
        
        print(f"   Всего загружено тайлсетов: {len(self.tilesets)}")
        
        print(f"   Слоёв в карте: {len(map_data['layers'])}")
        for layer in map_data['layers']:
            layer_type = layer.get('type', 'unknown')
            layer_name = layer.get('name', 'unnamed')
            print(f"      - {layer_name} (тип: {layer_type})")
        
        print(f"✅ Карта загружена успешно!")
        return map_data
    
    def load_collision_layer(self, layer_data, scale=1):
        """Загружает хитбоксы из слоя объектов - БЕЗ СМЕЩЕНИЯ"""
        walls = []
        
        # Убираем смещение - теперь 0
        Y_OFFSET = 0  # ← ИСПРАВЛЕНО: убираем смещение
        
        for obj in layer_data.get('objects', []):
            x = obj['x']
            y = obj['y'] + Y_OFFSET
            width = obj.get('width', 0)
            height = obj.get('height', 0)
            
            if width > 0 and height > 0:
                walls.append(Wall(x, y, width, height))
        
        print(f"   ✅ Загружено {len(walls)} хитбоксов")
        return walls

    def load_collision_from_tiles(self, layer, map_data, scale=1):
        """Загружает хитбоксы из тайлового слоя коллизий - БЕЗ СМЕЩЕНИЯ"""
        collision_walls = []
        tile_width = map_data['tilewidth']
        tile_height = map_data['tileheight']
        map_width = map_data['width']
        
        data = layer.get('data', [])
        
        # Убираем смещение
        Y_OFFSET = 0  # ← ИСПРАВЛЕНО: убираем смещение
        
        for i, gid in enumerate(data):
            if gid != 0:
                x = (i % map_width) * tile_width
                y = (i // map_width) * tile_height + Y_OFFSET
                
                collision_walls.append(Wall(x, y, tile_width, tile_height))
        
        print(f"   ✅ Загружено {len(collision_walls)} хитбоксов из тайлового слоя")
        return collision_walls