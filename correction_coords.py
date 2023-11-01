import math

def transform(coords):
    max_x = 961  # Maximum value for x
    max_y = 621  # Maximum value for y
    max_correction_x = 40 # Maximum correction for x 
    max_correction_y = 20  # Maximum correction for y
    
    x, y = coords
    correction_factor_x = 2 - (max_x - max_correction_x) / max_x
    correction_factor_y = (max_y - max_correction_y) / max_y 
    print(correction_factor_y)
    corrected_x = x * correction_factor_x
    corrected_y = y * correction_factor_y

    corrected_coords = (corrected_x, corrected_y)
    return corrected_coords

coords = (450, 621)  
corrected_coords = transform(coords)
print("Original coordinates:", coords)
print("Corrected coordinates:", corrected_coords)
