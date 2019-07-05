#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

'''
Gauge
=====

The :class:`Gauge` widget is a widget for displaying gauge.

.. note::

Source svg file provided for customing.

'''
from gaudges.utils.kivy_utils import get_module_resource_path

__all__ = ('Gauge',)

__title__ = 'garden.gauge'
__version__ = '0.1'
__author__ = 'julien@hautefeuille.eu'

import kivy

kivy.require('1.7.1')
from kivy.app import App
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.properties import BoundedNumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar


class Gauge(Widget):
    '''
    Gauge class

    '''

    unit = NumericProperty(1.8)
    file_gauge = StringProperty("cadran.png")
    file_needle = StringProperty("needle.png")
    size_text = NumericProperty(10)
    value = BoundedNumericProperty(0, min_value=0, max_value=100, errorvalue=0)

    def __init__(self, curent_value=0, min_value=0, max_value=100, half_widget=True, show_progress=True, **kwargs):

        super(Gauge, self).__init__(**kwargs)

        self.property('value').set_min(self, min_value)
        self.property('value').set_max(self, max_value)
        self.value = curent_value

        self.midle_value = (max_value - min_value) / 2
        self._show_progress = show_progress

        self._gauge = Scatter(
            size=self.size,
            do_rotation=False,
        )

        # _img_gauge = Image(source=get_module_resource_path(self.file_gauge), size=(self.size_gauge, self.size_gauge))
        self._img_gauge = get_module_resource_path(self.file_gauge, size=self.size, resource_package=__name__)

        self._needle = Scatter(
            size=self.size,
            do_rotation=False,
        )

        self._img_needle = get_module_resource_path(self.file_needle, size=self.size, resource_package=__name__)

        self._glab = Label(font_size=self.size_text, markup=True)


        self._gauge.add_widget(self._img_gauge)
        self._needle.add_widget(self._img_needle)

        self.add_widget(self._gauge)
        self.add_widget(self._needle)
        self.add_widget(self._glab)

        if show_progress:
            self._progress = ProgressBar(max=max_value, height=20, value=curent_value)
            self.add_widget(self._progress)

        self.bind(pos=self._update)
        self.bind(size=self._update)
        self.bind(value=self._turn)
        self.unit = 90 / self.midle_value if half_widget else 180 / self.midle_value
        self._turn()


    def _update(self, *args):
        '''
        Update gauge and needle positions after sizing or positioning.

        '''
        self._img_gauge.size = self.size
        self._img_needle.size = self._img_gauge.size
        self._needle.size  = self.size
        self._gauge.size = self.size
        self._gauge.pos = self.pos
        self._gauge.center = self.center
        self._needle.pos = (self.x, self.y)
        self._needle.center = self._gauge.center
        self._glab.center_x = self._gauge.center_x
        self._glab.center_y = self.center_y + (self.height / 4)

        if self._show_progress:
            element_size = min(self.height, self.width)
            self._progress.x = self._gauge.center_x - element_size/2
            self._progress.y = self._gauge.y + (self.height / 4)
            self._progress.width = element_size

    def _turn(self, *args):
        '''
        Turn needle, 1 degree = 1 unit, 0 degree point start on 50 value.

        '''
        self._needle.center_x = self._gauge.center_x
        self._needle.center_y = self._gauge.center_y
        self._needle.rotation = (self.midle_value * self.unit) - (self.value * self.unit)
        self._glab.text = "[b]{0:.0f}[/b]".format(self.value)
        if self._show_progress:
            self._progress.value = self.value

    def set_animate(self, value, easing = 'in_out_quad', speed = 1):
        from kivy.animation import Animation
        Animation(value=value, duration=speed, t=easing).start(self)

if __name__ == '__main__':
    class GaugeApp(App):
        def build(self):
            from kivy.uix.slider import Slider

            def test(*ars):
                #gauge.value = s.value
                gauge.set_animate(s.value)
                print(s.value)

            def test_(*ars):
                gauge_.value = s1.value
                print(s.value)

            box = BoxLayout(orientation='vertical', spacing=10, padding=10)
            gauge = Gauge(50, 0, 200, size_text=9)
            gauge_ = Gauge(value=50, size_text=19, half_widget=True, show_progress=False)

            box.add_widget(gauge)
            box.add_widget(gauge_)

            s = Slider(min=0, max=200, value=50)
            s.bind(value=test)
            box.add_widget(s)

            s1 = Slider(min=0, max=100, value=50)
            s1.bind(value=test_)
            box.add_widget(s1)

            return box



    GaugeApp().run()


