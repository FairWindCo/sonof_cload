from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Mesh
from functools import partial
from math import cos, sin, pi


class MeshTestApp(App):

    def change_mode(self, mode, *largs):
        self.mesh.mode = mode

    def build_mesh(self):
        #switch between original and alteration code
#        switch = False   #original
        switch = True   #alteration

        """ returns a Mesh of a rough circle. """
        vertices = []
        indices = []
        step = 10
        istep = (pi * 2) / float(step)

        # my alteration
        # mask for mapping list of vertices
        # where is problem with format?
        vertex_format = [(b'v_pos', 2,"float")]

        for i in range(step):
            x = 300 + cos(istep * i) * 100
            y = 300 + sin(istep * i) * 100

            if switch == False:
                # originall code
                vertices.extend([x, y, 0, 0])
            else:
                # my alteration
                vertices.extend([x, y])

            indices.append(i)

        if switch == False:
            # originall code
            return Mesh(vertices=vertices, indices=indices)
        else:
            # my alteration
            return Mesh(vertices=vertices, indices=indices, fmt = vertex_format )

    def build(self):
        wid = Widget()
        with wid.canvas:
            self.mesh = self.build_mesh()

        layout = BoxLayout(size_hint=(1, None), height=50)
        for mode in ('points', 'line_strip', 'line_loop', 'lines',
                'triangle_strip', 'triangle_fan'):
            button = Button(text=mode)
            button.bind(on_release=partial(self.change_mode, mode))
            layout.add_widget(button)

        root = BoxLayout(orientation='vertical')
        root.add_widget(wid)
        root.add_widget(layout)

        return root


if __name__ == '__main__':
    MeshTestApp().run()