def combine_to_layer(triangle_code: str, fill_code: str) -> str:
    # Извлекаем аргументы из функции draw_triangle
    triangle_args = triangle_code.split('(', 1)[1].rsplit(')', 1)[0].split(',', 1)[1]
    # Извлекаем аргументы из функции algorithm_A_fill
    fill_args = fill_code.split('(', 1)[1].rsplit(')', 1)[0].split(',', 1)[1]
    
    # Формируем строку для добавления в layers
    combined_code = f"layers.append(Layer(pixel_map,{triangle_args},{fill_args}))"
    return combined_code

# Пример строк
triangle_code = "draw_triangle(pixel_map, (100, 100),(100,150),(105,100))"
fill_code = "algorithm_A_fill(pixel_map,(102,101),0,(183,165,144),(0,0,0))"

# Преобразование
result = combine_to_layer(triangle_code, fill_code)
print(result)
