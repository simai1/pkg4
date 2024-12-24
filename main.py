# main.py
import pygame
import sys
import math

from pygame.gfxdraw import polygon

from config import *
from algorithms import *
from container import Layer, Container

GREY = (215, 219, 230)
YELLOW = (254, 246, 201)
BROWN = (104, 77, 68)
FLESH = (210, 191, 161)
DARK_GREY = (118, 112, 112)
BLACK = (0, 4, 0)

COLOR_CHOICES = {
    pygame.K_1: YELLOW,
    pygame.K_2: BROWN,
    pygame.K_3: FLESH,
    pygame.K_4: DARK_GREY,
    pygame.K_5: BLACK
}

def arc_length(radius, angle_start, angle_end):
    angle_start = math.radians(angle_start % 360)
    angle_end   = math.radians(angle_end % 360)
    if angle_end >= angle_start:
        theta = angle_end - angle_start
    else:
        theta = (2 * math.pi - angle_start) + angle_end
    length = radius * theta
    return length

def draw_canvas(screen, scale, pixel_map, offset_x, offset_y):
    screen.fill((230, 230, 230))
    for y in range(0, HEIGHT // PIXEL_SIZE):
        for x in range(0, WIDTH // PIXEL_SIZE):
            rect = pygame.Rect((x * PIXEL_SIZE * scale) + offset_x,
                               (y * PIXEL_SIZE * scale) + offset_y,
                               PIXEL_SIZE * scale,
                               PIXEL_SIZE * scale)
            if pixel_map[y][x] is not None:
                pygame.draw.rect(screen, pixel_map[y][x], rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pixel Canvas: Triangles with color selection")

    scale = INITIAL_SCALE
    offset_x, offset_y = 0, 0
    dragging = False
    last_mouse_x, last_mouse_y = 0, 0
    z = 50

    # Создаём ИСХОДНЫЙ (пустой) pixel_map
    empty_map = [[None for _ in range(WIDTH // PIXEL_SIZE)]
                       for _ in range(HEIGHT // PIXEL_SIZE)]
    # Текущая «рабочая» копия
    pixel_map = [row[:] for row in empty_map]

    # Создаём контейнер, передавая ему пустую копию
    container = Container([row[:] for row in empty_map])

    # Список для накопления координат (x, y) трёх точек
    triangle_points = []
    # Цвет по умолчанию
    selected_color = YELLOW

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- клавиатура ---
            if event.type == pygame.KEYDOWN:
                if event.key in COLOR_CHOICES:
                    selected_color = COLOR_CHOICES[event.key]
                    print("Выбранный цвет:", selected_color)

            # --- мышь ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # ЛКМ: добавляем вершину треугольника
                    mx, my = event.pos
                    triangle_points.append((mx, my))
                    if len(triangle_points) == 3:
                        # Создаём новый слой
                        new_layer = Layer(
                            polygon=triangle_points[:],
                            color=selected_color,
                            z_index=z,
                            outline_color=(0,0,0)
                        )
                        z += 1
                        container.add_layer(new_layer)
                        triangle_points.clear()

                        # ВАЖНО: очищаем pixel_map, заново рисуем все слои
                        pixel_map = [row[:] for row in empty_map]  # новая копия пустого
                        container.set_pixel_map(pixel_map)
                        container.draw()

                elif event.button == 3:
                    # Правая кнопка для перемещения
                    dragging = True
                    last_mouse_x, last_mouse_y = event.pos
                elif event.button == 4:
                    # Колёсико вверх (увеличение)
                    new_scale = min(scale + 0.2, MAX_SCALE)
                    offset_x -= (WIDTH // 2 - offset_x) * (new_scale / scale - 1)
                    offset_y -= (HEIGHT // 2 - offset_y) * (new_scale / scale - 1)
                    scale = new_scale
                elif event.button == 5:
                    # Колёсико вниз (уменьшение)
                    new_scale = max(scale - 0.2, MIN_SCALE)
                    offset_x -= (WIDTH // 2 - offset_x) * (new_scale / scale - 1)
                    offset_y -= (HEIGHT // 2 - offset_y) * (new_scale / scale - 1)
                    scale = new_scale

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                mx, my = event.pos
                offset_x += mx - last_mouse_x
                offset_y += my - last_mouse_y
                last_mouse_x, last_mouse_y = mx, my

        # Отрисовка на экран
        draw_canvas(screen, scale, pixel_map, offset_x, offset_y)

        pygame.display.flip()

if __name__ == "__main__":
    main()
