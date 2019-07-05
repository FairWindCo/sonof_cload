import itertools
import random

from kivy.app import App
from kivy.multistroke import xrange
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture

from gaudges.utils.kivy_utils import restriction


class GradientBuilder:

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
    def radial(center_color, border_color, size=(64, 64)):

        tex = Texture.create(size=size)

        cx = int(size[0] / 2)
        cy = int(size[1] / 2)

        # for x in xrange(-cx, cx):
        #     for y in xrange(-cy, cy):
        #         d = (((x/cx) ** 2 + (y/cy) ** 2) ** .5)
        #         print(d, end=' ')
        #     print(end='\n')

        distances = [(((x/cx) ** 2 + (y/cy) ** 2) ** .5) for x in xrange(-cx, cx) for y in xrange(-cy, cy)]

        buf = [restriction(int(center_color[c] * (1 - d)) + int(border_color[c] * d), 0, 255) for d in distances for c in (0, 1, 2, 3)]

        tex.blit_buffer(bytes(buf), colorfmt='rgba', bufferfmt='ubyte')
        return tex

    @staticmethod
    def radial_strict(center_color, border_color, size=(64, 64)):
        tex = Texture.create(size=size)

        cx = int(size[0] / 2)
        cy = int(size[1] / 2)

        # for x in xrange(-cx, cx):
        #     for y in xrange(-cy, cy):
        #         d = (((x/cx) ** 2 + (y/cy) ** 2) ** .5)
        #         print(d, end=' ')
        #     print(end='\n')

        distances = [(((x / cx) ** 2 + (y / cy) ** 2) ** .5) for x in xrange(-cx, cx) for y in xrange(-cy, cy)]

        buf = [restriction(int(center_color[c] * (1 - d)) + int(border_color[c] * d), 0, 255) if d <= 1 else 0 for d in distances for c in (0, 1, 2, 3)]

        tex.blit_buffer(bytes(buf), colorfmt='rgba', bufferfmt='ubyte')
        return tex

    @staticmethod
    def noise(size=(64, 64)):
        tex = Texture.create(size=size)




        buf = [int(random.uniform(0, 255)) for x in range(size[0]) for y in range(size[1]) for c in range(3)]
        #print(buf)
        tex.blit_buffer(bytes(buf), colorfmt='rgb', bufferfmt='ubyte')
        return tex

    @staticmethod
    def radial_shdr(border_color=(1, 1, 0), center_color=(1, 0, 0),
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
        fbo['border_color'] = tuple(map(float, border_color))
        fbo['center_color'] = tuple(map(float, center_color))
        with fbo:
            Color(1, 1, 1)
            Rectangle(size=size)
        fbo.draw()

        return fbo.texture


if __name__ == '__main__':
    class MyWidget(Widget):
        def __init__(self, **args):
            super(MyWidget, self).__init__(**args)

            self.texture = GradientBuilder.radial_shdr((0, 100, 0, 255), (100, 0, 100, 255), self.size)
            self.texture = GradientBuilder.radial_shdr((0, 1, 0), (1, 0, 1), self.size)
            #self.texture = GradientBuilder.noise(self.size)

            with self.canvas:
                Rectangle(pos=self.pos, size=self.size, texture=self.texture)


    class TestApp(App):
        def build(self):
            return MyWidget(size=(200, 200))
    TestApp().run()