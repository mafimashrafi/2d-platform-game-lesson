import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_VEL = 5

#setting up pygame window
window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]
    #false means don't flip in y direction. True will flip
    #true will flip in x direction. to do both true twice



def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))] #every single file from the directory
    
    all_sprites = {}

    for image in images: #spliting images
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha() #an individual sheet alpha loads transparent bg
    
        sprites = [] #list of each individual images
        for i in range(sprite_sheet.get_width() // width): #total width by individual width will split all images
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32) #32 is the width of our image and scralpha loads transparent
            rect = pygame.Rect(i * width, 0, width, height) #where the image is from
            surface.blit(sprite_sheet, (0, 0), rect) #blit will draw the sprite sheet
            sprites.append(pygame.transform.scale2x(surface)) # appending the 2x sized sufrace in sprite sheet
        
        #handling directions
        if direction:
            all_sprites[image.replace('.png', "") + '_right'] = sprites
            all_sprites[image.replace('.png', "") + '_left'] = flip(sprites)
        else:
            all_sprites[image.replace('.png', "")] = sprites

    return all_sprites

def get_block(size): #importing block image
    path = join('assets', "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size) #postion we are picking from the image
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1 #barai dile gravity barbe
    ANIMATION_DELAY = 3 #the less the number the fast the animation
    SPRITES = load_sprite_sheets('MainCharacters', "PinkMan", 32, 32, True)

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height) # for the Rect it will take our palyer as rectangular containing four values
        self.x_vel = 0
        self.y_vel = 0 #these x y velocity determines how fast we are moving our player on the xy plane
        self.mask = None
        self.direction = "left" #the direction my player facing
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 10
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count == 0
        

    def move(self, dx, dy): #we just change the signs of dx dy to move 
        self.rect.x += dx
        self.rect.y += dy
    
    def make_hit(self):
        self.hit = True
        self.hit_count = 0
    
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    def loop(self, fps): #loop will caleed once in every frame
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        #fire animation
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps*2: #to stop the hit loop
            self.hit = False
            self.hit_count = 0 

        self.fall_count += 1
        self.update_sprite() #instead of line 100

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1 #as we will come back after hited
    
    def update_sprite(self): #adding animation
        sprite_sheet = 'idle'
        if self.hit:
            sprite_sheet = 'hit'
        elif self.y_vel < 0 :
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"
        
        sprite_sheet_name = sprite_sheet + '_' + self.direction
        sprites =self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites) # every five frame will show a different idle
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y)) #rect will re size based on our image
        self.mask = pygame.mask.from_surface(self.sprite) #mask tells are where the pixel or the image is and allows to do prefect collision

    def draw(self, win, offset_x):
        # #if we keep the idle only it does not knows the direction for that we will add direction like idle_right or
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
        #pygame.draw.rect(win, self.COLOR, self.rect) #it was the red block


class Object(pygame.sprite.Sprite): #for collusion
    def __init__(self, x, y, width, height, name=None):
        super().__init__() #super class
        #define rectangle
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x): #drawing
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block =  get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image) #will help to avoid collusion


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__( x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire['off'][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = 'off'

    def on(self):
        self.animation_name = 'on'

    def off(self):
        self.animation_name = 'off'

    def loop(self):
        sprites =self.fire[self.animation_name]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites) # every five frame will show a different idle
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y)) #rect will re size based on our image
        self.mask = pygame.mask.from_surface(self.image)
        
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0 
        #so that animation does not goes too higher. to avoid lag


def get_background(name): #importing image and margening them
    image = pygame.image.load(join('assets', 'Background', name))
    _, _, width, height = image.get_rect() #_ two means x y plane which I don't care about and rect will get wid an h from image
    tiles = []

    for i in range(WIDTH // width+1):
        for j in range(HEIGHT // height+1):
            pos = (i * width, j*height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x): #this will draw the bg
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x) #will draw on the window
    
    player.draw(window, offset_x)
        
    pygame.display.update()

def handle_verticle_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy >0 :
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head
        
            collided_objects.append(obj)
    
    return collided_objects

def collied(player, objects, dx): #horizontal collision
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    
    player.move(-dx, 0)
    player.update()
    return collided_object



def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0 # it will stop the movement after one key. unless it wiil keep going
    
    collide_left = collied(player, objects, -PLAYER_VEL * 2)
    collide_right = collied(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left: #here k for key and left means left arrow key wi can use a
        player.move_left(PLAYER_VEL) #left arrow press korle prayer nijer vel poriman move korbe
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_verticle_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == 'fire':
            player.make_hit()


def main(window):
    clock = pygame.time.Clock()
    background, bg_image= get_background("Green.png")

    block_size = 96
    player = Player(100, 100, 50, 50)
    fire = Fire(300, HEIGHT - block_size * 4 - 64, 16, 32)
    fire1 = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    fire1.off()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    #blocks = [Block(0, HEIGHT-block_size, block_size)]

    objects = [*floor, Block(0, HEIGHT - block_size*2, block_size),
               Block(block_size * 3, HEIGHT - block_size*4, block_size),
               Block(block_size * 3 + 95, HEIGHT - block_size*4, block_size),
               Block(block_size * 3 + 190, HEIGHT - block_size*4, block_size), fire, fire1]

    offset_x = 0
    scroll_area_width = 200


    run = True
    while run:
        clock.tick(FPS) #so, our while loop will run 60 fps
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            #jumping you have to press again and again
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count <2:
                    player.jump()

        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        #scrolling bg only when we reaches the boundary
        if (player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()

if __name__ == '__main__': #for this the game will run when we will run this file directly
    main(window)