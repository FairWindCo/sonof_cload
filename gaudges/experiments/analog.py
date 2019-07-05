from kivy.uix.boxlayout import BoxLayout

__all__ = ('Gauge',)
__title__ = 'bkuri.gauge'
__version__ = '0.1'
__author__ = 'gauge@bkuri.com'

import kivy
kivy.require('1.7.1')

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.properties import BoundedNumericProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.label import Label
from kivy.uix.widget import Widget

class Gauge(Widget):
  angle_min, angle_max, bg, cx, cy, fg, radius, spacing = 272, 360, None, None, None, None, None, None
  area = ObjectProperty((100, 100))
  color_bg = ListProperty([1,1,1,0.1])
  color_value = ListProperty([1,1,1,1])
  color_labels = ListProperty([1,1,1,1])
  font_name = StringProperty('Times')
  font_size = StringProperty('200sp')
  footer = StringProperty("test")
  header = StringProperty("space")
  line_cap = StringProperty('')
  line_width = BoundedNumericProperty(10, min=1, max=200)
  max = BoundedNumericProperty(100, min=1)
  min = BoundedNumericProperty(0, min=0)
  mode = BoundedNumericProperty(0, min=0, max=2)
  value = NumericProperty(0)

  def __init__(self, **kwargs):
    super(Gauge, self).__init__(**kwargs)
    self.bg = Widget()
    self.fg = Widget()

    def draw_bg(*args):
      spacing = (self.line_width * 2)
      fs = '%dsp' % spacing

      self.bg.canvas.clear()
      with self.bg.canvas:
        self._color(self.color_bg)
        Line(circle=(self.cx, self.cy, self.radius, self.angle_min, (self.angle_min + self.angle_max)), width=self.line_width, cap=self.line_cap)

        if self.mode == 0:
          yh = (self.y + (self.spacing * 2))
          yf = (self.y - (self.spacing * 2))

        elif self.mode == 1:
          markers = (self.min, self.max)
          yh = (self.y + (self.spacing * 2))
          yf = (self.y + self.line_width)

        elif self.mode == 2:
          markers = (self.max, self.min)
          yh = self.y + self.area[1] - self.line_width
          yf = (self.y + self.spacing)

        if self.header: self._text(self.header, fs, yh)
        if self.footer: self._text(self.footer, fs, yf)

        if self.mode == 0: return
        for index, marker in enumerate(markers):
          marker = Label(color=self.color_labels, text=str(marker), size_hint=(None,None), font_name=self.font_name, font_size=fs)

          if self.mode == 1: marker.y = self.y - self.line_width
          else: marker.top = self.y + self.area[1] + self.line_width

          if index == 0: marker.x = self.x + spacing
          else: marker.right = self.x + self.area[0] - spacing
          Clock.schedule_once(marker.texture_update)

      self._update(*args)

    def mode(*args):
      self.angle_max = 360 if self.mode == 0 else 180
      self.angle_min = (182, 272, 92)[self.mode]
      Clock.schedule_once(calculate)

    def calculate(*args):
      self.cx = self.x + (self.area[0] / 2)
      self.cy = self.y + self.area[1] if self.mode == 2 else self.y
      self.radius = (max(self.area[0], self.area[1]) / 2) - self.line_width
      self.spacing = (self.area[1] / 3)
      Clock.schedule_once(draw_bg)

    self.add_widget(self.bg)
    self.add_widget(self.fg)
    self.bind(footer=draw_bg,header=draw_bg,mode=mode,value=self._update,area=calculate,pos=calculate)
    mode()

  def _color(self, c): return Color(c[0], c[1], c[2], c[3] or 1.)

  def _text(self, text, font_size, cy, mipmap=True):
    label = Label(color=self.color_labels,center=(self.cx, cy),text=text,font_name=self.font_name,font_size=font_size,mipmap=mipmap)
    Clock.schedule_once(label.texture_update)

  def _update(self, *args):
    if self.value < self.min: self.value = self.min
    elif self.value > self.max: self.value = self.max

    angle = self.angle_min + ((((self.value + (self.max / self.angle_max)) - self.min) * self.angle_max) / (self.max - self.min))
    value = int(self.value)

    self.fg.canvas.clear()
    with self.fg.canvas:
      self._color(self.color_value)
      Line(circle=(self.cx, self.cy, self.radius, self.angle_min, angle), width=self.line_width/2, cap=self.line_cap)
      y = (self.cy, self.y + self.spacing, self.y + (self.spacing * 2))[self.mode]
      self._text(str(value), self.font_size, y, mipmap=False)

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
      line_width=20,
      max=vmax,
      min=vmin,
      mode=0,
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