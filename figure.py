from algorithms import *
from config import *
import pygame
import sys
import math
from config import *
from sutherland_hodgman import sutherland_hodgman


def calculate_triangle_center(p1, p2, p3):
    """
    Вычисляет центр треугольника по его вершинам.
    """
    x_center = (p1[0] + p2[0] + p3[0]) / 3
    y_center = (p1[1] + p2[1] + p3[1]) / 3
    return round(x_center), round(y_center)


class Layer:
    def __init__(self, p1, p2, p3, new_color, zindex, visible=True, center=0):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.new_color = new_color
        self.zindex = zindex
        self.center = calculate_triangle_center(p1, p2, p3) if center == 0 else center
        self.visible = visible

    # def draw(self):
    #     if self.visible:
    #         draw_triangle(self.pixel_map, self.p1, self.p2, self.p3)
    #         # draw_triangle_hodjman(self.pixel_map, self.p1,self.p2,self.p3)
    #         algorithm_A_fill(self.pixel_map, self.center, self.new_color)


class Container:
    def __init__(self, pixel_map):
        self.layers = []  # Список всех слоев
        self.pixel_map = pixel_map # Карта пикселей полотна

    def add_layer(self, layer):
        """Добавляет слой в контейнер."""
        self.layers.append(layer)
        self.layers.sort(key=lambda l: l.zindex)  # Сортировка слоев по zindex

    def analyze_and_fill(self):
        """Анализирует слои и заполняет видимые области."""
        for y in range(len(self.pixel_map)):
            for x in range(len(self.pixel_map[0])):
                self.pixel_map[y][x] = None  # Очищаем карту пикселей

        for layer in self.layers:
            triangle = [layer.p1, layer.p2, layer.p3]
            draw_triangle(self.pixel_map, layer.p1, layer.p2, layer.p3)

            # Определяем видимую область с учетом предыдущих слоев
            visible_region = triangle
            for previous_layer in self.layers:
                if previous_layer.zindex < layer.zindex:
                    previous_triangle = [previous_layer.p1, previous_layer.p2, previous_layer.p3]
                    visible_region = sutherland_hodgman(visible_region, previous_triangle)
                    if not visible_region:
                        break

            # Если есть видимая область, применяем заливку
            if visible_region:
                pixels = self.get_polygon_pixels(visible_region)
                for x, y in pixels:
                    if 0 <= x < len(self.pixel_map[0]) and 0 <= y < len(self.pixel_map):
                        self.pixel_map[y][x] = layer.new_color
                # algorithm_A_fill(self.pixel_map, layer.center, layer.new_color)

    def get_polygon_pixels(self, polygon):
        """Вспомогательная функция для получения всех пикселей внутри многоугольника."""
        # Используем алгоритм сканирующих линий для получения всех пикселей внутри многоугольника
        def edge_fn(x1, y1, x2, y2, x, y):
            return (y1 - y2) * x + (x2 - x1) * y + (x1 * y2 - x2 * y1)

        # Найти границы многоугольника
        min_x = int(min(p[0] for p in polygon))
        max_x = int(max(p[0] for p in polygon))
        min_y = int(min(p[1] for p in polygon))
        max_y = int(max(p[1] for p in polygon))

        pixels = []
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                inside = True
                for i in range(len(polygon)):
                    p1 = polygon[i]
                    p2 = polygon[(i + 1) % len(polygon)]
                    if edge_fn(p1[0], p1[1], p2[0], p2[1], x, y) < 0:
                        inside = False
                        break
                if inside:
                    pixels.append((x, y))

        return pixels