import pygame
import json
import math
from pygame.math import Vector2

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GREY = (128, 128, 128)
 
pygame.init()
 
# Set the width and height of the screen [width, height]
rows = 12
cols = 14
pixel_size = 64
side_panel = 200

size = (cols*pixel_size + side_panel, rows*pixel_size)
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("Otis' Computer Science Project")

#game variables
placing_turrets = False

#importing the enemy image
#map
map_image = pygame.image.load('assets/levelv3.png').convert_alpha()
#cursor turret
cursor_turret_image = pygame.image.load('assets/cursor_turret.png').convert_alpha()
#enemy
enemy_image = pygame.image.load('assets/enemy_1.png').convert_alpha()
#buttons
buy_turret_image = pygame.image.load('assets/buy_turret.png').convert_alpha()
cancel_turret_image = pygame.image.load('assets/cancel.png').convert_alpha()


#creating map class
class Map():
    def __init__(self, map_image):
        self.image = map_image
       
    #end constructor

    def draw(self, surface):
        surface.blit(self.image, (0, 0))

#create map
world = Map(map_image)


#Creating Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, waypoints):
        super().__init__()

        self.waypoints = waypoints
        self.position = Vector2(self.waypoints[0])
        self.target_waypoint = 1
        self.speed = 2
        self.angle = 0
        self.original_image = image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    #adding movement to the enemy
    def update(self):
        self.move()
        self.rotate()
    
    def move(self):
        self.target = Vector2(self.waypoints[self.target_waypoint])
        self.movement = self.target - self.position
        dist = self.movement.length()
        if dist >= self.speed:
            self.position += self.movement.normalize()
        else:
            if self.target_waypoint <= 8:
                if dist != 0:
                    self.position += self.movement.normalize() 
                self.target_waypoint += 1
            else: self.kill()
        self.rect.center = self.position
        dist = self.movement.length()
    
    def rotate(self):
        dist = self.target - self.position
        self.angle = math.degrees(math.atan2(-dist[1], dist[0]))
        #rotate image and update rectangle
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.position

#creating tower class            
class Tower(pygame.sprite.Sprite):
    def __init__(self, image, position) -> None:
        super().__init__()
        self.range = 90

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = position

        #creating transparent circle to show range
        self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.range_image, GREY, (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    #drawing function for transparent range circle
    def draw(self, surface):
        surface.blit(self.image, self.rect)

#creating buttons
class Buttons(pygame.sprite.Sprite):
    def __init__(self, x, y, image, single_click):
        super().__init__()
        self.clicked = False
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.single_click = single_click

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                #if button is single_click then click is set to true
                if self.single_click:
                    self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
    
        surface.blit(self.image, self.rect)

        return action
    

all_sprites = pygame.sprite.Group()

enemy_group = pygame.sprite.Group()

tower_group = pygame.sprite.Group()

waypoints = [
    (640, 0),
    (640, 190),
    (190, 190),
    (190, 447),
    (447, 447),
    (447, 381),
    (705, 381),
    (705, 640),
    (0, 640),
]
#create enemy
enemy = Enemy(enemy_image, waypoints)



enemy_group.add(enemy)
all_sprites.add(enemy)


tower_button = Buttons(cols*pixel_size + 30, 120, buy_turret_image, True)
cancel_button = Buttons(cols*pixel_size + 50, 180, cancel_turret_image, True)


# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 
# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        #mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            #checking if cursor is in the game area

            if mouse_pos[0] < cols*pixel_size and mouse_pos[1] < rows*pixel_size:
                if placing_turrets == True:
                    tower = Tower(cursor_turret_image, mouse_pos)
                    tower_group.add(tower)
        
    # --- Game logic should go here
    
    all_sprites.update()
    
    # --- Screen-clearing code goes here
 
    # Here, we clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
 
    # If you want a background image, replace this clear with blit'ing the
    # background image.
    screen.fill(WHITE)
 
    # --- Drawing code should go here

    #draw level
    world.draw(screen)
    


    #draw enemy
    enemy_group.draw(screen)

    #draw tower
    tower_group.draw(screen)

    for tower in tower_group:
        tower.draw(screen)
        
    if tower_button.draw(screen):
        placing_turrets = True
    #if placing turrets then show cancel button as well
    if placing_turrets == True:
        if cancel_button.draw(screen):
            placing_turrets     = False    

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
pygame.quit()