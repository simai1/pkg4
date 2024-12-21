import pygame
import sys
import math
from config import *
from algorithms import *
from figure import Layer, Container

GREY = (215, 219, 230)
YELLOW = (254, 246, 201)
BROWN = (104, 77, 68)
FLESH = (210, 191, 161)
DARK_GREY = (118, 112, 112)
BLACK = (0, 4, 0)


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
            container.add_layer(Layer((128, 412), (565, 412), (565, 522), DARK_GREY, 1, visible=True, center=0))
            container.add_layer(Layer((128, 412), (128, 522), (565, 522), DARK_GREY, 1, visible=True, center=(150, 240)))
            # Земля
            # Layer(pixel_map, (128, 412), (565, 412), (565, 522), DARK_GREY).draw()
            # Layer(pixel_map, (128, 412), (128, 522), (565, 522), DARK_GREY).draw()
            # # Ноги
            # Layer(pixel_map, (237, 465), (293, 401), (308, 465), FLESH).draw()
            # Layer(pixel_map, (307, 413), (354, 391), (322, 447), FLESH).draw()
            # Layer(pixel_map, (312, 464), (354, 391), (365, 464), FLESH).draw()
            #
            #
            #
            # # Крыло и хвост
            # Layer(pixel_map, (393, 344), (484, 436), (324, 418), GREY).draw()
            # Layer(pixel_map, (276, 220), (384, 237), (364, 364), GREY).draw()
            #
            # # Лицо
            # Layer(pixel_map, (157, 182), (173, 182), (164, 171), BLACK).draw()
            # Layer(pixel_map, (231, 171), (238, 158), (248, 171), BLACK).draw()
            # Layer(pixel_map, (178, 168), (217, 168), (203, 253), BROWN).draw()
            # Layer(pixel_map, (235, 146), (219, 166), (259, 166), YELLOW, center=(236, 154)).draw()
            # Layer(pixel_map, (242, 186), (219, 166), (259, 166), YELLOW).draw()
            # Layer(pixel_map, (163, 161), (152, 178), (178, 178), YELLOW, center=(162, 167)).draw()
            # Layer(pixel_map, (167, 197), (152, 178), (178, 178), YELLOW).draw()
            #
            #
            # # Тело
            #
            # Layer(pixel_map, (140, 126), (186, 231), (140, 231), GREY).draw()
            # Layer(pixel_map, (140, 126), (233, 126), (233, 338), GREY, center=(220, 228)).draw()
            # Layer(pixel_map, (308, 126), (233, 126), (233, 271), GREY).draw()
            # Layer(pixel_map, (308, 126), (233, 271), (308, 271), GREY, center=(299, 196)).draw()
            # Layer(pixel_map, (308, 143), (384, 271), (308, 271), GREY).draw()
            # Layer(pixel_map, (377, 271), (233, 380), (233, 271), GREY).draw()
            # Layer(pixel_map, (377, 271), (233, 380), (377, 380), GREY).draw()
            # Layer(pixel_map, (265, 433), (237, 380), (377, 380), GREY).draw()
            # Layer(pixel_map, (377, 271), (410, 380), (377, 380), GREY).draw()

            # Layer(pixel_map, (361, 233), (384, 237), (380, 265), GREY).draw()
            container.analyze_and_fill()
            f = False

        pygame.display.flip()

        # Задержка для замедления отрисовки
        # pygame.time.delay(DELAY_MS)


if __name__ == "__main__":
    main()
