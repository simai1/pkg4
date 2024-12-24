# weiler_atherton.py

from typing import List, Tuple

Point = Tuple[int, int]

def polygon_area(poly: List[Point]) -> float:
    """ Формула шнурка для площади. """
    area = 0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        area += x1 * y2 - x2 * y1
    return area / 2

def force_ccw(poly: List[Point]) -> List[Point]:
    """ Если многоугольник ориентирован CW (area<0), переворачиваем его. """
    if polygon_area(poly) < 0:
        return list(reversed(poly))
    return poly

def weiler_atherton(subject_polygon: List[Point],
                    clip_polygon: List[Point],
                    operation='intersection') -> List[Point]:
    """
    Упрощённая реализация алгоритма Вейлера–Азертона (Sutherland–Hodgman).
    """
    # 1. Нормализуем ориентацию обоих полигонов в CCW
    subject_polygon = force_ccw(subject_polygon)
    clip_polygon    = force_ccw(clip_polygon)

    if not subject_polygon or not clip_polygon:
        return subject_polygon if operation != 'intersection' else []

    if operation == 'intersection':
        return polygon_clip(subject_polygon, clip_polygon, keep_inside=True)
    elif operation == 'union':
        # union(A, B) = A + B - intersection(A, B) (упрощённо для демонстрации)
        intersect_poly = polygon_clip(subject_polygon, clip_polygon, keep_inside=True)
        diff1 = polygon_clip(subject_polygon, clip_polygon, keep_inside=False)
        diff2 = polygon_clip(clip_polygon, subject_polygon, keep_inside=False)
        return merge_polygons(diff1, diff2, intersect_poly)
    elif operation == 'difference':
        return polygon_clip(subject_polygon, clip_polygon, keep_inside=False)

    # Если не intersection/union/difference, возвращаем как есть
    return subject_polygon

def polygon_clip(subject_polygon: List[Point],
                 clip_polygon: List[Point],
                 keep_inside: bool) -> List[Point]:
    """
    Алгоритм Sutherland–Hodgman:
    если keep_inside=True, оставляем часть subject, которая ВНУТРИ clip_polygon;
    если keep_inside=False, оставляем часть, которая СНАРУЖИ clip_polygon.
    """
    def inside(p, cp1, cp2):
        # Точка p "слева" от вектора cp1->cp2 (в терминах CCW)
        return ((cp2[0] - cp1[0]) * (p[1] - cp1[1])
              - (cp2[1] - cp1[1]) * (p[0] - cp1[0])) >= 0

    def compute_intersection(s: Point, p: Point, cp1: Point, cp2: Point) -> Point:
        # Пересечение отрезка (s->p) с прямой (cp1->cp2)
        x1, y1 = s
        x2, y2 = p
        x3, y3 = cp1
        x4, y4 = cp2
        denom = (y4 - y3)*(x2 - x1) - (x4 - x3)*(y2 - y1)
        if denom == 0:
            # Параллельные — можно возвращать p,
            # или s, или среднюю точку. Для упрощения вернём p.
            return p
        ua = ((x4 - x3)*(y1 - y3) - (y4 - y3)*(x1 - x3)) / denom
        ix = x1 + ua*(x2 - x1)
        iy = y1 + ua*(y2 - y1)
        return (int(round(ix)), int(round(iy)))

    output_list = subject_polygon[:]
    cp_count = len(clip_polygon)

    for i in range(cp_count):
        input_list = output_list
        output_list = []
        if not input_list:
            break
        cp1 = clip_polygon[i]
        cp2 = clip_polygon[(i + 1) % cp_count]

        s = input_list[-1]
        for p in input_list:
            # Проверяем "принадлежность" p и s
            p_in = (inside(p, cp1, cp2) == keep_inside)
            s_in = (inside(s, cp1, cp2) == keep_inside)

            if p_in:
                # p находится в нужной полуплоскости (или на границе)
                if not s_in:
                    # s было снаружи — значит, пересекаем границу
                    inter = compute_intersection(s, p, cp1, cp2)
                    output_list.append(inter)
                output_list.append(p)
            else:
                # p снаружи
                if s_in:
                    # но s было внутри — пересекаем границу
                    inter = compute_intersection(s, p, cp1, cp2)
                    output_list.append(inter)

            s = p
    return output_list

def merge_polygons(*polygons: List[Point]) -> List[Point]:
    """
    Утилита для "склеивания" наборов вершин (очень упрощённо).
    В настоящем "union" нужна полноценная сшивка ребер.
    """
    merged = []
    for poly in polygons:
        merged.extend(poly)
    return merged
