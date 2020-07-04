import os

import panda3d.core as p3d

from .renderpass import Pass


dir_path = os.path.dirname(os.path.realpath(__file__))
def get_shader_path(file_name):
    return os.path.join(dir_path, 'shaders', file_name)


class FilterPass(Pass):
    def __init__(self, name, frag_path, **pass_options):
        shader = p3d.Shader.load(
            p3d.Shader.SL_GLSL,
            get_shader_path('fsq.vert'),
            frag_path
        )
        filter_options = {
            'shader': shader
        }
        filter_options.update(pass_options)
        super().__init__(name, **filter_options)


class FxaaFilterPass(FilterPass):
    def __init__(
            self,
            name,
            subpixel_aliasing=0.75,
            edge_threshold=0.166,
            edge_threshold_min=0.0,
            **pass_options
    ):
        super().__init__(name, get_shader_path('fxaa.frag'), **pass_options)

        self.node_path.set_shader_input('subpix', subpixel_aliasing)
        self.node_path.set_shader_input('edgeThreshold', edge_threshold)
        self.node_path.set_shader_input('edgeThresholdMin', edge_threshold_min)
