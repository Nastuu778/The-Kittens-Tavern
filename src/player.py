import pygame
import os

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        
        # 🔧 ВИЗУАЛЬНЫЙ размер (для отрисовки)
        self.width = 32
        self.height = 32
        
        # 🔧 ХИТБОКС (для коллизий) — МЕНЬШЕ визуального размера
        # Можно настроить: например, 24x24 или 20x24
        self.hitbox_width = 20
        self.hitbox_height = 24
        
        # Смещение хитбокса относительно центра (чтобы он был по центру спрайта)
        self.hitbox_offset_x = (self.width - self.hitbox_width) // 2
        self.hitbox_offset_y = self.height - self.hitbox_height  # Хитбокс ближе к ногам
        
        # СИСТЕМА АНИМАЦИЙ
        self.animations = {}
        self.current_animation = 'idle'
        self.current_frame = 0
        self.animation_timer = 0
        
        # Загружаем анимацию ожидания (idle)
        print("\n🔍 Загрузка анимации idle...")
        self.animations['idle'] = self._load_animation('assets/cat_sprite', 8)
        print(f"✅ Загружено кадров idle: {len(self.animations['idle'])}\n")
        
        # Загружаем анимацию бега (sprint)
        print("🔍 Загрузка анимации sprint...")
        self.animations['sprint'] = self._load_animation('assets/cat_sprint', 10)
        print(f"✅ Загружено кадров sprint: {len(self.animations['sprint'])}\n")
        
        # Если ничего не загрузилось — создаём заглушку
        if not self.animations['idle']:
            print("⚠️  Создаём заглушку для idle")
            placeholder = pygame.Surface((self.width, self.height))
            placeholder.fill((0, 0, 255))
            self.animations['idle'] = [placeholder]
        
        if not self.animations['sprint']:
            print("⚠️  sprint не загружен, используем idle")
            self.animations['sprint'] = self.animations['idle'].copy()
        
        self.direction = 'down'
        
        # Rect для отрисовки (полный визуальный размер)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # 🔧 Rect для коллизий (уменьшенный)
        self.hitbox = pygame.Rect(
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.hitbox_width,
            self.hitbox_height
        )
    
    def _load_animation(self, folder_path, frames_count):
        """Загружает кадры анимации из папки"""
        frames = []
        
        for i in range(1, frames_count + 1):
            try:
                frame_path = f'{folder_path}/{i:02d}.png'
                
                if not os.path.exists(frame_path):
                    print(f"❌ Файл не найден: {frame_path}")
                    continue
                
                frame = pygame.image.load(frame_path).convert_alpha()
                print(f"   Загружен: {frame_path} (размер: {frame.get_size()})")
                
                frame = pygame.transform.scale(frame, (self.width, self.height))
                frames.append(frame)
                
            except Exception as e:
                print(f"❌ Ошибка загрузки {frame_path}: {e}")
        
        return frames
    
    def _update_hitbox(self):
        """Обновляет позицию хитбокса"""
        self.hitbox.x = self.x + self.hitbox_offset_x
        self.hitbox.y = self.y + self.hitbox_offset_y
    
    def move(self, keys, walls, map_width, map_height):
        dx = 0
        dy = 0
        is_moving = False
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.speed
            self.direction = 'up'
            is_moving = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.speed
            self.direction = 'down'
            is_moving = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
            self.direction = 'left'
            is_moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed
            self.direction = 'right'
            is_moving = True
        
        # 🔧 Движение по X — используем hitbox для коллизий
        self.x += dx
        self.rect.x = int(self.x)
        self._update_hitbox()
        for wall in walls:
            if self.hitbox.colliderect(wall.rect):
                if dx > 0:
                    self.x = wall.rect.left - self.hitbox_offset_x - self.hitbox_width
                elif dx < 0:
                    self.x = wall.rect.right - self.hitbox_offset_x
                self.rect.x = int(self.x)
                self._update_hitbox()
        
        # 🔧 Движение по Y — используем hitbox для коллизий
        self.y += dy
        self.rect.y = int(self.y)
        self._update_hitbox()
        for wall in walls:
            if self.hitbox.colliderect(wall.rect):
                if dy > 0:
                    self.y = wall.rect.top - self.hitbox_offset_y - self.hitbox_height
                elif dy < 0:
                    self.y = wall.rect.bottom - self.hitbox_offset_y
                self.rect.y = int(self.y)
                self._update_hitbox()
        
        # Границы карты
        self.x = max(0, min(self.x, map_width - self.width))
        self.y = max(0, min(self.y, map_height - self.height))
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self._update_hitbox()
        
        # Обновляем анимацию
        self.update_animation(is_moving)
    
    def update_animation(self, is_moving):
        """Обновляет кадр анимации"""
        new_animation = 'sprint' if is_moving else 'idle'
        
        if new_animation != self.current_animation:
            self.current_animation = new_animation
            self.current_frame = 0
            self.animation_timer = 0
        
        current_frames = self.animations.get(self.current_animation, self.animations['idle'])
        
        if not current_frames:
            return
        
        animation_speed = 3 if is_moving else 6
        
        self.animation_timer += 1
        
        if self.animation_timer >= animation_speed:
            self.current_frame = (self.current_frame + 1) % len(current_frames)
            self.animation_timer = 0
    
    def get_rect(self):
        """🔧 Возвращает ХИТБОКС (для коллизий и телепортов)"""
        return self.hitbox
    
    def draw(self, screen, camera):
        """Рисует игрока"""
        current_frames = self.animations.get(self.current_animation, self.animations['idle'])
        
        if not current_frames:
            return
        
        self.current_frame = min(self.current_frame, len(current_frames) - 1)
        current_image = current_frames[self.current_frame]
        
        # Отражение при движении влево
        if self.direction == 'left':
            current_image = pygame.transform.flip(current_image, True, False)
        
        screen_x = self.x * camera.scale + camera.camera.x
        screen_y = self.y * camera.scale + camera.camera.y
        
        if camera.scale != 1:
            current_image = pygame.transform.scale(
                current_image,
                (int(self.width * camera.scale), int(self.height * camera.scale))
            )
        
        screen.blit(current_image, (int(screen_x), int(screen_y)))