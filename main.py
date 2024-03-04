import os
import random
import math
from typing import Any
import pygame
from button import Button
from os import listdir
from os.path import isfile, join
import time
import requests
from io import BytesIO
import json
from widgets import SettingSlider

from pygame.sprite import Group

pygame.init()

pygame.display.set_caption("Platformer")


WIDTH, HEIGHT = 1300, 768
GREEN = (147, 200, 8)
PAUSED= False
FPS = 60
PLAYER_VEL = 5
MASTER_VOLUME = 0.5
font_path = "assets\\Fonts\\1_Minecraft-Regular.otf"
screen = ''

window = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()
gameEnd = pygame.image.load("Assets\\Other\\gameover.png").convert_alpha()

nextsong = pygame.USEREVENT + 9



SoundVolume = 0.9

characters = ["NinjaFrog","MaskDude","PinkMan","VirtualGuy"]
selected_character = 0


class SoundPlayer:
    jumpsfx = pygame.mixer.Sound("assets\\Soundfx\\cartoon-jump-6462.mp3")
    landsfx = pygame.mixer.Sound("assets\\Soundfx\\land2-43790.mp3")
    hitsfx = pygame.mixer.Sound("assets\\Soundfx\\mixkit-small-hit-in-a-game-2072.wav")
    achsfx = pygame.mixer.Sound("assets\\Soundfx\\mixkit-game-experience-level-increased-2062.wav")
    gameoversfx = pygame.mixer.Sound("assets\\Soundfx\\negative_beeps-6008.mp3")
    def __init__(self):
        self.SoundVolume = SoundVolume
        
    def setVolume(self, volume):
        self.SoundVolume = volume
        self.jumpsfx.set_volume(self.SoundVolume*MASTER_VOLUME)
        self.landsfx.set_volume(self.SoundVolume*MASTER_VOLUME)
        self.hitsfx.set_volume(self.SoundVolume*MASTER_VOLUME)
        self.achsfx.set_volume(self.SoundVolume*MASTER_VOLUME)
        self.gameoversfx.set_volume(self.SoundVolume*MASTER_VOLUME)
        

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

def round_image(image, radius):
    """Return a new image with rounded corners."""
    rect = pygame.Rect(0, 0, *image.get_size())
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, pygame.Color('white'), rect, border_radius=radius)
    mask.blit(image, rect, special_flags=pygame.BLEND_RGBA_MULT)
    return mask




class Player(pygame.sprite.Sprite):
    global characters,selected_character
    
    COLOR = (255,0,0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters",characters[selected_character],32,32,True)
    ANIMATION_DELAY = 4
    
    def __init__(self,x,y,width,height):
        """Player Class x y is left and top
         creates a player object with various properties 
         and method to control the player movement and animation"""
        super().__init__()
        self.SPRITES = load_sprite_sheets("MainCharacters",characters[selected_character],32,32,True)
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
        self.land = 0
        self.over_counter = 0
        self.air_counter = 0
        
    def jump(self):
        """ function for jump, gives player upward velocity """
        self.y_vel = -self.GRAVITY * 8
        sound.jumpsfx.play()
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
        if (int(self.y_vel)>0):
            self.air_counter +=1
        
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
        if self.air_counter > 0:
            sound.landsfx.play()
            self.air_counter =0

    def hit_header(self):
        """reverses the players y velocity"""
        self.count = 0
        self.y_vel *= -1
        sound.landsfx.play()

    def update_sprite(self):
        """updates the sprite according to players state 
        utilizes properties health,y_vel,x_vel,jump_count,gravity,direction"""
        sprite_sheet = "idle"

        if self.health ==0:
            sprite_sheet = "Disappear"
            if self.over_counter < 10:
                self.over_counter+=1
            if self.over_counter == 10:
                sound.gameoversfx.play()
                self.over_counter+=1


        elif self.hit:
            sprite_sheet= "hit"
            sound.hitsfx.play()
            

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

class MusicPlayer:
    def __init__(self,path) -> None:
        self.music_files = [f for f in listdir(path) if isfile(join(path,f)) and f.endswith(".mp3")]
        self.music_files = [join(path,m) for m in self.music_files]
        self.current_song_index = 0
        self.volume = 0.6
        self.iplay = True
        self.loadmetadata()
        self.imageloader()
        
    def loadmetadata(self):
        self.metadata = {}
        with open("assets\\Music\\Meta.json","r") as file:
            self.metadata = json.load(file)
            file.close()

    def imageloader(self):
        self.imageloc = requests.get(self.metadata["music"][self.current_song_index]["img"])
        self.image = pygame.image.load(BytesIO(self.imageloc.content)).convert_alpha()
        self.image = pygame.transform.scale(self.image,(80,80))
        self.image = round_image(self.image, 10)

    def play(self):
        pygame.mixer.music.load(self.music_files[self.current_song_index])
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(nextsong)
        pygame.mixer.music.set_volume(self.volume*MASTER_VOLUME)
        self.imageloader()
        print(pygame.mixer.music.get_volume())

    def playpause(self):
        self.iplay = not self.iplay
        if self.iplay:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        

    def next(self):
        if self.current_song_index == (len(self.music_files)-1) :
            self.current_song_index = 0
        else:
            self.current_song_index+=1
        self.play()

    def prev(self):
        if self.current_song_index == 0:
            self.current_song_index =len(self.music_files) - 1
        else:
            self.current_song_index -= 1
        self.play()

    def changevolume(self, volume):
        self.volume -= volume
        pygame.mixer.music.set_volume(self.volume*MASTER_VOLUME)

    def setVolume(self, volume):
        self.volume = volume
        pygame.mixer.music.set_volume(self.volume*MASTER_VOLUME)
    
    def draw(self,win):
        if screen=="main menu":
            win.blit(self.image,(WIDTH-390,HEIGHT-158))
            draw_text(win,self.metadata["music"][self.current_song_index]["Title"],22,(0,0,0,255),WIDTH-290,HEIGHT-155,False,(400,30))
            draw_text(win,self.metadata["music"][self.current_song_index]["Author"],18,(20,20,20,255),WIDTH-290,HEIGHT-130,False,(400,30))
            draw_text(win,"Press N for Next Song",18,(0,0,0,255),WIDTH-385,HEIGHT-105,True,(400,30))
        

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
        blocks.extend([pygame.transform.scale2x(get_block(size/2,(loc[0]+20,loc[1]+20))) for loc in blocks_loc])

        
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


def menu_button_pressed(menu,no,bgimg = None):
    global PAUSED, window, menu_run, run
    if menu == "pause":
        if no == 0:
            PAUSED = False
        if no == 1:
            PAUSED = False
            main(window)
        if no ==2:
            PAUSED = False
            settings(window,bgimg)
        
        if no == 4:
            run = False
            PAUSED = False
            main_menu(window)

    elif menu == "main":
        if no == 0:
            main(window)
        if no == 3:
            menu_run = False
        if no == 2:
            menu_run = False
            settings(window,bgimg)
                        
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

def draw (window,bg,bglist,pausebutton, restart, close, player,objects,bars,gameEnd,offset_x):
   
    global PAUSED,run
    window.fill(GREEN)
    window.blit(bg["bluesky"][0],(0,0))
    
    
    for compo in bglist:
        for i in range(-4,9,1):
            window.blit(bg[compo][0],((bg[compo][1][0]-4)*i - offset_x*bglist[compo], bg[compo][1][1]))
    

    player.draw(window, offset_x)
    for obj in objects:
        obj.draw(window, offset_x)

    

    for bar in bars:
        bar.draw(window,player.health)
    if player.health == 0:
        window.blit(gameEnd,((WIDTH-600)/2, (HEIGHT-309)/2))
        if restart.draw(window):
            main(window)
        if close.draw(window):
            run = False
            main_menu(window)

    if pausebutton.draw(window):
        PAUSED = True
        pausesurf = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        pausesurf.fill((30,30,30,150))
        window.blit(pausesurf,(0,0))

    
   

        
    pygame.display.update()

def draw_text(surface,text,size,color,x,y,fit = False, fit_size = (0,0)):
    font = pygame.font.Font(font_path,size) #pygame.font.SysFont("comicsans", size) 
    img = font.render(text,False,color).convert_alpha()
    #img.set_alpha(255)
    if fit:
        surface.blit(img,(x+(fit_size[0]-img.get_width())/2,y+(fit_size[1]-img.get_height())/2))
    else:
        surface.blit(img,(x,y))

def menu_draw(surface,menu, buttons,bgimg = None):
    for i in range(len(buttons)):
        if buttons[i].draw(surface):
            menu_button_pressed(menu,i,bgimg)
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
        else:
            player.land =0 
    
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

#global objects
music = MusicPlayer("assets\\Music")
music.play()
sound = SoundPlayer()
            

#Screen Functions
def main(window):
    """Opens the game Screen"""
    global PAUSED, run, music, screen
    screen = "game"
    
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
    pausebuttonimage = pygame.image.load("assets\Menu\Buttons\Pause.png").convert_alpha()
    pausebutton = Button(20,20,pausebuttonimage,1)
    restartimage = pygame.image.load("assets\Menu\Buttons\Restart.png").convert_alpha()
    restart = Button((WIDTH-restartimage.get_width()*9)/2,(HEIGHT+309)/2,restartimage,3)
    closeimage = pygame.image.load("assets\Menu\Buttons\Close.png").convert_alpha()
    close = Button((WIDTH-restartimage.get_width())/2,(HEIGHT+309)/2,closeimage,4.2)
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

            if event.type == nextsong:
                music.next()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    PAUSED = not PAUSED
                    if PAUSED:
                        pausesurf = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
                        pausesurf.fill((30,30,30,150))
                        window.blit(pausesurf,(0,0))
                if event.key == pygame.K_n :
                    music.next()
                if event.key == pygame.K_p:
                    music.prev()
                if event.key == pygame.K_3:
                    music.changevolume(0.01)
                if event.key == pygame.K_9:
                    music.changevolume(-0.01)
                if event.key == pygame.K_k:
                    music.playpause()
                
                
                


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
            draw(window, bg, bglist,pausebutton, restart, close, player, objects,bars,gameEnd, offset_x)

            if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0 ):
                offset_x += player.x_vel


    pygame.quit()
    quit()

def main_menu(window):
    """Opens the main menu screen"""
    global music, screen
    screen = "main menu"
    window.fill((0,0,0)) #fixes residue from previous screen
    bg = pygame.image.load("assets\\Background\\bg.jpg").convert_alpha()
    bgimg = pygame.transform.scale(bg,(WIDTH,HEIGHT))
    bgimg.set_alpha(100)
    window.blit(bgimg,(0,0))
    bgimg.set_alpha(20)
    
    musicBg = pygame.image.load("assets\\Menu\\Buttons\\musicbg1.png").convert_alpha()
    musicBg.set_alpha(65)
    #window.blit(musicBg,(WIDTH-400,HEIGHT-165))
    
    buttonimage = pygame.image.load("assets\\Menu\\Buttons\\MMButton2.png").convert_alpha()
    buttonimage.set_alpha(99)
    menu_buttons = [Button(100,((HEIGHT- 495)/2 + (141*i)),buttonimage,1) for i in range(4)]
    menu_action = ["PLAY","Progress","Settings","Quit"]
    
    global menu_run
    menu_run = True
    while menu_run:
        clock.tick(FPS)
        for event in pygame.event.get():

            if event.type == nextsong:  #Auto Play Next Song
                music.next()

            if event.type == pygame.QUIT:
                menu_run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n :
                    music.next()
                if event.key == pygame.K_p:
                    music.prev()
                if event.key == pygame.K_3:
                    music.changevolume(0.01)
                if event.key == pygame.K_9:
                    music.changevolume(-0.01)
                if event.key == pygame.K_k:
                    music.playpause()
        window.blit(bgimg,(0,0))
        window.blit(musicBg,(WIDTH-400,HEIGHT-165))
        
        
        
        music.draw(window)
        for i in range(4):
            draw_text(window,menu_action[i],32,(255,255,255,255),100,((HEIGHT- 495)/2 + (141*i)),True,(300,72))
            draw_text(window,menu_action[i],32,(150,200,255,255),100,((HEIGHT- 495)/2 + (141*i)),True,(300,72)) #(177,213,238)
        menu_draw(window,"main",menu_buttons,bgimg)
        
    

def  progress(window):
    """Opens the progress screen"""

def settings(window, bgimg = None):
    #window.fill((0,0,0)) #fixes residue from previous screen
    
    global menu_run,selected_character, music, sound, screen, MASTER_VOLUME, SoundVolume

    if screen == "main menu":
        window.fill((0,0,0))

    #if screen == "game":
        #window.fill((1, 122, 255))
    """Opens the settings screen"""
    settingimg = pygame.image.load("assets\\Menu\\settingscreen.png").convert_alpha()
    
    window.blit(settingimg,((WIDTH-settingimg.get_width())/2,(HEIGHT-settingimg.get_height()-90)/2))
    settingimg.set_alpha(50)
    if bgimg:
        bgimg.set_alpha(100)
        window.blit(bgimg,(0,0))
        bgimg.set_alpha(20)

    pygame.display.update()
    srun = True
    Options=["Audio","Controls","Character"]
    selected_option = 0
    buttonfont = pygame.font.SysFont("comicsans", 32)
    selectedfont = pygame.font.SysFont("comicsans", 32, bold=True)
    settingfont = pygame.font.SysFont("comicsans", 25)
    
    
    optionimg= [buttonfont.render(i,1,(30,30,30)) for i in Options]
        

    backimg = pygame.image.load("assets\\Menu\\Buttons\\arrow-left.png").convert_alpha()
    backbutton = Button((WIDTH-settingimg.get_width())/2 + 50 ,(HEIGHT-settingimg.get_height()-100)/2 + 10,backimg,1)
    characterimg = [pygame.image.load(join("assets","MainCharacters",c,"fall.png")).convert_alpha() for c in characters]
    
    characterimg = [pygame.transform.scale(c,(100,100)) for c in characterimg]
    characterbutton = [Button((WIDTH-settingimg.get_width())/2 + 60 + (200*i),(HEIGHT-settingimg.get_height()-100)/2 + 100,characterimg[i],1) for i in range(4)]
    musicBg = pygame.image.load("assets\\Menu\\Buttons\\musicbg1.png").convert_alpha()
    masterVolumeSlider = SettingSlider(window,WIDTH-900,+HEIGHT-530,400,20,txt_colour = (0,0,0),initial=MASTER_VOLUME*100)
    musicSettingSlider = SettingSlider(window,WIDTH-900,+HEIGHT-450,400,20,txt_colour = (0,0,0),initial=music.volume*100)
    soundSettingSlider = SettingSlider(window,WIDTH-900,+HEIGHT-370,400,20,txt_colour = (0,0,0),initial=SoundVolume*100)
    musicBg.set_alpha(65)
    text = buttonfont.render("Current Character",1,(0,0,0))
    optionbutton = [Button((WIDTH-settingimg.get_width())/2 + 200 + (200*i),(HEIGHT-settingimg.get_height()-100)/2 + 10,optionimg[i],1) for i in range(3)]
    while srun:
        clock.tick(FPS)
        selectedoptionimg = selectedfont.render(Options[selected_option],1,(0,0,0)) 
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                srun = False
                menu_run = False
                pygame.quit()
                quit()

            
            if event.type == nextsong:
                music.next()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    srun = False
                    masterVolumeSlider.destroy()
                    musicSettingSlider.destroy()
                    soundSettingSlider.destroy()
                    if screen == "main menu":
                        main_menu(window)
                    break
        if bgimg:
            window.blit(bgimg,(0,0))
        
        window.blit(settingimg,((WIDTH-settingimg.get_width())/2,(HEIGHT-settingimg.get_height()-90)/2))
        for i in range(len(optionbutton)):
            if i != selected_option:
                if optionbutton[i].draw(window):
                    selected_option = i
        window.blit(selectedoptionimg,((WIDTH-settingimg.get_width())/2 + 200 + (200*selected_option),(HEIGHT-settingimg.get_height()-100)/2 + 10))

        if backbutton.draw(window):
            srun = False
            masterVolumeSlider.destroy()
            musicSettingSlider.destroy()
            soundSettingSlider.destroy()
            if screen == "main menu":
                main_menu(window)
            
                
               
        pygame.display.update()
        window.blit(musicBg,(WIDTH-400,HEIGHT-165))
        music.draw(window)
        if selected_option == 0:
            mastertxtimg = settingfont.render("Master",False,(0,0,0)).convert_alpha()
            window.blit(mastertxtimg,(WIDTH-1000,+HEIGHT-540))
            masterVolumeSlider.update(events)
            MASTER_VOLUME = masterVolumeSlider.getValue()/100
            musictxtimg = settingfont.render("Music",False,(0,0,0)).convert_alpha()
            window.blit(musictxtimg,(WIDTH-1000,+HEIGHT-460))
            musicSettingSlider.update(events)
            music.setVolume(musicSettingSlider.getValue()/100)
            soundtxtimg = settingfont.render("Sound",False,(0,0,0)).convert_alpha()
            window.blit(soundtxtimg,(WIDTH-1000,+HEIGHT-380))
            soundSettingSlider.update(events)
            SoundVolume = soundSettingSlider.getValue()/100
            sound.setVolume(SoundVolume)
            
         
        if selected_option == 2:
            global selected_character
            
            window.blit(text,((WIDTH-settingimg.get_width())/2 + 60,(HEIGHT-settingimg.get_height()-100)/2 + 300)) 
            #draw_text(window,"Current Character",32,(0,0,0,255),(WIDTH-settingimg.get_width())/2 + 60,(HEIGHT-settingimg.get_height()-100)/2 + 300,False,(400,30))
            window.blit(characterimg[selected_character],((WIDTH-settingimg.get_width())/2 + 60 + (200*2),(HEIGHT-settingimg.get_height()-100)/2 + 250))
            for i in range(4):
                if characterbutton[i].draw(window):
                    selected_character = i
                    
                    break
                


            


if __name__ == "__main__":
    main_menu(window)

    