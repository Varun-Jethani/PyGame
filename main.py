import os
import random
import math
from typing import Any
import pygame
from button import Button
from os import listdir
from os.path import isfile, join
import time

from pygame.sprite import Group

pygame.init()

pygame.display.set_caption("Platformer")


WIDTH, HEIGHT = 1300, 768
GREEN = (147, 200, 8)
PAUSED= False
FPS = 60
PLAYER_VEL = 5
font_path = "assets\\Fonts\\1_Minecraft-Regular.otf"

window = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()
gameEnd = pygame.image.load("Assets\\Other\\gameover.png").convert_alpha()



def flip(sprites): 
    '''function for fliping images'''
    return[pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1,dir2,width,height,direction=False):
    '''Function for loading sheets of single sprite for giving it multiple images
     \nNOTE always applies scale2x for each image'''
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
    '''
    gets the square block image from pos in terrain png of size  
    \n NOTE Always Applies scale 2x 
    '''  
    path = join("assets","Terrain","Terrain.png") 
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(pos[0],pos[1],size,size)
    surface.blit(image,(0,0),rect)
    return pygame.transform.scale2x(surface)

def get_trap_block(size,pos):
    '''gets sqaure block image from pos in Sand Mud Ice png of size
    \n NOTE Always Applies scale 2x'''
    path = join ("assets","Traps","Sand Mud Ice", "Sand Mud Ice (16x6).png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(pos[0],pos[1],size,size)
    surface.blit(image,(0,0),rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255,0,0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters","NinjaFrog",32,32,True)
    ANIMATION_DELAY = 4
    
    def __init__(self,x,y,width,height):
        """Player Class x y is left and top
         creates a player object with various properties 
         and method to control the player movement and animation"""
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
        """ function for jump, gives player upward velocity """
        self.y_vel = -self.GRAVITY * 8
        self.animation_count=0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
        
    def move(self,dx, dy):
        """ function for moving player by dx and dy (pass the x and y velocity)"""
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        """ gives the player a hit state and reduces the health """
        self.hit = True
        self.hit_count = 0
        if self.health > 0:
            self.health-=1
        
    def move_left(self, vel):
        """ changes the players horizontal velocity towards left
          and changes the direction the player is facing to left"""
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
        
    def move_right(self, vel): 
        """ changes the players horizontal velocity towards right
          and changes the direction the player is facing to right"""   
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        """ constantly changes the players y velocity to  give gravity effect
        checks if player has health
        moves the players rect using x_vel and y_vel property
        checks if player has fallen off
        maintains hit check
        and updates the sprite"""
        self.y_vel += min(1, (self.fall_count/fps)*self.GRAVITY)
        if self.health > 0 :
            self.move(self.x_vel, self.y_vel)

        if self.rect.y > WIDTH:
            self.health = 0

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps/2:
            
            self.hit = False

        self.fall_count +=1
        self.update_sprite()

    def landed(self):
        """resets properties so player doesn't glitch out due to gravity"""
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_header(self):
        """reverses the players y velocity"""
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        """updates the sprite according to players state 
        utilizes properties health,y_vel,x_vel,jump_count,gravity,direction"""
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
        """ draws the sprite on win surface """
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


class Menu(Object):
    def __init__(self, x, y, width, height, name=None):
        super().__init__(x, y, width, height, name="menu")
        self.buttons = load_sprite_sheets("Menu","Buttons",width,height)  


def menu_button_pressed(menu,no):
    global PAUSED, window, menu_run, run
    if menu == "pause":
        if no == 0:
            PAUSED = False
        if no == 1:
            PAUSED = False
            main(window)
        if no == 4:
            run = False
            PAUSED = False
            main_menu(window)

    elif menu == "main":
        if no == 0:
            main(window)
        if no == 3:
            menu_run = False
                        
def get_background(name):
    image = pygame.image.load(join("assets","Background",name))
    _, _, width, height = image.get_rect()
    tiles=[]
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i*width,j*height)
            tiles.append(pos)

    return tiles, image

def backgroundloader(folder):
    bgpath = join("assets",folder)

    imgs = [f for f in listdir(bgpath) if isfile(join(bgpath,f))]
    bg={}
    for img in imgs:
        bg[img.replace(".png","")]=[pygame.image.load(join(bgpath,img)).convert_alpha()]

    bg["bluesky"].append((bg["bluesky"][0].get_width(),0))
    bg["clouds"].append((bg["clouds"][0].get_width(),50))
    bg["Mountains2"].append((bg["Mountains2"][0].get_width(),200))
    bg["Treessilu"].append((bg["Treessilu"][0].get_width(),450))
    bg["riverbankback"].append((bg["riverbankback"][0].get_width(),510))
    bg["river"].append((bg["river"][0].get_width(),570))
    bg["riverbankfront"].append((bg["riverbankfront"][0].get_width(),600))
    bg["trees"].append((bg["trees"][0].get_width(),400))
    bglist = {"clouds":0.1,
              "Mountains2":0.2,
              "Treessilu":0.3,
              "riverbankback":0.5,
              "river":0.7,
              "riverbankfront":0.9,
              "trees":0.9}
    return bg, bglist

def draw (window,bg,bglist, background, bg_image, player,objects,bars,gameEnd,offset_x):
    # for tile in background:
    #     window.blit(bg_image, tile)
    window.fill(GREEN)
    window.blit(bg["bluesky"][0],(0,0))
    
    
    for compo in bglist:
        for i in range(-4,9,1):
            window.blit(bg[compo][0],((bg[compo][1][0]-4)*i - offset_x*bglist[compo], bg[compo][1][1]))

    # window.blit(bg["bluesky"][0],bg["bluesky"][1]) 
    # window.blit(bg["clouds"][0],(bg["clouds"][1][0]-offset_x*0.4,bg["clouds"][1][1]))
    # window.blit(bg["Mountains2"][0],(bg["Mountains2"][1][0]-offset_x*0.5,bg["Mountains2"][1][1]))
    # window.blit(bg["Treessilu"][0],(bg["Treessilu"][1][0] - offset_x*0.6,bg["Treessilu"][1][1]))
    # window.blit(bg["riverbankback"][0],(bg["riverbankback"][1][0]-offset_x*0.7,bg["riverbankback"][1][1]))
    # window.blit(bg["river"][0],(bg["river"][1][0]-offset_x*0.8,bg["river"][1][1]))
    # window.blit(bg["riverbankfront"][0],(bg["riverbankfront"][1][0]-offset_x*0.9,bg["riverbankfront"][1][1]))
    # window.blit(bg["trees"][0],(bg["trees"][1][0]-offset_x,bg["trees"][1][1]))
    
    player.draw(window, offset_x)
    for obj in objects:
        obj.draw(window, offset_x)

    

    for bar in bars:
        bar.draw(window,player.health)
    if player.health == 0:
        window.blit(gameEnd,((WIDTH-600)/2, (HEIGHT-309)/2))
        
    pygame.display.update()

def draw_text(surface,text,size,color,x,y,fit = False, fit_size = (0,0)):
    font = pygame.font.Font(font_path,size)
    img = font.render(text,False,color).convert_alpha()
    if fit:
        surface.blit(img,(x+(fit_size[0]-img.get_width())/2,y+(fit_size[1]-img.get_height())/2))
    else:
        surface.blit(img,(x,y))

def menu_draw(surface,menu, buttons):
    for i in range(len(buttons)):
        if buttons[i].draw(surface):
            menu_button_pressed(menu,i)
    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            if player.spawned > 0:
                    player.spawned -= 1
            elif dy >= 0:
                collision_point = pygame.sprite.collide_mask(player, obj)
                
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


#Screen Functions
def main(window):
    """Opens the game Screen"""
    global PAUSED, run
    
    background, bg_image = get_background("Blue.png")
    bg, bglist = backgroundloader("New BG")
    

    block_size = 96
    
    player = Player(10,HEIGHT - block_size * 2 + 25 ,50,50)
    fire=Fire(100,HEIGHT - block_size - 64, 16, 32)
    fire.on()
    saws = [Saw(200, HEIGHT - block_size -74,38,38),Saw(400, HEIGHT - block_size -74,38,38),Saw(800, HEIGHT - block_size -74,38,38),Saw(1200, HEIGHT - block_size -74,38,38)]
    for saw in saws:
        saw.on()
    negfloor= [Block(i* block_size, HEIGHT - block_size, block_size,3) 
             for i in range(-WIDTH//block_size- 7, -WIDTH*2//block_size,-1)]
    floor = [Block(i* block_size, HEIGHT - block_size, block_size,3) 
             for i in range(-WIDTH // block_size, WIDTH//block_size)]
    
    floor2 = [Block(i* block_size, HEIGHT - block_size, block_size,3) 
             for i in range(WIDTH//block_size+ 2, WIDTH*2//block_size)]
    floor3 = [Block(i* block_size, HEIGHT - block_size, block_size,3) 
             for i in range(WIDTH*2//block_size+ 3, WIDTH*3//block_size)]
    floor4 = [Block(i* block_size, HEIGHT - block_size, block_size,3) 
             for i in range(WIDTH*3//block_size+ 4, WIDTH*4//block_size)]
    floor5 = [Block(i* block_size + block_size/2, HEIGHT - block_size, block_size,3) 
             for i in range(WIDTH*4//block_size+ 4, WIDTH*5//block_size)]
    #blocks = [Block(0,HEIGHT - block_size,block_size)]

    objects = [*negfloor, *floor,*floor2,*floor3,*floor4,*floor5, Block(0,HEIGHT - block_size * 2, block_size,2),
               Block(block_size * 3,HEIGHT - block_size * 4, block_size,3),fire,*saws]
    buttonimage = pygame.image.load("assets\\Menu\\Buttons\\menubutton.png").convert_alpha()
    buttonimage.set_alpha(30)
    pausemenu_buttons = [Button((WIDTH-302)/2,(HEIGHT-504)/2 + 89*i,buttonimage,1) for i in range(5)]
    pausemenu_actions = ["Resume","Restart","Settings","Progress","Main Menu"]
    
    bars= [HealthBar(WIDTH-200,10,16,16)]
    
    offset_x = 0
    scroll_area_width = 400
    

    run = True
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    PAUSED = not PAUSED
                    if PAUSED:
                        pausesurf = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
                        pausesurf.fill((30,30,30,150))
                        window.blit(pausesurf,(0,0))

                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    if not PAUSED:
                        player.jump()

        if PAUSED:
            menu_draw(window,"pause",pausemenu_buttons)
            for i in range(5):
                draw_text(window,pausemenu_actions[i],26,(255,255,255,255),(WIDTH-302)/2,(HEIGHT-504)/2 + 89*i,True,(302,57))
        else:
            player.loop(FPS)
            fire.loop()
            for saw in saws:
                saw.loop()

            handle_move(player,objects)
            # handle_game_over(player,window)
            draw(window, bg, bglist, background, bg_image, player, objects,bars,gameEnd, offset_x)

            if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0 ):
                offset_x += player.x_vel


    pygame.quit()
    quit()

def main_menu(window):
    """Opens the main menu screen"""
    bg = pygame.image.load("assets\\Background\\bg.jpg").convert_alpha()
    bgimg = pygame.transform.scale(bg,(WIDTH,HEIGHT))
    window.blit(bgimg,(0,0))

    
    buttonimage = pygame.image.load("assets\\Menu\\Buttons\\MMButton2.png").convert_alpha()
    buttonimage.set_alpha(30)
    menu_buttons = [Button(100,((HEIGHT- 495)/2 + (141*i)),buttonimage,1) for i in range(4)]
    menu_action = ["PLAY","Progress","Settings","Quit"]
    global menu_run
    menu_run = True
    while menu_run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_run = False
                break

        menu_draw(window,"main",menu_buttons)
        for i in range(4):
            draw_text(window,menu_action[i],32,(177,213,238,0),100,((HEIGHT- 495)/2 + (141*i)),True,(300,72))

def  progress(window):
    """Opens the progress screen"""

if __name__ == "__main__":
    main_menu(window)