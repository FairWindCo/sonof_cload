import itertools

from kivy.app import App
from kivy.graphics.vertex_instructions import Line
from kivy.multistroke import xrange
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture

class Gradient(object):
    @staticmethod
    def horizontal(*args):
        texture = Texture.create(size=(len(args), 1), colorfmt='rgba')
        buf = bytes([int(v * 255) for v in itertools.chain(*args)])  # flattens
        texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        return texture

    @staticmethod
    def vertical(*args):
        texture = Texture.create(size=(1, len(args)), colorfmt='rgba')
        buf = bytes([int(v * 255) for v in itertools.chain(*args)])  # flattens
        texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        return texture

    @staticmethod
    def radial(center_color, border_color, *args):
        size = (64, 64)
        tex = Texture.create(size=size)

        buf = bytes([int(v * 255) for v in itertools.chain(*args)])  # flattens
        sx_2 = size[0] / 2
        sy_2 = size[1] / 2

        buf = ''
        for x in xrange(-sx_2, sx_2):
            for y in xrange(-sy_2, sy_2):
                a = x / (1.0 * sx_2)
                b = y / (1.0 * sy_2)
                d = (a ** 2 + b ** 2) ** .5

                for c in (0, 1, 2):
                    buf += chr(max(0,
                                   min(255,
                                       int(center_color[c] * (1 - d)) +
                                       int(border_color[c] * d))))

        tex.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        return tex

    @staticmethod
    def radial_gradient(border_color=(1, 1, 0), center_color=(1, 0, 0),
            size=(64, 64)):
        from kivy.graphics import Fbo, Rectangle, Color
        fbo = Fbo(size=size)
        fbo.shader.fs = '''
        $HEADER$
        uniform vec3 border_color;
        uniform vec3 center_color;
        void main (void) {
            float d = clamp(distance(tex_coord0, vec2(0.5, 0.5)), 0., 1.);
            gl_FragColor = vec4(mix(center_color, border_color, d), 1);
        }
        '''

        # use the shader on the entire surface
        fbo['border_color'] = map(float, border_color)
        fbo['center_color'] = map(float, center_color)
        with fbo:
            Color(1, 1, 1)
            Rectangle(size=size)
        fbo.draw()

        return fbo.texture

class MyWidget(Widget):
    def __init__(self, **args):
        super(MyWidget, self).__init__(**args)

        self.texture = Gradient.radial_gradient((0,0,0,1),(1,1,1,1))

        with self.canvas:
            Rectangle(pos=self.pos, size=self.size, texture=self.texture)
            Line(points=[100, 100, 200, 100, 100, 200], width=10, texture=self.texture)


class TestApp(App):
    def build(self):
        return MyWidget(size=(200, 200))


if __name__ == '__main__':
    TestApp().run()