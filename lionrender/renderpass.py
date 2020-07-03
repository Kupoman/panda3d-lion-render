import panda3d.core as p3d


class Pass:
    def __init__(
            self,
            name,
            pipe=None,
            engine=None,
            window=None,
            camera=None,
            scene=None,
            shader=None,
            frame_buffer_properties=None,
            clear_color=p3d.LColor(0.41, 0.41, 0.41, 0.0),
            share_depth_with=None,
    ):
        self.name = name
        self._pipe = pipe if pipe else base.pipe
        self._engine = engine if engine else base.graphics_engine
        self._window = window if window else base.win
        self.node_path = p3d.NodePath(p3d.ModelNode(f'{self.name}_node_path'))

        if scene:
            scene.instance_to(self.node_path)
        else:
            quad = self._make_fullscreen_quad()
            quad.reparent_to(self.node_path)

        if shader:
            self.node_path.set_shader(shader)

        if not frame_buffer_properties:
            frame_buffer_properties = self._make_default_buffer_props()
        output_count = self._count_outputs(frame_buffer_properties)

        self._camera = self._make_camera(camera)
        self.buffer = self._make_buffer(frame_buffer_properties)
        if share_depth_with:
            success = self.buffer.share_depth_buffer(share_depth_with.buffer)
            if success:
                self.buffer.set_clear_depth_active(False)
                self.node_path.set_attrib(p3d.DepthTestAttrib.make(p3d.RenderAttrib.MLessEqual))
            else:
                raise Exception('Unable to share depth buffer')

        self.outputs = self._make_outputs(output_count)
        self.output = self.outputs[0] if self.outputs else None

        self.display_region = self.buffer.make_display_region(0, 1, 0, 1)
        if self._camera:
            self.display_region.set_camera(self._camera)
        self.buffer.set_clear_color(clear_color)

    def output_to(self, render2d, index=0):
        card = self.buffer.getTextureCard()
        card.setTexture(self.outputs[index])
        card.reparentTo(render2d)

    def _count_outputs(self, fb_props):
        count = 0
        if fb_props.get_rgb_color():
            count += 1
        count += fb_props.get_aux_rgba()
        return count

    def _make_outputs(self, count):
        outputs = [p3d.Texture(f'{self.name}_output_{i}') for i in range(count)]
        for i, output in enumerate(outputs):
            attach_point = p3d.GraphicsOutput.RTP_color
            if i > 0:
                attach_point = getattr(p3d.GraphicsOutput, f'RTP_aux_rgba_{i - 1}')

            self.buffer.add_render_texture(
                output,
                p3d.GraphicsOutput.RTM_bind_or_copy,
                attach_point
            )
        return outputs

    def _make_camera(self, source_cam):
        cam = p3d.Camera(f'{self.name}_camera')
        cam_nodepath = self.node_path.attach_new_node(cam)
        cam.set_scene(self.node_path)

        if source_cam:
            def update(callback_data):
                try:
                    lens = source_cam.get_node(0).get_lens()
                except AttributeError:
                    lens = source_cam.find('**/+Camera').get_node(0).get_lens()
                cam.set_lens(lens)
                cam_nodepath.set_pos(source_cam.get_pos(self.node_path))
                cam_nodepath.set_hpr(source_cam.get_hpr(self.node_path))
                callback_data.upcall()
            callback = p3d.CallbackNode(f'{self.name}_update_camera')
            callback.set_cull_callback(update)
            cam_nodepath.attach_new_node(callback)

        return cam_nodepath

    def _make_default_buffer_props(self):
        fb_props = p3d.FrameBufferProperties()
        fb_props.set_rgb_color(True)
        fb_props.set_rgba_bits(8, 8, 8, 0)
        fb_props.set_depth_bits(24)
        return fb_props

    def _make_buffer(self, fb_props):
        return self._engine.make_output(
            self._pipe,
            self.name,
            0,
            fb_props,
            p3d.WindowProperties(),
            p3d.GraphicsPipe.BF_refuse_window | p3d.GraphicsPipe.BF_size_track_host,
            self._window.get_gsg(),
            self._window
        )

    def _make_fullscreen_quad(self):
        tris = p3d.GeomTristrips(p3d.GeomEnums.UH_static)
        tris.add_next_vertices(4)
        vdata = p3d.GeomVertexData(
            'abc',
            p3d.GeomVertexFormat.get_empty(),
            p3d.GeomEnums.UH_static
        )

        geom = p3d.Geom(vdata)
        geom.add_primitive(tris)
        geom.set_bounds(p3d.OmniBoundingVolume())

        node = p3d.GeomNode(f'{self.name}_fullscreen_quad')
        node.add_geom(geom)

        return p3d.NodePath(node)
