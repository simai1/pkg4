import pygame
import sys
import math

from pygame.gfxdraw import polygon

from config import *
from algorithms import *
from container import Layer, Container

RED = (245, 6, 0)
ORANGE = (252, 205, 2)
YELLOW = (251, 248, 5)
LIME = (162, 226, 4)
GREEN = (13, 149, 59)
DARK_ORANGE = (255, 102, 0)
BROWN = (197, 95, 4)
BLUE = (2, 147, 221)
LIGHT = (199, 231, 234)


def arc_length(radius, angle_start, angle_end):
    # Преобразуем углы из градусов в радианы
    angle_start = math.radians(angle_start % 360)
    angle_end = math.radians(angle_end % 360)

    # Рассчитываем угловую разницу в радианах
    if angle_end >= angle_start:
        theta = angle_end - angle_start
    else:
        theta = (2 * math.pi - angle_start) + angle_end

    # Вычисляем длину дуги
    length = radius * theta
    return length


def draw_canvas(screen, scale, pixel_map, offset_x, offset_y):
    # Заливаем экран белым цветом
    screen.fill((230, 230, 230))
    # Рисуем рамки для каждого пикселя
    for y in range(0, HEIGHT // PIXEL_SIZE):
        for x in range(0, WIDTH // PIXEL_SIZE):
            # Увеличиваем размер пикселя по масштабу
            rect = pygame.Rect((x * PIXEL_SIZE * scale) + offset_x, (y * PIXEL_SIZE * scale) + offset_y,
                               PIXEL_SIZE * scale, PIXEL_SIZE * scale)
            # if scale >= 3:
            #     pygame.draw.rect(screen, (192, 192, 192), rect, 1)  # Обводим серым цветом с шириной 1

            # Если пиксель активен, заливаем его цветом
            if pixel_map[y][x] is not None:  # Проверяем, не является ли цвет пустым
                pygame.draw.rect(screen, pixel_map[y][x], rect)  # Заполнение активных пикселей их цветом

    # Координаты для рисования осей, учитывая масштаб и смещение
    center_x_pixel = (WIDTH // PIXEL_SIZE) // 2
    center_y_pixel = (HEIGHT // PIXEL_SIZE) // 2
    center_x = center_x_pixel * PIXEL_SIZE * scale + offset_x
    center_y = center_y_pixel * PIXEL_SIZE * scale + offset_y

    # Рисуем оси
    # pygame.draw.line(screen, (0, 0, 0), (0, center_y), (WIDTH, center_y), 2)  # Ось X
    # pygame.draw.line(screen, (0, 0, 0), (center_x, 0), (center_x, HEIGHT), 2)  # Ось Y
    #
    # # Рисуем засечки на каждой 20-й ячейке
    # tick_length = 4 * scale  # Увеличенная длина засечки для лучшей видимости
    # tick_thickness = 2  # Толщина засечки
    # for i in range(0, WIDTH // PIXEL_SIZE, 20):
    #     # Засечки по оси X
    #     tick_x = i * PIXEL_SIZE * scale + offset_x
    #     pygame.draw.line(screen, (0, 0, 0), (tick_x, center_y - tick_length), (tick_x, center_y + tick_length),
    #                      tick_thickness)
    #
    # for i in range(0, HEIGHT // PIXEL_SIZE, 20):
    #     # Засечки по оси Y
    #     tick_y = i * PIXEL_SIZE * scale + offset_y
    #     pygame.draw.line(screen, (0, 0, 0), (center_x - tick_length, tick_y), (center_x + tick_length, tick_y),
    #                      tick_thickness)


def create_example_pattern(pixel_map, outline_color, fill_color, algorithm_round, algorithm_fill, _radius, x, y):
    center_x = len(pixel_map[0]) // 2 + int(x * 20)
    center_y = len(pixel_map) // 2 - int(y * 20)
    radius = int(_radius * 20)

    # Возвращаем генераторы для отрисовки контура окружности и заливки
    algorithm_round(pixel_map, (center_x, center_y), radius,
                    outline_color)  # Используем reference_algorithm_round
    algorithm_fill(pixel_map, (center_x, center_y), radius, fill_color, outline_color)


def create_arc_pattern(pixel_map, outline_color, algorithm_round, _radius, x, y, ara, arb):
    # print(f"Длина дуги: {arc_length(_radius, ara, arb)}")
    center_x = len(pixel_map[0]) // 2 + int(x * 20)
    center_y = len(pixel_map) // 2 - int(y * 20)
    radius = int(_radius * 20)  # 3
    algorithm_round(pixel_map, (center_x, center_y), radius, outline_color, ara, arb)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pixel Canvas")

    f = True
    scale = INITIAL_SCALE
    offset_x, offset_y = 0, 0
    dragging = False
    last_mouse_x, last_mouse_y = 0, 0

    # Инициализируем карту пикселей
    pixel_map = [[None for _ in range(WIDTH // PIXEL_SIZE)] for _ in range(HEIGHT // PIXEL_SIZE)]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Управление масштабированием с помощью колесика мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Правая кнопка мыши
                    dragging = True
                    last_mouse_x, last_mouse_y = event.pos  # Сохраняем начальную позицию
                elif event.button == 4:  # Колесо мыши (прокрутка вверх)
                    # Увеличиваем масштаб с фокусировкой на центр координат
                    new_scale = min(scale + 0.1, MAX_SCALE)
                    offset_x -= (WIDTH // 2 - offset_x) * (new_scale / scale - 1)
                    offset_y -= (HEIGHT // 2 - offset_y) * (new_scale / scale - 1)
                    scale = new_scale
                elif event.button == 5:  # Колесо мыши (прокрутка вниз)
                    # Уменьшаем масштаб с фокусировкой на центр координат
                    new_scale = max(scale - 0.1, MIN_SCALE)
                    offset_x -= (WIDTH // 2 - offset_x) * (new_scale / scale - 1)
                    offset_y -= (HEIGHT // 2 - offset_y) * (new_scale / scale - 1)
                    scale = new_scale

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:  # Правая кнопка мыши
                    dragging = False

            # Перемещение холста при перетаскивании
            if event.type == pygame.MOUSEMOTION and dragging:
                mouse_x, mouse_y = event.pos
                offset_x += mouse_x - last_mouse_x
                offset_y += mouse_y - last_mouse_y
                last_mouse_x, last_mouse_y = mouse_x, mouse_y

        draw_canvas(screen, scale, pixel_map, offset_x, offset_y)
        if (f):
            container = Container(pixel_map)

            # голова
            container.add_layer(Layer(polygon=[(467, 15), (346, 261), (588, 261)], color=ORANGE, z_index=1, outline_color=(0,0,0)))
            container.add_layer(Layer(polygon=[(364, 23), (390, 170), (439, 73)], color=RED, z_index=2, outline_color=(0,0,0)))
            container.add_layer(Layer(polygon=[(496, 73), (542, 170), (570, 23)], color=RED, z_index=3, outline_color=(0,0,0)))
            container.add_layer(Layer(polygon=[(432, 126), (407, 178), (458, 178)], color=LIME, z_index=4, outline_color=(0,0,0)))
            container.add_layer(Layer(polygon=[(476, 178), (530, 178), (504, 126)], color=LIME, z_index=5, outline_color=(0,0,0)))
            container.add_layer(Layer(polygon=[(476, 178), (504, 178), (504, 126)], color=GREEN, z_index=6, outline_color=(0,0,0)))
            container.add_layer(Layer(polygon=[(432, 126), (432, 178), (458, 178)], color=GREEN, z_index=7, outline_color=(0,0,0)))
            container.add_layer(Layer(polygon=[(467, 215), (447, 261), (490, 261)], color=YELLOW, z_index=8, outline_color=(0,0,0)))
            # тело
            container.add_layer(Layer(polygon=[(467, 215), (300, 616), (640, 616)], color=DARK_ORANGE, z_index=1, outline_color=(0,0,0)))
            container.add_layer(Layer(polygon=[(396, 526), (351, 616), (436, 616)], color=BROWN, z_index=2, outline_color=(0,0,0)))
            container.add_layer(Layer(polygon=[(539, 526), (498, 616), (580, 616)], color=BROWN, z_index=2, outline_color=(0,0,0)))
            #хвост
            container.add_layer(Layer(polygon=[(329, 546), (300, 616), (42, 546)], color=BLUE, z_index=2, outline_color=(0, 0, 0)))
            container.add_layer(Layer(polygon=[(111, 565), (224, 447), (42, 546)], color=BLUE, z_index=3, outline_color=(0, 0, 0)))
            container.add_layer(Layer(polygon=[(188, 486), (224, 447), (134, 390)], color=BLUE, z_index=4, outline_color=(0, 0, 0)))


            # Выполняем «рисование» (определение видимой области + растеризация)
            container.draw()

            # Layer(pixel_map, (361, 233), (384, 237), (380, 265), GREY).draw()
            f = False

        pygame.display.flip()

        # Задержка для замедления отрисовки
        # pygame.time.delay(DELAY_MS)


if __name__ == "__main__":
    main()
