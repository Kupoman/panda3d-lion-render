import panda3d.core as p3d

from lionrender import GpuBuffer


def test_constructor(gsg):
    count = 5
    buffer = GpuBuffer.make_rgba32f('test', count, gsg)
    texture = buffer.get_texture()

    # Check name
    assert texture.name == 'test'

    # Check data type
    assert texture.get_component_type() == p3d.Texture.T_float
    assert texture.get_format() == p3d.Texture.F_rgba32

    # Check size
    assert texture.get_x_size() == count
    assert texture.get_y_size() == 1
    assert texture.get_z_size() == 1


def test_extract_data(gsg, engine):
    buffer = GpuBuffer.make_rgba32f('test', 1, gsg)
    view = buffer.extract_data(engine)
    assert list(view) == [0, 0, 0, 0]


def test_buffer_id(gsg, engine):
    buffer0 = GpuBuffer.make_rgba32f('zero', 1, gsg)
    buffer1 = GpuBuffer.make_rgba32f('one', 1, gsg)
    engine.render_frame()

    assert abs(buffer0.get_buffer_id() - buffer1.get_buffer_id()) == 1
