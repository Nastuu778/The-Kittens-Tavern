import pygame
import json
import os
from wall import Wall

class MapLoader:
    def __init__(self):
        self.tilesets = {}
        
    def load_tileset(self, tileset_data, map_dir):
        """Загружает тайлсет из JSON"""
        image_path = tileset_data['image']
        
        possible_paths = [
            os.path.join(map_dir, image_path),
            image_path,
            os.path.join('assets', 'tilesets', os.path.basename(image_path)),
        ]
        
        tile_width = tileset_data['tilewidth']
        tile_height = tileset_data['tileheight']
        first_gid = tileset_data['firstgid']
        columns = tileset_data['columns']
        
        found_path = None
        for path in possible_paths:
            if os.path.exists(path):
                found_path = path
                break
        
        if not found_path:
            print(f"❌ Файл не найден: {image_path}")
            return
        
        try:
            image = pygame.image.load(found_path).convert_alpha()
            print(f"✅ Загружен тайлсет: {os.path.basename(found_path)}")
            
            tiles = []
            tile_count = tileset_data['tilecount']
            rows = (tile_count + columns - 1) // columns
            
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
                'columns': columns
            }
            print(f"   Нарезано {len(tiles)} тайлов (GID {first_gid}-{first_gid+len(tiles)-1})")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки {found_path}: {e}")
    
    def get_tile(self, gid):
        """Получает тайл по его gid"""
        if gid == 0:
            return None
            
        matching_gid = None
        for first_gid in self.tilesets.keys():
            if gid >= first_gid:
                if matching_gid is None or first_gid > matching_gid:
                    matching_gid = first_gid
        
        if matching_gid is not None:
            tileset = self.tilesets[matching_gid]
            tile_index = gid - matching_gid
            if 0 <= tile_index < len(tileset['tiles']):
                return tileset['tiles'][tile_index]
        
        print(f"⚠️  Тайл GID {gid} не найден")
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
        
        for tileset in map_data['tilesets']:
            print(f"   Загрузка тайлсета: {tileset['name']}")
            self.load_tileset(tileset, map_dir)
        
        # 🔍 ОТЛАДКА: выводим все слои
        print(f"   Слоёв в карте: {len(map_data['layers'])}")
        for layer in map_data['layers']:
            print(f"      - {layer.get('name')} (тип: {layer.get('type')})")
        
        print(f"✅ Карта загружена успешно!")
        return map_data
    
    def load_collision_layer(self, layer_data, scale=1):
        """Загружает хитбоксы из слоя объектов"""
        walls = []
        
        for obj in layer_data.get('objects', []):
            x = obj['x'] / scale
            y = obj['y'] / scale
            width = obj.get('width', 0) / scale
            height = obj.get('height', 0) / scale
            
            if width > 0 and height > 0:
                walls.append(Wall(x, y, width, height))
        
        print(f"   ✅ Загружено {len(walls)} хитбоксов из слоя '{layer_data.get('name')}'")
        return walls

    # Этот метод должен быть на том же уровне отступа, что и load_collision_layer
    def load_collision_from_tiles(self, layer_data, map_data, scale=1):
        """Загружает хитбоксы из ТАЙЛОВОГО слоя"""
        walls = []
        
        map_width = map_data['width']
        tile_width = map_data['tilewidth']
        tile_height = map_data['tileheight']
        data = layer_data['data']
        
        for i, gid in enumerate(data):
            if gid == 0:
                continue
            
            x = (i % map_width) * tile_width / scale
            y = (i // map_width) * tile_height / scale
            
            walls.append(Wall(x, y, tile_width / scale, tile_height / scale))
        
        print(f"   ✅ Загружено {len(walls)} хитбоксов из тайлового слоя")
        return walls