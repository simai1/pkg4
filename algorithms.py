import math
import time
from hodjman import *
import pygame
# from figure import Layer

from config import *
# кадрирование
xmin = 0
xmax = 400
ymin = 0
ymax = 400

# def init_list():
#     return inited_list

def algorithm_A_fill(pixel_map, center, radius, new_color, outline_color):
    time.sleep(0.001)
    # global flag1
    x = center[1]
    y = center[0]
    """Заполняет область, начиная с пикселя (x, y) новым цветом."""
    stack = [(x, y)]
    old_color = pixel_map[x][y]  # Получаем цвет текущего пикселя (RGB)
    while stack:
        x, y = stack.pop()
        if(x<=xmax and y<=ymax and x>-xmin and y>=ymin):
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


def liang_barsky_clip(x1, y1, x2, y2, x_min, y_min, x_max, y_max):
    """Кадрирование отрезка по алгоритму Лианга-Барски."""
    dx = x2 - x1
    dy = y2 - y1

    # Инициализация параметров
    p = [-dx, dx, -dy, dy]
    q = [x1 - x_min, x_max - x1, y1 - y_min, y_max - y1]

    t_min, t_max = 0, 1

    for i in range(4):
        if p[i] == 0:  # Линия параллельна границе
            if q[i] < 0:
                return None  # Отрезок полностью вне окна
        else:
            t = q[i] / p[i]
            if p[i] < 0:  # Вход в видимую область
                t_min = max(t_min, t)
            else:  # Выход из видимой области
                t_max = min(t_max, t)

    if t_min > t_max:
        return None  # Отрезок вне окна

    # Вычисление новых координат отсечённого отрезка
    x1_clip = x1 + t_min * dx
    y1_clip = y1 + t_min * dy
    x2_clip = x1 + t_max * dx
    y2_clip = y1 + t_max * dy

    return round(x1_clip), round(y1_clip), round(x2_clip), round(y2_clip)

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
        #------------------------------------------------режим функционирования A
        if pixel_map[y1][x1] == None:
            pixel_map[y1][x1] = (0,0,0)  # Отметка пикселя
        else:
            pixel_map[y1][x1] = (255,0,0)  # Отметка пикселя
        #------------------------------------------------ режим функционирования Б
        # if pixel_map[y1][x1] == None:
        #     pixel_map[y1][x1] = (0,0,0)  # Отметка пикселя
        #------------------------------------------------
        if (x1, y1) == (x2, y2):
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

def draw_triangle(pixel_map, p1, p2, p3):
    """Растеризация треугольника заданного тремя точками с кадрированием линий."""
    if is_triangle(p1, p2, p3):
        for line in [(p1, p2), (p2, p3), (p3, p1)]:
            p1, p2 = line
            clipped_line = liang_barsky_clip(p1[0], p1[1], p2[0], p2[1], xmin, ymin, xmax, ymax)
            if clipped_line:
                bresenham_line(pixel_map, (clipped_line[0], clipped_line[1]), (clipped_line[2], clipped_line[3]))
    else:
        print("Треугольник с данными вершинами не существует.")

