def normalize(vector):
    length = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
    if length == 0:
        return (0, 0)
    return (vector[0] / length, vector[1] / length)

def distance(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def lerp(start, end, t):
    return start + (end - start) * t

def rotate_vector(vector, angle):
    import math
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    return (vector[0] * cos_angle - vector[1] * sin_angle,
            vector[0] * sin_angle + vector[1] * cos_angle)