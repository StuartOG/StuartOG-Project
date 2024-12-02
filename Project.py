import pygame
import json
import math
from pygame.math import Vector2
import random

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GREY = (128, 128, 128)

TURRET_DATA = [
    {   
        #1
        "range": 120,
        "cooldown": 1500,
    },
    {
        #2
        "range": 140,
        "cooldown": 1200,
    },
    {
        #3
        "range": 160,
        "cooldown": 1000,
    },
    {
        #4
        "range": 180,
        "cooldown": 800,
    }
]

TURRET_MAXLVL = 4

ENEMY_SPAWN_DATA = [
  {
    #1
    "tier 1": 15,
    "tier 2": 0,
    "tier 3": 0,
    "tier 4": 0
  },
  {
    #2
    "tier 1": 30,
    "tier 2": 0,
    "tier 3": 0,
    "tier 4": 0
  },
  {
    #3
    "tier 1": 20,
    "tier 2": 5,
    "tier 3": 0,
    "tier 4": 0
  },
  
  {
    "#4": {
      "tier 1": 30,
      "tier 2": 15,
      "tier 3": 0,
      "tier 4": 0
    }
  },
  {
    "#5": {
      "tier 1": 5,
      "tier 2": 20,
      "tier 3": 0,
      "tier 4": 0
    }
  },
  {
    "#6": {
      "tier 1": 15,
      "tier 2": 15,
      "tier 3": 4,
      "tier 4": 0
    }
  },
  {
    "#7": {
      "tier 1": 20,
      "tier 2": 25,
      "tier 3": 5,
      "tier 4": 0
    }
  },
  {
    "#8": {
      "tier 1": 10,
      "tier 2": 20,
      "tier 3": 15,
      "tier 4": 0
    }
  },
  {
    "#9": {
      "tier 1": 15,
      "tier 2": 10,
      "tier 3": 5,
      "tier 4": 0
    }
  },
  {
    "#10": {
      "tier 1": 0,
      "tier 2": 100,
      "tier 3": 0,
      "tier 4": 0
    }
  },
  {
    "#11": {
      "tier 1": 5,
      "tier 2": 10,
      "tier 3": 12,
      "tier 4": 2
    }
  },
  {
    "#12": {
      "tier 1": 0,
      "tier 2": 15,
      "tier 3": 10,
      "tier 4": 5
    }
  },
  {
    "#13": {
      "tier 1": 20,
      "tier 2": 0,
      "tier 3": 25,
      "tier 4": 10
    }
  },
  {
    "#14": {
      "tier 1": 15,
      "tier 2": 15,
      "tier 3": 15,
      "tier 4": 15
    }
  },
  {
    "#15": {
      "tier 1": 25,
      "tier 2": 25,
      "tier 3": 25,
      "tier 4": 25
    }
  }
  ]

ENEMY_DATA = {
    "tier 1": {
    "health": 10,
    "speed": 2
  },
    "tier 2": {
    "health": 15,
    "speed": 3
  },
    "tier 3": {
    "health": 20,
    "speed": 4
  },
    "tier 4": {
    "health": 30,
    "speed": 6
  }
}
 
pygame.init()
 
# Set the width and height of the screen [width, height]
rows = 12
cols = 14
pixel_size = 64
side_panel = 200

spawn_cooldown = 400

size = (cols*pixel_size + side_panel, rows*pixel_size)
screen = pygame.display.set_mode(size)

animation_steps = 8
animation_delay = 15
 
pygame.display.set_caption("Otis' Computer Science Project")

#game variables
last_enemy_spawn = pygame.time.get_ticks()
placing_turrets = False
selected_turret = None

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
enemy_images = {
    "tier 1" : pygame.image.load('assets/enemy_1.png').convert_alpha(),
    "tier 2" : pygame.image.load('assets/enemy_2.png').convert_alpha(),
    "tier 3" : pygame.image.load('assets/enemy_3.png').convert_alpha(),
    "tier 4" : pygame.image.load('assets/enemy_4.png').convert_alpha()
    }   
#buy turret button
buy_turret_image = pygame.image.load('assets/buy_turret.png').convert_alpha()
#cancel buying turret button
cancel_turret_image = pygame.image.load('assets/cancel.png').convert_alpha()
#upgrade turret turret button
upgrade_turret_image = pygame.image.load('assets/upgrade_turret.png').convert_alpha()




#creating map class
class Map():
    def __init__(self, data, map_image):    
        self.level = 1
        self.tile_map = []
        self.level_data = data
        self.image = map_image
        self.enemy_list = []
        self.spawned_enemies = 0
       
    #end constructor
    def process_data(self):
        #look through data to extract relevant info
        for layer in self.level_data["layers"]:
            if layer["name"] == "Tile Layer 1":
                self.tile_map = layer["data"]
    
    def process_enemies(self):
        enemies = ENEMY_SPAWN_DATA[self.level - 1]
        for enemy_type in enemies:
            enemies_to_spawn = enemies[enemy_type]
            for enemy in range(enemies_to_spawn):
                self.enemy_list.append(enemy_type)
        #shuffle the list
        random.shuffle(self.enemy_list)
                

    
    def draw(self, surface):
        surface.blit(self.image, (0, 0))

#create map
world = Map(world_data, map_image)
world.process_data()
world.process_enemies()

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

def select_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // pixel_size
    mouse_tile_y = mouse_pos[1] // pixel_size
    for turret in tower_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret


#Creating Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, images, waypoints):
        super().__init__()

        self.waypoints = waypoints
        self.position = Vector2(self.waypoints[0])
        self.target_waypoint = 1
        self.speed = ENEMY_DATA.get(enemy_type)["speed"]
        self.health = ENEMY_DATA.get(enemy_type)["health"]
        self.angle = 0
        self.original_image = images.get(enemy_type)
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
            if self.target_waypoint <= len(waypoints):
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
        self.upgrade_level = 1
        self.range = TURRET_DATA[self.upgrade_level-1].get("range")
        self.cooldown = TURRET_DATA[self.upgrade_level-1].get("cooldown")
        self.last_shot = pygame.time.get_ticks()
        self.selected = False
        self.target = None
        
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

        #update image
        self.angle = 90
        self. original_image = self.animation_list[self.frame_index]
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        #creating transparent circle to show range
        self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.range_image, GREY, (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center


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
        self.original_image = self.animation_list[self.frame_index]
        #check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > animation_delay:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            #check if animation ahs finished
            if self.frame_index >= len(self.animation_list):
                self.frame_index = 0
                self.last_shot = pygame.time.get_ticks()
                self.target = None
    
    def pick_target(self, enemy_group):
        #find an enemy to target
        x_dist = 0
        y_dist = 0
        #check distance to each enemy to see if it is in range
        for enemy in enemy_group:
            x_dist = enemy.position[0] - self.x
            y_dist = enemy.position[1] - self.y
            dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
            if dist < self.range:
                self.target = enemy

                self.angle = math.degrees(math.atan2(-y_dist, x_dist)) 


    def update(self, enemy_group):
        if self.target:
            self.play_animation()
        else:
            if pygame.time.get_ticks() - self.last_shot > self.cooldown:
                self.pick_target(enemy_group)

    def upgrade(self):
        self.upgrade_level += 1
        self.range = TURRET_DATA[self.upgrade_level-1].get("range")
        self.cooldown = TURRET_DATA[self.upgrade_level-1].get("cooldown")

        #change the circle for the new level
        self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.range_image, GREY, (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center


    
    #drawing function for transparent range circle
    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        if self.selected:
            surface.blit(self.range_image, self.range_rect)

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


#creating button to place the tower
tower_button = Buttons(cols*pixel_size + 30, 120, buy_turret_image, True)

#creating button to cancel placing the tower
cancel_button = Buttons(cols*pixel_size + 50, 180, cancel_turret_image, True)

#creating button to cancel placing the tower
upgrade_button = Buttons(cols*pixel_size + 5, 180, upgrade_turret_image, True)


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
        #check if mouse is on the game area
        if mouse_pos[0] < cols*pixel_size and mouse_pos[1] < rows*pixel_size:
            #checks if player can place turret
            if placing_turrets == True:
                create_turret(mouse_pos)
            else: 
                selected_turret = select_turret(mouse_pos)
        
    # --- Game logic should go here
    #updating all sprites
    all_sprites.update()

    #updating towers
    tower_group.update(enemy_group)

    
    #highlight selected turret
    if selected_turret:
        selected_turret.selected = True
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

    #spawn enemies
    if pygame.time.get_ticks()- last_enemy_spawn > spawn_cooldown:
        if world.spawned_enemies < len(world.enemy_list):   
            enemy_type = world.enemy_list[world.spawned_enemies]
            enemy = Enemy(enemy_type, enemy_images, waypoints)
            enemy_group.add(enemy)
            world.spawned_enemies += 1
            last_enemy_spawn = pygame.time.get_ticks()

    enemy_group.update()

    if tower_button.draw(screen):
        placing_turrets = True
    #if placing turrets then show cancel button as well
    if placing_turrets == True:
        if cancel_button.draw(screen):
            placing_turrets = False    
    if selected_turret:
        if selected_turret.upgrade_level < TURRET_MAXLVL:
            if upgrade_button.draw(screen):
                selected_turret.upgrade()



    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
pygame.quit()