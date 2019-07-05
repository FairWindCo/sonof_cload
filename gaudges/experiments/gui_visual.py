from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from gaudges.analog import Gauge


class GaugeApp(App):
    def build(self):
        from kivy.uix.slider import Slider

        def test(*ars):
            gauge.value = s.value

            print(s.value)

        def test_(*ars):
            gauge_.value = s1.value
            print(s.value)

        box = BoxLayout(orientation='vertical', spacing=10, padding=10)
        gauge = Gauge(value=50, size_gauge=256, size_text=9)
        gauge_ = Gauge(value=50, size_gauge=256, size_text=19)

        box.add_widget(gauge)
        box.add_widget(gauge_)

        s = Slider(min=0, max=100, value=50)
        s.bind(value=test)
        box.add_widget(s)

        s1 = Slider(min=0, max=100, value=50)
        s1.bind(value=test_)
        box.add_widget(s1)

        return box


GaugeApp().run()