import pygame
import random
import math
from enum import Enum

pygame.init()

# Constants
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
TILE_SIZE = 8 # Default tile size
DESTRUCTION_RADIUS = TILE_SIZE + 10
CHUNK_SIZE = 16  # Number of tiles in a chunk (both x and y)
SURFACE_HEIGHT = 5  # Height of surface in chunks from top

# FPS
clock = pygame.time.Clock()
fps = 60



# Colors and Block Types
class BlockType(Enum):
    AIR = (0, "Air", (0, 0, 0, 0))
    DIRT = (1, "Dirt", (139, 69, 19))
    STONE = (2, "Stone", (128, 128, 128))
    IRON = (3, "Iron", (192, 192, 192))
    GOLD = (4, "Gold", (255, 215, 0))
    DIAMOND = (5, "Diamond", (185, 242, 255))
    EMERALD = (6, "Emerald", (0, 168, 107))
    OIL = (7, "Oil", (53, 53, 53))


# Ore generation chances (out of 100,000)
ORE_CHANCES = {
    BlockType.STONE: 4500,
    BlockType.IRON: 150,
    BlockType.GOLD: 10,
    BlockType.DIAMOND: 5,
    BlockType.EMERALD: 2,
    BlockType.OIL: 100
}

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Camera
camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

# Title and Icon
pygame.display.set_caption("Diggi")
icon = pygame.image.load("drill.png")
pygame.display.set_icon(icon)

# Player
width_player = 60
height_player = 80
playerX = SCREEN_WIDTH // 2
playerY = 0  # Will be set after surface generation
playerX_change = 0
playerY_change = 0
player_angle = 0
speed = 5
angle = 5

playerImg = pygame.image.load("drill.png")
playerImg = pygame.transform.scale(playerImg, (width_player, height_player))


# Particle System
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = random.uniform(-2, 2)
        self.velocity_y = random.uniform(-2, 2)
        self.lifetime = 2  # frames
        self.size = random.randint(2, 6)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, screen, camera):
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x - camera.x), int(self.y - camera.y)),
            int(self.size)
        )


class ParticleManager:
    def __init__(self):
        self.particles = []

    def create_destruction_particles(self, x, y, color):
        for _ in range(10):
            self.particles.append(Particle(x, y, color))

    def update_and_draw(self, screen, camera):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()
            particle.draw(screen, camera)


# Upgrade Station
class UpgradeStation:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE * 2
        self.height = TILE_SIZE * 3
        self.interaction_radius = TILE_SIZE * 3

    def draw(self, screen, camera):
        pygame.draw.rect(
            screen,
            (150, 150, 150),
            (
                self.x - camera.x,
                self.y - camera.y,
                self.width,
                self.height
            )
        )

    def check_interaction(self, player_x, player_y):
        distance = math.sqrt((player_x - (self.x + self.width / 2)) ** 2 +
                             (player_y - (self.y + self.height / 2)) ** 2)
        return distance < self.interaction_radius


# Terrain System
class TerrainChunk:
    def __init__(self, chunk_x, chunk_y, surface_height):
        self.tiles = {}
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.generate(surface_height)

    def generate(self, surface_height):
        for y in range(CHUNK_SIZE):
            for x in range(CHUNK_SIZE):
                world_y = self.chunk_y * CHUNK_SIZE + y

                if world_y < surface_height:
                    # Air above surface
                    self.tiles[(x, y)] = BlockType.AIR
                elif world_y == surface_height:
                    # Surface layer is dirt
                    self.tiles[(x, y)] = BlockType.DIRT
                else:
                    # Underground generation
                    roll = random.randint(1, 100000)
                    current_chance = 0
                    block_type = BlockType.DIRT

                    for ore_type, chance in ORE_CHANCES.items():
                        current_chance += chance
                        if roll <= current_chance:
                            block_type = ore_type
                            break

                    self.tiles[(x, y)] = block_type


class TerrainManager:
    def __init__(self):
        self.chunks = {}
        self.destroyed_tiles = set()
        self.particle_manager = ParticleManager()
        self.surface_height = SURFACE_HEIGHT
        self.upgrade_station = None
        self.generate_initial_chunks()

    def generate_initial_chunks(self):
        # Generate initial chunks around player spawn
        for chunk_x in range(-2, 3):
            for chunk_y in range(-1, 4):
                self.chunks[(chunk_x, chunk_y)] = TerrainChunk(chunk_x, chunk_y, self.surface_height)

        # Create upgrade station
        station_x = SCREEN_WIDTH // 2 - TILE_SIZE
        station_y = (self.surface_height * TILE_SIZE) - (TILE_SIZE * 3)
        self.upgrade_station = UpgradeStation(station_x, station_y)

    def get_chunk_for_position(self, x, y):
        chunk_x = int(x // (CHUNK_SIZE * TILE_SIZE))
        chunk_y = int(y // (CHUNK_SIZE * TILE_SIZE))
        if (chunk_x, chunk_y) not in self.chunks:
            self.chunks[(chunk_x, chunk_y)] = TerrainChunk(chunk_x, chunk_y, self.surface_height)
        return chunk_x, chunk_y

    def destroy_terrain(self, world_x, world_y):
        # Convert world coordinates to tile coordinates
        center_tile_x = int(world_x // TILE_SIZE)
        center_tile_y = int(world_y // TILE_SIZE)
        chunk_x, chunk_y = self.get_chunk_for_position(world_x, world_y)

        # Check tiles in a circle around the destruction point
        for offset_y in range(-2, 3):
            for offset_x in range(-2, 3):
                tile_x = center_tile_x + offset_x
                tile_y = center_tile_y + offset_y

                # Calculate distance to center
                distance = math.sqrt(offset_x ** 2 + offset_y ** 2) * TILE_SIZE
                if distance <= DESTRUCTION_RADIUS:
                    local_chunk_x = tile_x // CHUNK_SIZE
                    local_chunk_y = tile_y // CHUNK_SIZE
                    local_tile_x = tile_x % CHUNK_SIZE
                    local_tile_y = tile_y % CHUNK_SIZE

                    chunk = self.chunks.get((local_chunk_x, local_chunk_y))
                    if chunk:
                        tile = chunk.tiles.get((local_tile_x, local_tile_y))
                        if tile != BlockType.AIR and tile not in self.destroyed_tiles:
                            # # Create particles
                            # particle_x = tile_x * TILE_SIZE + TILE_SIZE // 2
                            # particle_y = tile_y * TILE_SIZE + TILE_SIZE // 2
                            # self.particle_manager.create_destruction_particles(
                            #     particle_x,
                            #     particle_y,
                            #     tile.value[2]
                            # )
                            # Mark tile as destroyed
                            self.destroyed_tiles.add((local_chunk_x, local_chunk_y, local_tile_x, local_tile_y))

    def draw(self, screen, camera):
        # Calculate visible chunk range
        start_chunk_x = int((camera.x - SCREEN_WIDTH) // (CHUNK_SIZE * TILE_SIZE))
        end_chunk_x = int((camera.x + SCREEN_WIDTH * 2) // (CHUNK_SIZE * TILE_SIZE))
        start_chunk_y = int((camera.y - SCREEN_HEIGHT) // (CHUNK_SIZE * TILE_SIZE))
        end_chunk_y = int((camera.y + SCREEN_HEIGHT * 2) // (CHUNK_SIZE * TILE_SIZE))

        # Draw visible chunks
        for chunk_x in range(start_chunk_x, end_chunk_x + 1):
            for chunk_y in range(start_chunk_y, end_chunk_y + 1):
                if (chunk_x, chunk_y) not in self.chunks:
                    self.chunks[(chunk_x, chunk_y)] = TerrainChunk(chunk_x, chunk_y, self.surface_height)

                chunk = self.chunks[(chunk_x, chunk_y)]
                chunk_screen_x = chunk_x * CHUNK_SIZE * TILE_SIZE - camera.x
                chunk_screen_y = chunk_y * CHUNK_SIZE * TILE_SIZE - camera.y

                for (tile_x, tile_y), block_type in chunk.tiles.items():
                    if (chunk_x, chunk_y, tile_x, tile_y) not in self.destroyed_tiles and block_type != BlockType.AIR:
                        pygame.draw.rect(
                            screen,
                            block_type.value[2],
                            (
                                chunk_screen_x + tile_x * TILE_SIZE,
                                chunk_screen_y + tile_y * TILE_SIZE,
                                TILE_SIZE,
                                TILE_SIZE
                            )
                        )

        # Draw upgrade station
        if self.upgrade_station:
            self.upgrade_station.draw(screen, camera)

        # Update and draw particles
        self.particle_manager.update_and_draw(screen, camera)


# Initialize terrain
terrain_manager = TerrainManager()

# Set initial player position on surface
playerY = (terrain_manager.surface_height * TILE_SIZE) - height_player

# Press states
pressW = False
pressA = False
pressS = False
pressD = False



def update_camera(target_x, target_y):
    camera.x = target_x - camera.width // 2 + width_player // 2
    camera.y = target_y - camera.height // 2 + height_player // 2


def player(x, y, angle):
    # Rotate player image
    rotated_player = pygame.transform.rotate(playerImg, angle)
    # Get new rect
    player_rect = rotated_player.get_rect(center=playerImg.get_rect(topleft=(x - camera.x, y - camera.y)).center)
    screen.blit(rotated_player, player_rect)




# Game loop
running = True
while running:
    clock.tick(fps)
    screen.fill((135, 206, 235))  # Sky blue background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard Control
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                playerX_change = -speed
                pressA = True
                player_angle = -angle
            if event.key == pygame.K_d:
                playerX_change = speed
                pressD = True
                player_angle = angle
            if event.key == pygame.K_w:
                playerY_change = -speed
                pressW = True
                player_angle = angle
            if event.key == pygame.K_s:
                playerY_change = speed
                pressS = True
                player_angle = -angle
            if event.key == pygame.K_e:
                # Check for upgrade station interaction
                if terrain_manager.upgrade_station and \
                        terrain_manager.upgrade_station.check_interaction(playerX, playerY):
                    print("Interacting with upgrade station!")

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                if not pressD:
                    playerX_change = 0
                pressA = False
            if event.key == pygame.K_d:
                if not pressA:
                    playerX_change = 0
                pressD = False
            if event.key == pygame.K_w:
                if not pressS:
                    playerY_change = 0
                pressW = False
            if event.key == pygame.K_s:
                if not pressW:
                    playerY_change = 0
                pressS = False

    # Update player position
    playerX += playerX_change
    playerY += playerY_change

    # Destroy terrain around player
    if any([pressW, pressA, pressS, pressD]):
        terrain_manager.destroy_terrain(playerX + width_player / 2, playerY + height_player / 2)

    # Update camera to follow player
    update_camera(playerX, playerY)

    # Draw terrain
    terrain_manager.draw(screen, camera)

    # Draw player
    player(playerX, playerY, player_angle)

    pygame.display.update()

pygame.quit()
