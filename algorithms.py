import math
import time
import pygame
# from figure import Layer
from config import *

# def init_list():
#     return inited_list

def algorithm_A_fill(pixel_map, center, new_color):
    time.sleep(0.001)
    # global flag1
    x = center[1]
    y = center[0]
    """Заполняет область, начиная с пикселя (x, y) новым цветом."""
    stack = [(x, y)]
    old_color = pixel_map[x][y]  # Получаем цвет текущего пикселя (RGB)
    while stack:
        x, y = stack.pop()
        if XMAX >= x > -XMIN and y <= YMAX and y >= YMIN:
            current_color = pixel_map[x][y]
            # print(x, y)

            # Если цвет текущего пикселя совпадает со старым цветом, меняем его
            # if current_color != new_color and current_color != outline_color and current_color !=(255,0,0):
            if current_color == None:
                # screen.set_at((x, y), new_color)  # Меняем цвет текущего пикселя
                pixel_map[x][y] = new_color
                # Добавляем соседние пиксели в стек
                if x + 1 < WIDTH:
                    stack.append((x + 1, y))  # Право
                if x - 1 >= 0:
                    stack.append((x - 1, y))  # Лево
                if y + 1 < HEIGHT:
                    stack.append((x, y + 1))  # Вниз
                if y - 1 >= 0:
                    stack.append((x, y - 1))  # Вверх
                    # if flag1:
                    # pygame.display.flip()
                    # pygame.time.delay(DELAY_MS)
        # flag1 = False

def compute_outcode(x, y, x_min, y_min, x_max, y_max):
    """
    Вычисляет код положения точки относительно окна.
    """
    code = 0  # Внутри окна
    if x < x_min:  # Левее окна
        code |= 1
    elif x > x_max:  # Правее окна
        code |= 2
    if y < y_min:  # Ниже окна
        code |= 4
    elif y > y_max:  # Выше окна
        code |= 8
    return code


def sutherland_cohen_clip(x1, y1, x2, y2, x_min, y_min, x_max, y_max):
    """
    Реализация алгоритма Сазерленда-Коэна для отсечения отрезка.
    Возвращает координаты отсеченного отрезка или None, если отрезок полностью вне окна.
    """
    outcode1 = compute_outcode(x1, y1, x_min, y_min, x_max, y_max)
    outcode2 = compute_outcode(x2, y2, x_min, y_min, x_max, y_max)

    while True:
        if outcode1 == 0 and outcode2 == 0:
            # Полностью внутри окна
            return round(x1), round(y1), round(x2), round(y2)
        elif outcode1 & outcode2 != 0:
            # Полностью вне окна
            return None
        else:
            # Отрезок пересекает границу окна
            if outcode1 != 0:
                outcode_out = outcode1
            else:
                outcode_out = outcode2

            if outcode_out & 8:  # точка выше окна
                x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                y = y_max
            elif outcode_out & 4:  # точка ниже окна
                x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                y = y_min
            elif outcode_out & 2:  # точка правее окна
                y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                x = x_max
            elif outcode_out & 1:  # точка левее окна
                y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                x = x_min

            if outcode_out == outcode1:
                x1, y1 = x, y
                outcode1 = compute_outcode(x1, y1, x_min, y_min, x_max, y_max)
            else:
                x2, y2 = x, y
                outcode2 = compute_outcode(x2, y2, x_min, y_min, x_max, y_max)


def is_triangle(p1, p2, p3):
    """Проверяет существование треугольника с заданными точками."""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    # Вычисление площади треугольника
    area = abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2
    return area > 0


def bresenham_line(pixel_map, p1, p2):
    """Растеризация линии по алгоритму Брезенхема."""
    x1, y1 = p1
    x2, y2 = p2
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        # ------------------------------------------------режим функционирования A
        if pixel_map[y1][x1] == None:
            pixel_map[y1][x1] = (0, 0, 0)  # Отметка пикселя
        elif SHOW_INVISIBLE:
            pixel_map[y1][x1] = (255, 0, 0)  # Отметка пикселя
        # ------------------------------------------------ режим функционирования Б
        # if pixel_map[y1][x1] == None:
        #     pixel_map[y1][x1] = (0,0,0)  # Отметка пикселя
        # ------------------------------------------------
        if (x1, y1) == (x2, y2):
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy


def draw_polygon(pixel_map, polygon):
    for i in range(len(polygon)):
        # Определяем текущую и следующую точки
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]  # Циклическое замыкание фигуры
        # Клиппинг линии
        clipped_line = sutherland_cohen_clip(p1[0], p1[1], p2[0], p2[1], XMIN, YMIN, XMAX, YMAX)
        if clipped_line:
            # Отрисовка линии через алгоритм Брезенхема
            bresenham_line(pixel_map, (clipped_line[0], clipped_line[1]), (clipped_line[2], clipped_line[3]))

