import pygame_widgets
import pygame

from pygame import gfxdraw
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.progressbar import ProgressBar
import time

class ProgressiveSlider(Slider):
    def __init__(self, win,x,y,width,height,**kwargs):
        super().__init__(win,x,y,width,height,**kwargs)
        self.progress = 0
        self.progressColour = kwargs.get('progressColour',(0,35,255))
        
        
        


    def draw(self):
        if not self._hidden:
            pygame.draw.rect(self.win, self.colour, (self._x, self._y, self._width, self._height))

            if self.vertical:
                if self.curved:
                    pygame.draw.circle(self.win, self.colour, (self._x + self._width // 2, self._y), self.radius)
                    pygame.draw.circle(self.win, self.colour, (self._x + self._width // 2, self._y + self._height),
                                       self.radius)
                circle = (self._x + self._width // 2,
                          int(self._y + (self.max - self.value) / (self.max - self.min) * self._height))
                
                pygame.draw.circle(self.win, self.progressColour, (self._x + self._width // 2, self._y + self._height),
                                   self.radius)
                pygame.draw.rect(self.win, self.progressColour,
                                (self._x, self._y + int(self._height * (1 - self.value/self.max)), self._width, int(self._height * self.value/self.max)))
            else:
                if self.curved:
                    pygame.draw.circle(self.win, self.colour, (self._x, self._y + self._height // 2), self.radius)
                    pygame.draw.circle(self.win, self.colour, (self._x + self._width, self._y + self._height // 2),
                                       self.radius)
                circle = (int(self._x + (self.value - self.min) / (self.max - self.min) * self._width),
                          self._y + self._height // 2)
                
                pygame.draw.circle(self.win, self.progressColour, (self._x, self._y + self._height // 2),
                                       self.radius)
                pygame.draw.rect(self.win, self.progressColour,
                             (self._x, self._y, int(self._width * self.value/self.max)-self.radius, self._height))

            gfxdraw.filled_circle(self.win, *circle, self.handleRadius, self.handleColour)
            gfxdraw.aacircle(self.win, *circle, self.handleRadius, self.handleColour)

class SettingSlider(ProgressiveSlider):
    def __init__(self, win, x, y, width, height, **kwargs):
        super().__init__(win, x, y, width, height, **kwargs)
        self.txt_colour = kwargs.get('txt_colour', (255, 255, 255))
        #self.textbox = TextBox(win, x + width + 20, y, 40, 25, fontSize=15, colour= self.txt_bg_colour, borderColour=self.txt_bg_colour)
        self.txtfont = kwargs.get('txtfont','comicsans')
        self.customfont = kwargs.get('customfont',False)
        if self.customfont:
            self.font = pygame.font.Font(self.txtfont,self._height) #
    
        else:
            self.font= pygame.font.SysFont("comicsans", self._height) 
    def draw(self):
        if self.isEnabled:
            super().draw()
            #self.textbox.draw()
            #self.textbox.setText(str(self.getValue())+'%')

            img = self.font.render(str(self.getValue())+'%',False,self.txt_colour).convert_alpha()
            self.win.blit(img,(self._x + self._width + self._height, self._y-5))
    
    def update(self, events):
        pygame_widgets.update(events)
    
    def destroy(self):
        self.textbox=None

        self.isEnabled=False
        

        


if __name__ == "__main__":

    pygame.init()
    win = pygame.display.set_mode((1000, 600))


    slider = ProgressiveSlider(win, 100, 100, 500, 10, min=0, max=100, step=1, colour = (220,220,220))
    output = TextBox(win, 625, 92, 40, 25, fontSize=15, colour = (255,255,255), borderColour = (255,255,255))
    print(type(slider))
    print(type(output))
    output.disable()  # Act as label instead of textbox

    startTime = time.time()


    def volume_change():
        return slider.getValue() / 100

    #progressBar = ProgressBar(win,100, 100, 500, 10, lambda: volume_change(), curved=True, completedColour=(75, 129, 245), incompletedColour=(255,255,255,0))

    run = True
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                quit()

        win.fill((255, 255, 255))

        output.setText(str(slider.getValue() )+ "%")

        pygame_widgets.update(events)
        pygame.display.update()