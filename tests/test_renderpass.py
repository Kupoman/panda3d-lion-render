import pytest

import panda3d.core as p3d

import lionrender


def create_window(engine, pipe):
    fbprops = p3d.FrameBufferProperties()
    fbprops.set_rgba_bits(8, 8, 8, 0)
    fbprops.set_depth_bits(24)
    winprops = p3d.WindowProperties.size(1, 1)
    flags = p3d.GraphicsPipe.BF_refuse_window
    return engine.make_output(
        pipe,
        'window',
        0,
        fbprops,
        winprops,
        flags
    )


@pytest.fixture
def default_args():
    pipe = p3d.GraphicsPipeSelection.get_global_ptr().make_default_pipe()
    engine = p3d.GraphicsEngine(pipe)
    window = create_window(engine, pipe)
    return {
        'pipe': pipe,
        'engine': engine,
        'window': window,
    }


@pytest.fixture
def camera():
    return p3d.NodePath(p3d.Camera('camera', p3d.PerspectiveLens()))


@pytest.fixture
def scene():
    return p3d.NodePath(p3d.ModelNode('scene'))


def test_create_buffer(default_args):
    engine = default_args['engine']
    initial_win_count = len(engine.get_windows())
    rpass = lionrender.Pass('test', **default_args)
    engine.render_frame()

    assert len(engine.get_windows()) == initial_win_count + 1
    assert type(rpass.buffer == p3d.GraphicsOutput)


def test_scene(default_args, scene):
    default_args['scene'] = scene
    rpass = lionrender.Pass('test', **default_args)
    display_scene = rpass.display_region.get_camera().get_node(0).get_scene()
    assert display_scene.find('**/scene')


def test_empty_scene(default_args):
    rpass = lionrender.Pass('test', **default_args)
    display_scene = rpass.display_region.get_camera().get_node(0).get_scene()
    quad = display_scene.find('**/+GeomNode')
    assert quad.get_node(0).get_geom(0).get_num_primitives() == 1


def test_camera_sync(default_args, camera):
    default_args['camera'] = camera
    rpass = lionrender.Pass('test', **default_args)
    camera.set_pos(p3d.LVector3(1, 2, 3))
    camera.set_hpr(p3d.LVector3(1, 2, 3))
    default_args['engine'].render_frame()
    default_args['engine'].render_frame()
    default_args['engine'].render_frame()
    default_args['engine'].render_frame()

    rcam = rpass.display_region.get_camera()
    assert rcam.get_pos().compare_to(camera.get_pos()) == 0
    assert rcam.get_hpr().compare_to(camera.get_hpr()) == 0
    assert rcam.get_node(0).get_lens() == camera.get_node(0).get_lens()


def test_camera_sync_indirect(default_args, camera):
    default_args['camera'] = p3d.NodePath(p3d.ModelNode('indirect'))
    camera.reparent_to(default_args['camera'])
    indirect = default_args['camera']

    rpass = lionrender.Pass('test', **default_args)
    camera.set_pos(p3d.LVector3(1, 2, 3))
    camera.set_hpr(p3d.LVector3(1, 2, 3))
    default_args['engine'].render_frame()

    rcam = rpass.display_region.get_camera()
    assert rcam.get_pos().compare_to(indirect.get_pos()) == 0
    assert rcam.get_hpr().compare_to(indirect.get_hpr()) == 0
    assert rcam.get_node(0).get_lens() == camera.get_node(0).get_lens()


def test_control_clear_color(default_args):
    default_args['clear_color'] = p3d.LColor(0.5, 1.0, 0.0, 1.0)
    rpass = lionrender.Pass('test', **default_args)
    assert rpass.buffer.get_clear_color() == default_args['clear_color']


def test_apply_shader(default_args):
    vertex = '#version 120\nvoid main() { gl_Position = vec4(0.0); }'
    fragment = '#version 120\nvoid main() { gl_FragColor = vec4(0.0); }'
    default_args['shader'] = p3d.Shader.make(p3d.Shader.SL_GLSL, vertex, fragment, '', '', '')

    rpass = lionrender.Pass('test', **default_args)
    assert rpass.node_path.get_shader()


def test_multiple_targets(default_args):
    prepared = default_args['window'].get_gsg().get_prepared_objects()
    initial_texture_count = prepared.get_num_prepared_textures()

    default_args['frame_buffer_properties'] = p3d.FrameBufferProperties()
    default_args['frame_buffer_properties'].set_rgb_color(True)
    default_args['frame_buffer_properties'].set_aux_rgba(1)
    rpass = lionrender.Pass('test', **default_args)
    default_args['engine'].render_frame()

    assert len(rpass.outputs) == 2
    assert prepared.get_num_prepared_textures() == initial_texture_count + 2

def test_share_depth(default_args):
    pass_one = lionrender.Pass('test', **default_args)
    default_args['share_depth_with'] = pass_one
    pass_two = lionrender.Pass('test', **default_args)
    assert not pass_two.buffer.get_clear_depth_active()
