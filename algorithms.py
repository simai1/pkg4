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

