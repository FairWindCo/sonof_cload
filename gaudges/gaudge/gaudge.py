from itertools import chain

from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle, Line, Mesh
from kivy.uix.widget import Widget

from gaudges.utils import GradientBuilder
from gaudges.utils.kivy_utils import register_default_fonts, create_round_line, create_rect, create_brush


def paint_gaudge_background(canvas, pos, size, *colors, **atribute):
    canvas.clear()
    with canvas:
        Color(1,1,1,1)

        #Line(points=(pos[0],pos[1],pos[0],pos[1]+size[1] ,pos[0]+size[0], pos[1]+size[1]),close=True, texture=GradientBuilder.GradientBuilder.noise((10,10)))
        textute = GradientBuilder.GradientBuilder.noise((1,10))
        #Rectangle(pos=pos, size=size, corner_radius=10, texture=textute)

        mesh = create_rect(pos=pos, size=size, color=(100, 0, 0, 255), radius=5)
        mesh.texture = GradientBuilder.GradientBuilder.noise((1,1))
        #mesh.texture = create_brush(color=(100, 0, 0, 255))
        pass

class LCDGauge(Widget):
    def __init__(self, **kwargs):
        super(LCDGauge, self).__init__(**kwargs)
        self.bind(pos=self._update)
        self.bind(size=self._update)
        self.paint_gaudge_background()

    def paint_gaudge_background(self):
        paint_gaudge_background(self.canvas, self.pos, self.size)

    def _update(self, *args):
        self.paint_gaudge_background()


if __name__ == '__main__':
    class GaugeApp(App):
        def build(self):
            from kivy.uix.slider import Slider
            register_default_fonts()

            def test(*ars):
                #gauge.value = s.value
                #gauge.set_animate(s.value)
                pass

            from kivy.uix.boxlayout import BoxLayout
            box = BoxLayout(orientation='vertical', spacing=10, padding=10)
            gauge = LCDGauge()
            box.add_widget(gauge)

            s = Slider(min=0, max=100, value=50)
            s.bind(value=test)
            box.add_widget(s)
            #gauge.file_gauge = 'cadran.png'
            #gauge.file_gauge = ''
            return box



    GaugeApp().run()