from kivy.uix.boxlayout import BoxLayout

from gaudges.utils.kivy_utils import get_size_in_pixels

__all__ = ('Gauge',)
__title__ = 'fairwind.gauge'
__version__ = '0.1'
__author__ = 'sergey.manenok@gmail.com'


import kivy
kivy.require('1.7.1')

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.properties import BoundedNumericProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.label import Label
from kivy.uix.widget import Widget

class Gauge(Widget):
  angle_min, angle_max, bg, cx, cy, fg, radius = 270, 360, None, None, None, None, None
  color_bg = ListProperty([1,1,1,0.1])
  color_value = ListProperty([1,0.4,0.4,1])
  color_labels = ListProperty([1,1,1,1])
  font_name = StringProperty('Times')
  font_size = StringProperty('100sp')
  footer = StringProperty("")
  header = StringProperty("")
  line_cap = StringProperty('round')
  line_width = BoundedNumericProperty(10, min=1, max=200)
  max = BoundedNumericProperty(100, min=1)
  min = BoundedNumericProperty(0, min=0)
  mode = BoundedNumericProperty(0, min=0, max=2)
  value = NumericProperty(0)
  spacing = NumericProperty(10)

  def __init__(self, **kwargs):


    super(Gauge, self).__init__(**kwargs)
    self.bg = Widget()
    self.fg = Widget()

    def draw_bg(*args):
      spacing = (self.line_width * 2)
      fs = '%dsp' % spacing
      fs_pixel_size = get_size_in_pixels(fs)
      self.bg.canvas.clear()
      with self.bg.canvas:
        self._color(self.color_bg)

        Line(circle=(self.cx, self.cy, self.radius, self.angle_min, (self.angle_min + self.angle_max)), width=self.line_width, cap=self.line_cap)



        if self.mode == 0:
          font_pixels = get_size_in_pixels(self.font_size)
          yh = (self.cy + fs_pixel_size + self.spacing+font_pixels/2)
          yf = (self.cy - fs_pixel_size - self.spacing-font_pixels/2)

        elif self.mode == 1:
          markers = (self.min, self.max)
          yh = self.top - fs_pixel_size/2
          yf = (self.y + fs_pixel_size/2)

        elif self.mode == 2:
          markers = (self.max, self.min)
          yh = self.top - fs_pixel_size/2
          yf = (self.y + fs_pixel_size/2)

        if self.header: self._text(self.header, fs, yh)
        if self.footer: self._text(self.footer, fs, yf)

        if self.mode > 0:
          for index, marker in enumerate(markers):
            marker = Label(color=self.color_labels, text=str(marker), size_hint=(None,None), font_name=self.font_name, font_size=fs)

            if self.mode == 1: marker.y = self.cy - self.line_width
            else: marker.top = self.cy + self.line_width

            if index == 0: marker.x = self.x + spacing
            else: marker.right = self.x + self.msize[0] - spacing
            Clock.schedule_once(marker.texture_update)

      self._update(*args)

    def mode(*args):
      self.angle_max = 360 if self.mode == 0 else 180
      self.angle_min = (180, 270, 90)[self.mode]
      Clock.schedule_once(calculate)

    def calculate(*args):
      mwidth = self.right - self.x
      mheight = self.top - self.y
      self.msize = (mwidth, mheight)
      self.element_size = mheight if mheight < mwidth else mwidth
      self.cx = self.x + mwidth / 2
      self.cy = self.y + mheight / 2
      self.bg.size = self.msize
      self.fg.size = self.msize
      self.radius = self.element_size/2 - self.line_width - self.spacing
      Clock.schedule_once(draw_bg)
      Clock.schedule_once(self._update)

    self.add_widget(self.bg)
    self.add_widget(self.fg)
    self.bind(footer=draw_bg,header=draw_bg,mode=mode,value=self._update,pos=calculate, size=calculate, spacing=calculate)
    mode()

  def _color(self, c): return Color(c[0], c[1], c[2], c[3] or 1.)

  def _text(self, text, font_size, cy, mipmap=True):
    label = Label(color=self.color_labels,center=(self.cx, cy),text=text,font_name=self.font_name,font_size=font_size,mipmap=mipmap, halign="center", valign="middle")
    Clock.schedule_once(label.texture_update)

  def _update(self, *args):
    print('update')
    if self.value < self.min: self.value = self.min
    elif self.value > self.max: self.value = self.max

    angle = self.angle_min + ((((self.value + (self.max / self.angle_max)) - self.min) * self.angle_max) / (self.max - self.min))
    value = int(self.value)

    self.fg.canvas.clear()
    font_pixels=get_size_in_pixels(self.font_size)
    with self.fg.canvas:
      self._color(self.color_value)
      if value > self.min:
        Line(circle=(self.cx, self.cy, self.radius, self.angle_min, angle), width=self.line_width/2, cap=self.line_cap)
      y = (self.cy, self.cy + font_pixels/2, self.cy - font_pixels/2)[self.mode]
      self._text(str(value), self.font_size, y, mipmap=False)

  def set_animate(self, value, easing = 'in_out_quad', speed = 1):
    from kivy.animation import Animation
    Animation(value=value, duration=speed, t=easing).start(self)

class SampleApp(App):
  def build(self):
    from kivy.animation import Animation
    from kivy.uix.slider import Slider
    from random import random

    def update(*args):
      Animation(value=slider.value,duration=speed,t=easing).start(gauge)

    easing = 'in_out_quad'
    speed = 1
    vmin = 0
    vmax = 100
    value = round(random() * vmax)
    gauge = Gauge(
      header='km/h',
      footer='test',
      line_width=10,
      max=vmax,
      min=vmin,
      mode=2,
      value = value
    )

    slider = Slider(min=vmin, max=vmax, value=vmin)
    slider.value = value
    slider.bind(value=update)

    layout = BoxLayout()
    layout.add_widget(gauge)
    layout.add_widget(slider)

    return layout

if __name__ == "__main__":
  SampleApp().run()