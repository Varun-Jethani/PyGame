import pygame

class Button():
    def __init__(self,x,y,image,scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image,(int(width*scale),int(height*scale)))
        self.hovimage = pygame.transform.scale(image,(int(width*scale),int(height*scale)))
        self.hovimage.fill((68,0,32,128),None,pygame.BLEND_RGBA_MULT)
        self.currentimage = self.image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False

    def draw(self,surface):
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            self.currentimage = self.hovimage
            pygame.mouse.set_cursor(*pygame.cursors.ball)

            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
            
            if pygame.mouse.get_pressed()[0] == 0 and self.clicked == True:
                action = True
                self.clicked = False
        else:
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            self.currentimage = self.image
        

        #draw button
        surface.blit(self.currentimage, (self.rect.x, self.rect.y))

        return action