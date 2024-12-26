def compute_outcode(x, y, x_min, y_min, x_max, y_max):
    """
    4-битный код положения точки (x, y) относительно
    прямоугольного окна [x_min, x_max] x [y_min, y_max].
    Биты (считаем справа налево):
        1 (0001) -> левее x_min
        2 (0010) -> правее x_max
        4 (0100) -> ниже y_min
        8 (1000)-> выше y_max
    """
    code = 0
    if x < x_min:
        code |= 1
    elif x > x_max:
        code |= 2
    if y < y_min:
        code |= 4
    elif y > y_max:
        code |= 8
    return code

def fast_clip_line(x1, y1, x2, y2, x_min, y_min, x_max, y_max, epsilon=0.5):
    """
    Алгоритм Fast Clipping (деление пополам) для отрезка (x1,y1)-(x2,y2):
    - Возвращает отрезок, который находится ВНУТРИ окна.
    - Параметр epsilon: минимальная длина, при которой прекращаем делить.
    """
    out1 = compute_outcode(x1, y1, x_min, y_min, x_max, y_max)
    out2 = compute_outcode(x2, y2, x_min, y_min, x_max, y_max)

    # 1) Тривиальное отклонение (если есть общее пересечение кодов)
    if (out1 & out2) != 0:
        return []  # пусто

    # 2) Тривиальное принятие (оба внутри)
    if out1 == 0 and out2 == 0:
        # Вернём один отрезок как есть
        return [(round(x1), round(y1), round(x2), round(y2))]

    # 3) Если длина отрезка меньше порога,
    #    считаем, что он либо внутри, либо вне
    dx = x2 - x1
    dy = y2 - y1
    length_sq = dx*dx + dy*dy  # квадрат длины
    if length_sq <= epsilon*epsilon:
        # Длина очень маленькая - решаем по кодам:
        # если OR=0 => внутри, если AND!=0 => вне
        # иначе считаем "пограничным" - можно либо отбросить, либо принять
        if (out1 | out2) == 0:
            return [(round(x1), round(y1), round(x2), round(y2))]
        else:
            return []

    # 4) Иначе делим отрезок пополам
    mx = (x1 + x2)/2.0
    my = (y1 + y2)/2.0

    # Рекурсивно пытаемся "отрезать" левую часть и правую часть
    left_part  = fast_clip_line(x1, y1, mx, my, x_min, y_min, x_max, y_max, epsilon)
    right_part = fast_clip_line(mx, my, x2, y2, x_min, y_min, x_max, y_max, epsilon)

    # Объединяем результаты (список подотрезков)
    return left_part + right_part
