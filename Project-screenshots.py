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

placing_towers = False

#load json data for level
with open('level.tmj') as file:
    world_data = json.load(file)

screen = pygame.display.set_mode(size)

pixel_size = 64
 
pygame.display.set_caption("Otis' Computer Science Project")

enemy_image = pygame.image.load('assets/enemy_1.png').convert_alpha()

#map
map_image = pygame.image.load('assets/levelv3.png').convert_alpha()

#buy turret button
buy_tower_image = pygame.image.load('assets/buy_tower.png').convert_alpha()
#cancel buying turret button
cancel_tower_image = pygame.image.load('assets/cancel.png').convert_alpha()

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
                

       
    #end constructor

    def draw(self, surface):
        surface.blit(self.image, (0, 0))

#create map
world = Map(world_data, map_image)
world.process_data()

def create_tower(mouse_pos):
    mouse_tile_x = mouse_pos[0] // pixel_size
    mouse_tile_y = mouse_pos[1] // pixel_size
    #calculate the sequential number of the tile
    mouse_tile_num = (mouse_tile_y * cols) + mouse_tile_x
    #check if that tile is grass
    if world.tile_map[mouse_tile_num] == 25:
        #check that there isn't already a turret there
        space_is_free = True
        for tower in tower_group:
            if (mouse_tile_x, mouse_tile_y) == (tower.tile_x, tower.tile_y):
                space_is_free = False
            #if it is a free space then create turret
        if space_is_free == True:
            new_tower = Tower(30, 40, mouse_tile_x, mouse_tile_y)
            tower_group.add(new_tower)


# def select_tower(mouse_pos):
#     mouse_tile_x = mouse_pos[0] // pixel_size
#     mouse_tile_y = mouse_pos[1] // pixel_size
#     for tower in tower_group:
#         if (mouse_tile_x, mouse_tile_y) == (tower.tile_x, tower.tile_y):
#             return tower



#creating enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, waypoints):
        super().__init__()

        self.image = image
        self.waypoints = waypoints
        self.position = Vector2(self.waypoints[0])
        self.target_waypoint = 1
        self.angle = 0
        self.original_image = image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.speed = 1
        self.rect = self.image.get_rect()
        self.rect.center = self.position


    #adding movement to the enemy
    def update(self):
        self.move()
        #self.rotate()
    
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

class Tower(pygame.sprite.Sprite):
    def __init__(self, s_width, s_length, tile_x, tile_y) -> None:
        super().__init__()
        self.width = s_width
        self.range = 90
        self.length = s_length
        self.image = pygame.Surface([self.width, self.length])
        self.image.fill(BLACK) 
        self.rect = self.image.get_rect()

        #position variables
        self.tile_x = tile_x
        self.tile_y = tile_y
        #calculate center coordinates
        self.x = (self.tile_x + 0.5) * pixel_size
        self.y = (self.tile_y + 0.5) * pixel_size

        self.rect.center = (self.x, self.y)

        #creating transparent circle to show range
        self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.range_image, GREY, (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def draw(self, surface):
        surface.blit(self.range_image, self.range_rect)

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
done = False



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

enemy = Enemy(enemy_image, waypoints)

all_sprites = pygame.sprite.Group()

enemy_group = pygame.sprite.Group()

tower_group = pygame.sprite.Group()

#creating button to place the tower
tower_button = Buttons((cols*pixel_size + 30), 120, buy_tower_image, True)

#creating button to cancel placing the tower
cancel_button = Buttons((cols*pixel_size + 50), 180, cancel_tower_image, True)

all_sprites.add(tower_button)


enemy_group.add(enemy)
all_sprites.add(enemy)
 

# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 
# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

            # selected_tower = select_tower(mouse_pos)
    
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

    enemy_group.draw(screen)

    tower_group.draw(screen)

    for tower in tower_group:
        tower.draw(screen)



    #mouse click
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_pos = pygame.mouse.get_pos()
        #check if mouse is on the game area
        if mouse_pos[0] < cols*pixel_size and mouse_pos[1] < rows*pixel_size:
            if placing_towers == True:
                create_tower(mouse_pos)
    

    if tower_button.draw(screen):
        placing_towers = True
    #if placing turrets then show cancel button as well
    if placing_towers == True:
        if cancel_button.draw(screen):
            placing_towers = False 

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
pygame.quit()



















