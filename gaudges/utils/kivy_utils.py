import io
import os
import re
import sys
from itertools import chain

import math
from kivy.core.image import Image as CoreImage, Texture
from kivy.graphics.vertex_instructions import Rectangle, Mesh
from kivy.uix.image import Image
from kivy.vector import Vector
from kivy.properties import dpi2px


def get_from_vector(cx, cy, leng, angle):
    vector = Vector(0, leng).rotate(angle)
    return vector[0] + cx, vector[1] + cy


def get_mark_vector(cx, cy, leng, width, angle):
    vector1 = get_from_vector(cx, cy, leng, angle)
    vector2 = get_from_vector(cx, cy, leng+width, angle)
    return vector1[0], vector1[1], vector2[0], vector2[1]


def get_size_in_pixels(size):
    res = 0
    if size:
        try:
            res = float(size)
        except ValueError:
            regex = r'([\d]+)(\D+)'
            searched = re.findall(regex, size)
            if searched:
                resize = searched[0]
                res = dpi2px(resize[0], resize[1])
    return res


def clamp(min_val, max_val, value):
    return max(min_val,(min(max_val, value)))


def interpolate_color(lower_color_bound, upper_color_bound, position):
    assert len(lower_color_bound) < 2 and len(upper_color_bound) < 2, "Incorrect arguments"
    pos = (position - lower_color_bound[0]) / (upper_color_bound[0] - lower_color_bound[0])
    length = min(len(lower_color_bound), len(lower_color_bound))
    return tuple([clamp(lower_color_bound[i], (upper_color_bound[i] - lower_color_bound[i]) * pos) for i in range(1, length)])


def calculate_stops(offset, *stops):
    min_step = sys.float_info.min
    res_stops = list()

    for stop in stops:
        offs, *color = stop
        new_offset_bd = (offset + offs) % 1

        if new_offset_bd == 0:
            new_offset_bd = 1
            res_stops.append((min_step, *color))
        elif new_offset_bd == 1:
            new_offset_bd -= min_step

        res_stops.append((new_offset_bd, color))

    res_stops.sort(key=lambda val: val[0])

    if res_stops[0][0] > 0:
        first, *color = res_stops[0]
        res_stops = [(0, *color), *res_stops]
    if res_stops[-1][0] < 1:
        first, *color = res_stops[-1]
        res_stops.append((1, *color))

    return res_stops


def normalize_stops(offset, *stops, reverse=False):
    offset = clamp(0, 1, offset)
    if not stops:
        stops = [(0, 0, 0, 0, 0), (1, 0, 0, 0, 0)]

    sorted_stops = calculate_stops(offset, *stops)

    if reverse:
        sorted_stops.reverse()
        sorted_stops = [(1 - fr, *col) for fr, *col in sorted_stops]

    return sorted_stops


def adjust_angle(dx, dy, angle):
    if dx >= 0 >= dy:
        result = 90 - angle
    elif dx >= 0 and dy >= 0:
        result = 90 + angle
    elif dx <= 0 <= dy:
        result = 90 + angle
    elif dx <= 0 and dy <= 0:
        result = 450 - angle
    else:
        result = angle
    return result


def get_module_resource_path(file_name, size, resource_package=__name__):
    import os
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if regex.match(file_name) or os.path.isfile(file_name):
        image = Image(source=file_name)
    else:
        __requires__ = ["CherryPy < 3"]  # Must be set before pkg_resources import
        import pkg_resources
        resource_path = '/' + file_name

        reader = pkg_resources.resource_stream(resource_package, resource_path)
        if reader:
            stream = io.BytesIO(reader.read())
        _, file_extension = os.path.splitext(file_name)

        im = CoreImage(stream, ext=file_extension[1:])

        image = Image(source="")
        image.texture = im.texture
        image.reload()
        image.size = size
    return image


CONNECT_LEFT = 1
CONNECT_RIGHT = 2
CONNECT_TOP = 3
CONNECT_BOTTOM = 4
CONNECT_CENTER = 0


def convert_points_tuples(points, text_x=0, text_y=0):
    vertices = [(x, y, 0, 0) for x, y in points]
    vertices = chain.from_iterable(vertices)
    return list(vertices)

def create_round_line(pos, radius, start_angle=0, end_angle=360, point_count=100, connect_type=CONNECT_CENTER):
    center_point_x = pos[0]
    center_point_y = pos[1]

    if connect_type == CONNECT_LEFT:
        center_point_x += radius
    elif connect_type == CONNECT_RIGHT:
        center_point_x -= radius
    elif connect_type == CONNECT_TOP:
        center_point_y += radius
    elif connect_type == CONNECT_BOTTOM:
        center_point_y -= radius


    delta_angle = (end_angle - start_angle) / (point_count)

    print(delta_angle)

    # for i in range(point_count):
    #     x = center_point_x + math.cos(start_radian + delta_angle * i) * radius
    #     y = center_point_y + math.sin(start_radian + delta_angle * i) * radius
    radian = math.pi / 180

    return [(center_point_x + math.cos((start_angle + delta_angle * i)*radian) * radius,
             center_point_y + math.sin((start_angle + delta_angle * i)*radian) * radius) for i in range(point_count)]


def create_brush(color=(0, 0, 0, 0), format_c='rgba'):
    tex = Texture.create(size=(10, 10))
    buf = []
    for i in range(100):
        buf += [restriction(c, 0, 255) for c in color]
    tex.blit_buffer(bytes(buf), colorfmt=format_c, bufferfmt='ubyte')

def create_rect_gradient_vertical(pos, size, *color, radius=0):
    color_count = len(color)
    if color_count<2:
        return None


def create_rect(pos, size, color=(1, 1, 1, 1), radius=0, format_c='rgba', correct_radius=True):
    min_size = min(*size)
    if correct_radius and min_size <= 2*radius:
        radius = min_size / 2
    texture = create_brush(color, format_c=format_c)

    if radius<=0 or min_size < 2*radius:
        return Rectangle(pos=pos, size=size, texture=texture)
    else:
        left_down_coner_center = pos[0] + radius, pos[1] + radius
        left_upper_coner_center = pos[0] + radius, pos[1] + size[1] - radius
        right_down_coner_center = pos[0] - radius + size[0], pos[1]+radius
        right_upper_coner_center = pos[0] - radius + size[0], pos[1] +size[1] - radius
        points = []


        points += create_round_line(left_down_coner_center, radius, start_angle=270, end_angle=180,
                                    point_count=int(radius))
        points += create_round_line(left_upper_coner_center, radius, start_angle=180, end_angle=90,
                                    point_count=int(radius))
        points += create_round_line(right_upper_coner_center, radius, start_angle=90, end_angle=0,
                                    point_count=int(radius))
        points += create_round_line(right_down_coner_center, radius, start_angle=360, end_angle=270,
                                    point_count=int(radius))

        vertex = convert_points_tuples(points)

        return Mesh(vertices=vertex,
                 mode='triangle_fan',
                 texture=texture,
                 indices=range(int(radius)*4))


def register_default_fonts():
    from kivy.core.text import LabelBase

    base_path = os.path.dirname(__file__)

    default_fonts_def = [
        {
            "name": "elektra",
            "fn_regular": base_path + "/data/fonts/elektra.ttf",
        },
        {
            "name": "RobotoCondensed",
            "fn_regular": base_path + "/data/fonts/RobotoCondensed-Regular.ttf",
            "fn_bold": base_path + "/data/fonts/RobotoCondensed-Bold.ttf",
            "fn_italic": base_path + "/data/fonts/RobotoCondensed-Light.ttf",
        },
        {
            "name": "Lato",
            "fn_regular": base_path + "/data/fonts/Lato-Reg.otf",
            "fn_bold": base_path + "/data/fonts/Lato-Bol.otf",
            "fn_italic": base_path + "/data/fonts/Roboto-Light.ttf",
        },
        {
            "name": "Roboto",
            "fn_regular": base_path + "/data/fonts/Roboto-Regular.ttf",
            "fn_bold": base_path + "/data/fonts/Roboto-Bold.ttf",
            "fn_italic": base_path + "/data/fonts/Roboto-Light.ttf",
            "fn_bolditalic": base_path + "/data/fonts/Roboto-Medium.ttf"
        },
        {
            "name": "digital",
            "fn_regular": base_path + "/data/fonts/digital.ttf",
            "fn_bold": base_path + "/data/fonts/digitalreadoutb.ttf",
            "fn_italic": base_path + "/data/fonts/digitalreadout.ttf",
        },
    ]

    for font in default_fonts_def:
        LabelBase.register(**font)

def restriction(value, min_value, max_value):
    if value > max_value:
        return max_value
    elif value < min_value:
        return min_value
    else:
        return value
