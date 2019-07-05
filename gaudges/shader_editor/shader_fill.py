from kivy.app import runTouchApp
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.graphics import RenderContext
from kivy.properties import StringProperty


Builder.load_string(r'''
<ShaderWidget>:
    canvas:
        Line:
            width: 2.
            bezier: 
                (self.x, self.y, self.center_x - 140, self.y + 100, 
                self.center_x + 40, self.y - 100, self.right, self.y) 
''')


class ShaderWidget(Factory.Widget):

    fs = StringProperty(None)

    def __init__(self, **kwargs):
        self.canvas = RenderContext(
            use_parent_projection=True,
            use_parent_modelview=True,
            use_parent_frag_modelview=True)
        super().__init__(**kwargs)

    def on_fs(self, __, value):
        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('Failed to compile GLSL.')

    def on_size(self, __, size):
        self.canvas['resolution'] = [float(size[0]), float(size[1]), ]


GLSL_CODE = '''
uniform vec2 resolution;
void main(void)
{
    float sx = gl_FragCoord.x / resolution.x;
    float sy = gl_FragCoord.y / resolution.y;
    gl_FragColor = vec4( 1.0, sx, sy, 1.0);
}
'''
root = ShaderWidget(fs=GLSL_CODE)
runTouchApp(root)