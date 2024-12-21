import math
import time
import pygame
# from figure import Layer
from config import *

# кадрирование
xmin = 0
xmax = 640
ymin = 0
ymax = 640


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
        if (x <= xmax and y <= ymax and x > -xmin and y >= ymin):
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
        # ------------------------------------------------режим функционирования A
        # if pixel_map[y1][x1] == None:
        pixel_map[y1][x1] = (0, 0, 0)  # Отметка пикселя
        if SHOW_INVISIBLE:
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


def draw_triangle(pixel_map, p1, p2, p3):
    """Растеризация треугольника заданного тремя точками с кадрированием линий."""
    if is_triangle(p1, p2, p3):
        for line in [(p1, p2), (p2, p3), (p3, p1)]:
            p1, p2 = line
            clipped_line = sutherland_cohen_clip(p1[0], p1[1], p2[0], p2[1], xmin, ymin, xmax, ymax)
            if clipped_line:
                bresenham_line(pixel_map, (clipped_line[0], clipped_line[1]), (clipped_line[2], clipped_line[3]))
    else:
        print("Треугольник с данными вершинами не существует.")

def sutherland_hodgman_clip(subject_polygon, clip_polygon):
    def inside(point, edge_start, edge_end):
        return (edge_end[0] - edge_start[0]) * (point[1] - edge_start[1]) - \
               (edge_end[1] - edge_start[1]) * (point[0] - edge_start[0]) >= 0

    def intersection(p1, p2, edge_start, edge_end):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = edge_start
        x4, y4 = edge_end

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return None

        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

        return px, py

    def is_ccw(polygon):
        area = 0
        n = len(polygon)
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]
            area += (x2 - x1) * (y2 + y1)
        return area > 0

    if not is_ccw(subject_polygon):
        subject_polygon = subject_polygon[::-1]

    if not is_ccw(clip_polygon):
        clip_polygon = clip_polygon[::-1]

    output_list = subject_polygon

    for i in range(len(clip_polygon)):
        input_list = output_list
        output_list = []

        edge_start = clip_polygon[i]
        edge_end = clip_polygon[(i + 1) % len(clip_polygon)]

        for j in range(len(input_list)):
            current_point = input_list[j]
            prev_point = input_list[j - 1]

            if inside(current_point, edge_start, edge_end):
                if not inside(prev_point, edge_start, edge_end):
                    output_list.append(intersection(prev_point, current_point, edge_start, edge_end))
                output_list.append(current_point)
            elif inside(prev_point, edge_start, edge_end):
                output_list.append(intersection(prev_point, current_point, edge_start, edge_end))

    return output_list

if __name__ == '__main__':
    subject = [(360, 100), (400, 100), (380, 50)]
    clipper = [(340, 110), (420, 110), (380, 40)]

    result = sutherland_hodgman_clip(subject, clipper)
    print(f"Результат отсечения: {result}")
