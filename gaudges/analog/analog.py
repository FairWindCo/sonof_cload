from kivy.app import App
from kivy.graphics.context_instructions import Translate, Rotate, Color, PopMatrix, PushMatrix
from kivy.graphics.vertex_instructions import Line, Ellipse
from kivy.properties import NumericProperty, BoundedNumericProperty, StringProperty, BooleanProperty, ColorProperty
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget

from gaudges.utils.kivy_utils import get_module_resource_path, get_mark_vector, register_default_fonts


class AnalogeGauge(Widget):
    '''
    Gauge class

    '''
    unit = NumericProperty(1.8)
    size_text = NumericProperty(10)
    value = BoundedNumericProperty(0, min_value=0, max_value=100, errorvalue=0)
    start_angle = BoundedNumericProperty(90, min_value=-360, max_value=360, errorvalue=0)
    angle_width = BoundedNumericProperty(180, min_value=0, max_value=360, errorvalue=0)
    min_value = NumericProperty(0)
    max_value = NumericProperty(100)
    rotate_clock = BooleanProperty(True)
    file_background = StringProperty("cadran.png")
    file_gauge = StringProperty("")
    file_needle = StringProperty("")

    half_widget_view = BooleanProperty(False)

    padding = BoundedNumericProperty(10, min_value=0, max_value=360, errorvalue=0)

    mark_count = BoundedNumericProperty(10, min_value=0, max_value=360, errorvalue=0)
    mark_sub_count = BoundedNumericProperty(10, min_value=0, max_value=100, errorvalue=0)
    show_middle_marks = BooleanProperty(True)
    show_sub_marks = BooleanProperty(True)
    mark_size = BoundedNumericProperty(20, min_value=0, max_value=300, errorvalue=0)
    mark_mid_size = BoundedNumericProperty(15, min_value=0, max_value=300, errorvalue=0)
    mark_sub_size = BoundedNumericProperty(10, min_value=0, max_value=300, errorvalue=0)

    mark_color = ColorProperty('#ffffffff')
    mark_sub_color = ColorProperty('#ffffffff')
    mark_mid_color = ColorProperty('#ffffffff')

    needle_color = ColorProperty('#ff0000ff')
    glab_color = ColorProperty('#ff0000ff')


    def __init__(self, **kwargs):
        super(AnalogeGauge, self).__init__(**kwargs)
        self._gauge_widget = Widget()
        self._gauge = self._gauge_widget

        self._needle_widget_safe = Widget()
        self._needle_widget = self._needle_widget_safe

        self._form_processor_constants()

        self._needle = Scatter(
            size=self.size,
            do_rotation=False,
            do_scale = False
        )

        self._background_widget = Widget()
        self._background = Scatter(
            size=self.size,
            do_rotation=False,
            do_scale=False
        )

        self._glab = Label(font_size=self.size_text, markup=True, font_name='digital')

        self._needle.add_widget(self._needle_widget)

        self.add_widget(self._background)
        self.add_widget(self._gauge)
        self.add_widget(self._glab)
        self.add_widget(self._needle)


        self.bind(pos=self._update)
        self.bind(size=self._update)
        self.bind(value=self._turn)

        self.bind(file_gauge=self._reform_widget_graphics)
        self.bind(file_needle=self._reform_widget_graphics)
        self.bind(file_background=self._reform_widget_graphics)

        self.bind(min_value=self._form_processor_constants)
        self.bind(rotate_clock=self._form_processor_constants)
        self.bind(max_value=self._form_processor_constants)
        self.bind(start_angle=self._form_processor_constants)
        self.bind(angle_width=self._form_processor_constants)

        self.bind(mark_color=self._create_gaudge)
        self.bind(mark_sub_color=self._create_gaudge)
        self.bind(mark_mid_color=self._create_gaudge)
        self.bind(show_middle_marks=self._create_gaudge)
        self.bind(show_middle_marks=self._create_gaudge)
        self.bind(mark_count=self._create_gaudge)
        self.bind(mark_sub_count=self._create_gaudge)

        self.bind(needle_color=self._create_needle)

        self.bind(padding=self._update)

        self._update()
        self._reform_widget_graphics()
        self._turn()

    def _form_processor_constants(self, *args):
        self.property('value').set_min(self, self.min_value)
        self.property('value').set_max(self, self.max_value)
        self.unit = self.angle_width / abs(self.max_value - self.min_value) * (-1 if self.rotate_clock else 1)
        #print(self.unit, self.angle_width)

    def _reform_widget_graphics(self, *args):
        #print(self.size)

        if self.file_gauge:
            self.remove_widget(self._gauge)
            self._gauge=get_module_resource_path(self.file_gauge, size=self.size, resource_package=__name__)
            self.add_widget(self._gauge)
        else:
            self.remove_widget(self._gauge)
            self._gauge = self._gauge_widget
            self.add_widget(self._gauge)

        if self.file_background:
            self._background.remove_widget(self._background_widget)
            self._background_widget=get_module_resource_path(self.file_background, size=self.size, resource_package=__name__)
            self._background.add_widget(self._background_widget)

        if self.file_needle:
            self._needle.remove_widget(self._needle_widget)
            self._needle_widget=get_module_resource_path(self.file_needle, size=self.size, resource_package=__name__)
            self._needle.add_widget(self._needle_widget)
        else:
            self._needle.remove_widget(self._needle_widget)
            self._needle_widget = self._needle_widget_safe
            self._needle.add_widget(self._needle_widget)


    def _turn(self, *args):
        '''
        Turn needle, 1 degree = 1 unit, 0 degree point start on 50 value.

        '''
        self._needle.center_x = self._gauge.center_x
        self._needle.center_y = self._gauge.center_y
        self._needle.rotation = self.start_angle + (self.value - self.min_value) * self.unit
        #print(self.start_angle, self.unit,self.value,self.min_value,self._needle.rotation)
        self._glab.text = "[b]{0:.0f}[/b]".format(self.value)

    def _create_needle(self, *args):
        if self._needle_widget == self._needle_widget_safe:
            self._needle_widget_safe.canvas.clear()
            with self._needle_widget_safe.canvas:
                Color(*self.needle_color)
                Line(points=(*self._needle_widget_safe.center, self._needle_widget_safe.center_x, self._needle_widget_safe.center_y+self.circle_radius))
                Line(points=(*self._needle_widget_safe.center, self._needle_widget_safe.center_x,
                             self._needle_widget_safe.center_y + self.circle_radius-20), width=1.5)
                Ellipse(pos=(self._needle_widget_safe.center_x-5,self._needle_widget_safe.center_y-5), size=(10,10))


    def _create_gaudge(self, *args):
        if self._gauge == self._gauge_widget:

            self._gauge_widget.canvas.clear()
            if self.mark_count>0:
                delta_mark = self.angle_width / self.mark_count
                mark_width = 10
                mark_end = min(self.width, self.height)/2
                with self._gauge_widget.canvas:

                    if self.show_sub_marks:
                        Color(*self.mark_sub_color)
                        sub_delta_mark=delta_mark / self.mark_sub_count
                        count = self.mark_count*self.mark_sub_count + 1
                        sub_start_size = self.circle_radius - self.mark_sub_size
                        for i in range(count):
                            Line(points=get_mark_vector(*self.circle_pos, sub_start_size, self.mark_sub_size,
                                                        self.start_angle - sub_delta_mark * i))

                    if self.show_middle_marks:
                        Color(*self.mark_mid_color)
                        sub_delta_mark=delta_mark / 2
                        count = self.mark_count*2 + 1
                        sub_start_size = self.circle_radius - self.mark_mid_size
                        for i in range(count):
                            Line(points=get_mark_vector(*self.circle_pos, sub_start_size, self.mark_mid_size,
                                                        self.start_angle - sub_delta_mark * i))

                    Color(*self.mark_color)
                    start_size = self.circle_radius - self.mark_size
                    for i in range(self.mark_count+1):
                        Line(points=get_mark_vector(*self.circle_pos, start_size, self.mark_size, self.start_angle - delta_mark*i))



    def _update(self, *args):
        '''
        Update gauge and needle positions after sizing or positioning.

        '''
        if self.half_widget_view:
            self.circle_radius = min(*self.size) - self.padding * 2
            self.circle_size = (self.circle_radius, self.circle_radius)
            self.circle_pos = (self.center_x, self.center_y-self.circle_radius/2)
            self._bg_pos = (self.x, self.y - self.circle_radius/2)
        else:
            self.circle_radius = min(*self.size)/2 - self.padding
            self.circle_size = (self.circle_radius, self.circle_radius)
            self.circle_pos = self.center
            self._bg_pos = (self.x, self.y)




        self._needle.size = self.size
        self._gauge.size = self.size
        self._gauge.pos = self.pos
        self._gauge.center = self.circle_pos

        self._needle.pos = (self.x, self.y)
        self._needle.center = self.circle_pos

        self._background.pos = self._bg_pos


        self._needle_widget.size = self.size
        self._background_widget.size = self.size

        self._glab.center_x = self._gauge.center_x
        self._glab.center_y = self.center_y + (self.height / 4)

        self._create_gaudge()
        self._create_needle()


    def set_animate(self, value, easing = 'in_out_quad', speed = 1):
        from kivy.animation import Animation
        Animation(value=value, duration=speed, t=easing).start(self)


if __name__ == '__main__':
    class GaugeApp(App):
        def build(self):
            from kivy.uix.slider import Slider
            register_default_fonts()

            def test(*ars):
                #gauge.value = s.value
                gauge.set_animate(s.value)

            from kivy.uix.boxlayout import BoxLayout
            box = BoxLayout(orientation='vertical', spacing=10, padding=10)
            gauge = AnalogeGauge(value=50, size_text=80, rotate_clock=True, start_angle=90, angle_width=180, half_widget_view=True)
            box.add_widget(gauge)

            s = Slider(min=0, max=100, value=50)
            s.bind(value=test)
            box.add_widget(s)
            #gauge.file_gauge = 'cadran.png'
            #gauge.file_gauge = ''
            return box



    GaugeApp().run()