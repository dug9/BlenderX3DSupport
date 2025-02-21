# SPDX-License-Identifier: Apache-2.0
# Copyright 2018-2021 The glTF-Blender-IO authors.

import bpy
from ..com.gltf2_blender_extras import set_extras
from io_scene_gltf2.io.imp.gltf2_io_user_extensions import import_user_extensions


class BlenderCamera():
    """Blender Camera."""
    def __new__(cls, *args, **kwargs):
        raise RuntimeError("%s should not be instantiated" % cls)

    @staticmethod
    def create(gltf, vnode, camera_id):
        """Camera creation."""
        pycamera = gltf.data.cameras[camera_id]

        import_user_extensions('gather_import_camera_before_hook', gltf, vnode, pycamera)

        if not pycamera.name:
            pycamera.name = "Camera"

        cam = bpy.data.cameras.new(pycamera.name)
        set_extras(cam, pycamera.extras)

        # Blender create a perspective camera by default
        if pycamera.type == "orthographic":
            cam.type = "ORTHO"

            cam.ortho_scale = max(pycamera.orthographic.xmag, pycamera.orthographic.ymag) * 2

            cam.clip_start = pycamera.orthographic.znear
            cam.clip_end = pycamera.orthographic.zfar

        else:
            cam.angle_y = pycamera.perspective.yfov
            cam.lens_unit = "FOV"
            cam.sensor_fit = "VERTICAL"

            # TODO: fov/aspect ratio

            cam.clip_start = pycamera.perspective.znear
            if pycamera.perspective.zfar is not None:
                cam.clip_end = pycamera.perspective.zfar
            else:
                # Infinite projection
                cam.clip_end = 1e12  # some big number

        return cam
