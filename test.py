import pygame
import sys
import math
from config import *
from algorithms import *
from figure import Layer

def arc_length(radius, angle_start, angle_end):
    # Преобразуем углы из градусов в радианы
    angle_start = math.radians(angle_start % 360)
    angle_end = math.radians(angle_end % 360)

    # Рассчитываем угловую разницу в радианах
    if angle_end >= angle_start:
        theta = angle_end - angle_start
    else:
        theta = (2 * math.pi - angle_start) + angle_end

    # Вычисляем длину дуги
    length = radius * theta
    return length


def draw_canvas(screen, scale, pixel_map, offset_x, offset_y):
    # Заливаем экран белым цветом
    screen.fill((230, 230, 230))
    # Рисуем рамки для каждого пикселя
    for y in range(0, HEIGHT // PIXEL_SIZE):
        for x in range(0, WIDTH // PIXEL_SIZE):
            # Увеличиваем размер пикселя по масштабу
            rect = pygame.Rect((x * PIXEL_SIZE * scale) + offset_x, (y * PIXEL_SIZE * scale) + offset_y,
                               PIXEL_SIZE * scale, PIXEL_SIZE * scale)
            if scale >= 3:
                pygame.draw.rect(screen, (192, 192, 192), rect, 1)  # Обводим серым цветом с шириной 1

            # Если пиксель активен, заливаем его цветом
            if pixel_map[y][x] is not None:  # Проверяем, не является ли цвет пустым
                pygame.draw.rect(screen, pixel_map[y][x], rect)  # Заполнение активных пикселей их цветом

    # Координаты для рисования осей, учитывая масштаб и смещение
    center_x_pixel = (WIDTH // PIXEL_SIZE) // 2
    center_y_pixel = (HEIGHT // PIXEL_SIZE) // 2
    center_x = center_x_pixel * PIXEL_SIZE * scale + offset_x
    center_y = center_y_pixel * PIXEL_SIZE * scale + offset_y

    # Рисуем оси
    pygame.draw.line(screen, (0, 0, 0), (0, center_y), (WIDTH, center_y), 2)  # Ось X
    pygame.draw.line(screen, (0, 0, 0), (center_x, 0), (center_x, HEIGHT), 2)  # Ось Y

    # Рисуем засечки на каждой 20-й ячейке
    tick_length = 4 * scale  # Увеличенная длина засечки для лучшей видимости
    tick_thickness = 2  # Толщина засечки
    for i in range(0, WIDTH // PIXEL_SIZE, 20):
        # Засечки по оси X
        tick_x = i * PIXEL_SIZE * scale + offset_x
        pygame.draw.line(screen, (0, 0, 0), (tick_x, center_y - tick_length), (tick_x, center_y + tick_length),
                         tick_thickness)

    for i in range(0, HEIGHT // PIXEL_SIZE, 20):
        # Засечки по оси Y
        tick_y = i * PIXEL_SIZE * scale + offset_y
        pygame.draw.line(screen, (0, 0, 0), (center_x - tick_length, tick_y), (center_x + tick_length, tick_y),
                         tick_thickness)


def create_example_pattern(pixel_map, outline_color, fill_color, algorithm_round, algorithm_fill, _radius, x, y):
    center_x = len(pixel_map[0]) // 2 + int(x * 20)
    center_y = len(pixel_map) // 2 - int(y * 20)
    radius = int(_radius * 20)

    # Возвращаем генераторы для отрисовки контура окружности и заливки
    algorithm_round(pixel_map, (center_x, center_y), radius,
                    outline_color)  # Используем reference_algorithm_round
    algorithm_fill(pixel_map, (center_x, center_y), radius, fill_color, outline_color)


def create_arc_pattern(pixel_map, outline_color, algorithm_round, _radius, x, y, ara, arb):
    # print(f"Длина дуги: {arc_length(_radius, ara, arb)}")
    center_x = len(pixel_map[0]) // 2 + int(x * 20)
    center_y = len(pixel_map) // 2 - int(y * 20)
    radius = int(_radius * 20)  # 3
    algorithm_round(pixel_map, (center_x, center_y), radius, outline_color, ara, arb)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pixel Canvas")

    f = True
    scale = INITIAL_SCALE
    offset_x, offset_y = 0, 0
    dragging = False
    last_mouse_x, last_mouse_y = 0, 0
    layers =[]
    

    # Инициализируем карту пикселей
    pixel_map = [[None for _ in range(WIDTH // PIXEL_SIZE)] for _ in range(HEIGHT // PIXEL_SIZE)]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Управление масштабированием с помощью колесика мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Правая кнопка мыши
                    dragging = True
                    last_mouse_x, last_mouse_y = event.pos  # Сохраняем начальную позицию
                elif event.button == 4:  # Колесо мыши (прокрутка вверх)
                    # Увеличиваем масштаб с фокусировкой на центр координат
                    new_scale = min(scale + 0.1, MAX_SCALE)
                    offset_x -= (WIDTH // 2 - offset_x) * (new_scale / scale - 1)
                    offset_y -= (HEIGHT // 2 - offset_y) * (new_scale / scale - 1)
                    scale = new_scale
                elif event.button == 5:  # Колесо мыши (прокрутка вниз)
                    # Уменьшаем масштаб с фокусировкой на центр координат
                    new_scale = max(scale - 0.1, MIN_SCALE)
                    offset_x -= (WIDTH // 2 - offset_x) * (new_scale / scale - 1)
                    offset_y -= (HEIGHT // 2 - offset_y) * (new_scale / scale - 1)
                    scale = new_scale

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:  # Правая кнопка мыши
                    dragging = False

            # Перемещение холста при перетаскивании
            if event.type == pygame.MOUSEMOTION and dragging:
                mouse_x, mouse_y = event.pos
                offset_x += mouse_x - last_mouse_x
                offset_y += mouse_y - last_mouse_y
                last_mouse_x, last_mouse_y = mouse_x, mouse_y

        draw_canvas(screen, scale, pixel_map, offset_x, offset_y)
        if (f):
            
            
            layers.append(Layer(pixel_map,(110, 265),(110,250),(130,265),(111,264),0,(251,254,155),(0,0,0)))#свет правой фары
            layers.append(Layer(pixel_map,(130, 250),(110,250),(130,265),(129,251),0,(251,254,155),(0,0,0)))

            layers.append(Layer(pixel_map,(100, 270),(140,270),(140,245),(139,269),0,(159,79,72),(0,0,0)))#каркас правой фары
            layers.append(Layer(pixel_map,(100, 270),(100,245),(140,245),(101,246),0,(159,79,72),(0,0,0)))

            layers.append(Layer(pixel_map,(150, 268),(165,242),(190,250),(165,243),0,(159,79,72),(0,0,0))) #над правым колесом
            layers.append(Layer(pixel_map,(186, 240),(165,242),(190,250),(186,242),0,(159,79,72),(0,0,0)))
            layers.append(Layer(pixel_map,(202, 275),(170,260),(190,250),(197,272),0,(159,79,72),(0,0,0)))

            layers.append(Layer(pixel_map,(195, 190),(100,245),(100,190),(101,191),0,(159,79,72),(0,0,0)))#правая часть копота
            layers.append(Layer(pixel_map,(195, 190),(100,245),(195,245),(194,220),0,(159,79,72),(0,0,0)))

            layers.append(Layer(pixel_map,(10, 270),(150,270),(10,300),(11,271),0,(173,185,202),(0,0,0),0))#бампер
            layers.append(Layer(pixel_map,(150, 300),(150,270),(10,300),(149,299),0,(173,185,202),(0,0,0),0))#задаем невидимым------------------------------------------

            layers.append(Layer(pixel_map,(100, 100),(100,150),(105,100),(102,101),0,(183,165,144),(0,0,0)))#левая труба
            layers.append(Layer(pixel_map,(105, 150),(100,150),(105,100),(102,149),0,(183,165,144),(0,0,0)))
            
            layers.append(Layer(pixel_map,(80, 150),(80,160),(200,150),(81,151),0,(173,185,202),(0,0,0)))#над лобовым стеклом крышка
            layers.append(Layer(pixel_map,(200, 160),(80,160),(200,150),(199,159),0,(173,185,202),(0,0,0)))

            layers.append(Layer(pixel_map,(120, 150),(135,150),(135,120),(134,125),0,(159,79,72),(0,0,0)))#крыша
            layers.append(Layer(pixel_map,(135, 150),(135,120),(230,120),(136,121),0,(159,79,72),(0,0,0)))
            layers.append(Layer(pixel_map,(135, 150),(230,150),(230,120),(229,149),0,(159,79,72),(0,0,0)))

            layers.append(Layer(pixel_map,(233, 100),(233,170),(238,100),(235,101),0,(183,165,144),(0,0,0)))#правая труба
            layers.append(Layer(pixel_map,(238, 170),(233,170),(238,100),(235,169),0,(183,165,144),(0,0,0)))

            layers.append(Layer(pixel_map,(228, 260),(228,170),(243,170),(234,171),0,(183,165,144),(0,0,0)))#правая большая труба
            layers.append(Layer(pixel_map,(228, 260),(243,260),(243,170),(234,259),0,(183,165,144),(0,0,0)))

            layers.append(Layer(pixel_map,(230, 115),(230,260),(275,115),(274,116),0,(159,79,72),(0,0,0)))#за кабиной
            layers.append(Layer(pixel_map,(275, 260),(230,260),(275,115),(274,259),0,(159,79,72),(0,0,0)))

            layers.append(Layer(pixel_map,(80, 180),(90,180),(90,160),(89,179),0,(99,119,133),(0,0,0)))#лобовое окно
            layers.append(Layer(pixel_map,(195, 160),(90,180),(90,160),(91,179),0,(99,119,133),(0,0,0)))
            layers.append(Layer(pixel_map,(195, 160),(90,180),(195,180),(194,179),0,(99,119,133),(0,0,0)))

            layers.append(Layer(pixel_map,(197, 178),(208,178),(208,160),(200,177),0,(99,119,133),(0,0,0)))#боковое окно
            layers.append(Layer(pixel_map,(219, 160),(208,178),(208,160),(210,161),0,(99,119,133),(0,0,0)))
            layers.append(Layer(pixel_map,(219, 160),(208,178),(219,178),(210,177),0,(99,119,133),(0,0,0)))

            layers.append(Layer(pixel_map,(195, 150),(195,260),(230,150),(205,151),0,(159,79,72),(0,0,0)))#боковая дверь 
            layers.append(Layer(pixel_map,(230, 260),(195,260),(230,150),(205,259),0,(159,79,72),(0,0,0)))

            layers.append(Layer(pixel_map,(100, 270),(40,270),(100,183),(70,269),0,(118,113,113),(0,0,0)))#передний капот (серый)
            layers.append(Layer(pixel_map,(40, 183),(40,270),(100,183),(70,184),0,(118,113,113),(0,0,0)))

            layers.append(Layer(pixel_map,(195, 190),(40,190),(195,180),(194,189),0,(159,79,72),(0,0,0)))#верх капота
            layers.append(Layer(pixel_map,(40, 180),(40,190),(195,180),(41,181),0,(159,79,72),(0,0,0)))

            layers.append(Layer(pixel_map,(10, 265),(10,250),(30,265),(11,264),0,(251,254,155),(0,0,0)))#свет левой фары
            layers.append(Layer(pixel_map,(30, 250),(10,250),(30,265),(29,251),0,(251,254,155),(0,0,0)))

            layers.append(Layer(pixel_map,(0, 270),(40,270),(40,245),(39,248),0,(159,79,72),(0,0,0)))#каркас левой фары
            layers.append(Layer(pixel_map,(0, 270),(0,245),(40,245),(1,246),0,(159,79,72),(0,0,0)))
            layers.append(Layer(pixel_map,(15, 245),(40,245),(40,230),(39,233),0,(159,79,72),(0,0,0)))

            layers.append(Layer(pixel_map,(170, 285),(170,260),(145,272),(168,280),0,(81,81,72),(0,0,0)))#переднее правое колесо
            layers.append(Layer(pixel_map,(170, 285),(170,260),(195,272),(172,280),0,(81,81,72),(0,0,0)))
            layers.append(Layer(pixel_map,(170, 285),(145,298),(145,272),(168,285),0,(81,81,72),(0,0,0)))
            layers.append(Layer(pixel_map,(170, 285),(195,296),(195,272),(172,285),0,(81,81,72),(0,0,0)))
            layers.append(Layer(pixel_map,(170, 285),(145,298),(170,310),(168,290),0,(81,81,72),(0,0,0)))
            layers.append(Layer(pixel_map,(170, 285),(195,296),(170,310),(172,290),0,(81,81,72),(0,0,0)))

            layers.append(Layer(pixel_map,(195, 270),(140,270),(195,245),(141,269),0,(159,79,72),(0,0,0)))#заглушка
            layers.append(Layer(pixel_map,(140, 245),(195,245),(140,270),(194,246),0,(159,79,72),(0,0,0)))

            layers.append(Layer(pixel_map,(295, 272),(295,247),(270,259),(294,259),0,(81,81,72),(0,0,0)))#заднее колесо
            layers.append(Layer(pixel_map,(295, 272),(295,247),(320,259),(296,259),0,(81,81,72),(0,0,0)))
            layers.append(Layer(pixel_map,(295, 272),(270,285),(270,259),(292,272),0,(81,81,72),(0,0,0)))
            layers.append(Layer(pixel_map,(295, 272),(320,283),(320,259),(298,272),0,(81,81,72),(0,0,0)))
            layers.append(Layer(pixel_map,(295, 272),(270,285),(295,297),(292,285),0,(81,81,72),(0,0,0)))
            layers.append(Layer(pixel_map,(295, 272),(320,283),(295,297),(298,285),0,(81,81,72),(0,0,0)))

            layers.append(Layer(pixel_map,(275, 260),(275,240),(340, 240),(276,241),0,(76,82,82),(0,0,0)))#багажник
            layers.append(Layer(pixel_map,(275, 260),(340,260),(340, 240),(339,259),0,(76,82,82),(0,0,0)))

            layers.append(Layer(pixel_map,(275, 285),(275,260),(195, 285),(250,261),0,(76,82,82),(0,0,0)))#нижний корпус
            layers.append(Layer(pixel_map,(195, 260),(275,260),(195, 285),(250,284),0,(76,82,82),(0,0,0)))

            layers.append(Layer(pixel_map,(40, 285),(40,260),(15,272),(38,280),0,(81,81,72),(0,0,0)))#заднее колесо
            layers.append(Layer(pixel_map,(40, 285),(40,260),(65,272),(42,280),0,(81,81,72),(0,0,0)))
            layers.append(Layer(pixel_map,(40, 285),(15,298),(15,272),(38,285),0,(81,81,72),(0,0,0)))
            layers.append(Layer(pixel_map,(40, 285),(65,296),(65,272),(42,285),0,(81,81,72),(0,0,0)))
            layers.append(Layer(pixel_map,(40, 285),(15,298),(40,310),(38,301),0,(81,81,72),(0,0,0)))
            layers.append(Layer(pixel_map,(40, 285),(65,296),(40,310),(42,301),0,(81,81,72),(0,0,0)))
            

            # # Домик------------------------------------------------------------------------------------------------------------------------------------
            # layers.append(Layer(pixel_map, (50, 150), (150, 150), (100, 100), (100, 125), 0, (200, 100, 50), (0, 0, 0))) # Крыша
            # layers.append(Layer(pixel_map, (50, 150), (50, 250), (150, 150), (75, 200), 0, (150, 75, 0), (0, 0, 0))) # Левая стена
            # layers.append(Layer(pixel_map, (50, 250), (150, 150), (150, 250), (125, 200), 0, (150, 75, 0), (0, 0, 0))) # Правая стена

            # # Дерево
            # layers.append(Layer(pixel_map, (150, 250), (160, 250), (155, 200), (155, 225), 0, (139, 69, 19), (0, 0, 0))) # Ствол
            # layers.append(Layer(pixel_map, (135, 200), (175, 200), (155, 150), (155, 175), 0, (0, 200, 0), (0, 0, 0))) # Крона

            

            # Ромашка (увеличенная)
            # # Лепестки
            # layers.append(Layer(pixel_map, (100, 210), (120, 180), (80, 180), (100, 190), 0, (255, 255, 255), (0, 0, 0))) # Верхний лепесток
            # layers.append(Layer(pixel_map, (100, 200), (120, 220), (80, 220), (100, 210), 0, (255, 255, 255), (0, 0, 0))) # Нижний лепесток
            # layers.append(Layer(pixel_map, (90, 200), (120, 190), (120, 210), (110, 200), 0, (255, 255, 255), (0, 0, 0))) # Правый лепесток
            # layers.append(Layer(pixel_map, (100, 200), (80, 190), (80, 210), (90, 200), 0, (255, 255, 255), (0, 0, 0))) # Левый лепесток
            
            



            for layer in layers:
                layer.draw()    
                  
            f = False

        pygame.display.flip()

        # Задержка для замедления отрисовки
        # pygame.time.delay(DELAY_MS)


if __name__ == "__main__":
    main()
