import panda3d.core as p3d

import lionrender


def test_create_buffer(graphics_context):
    engine = graphics_context['engine']
    initial_win_count = len(engine.get_windows())
    rpass = lionrender.Pass('test', **graphics_context)
    engine.render_frame()

    assert len(engine.get_windows()) == initial_win_count + 1
    assert type(rpass.buffer == p3d.GraphicsOutput)


def test_scene(graphics_context, scene):
    graphics_context['scene'] = scene
    rpass = lionrender.Pass('test', **graphics_context)
    display_scene = rpass.display_region.get_camera().get_node(0).get_scene()
    assert display_scene.find('**/scene')


def test_empty_scene(graphics_context):
    rpass = lionrender.Pass('test', **graphics_context)
    display_scene = rpass.display_region.get_camera().get_node(0).get_scene()
    quad = display_scene.find('**/+GeomNode')
    assert quad.get_node(0).get_geom(0).get_num_primitives() == 1


def test_camera_sync(graphics_context, camera):
    graphics_context['camera'] = camera
    rpass = lionrender.Pass('test', **graphics_context)
    camera.set_pos(p3d.LVector3(1, 2, 3))
    camera.set_hpr(p3d.LVector3(1, 2, 3))
    graphics_context['engine'].render_frame()
    graphics_context['engine'].render_frame()
    graphics_context['engine'].render_frame()
    graphics_context['engine'].render_frame()

    rcam = rpass.display_region.get_camera()
    assert rcam.get_pos().compare_to(camera.get_pos()) == 0
    assert rcam.get_hpr().compare_to(camera.get_hpr()) == 0
    assert rcam.get_node(0).get_lens() == camera.get_node(0).get_lens()


def test_camera_sync_indirect(graphics_context, camera):
    graphics_context['camera'] = p3d.NodePath(p3d.ModelNode('indirect'))
    camera.reparent_to(graphics_context['camera'])
    indirect = graphics_context['camera']

    rpass = lionrender.Pass('test', **graphics_context)
    camera.set_pos(p3d.LVector3(1, 2, 3))
    camera.set_hpr(p3d.LVector3(1, 2, 3))
    graphics_context['engine'].render_frame()

    rcam = rpass.display_region.get_camera()
    assert rcam.get_pos().compare_to(indirect.get_pos()) == 0
    assert rcam.get_hpr().compare_to(indirect.get_hpr()) == 0
    assert rcam.get_node(0).get_lens() == camera.get_node(0).get_lens()


def test_control_clear_color(graphics_context):
    graphics_context['clear_color'] = p3d.LColor(0.5, 1.0, 0.0, 1.0)
    rpass = lionrender.Pass('test', **graphics_context)
    assert rpass.buffer.get_clear_color() == graphics_context['clear_color']


def test_apply_shader(graphics_context):
    vertex = '#version 120\nvoid main() { gl_Position = vec4(0.0); }'
    fragment = '#version 120\nvoid main() { gl_FragColor = vec4(0.0); }'
    graphics_context['shader'] = p3d.Shader.make(p3d.Shader.SL_GLSL, vertex, fragment, '', '', '')

    rpass = lionrender.Pass('test', **graphics_context)
    assert rpass.node_path.get_shader()


def test_multiple_targets(graphics_context):
    prepared = graphics_context['window'].get_gsg().get_prepared_objects()
    initial_texture_count = prepared.get_num_prepared_textures()

    graphics_context['frame_buffer_properties'] = p3d.FrameBufferProperties()
    graphics_context['frame_buffer_properties'].set_rgb_color(True)
    graphics_context['frame_buffer_properties'].set_aux_rgba(1)
    rpass = lionrender.Pass('test', **graphics_context)
    graphics_context['engine'].render_frame()

    assert len(rpass.outputs) == 2
    assert prepared.get_num_prepared_textures() == initial_texture_count + 2

def test_share_depth(graphics_context):
    pass_one = lionrender.Pass('test', **graphics_context)
    graphics_context['share_depth_with'] = pass_one
    pass_two = lionrender.Pass('test', **graphics_context)
    assert not pass_two.buffer.get_clear_depth_active()
