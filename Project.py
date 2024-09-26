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

animation_steps = 8
animation_delay = 15
 
pygame.display.set_caption("Otis' Computer Science Project")

#game variables
placing_turrets = False

#load json data for level
with open('level.tmj') as file:
    world_data = json.load(file)

#importing the enemy image
#map
map_image = pygame.image.load('assets/levelv3.png').convert_alpha()
#turret spritesheets
turret_sheet = pygame.image.load('assets/turret_1.png').convert_alpha()
#cursor turret
cursor_turret_image = pygame.image.load('assets/cursor_turret.png').convert_alpha()
#enemy
enemy_image = pygame.image.load('assets/enemy_1.png').convert_alpha()
#buttons
buy_turret_image = pygame.image.load('assets/buy_turret.png').convert_alpha()
cancel_turret_image = pygame.image.load('assets/cancel.png').convert_alpha()



#creating map class
class Map():
    def __init__(self, data, map_image):
        self.tile_map = []
        self.level_data = data
        self.image = map_image
       
    #end constructor
    def process_data(self):
        #look through data to extract relevant info
        for layer in self.level_data["layers"]:
            if layer["name"] == "Tile Layer 1":
                self.tile_map = layer["data"]
                

    
    def draw(self, surface):
        surface.blit(self.image, (0, 0))

#create map
world = Map(world_data, map_image)
world.process_data()

def create_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // pixel_size
    mouse_tile_y = mouse_pos[1] // pixel_size
    #calculate the sequential number of the tile
    mouse_tile_num = (mouse_tile_y * cols) + mouse_tile_x
    #check if that tile is grass
    if world.tile_map[mouse_tile_num] == 25:
        #check that there isn't already a turret there
        space_is_free = True
        for turret in tower_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False
            #if it is a free space then create turret
        if space_is_free == True:
            new_turret = Tower(turret_sheet, mouse_tile_x, mouse_tile_y)
            tower_group.add(new_turret)

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
    def __init__(self, sprite_sheet, tile_x, tile_y) -> None:
        super().__init__()
        self.range = 90
        self.cooldown = 1500
        self.last_shot = pygame.time.get_ticks()

        
        #position variables
        self.tile_x = tile_x
        self.tile_y = tile_y
        #calculate center coordinates
        self.x = (self.tile_x + 0.5) * pixel_size
        self.y = (self.tile_y + 0.5) * pixel_size

        #animation variables
        self.sprite_sheet = sprite_sheet
        self.animation_list = self.load_images()
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()


        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        #creating transparent circle to show range
        # self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        # self.range_image.fill((0, 0, 0))
        # self.range_image.set_colorkey((0, 0, 0))
        # pygame.draw.circle(self.range_image, GREY, (self.range, self.range), self.range)
        # self.range_image.set_alpha(100)
        # self.range_rect = self.range_image.get_rect()
        # self.range_rect.center = self.rect.center


    #extracts images from sprite sheet
    def load_images(self):
        size = self.sprite_sheet.get_height()
        animation_list = []
        for x in range(animation_steps):
            temp = self.sprite_sheet.subsurface(x * size, 0, size, size)
            animation_list.append(temp)
        return animation_list
    
    

    def play_animation(self):
        #update image
        self.image = self.animation_list[self.frame_index]
        #check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > animation_delay:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            #check if animation ahs finished
            if self.frame_index >= len(self.animation_list):
                self.frame_index = 0
                self.last_shot = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.last_shot > self.cooldown:
            self.play_animation()

        #creating transparent circle to show range
    
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


#adding enemy to the group
enemy_group.add(enemy)

all_sprites.add(enemy)

#creating button to place the tower
tower_button = Buttons(cols*pixel_size + 30, 120, buy_turret_image, True)

#creating button to cancel placing the tower
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
        
    # --- Game logic should go here
    #updating all sprites
    all_sprites.update()

    #updating towers
    tower_group.update()
    
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

    #mouse click
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_pos = pygame.mouse.get_pos()
        #check if mouse is on the game area
        if mouse_pos[0] < cols*pixel_size and mouse_pos[1] < rows*pixel_size:
            #checks if player can place turret
            if placing_turrets == True:
                create_turret(mouse_pos)

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
pygame.quit()