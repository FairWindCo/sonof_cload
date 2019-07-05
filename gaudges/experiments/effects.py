from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.effectwidget import EffectWidget, InvertEffect, HorizontalBlurEffect


class TestApp(App):
    def build(self):
        w = EffectWidget()
        w.add_widget(Button(text='Hello!'))
        w.effects = [InvertEffect(), HorizontalBlurEffect(size=2.0)]
        return w


if __name__ == '__main__':
    TestApp().run()

