# packages
import pygame
from math import sin, cos, pi
from random import randrange, randint, shuffle
import sys

# init pygame
pygame.init()
pygame.mouse.set_visible(False)
window = pygame.display.set_mode((1366, 768), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# screen
WIDTH = 80
HEIGHT = 24
FOV = pi / 3

# map
MAP_SIZE = 12
MAP_SCALE = 30
MAP_RANGE = MAP_SIZE * MAP_SCALE
MAP_SPEED = (MAP_SCALE / 2) / 10 + 3
MAP = list(
    '############'
    '#          #'
    '#  #   #   #'
    '#  #   #   #'
    '#  ### #   #'
    '#    # #   #'
    '#      #   #'
    '#  #####   #'
    '#  #       #'
    '#  #####   #'
    '#          #'
    '############'
)

# player
player_x = MAP_SCALE + 20
player_y = MAP_SCALE + 20
player_angle = pi / 3

# fonts
chr_size = 18; chr_font = pygame.font.Font('mincho.ttf', chr_size)
fps_size = 24; fps_font = pygame.font.SysFont('Monospace Regular', fps_size)

# symbols
katakana = [chr(int('0x30a0', 16) + i) for i in range(96)] + list("0123456789Z")
dark = [pygame.transform.flip(chr_font.render(katakana[char], False, (0, 100, 0), (0, 0, 0)), True, False)
if not katakana[char].isdigit() else chr_font.render(katakana[char], False, (0, 100, 0), (0, 0, 0)) for char in range(107)]
light = [pygame.transform.flip(chr_font.render(katakana[char], False, (0, 200, 0), (0, 0, 0)), True, False)
if not katakana[char].isdigit() else chr_font.render(katakana[char], False, (0, 200, 0), (0, 0, 0)) for char in range(107)]
highlight = [pygame.transform.flip(chr_font.render(katakana[char], False, (0, 255, 140), (0, 0, 0)), True, False)
if not katakana[char].isdigit() else chr_font.render(katakana[char], False, (0, 255,140), (0, 0, 0)) for char in range(107)]


color = [randint(0, 1) for i in katakana]
shift_index = -HEIGHT * 2
shift_index_next = -HEIGHT * 4
row_offset = [randint(-HEIGHT, HEIGHT) for col in range(WIDTH)]
chunk_length = [randint(4, 12) for col in range(WIDTH)]

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
    if keys[pygame.K_LEFT]: player_angle -= 0.1
    if keys[pygame.K_RIGHT]: player_angle += 0.1
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

    # raycasting
    window.fill((0, 0, 0))
    step_angle = player_angle - (FOV / 2)
    start_x = int(player_x / MAP_SCALE) * MAP_SCALE
    start_y = int(player_y / MAP_SCALE) * MAP_SCALE
    
    # loop over casted rays
    for col in range(WIDTH):
        hit_wall = False
        current_sin = sin(step_angle); current_sin = current_sin if current_sin else 0.000001
        current_cos = cos(step_angle); current_cos = current_cos if current_cos else 0.000001

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
        shade = int(150 / depth * 100) if depth > 100 else 150
        depth *= cos(player_angle - step_angle)
        wall_height = int(HEIGHT / (depth / MAP_SCALE))
        ceiling = int(HEIGHT / 2) - wall_height
        floor = HEIGHT - ceiling + 5
        
        # render scene
        for row in range(HEIGHT):
            if row in range(ceiling, floor):
                for l in range(chunk_length[col]):
                    if row + row_offset[col] + l + shift_index in range(ceiling, floor):
                        if l == chunk_length[col] - 1:
                            rand_chr = highlight[randint(0, 106)]
                            rand_chr.set_alpha(shade)
                        else:    
                            rand_chr = light[randint(0, 106)] if color[col] else dark[randint(0, 106)]
                            rand_chr.set_alpha(shade)
                        window.blit(rand_chr, (col * chr_size, (row + row_offset[col] + l + shift_index) * chr_size))
                    if row + row_offset[col] + l + shift_index_next in range(ceiling, floor):
                        if l == chunk_length[col] - 1:
                            rand_chr = highlight[randint(0, 106)]
                            rand_chr.set_alpha(shade)
                        else:
                            rand_chr = light[randint(0, 106)] if color[col] else dark[randint(0, 106)]
                            rand_chr.set_alpha(shade)
                        window.blit(rand_chr, (col * chr_size, (row + row_offset[col] + l + shift_index_next) * chr_size))
        
        # increment angle (next ray)
        step_angle += (FOV / WIDTH)
    
    # update 'code rain' shift offsets
    shift_index += 1
    shift_index_next += 1
    if shift_index == 2 * HEIGHT: shift_index = -2 * HEIGHT
    if shift_index_next == 2 * HEIGHT: shift_index_next = -2 * HEIGHT
    
    # fps
    clock.tick(60)
    fps = str(int(clock.get_fps()))
    fps_surface = fps_font.render(fps, False, (255, 255, 255))
    window.blit(fps_surface, (0, 0))

    # update display
    pygame.display.flip()
    




















