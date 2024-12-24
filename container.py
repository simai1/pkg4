# container.py

from typing import List, Tuple

from config import *
from sutherland_cohen_clip import fast_clip_line
from sutherland_hodgman import sutherland_hodgman

Point = Tuple[int, int]

class Layer:
    def __init__(self, polygon, color, z_index=0, outline_color=(0, 0, 0)):
        self.polygon = polygon       # список вершин (x, y)
        self.color = color           # цвет заливки
        self.outline_color = outline_color  # цвет обводки (по умолчанию чёрный)
        self.z_index = z_index

    def get_polygon(self):
        return self.polygon

    def set_polygon(self, new_polygon):
        self.polygon = new_polygon

    def draw(self, pixel_map):
        """
        Растеризация многоугольника (после определения видимой части),
        а также обрисовка контура по Брезенхему.
        """
        if not self.polygon:
            return

        # 1) Заливка (примерно как раньше)
        fill_polygon_scanline(pixel_map, self.polygon, self.color)

        # 2) Обводка сторон многоугольника
        for i in range(len(self.polygon)):
            x1, y1 = self.polygon[i]
            x2, y2 = self.polygon[(i + 1) % len(self.polygon)]  # соединяем вершины кольцево

            clipped_segments = fast_clip_line(x1, y1, x2, y2, XMIN, YMIN, XMAX, YMAX)

            # Рисуем все подотрезки
            for (cx1, cy1, cx2, cy2) in clipped_segments:
                bresenham_line(pixel_map, cx1, cy1, cx2, cy2, self.outline_color)


class Container:
    """
    Класс, содержащий список слоёв и управляющий их отрисовкой.
    """
    def __init__(self, pixel_map):
        self.layers: List[Layer] = []
        self.pixel_map = pixel_map

    def set_pixel_map(self, pixel_map):
        self.pixel_map = pixel_map

    def add_layer(self, layer: Layer):
        self.layers.append(layer)
        # Сортируем слои по Z (по высоте).
        self.layers.sort(key=lambda l: l.z_index)

    def draw(self):
        """
        Последовательно определяем видимую часть каждого слоя,
        учитывая все слои, которые находятся выше него.
        Затем выполняем растеризацию.
        """
        # Копируем список слоёв (он отсортирован по z-индексу).
        self.layers.reverse()

        for i in range(len(self.layers)):
            current_layer = self.layers[i]
            subject_polygon = current_layer.get_polygon()

            # Для каждого слоя выше текущего:
            # for j in range(i+1, len(self.layers)):
            #     clip_polygon = self.layers[j].get_polygon()
            #     # Применяем Вейлера–Азертона (операция "исключение" видимых поверхностей из нижележащего)
            #     # Т.е. вычитаем часть, которую перекрывает вышележащий слой
            #     subject_polygon = sutherland_hodgman(subject_polygon, clip_polygon)
            #
            #     # Если многоугольник "исчез" — слой полностью перекрыт
            #     if not subject_polygon:
            #         break

            # Устанавливаем результирующий многоугольник (видимую часть слоя)
            current_layer.set_polygon(subject_polygon)
            # Выполняем растеризацию полученного многоугольника
            current_layer.draw(self.pixel_map)


def fill_polygon_scanline(pixel_map, polygon, color):
    """
    Упрощённая реализация заливки многоугольника методом scan-line,
    с ограничением по кадру [XMIN..XMAX, YMIN..YMAX].
    """
    if not polygon:
        return

    ys = [p[1] for p in polygon]
    min_y = min(ys)
    max_y = max(ys)

    # Сужаем диапазон по вертикали рамкой [YMIN, YMAX]
    top    = max(min_y, YMIN)
    bottom = min(max_y, YMAX)

    for scan_y in range(top, bottom + 1):
        # Собираем все x-пересечения с текущей горизонталью
        intersection_xs = []
        for i in range(len(polygon)):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % len(polygon)]

            # Проверка: пересекает ли отрезок (x1,y1)-(x2,y2) горизонталь scan_y
            # (учитываем случаи, когда y1 <= scan_y < y2 или y2 <= scan_y < y1)
            if (y1 <= scan_y < y2) or (y2 <= scan_y < y1):
                if (y2 - y1) != 0:
                    intersect_x = x1 + (scan_y - y1) * (x2 - x1) / (y2 - y1)
                    intersection_xs.append(int(round(intersect_x)))

        intersection_xs.sort()

        # Попарно заливаем участки [x_start .. x_end]
        # Но тоже ограничиваем их [XMIN..XMAX].
        for k in range(0, len(intersection_xs) - 1, 2):
            x_start = intersection_xs[k]
            x_end   = intersection_xs[k + 1]

            # Сужаем диапазон заливки кадром
            actual_start = max(x_start, XMIN)
            actual_end   = min(x_end,   XMAX)

            for px in range(actual_start, actual_end + 1):
                # Проверяем, что в пределах pixel_map
                if (0 <= scan_y < len(pixel_map)) and (0 <= px < len(pixel_map[0])):
                    if SHOW_INVISIBLE:
                        # Если эта ячейка уже занята, «меняем» цвет по какой-то логике
                        if pixel_map[scan_y][px] is not None:
                            if pixel_map[scan_y][px] == (0, 0, 0):
                                pixel_map[scan_y][px] = (255, 0, 0)
                            else:
                                old_col = pixel_map[scan_y][px]
                                pixel_map[scan_y][px] = (
                                    (old_col[0] + 50) % 255,
                                    old_col[1],
                                    old_col[2]
                                )
                        else:
                            pixel_map[scan_y][px] = color
                    else:
                        pixel_map[scan_y][px] = color

def bresenham_line(pixel_map, x1, y1, x2, y2, color):
    """
    Рисует линию от (x1, y1) до (x2, y2) цветом color.
    Пиксели ставятся в pixel_map[y][x].
    """

    # Вспомогательные переменные
    dx = abs(x2 - x1)
    sx = 1 if x1 < x2 else -1
    dy = -abs(y2 - y1)
    sy = 1 if y1 < y2 else -1
    err = dx + dy  # начальная ошибка

    while True:
        # Рисуем текущую точку
        if 0 <= y1 < len(pixel_map) and 0 <= x1 < len(pixel_map[0]):
            pixel_map[y1][x1] = color

        # Если дошли до конца
        if x1 == x2 and y1 == y2:
            break

        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x1 += sx
        if e2 <= dx:
            err += dx
            y1 += sy
