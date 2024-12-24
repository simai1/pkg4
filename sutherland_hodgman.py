# sutherland_hodgman.py

from typing import List, Tuple

Point = Tuple[int, int]

def polygon_area(poly: List[Point]) -> float:
    """
    Формула шнурка (Shoelace formula). 
    Если результат < 0, многоугольник ориентирован CW; > 0 — CCW.
    """
    area = 0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        area += x1 * y2 - x2 * y1
    return area / 2

def force_ccw(poly: List[Point]) -> List[Point]:
    """
    Если многоугольник ориентирован CW (area<0), переворачиваем порядок вершин (делаем CCW).
    """
    if polygon_area(poly) < 0:
        return list(reversed(poly))
    return poly

def sutherland_hodgman(subject_polygon: List[Point],
                       clip_polygon: List[Point],
                       operation='intersection') -> List[Point]:
    """
    Пример использования классического (упрощённого) алгоритма
    Sutherland–Hodgman для двух операций:

    - 'intersection': вернуть часть subject, лежащую ВНУТРИ clip_polygon.
    - 'difference':   вернуть часть subject, лежащую СНАРУЖИ clip_polygon.

    (Для difference тоже используем S-H, но с keep_inside=False.)
    """
    # 1. Приводим полигоны к обходу CCW (не обязательно, но гарантирует единообразие)
    subject_polygon = force_ccw(subject_polygon)
    clip_polygon    = force_ccw(clip_polygon)

    if not subject_polygon or not clip_polygon:
        # Если один из полигонов пуст, 
        # при intersection это значит итог пуст, 
        # при difference — исходный subject.
        if operation == 'intersection':
            return []
        return subject_polygon

    if operation == 'intersection':
        # Оставляем часть, которая внутри clip_polygon
        return sutherland_hodgman_clip(subject_polygon, clip_polygon, keep_inside=True)
    elif operation == 'difference':
        # Оставляем часть, которая снаружи clip_polygon
        return sutherland_hodgman_clip(subject_polygon, clip_polygon, keep_inside=False)
    else:
        # Если нужно только intersection/difference,
        # а здесь попало что-то ещё — вернём subject без изменений.
        return subject_polygon


def sutherland_hodgman_clip(subject_polygon: List[Point],
                            clip_polygon: List[Point],
                            keep_inside: bool) -> List[Point]:
    """
    Классический алгоритм Sutherland–Hodgman для отсечения многоугольника.

    - subject_polygon: многоугольник, который «отсекаем» (или вырезаем).
    - clip_polygon:   многоугольник-«окно».
    - keep_inside: True = берём часть subject, которая ВНУТРИ clip_polygon.
                   False = берём часть, которая СНАРУЖИ clip_polygon 
                           (аналог difference subject \ clip).

    Возвращает список вершин результирующего многоугольника.
    """

    def inside(point: Point, c1: Point, c2: Point) -> bool:
        """
        Проверяем, лежит ли 'point' слева (или на) вектора c1->c2
        (т.е. внутри, если clip_polygon идёт против часовой стрелки).
        """
        return ((c2[0] - c1[0])*(point[1] - c1[1])
              - (c2[1] - c1[1])*(point[0] - c1[0])) >= 0

    def compute_intersection(s: Point, p: Point, c1: Point, c2: Point) -> Point:
        """
        Находим координаты пересечения отрезка (s->p) 
        с прямой, проходящей через (c1->c2).
        """
        x1, y1 = s
        x2, y2 = p
        x3, y3 = c1
        x4, y4 = c2
        denom = (y4 - y3)*(x2 - x1) - (x4 - x3)*(y2 - y1)
        if denom == 0:
            # Отрезок параллелен (или совпадает) с границей
            # Для упрощения вернём p
            return p
        ua = ((x4 - x3)*(y1 - y3) - (y4 - y3)*(x1 - x3)) / denom
        ix = x1 + ua*(x2 - x1)
        iy = y1 + ua*(y2 - y1)
        return (int(round(ix)), int(round(iy)))

    output_list = subject_polygon[:]
    clip_count = len(clip_polygon)

    input_list = []
    for i in range(clip_count):
        input_list = output_list
        output_list = []
        if not input_list:
            break

        c1 = clip_polygon[i]
        c2 = clip_polygon[(i + 1) % clip_count]

        s = input_list[-1]
        for p in input_list:
            p_in = (inside(p, c1, c2) == keep_inside)
            s_in = (inside(s, c1, c2) == keep_inside)

            if p_in:
                # Точка p внутри
                if not s_in:
                    # Точка s была снаружи -> пересечение
                    inter = compute_intersection(s, p, c1, c2)
                    output_list.append(inter)
                output_list.append(p)
            else:
                # Точка p снаружи
                if s_in:
                    # s была внутри -> пересечение
                    inter = compute_intersection(s, p, c1, c2)
                    output_list.append(inter)

            s = p

    return input_list
