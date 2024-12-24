def compute_outcode(x, y, x_min, y_min, x_max, y_max):
    """
    Вычисляет 4-битный код положения точки (x, y)
    относительно окна [x_min, x_max] x [y_min, y_max].
    Биты (считаем справа налево):
        1 (0001)  -> точка левее x_min
        2 (0010)  -> точка правее x_max
        4 (0100)  -> точка ниже y_min
        8 (1000)  -> точка выше y_max
    """
    code = 0
    if x < x_min:
        code |= 1  # 0001
    elif x > x_max:
        code |= 2  # 0010

    if y < y_min:
        code |= 4  # 0100
    elif y > y_max:
        code |= 8  # 1000

    return code


def sutherland_cohen_clip_line(x1, y1, x2, y2, x_min, y_min, x_max, y_max):
    """
    Отсекает отрезок (x1,y1)-(x2,y2) прямоугольным окном [x_min, x_max] x [y_min, y_max].
    Возвращает (X1, Y1, X2, Y2) для отсечённого отрезка или None,
    если отрезок полностью вне окна.
    """
    outcode1 = compute_outcode(x1, y1, x_min, y_min, x_max, y_max)
    outcode2 = compute_outcode(x2, y2, x_min, y_min, x_max, y_max)

    while True:
        # 1) Проверка на тривиальное принятие:
        if outcode1 == 0 and outcode2 == 0:
            # Отрезок полностью внутри
            return (round(x1), round(y1), round(x2), round(y2))

        # 2) Проверка на тривиальное отклонение:
        if (outcode1 & outcode2) != 0:
            # Отрезок полностью вне
            return None

        # 3) Иначе отрезок пересекает границу
        # Берём точку с ненулевым outcode
        if outcode1 != 0:
            outcode_out = outcode1
        else:
            outcode_out = outcode2

        # Координаты точки пересечения (xi, yi)
        xi, yi = 0.0, 0.0

        # Проверяем, какая именно граница нарушена
        if outcode_out & 8:  # точка выше y_max
            xi = x1 + (x2 - x1) * (y_max - y1) / float(y2 - y1)
            yi = y_max
        elif outcode_out & 4:  # точка ниже y_min
            xi = x1 + (x2 - x1) * (y_min - y1) / float(y2 - y1)
            yi = y_min
        elif outcode_out & 2:  # точка правее x_max
            yi = y1 + (y2 - y1) * (x_max - x1) / float(x2 - x1)
            xi = x_max
        elif outcode_out & 1:  # точка левее x_min
            yi = y1 + (y2 - y1) * (x_min - x1) / float(x2 - x1)
            xi = x_min

        # Теперь обновим координаты точки
        if outcode_out == outcode1:
            # сдвигаем (x1, y1)
            x1, y1 = xi, yi
            outcode1 = compute_outcode(x1, y1, x_min, y_min, x_max, y_max)
        else:
            # сдвигаем (x2, y2)
            x2, y2 = xi, yi
            outcode2 = compute_outcode(x2, y2, x_min, y_min, x_max, y_max)
