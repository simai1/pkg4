def sutherland_hodgman(subject_polygon, clip_polygon):
    """
    Отсекает многоугольник subject_polygon по многоугольнику clip_polygon.
    """
    def inside(p, edge):
        """Проверяет, находится ли точка внутри текущего ребра отсекателя."""
        (x1, y1), (x2, y2) = edge
        return (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) >= 0

    def intersection(p1, p2, edge):
        """Вычисляет точку пересечения отрезка p1-p2 с ребром edge."""
        (x1, y1), (x2, y2) = edge
        (px1, py1), (px2, py2) = p1, p2
        dx, dy = px2 - px1, py2 - py1
        edge_dx, edge_dy = x2 - x1, y2 - y1
        det = -edge_dx * dy + dx * edge_dy
        if det == 0:
            return None  # Параллельны
        t = (-dy * (px1 - x1) + dx * (py1 - y1)) / det
        return (x1 + t * edge_dx, y1 + t * edge_dy)

    output_list = subject_polygon[:]
    for i in range(len(clip_polygon)):
        input_list = output_list[:]
        output_list = []

        clip_edge = (clip_polygon[i], clip_polygon[(i + 1) % len(clip_polygon)])
        for j in range(len(input_list)):
            current_point = input_list[j]
            prev_point = input_list[j - 1]

            if inside(current_point, clip_edge):
                if not inside(prev_point, clip_edge):
                    intersect_point = intersection(prev_point, current_point, clip_edge)
                    if intersect_point:
                        output_list.append(intersect_point)
                output_list.append(current_point)
            elif inside(prev_point, clip_edge):
                intersect_point = intersection(prev_point, current_point, clip_edge)
                if intersect_point:
                    output_list.append(intersect_point)

        # Если многоугольник полностью вне текущего ребра отсекателя
        if not output_list:
            return []

    return output_list


# Пример использования: два треугольника
# clip_polygon = [(1, 1), (4, 1), (2.5, 4)]
# subject_polygon= [(2, 2), (5, 2), (3.5, 5)]
#
# result = sutherland_hodgman(subject_polygon, clip_polygon)
# print("Отсеченный многоугольник:", result)
