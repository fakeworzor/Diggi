import pygame

pygame.init() # intialize pygame

# Create screen
screen= pygame.display.set_mode((960,640))

# Camera
camera = pygame.Rect(0,0,0,0)

def create_screen(width, height, title):
    pygame.display.set_caption(title)

    screen = pygame.display.set_mode((width,height))
    camera.width = width
    camera.height = height
    return screen

# Title and Icon
pygame.display.set_caption("Diggi") # Title
icon = pygame.image.load("drill.png")
pygame.display.set_icon(icon) # Icon

# Player
width_player = 60
height_player = 80
playerX = 460
playerY = 480
playerX_change = 0
playerY_change = 0
speed = 3

playerImg = pygame.image.load("drill.png")
playerImg = pygame.transform.scale(playerImg, (width_player, height_player))
pygame.display.flip()
def player(x,y):
    screen.blit(playerImg, (playerX, playerY))

# Press
pressW = False
pressA = False
pressS = False
pressD = False

# FPS
fps = pygame.time.Clock()
fps.tick(120)


# Game loop
running = True
while running:

    # create background backup
    screen.fill((0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard Control
        # Press Key
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                playerX_change = -speed
                pressA = True
            if event.key == pygame.K_d:
                playerX_change = speed
                pressD = True
            if event.key == pygame.K_w:
                playerY_change = -speed
                pressW = True
            if event.key == pygame.K_s:
                playerY_change = speed
                pressS = True
        # Let Go of the Key
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                if pressD != True:
                    playerX_change = 0
                pressA = False
            if event.key == pygame.K_d:
                if pressA != True:
                    playerX_change = 0
                pressD = False
            if event.key == pygame.K_w:
                if pressS != True:
                    playerY_change = 0
                pressW = False
            if event.key == pygame.K_s:
                if pressW != True:
                    playerY_change = 0
                pressS = False


    # Background
    background = pygame.image.load("Forest_background.webp")
    screen.blit(background,(0,0))

    # Player
    playerX += playerX_change
    playerY += playerY_change
    player(playerX,playerY)

    # Update for every frame
    pygame.display.update()


