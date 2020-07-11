from OpenGL import GL as gl

import panda3d.core as p3d


class TransformFeedbackBuffer:
    def __init__(self, name, buffer, stride=4):
        self.name = name
        self.xfb_active = False
        self.buffer = buffer
        self.primitive_count = 0
        self.stride = stride

    def _update_mesh_buffer_size(self, primitive_count):
        if primitive_count <= self.primitive_count:
            return
        self.primitive_count = primitive_count
        self.buffer.resize(self.primitive_count * 3 * self.stride)


    def _iterate_geometry(self, node_path):
        geom_node_paths = list(node_path.find_all_matches('**/+GeomNode'))

        primitive_count = 0
        for nodepath in geom_node_paths:
            for node in nodepath.get_nodes():
                if isinstance(node, p3d.GeomNode):
                    for geom in node.get_geoms():
                        for primitive in geom.get_primitives():
                            primitive_count += primitive.get_num_faces()

        self._update_mesh_buffer_size(primitive_count)

    def attach(self, node_path):
        def attach_new_callback(prop, nodepath, name, callback):
            cb_node = p3d.CallbackNode(name)
            setattr(cb_node, prop, p3d.PythonCallbackObject(callback))
            cb_node_path = nodepath.attach_new_node(cb_node)
            return cb_node_path

        def attach_new_cull_callback(nodepath, name, callback):
            return attach_new_callback('cull_callback', nodepath, name, callback)

        def attach_new_draw_callback(nodepath, name, callback):
            return attach_new_callback('draw_callback', nodepath, name, callback)

        def update(callback_data):
            self._iterate_geometry(node_path)
            callback_data.upcall()

        def begin(callback_data):
            buffer_id = self.buffer.get_buffer_id()
            if buffer_id and not self.xfb_active:
                gl.glEnable(gl.GL_RASTERIZER_DISCARD)
                gl.glBindBufferBase(gl.GL_TRANSFORM_FEEDBACK_BUFFER, 0, buffer_id)
                gl.glBeginTransformFeedback(gl.GL_TRIANGLES)
                self.xfb_active = True
            callback_data.upcall()

        def end(callback_data):
            if self.xfb_active:
                gl.glEndTransformFeedback()
                gl.glBindBufferBase(gl.GL_TRANSFORM_FEEDBACK_BUFFER, 0, 0)
                gl.glDisable(gl.GL_RASTERIZER_DISCARD)
                self.xfb_active = False
            callback_data.upcall()

        bin_manager = p3d.CullBinManager.get_global_ptr()
        bin_manager.add_bin('xfb_begin', p3d.CullBinManager.BT_fixed, 5)
        bin_manager.add_bin('xfb_end', p3d.CullBinManager.BT_fixed, 55)

        path = attach_new_cull_callback(
            node_path,
            self.name + '_xfb_resize',
            update
        )
        path.set_bin('xfb_begin', 10)

        path = attach_new_draw_callback(
            node_path,
            self.name + '_xfb_begin',
            begin
        )
        path.set_bin('xfb_begin', 11)

        path = attach_new_draw_callback(
            node_path,
            self.name + '_xfb_end',
            end
        )
        path.set_bin('xfb_end', 10)

    def make_node(self):
        def draw_callback(callback_data):
            buffer_id = self.buffer.get_buffer_id()
            gl.glBindBufferBase(gl.GL_TRANSFORM_FEEDBACK_BUFFER, 0, buffer_id)
            gl.glDrawTransformFeedback(gl.GL_TRIANGLES, 0)
            callback_data.upcall()

        cb_node = p3d.CallbackNode('XFB Draw Callback')
        cb_node.draw_callback = p3d.PythonCallbackObject(draw_callback)
        return cb_node
