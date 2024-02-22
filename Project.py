import pygame
 
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
 
pygame.init()
 
# Set the width and height of the screen [width, height]
size = (700, 500)
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("Otis' Computer Science Project")

#importing the enemy image
enemy_image = pygame.image.load('enemy_1.png').convert_alpha()

#Creating Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, waypoints):
        super().__init__()

        self.image = image
        self.waypoints = waypoints
        self.position = self.waypoints[0]
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    #adding movement to the enemy
    def update(self):
        self.move()
    
    def move(self):
        self.rect.x += 1


waypoints = [
    (000, 300),
    (150, 300),
    (150, 100),
    (550, 100),
    (550, 300),
    (700, 300)

]

enemy = Enemy(enemy_image, waypoints)

all_sprites = pygame.sprite.Group()

enemy_group = pygame.sprite.Group()




enemy = Enemy(enemy_image, waypoints)
enemy_group.add(enemy)
all_sprites.add(enemy)
 
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
    
    enemy_group.update()

    # --- Screen-clearing code goes here
 
    # Here, we clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
 
    # If you want a background image, replace this clear with blit'ing the
    # background image.
    screen.fill(WHITE)
 
    # --- Drawing code should go here
    
    pygame.draw.lines(screen, BLACK, False, waypoints)
    enemy_group.draw(screen)


    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
pygame.quit()