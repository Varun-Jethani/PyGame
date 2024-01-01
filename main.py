import os
import random
import math
from typing import Any
import pygame
from os import listdir
from os.path import isfile, join
import time

from pygame.sprite import Group

pygame.init()

pygame.display.set_caption("Platformer")


WIDTH, HEIGHT = 1300, 760
FPS = 60
PLAYER_VEL = 5
window = pygame.display.set_mode((WIDTH,HEIGHT))


def flip(sprites):
    return[pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1,dir2,width,height,direction=False):
    if dir2 == None:
        path = join("assets",dir1)
    else:
        path = join("assets",dir1,dir2)
    
    images = [f for f in listdir(path) if isfile(join(path,f))]
    
    all_sprites = {}

    for image in images:
        sprite_sheet  =pygame.image.load(join(path,image)).convert_alpha()
        
        sprites=[]
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width,height),pygame.SRCALPHA, 32)
            rect = pygame.Rect(i*width,0,width,height)
            surface.blit(sprite_sheet, (0,0),rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png","")+"_right"]=sprites
            all_sprites[image.replace(".png","")+"_left"]=flip(sprites)

        else:
            all_sprites[image.replace(".png","")] = sprites

    return all_sprites
            
def get_block(size,pos):
    path = join("assets","Terrain","Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(pos[0],pos[1],size,size)
    surface.blit(image,(0,0),rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    COLOR = (255,0,0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters","VirtualGuy",32,32,True)
    ANIMATION_DELAY = 3
    
    def __init__(self,x,y,width,height):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.x_vel = 0
        self.y_vel = -8
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count=0
        self.hit=False
        self.hit_count=0
        self.health = 100
        self.health_counter=0
        self.spawned = 12
        


    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count=0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
        


    def move(self,dx, dy):
        self.rect.x += dx
        self.rect.y += dy


    def make_hit(self):
        self.hit = True
        self.hit_count = 0
        if self.health > 0:
            self.health-=1
        

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

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count/fps)*self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps*2:
            
            self.hit = False

        self.fall_count +=1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_header(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"

        if self.health ==0:
            sprite_sheet = "Disappear"

        elif self.hit:
            sprite_sheet= "hit"
            

        elif self.y_vel < 0 :
            if self.jump_count==1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        
        elif self.y_vel > self.GRAVITY*2:
            sprite_sheet = "fall"

        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count+=1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)


    def draw(self, win, offset_x):
        # pygame.draw.rect(win,self.COLOR,self.rect)
        #self.sprite = self.SPRITES["idle_"+self.direction][0]
        win.blit(self.sprite, (self.rect.x - offset_x ,self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name= None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self,win, offset_x):
        win.blit(self.image,(self.rect.x - offset_x ,self.rect.y))

class Bar(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height, name = None):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.image = pygame.Surface((width,height),pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self,win,size):
        for i in range(round(size/10)):
            win.blit(self.image,(self.rect.x + (self.width*i) ,self.rect.y))



class HealthBar(Bar):
    def __init__(self, x, y, width, height, name="Health"):
        super().__init__(x, y, width, height, name="health")
        self.bar = load_sprite_sheets("Bars",None, width,height)
        self.image = self.bar["colors"][1]
        


class Block(Object):
    def __init__(self, x, y, size,type):
        super().__init__(x, y, size, size)
        blocks_loc = [(0,0),(0,64),(0,128),(96,0),(96,64),(96,128),(192,0),(192,64),(192,128),(288,64),(288,128)]
        blocks = [get_block(size,loc) for loc in blocks_loc]
        
        self.image.blit(blocks[type],(0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire (Object):
    ANIMATION_DELAY = 4

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps","Fire",width,height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"
    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites)
        
        self.image = sprites[sprite_index]
        self.animation_count+=1

        self.rect = self.image.get_rect(topleft = (self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.aniamtion_count = 0 
        
class Saw(Object):
    ANIMATION_DELAY = 4
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, name="saw")
        self.sprite_sheet = load_sprite_sheets("Traps","Saw",width,height)
        self.image = self.sprite_sheet["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"
    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.sprite_sheet[self.animation_name]
        sprites = sprites[::-1]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites)
        
        self.image = sprites[sprite_index]
        self.animation_count+=1

        self.rect =  self.image.get_rect(topleft = (self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.aniamtion_count = 0

class GameOver(Object):
    def __init__(self, x, y, width, height, name=None):
        super().__init__(x, y, width, height, name="gameOver")
        self.sprite_sheet = load_sprite_sheets("Other",None,width,height)
        self.image = self.sprite_sheet["gameover"][0]
        self.mask = pygame.mask.from_surface(self.image)

class Menu(Object):
    def __init__(self, x, y, width, height, name=None):
        super().__init__(x, y, width, height, name="menu")
        self.buttons = load_sprite_sheets("Menu","Buttons",width,height)  
              

def get_background(name):
    image = pygame.image.load(join("assets","Background",name))
    _, _, width, height = image.get_rect()
    tiles=[]
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i*width,j*height)
            tiles.append(pos)

    return tiles, image

def draw (window, background, bg_image, player,objects,bars,gameEnd,offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    player.draw(window, offset_x)
    for obj in objects:
        obj.draw(window, offset_x)

    

    for bar in bars:
        bar.draw(window,player.health)
    if player.health == 0:
        gameEnd.draw(window,0)
        


    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            if player.spawned > 0:
                    player.spawned -= 1
            elif dy >= 0:
                collision_point = pygame.sprite.collide_mask(player, obj)
                print(collision_point)
                print(player.rect.height)
                # Check if the collision happened at the bottom of sprite1's rect
                if collision_point[1] >= player.rect.height-15:
                    player.rect.bottom = obj.rect.top
                    player.landed()
                else:
                    if player.direction == "left":
                        player.rect.left -= 2
                    else:
                        player.rect.left += 2
                    player.rect.bottom = obj.rect.top
                    player.landed()        
                        

            elif dy <= 0:
                player.rect.top = obj.rect.bottom
                player.hit_header()
        
            collided_objects.append(obj)
    
    return collided_objects

def collide(player, objects, dx):
    player.move(dx,0)
    player.update()
    collided_object=None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    
    player.move(-dx,0)
    player.update()
    return collided_object

def handle_move(player,objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL*2)
    collide_right = collide(player, objects, PLAYER_VEL*2)

    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not collide_left:
        player.move_left(PLAYER_VEL)
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player,objects,player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name in ("fire","saw"):
            player.make_hit()


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96
    
    player = Player(10,HEIGHT - block_size * 2 + 25 ,50,50)
    fire=Fire(100,HEIGHT - block_size - 64, 16, 32)
    fire.on()
    saws = [Saw(200, HEIGHT - block_size -74,38,38),Saw(400, HEIGHT - block_size -74,38,38),Saw(800, HEIGHT - block_size -74,38,38),Saw(1200, HEIGHT - block_size -74,38,38)]
    for saw in saws:
        saw.on()
    floor = [Block(i* block_size, HEIGHT - block_size, block_size,1) 
             for i in range(-WIDTH // block_size, WIDTH*2//block_size)]
    #blocks = [Block(0,HEIGHT - block_size,block_size)]

    objects = [*floor, Block(0,HEIGHT - block_size * 2, block_size,2),
               Block(block_size * 3,HEIGHT - block_size * 4, block_size,3),fire,*saws]
    gameEnd = GameOver((WIDTH-1200)/2, (HEIGHT-618)/2,600,309)
    
    bars= [HealthBar(WIDTH-200,10,16,16)]
    
    offset_x = 0
    scroll_area_width = 200
    PAUSED=False

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    PAUSED= not PAUSED

                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    if not PAUSED:
                        player.jump()

        if PAUSED:
            pass
        else:
            player.loop(FPS)
            fire.loop()
            for saw in saws:
                saw.loop()

            handle_move(player,objects)
            # handle_game_over(player,window)
            draw(window, background, bg_image, player, objects,bars,gameEnd, offset_x)

            if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0 ):
                offset_x += player.x_vel


    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)