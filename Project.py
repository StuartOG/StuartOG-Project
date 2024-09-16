import pygame
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
size = (900, 500)
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("Otis' Computer Science Project")

#importing the enemy image
enemy_image = pygame.image.load('enemy_1.png').convert_alpha()

#Creating Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, waypoints):
        super().__init__()

        self.waypoints = waypoints
        self.position = Vector2(self.waypoints[0])
        self.target_waypoint = 1
        self.speed = 1  
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    #adding movement to the enemy
    def update(self):
        self.move()
    
    def move(self):
        self.target = Vector2(self.waypoints[self.target_waypoint])
        self.movement = self.target - self.position
        dist = self.movement.length()
        if dist >= self.speed:
            self.position += self.movement.normalize()
        else:
            if self.target_waypoint <= 4:
                if dist != 0:
                    self.position += self.movement.normalize() 
                self.target_waypoint += 1
            else: self.kill()
        self.rect.center = self.position
        dist = self.movement.length()
        
            
class Tower(pygame.sprite.Sprite):
    def __init__(self, s_width, s_length, position) -> None:
        super().__init__()
        self.range = 90

        self.width = s_width
        self.length = s_length
        self.image = pygame.Surface([self.width, self.length])
        self.image.fill(BLACK) 
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
    def __init__(self, x_pos, y_pos, s_colour):
        super().__init__()
        self.image = pygame.Surface([125, 50])
        self.colour = s_colour
        self.image.fill(s_colour)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x_pos, y_pos)
    

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        return action
    

waypoints = [
    (000, 300),
    (150, 300),
    (150, 100),
    (550, 100),
    (550, 300),
    (700, 300)

]

all_sprites = pygame.sprite.Group()

enemy_group = pygame.sprite.Group()

tower_group = pygame.sprite.Group()

enemy = Enemy(enemy_image, waypoints)

enemy_group.add(enemy)
all_sprites.add(enemy)

tower_button = Buttons(750, 50, RED)
all_sprites.add(tower_button)

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
            tower = Tower(30, 30, mouse_pos)
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
    
    pygame.draw.lines(screen, BLACK, False, waypoints)
    enemy_group.draw(screen)
    tower_group.draw(screen)
    for tower in tower_group:
        tower.draw(screen)
    tower_button.draw(screen)

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
pygame.quit()