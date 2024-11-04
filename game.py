import pygame
import input
from player import Player
from sprite import sprites,Sprite
from map import TileKind,Map
from camera import create_screen

pygame.init()

screen = create_screen(960,640,"Diggi")
# Game loop
running = True
player = Player("images/drill.png",0,0)
tile_kinds = [
    TileKind("dirt", "images/dirts.webp",False,32),
    TileKind("grass","images/dirts.webp",False,32)
]
map = Map("maps/start.map", tile_kinds, 32)

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            input.keys_down.add(event.key)
        elif event.type == pygame.KEYUP:
            input.keys_down.remove(event.key)

    # Update Code
    player.update()

    # Draw Code
    screen.fill((0, 0, 0))
    map.draw(screen)
    for s in sprites:
        s.draw(screen)
    pygame.display.flip()

    pygame.time.delay(17)

pygame.quit()