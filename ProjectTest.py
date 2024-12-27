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

TOWER_DATA = [
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
]

TOWER_MAXLVL = 3

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
animation_steps_shooting = 29
 
pygame.display.set_caption("Otis' Computer Science Project")

#game variables
last_enemy_spawn = pygame.time.get_ticks()
placing_towers = False
selected_tower = None

#load json data for level
with open('level.tmj') as file:
    world_data = json.load(file)

#importing the enemy image
#map
map_image = pygame.image.load('assets/levelv3.png').convert_alpha()
#turret spritesheets
tower_sheet = pygame.image.load('assets/towers_images.png').convert_alpha()
#cursor turret
cursor_tower_image = pygame.image.load('assets/tower_lvl1.png').convert_alpha()
#enemy
enemy_images = {
    "tier 1" : pygame.image.load('assets/enemy_1.png').convert_alpha(),
    "tier 2" : pygame.image.load('assets/enemy_2.png').convert_alpha(),
    "tier 3" : pygame.image.load('assets/enemy_3.png').convert_alpha(),
    "tier 4" : pygame.image.load('assets/enemy_4.png').convert_alpha()
    }   


weapon_spritesheets_idle = []
for x in range(1, TOWER_MAXLVL+1):
    weapon_idle_sheet = pygame.image.load(f'assets/lvl{x}weaponidle.PNG').convert_alpha()
    weapon_spritesheets_idle.append(weapon_idle_sheet)
list(weapon_spritesheets_idle)

weapon_spritesheets_shooting = []
for x in range(1, TOWER_MAXLVL+1):
    weapon_shooting_sheet = pygame.image.load(f'assets/lvl{x}weaponshooting.PNG').convert_alpha()
    weapon_spritesheets_shooting.append(weapon_shooting_sheet)
list(weapon_spritesheets_shooting)

tower_images = []
for x in range(1, TOWER_MAXLVL+1):
    tower_image = pygame.image.load(f'assets/tower_lvl{x}.PNG').convert_alpha()
    tower_images.append(tower_image)


#buy turret button
buy_tower_image = pygame.image.load('assets/buy_tower.png').convert_alpha()
#cancel buying turret button
cancel_tower_image = pygame.image.load('assets/cancel.png').convert_alpha()
#upgrade turret turret button
upgrade_tower_image = pygame.image.load('assets/upgrade_tower.png').convert_alpha()




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
            tower_level = "lvl1"
            new_tower = Tower(tower_level, tower_images, mouse_tile_x, mouse_tile_y)
            tower_group.add(new_tower)
            new_weapon = Weapons(weapon_spritesheets_idle, weapon_spritesheets_shooting, mouse_tile_x, mouse_tile_y)
            weapons_group.add(new_weapon)

def select_tower(mouse_pos):
    mouse_tile_x = mouse_pos[0] // pixel_size
    mouse_tile_y = mouse_pos[1] // pixel_size
    for tower in tower_group:
        if (mouse_tile_x, mouse_tile_y) == (tower.tile_x, tower.tile_y):
            return tower


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
    def __init__(self, tower_level, images, tile_x, tile_y) -> None:
        super().__init__()
        self.upgrade_level = 1
        self.angle = 0
        #position variables
        self.tile_x = tile_x
        self.tile_y = tile_y
        #calculate center coordinates
        self.x = (self.tile_x + 0.5) * pixel_size
        self.y = (self.tile_y + 0.5) * pixel_size
        
        self.tower_level = tower_level
        self.image = images.get(self.tower_level-1)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def upgrade(self):
        self.upgrade_level += 1
        self.image = self.image.get(self.tower_level+self.upgrade_level)

class Weapons(pygame.sprite.Sprite):
    def __init__(self, spritesheets_idle, spritesheets_shooting, tile_x, tile_y):
        super().__init__()

        #animation variables
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.upgrade_level = 1

        #idle animation variables
        self.sprite_sheet_idle = spritesheets_idle
        self.animation_list_idle = self.load_images_idle(self.sprite_sheet_idle[self.upgrade_level - 1])
        #shooting animation variables
        self.sprite_sheet_shooting = spritesheets_shooting
        self.animation_list_shooting = self.load_images_shooting(self.sprite_sheet_shooting[self.upgrade_level - 1])
        #position variables
        self.tile_x = tile_x
        self.tile_y = tile_y
        #calculate center coordinates
        self.x = (self.tile_x + 0.5) * pixel_size
        self.y = (self.tile_y + 0.5) * pixel_size

        #update image
        self.angle = 90
        self.original_image = self.animation_list_idle[self.frame_index]
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)


        self.upgrade_level = 1
        self.range = TOWER_DATA[self.upgrade_level-1].get("range")
        self.cooldown = TOWER_DATA[self.upgrade_level-1].get("cooldown")
        self.last_shot = pygame.time.get_ticks()
        self.selected = False
        self.target = None

        #set range
        self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.range_image, GREY, (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def play_idle_animation(self):
        self.original_image = self.animation_list_idle[self.frame_index]
        if self.frame_index >= len(self.animation_list_idle):
            self.frame.index = 0

    def play_shooting_animation(self):
        #update image
        self.original_image = self.animation_list_shooting[self.frame_index]
        #check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > animation_delay:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            #check if animation has finished
            if self.frame_index >= len(self.animation_list_shooting):
                self.frame_index = 0
                self.last_shot = pygame.time.get_ticks()
                self.target = None
    

    def load_images_idle(self, spritesheet_idle):
        animation_list_idle = []
        for x in range(animation_steps):
            if spritesheet_idle.get_width() >= (x + 1) * 96:
                temp_img = spritesheet_idle.subsurface(x * 96, 0, 96, 96)
                animation_list_idle.append(temp_img)
        return animation_list_idle
    
    def load_images_shooting(self, spritesheet_shooting):
        animation_list_shooting = []
        for x in range(animation_steps_shooting):
            if spritesheet_shooting.get_width() >= (x + 1) * 96:
                temp_img = spritesheet_shooting.subsurface(x * 96, 0, 96, 96)
                animation_list_shooting.append(temp_img)
        return animation_list_shooting
    
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

                self.shooting = True

    def upgrade(self):
        self.upgrade_level += 1
        self.range = TOWER_DATA[self.upgrade_level-1].get("range")
        self.cooldown = TOWER_DATA[self.upgrade_level-1].get("cooldown")

        #upgrade weapon image
        self.animation_list_idle = self.load_images_idle(self.sprite_sheet_idle[self.upgrade_level-1])

        self.animation_list_shooting = self.load_images_shooting(self.sprite_sheet_shooting[self.upgrade_level-1])

        self.original_image = self.animation_list_idle[self.frame_index]

        #change the circle for the new level
        self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.range_image, GREY, (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

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

weapons_group = pygame.sprite.Group()

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
tower_button = Buttons(cols*pixel_size + 30, 120, buy_tower_image, True)

#creating button to cancel placing the tower
cancel_button = Buttons(cols*pixel_size + 50, 180, cancel_tower_image, True)

#creating button to cancel placing the tower
upgrade_button = Buttons(cols*pixel_size + 5, 180, upgrade_tower_image, True)


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
            #checks if player can place tower
            if placing_towers == True:
                create_tower(mouse_pos)
            else: 
                selected_tower = select_tower(mouse_pos)
        
    # --- Game logic should go here
    #updating all sprites
    all_sprites.update()



    # updating weapons
    weapons_group.update(enemy_group)

    
    #highlight selected tower
    if selected_tower:
        selected_tower.selected = True
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

    for weapon in weapons_group:
        weapon.draw(screen)

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
        placing_towers = True
    #if placing turrets then show cancel button as well
    if placing_towers == True:
        if cancel_button.draw(screen):
            placing_towers = False    
    if selected_tower:
        if selected_tower.upgrade_level < TOWER_MAXLVL:
            if upgrade_button.draw(screen):
                selected_tower.upgrade()



    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
pygame.quit()