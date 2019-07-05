import kivy

kivy.require('1.9.0')
from kivy.uix.effectwidget import EffectBase
from kivy.properties import (StringProperty, ObjectProperty, ListProperty,
                             NumericProperty, DictProperty)

effect_bloom_h = ''' 
float luminance(vec3 color) 
{ 
    return color.x*0.299 + color.y * 0.587 + color.z * 0.114; 
} 


vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords) 
{ 
    vec4 sum = vec4(0); 
    vec4 result = vec4(0); 
    vec4 temp = vec4(0); 
    int j; 
    int i; 

    float dt = (5.0 / 4.0) * 1.0 / resolution.x; 
    for( i= -4 ;i < 4; i++) 
    { 
        for (j = -3; j < 3; j++) 
        { 
            temp = texture2D(texture, tex_coords + vec2(j, i)*dt); 
            sum += temp * 0.25; 
        } 
    } 
    if (luminance(texture2D(texture, tex_coords).xyz) < 0.3) 
    { 
        result = sum*sum*0.012 + color*0.9; 
    } 
    else 
    { 
        if (luminance(texture2D(texture, tex_coords).xyz) < 0.5) 
        { 
            result = sum*sum*0.009 + color*0.9; 
        } 
        else 
        { 
            result = sum*sum*0.0075 + color*0.9; 
        } 
    } 
    return result; 
} 
'''


class BloomEffect(EffectBase):
    # size = NumericProperty(4.0)
    '''The bloom radius in pixels.
    size is a :class:`~kivy.properties.NumericProperty` and defaults to
    4.0.
    '''

    def __init__(self, *args, **kwargs):
        super(BloomEffect, self).__init__(*args, **kwargs)
        self.do_glsl()

    def on_size(self, *args):
        self.do_glsl()

    def do_glsl(self):
        self.glsl = effect_bloom_h
