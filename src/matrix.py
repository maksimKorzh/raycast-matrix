# packages
import pygame
from math import sin, cos, pi
from random import randrange, randint, shuffle
import sys

# init pygame
pygame.init()
window = pygame.display.set_mode((1366, 768), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# screen
WIDTH = 136
HEIGHT = 76
FOV = pi / 3

# map
MAP_SIZE = 20
MAP_SCALE = 30
MAP_RANGE = MAP_SIZE * MAP_SCALE
MAP_SPEED = (MAP_SCALE / 2) / 10
MAP = (
    '####################'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#       #   #      #'
    '#       #   #      #'
    '#       #   #      #'
    '#       #   #      #'
    '#       #   #      #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '####################'
)

# player
player_x = MAP_SCALE + 20
player_y = MAP_SCALE + 20
player_angle = pi / 3

# fonts
chr_size = 10; chr_font = pygame.font.Font('mincho.ttf', chr_size, bold=True)
fps_size = 16; fps_font = pygame.font.Font('mincho.ttf', fps_size, bold=True)
sys_size = 10; sys_font = pygame.font.SysFont('Monospace Regular', sys_size, bold=True)

# symbols
katakana = [chr(int('0x30a0', 16) + i) for i in range(96)]
dark = [chr_font.render(char, False, (0, 255, 0)) for char in katakana]
light = [chr_font.render(char, False, (0, 255, 0)) for char in katakana]
background = sys_font.render('0', False, (0, 255, 0))
shift_index = 0

row_offset = [randint(4, 12) for col in range(WIDTH)]
chunk_length = [randint(5, 25) for col in range(WIDTH)]

# game loop
while True:
    # escape condition
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

    # get user input
    keys = pygame.key.get_pressed()
    
    # player move offset
    offset_x = sin(player_angle) * MAP_SPEED
    offset_y = cos(player_angle) * MAP_SPEED
    distance_thresh_x = 10 if offset_x > 0 else -10
    distance_thresh_y = 10 if offset_y > 0 else -10

    # handle user input
    if keys[pygame.K_ESCAPE]: pygame.quit(); sys.exit(0);
    if keys[pygame.K_LEFT]: player_angle -= 0.03
    if keys[pygame.K_RIGHT]: player_angle += 0.03
    if keys[pygame.K_UP]:
        dest_x = int(player_y / MAP_SCALE) * MAP_SIZE + int((player_x + offset_x + distance_thresh_x) / MAP_SCALE)
        dest_y = int((player_y + offset_y + distance_thresh_y) / MAP_SCALE) * MAP_SIZE + int(player_x / MAP_SCALE)
        if MAP[dest_x] in ' e': player_x += offset_x
        if MAP[dest_y] in ' e': player_y += offset_y
    if keys[pygame.K_DOWN]:
        dest_x = int(player_y / MAP_SCALE) * MAP_SIZE + int((player_x - offset_x - distance_thresh_x) / MAP_SCALE)
        dest_y = int((player_y - offset_y - distance_thresh_y) / MAP_SCALE) * MAP_SIZE + int(player_x / MAP_SCALE)
        if MAP[dest_x] in ' e': player_x -= offset_x
        if MAP[dest_y] in ' e': player_y -= offset_y

    # fall down incremental offset
    shift_index += 1

    # raycasting
    window.fill((0, 0, 0))
    current_angle = player_angle - (FOV / 2)
    start_x = int(player_x / MAP_SCALE) * MAP_SCALE
    start_y = int(player_y / MAP_SCALE) * MAP_SCALE
    
    # loop over casted rays
    for col in range(WIDTH):
        hit_wall = False
        current_sin = sin(current_angle); current_sin = current_sin if current_sin else 0.000001
        current_cos = cos(current_angle); current_cos = current_cos if current_cos else 0.000001

        # ray hits vertical line
        ray_x, direction_x = (start_x + MAP_SCALE, 1) if current_sin >= 0 else (start_x, -1)
        for i in range(0, MAP_RANGE, MAP_SCALE):
            vertical_depth = (ray_x - player_x) / current_sin
            ray_y = player_y + vertical_depth * current_cos
            map_x = int(ray_x / MAP_SCALE)
            map_y = int(ray_y / MAP_SCALE)
            if current_sin <= 0: map_x += direction_x
            target_square = map_y * MAP_SIZE + map_x
            if target_square not in range(len(MAP)): break
            if MAP[target_square] != ' ': hit_wall = True; break
            ray_x += direction_x * MAP_SCALE

        # ray hits horizontal line
        ray_y, direction_y = (start_y + MAP_SCALE, 1) if current_cos >= 0 else (start_y, -1)
        for i in range(0, MAP_RANGE, MAP_SCALE):
            horizontal_depth = (ray_y - player_y) / current_cos
            ray_x = player_x + horizontal_depth * current_sin
            map_x = int(ray_x / MAP_SCALE)
            map_y = int(ray_y / MAP_SCALE)
            if current_cos <= 0: map_y += direction_y
            target_square = map_y * MAP_SIZE + map_x
            if target_square not in range(len(MAP)): break
            if MAP[target_square] != ' ': hit_wall = True; break
            ray_y += direction_y * MAP_SCALE

        # calculate 3D projection
        depth = vertical_depth if vertical_depth < horizontal_depth else horizontal_depth
        background.set_alpha(50)
        #background.set_alpha(int(255 / depth * 100))
        #dark[0].set_alpha(int(255 / depth * 100))
        depth *= cos(player_angle - current_angle)
        wall_height = int(HEIGHT / (depth / MAP_SCALE))
        ceiling = int(HEIGHT / 2) - wall_height
        floor = HEIGHT - ceiling        

        
        # render scene
        for row in range(HEIGHT):
            if row in range(ceiling, floor): window.blit(background, (col * chr_size, row * chr_size))

            if shift_index >= floor:
                shift_index = 0
                shuffle(row_offset)
                shuffle(chunk_length)
            if row == shift_index:
                for l in range(chunk_length[col]):
                    current_row = (row + row_offset[col] + l)
                    if current_row in range(ceiling, floor):
                        
                        window.blit(dark[0], (col * chr_size, current_row * chr_size))
                    #window.blit(dark[0], (col * 5, (row + row_offset[col] - l - wall_height * 2) * 5))

            # rain bg
            #else: window.blit(dark[13], (col * 5, row * 5))
            
            
                
        current_angle += (FOV / WIDTH)
    
    # fps
    clock.tick(60)
    fps = str(int(clock.get_fps()))
    fps_surface = fps_font.render(fps, False, (255, 255, 255))
    window.blit(fps_surface, (0, 0))
    
    # update display
    pygame.display.flip()
    




















