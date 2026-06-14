import pygame
import os
from settings import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED          # Обычная скорость (из settings.py)
        self.sprint_speed = PLAYER_SPEED * PLAYER_SPRINT_MULTIPLIER  # Скорость бега (можно настроить)
        self.current_speed = self.speed    # Текущая применяемая скорость
        
        # 🔧 ВИЗУАЛЬНЫЙ размер (для отрисовки)
        self.width = 32
        self.height = 32
        
        # 🔧 ХИТБОКС (для коллизий) — МЕНЬШЕ визуального размера
        self.hitbox_width = 20
        self.hitbox_height = 24
        
        # Смещение хитбокса относительно центра
        self.hitbox_offset_x = (self.width - self.hitbox_width) // 2
        self.hitbox_offset_y = self.height - self.hitbox_height
        
        # СИСТЕМА АНИМАЦИЙ
        self.animations = {}
        self.current_animation = 'idle'
        self.current_frame = 0
        self.animation_timer = 0
        self.is_sprinting = False  # Флаг: бежит ли игрок сейчас
        
        # Загружаем анимации
        print("\n🔍 Загрузка анимаций игрока...")
        self.animations['idle'] = self._load_animation('assets/cat_sprite', 8)
        self.animations['sprint'] = self._load_animation('assets/cat_sprint', 10)
        print(f"✅ idle: {len(self.animations['idle'])} кадров, sprint: {len(self.animations['sprint'])} кадров\n")
        
        # Заглушки, если спрайты не найдены
        if not self.animations['idle']:
            placeholder = pygame.Surface((self.width, self.height))
            placeholder.fill(BLUE)
            self.animations['idle'] = [placeholder]
        if not self.animations['sprint']:
            self.animations['sprint'] = self.animations['idle'].copy()
        
        self.direction = 'down'
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
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
                    continue
                frame = pygame.image.load(frame_path).convert_alpha()
                frame = pygame.transform.scale(frame, (self.width, self.height))
                frames.append(frame)
            except Exception as e:
                print(f"❌ Ошибка {frame_path}: {e}")
        return frames
    
    def _update_hitbox(self):
        """Обновляет позицию хитбокса"""
        self.hitbox.x = self.x + self.hitbox_offset_x
        self.hitbox.y = self.y + self.hitbox_offset_y
    
    def move(self, keys, walls, map_width, map_height):
        """Обработка движения с поддержкой спринта"""
        dx = 0
        dy = 0
        is_moving = False
        
        # 🔧 Проверка спринта: зажат Shift (левый или правый)
        self.is_sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        # Выбираем скорость в зависимости от спринта
        move_speed = self.sprint_speed if self.is_sprinting else self.speed
        
        # Обработка ввода
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -move_speed
            self.direction = 'up'
            is_moving = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = move_speed
            self.direction = 'down'
            is_moving = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -move_speed
            self.direction = 'left'
            is_moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = move_speed
            self.direction = 'right'
            is_moving = True
        
        # 🔧 Движение по X с коллизиями
        self.x += dx
        self.rect.x = int(self.x)
        self._update_hitbox()
        for wall in walls:
            if self.hitbox.colliderect(wall.get_rect()):
                if dx > 0:
                    self.x = wall.x - self.hitbox_offset_x - self.hitbox_width
                elif dx < 0:
                    self.x = wall.x + wall.width - self.hitbox_offset_x
                self.rect.x = int(self.x)
                self._update_hitbox()
        
        # 🔧 Движение по Y с коллизиями
        self.y += dy
        self.rect.y = int(self.y)
        self._update_hitbox()
        for wall in walls:
            if self.hitbox.colliderect(wall.get_rect()):
                if dy > 0:
                    self.y = wall.y - self.hitbox_offset_y - self.hitbox_height
                elif dy < 0:
                    self.y = wall.y + wall.height - self.hitbox_offset_y
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
        """Обновляет кадр анимации с учётом спринта"""
        # 🔧 Выбираем анимацию: спринт только если бежим И зажат Shift
        if is_moving and self.is_sprinting:
            new_animation = 'sprint'
        elif is_moving:
            new_animation = 'idle'  # Можно заменить на 'walk', если будет отдельная анимация
        else:
            new_animation = 'idle'
        
        if new_animation != self.current_animation:
            self.current_animation = new_animation
            self.current_frame = 0
            self.animation_timer = 0
        
        current_frames = self.animations.get(self.current_animation, self.animations['idle'])
        if not current_frames:
            return
        
        # 🔧 Спринт проигрывается быстрее
        animation_speed = 2 if self.is_sprinting else 4
        
        self.animation_timer += 1
        if self.animation_timer >= animation_speed:
            self.current_frame = (self.current_frame + 1) % len(current_frames)
            self.animation_timer = 0
    
    def get_rect(self):
        """Возвращает хитбокс для коллизий"""
        return self.hitbox
    
    def draw(self, screen, camera):
        """Рисует игрока с учётом камеры и масштаба"""
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
        
        # Масштабирование спрайта
        if camera.scale != 1:
            current_image = pygame.transform.scale(
                current_image,
                (int(self.width * camera.scale), int(self.height * camera.scale))
            )
        
        screen.blit(current_image, (int(screen_x), int(screen_y)))