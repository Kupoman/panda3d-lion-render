import panda3d.core as p3d

from .renderpass import Pass


class ScenePass(Pass):
    def __init__(
            self,
            name='scene-pass',
            **pass_options
    ):
        options = {
            'camera': base.camera,
            'scene': base.render,
        }
        options.update(pass_options)
        super().__init__(name, **options)


class DepthScenePass(ScenePass):
    def __init__(
            self,
            name='depth-scene-pass',
            depth_bits=32,
            **pass_options
    ):
        fb_props = p3d.FrameBufferProperties()
        fb_props.set_depth_bits(depth_bits)
        fb_props.set_rgba_bits(0, 0, 0, 0)

        options = {
            'frame_buffer_properties': fb_props,
        }

        options.update(pass_options)
        super().__init__(name, **options)
