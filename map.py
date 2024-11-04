import pygame

class TileKind:
    def __init__(self, name, image, is_solid,tile_size):
        self.name = name
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.is_solid = is_solid


class Map:
    def __init__(self, map_file, tile_kinds, tile_size):
        self.tile_kinds = tile_kinds

        # Load the file
        file = open(map_file, "r")
        data = file.read()
        file.close()

        # Set up the tiles from loaded data
        self.tiles = []
        for line in data.split("\n"):
            row = []
            for tile_number in line:
                row.append(int(tile_number))
            self.tiles.append(row)

        # Set the size
        self.tile_size = tile_size

    def draw(self, screen):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                location = (x * self.tile_size, y * self.tile_size)
                image = self.tile_kinds[tile].image
                screen.blit(image, location)
