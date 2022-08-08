###################
#
#  INITIALIZATIONS
#
###################

# set path to game source (images, sounds ect.)
from os import path
SRC_DIR = path.join(path.dirname(__file__), 'src')

# additional library for quit game
import sys

# import random integer
from random import randint

# init pygame and creating aliases
import pygame as PG
PG.init()
CLOCK = PG.time.Clock()
SPRITE = PG.sprite.Sprite

# init sounds
PG.mixer.init() # using sounds in game
explosion_sound = PG.mixer.Sound(path.join(SRC_DIR, 'explosion.ogg'))
explosion_sound.set_volume(0.2)
shut_sound = PG.mixer.Sound(path.join(SRC_DIR, 'shut.ogg'))
shut_sound.set_volume(0.2)
move_sound = PG.mixer.Sound(path.join(SRC_DIR, 'move.ogg'))
move_sound.set_volume(0.5)

PG.mixer.music.load(path.join(SRC_DIR, 't2.mp3'))
PG.mixer.music.set_volume(0.5)
PG.mixer.music.play()

# init sprite groups
ALL_SPRITES = PG.sprite.Group() # use for drawing sprites
SOLID_SPRITES = PG.sprite.Group() # use for check collisions
WALL_SPRITES = PG.sprite.Group() # use for check collisions with bullets
BORDER_SPRITES = PG.sprite.Group() # use for check collisions with bullets
MOVING_SPRITES = PG.sprite.Group() # use for update positions
ENEMIES_SPRITES = PG.sprite.Group() # use for check collisions player with enemies

ALL_BULLETS = PG.sprite.Group()
PLAYER_BULLETS = PG.sprite.Group()
ENEMIES_BULLETS = PG.sprite.Group()

# set game screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 768
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
SCREEN = PG.display.set_mode(SCREEN_SIZE)
# set screen caption
PG.display.set_caption("MY PYGAME GAME")
# set screen icon
ICON = PG.image.load(path.join(SRC_DIR, 'icon.png')).convert_alpha()
PG.display.set_icon(ICON)
# set game loop speed
FPS = 60
# set game fps timer
tick = 0

# set player scores and lives
player_lives = 3
player_scores = 0

# set enemies counter
enemies_counter = 0

# set current map
current_map = 0

# set game status ant screen timer
GAME_STATUS = 'start' #'start', 'level', 'defeat', 'win'
min_screen_timeout = FPS
screen_timeout = min_screen_timeout + tick

###################
#
#   UPLOAD IMAGES
#
###################

def image_load(img):
    return PG.image.load(path.join(SRC_DIR, img)).convert()

def image_load_alpha(img):
    return PG.image.load(path.join(SRC_DIR, img)).convert_alpha()

BG_IMAGE = image_load('background_1280x768.jpg')
BG_IMG_RECT = BG_IMAGE.get_rect()

START_IMAGE = image_load('start_screen.png')
START_IMG_RECT = BG_IMAGE.get_rect()

DEFEAT_IMAGE = image_load('defeat_screen.png')
DEFEAT_IMG_RECT = BG_IMAGE.get_rect()

WIN_IMAGE = image_load('win_screen.png')
WIN_IMG_RECT = BG_IMAGE.get_rect()

BASE_IMAGE = image_load_alpha('base.png')
BORDER_IMAGE = image_load('border.png')
WALL_4_IMAGE = image_load('wall_4.png')
WALL_3_IMAGE = image_load_alpha('wall_3.png')
WALL_2_IMAGE = image_load_alpha('wall_2.png')
WALL_1_IMAGE = image_load_alpha('wall_1.png')

PLAYER_UP_IMAGE = image_load_alpha('player.png')
PLAYER_LEFT_IMAGE = PG.transform.rotate(PLAYER_UP_IMAGE, 90)
PLAYER_DOWN_IMAGE = PG.transform.rotate(PLAYER_UP_IMAGE, 180)
PLAYER_RIGHT_IMAGE = PG.transform.rotate(PLAYER_UP_IMAGE, 270)

ENEMY_UP_IMAGE = image_load_alpha('enemy.png')
ENEMY_LEFT_IMAGE = PG.transform.rotate(ENEMY_UP_IMAGE, 90)
ENEMY_DOWN_IMAGE = PG.transform.rotate(ENEMY_UP_IMAGE, 180)
ENEMY_RIGHT_IMAGE = PG.transform.rotate(ENEMY_UP_IMAGE, 270)

BULLET_IMAGE = image_load_alpha('bullet.png')

def get_spriteshit(img, frame_size, start_image_points, images):
    spriteshit = []
    img_w = img.get_width()
    img_h = img.get_height()
    frame_w, frame_h = frame_size
    start_row, start_row_ceil = start_image_points
    point_x = point_y = 0
    step_size_x = img_w // frame_w
    step_size_y = img_h // frame_h
    counter = 0;
    start_is = False
    while counter < images:
        for step_y in range(step_size_y):
            for step_x in range(step_size_x):
                if not start_is and step_y == start_row and step_x == start_row_ceil:
                    start_is = True
                if start_is:
                    counter += 1
                    frame = PG.Surface(frame_size)
                    frame.blit(img, (0, 0), (point_x, point_y, point_x + frame_w, point_y + frame_h))
                    frame.set_colorkey((0, 0, 0))
                    spriteshit.append(frame)
                point_x += frame_w
            point_x = 0
            point_y += frame_h
    return spriteshit

RELOAD_SPRITESHEET_IMAGE = image_load_alpha('reload_9f_1r_64x64.png')
RELOAD_SPRITESHEET = get_spriteshit(RELOAD_SPRITESHEET_IMAGE, (64, 64), (0, 0), 9)

EXPLOSION_SPRITESHEET_IMAGE = image_load_alpha('explosion_4f_4r_64x64.png')
EXPLOSION_SPRITESHEET = get_spriteshit(EXPLOSION_SPRITESHEET_IMAGE, (64, 64), (0, 0), 16)

###################
#
#   UPLOAD FONTS
#
###################

C_BLUE = (0, 0, 255)
LEVEL_FONT = PG.font.Font(path.join(SRC_DIR, 'Roboto-Black.ttf'), 48)
LEVEL_TEXT = LEVEL_FONT.render(f'Уровень {current_map + 1}', True, C_BLUE)
LEVEL_TEXT_POSITION = LEVEL_TEXT.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT/ 2 - 12))

C_BLACK = (0, 0, 0)
PLAYER_FONT = PG.font.Font(path.join(SRC_DIR, 'Roboto-Bold.ttf'), 24)
PLAYER_TEXT = PLAYER_FONT.render(f'Жизни: {player_lives} | Очки: {player_scores}', True, C_BLACK)
PLAYER_TEXT_POSITION = PLAYER_TEXT.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT/ 2 + 24))

###################
#
#   UNITS CLASSES
#
###################

class Base(SPRITE):
    def __init__(self, x, y):
        SPRITE.__init__(self)
        self.image = BASE_IMAGE
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

base = Base(0, 0)

class Player(SPRITE):
    def __init__(self, x, y):
        SPRITE.__init__(self)
        self.image = PLAYER_UP_IMAGE
        self.reload_sprite = None
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 0
        self.speed_y = 0
        self.speed = 2
        self.max_bullets = 5
        self.bullets = self.max_bullets
        self.shut_timeout = 0 # after shut = FPS
        self.reloading_step_timeout = 0 # if reload = (FPS // 2) * steps

    def update(self):
        global player_lives, player_scores, PLAYER_TEXT
        # test bullet hit
        if PG.sprite.spritecollide(self, ENEMIES_BULLETS, True):
            player_lives -= 1;
            PLAYER_TEXT = PLAYER_FONT.render(f'Жизни: {player_lives} | Очки: {player_scores}', True, C_BLACK)
            explosion = Explosion(self.rect.x, self.rect.y)
            ALL_SPRITES.add(explosion)
            MOVING_SPRITES.add(explosion)
            if player_lives > 0:
                self.rect.x = base.rect.x
                self.rect.y = base.rect.y
            else:
                self.kill()

        # get pressed keys
        key = PG.key.get_pressed()

        # test shuting or await
        if self.bullets > 0:
            if self.shut_timeout == 0:
                if key[PG.K_SPACE]:
                    PG.mixer.Sound.play(shut_sound)
                    self.shut()
            else:
                self.shut_timeout -= 1;
        else:
            self.reloading()

        # test position for change direction
        if self.rect.x % 32 == 0 and self.rect.y % 32 == 0:
            self.update_direction(key)

        # move
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # test collisions
        if PG.sprite.spritecollide(self, SOLID_SPRITES, False)\
        or PG.sprite.spritecollide(self, ENEMIES_SPRITES, False):
            self.rect.x -= self.speed_x
            self.rect.y -= self.speed_y

    def update_direction(self, key):
        self.speed_x = 0
        self.speed_y = 0
        if key[PG.K_LEFT]:
            self.speed_x = -self.speed
            self.image = PLAYER_LEFT_IMAGE
            PG.mixer.Sound.play(move_sound)
        elif key[PG.K_RIGHT]:
            self.speed_x = self.speed
            self.image = PLAYER_RIGHT_IMAGE
            PG.mixer.Sound.play(move_sound)
        elif key[PG.K_UP]:
            self.speed_y = -self.speed
            self.image = PLAYER_UP_IMAGE
            PG.mixer.Sound.play(move_sound)
        elif key[PG.K_DOWN]:
            self.speed_y = self.speed
            self.image = PLAYER_DOWN_IMAGE
            PG.mixer.Sound.play(move_sound)
        else:
            PG.mixer.Sound.stop(move_sound)

    def shut(self):
        self.bullets -= 1
        if self.bullets == 0:
            self.reloading_step_timeout = (FPS // 2) * len(RELOAD_SPRITESHEET)

        self.shut_timeout = FPS
        # get start bullet position
        if self.image == PLAYER_UP_IMAGE or self.image == PLAYER_DOWN_IMAGE:
            bullet_x = self.rect.centerx
            if self.image == PLAYER_UP_IMAGE:
                bullet_y = self.rect.top
                direction = 0
            else:
                bullet_y = self.rect.bottom
                direction = 2
        else:
            bullet_y = self.rect.centery
            if self.image == PLAYER_RIGHT_IMAGE:
                bullet_x = self.rect.right
                direction = 1
            else:
                bullet_x = self.rect.left
                direction = 3
        # create bullet
        bullet = Bullet(bullet_x, bullet_y, direction, ENEMIES_BULLETS)
        ALL_BULLETS.add(bullet)
        PLAYER_BULLETS.add(bullet)
        MOVING_SPRITES.add(bullet)
        ALL_SPRITES.add(bullet)

    def reloading(self):
        self.reloading_step_timeout -= 1
        if self.reloading_step_timeout == 0:
            self.reload_sprite = None
            self.bullets = self.max_bullets
        else:
            reload_frame = self.reloading_step_timeout // (FPS // 2)
            self.reload_sprite = RELOAD_SPRITESHEET[reload_frame]

player = Player(0, 0)

class Enemy(SPRITE):
    def __init__(self, x, y):
        SPRITE.__init__(self)
        self.direction = randint(0, 3)
        self.images = [ENEMY_UP_IMAGE, ENEMY_RIGHT_IMAGE, ENEMY_DOWN_IMAGE, ENEMY_LEFT_IMAGE]
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 0
        self.speed_y = 0
        self.speed = 2
        self.turn_time = 0
        self.shut_time = FPS * randint(2, 3)

    def update(self):
        global player_scores, player_lives, PLAYER_TEXT, enemies_counter
        # test bullet hit
        if PG.sprite.spritecollide(self, PLAYER_BULLETS, True):
            player_scores += 1;
            if player_scores % 10 == 0:
                player_lives += 1
            PLAYER_TEXT = PLAYER_FONT.render(f'Жизни: {player_lives} | Очки: {player_scores}', True, C_BLACK)
            explosion = Explosion(self.rect.x, self.rect.y)
            ALL_SPRITES.add(explosion)
            MOVING_SPRITES.add(explosion)
            enemies_counter -= 1
            self.kill()

        # test time to shut
        if tick >= self.shut_time:
            self.shut()

        # test time to change direction
        if tick >= self.turn_time and self.rect.x % 32 == 0 and self.rect.y % 32 == 0:
            self.update_direction()

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if PG.sprite.spritecollide(self, SOLID_SPRITES, False)\
        or self.rect.colliderect(base.rect):
            self.rect.x -= self.speed_x
            self.rect.y -= self.speed_y
            self.speed_x = 0
            self.speed_y = 0

        if len(PG.sprite.spritecollide(self, MOVING_SPRITES, False)) > 1:
            self.rect.x -= self.speed_x
            self.rect.y -= self.speed_y
            self.direction += 2
            if self.direction > 3:
                self.direction -= 4
            self.image = self.images[self.direction]
            self.speed_x *= -1
            self.speed_y *= -1
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y             
    
    def update_direction(self):
        self.turn_time = tick + FPS * randint(1, 3)
        self.direction = randint(0, 3)
        self.image = self.images[self.direction]
        self.speed_x = 0
        self.speed_y = 0
        if self.direction == 0:
            self.speed_y += -self.speed
        elif self.direction == 1:
            self.speed_x += self.speed
        elif self.direction == 2:
            self.speed_y += self.speed
        elif self.direction == 3:
            self.speed_x += -self.speed

    def shut(self):
        self.shut_time += FPS * 2 + randint(0, FPS)
        if self.direction == 0 or self.direction == 2:
            bullet_x = self.rect.centerx
            if self.direction == 0:
                bullet_y = self.rect.top
            else:
                bullet_y = self.rect.bottom
        else:
            bullet_y = self.rect.centery
            if self.direction == 1:
                bullet_x = self.rect.right
            else:
                bullet_x = self.rect.left
        # create bullet
        bullet = Bullet(bullet_x, bullet_y, self.direction, PLAYER_BULLETS)
        ALL_BULLETS.add(bullet)
        ENEMIES_BULLETS.add(bullet)
        MOVING_SPRITES.add(bullet)
        ALL_SPRITES.add(bullet)

class Bullet(SPRITE):
    def __init__(self, x, y, direction, other_bullet):
        SPRITE.__init__(self)
        self.other_bullet = other_bullet
        self.image = BULLET_IMAGE
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed_x = 0
        self.speed_y = 0
        self.speed = 4
        if direction == 0:
            self.speed_y = -self.speed
        elif direction == 1:
            self.speed_x = self.speed
        elif direction == 2:
            self.speed_y = self.speed
        elif direction == 3:
            self.speed_x = -self.speed
        # move aside from parent
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # test collisions
        if PG.sprite.spritecollide(self, BORDER_SPRITES, False) \
        or PG.sprite.spritecollide(self, self.other_bullet, True):
            self.kill()

        walls = PG.sprite.spritecollide(self, WALL_SPRITES, False)
        if walls:
            walls[0].get_hit()
            self.kill()

        # destroy bullet if it out of screen
        if self.rect.x > 1292 or self.rect.x < -12 or self.rect.y > 780 or self.rect.y < -12:
            self.kill()

class Border(SPRITE):
    def __init__(self, x, y):
        SPRITE.__init__(self)
        self.image = BORDER_IMAGE
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Wall(SPRITE):
    def __init__(self, x, y, hp):
        SPRITE.__init__(self)
        self.hp = hp
        self.images = [WALL_1_IMAGE, WALL_2_IMAGE, WALL_3_IMAGE, WALL_4_IMAGE]
        self.image = self.images[hp]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def get_hit(self):
        self.hp -= 1
        if self.hp >= 0:
            self.image = self.images[self.hp]
        else:
            self.kill()

class Explosion(SPRITE):
    def __init__(self, x, y):
        SPRITE.__init__(self)
        self.frame = 0;
        self.lust_frame = len(EXPLOSION_SPRITESHEET)
        self.images = EXPLOSION_SPRITESHEET
        self.image = EXPLOSION_SPRITESHEET[self.frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        PG.mixer.Sound.play(explosion_sound)
    
    def update(self):
        global GAME_STATUS, current_map, screen_timeout, enemies_counter, player_lives
        self.frame += 1
        if self.frame == self.lust_frame:
            # test enemies and player lives
            if player_lives < 1:
                GAME_STATUS = 'defeat'
                screen_timeout = min_screen_timeout + tick
            elif enemies_counter < 1:
                GAME_STATUS = 'win'
                screen_timeout = min_screen_timeout + tick
            self.kill()
        else:
            self.image = EXPLOSION_SPRITESHEET[self.frame]
    
###################
#
#    MAP ARRAYS
#
###################

maps_list = []

def fill_map():
    global LEVEL_TEXT, PLAYER_TEXT, current_map, maps_list, enemies_counter, player_lives, player_scores
    LEVEL_TEXT = LEVEL_FONT.render(f'Уровень {current_map + 1}', True, C_BLUE)
    PLAYER_TEXT = PLAYER_FONT.render(f'Жизни: {player_lives} | Очки: {player_scores}', True, C_BLACK)
    # clear all sprite groups
    ALL_SPRITES.empty()
    SOLID_SPRITES.empty()
    WALL_SPRITES.empty()
    BORDER_SPRITES.empty()
    MOVING_SPRITES.empty()
    ENEMIES_SPRITES.empty()
    ALL_BULLETS.empty()
    PLAYER_BULLETS.empty()
    ENEMIES_BULLETS.empty()

    enemies_counter = 0

    BLOCK_STEP = 64
    point_x = BLOCK_STEP / 2 - BLOCK_STEP
    point_y = BLOCK_STEP / 2 - BLOCK_STEP
    
    for line in maps_list[current_map]:
        for ceil in line:
            if ceil == '#':
                border = Border(point_x, point_y)
                ALL_SPRITES.add(border)
                SOLID_SPRITES.add(border)
                BORDER_SPRITES.add(border)
            if ceil == '4' or ceil == '3' or ceil == '2' or ceil == '1':
                wall = Wall(point_x, point_y, int(ceil) - 1)
                ALL_SPRITES.add(wall)
                SOLID_SPRITES.add(wall)
                WALL_SPRITES.add(wall)
            if ceil == 'E':
                enemy = Enemy(point_x, point_y)
                ALL_SPRITES.add(enemy)
                MOVING_SPRITES.add(enemy)
                ENEMIES_SPRITES.add(enemy)
                enemies_counter += 1
            if ceil == 'P':
                base.rect.x = point_x
                base.rect.y = point_y
                ALL_SPRITES.add(base)
                player.rect.x = point_x
                player.rect.y = point_y
                ALL_SPRITES.add(player)
                MOVING_SPRITES.add(player)

            point_x += BLOCK_STEP
        
        point_x = BLOCK_STEP / 2 - BLOCK_STEP
        point_y += BLOCK_STEP

'''
Empty block  = ' '
Player block = 'P'
Enemy block  = 'E'
Border block = '#'
WAll block   = '4' -> 4 is a Wall HP
'''
MAP_1 = [
    ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
    ['#', ' ', ' ', ' ', ' ', ' ', '4', '4', ' ', ' ', ' ', ' ', ' ', '4', '4', ' ', ' ', ' ', ' ', ' ', '#'],
    ['#', ' ', '4', ' ', '4', ' ', '4', '4', ' ', '4', '4', '4', ' ', '4', '4', ' ', '4', 'E', '4', ' ', '#'],
    ['#', ' ', ' ', ' ', '4', 'E', ' ', ' ', ' ', 'E', ' ', ' ', ' ', ' ', ' ', 'E', '4', ' ', ' ', 'E', '#'],
    ['#', ' ', '4', ' ', '4', ' ', '4', '4', '4', '4', '4', '4', '4', '4', '4', ' ', '4', ' ', '4', ' ', '#'],
    ['#', ' ', ' ', ' ', '4', ' ', '4', '#', '#', '#', '#', '#', '#', '#', '4', ' ', '4', ' ', ' ', ' ', '#'],
    ['#', ' ', '4', ' ', '4', ' ', '4', '#', '#', '#', '#', '#', '#', '#', '4', ' ', '4', ' ', '4', ' ', '#'],
    ['#', ' ', ' ', ' ', '4', ' ', '4', '#', '#', '#', '#', '#', '#', '#', '4', ' ', '4', ' ', ' ', ' ', '#'],
    ['#', ' ', '4', ' ', '4', ' ', '4', '4', '4', '4', '4', '4', '4', '4', '4', ' ', '4', ' ', '4', ' ', '#'],
    ['#', ' ', ' ', ' ', '4', 'E', ' ', ' ', ' ', 'E', ' ', ' ', ' ', ' ', ' ', 'E', '4', ' ', ' ', 'E', '#'],
    ['#', ' ', '4', ' ', '4', ' ', '4', '4', ' ', '4', '4', '4', ' ', '4', '4', ' ', '4', 'E', '4', ' ', '#'],
    ['#', 'P', ' ', ' ', ' ', ' ', '4', '4', ' ', ' ', ' ', ' ', ' ', '4', '4', ' ', ' ', ' ', ' ', ' ', '#'],
    ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']
]
maps_list.append(MAP_1)

MAP_2 = [
    ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
    ['#', '4', '4', '4', '4', '4', '3', '3', ' ', ' ', 'E', ' ', 'E', ' ', ' ', '3', ' ', ' ', ' ', ' ', '#'],
    ['#', '4', '4', '4', '4', '4', '3', '3', ' ', '4', ' ', 'E', ' ', '4', ' ', '3', ' ', 'E', ' ', 'E', '#'],
    ['#', ' ', ' ', ' ', ' ', '3', ' ', ' ', ' ', '4', 'E', ' ', 'E', '4', ' ', '2', ' ', ' ', ' ', ' ', '#'],
    ['#', ' ', ' ', ' ', ' ', '2', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '2', ' ', 'E', ' ', 'E', '#'],
    ['#', ' ', '4', '4', ' ', '1', ' ', '#', '#', '#', '#', '#', '#', '#', ' ', '1', ' ', ' ', ' ', ' ', '#'],
    ['#', ' ', '4', '4', ' ', ' ', ' ', '#', '#', '#', '#', '#', '#', '#', ' ', '1', ' ', 'E', ' ', 'E', '#'],
    ['#', ' ', '4', '4', '4', '4', ' ', '#', '#', '#', '#', '#', '#', '#', ' ', '1', ' ', ' ', ' ', ' ', '#'],
    ['#', '2', '4', '4', '4', '4', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '2', ' ', 'E', ' ', ' ', '#'],
    ['#', ' ', ' ', ' ', '4', '4', ' ', ' ', ' ', '4', 'E', ' ', 'E', '4', ' ', '3', ' ', ' ', ' ', ' ', '#'],
    ['#', '2', '2', ' ', '4', '4', '3', '3', ' ', '4', ' ', 'E', ' ', '4', ' ', '3', ' ', 'E', ' ', 'E', '#'],
    ['#', 'P', '2', ' ', '4', '4', '3', '3', ' ', ' ', 'E', ' ', 'E', ' ', ' ', '3', ' ', ' ', ' ', ' ', '#'],
    ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']
]
maps_list.append(MAP_2)

MAP_3 = [
    ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
    ['#', 'E', ' ', ' ', 'E', '4', '4', '4', 'E', ' ', ' ', ' ', ' ', 'E', ' ', ' ', ' ', ' ', 'E', ' ', '#'],
    ['#', ' ', '4', '4', ' ', '4', '4', '4', ' ', '4', '4', '4', 'E', ' ', 'E', ' ', 'E', ' ', ' ', ' ', '#'],
    ['#', ' ', '4', '4', ' ', '4', '4', '4', 'E', '4', '4', '4', ' ', 'E', ' ', 'E', ' ', ' ', 'E', ' ', '#'],
    ['#', ' ', ' ', ' ', 'E', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'E', ' ', 'E', ' ', ' ', 'E', ' ', 'E', '#'],
    ['#', '4', 'E', ' ', ' ', ' ', 'E', '#', '#', '#', '#', '#', '#', '#', ' ', 'E', 'E', ' ', ' ', ' ', '#'],
    ['#', '4', ' ', '4', '4', '4', ' ', '#', '#', '#', '#', '#', '#', '#', 'E', ' ', ' ', ' ', 'E', ' ', '#'],
    ['#', '4', ' ', ' ', ' ', ' ', ' ', '#', '#', '#', '#', '#', '#', '#', ' ', 'E', 'E', ' ', ' ', ' ', '#'],
    ['#', ' ', ' ', ' ', 'E', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'E', ' ', 'E', ' ', ' ', 'E', ' ', 'E', '#'],
    ['#', ' ', '4', '4', ' ', '4', '4', '4', 'E', '4', '4', '4', ' ', 'E', ' ', 'E', ' ', ' ', 'E', ' ', '#'],
    ['#', ' ', '4', '4', ' ', '4', '4', '4', ' ', '4', '4', '4', 'E', ' ', 'E', ' ', 'E', ' ', ' ', ' ', '#'],
    ['#', 'P', ' ', ' ', ' ', '4', '4', '4', 'E', ' ', ' ', ' ', ' ', 'E', ' ', ' ', ' ', ' ', 'E', ' ', '#'],
    ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']
]
maps_list.append(MAP_3)

###################
#
#    GAME LOOP
#
###################

game_loop_is = True
while game_loop_is:
    CLOCK.tick(FPS)
    for event in PG.event.get():
        # test game quit events
        if event.type == PG.QUIT or (event.type == PG.KEYDOWN and event.key == PG.K_ESCAPE):
            game_loop_is = False

    # GAME_STATUS = ('start', 'level', 'defeat', 'win')
    if GAME_STATUS == 'level':
        # Fill the window background, draw and update sprites
        SCREEN.blit(BG_IMAGE, BG_IMG_RECT)
        MOVING_SPRITES.update()
        ALL_SPRITES.draw(SCREEN)

        if player.reload_sprite:
            player.reload_sprite
            SCREEN.blit(player.reload_sprite, player.rect)

        SCREEN.blit(LEVEL_TEXT, LEVEL_TEXT_POSITION)
        SCREEN.blit(PLAYER_TEXT, PLAYER_TEXT_POSITION)

    else:
        if GAME_STATUS == 'start':
            SCREEN.blit(START_IMAGE, START_IMG_RECT)
        elif GAME_STATUS == 'defeat':
            SCREEN.blit(DEFEAT_IMAGE, DEFEAT_IMG_RECT)
        else:
            SCREEN.blit(WIN_IMAGE, WIN_IMG_RECT)
        
        keys = PG.key.get_pressed()
        if tick > screen_timeout and keys:
            if True in keys:
                # if any key is pressed
                if GAME_STATUS == 'start':
                    GAME_STATUS = 'level'
                    fill_map()
                elif GAME_STATUS == 'defeat':
                    tick = 0
                    screen_timeout = min_screen_timeout + tick
                    GAME_STATUS = 'start'
                    player_lives = 3
                    player_scores = 0
                    player = Player(base.rect.x, base.rect.y)
                else:
                    current_map += 1
                    if current_map < len(maps_list):
                        GAME_STATUS = 'level'
                        fill_map()
                    else:
                        current_map = 0;
                        player_lives = 3
                        player_scores = 0
                        tick = 0
                        screen_timeout = min_screen_timeout + tick
                        GAME_STATUS = 'start'

    # Flip the display
    PG.display.flip()

    # update game fps timer
    tick += 1

# To quit
PG.quit()
sys.exit()