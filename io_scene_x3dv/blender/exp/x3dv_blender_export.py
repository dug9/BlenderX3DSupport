# SPDX-License-Identifier: Apache-2.0)
# Copyright 2023 The x3dv-Blender-IO authors.
# Contributors: bart:neeneenee*de, http://www.neeneenee.de/vrml, Campbell Barton
"""
This script exports to X3D format.

Usage:
Run this script from "File->Export" menu.  A pop-up will ask whether you
want to export only selected or all relevant objects.

Known issues:
    Doesn't handle multiple materials (don't use material indices);<br>
    Doesn't handle multiple UV textures on a single mesh (create a mesh for each texture);<br>
    Can't get the texture array associated with material * not the UV ones;
"""

import time

import bpy
import sys
import traceback
from io_scene_x3dv.io.com.x3dv_io_debug import print_console, print_newline
from io_scene_x3dv.blender.com.x3d import *
import math
import os
import mathutils
import random

from .export_bvh import write_animation
from .export_interpolators import write_interpolators

from bpy_extras.io_utils import create_derived_objects

from .RoundArray import round_array, round_array_no_unit_scale
from .GetSceneScale import getscenescale

from .swap_USEbeforeDEF import swap_USEbeforeDEF, USEdict, DEFdict, USEbeforeDEFdict

JointsSegments = {
"humanoid_root" : "sacrum",
"sacroiliac" : "pelvis",
"Sacroiliac" : "pelvis",
"l_hip" : "l_thigh",
"l_knee" : "l_calf",
"l_talocrural" : "l_talus",
"l_talocalcaneonavicular" : "l_navicular",
"l_cuneonavicular_1" : "l_cuneiform_1",
"l_tarsometatarsal_1" : "l_metatarsal_1",
"l_metatarsophalangeal_1" : "l_tarsal_proximal_phalanx_1",
"l_tarsal_interphalangeal_1" : "l_tarsal_distal_phalanx_1",
"l_cuneonavicular_2" : "l_cuneiform_2",
"l_tarsometatarsal_2" : "l_metatarsal_2",
"l_metatarsophalangeal_2" : "l_tarsal_proximal_phalanx_2",
"l_tarsal_proximal_interphalangeal_2" : "l_tarsal_middle_phalanx_2",
"l_tarsal_distal_interphalangeal_2" : "l_tarsal_distal_phalanx_2",
"l_cuneonavicular_3" : "l_cuneiform_3",
"l_tarsometatarsal_3" : "l_metatarsal_3",
"l_metatarsophalangeal_3" : "l_tarsal_proximal_phalanx_3",
"l_tarsal_proximal_interphalangeal_3" : "l_tarsal_middle_phalanx_3",
"l_tarsal_distal_interphalangeal_3" : "l_tarsal_distal_phalanx_3",
"l_calcaneuscuboid" : "l_calcaneus",
"l_transversetarsal" : "l_cuboid",
"l_tarsometatarsal_4" : "l_metatarsal_4",
"l_metatarsophalangeal_4" : "l_tarsal_proximal_phalanx_4",
"l_tarsal_proximal_interphalangeal_4" : "l_tarsal_middle_phalanx_4",
"l_tarsal_distal_interphalangeal_4" : "l_tarsal_distal_phalanx_4",
"l_tarsometatarsal_5" : "l_metatarsal_5",
"l_metatarsophalangeal_5" : "l_tarsal_proximal_phalanx_5",
"l_tarsal_proximal_interphalangeal_5" : "l_tarsal_middle_phalanx_5",
"l_tarsal_distal_interphalangeal_5" : "l_tarsal_distal_phalanx_5",
"r_hip" : "r_thigh",
"r_knee" : "r_calf",
"r_talocrural" : "r_talus",
"r_talocalcaneonavicular" : "r_navicular",
"r_cuneonavicular_1" : "r_cuneiform_1",
"r_tarsometatarsal_1" : "r_metatarsal_1",
"r_metatarsophalangeal_1" : "r_tarsal_proximal_phalanx_1",
"r_tarsal_interphalangeal_1" : "r_tarsal_distal_phalanx_1",
"r_cuneonavicular_2" : "r_cuneiform_2",
"r_tarsometatarsal_2" : "r_metatarsal_2",
"r_metatarsophalangeal_2" : "r_tarsal_proximal_phalanx_2",
"r_tarsal_proximal_interphalangeal_2" : "r_tarsal_middle_phalanx_2",
"r_tarsal_distal_interphalangeal_2" : "r_tarsal_distal_phalanx_2",
"r_cuneonavicular_3" : "r_cuneiform_3",
"r_tarsometatarsal_3" : "r_metatarsal_3",
"r_metatarsophalangeal_3" : "r_tarsal_proximal_phalanx_3",
"r_tarsal_proximal_interphalangeal_3" : "r_tarsal_middle_phalanx_3",
"r_tarsal_distal_interphalangeal_3" : "r_tarsal_distal_phalanx_3",
"r_calcaneuscuboid" : "r_calcaneus",
"r_transversetarsal" : "r_cuboid",
"r_tarsometatarsal_4" : "r_metatarsal_4",
"r_metatarsophalangeal_4" : "r_tarsal_proximal_phalanx_4",
"r_tarsal_proximal_interphalangeal_4" : "r_tarsal_middle_phalanx_4",
"r_tarsal_distal_interphalangeal_4" : "r_tarsal_distal_phalanx_4",
"r_tarsometatarsal_5" : "r_metatarsal_5",
"r_metatarsophalangeal_5" : "r_tarsal_proximal_phalanx_5",
"r_tarsal_proximal_interphalangeal_5" : "r_tarsal_middle_phalanx_5",
"r_tarsal_distal_interphalangeal_5" : "r_tarsal_distal_phalanx_5",
"vl5" : "l5",
"vl4" : "l4",
"vl3" : "l3",
"vl2" : "l2",
"vl1" : "l1",
"vt12" : "t12",
"vt11" : "t11",
"vt10" : "t10",
"vt9" : "t9",
"vt8" : "t8",
"vt7" : "t7",
"vt6" : "t6",
"vt5" : "t5",
"vt4" : "t4",
"vt3" : "t3",
"vt2" : "t2",
"vt1" : "t1",
"vc7" : "c7",
"vc6" : "c6",
"vc5" : "c5",
"vc4" : "c4",
"vc3" : "c3",
"vc2" : "c2",
"vc1" : "c1",
"skullbase" : "skull",
"l_eyelid_joint" : "l_eyelid",
"r_eyelid_joint" : "r_eyelid",
"l_eyeball_joint" : "l_eyeball",
"r_eyeball_joint" : "r_eyeball",
"l_eyebrow_joint" : "l_eyebrow",
"r_eyebrow_joint" : "r_eyebrow",
"tongue_joint" : "tongue",
"temporomandibular" : "jaw",
"l_sternoclavicular" : "l_clavicle",
"l_acromioclavicular" : "l_scapula",
"l_shoulder" : "l_upperarm",
"l_elbow" : "l_forearm",
"l_radiocarpal" : "l_carpal",
"l_midcarpal_1" : "l_trapezium",
"l_carpometacarpal_1" : "l_metacarpal_1",
"l_metacarpophalangeal_1" : "l_carpal_proximal_phalanx_1",
"l_carpal_interphalangeal_1" : "l_carpal_distal_phalanx_1",
"l_midcarpal_2" : "l_trapezoid",
"l_carpometacarpal_2" : "l_metacarpal_2",
"l_metacarpophalangeal_2" : "l_carpal_proximal_phalanx_2",
"l_carpal_proximal_interphalangeal_2" : "l_carpal_middle_phalanx_2",
"l_carpal_distal_interphalangeal_2" : "l_carpal_distal_phalanx_2",
"l_midcarpal_3" : "l_capitate",
"l_carpometacarpal_3" : "l_metacarpal_3",
"l_metacarpophalangeal_3" : "l_carpal_proximal_phalanx_3",
"l_carpal_proximal_interphalangeal_3" : "l_carpal_middle_phalanx_3",
"l_carpal_distal_interphalangeal_3" : "l_carpal_distal_phalanx_3",
"l_midcarpal_4_5" : "l_hamate",
"l_carpometacarpal_4" : "l_metacarpal_4",
"l_metacarpophalangeal_4" : "l_carpal_proximal_phalanx_4",
"l_carpal_proximal_interphalangeal_4" : "l_carpal_middle_phalanx_4",
"l_carpal_distal_interphalangeal_4" : "l_carpal_distal_phalanx_4",
"l_carpometacarpal_5" : "l_metacarpal_5",
"l_metacarpophalangeal_5" : "l_carpal_proximal_phalanx_5",
"l_carpal_proximal_interphalangeal_5" : "l_carpal_middle_phalanx_5",
"l_carpal_distal_interphalangeal_5" : "l_carpal_distal_phalanx_5",
"r_sternoclavicular" : "r_clavicle",
"r_acromioclavicular" : "r_scapula",
"r_shoulder" : "r_upperarm",
"r_elbow" : "r_forearm",
"r_radiocarpal" : "r_carpal",
"r_midcarpal_1" : "r_trapezium",
"r_carpometacarpal_1" : "r_metacarpal_1",
"r_metacarpophalangeal_1" : "r_carpal_proximal_phalanx_1",
"r_carpal_interphalangeal_1" : "r_carpal_distal_phalanx_1",
"r_midcarpal_2" : "r_trapezoid",
"r_carpometacarpal_2" : "r_metacarpal_2",
"r_metacarpophalangeal_2" : "r_carpal_proximal_phalanx_2",
"r_carpal_proximal_interphalangeal_2" : "r_carpal_middle_phalanx_2",
"r_carpal_distal_interphalangeal_2" : "r_carpal_distal_phalanx_2",
"r_midcarpal_3" : "r_capitate",
"r_carpometacarpal_3" : "r_metacarpal_3",
"r_metacarpophalangeal_3" : "r_carpal_proximal_phalanx_3",
"r_carpal_proximal_interphalangeal_3" : "r_carpal_middle_phalanx_3",
"r_carpal_distal_interphalangeal_3" : "r_carpal_distal_phalanx_3",
"r_midcarpal_4_5" : "r_hamate",
"r_carpometacarpal_4" : "r_metacarpal_4",
"r_metacarpophalangeal_4" : "r_carpal_proximal_phalanx_4",
"r_carpal_proximal_interphalangeal_4" : "r_carpal_middle_phalanx_4",
"r_carpal_distal_interphalangeal_4" : "r_carpal_distal_phalanx_4",
"r_carpometacarpal_5" : "r_metacarpal_5",
"r_metacarpophalangeal_5" : "r_carpal_proximal_phalanx_5",
"r_carpal_proximal_interphalangeal_5" : "r_carpal_middle_phalanx_5",
"r_carpal_distal_interphalangeal_5" : "r_carpal_distal_phalanx_5",
}

# h3d defines
H3D_TOP_LEVEL = 'TOP_LEVEL_TI'
H3D_CAMERA_FOLLOW = 'CAMERA_FOLLOW_TRANSFORM'
H3D_VIEW_MATRIX = 'view_matrix'

HANIM_DEF_PREFIX = 'hanim_'

def clamp_color(col):
    return tuple([max(min(c, 1.0), 0.0) for c in col])


def matrix_direction_neg_z(matrix):
    return (matrix.to_3x3() @ mathutils.Vector((0.0, 0.0, -1.0))).normalized()[:]


def prefix_quoted_str(value, prefix):
    return value[0] + prefix + value[1:]


def suffix_quoted_str(value, suffix):
    return value[:-1] + suffix + value[-1:]

def prefix_str(value, prefix):
    return prefix + value


def suffix_str(value, suffix):
    return value + suffix


def bool_as_str(value):
    return ('false', 'true')[bool(value)]


def clean_def(txt):
    # see report [#28256]
    if not txt:
        txt = "None"
    # no digit start
    if txt[0] in "1234567890+-":
        txt = "_" + txt
    return txt.translate({
        # control characters 0x0-0x1f
        # 0x00: "_",
        0x01: "_",
        0x02: "_",
        0x03: "_",
        0x04: "_",
        0x05: "_",
        0x06: "_",
        0x07: "_",
        0x08: "_",
        0x09: "_",
        0x0a: "_",
        0x0b: "_",
        0x0c: "_",
        0x0d: "_",
        0x0e: "_",
        0x0f: "_",
        0x10: "_",
        0x11: "_",
        0x12: "_",
        0x13: "_",
        0x14: "_",
        0x15: "_",
        0x16: "_",
        0x17: "_",
        0x18: "_",
        0x19: "_",
        0x1a: "_",
        0x1b: "_",
        0x1c: "_",
        0x1d: "_",
        0x1e: "_",
        0x1f: "_",

        0x7f: "_",  # 127

        0x20: "_",  # space
        0x22: "_",  # "
        0x27: "_",  # '
        0x23: "_",  # #
        0x2c: "_",  # ,
        0x2e: "_",  # .
        0x5b: "_",  # [
        0x5d: "_",  # ]
        0x5c: "_",  # \
        0x7b: "_",  # {
        0x7d: "_",  # }
        })


def build_hierarchy(objects):
    """ returns parent child relationships, skipping
    """
    objects_set = set(objects)
    par_lookup = {}

    def test_parent(parent):
        while (parent is not None) and (parent not in objects_set):
            parent = parent.parent
        return parent

    for obj in objects:
        par_lookup.setdefault(test_parent(obj.parent), []).append((obj, []))

    for parent, children in par_lookup.items():
        for obj, subchildren in children:
            subchildren[:] = par_lookup.get(obj, [])

    return par_lookup.get(None, [])


""" 
# -----------------------------------------------------------------------------
# H3D Functions
# -----------------------------------------------------------------------------

def h3d_shader_glsl_frag_patch(filepath, scene, global_vars, frag_uniform_var_map):
    h3d_file = open(filepath, 'r', encoding='utf-8')
    lines = []

    last_transform = None

    for l in h3d_file:
        if l.startswith("void main(void)"):
            lines.append("\n")
            lines.append("// h3d custom vars begin\n")
            for v in global_vars:
                lines.append("%s\n" % v)
            lines.append("// h3d custom vars end\n")
            lines.append("\n")
        elif l.lstrip().startswith("light_visibility_other("):
            w = l.split(', ')
            last_transform = w[1] + "_transform"  # XXX - HACK!!!
            w[1] = '(view_matrix * %s_transform * vec4(%s.x, %s.y, %s.z, 1.0)).xyz' % (w[1], w[1], w[1], w[1])
            l = ", ".join(w)
        elif l.lstrip().startswith("light_visibility_sun_hemi("):
            w = l.split(', ')
            w[0] = w[0][len("light_visibility_sun_hemi(") + 1:]

            if not h3d_is_object_view(scene, frag_uniform_var_map[w[0]]):
                w[0] = '(mat3(normalize(view_matrix[0].xyz), normalize(view_matrix[1].xyz), normalize(view_matrix[2].xyz)) * -%s)' % w[0]
            else:
                w[0] = ('(mat3(normalize((view_matrix*%s)[0].xyz), normalize((view_matrix*%s)[1].xyz), normalize((view_matrix*%s)[2].xyz)) * -%s)' %
                        (last_transform, last_transform, last_transform, w[0]))

            l = "\tlight_visibility_sun_hemi(" + ", ".join(w)
        elif l.lstrip().startswith("light_visibility_spot_circle("):
            w = l.split(', ')
            w[0] = w[0][len("light_visibility_spot_circle(") + 1:]

            if not h3d_is_object_view(scene, frag_uniform_var_map[w[0]]):
                w[0] = '(mat3(normalize(view_matrix[0].xyz), normalize(view_matrix[1].xyz), normalize(view_matrix[2].xyz)) * -%s)' % w[0]
            else:
                w[0] = ('(mat3(normalize((view_matrix*%s)[0].xyz), normalize((view_matrix*%s)[1].xyz), normalize((view_matrix*%s)[2].xyz)) * %s)' %
                    (last_transform, last_transform, last_transform, w[0]))

            l = "\tlight_visibility_spot_circle(" + ", ".join(w)

        lines.append(l)

    h3d_file.close()

    h3d_file = open(filepath, 'w', encoding='utf-8')
    h3d_file.writelines(lines)
    h3d_file.close()


def h3d_is_object_view(scene, obj):
    camera = scene.camera
    parent = obj.parent
    while parent:
        if parent == camera:
            return True
        parent = parent.parent
    return False
"""

# -----------------------------------------------------------------------------
# Functions for writing output file
# -----------------------------------------------------------------------------
def export(context, x3dv_export_settings):
    """
           file,
           global_matrix,
           depsgraph,
           scene,
           view_layer,
           use_mesh_modifiers=False,
           use_selection=True,
           use_triangulate=False,
           use_normals=False,
           use_hierarchy=True,
           use_h3d=False,
           path_mode='AUTO',
           name_decorations=True,
           round_precision=16
           ):
    """
    export_settings = x3dv_export_settings
    scene = context.scene
    view_layer = context.view_layer
    depsgraph = context.evaluated_depsgraph_get()
    global_matrix = mathutils.Matrix()
    use_h3d = False

    # -------------------------------------------------------------------------
    # Global Setup
    # -------------------------------------------------------------------------
    import bpy_extras
    from bpy_extras.io_utils import unique_name
    from xml.sax.saxutils import quoteattr, escape

    if export_settings['x3dv_name_decorations']:
        # If names are decorated, the uuid map can be split up
        # by type for efficiency of collision testing
        # since objects of different types will always have
        # different decorated names.
        uuid_cache_object = {}    # object
        uuid_cache_light = {}      # 'LA_' + object.name
        uuid_cache_view = {}      # object, different namespace
        uuid_cache_mesh = {}      # mesh
        uuid_cache_material = {}  # material
        uuid_cache_image = {}     # image
        uuid_cache_world = {}     # world
        uuid_defs = {}            # defs
        CA_ = 'CA_'
        OB_ = 'OB_'
        ME_ = 'ME_'
        SH_ = 'SH_'
        IM_ = 'IM_'
        WO_ = 'WO_'
        MA_ = 'MA_'
        LA_ = 'LA_'
        group_ = 'group_'
    else:
        # If names are not decorated, it may be possible for two objects to
        # have the same name, so there has to be a unified dictionary to
        # prevent uuid collisions.
        uuid_cache = {}
        uuid_cache_object = uuid_cache           # object
        uuid_cache_light = uuid_cache             # 'LA_' + object.name
        uuid_cache_view = uuid_cache             # object, different namespace
        uuid_cache_mesh = uuid_cache             # mesh
        uuid_cache_material = uuid_cache         # material
        uuid_cache_image = uuid_cache            # image
        uuid_cache_world = uuid_cache            # world
        uuid_defs = uuid_cache                   # defs
        del uuid_cache
        CA_ = ''
        OB_ = ''
        ME_ = ''
        SH_ = ''
        IM_ = ''
        WO_ = ''
        MA_ = ''
        LA_ = ''
        group_ = ''

    _TRANSFORM = '_TRANSFORM'

    def name_used(DEF):
        if DEF in uuid_defs.keys():
            uuid_defs[DEF] = uuid_defs[DEF] + 1
            return True
        else:
            uuid_defs.update({DEF: 1})
            return False

    def setUSEDEF(prefix, name, node):
        if name is None:
            name = ""
        else:
            node.name = name
        if name_used(prefix+name):
            node.USE = prefix+name
        else:
            node.DEF = prefix+name

    # store files to copy
    copy_set = set()

    # store names of newly created meshes, so we dont overlap
    mesh_name_set = set()

    # fw = file.write
    base_src = export_settings['x3dv_blender_directory']  # os.path.dirname(bpy.data.filepath)
    base_dst = export_settings['x3dv_filedirectory']  # os.path.dirname(file.name)
    # filename_strip = os.path.splitext(os.path.basename(file.name))[0]
    gpu_shader_cache = {}

    #if use_h3d:
    #    import gpu
    #    gpu_shader_dummy_mat = bpy.data.materials.new('X3D_DYMMY_MAT')
    #    gpu_shader_cache[None] = gpu.export_shader(scene, gpu_shader_dummy_mat)
    #    h3d_material_route = []

    # -------------------------------------------------------------------------
    # File Writing Functions
    # -------------------------------------------------------------------------

    def b2xHeader():
        filepath = os.path.basename(export_settings['x3dv_filepath'])
        blender_ver = 'Blender %s' % bpy.app.version_string
        copyright = export_settings['x3dv_copyright']
        hd = head()

    
        hd.children=[
          component(name='HAnim', level=3),
          unit(category='length', conversionFactor=getscenescale(bpy.context.scene), name=scene.unit_settings.length_unit),
          meta(content=filepath,name='filename'),
          meta(content=copyright,name='copyright'),
          meta(content='http://www.web3D.org',name='reference'),
          meta(content=blender_ver,name='generator'),
          meta(content='io_scene_x3dv',name='exporter'),
        ]

        # looks interesting but wrong place and not in X3D specs v.4
        #if use_h3d:
        #    # outputs the view matrix in glModelViewMatrix field
        #    fw('%s<TransformInfo DEF="%s" outputGLMatrices="true" />\n' % (ident, H3D_TOP_LEVEL))

        return hd

    def b2xFooter():

        #if use_h3d:
        #    # global
        #    for route in h3d_material_route:
        #        fw('%s%s\n' % (ident, route))

        return None

    def b2xViewpoint(obj, matrix):
        view_id = unique_name(obj, CA_ + obj.name, uuid_cache_view, clean_func=clean_def, sep="_")
        loc, rot, scale = matrix.decompose()
        rot = rot.to_axis_angle()
        rot = (*rot[0].normalized(), rot[1])

        vp = Viewpoint()
        vp.DEF = view_id
        vp.position = (loc[:])
        vp.orientation = rot
        vp.fieldOfView = obj.data.angle
        return vp

    def b2xFog(world):
        if world:
            mtype = world.mist_settings.falloff
            mparam = world.mist_settings
        else:
            return None
        fog = Fog()
        if mparam.use_mist:
            fog.fogType = 'LINEAR' if (mtype == 'LINEAR') else 'EXPONENTIAL'
            fog.color = clamp_color(world.horizon_color)
            fog.visibilityRange = mparam.depth
            return fog
        else:
            return None

    def b2xNavigationInfo(has_light):
        ni = NavigationInfo()
        ni.headlight = has_light
        ni.visibilityLimit = 0.0
        # default ni.type = ["EXAMINE", "ANY"]
        # default ni.avatarSize = [0.25, 1.6, 0.75]
        return ni

    def b2xTransform(matrix, def_id):

        loc, rot, sca = matrix.decompose()
        rot = rot.to_axis_angle()
        rot = (*rot[0], rot[1])

        trans = Transform()
        if def_id is not None:
            trans.DEF = def_id
        trans.translation = round_array(loc[:])
        trans.scale = round_array_no_unit_scale(sca[:])
        trans.rotation = round_array_no_unit_scale(rot)
        return trans


    def b2xSpotLight(obj, matrix, light, world):
        # note, light_id is not re-used
        light_id = unique_name(obj, LA_ + obj.name, uuid_cache_light, clean_func=clean_def, sep="_")

        if world and 0:
            ambi = world.ambient_color
            amb_intensity = ((ambi[0] + ambi[1] + ambi[2]) / 3.0) / 2.5
            del ambi
        else:
            amb_intensity = 0.0

        # compute cutoff and beamwidth
        lamp = obj.data  # added by John
        intensity = min(lamp.energy / 1.75, 1.0)
        beamWidth = lamp.spot_size * 0.37
        # beamWidth=((lamp.spotSize*math.pi)/180.0)*.37
        cutOffAngle = beamWidth * 1.3

        orientation = matrix_direction_neg_z(matrix)

        location = matrix.to_translation()[:]

        radius = lamp.distance * math.cos(beamWidth)
        lite = SpotLight(DEF=light_id)
        lite.radius = radius
        lite.ambientIntensity = amb_intensity
        lite.intensity = intensity
        lite.color = clamp_color(light.color)
        lite.beamWidth= beamWidth
        lite.cutOffAngle = cutOffAngle
        lite.direction = orientation
        lite.location = location
        
        return lite

    def b2xDirectionalLight(obj, matrix, light, world):
        # note, light_id is not re-used
        light_id = unique_name(obj, LA_ + obj.name, uuid_cache_light, clean_func=clean_def, sep="_")

        if world and 0:
            ambi = world.ambient_color
            # ambi = world.amb
            amb_intensity = ((float(ambi[0] + ambi[1] + ambi[2])) / 3.0) / 2.5
        else:
            ambi = 0
            amb_intensity = 0.07 #was 0, turned it on a bit

        intensity = min(light.energy / 1.75, 1.0)

        orientation = matrix_direction_neg_z(matrix)


        lite = DirectionalLight(DEF=light_id)
        lite.ambientIntensity = amb_intensity
        lite.intensity = intensity
        lite.on = True
        lite.global_ = True #the way we export wrapping in a transform means to get light we need it global
        lite.color = clamp_color(light.color)
        lite.direction = orientation
        return lite

    def b2xPointLight( obj, matrix, light, world):
        # note, light_id is not re-used
        light_id = unique_name(obj, LA_ + obj.name, uuid_cache_light, clean_func=clean_def, sep="_")

        if world and 0:
            ambi = world.ambient_color
            # ambi = world.amb
            amb_intensity = ((float(ambi[0] + ambi[1] + ambi[2])) / 3.0) / 2.5
        else:
            ambi = 0.0
            amb_intensity = 0.0

        intensity = min(light.energy / 1.75, 1.0)
        location = matrix.to_translation()[:]

        lite = PointLight(DEF=light_id)
        lite.radius = light.distance
        lite.ambientIntensity = amb_intensity
        lite.intensity = intensity
        lite.color = clamp_color(light.color)
        lite.location = location
        
        return lite

    def b2xHAnimNode(obj, matrix, name, tag, segment_name=None, skinCoordIndex=None, skinCoordWeight=None, motions=None):

        match tag:
              case     "HAnimJoint":
                  print(f"Exporting joint {tag} {obj.name}")
                  try:
                      #obj_matrix = obj.matrix_local
                      #if obj_matrix is not None:
                      #    loc, rot, sca = obj_matrix.decompose()
                      #    rot = rot.to_axis_angle()
                      #    rot = (*rot[0], rot[1])
                      #center = matrix.to_translation()[:]
                      center = obj.head_local
                      chicenter = obj.tail_local
                  except AttributeError:
                      center = [0, 0, 0]
                      chicenter = [0, 0, 0]
                  # eul = mathutils.Euler((math.radians(90.0), 0.0, 0.0), 'XZY')
                  # eul2 = mathutils.Euler((0.0, 0.0, math.radians(180.0)), 'XZY')

                  vec = mathutils.Vector((center[0], center[1], center[2]))  # in Blender space
                  #vec.rotate(eul)
                  # vec.rotate(eul2)
                  center = round_array(vec)  # in X3D space

                  chivec = mathutils.Vector((chicenter[0], chicenter[1], chicenter[2]))  # in Blender space
                  #chivec.rotate(eul)
                  chicenter = round_array(chivec)  # in X3D space
                  print(f"center {center[:]}")
                  if segment_name is None:
                      node = HAnimJoint(
                         #translation=loc[:],
                         #rotation=rot,
                         #scale=sca[:],
                         center=center[:]
                         )
                      if skinCoordIndex is not None:
                         node.skinCoordIndex = skinCoordIndex
                      if skinCoordWeight is not None:
                         node.skinCoordWeight = round_array_no_unit_scale(skinCoordWeight)
                  else:
                      site = HAnimSite(# translation=loc[:],
                                children=[
                                Transform(
                                    translation=center[:],
                                    children=[
                                    Shape(
                                        USE="SiteShape"
                                        #appearance=Appearance(material=Material(diffuseColor = (0, 0, 1))),
                                        #geometry=Box(size = (0.05, 0.05, 0.05))
                                    )
                                ])
                            ])
                      setUSEDEF(HANIM_DEF_PREFIX, segment_name+"_tip", site)
                      segment = HAnimSegment(children=[
                          TouchSensor(description=f"joint {obj.name} segment {segment_name}"),
                          Transform(translation=center[:],
                              children=[
                                  Shape(
                                      USE="JointShape"
                                  )
                              ]),
                            #Shape(appearance=Appearance(lineProperties=LineProperties(linewidthScaleFactor=5)),
                            #      geometry=LineSet(
                            #        vertexCount=2,
                            #        coord=Coordinate(point=[center[:],chicenter[:]]),
                            #        color=ColorRGBA(USE='SegmentLineColor')
                            #      )),
                            site
                        ])
                      setUSEDEF(HANIM_DEF_PREFIX, segment_name, segment)
                      node = HAnimJoint(
                         #translation=loc[:],
                         #rotation=rot,
                         #scale=sca[:],
                         center=center[:],
                         children=[
                             segment
                         ])
                      if skinCoordIndex is not None:
                         node.skinCoordIndex = skinCoordIndex
                      if skinCoordWeight is not None:
                         node.skinCoordWeight = round_array_no_unit_scale(skinCoordWeight)
                  setUSEDEF(HANIM_DEF_PREFIX, name, node)
                  return node
              case     "HAnimSegment":
                  print(f"Exporting type {tag} {obj.type}")
                  node = HAnimSegment()
                  setUSEDEF(HANIM_DEF_PREFIX, name, node)
                  return node
              case     "HAnimSite":
                  print(f"Exporting type {tag} {obj.type}")
                  node = HAnimSite()
                  setUSEDEF(HANIM_DEF_PREFIX, name, node)
                  return node
              case     "HAnimHumanoid":
                  print(f"Exporting type {tag} {obj.type}")
                  if motions and motions[0] is not None:
                      print(f"{motions}")
                      node = HAnimHumanoid( #motionsEnabled=MFBool([random.choice([True]) for i in range(len(motions))]),
                                           motions=motions)
                      setUSEDEF(HANIM_DEF_PREFIX, name, node)
                  else:
                      node = HAnimHumanoid()
                      setUSEDEF(HANIM_DEF_PREFIX, name, node)
                  return node
              case     "HAnimInterpolators":
                  print(f"Exporting rest interpolators of {tag} {obj.type}")
                  children = []
                  if obj.type == 'ARMATURE':
                      armature = obj
                      bpy.context.view_layer.objects.active = armature
                      bpy.ops.object.mode_set(mode='POSE')
                      children = write_interpolators(obj, name, HANIM_DEF_PREFIX)
                  return children
#              case     "HAnimInterpolatorsOld":
#                  print(f"Exporting interpolators of {tag} {obj.type}")
#                  children = []
#                  if obj.type == 'ARMATURE':
#                      armature = obj
#                      bpy.context.view_layer.objects.active = armature
#                      bpy.ops.object.mode_set(mode='POSE')
#                      print(f"Activated armature {armature} in pose mode")
#                      if armature:
#                            animation_data = armature.animation_data
#                            if animation_data:
#                                print(f"Exporting animation data")
#                                action = animation_data.action
#                                if action:
#                                    numbones = len(armature.pose.bones)
#                                    frame_range = action.frame_range
#                                    time_sensor = TimeSensor(cycleInterval=(frame_range[1] - frame_range[0]), loop=True, enabled=True)
#                                    clock_name = name+"_Clock"
#                                    setUSEDEF(clock_name, None, time_sensor)
#                                    activate_sensor = ProximitySensor(size=[ 1000000, 1000000, 1000000 ])
#                                    activate_name = name+"_Close"
#                                    setUSEDEF(activate_name, None, activate_sensor)
#                                    activate_route = ROUTE(
#                                            fromNode=activate_name,
#                                            fromField="enterTime",
#                                            toNode=clock_name,
#                                            toField="startTime")
#
#                                    positionInterpolators = []
#                                    orientationInterpolators = []
#                                    positionRoutes = []
#                                    orientationRoutes = []
#                                    root_found = False
#                                    for b in range(numbones):
#                                        bone = armature.pose.bones[b]
#                                        if bone.name == 'humanoid_root':
#                                            posInterp = PositionInterpolator()
#                                            setUSEDEF(name+"_PI_", bone.name, posInterp)
#                                            positionInterpolators.append(posInterp)
#                                            positionRoutes.append(ROUTE(
#                                                fromNode=clock_name,
#                                                fromField="fraction_changed",
#                                                toNode=name+"_PI_"+bone.name,
#                                                toField="set_fraction"))
#                                            positionRoutes.append(ROUTE(
#                                                fromNode=name+"_PI_"+bone.name,
#                                                fromField="value_changed",
#                                            toNode=HANIM_DEF_PREFIX+bone.name,
#                                            toField="translation"))
#                                            root_found = True
#
#                                        rotInterp = OrientationInterpolator()
#                                        setUSEDEF(name+"_OI_", bone.name, rotInterp)
#                                        orientationInterpolators.append(rotInterp)
#                                        orientationRoutes.append(ROUTE(
#                                            fromNode=clock_name,
#                                            fromField="fraction_changed",
#                                            toNode=name+"_OI_"+bone.name,
#                                            toField="set_fraction"))
#                                        orientationRoutes.append(ROUTE(
#                                            fromNode=name+"_OI_"+bone.name,
#                                            fromField="value_changed",
#                                            toNode=HANIM_DEF_PREFIX+bone.name,
#                                            toField="rotation"))
#                                    if not root_found:
#                                        print("humanoid_root not found in bone data")
#                                    root_found = False
#                                    lasttime = range(int(action.frame_range.x), int(action.frame_range.y) + 1)[-1]
#                                    keyframe_length = (frame_range[1] - frame_range[0]) / bpy.context.scene.render.fps
#                                    keyframe_time = 0
#                                    for frame in range(int(action.frame_range.x), int(action.frame_range.y) + 1):
#                                        # frame is frame number
#                                        bpy.context.scene.frame_set(frame)
#                                        print(f"Exporting interpolator frame {frame}")
#                                        for b in range(numbones):
#                                            bone = armature.pose.bones[b]
#                                            bone.rotation_mode = 'AXIS_ANGLE'
#                                            if bone.name == 'humanoid_root':
#                                                positionInterpolators[b].key.append(round_array_no_unit_scale([keyframe_time])[:])
#                                                loc = round_array(bone.location)
#                                                positionInterpolators[b].keyValue.append(loc) # location
#                                                root_found = True
#                                            axa = round_array_no_unit_scale(bone.rotation_axis_angle)
#                                            oldlen = len(orientationInterpolators[b].keyValue)
#                                            if oldlen > 0:
#                                                oldaxa = orientationInterpolators[b].keyValue[oldlen-1]
#                                            else:
#                                                oldaxa = None
#                                            if frame == lasttime or oldaxa is None or (oldaxa[0] != axa[0] or oldaxa[1] != axa[1] or oldaxa[2] != axa[2] or oldaxa[3] != axa[3]):
#                                                orientationInterpolators[b].key.append(round_array_no_unit_scale([keyframe_time])[:])
#                                                orientationInterpolators[b].keyValue.append([axa[0], axa[1], axa[2], axa[3]]) # TODO SFRotation.x, y, z, w
#                                        keyframe_time = keyframe_time + keyframe_length
#                                    children.append(time_sensor)
#                                    children.append(activate_sensor)
#                                    children.append(activate_route)
#                                    children.append(orientationInterpolators[:])
#                                    children.append(orientationRoutes[:])
#                                    if root_found:
#                                        print("humanoid_root found in bone data")
#                                        children.append(positionInterpolators[:])
#                                        children.append(positionRoutes[:])
#                                    else:
#                                        print("humanoid_root not found in bone data")
#                                    return children
#                                else:
#                                    print("No animation data associated with the armature.")
#                            else:
#                                print("No animation data found for the armature.")
#                      else:
#                          print("No armature found in the scene.")
#                  else:
#                      print("Object is not an armature.")
#                  return children
#              case     "HAnimMotion":
#                  print(f"Exporting bvh of {tag} {obj.type}")
#                  node = None
#                  if obj.type == 'ARMATURE':
#                      armature = obj
#                      bpy.context.view_layer.objects.active = armature
#                      bpy.ops.object.mode_set(mode='POSE')
#                      node = write_animation(obj)
#                  return node
#              case     "HAnimMotionOld":
#                  print(f"Exporting motion of {tag} {obj.type}")
#                  if obj.type == 'ARMATURE':
#                      armature = obj
#                      bpy.context.view_layer.objects.active = armature
#                      bpy.ops.object.mode_set(mode='POSE')
#                      print(f"Activated armature {armature}")
#                      if armature:
#                            animation_data = armature.animation_data
#                            if animation_data:
#                                print(f"Exporting animation data")
#                                action = animation_data.action
#                                if action:
#                                    print(f"Exporting action")
#                                    values = []
#                                    # numframes = range(int(action.frame_range.x), int(action.frame_range.y) + 1)
#                                    root_found = False
#                                    for frame in range(int(action.frame_range.x), int(action.frame_range.y) + 1):
#                                        # frame is frame number
#                                        bpy.context.scene.frame_set(frame)
#                                        print(f"Exporting values frame {frame}")
#                                        for bone in armature.pose.bones:
#                                            bone.rotation_mode = 'XZY'
#                                            if bone.name == 'humanoid_root':
#                                                loc = round_array(bone.location)
#                                                values.append(loc[0]) # location
#                                                values.append(loc[1]) # location  reverse Y and Z for X3D
#                                                values.append(loc[2]) # location  reverse Y and Z for X3D
#                                                root_found = True
#                                            eul = bone.rotation_euler
#                                            rot = [ eul.x, eul.y, eul.z ]
#                                            if bpy.context.scene.unit_settings.system_rotation == 'DEGREES':
#                                                r = round_array_no_unit_scale([math.radians(rot[0]), math.radians(rot[1]),math.radians(rot[2])])
#                                                values.append(r[0]) # rotation_euler
#                                                values.append(r[1]) # rotation_euler
#                                                values.append(r[2]) # rotation_euler
#                                            else:
#                                                r = round_array_no_unit_scale(rot)
#                                                values.append(r[0]) # rotation_euler
#                                                values.append(r[1]) # rotation_euler
#                                                values.append(r[2]) # rotation_euler
#                                            # values.append(bone.scale[0]) # scale
#                                            # values.append(bone.scale[1]) # scale
#                                            # values.append(bone.scale[2]) # scale
#                                    numbones = len(armature.pose.bones)
#                                    if root_found:
#                                        print("humanoid_root found in bone data, adding position")
#                                        channelsEnabled=MFBool([random.choice([True]) for i in range(numbones * 3 + 1)])
#                                        channels="6 Xposition Yposition Zposition Xrotation Yrotation Zrotation "+("3 Xrotation Yrotation Zrotation " * (numbones - 1))
#                                        joints=HANIM_DEF_PREFIX+"humanoid_root "+(" ".join(HANIM_DEF_PREFIX+bone.name for bone in armature.pose.bones if bone.name != "humanoid_root"))
#                                    else:
#                                        print("humanoid_root not found in bone data, not adding position")
#                                        channelsEnabled=MFBool([random.choice([True]) for i in range(numbones * 3)])
#                                        channels=("3 Xrotation Yrotation Zrotation " * (numbones - 1))
#                                        joints=(" ".join(HANIM_DEF_PREFIX+bone.name for bone in armature.pose.bones))
#                                    node = HAnimMotion(
#                                        #frameIncrement=1,
#                                        #frameIndex=0,
#                                        loop=True,
#                                        #frameDuration=0.033333,
#                                        enabled=True,
#                                        channels=channels,
#                                        joints=joints,
#                                        channelsEnabled=channelsEnabled,
#                                        values=MFFloat(values)
#                                        )
#                                    return node
#                                else:
#                                    print("No animation data associated with the armature.")
#                            else:
#                                print("No animation data found for the armature.")
#                      else:
#                          print("No armature found in the scene.")
#                  else:
#                      print("Object is not an armature.")
#                  node = HAnimMotion()  # fake motion
#                  return node

    def b2xJoint(joint_parent, joint, matrix, joint_lookup, segment_lookup, armature, skinCoordInfo):
        # print(f"joint {joint}")
        try:
            if skinCoordInfo[joint.name] is None:
                skinCoordWeight = []
                skinCoordIndex = []
            else:
                skinCoordIndex = skinCoordInfo[joint.name]['indices']
                skinCoordWeight = skinCoordInfo[joint.name]['weights']
        except:
                skinCoordWeight = []
                skinCoordIndex = []
#            for obj in bpy.data.objects:
#                if obj.type == 'MESH':
#                    if obj.parent == armature:
#                        vertex_groups = obj.vertex_groups
#                        skinCoordIndex = []
#                        for vertex in obj.data.vertices:
#                            skinCoordWeight = []
#                            for group in vertex.groups:
#                                #print("Mesh", vertex_groups)
#                                # print("groups", vertex.groups)
#                                if group.group >= 0  and group.group < len(vertex_groups) and vertex_groups[group.group].name == joint.name:
#                                    skinCoordIndex.append(vertex.index)
#                                    skinCoordWeight.append(group.weight)
        # joint_id = quoteattr(unique_name(joint, joint.name, uuid_cache_skeleton, clean_func=clean_def, sep="_"))
        if not joint.name.endswith("_end"):  # exclude sites for now
            try:
                segment_name = segment_lookup[joint.name]
            except KeyError:
                segment_name = None
            node = b2xHAnimNode(joint, matrix, joint.name, "HAnimJoint", segment_name=segment_name, skinCoordIndex=skinCoordIndex, skinCoordWeight=skinCoordWeight)

            for joint_child in joint_lookup[joint.name]['joint_children']:
                child = b2xJoint(joint, joint_child.joint, joint_child.joint.matrix, joint_lookup, segment_lookup, armature, skinCoordInfo)
                node.children.append(child)
            return node
        else:
            site_name = joint.name
            site = HAnimSite(children=[
                Transform( children=[
                    Shape(
                        USE="SiteShape"
                        #appearance=Appearance(material=Material(diffuseColor = (0, 0, 1))),
                        #geometry=Box(size = (0.05, 0.05, 0.05))
                    )
                ])
            ])
            setUSEDEF(HANIM_DEF_PREFIX, site_name, site)
            segment = HAnimSegment(children=[ site ])
            setUSEDEF(HANIM_DEF_PREFIX+"SEGMENT_FOR_", site_name, segment)
            node = HAnimJoint( children=[ segment ]) # TODO maybe return site?
            return node;

    class HAnimNode:
        def __init__(self, name, parent_name, joint, joint_lookup):
            self.name = name
            self.parent_name = parent_name
            self.joint = joint
            joint_lookup[joint.name] = {}
            joint_lookup[joint.name]['joint'] = joint
            joint_lookup[joint.name]['joint_children'] = []
            if parent_name:
                try:
                    joint_lookup[parent_name]['joint_children'].append(self)
                except:
                    joint_lookup[parent_name]['joint_children'].append(self)


    def b2xFindCoordinate(x3dnode):
        defList = []
        children = None
        if (isinstance(x3dnode, Group)):
            children = x3dnode.children
        elif (isinstance(x3dnode, Transform)):
            children = x3dnode.children
        elif (isinstance(x3dnode, Shape)):
            children = [x3dnode.geometry]
        elif (isinstance(x3dnode, (IndexedFaceSet, IndexedLineSet, IndexedTriangleFanSet, IndexedTriangleSet, IndexedTriangleStripSet, PointSet, TriangleFanSet, TriangleSet, TriangleStripSet))):
            children = [x3dnode.coord]
        elif (isinstance(x3dnode, Coordinate)):
            if x3dnode.DEF is not None:
                defList.append(x3dnode.DEF)
            else:
                defList.append(x3dnode.name)
        if children is not None:
            for child in children:
                defList = defList + b2xFindCoordinate(child)
        return defList

    def b2xArmature(obj, obj_main, obj_children, obj_matrix, data, world):
        armature = obj
        armature_matrix = obj_matrix
        print(f"Info: Called b2xArmature, exporting {armature.name}, object type {armature.type}")
        segment_lookup = JointsSegments

        # each armature needs their own hierarchy
        joint_lookup = {}
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='OBJECT')
        #armature_id = quoteattr(HANIM_DEF_PREFIX+armature.parent.name)
        # motions = [b2xHAnimNode(armature, armature_matrix, "motions", "HAnimMotion")]
        motions = None
        humanoid = b2xHAnimNode(armature, armature_matrix, "humanoid", "HAnimHumanoid", motions=motions)
        HAnimNode(armature.name, None, armature, joint_lookup)  # populates joint_lookup
        for joint in armature.data.bones:
            if joint.parent:
                joint_parent_name = joint.parent.name
            else:
                joint_parent_name = armature.name
            HAnimNode(joint.name, joint_parent_name, joint, joint_lookup) # populates joint_lookup

        # BEGINNNING
        # get the names of the bones in the armature associated with the object
        #for modifier in obj.modifiers:
            #if modifier.type == 'ARMATURE':
                #armature = modifier.object.data
            
        armature_bones = {bone.name for bone in armature.data.bones}
                #break
            
        """
        # get the mapping from group indices to bones
        # TDOO onnly work on a one MESH file
        # https://blenderartists.org/t/script-that-normalize-only-bones-weight-in-vertex-groups/557887
        skinCoordInfo = {}

        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='OBJECT') # ('OBJECT', 'EDIT', 'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT')


        obj = bpy.context.active_object
        mesh = bpy.data.objects[obj.name].data
        mesh_name = bpy.data.objects[obj.name].data.name
        listbones = {}
        b=0


        ## check the armature attached to the object
        for modifiers in bpy.data.objects[obj.name].modifiers:
            if modifiers.type == 'ARMATURE':
                data = bpy.data.objects[modifiers.object.name].data.name
                for bones in bpy.data.armatures[data].bones:
                    #print(f"Listing bones {bones.name}")
                    listbones[bones.name] = b
                    b+=1


        ## create the dict for the groups attache the index to the name
        DictGroup = {} ##ask the index it will give you the name

        i=0
        for group in bpy.context.active_object.vertex_groups:
            #print(f"Listing group {group.name}")
            DictGroup[i]=group.name
            i+=1

        if bpy.context.mode == 'OBJECT':
            for vertex in bpy.data.meshes[mesh_name].vertices: ##in each vertex of the mesh
                total_weight=0 ##where to add the total of unlock
                space_left=1 ##goal less the locked ones

                for group in vertex.groups: #first loop to calculate the total weight and the space allowed if some are locked
                    if DictGroup[group.group] in listbones: ##if it's a bone
                        # group.weight
                        # print("this is a bone " + str(DictGroup[group.group]))
                        pass
                    else:
                        print("this is not a bone group " + str(DictGroup[group.group]))

                for group in vertex.groups: #second on is to assign the new weight
                    if DictGroup[group.group] in listbones:
                        if not obj.vertex_groups[DictGroup[group.group]].lock_weight: ##if it's not locked!
                            this_weight = group.weight
                            # print(f"OBJECT bone {DictGroup[group.group]} index {vertex.index} weight {this_weight}")
                            group_bone = DictGroup[group.group]
                            try:
                                if skinCoordInfo[group_bone] is None:
                                    skinCoordInfo = {**skinCoordInfo, group_bone : { 'indices' : [], 'weights': []}}
                            except:
                                    skinCoordInfo = {**skinCoordInfo, group_bone : { 'indices' : [], 'weights': []}}
                            skinCoordInfo[group_bone]['indices'].append(vertex.index)
                            skinCoordInfo[group_bone]['weights'].append(this_weight)

                            # obj.vertex_groups[DictGroup[group.group]].add([vertex.index],new_weight,'REPLACE')

        if bpy.context.mode == 'EDIT_MESH':
            myVertex = {}
            v=0
            bpy.ops.object.mode_set(mode='OBJECT')
            for vertex in bpy.data.meshes[mesh_name].vertices:
                if vertex.select==True:
                    myVertex[v]=vertex.index
                    v+=1

            for each in myVertex:
                for group in mesh.vertices[myVertex[each]].groups: #first loop to calculate the total weight and the space allowed if some are locked
                    # print(group.weight)
                    if DictGroup[group.group] in listbones: ##if it's a bone
                        #print("this is a bone " + str(DictGroup[group.group]))
                        pass
                    else:
                        print("this is not a bone group " + str(DictGroup[group.group]))

                for group in mesh.vertices[myVertex[each]].groups: #second on is to assign the new weight
                    if DictGroup[group.group] in listbones:
                        if not obj.vertex_groups[DictGroup[group.group]].lock_weight: ##if it's not locked!
                            this_weight = group.weight
                            # print(f"EDIT MESH bone {DictGroup[group.group]} index {myVertex[each]} weight {this_weight}")
                            group_bone = DictGroup[group.group]
                            try:
                                if skinCoordInfo[group_bone] is None:
                                    skinCoordInfo = {**skinCoordInfo, group_bone : { 'indices' : [], 'weights': []}}
                            except:
                                    skinCoordInfo = {**skinCoordInfo, group_bone : { 'indices' : [], 'weights': []}}
                            skinCoordInfo[group_bone]['indices'].append(vertex.index)
                            skinCoordInfo[group_bone]['weights'].append(this_weight)

        bpy.ops.object.mode_set(mode='EDIT')
        for group_bone in skinCoordInfo:
            try:
                info = skinCoordInfo[group_bone]
                print(f"\n<{group_bone}>\n")
                indices = info['indices']
                weights = info['weights']
                for i in range(len(info['indices'])):
                    print(f"({indices[i]}) = {weights[i]}")
            except:
                pass
        """
        # get the mapping from group indices to bones
        skinCoordInfo = {}
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                if obj.parent == armature:
                    group_to_bone = {i: group.name for i, group in enumerate(obj.vertex_groups)}
        
                    # determine the bone weights associated with each vertex
                    mesh = obj.data
                    for vertex in mesh.vertices: ##in each vertex of the mesh
                        #print('Vertex', vertex.index)
                        for group in vertex.groups: #first loop to calculate the total weight and the space allowed if some are locked
                            group_index = group.group
                            group_bone = group_to_bone[group_index]
                            if group_bone in armature_bones: ##if it's a bone
                                #print('\t', group_bone, group.weight)
                                try:
                                    if skinCoordInfo[group_bone] is None:
                                        skinCoordInfo = {**skinCoordInfo, group_bone : { 'indices' : [], 'weights': []}}
                                except:
                                        skinCoordInfo = {**skinCoordInfo, group_bone : { 'indices' : [], 'weights': []}}
                                skinCoordInfo[group_bone]['indices'].append(vertex.index)
                                    
                                skinCoordInfo[group_bone]['weights'].append(group.weight)
                            else:
                                print('\t', 'NOT A BONE:', group_bone, group.weight)
        humanoid.skeleton = [b2xJoint(obj_main, armature, armature_matrix, joint_lookup, segment_lookup, armature, skinCoordInfo)]
        # joints should be printed after skeleton in x3d.py. That's why I've picked out skeleton in x3d.py
        for joint in armature.data.bones:
            if not joint.name.endswith("_end"):  # exclude sites for now
                node = HAnimJoint()
                setUSEDEF(HANIM_DEF_PREFIX+joint.name, None, node)
                humanoid.joints.append(node)
        scale = 1 # getscenescale(bpy.context.scene)
        unit_settings = bpy.context.scene.unit_settings
        length_unit = bpy.context.scene.unit_settings.length_unit 
        print(f"scene scale is {scale} {unit_settings} {length_unit}")
        return humanoid

    def image_get(mat):
        from bpy_extras import node_shader_utils
        if mat.use_nodes:
            mat_wrap = node_shader_utils.PrincipledBSDFWrapper(mat)
            base_color_tex = mat_wrap.base_color_texture
            if base_color_tex and base_color_tex.image:
                return base_color_tex.image
        return None

    def b2xIndexedFaceSet(obj, mesh, mesh_name, matrix, world):
        obj_id = unique_name(obj, OB_ + obj.name, uuid_cache_object, clean_func=clean_def, sep="_")
        mesh_id = unique_name(mesh, ME_ + mesh_name, uuid_cache_mesh, clean_func=clean_def, sep="_")
        mesh_id_group = prefix_str(mesh_id, group_)
        mesh_id_coords = prefix_str(mesh_id, 'coords_')
        mesh_id_normals = prefix_str(mesh_id, 'normals_')

        # Be sure tessellated loop triangles are available!
        if export_settings['x3dv_use_triangulate']:
            if not mesh.loop_triangles and mesh.polygons:
                mesh.calc_loop_triangles()

        top = None
        bottom = None
        use_collnode = bool([mod for mod in obj.modifiers
                             if mod.type == 'COLLISION'
                             if mod.show_viewport])

        if use_collnode:
            coll = Collision(enabled='True')
            top = coll
            bottom = coll

        # use _ifs_TRANSFORM suffix so we dont collide with transform node when
        # hierarchys are used.
        trans = b2xTransform(matrix, suffix_str(obj_id, "_ifs" + _TRANSFORM))
        grp = None
        if mesh.tag:
            grp = Group(USE=mesh_id_group)
            if bottom != None:
                bottom.children.append(grp)
            else:
                top = grp
            bottom = grp
            
        else:
            mesh.tag = True
            grp = Group(DEF=mesh_id_group)
            if bottom != None:
                bottom.children.append(grp)
            else:
                top = grp
            bottom = grp

            is_uv = bool(mesh.uv_layers.active)
            # is_col, defined for each material

            is_coords_written = False

            mesh_materials = mesh.materials[:]
            if not mesh_materials:
                mesh_materials = [None]

            mesh_material_tex = [None] * len(mesh_materials)
            mesh_material_mtex = [None] * len(mesh_materials)
            mesh_material_images = [None] * len(mesh_materials)

            for i, material in enumerate(mesh_materials):
                if material and 'texture_slots' in material:
                    for mtex in material.texture_slots:
                        if mtex:
                            tex = mtex.texture
                            if tex and tex.type == 'IMAGE':
                                image = tex.image
                                if image:
                                    mesh_material_tex[i] = tex
                                    mesh_material_mtex[i] = mtex
                                    mesh_material_images[i] = image
                                    break
                elif material:
                    mesh_material_images[0] = image_get(material)

            # fast access!
            mesh_vertices = mesh.vertices[:]
            mesh_loops = mesh.loops[:]
            mesh_polygons = mesh.polygons[:]
            mesh_polygons_materials = [p.material_index for p in mesh_polygons]
            mesh_polygons_vertices = [p.vertices[:] for p in mesh_polygons]

            if len(set(mesh_material_images)) > 0:  # make sure there is at least one image
                mesh_polygons_image = [mesh_material_images[material_index] for material_index in mesh_polygons_materials]
            else:
                mesh_polygons_image = [None] * len(mesh_polygons)
            mesh_polygons_image_unique = set(mesh_polygons_image)

            # group faces
            polygons_groups = {}
            for material_index in range(len(mesh_materials)):
                for image in mesh_polygons_image_unique:
                    polygons_groups[material_index, image] = []
            del mesh_polygons_image_unique

            for i, (material_index, image) in enumerate(zip(mesh_polygons_materials, mesh_polygons_image)):
                polygons_groups[material_index, image].append(i)

            # Py dict are sorted now, so we can use directly polygons_groups.items()
            # and still get consistent reproducible outputs.

            is_col = mesh.vertex_colors.active
            mesh_loops_col = mesh.vertex_colors.active.data if is_col else None

            # Check if vertex colors can be exported in per-vertex mode.
            # Do we have just one color per vertex in every face that uses the vertex?
            if is_col:
                def calc_vertex_color():
                    vert_color = [None] * len(mesh.vertices)

                    for i, p in enumerate(mesh_polygons):
                        for lidx in p.loop_indices:
                            l = mesh_loops[lidx]
                            if vert_color[l.vertex_index] is None:
                                vert_color[l.vertex_index] = mesh_loops_col[lidx].color[:]
                            elif vert_color[l.vertex_index] != mesh_loops_col[lidx].color[:]:
                                return False, ()

                    return True, vert_color

                is_col_per_vertex, vert_color = calc_vertex_color()
                del calc_vertex_color

            # If using looptris, we need a mapping poly_index -> loop_tris_indices...
            if export_settings['x3dv_use_triangulate']: 
                polygons_to_loop_triangles_indices = [[] for  i in range(len(mesh_polygons))]
                for ltri in mesh.loop_triangles:
                    polygons_to_loop_triangles_indices[ltri.polygon_index].append(ltri)

            for (material_index, image), polygons_group in polygons_groups.items():
                if polygons_group:
                    material = mesh_materials[material_index]
                    shape_id = unique_name(mesh, SH_ + mesh_name, uuid_cache_mesh, clean_func=clean_def, sep="_")
                    shape = Shape(DEF=shape_id)
                    bottom.children.append(shape)

                    is_smooth = False

                    # kludge but as good as it gets!
                    for i in polygons_group:
                        if mesh_polygons[i].use_smooth:
                            is_smooth = True
                            break

                    # UV's and VCols split verts off which effects smoothing
                    # force writing normals in this case.
                    # Also, creaseAngle is not supported for IndexedTriangleSet,
                    # so write normals when is_smooth (otherwise
                    # IndexedTriangleSet can have only all smooth/all flat shading).
                    is_force_normals = export_settings['x3dv_use_triangulate'] and (is_smooth or is_uv or is_col)

                    """
                    if use_h3d:
                        gpu_shader = gpu_shader_cache.get(material)  # material can be 'None', uses dummy cache
                        if gpu_shader is None:
                            gpu_shader = gpu_shader_cache[material] = gpu.export_shader(scene, material)

                            if 1:  # XXX DEBUG
                                gpu_shader_tmp = gpu.export_shader(scene, material)
                                import pprint
                                print('\nWRITING MATERIAL:', material.name)
                                del gpu_shader_tmp['fragment']
                                del gpu_shader_tmp['vertex']
                                pprint.pprint(gpu_shader_tmp, width=120)
                                #pprint.pprint(val['vertex'])
                                del gpu_shader_tmp
                    """
                    appr = Appearance()
                    shape.appearance = appr
                    print(f" Image {image} use_h3d {use_h3d}")
                    if image and not use_h3d:
                        imt = b2xImageTexture( image)
                        appr.texture = imt
                        print(f" Appearance {appr} texture {appr.texture} url {appr.texture.url}")
                        # transform by mtex
                        # TODO
                        if 0:
                            loc = mesh_material_mtex[material_index].offset[:2]

                            # mtex_scale * tex_repeat
                            sca_x, sca_y = mesh_material_mtex[material_index].scale[:2]

                            sca_x *= mesh_material_tex[material_index].repeat_x
                            sca_y *= mesh_material_tex[material_index].repeat_y

                            # flip x/y is a sampling feature, convert to transform
                            if mesh_material_tex[material_index].use_flip_axis:
                                rot = math.pi / -2.0
                                sca_x, sca_y = sca_y, -sca_x
                            else:
                                rot = 0.0

                            tt = TextureTransform()
                            tt.translation = loc
                            tt.scale = (sca_x,sca_y)
                            tt.rotation = rot
                            appr.textureTransform = tt

                    if use_h3d:
                        #mat_tmp = material if material else gpu_shader_dummy_mat
                        #writeMaterialH3D(ident, mat_tmp, world,
                        #                 obj, gpu_shader)
                        #del mat_tmp
                        pass
                    else:
                        if material:
                            mat = b2xMaterial(material, world)
                            appr.material = mat

                    #/Appearance

                    mesh_loops_uv = mesh.uv_layers.active.data if is_uv else None

                    #-- IndexedFaceSet or IndexedLineSet
                    if export_settings['x3dv_use_triangulate']:
                        ident_step = ident + (' ' * (-len(ident) + \
                        fw('%s<IndexedTriangleSet ' % ident)))
                        its = IndexedTriangleSet()
                        shape.geometry = its
                        # --- Write IndexedTriangleSet Attributes (same as IndexedFaceSet)
                        its.solid = material and material.use_backface_culling
                        if export_settings['x3dv_normals'] or is_force_normals:
                            its.normalPerVertex = True
                        else:
                            # Tell X3D browser to generate flat (per-face) normals
                            its.normalPerVertex = False


                        slot_uv = None
                        slot_col = None
                        def _tuple_from_rounded_iter(it):
                            return tuple(round(v, 5) for v in it)

                        if is_uv and is_col:
                            slot_uv = 0
                            slot_col = 1

                            def vertex_key(lidx):
                                return (
                                    _tuple_from_rounded_iter(mesh_loops_uv[lidx].uv),
                                    _tuple_from_rounded_iter(mesh_loops_col[lidx].color),
                                )
                        elif is_uv:
                            slot_uv = 0

                            def vertex_key(lidx):
                                return (
                                    _tuple_from_rounded_iter(mesh_loops_uv[lidx].uv),
                                )
                        elif is_col:
                            slot_col = 0

                            def vertex_key(lidx):
                                return (
                                    _tuple_from_rounded_iter(mesh_loops_col[lidx].color),
                                )
                        else:
                            # ack, not especially efficient in this case
                            def vertex_key(lidx):
                                return None

                        # build a mesh mapping dict
                        vertex_hash = [{} for i in range(len(mesh.vertices))]
                        face_tri_list = [[None, None, None] for i in range(len(mesh.loop_triangles))]
                        vert_tri_list = []
                        totvert = 0
                        totface = 0
                        temp_tri = [None] * 3
                        for pidx in polygons_group:
                            for ltri in polygons_to_loop_triangles_indices[pidx]:
                                for tri_vidx, (lidx, vidx) in enumerate(zip(ltri.loops, ltri.vertices)):
                                    key = vertex_key(lidx)
                                    vh = vertex_hash[vidx]
                                    x3d_v = vh.get(key)
                                    if x3d_v is None:
                                        x3d_v = key, vidx, totvert
                                        vh[key] = x3d_v
                                        # key / original_vertex / new_vertex
                                        vert_tri_list.append(x3d_v)
                                        totvert += 1
                                    temp_tri[tri_vidx] = x3d_v

                                face_tri_list[totface][:] = temp_tri[:]
                                totface += 1

                        del vertex_key
                        del _tuple_from_rounded_iter
                        assert(len(face_tri_list) == len(mesh.loop_triangles))

                        #fw(ident_step + 'index="')
                        for x3d_f in face_tri_list:
                            #fw('%i %i %i ' % (x3d_f[0][2], x3d_f[1][2], x3d_f[2][2]))
                            its.index.append((x3d_f[0][2], x3d_f[1][2], x3d_f[2][2]))

                        coord = Coordinate()
                        its.coord = coord

                        #fw('%s<Coordinate ' % ident)
                        #fw('point="')
                       
                        for x3d_v in vert_tri_list:
                            #fw('%.6f %.6f %.6f ' % mesh_vertices[x3d_v[1]].co[:])
                            coord.point.append(round_array(mesh_vertices[x3d_v[1]].co[:]))

                        if export_settings['use_normals'] or is_force_normals:
                            norm = Normal()
                            its.normal = norm
                            #fw('%s<Normal ' % ident)
                            #fw('vector="')
                            for x3d_v in vert_tri_list:
                                #fw('%.6f %.6f %.6f ' % mesh_vertices[x3d_v[1]].normal[:])
                                norm.vector.append(round_array_no_unit_scale(mesh_vertices[x3d_v[1]].normal[:]))

                        if is_uv:
                            texcoord = TextureCoordinate()
                            its.texCoord = texcoord
                            #fw('%s<TextureCoordinate point="' % ident)
                            for x3d_v in vert_tri_list:
                                #fw('%.4f %.4f ' % x3d_v[0][slot_uv])
                                texcoord.point.append(round_array_no_unit_scale(x3d_v[0][slot_uv]))


                        if is_col:
                            #fw('%s<ColorRGBA color="' % ident)
                            rgba = ColorRGBA()
                            its.color = rgba
                            for x3d_v in vert_tri_list:
                                #fw('%.3f %.3f %.3f %.3f ' % x3d_v[0][slot_col])
                                rgba.color.append(x3d_v[0][slot_col])

                        """
                        if use_h3d:
                            # write attributes
                            for gpu_attr in gpu_shader['attributes']:

                                # UVs
                                if gpu_attr['type'] == gpu.CD_MTFACE:
                                    if gpu_attr['datatype'] == gpu.GPU_DATA_2F:
                                        fw('%s<FloatVertexAttribute ' % ident)
                                        fw('name="%s" ' % gpu_attr['varname'])
                                        fw('numComponents="2" ')
                                        fw('value="')
                                        for x3d_v in vert_tri_list:
                                            fw('%.4f %.4f ' % x3d_v[0][slot_uv])
                                        fw('" />\n')
                                    else:
                                        assert(0)

                                elif gpu_attr['type'] == gpu.CD_MCOL:
                                    if gpu_attr['datatype'] == gpu.GPU_DATA_4UB:
                                        pass  # XXX, H3D can't do
                                    else:
                                        assert(0)
                        """

                        #/IndexedTriangleSet

                    else:
                        ifs = IndexedFaceSet()
                        shape.geometry = ifs
                        # --- Write IndexedFaceSet Attributes (same as IndexedTriangleSet)
                        ifs.solid = material and material.use_backface_culling
                        if is_smooth:
                            # use Auto-Smooth angle, if enabled. Otherwise make
                            # the mesh perfectly smooth by creaseAngle > pi.
                            ifs.creaseAngle = mesh.auto_smooth_angle if mesh.use_auto_smooth else 4.0

                        if export_settings['x3dv_normals']:
                            # currently not optional, could be made so:
                            ifs.normalPerVertex = True

                        # IndexedTriangleSet assumes true
                        if is_col and not is_col_per_vertex:
                            ifs.colorPerVertex = False

                        # for IndexedTriangleSet we use a uv per vertex so this isn't needed.
                        if is_uv:
                            j = 0
                            for i in polygons_group:
                                num_poly_verts = len(mesh_polygons_vertices[i])
                                #fw('%s -1 ' % ' '.join((str(i) for i in range(j, j + num_poly_verts))))
                                for i in range(j, j + num_poly_verts):
                                    ifs.texCoordIndex.append(i)
                                ifs.texCoordIndex.append(-1)
                                j += num_poly_verts
                            # --- end texCoordIndex

                        if True:
                            for i in polygons_group:
                                poly_verts = mesh_polygons_vertices[i]
                                #fw('%s -1 ' % ' '.join((str(i) for i in poly_verts)))
                                for i in poly_verts:
                                    ifs.coordIndex.append(i)
                                    if export_settings['x3dv_normals']:
                                        ifs.normalIndex.append(i)
                                ifs.coordIndex.append(-1)
                                if export_settings['x3dv_normals']:
                                    ifs.normalIndex.append(-1)
                            # --- end coordIndex


                        # --- Write IndexedFaceSet Elements
                        if True:
                            if is_coords_written:
                                coord = Coordinate( USE=mesh_id_coords )
                                ifs.coord = coord
                                if export_settings['x3dv_normals']:
                                    norms = Normal(USE = mesh_id_normals)
                                    ifs.normal = norms
                            else:
                                coord = Coordinate(DEF = mesh_id_coords)
                                ifs.coord = coord
                                for v in mesh.vertices:
                                    #fw('%.6f %.6f %.6f ' % v.co[:])
                                    #ifs.coord.point.append(v.co[:])
                                    vco = [ None, None, None ]
                                    vco[0] = v.co[0]
                                    vco[1] = v.co[1]
                                    vco[2] = v.co[2]
                                    loc = round_array(vco)
                                    ifs.coord.point.append(loc[:])

                                is_coords_written = True

                                if export_settings['x3dv_normals']:
                                    norms = Normal(DEF = mesh_id_normals)
                                    ifs.normal = norms

                                    for v in mesh.vertices:
                                        #fw('%.6f %.6f %.6f ' % v.normal[:])
                                        ifs.normal.vector.append(round_array_no_unit_scale(v.normal[:]))

                        if is_uv:
                            texcoord = TextureCoordinate()
                            ifs.texCoord = texcoord
                            for i in polygons_group:
                                for lidx in mesh_polygons[i].loop_indices:
                                    # John patch
                                    if len(mesh_loops_uv) > 0:
                                        #fw('%.4f %.4f ' % mesh_loops_uv[lidx].uv[:])
                                        texcoord.point.append(round_array_no_unit_scale(mesh_loops_uv[lidx].uv[:]))

                        if is_col:
                            # Need better logic here, dynamic determination
                            # which of the X3D coloring models fits better this mesh - per face
                            # or per vertex. Probably with an explicit fallback mode parameter.
                            #fw('%s<ColorRGBA color="' % ident)
                            rgba = ColorRGBA()
                            ifs.color = rgba
                            if is_col_per_vertex:
                                for i in range(len(mesh.vertices)):
                                    # may be None,
                                    #fw('%.3f %.3f %.3f %.3f ' % (vert_color[i] or (0.0, 0.0, 0.0, 0.0)))
                                    ifs.color.color.append(vert_color[i] or (0.0, 0.0, 0.0, 0.0))
                            else: # Export as colors per face.
                                # TODO: average them rather than using the first one!
                                for i in polygons_group:
                                    #fw('%.3f %.3f %.3f %.3f ' % mesh_loops_col[mesh_polygons[i].loop_start].color[:])
                                    ifs.color.color.append(mesh_loops_col[mesh_polygons[i].loop_start].color[:])

                        #/IndexedFaceSet

                    #/Shape

                    # XXX

            #fw('%s<PythonScript DEF="PS" url="object.py" >\n' % ident)
            #fw('%s    <ShaderProgram USE="MA_Material.005" containerField="references"/>\n' % ident)
            #fw('%s</PythonScript>\n' % ident)

            # /Group>

        return top

    def b2xMaterial(material, world):
        material_id = unique_name(material, MA_ + material.name, uuid_cache_material, clean_func=clean_def, sep="_")

        # look up material name, use it if available
        if material.tag:
            mat = Material(USE=material_id)
        else:
            material.tag = True
            mat = Material(DEF=material_id)

            emit = 0.0 #material.emit
            ambient = 0.0 #material.ambient / 3.0
            diffuseColor = material.diffuse_color[:3]
            if world and 0:
                ambiColor = ((material.ambient * 2.0) * world.ambient_color)[:]
            else:
                ambiColor = 0.0, 0.0, 0.0

            emitColor = tuple(((c * emit) + ambiColor[i]) / 2.0 for i, c in enumerate(diffuseColor))
            shininess = material.specular_intensity
            specColor = tuple((c + 0.001) / (1.25 / (material.specular_intensity + 0.001)) for c in material.specular_color)
            transp = 1.0 - material.diffuse_color[3]

            mat.diffuseColor = clamp_color(diffuseColor)
            mat.specularColor = clamp_color(specColor)
            mat.emissiveColor = clamp_color(emitColor)
            mat.ambientIntensity = ambient
            mat.shininess = shininess
            mat.transparency = transp
        return mat

    """
    def b2xMaterialH3D(ident, material, world,
                         obj, gpu_shader):
        material_id = unique_name(material, 'MA_' + material.name, uuid_cache_material, clean_func=clean_def, sep="_")

        fw('%s<Material />\n' % ident)
        if material.tag:
            fw('%s<ComposedShader USE=%s />\n' % (ident, material_id))
        else:
            material.tag = True

            # GPU_material_bind_uniforms
            # GPU_begin_object_materials

            #~ CD_MCOL 6
            #~ CD_MTFACE 5
            #~ CD_ORCO 14
            #~ CD_TANGENT 18
            #~ GPU_DATA_16F 7
            #~ GPU_DATA_1F 2
            #~ GPU_DATA_1I 1
            #~ GPU_DATA_2F 3
            #~ GPU_DATA_3F 4
            #~ GPU_DATA_4F 5
            #~ GPU_DATA_4UB 8
            #~ GPU_DATA_9F 6
            #~ GPU_DYNAMIC_LIGHT_DYNCO 7
            #~ GPU_DYNAMIC_LIGHT_DYNCOL 11
            #~ GPU_DYNAMIC_LIGHT_DYNENERGY 10
            #~ GPU_DYNAMIC_LIGHT_DYNIMAT 8
            #~ GPU_DYNAMIC_LIGHT_DYNPERSMAT 9
            #~ GPU_DYNAMIC_LIGHT_DYNVEC 6
            #~ GPU_DYNAMIC_OBJECT_COLOR 5
            #~ GPU_DYNAMIC_OBJECT_IMAT 4
            #~ GPU_DYNAMIC_OBJECT_MAT 2
            #~ GPU_DYNAMIC_OBJECT_VIEWIMAT 3
            #~ GPU_DYNAMIC_OBJECT_VIEWMAT 1
            #~ GPU_DYNAMIC_SAMPLER_2DBUFFER 12
            #~ GPU_DYNAMIC_SAMPLER_2DIMAGE 13
            #~ GPU_DYNAMIC_SAMPLER_2DSHADOW 14

            '''
            inline const char* typeToString( X3DType t ) {
              switch( t ) {
              case     SFFLOAT: return "SFFloat";
              case     MFFLOAT: return "MFFloat";
              case    SFDOUBLE: return "SFDouble";
              case    MFDOUBLE: return "MFDouble";
              case      SFTIME: return "SFTime";
              case      MFTIME: return "MFTime";
              case     SFINT32: return "SFInt32";
              case     MFINT32: return "MFInt32";
              case     SFVEC2F: return "SFVec2f";
              case     MFVEC2F: return "MFVec2f";
              case     SFVEC2D: return "SFVec2d";
              case     MFVEC2D: return "MFVec2d";
              case     SFVEC3F: return "SFVec3f";
              case     MFVEC3F: return "MFVec3f";
              case     SFVEC3D: return "SFVec3d";
              case     MFVEC3D: return "MFVec3d";
              case     SFVEC4F: return "SFVec4f";
              case     MFVEC4F: return "MFVec4f";
              case     SFVEC4D: return "SFVec4d";
              case     MFVEC4D: return "MFVec4d";
              case      SFBOOL: return "SFBool";
              case      MFBOOL: return "MFBool";
              case    SFSTRING: return "SFString";
              case    MFSTRING: return "MFString";
              case      SFNODE: return "SFNode";
              case      MFNODE: return "MFNode";
              case     SFCOLOR: return "SFColor";
              case     MFCOLOR: return "MFColor";
              case SFCOLORRGBA: return "SFColorRGBA";
              case MFCOLORRGBA: return "MFColorRGBA";
              case  SFROTATION: return "SFRotation";
              case  MFROTATION: return "MFRotation";
              case  SFQUATERNION: return "SFQuaternion";
              case  MFQUATERNION: return "MFQuaternion";
              case  SFMATRIX3F: return "SFMatrix3f";
              case  MFMATRIX3F: return "MFMatrix3f";
              case  SFMATRIX4F: return "SFMatrix4f";
              case  MFMATRIX4F: return "MFMatrix4f";
              case  SFMATRIX3D: return "SFMatrix3d";
              case  MFMATRIX3D: return "MFMatrix3d";
              case  SFMATRIX4D: return "SFMatrix4d";
              case  MFMATRIX4D: return "MFMatrix4d";
              case UNKNOWN_X3D_TYPE:
              default:return "UNKNOWN_X3D_TYPE";
            '''
            import gpu

            fw('%s<ComposedShader DEF=%s language="GLSL" >\n' % (ident, material_id))
            ident += '\t'

            shader_url_frag = 'shaders/%s_%s.frag' % (filename_strip, material_id[1:-1])
            shader_url_vert = 'shaders/%s_%s.vert' % (filename_strip, material_id[1:-1])

            # write files
            shader_dir = os.path.join(base_dst, 'shaders')
            if not os.path.isdir(shader_dir):
                os.mkdir(shader_dir)

            # ------------------------------------------------------
            # shader-patch
            field_descr = " <!--- H3D View Matrix Patch -->"
            fw('%s<field name="%s" type="SFMatrix4f" accessType="inputOutput" />%s\n' % (ident, H3D_VIEW_MATRIX, field_descr))
            frag_vars = ["uniform mat4 %s;" % H3D_VIEW_MATRIX]

            # annoying!, we need to track if some of the directional lamp
            # vars are children of the camera or not, since this adjusts how
            # they are patched.
            frag_uniform_var_map = {}

            h3d_material_route.append(
                    '<ROUTE fromNode="%s" fromField="glModelViewMatrix" toNode=%s toField="%s" />%s' %
                    (H3D_TOP_LEVEL, material_id, H3D_VIEW_MATRIX, field_descr))
            # ------------------------------------------------------

            for uniform in gpu_shader['uniforms']:
                if uniform['type'] == gpu.GPU_DYNAMIC_SAMPLER_2DIMAGE:
                    field_descr = " <!--- Dynamic Sampler 2d Image -->"
                    fw('%s<field name="%s" type="SFNode" accessType="inputOutput">%s\n' % (ident, uniform['varname'], field_descr))
                    writeImageTexture(ident + '\t', uniform['image'])
                    fw('%s</field>\n' % ident)

                elif uniform['type'] == gpu.GPU_DYNAMIC_LIGHT_DYNCO:
                    light_obj = uniform['lamp']
                    frag_uniform_var_map[uniform['varname']] = light_obj

                    if uniform['datatype'] == gpu.GPU_DATA_3F:  # should always be true!
                        light_obj_id = unique_name(light_obj, LA_ + light_obj.name, uuid_cache_light, clean_func=clean_def, sep="_")
                        light_obj_transform_id = unique_name(light_obj, light_obj.name, uuid_cache_object, clean_func=clean_def, sep="_")

                        value = '%.6f %.6f %.6f' % (global_matrix * light_obj.matrix_world).to_translation()[:]
                        field_descr = " <!--- Lamp DynCo '%s' -->" % light_obj.name
                        fw('%s<field name="%s" type="SFVec3f" accessType="inputOutput" value="%s" />%s\n' % (ident, uniform['varname'], value, field_descr))

                        # ------------------------------------------------------
                        # shader-patch
                        field_descr = " <!--- Lamp DynCo '%s' (shader patch) -->" % light_obj.name
                        fw('%s<field name="%s_transform" type="SFMatrix4f" accessType="inputOutput" />%s\n' % (ident, uniform['varname'], field_descr))

                        # transform
                        frag_vars.append("uniform mat4 %s_transform;" % uniform['varname'])
                        h3d_material_route.append(
                                '<ROUTE fromNode=%s fromField="accumulatedForward" toNode=%s toField="%s_transform" />%s' %
                                (suffix_quoted_str(light_obj_transform_id, _TRANSFORM), material_id, uniform['varname'], field_descr))

                        h3d_material_route.append(
                                '<ROUTE fromNode=%s fromField="location" toNode=%s toField="%s" /> %s' %
                                (light_obj_id, material_id, uniform['varname'], field_descr))
                        # ------------------------------------------------------

                    else:
                        assert(0)

                elif uniform['type'] == gpu.GPU_DYNAMIC_LIGHT_DYNCOL:
                    # odd  we have both 3, 4 types.
                    light_obj = uniform['lamp']
                    frag_uniform_var_map[uniform['varname']] = light_obj

                    lamp = light_obj.data
                    value = '%.6f %.6f %.6f' % (lamp.color * lamp.energy)[:]
                    field_descr = " <!--- Lamp DynColor '%s' -->" % light_obj.name
                    if uniform['datatype'] == gpu.GPU_DATA_3F:
                        fw('%s<field name="%s" type="SFVec3f" accessType="inputOutput" value="%s" />%s\n' % (ident, uniform['varname'], value, field_descr))
                    elif uniform['datatype'] == gpu.GPU_DATA_4F:
                        fw('%s<field name="%s" type="SFVec4f" accessType="inputOutput" value="%s 1.0" />%s\n' % (ident, uniform['varname'], value, field_descr))
                    else:
                        assert(0)

                elif uniform['type'] == gpu.GPU_DYNAMIC_LIGHT_DYNENERGY:
                    # not used ?
                    assert(0)

                elif uniform['type'] == gpu.GPU_DYNAMIC_LIGHT_DYNVEC:
                    light_obj = uniform['lamp']
                    frag_uniform_var_map[uniform['varname']] = light_obj

                    if uniform['datatype'] == gpu.GPU_DATA_3F:
                        light_obj = uniform['lamp']
                        value = '%.6f %.6f %.6f' % ((global_matrix * light_obj.matrix_world).to_quaternion() * mathutils.Vector((0.0, 0.0, 1.0))).normalized()[:]
                        field_descr = " <!--- Lamp DynDirection '%s' -->" % light_obj.name
                        fw('%s<field name="%s" type="SFVec3f" accessType="inputOutput" value="%s" />%s\n' % (ident, uniform['varname'], value, field_descr))

                        # route so we can have the lamp update the view
                        if h3d_is_object_view(scene, light_obj):
                            light_id = unique_name(light_obj, LA_ + light_obj.name, uuid_cache_light, clean_func=clean_def, sep="_")
                            h3d_material_route.append(
                                '<ROUTE fromNode=%s fromField="direction" toNode=%s toField="%s" />%s' %
                                        (light_id, material_id, uniform['varname'], field_descr))

                    else:
                        assert(0)

                elif uniform['type'] == gpu.GPU_DYNAMIC_OBJECT_VIEWIMAT:
                    frag_uniform_var_map[uniform['varname']] = None
                    if uniform['datatype'] == gpu.GPU_DATA_16F:
                        field_descr = " <!--- Object View Matrix Inverse '%s' -->" % obj.name
                        fw('%s<field name="%s" type="SFMatrix4f" accessType="inputOutput" />%s\n' % (ident, uniform['varname'], field_descr))

                        h3d_material_route.append(
                            '<ROUTE fromNode="%s" fromField="glModelViewMatrixInverse" toNode=%s toField="%s" />%s' %
                                    (H3D_TOP_LEVEL, material_id, uniform['varname'], field_descr))
                    else:
                        assert(0)

                elif uniform['type'] == gpu.GPU_DYNAMIC_OBJECT_IMAT:
                    frag_uniform_var_map[uniform['varname']] = None
                    if uniform['datatype'] == gpu.GPU_DATA_16F:
                        value = ' '.join(['%.6f' % f for v in (global_matrix * obj.matrix_world).inverted().transposed() for f in v])
                        field_descr = " <!--- Object Invertex Matrix '%s' -->" % obj.name
                        fw('%s<field name="%s" type="SFMatrix4f" accessType="inputOutput" value="%s" />%s\n' % (ident, uniform['varname'], value, field_descr))
                    else:
                        assert(0)

                elif uniform['type'] == gpu.GPU_DYNAMIC_SAMPLER_2DSHADOW:
                    pass  # XXX, shadow buffers not supported.

                elif uniform['type'] == gpu.GPU_DYNAMIC_SAMPLER_2DBUFFER:
                    frag_uniform_var_map[uniform['varname']] = None

                    if uniform['datatype'] == gpu.GPU_DATA_1I:
                        if 1:
                            tex = uniform['texpixels']
                            value = []
                            for i in range(0, len(tex) - 1, 4):
                                col = tex[i:i + 4]
                                value.append('0x%.2x%.2x%.2x%.2x' % (col[0], col[1], col[2], col[3]))

                            field_descr = " <!--- Material Buffer -->"
                            fw('%s<field name="%s" type="SFNode" accessType="inputOutput">%s\n' % (ident, uniform['varname'], field_descr))

                            ident += '\t'

                            ident_step = ident + (' ' * (-len(ident) + \
                            fw('%s<PixelTexture \n' % ident)))
                            fw(ident_step + 'repeatS="false"\n')
                            fw(ident_step + 'repeatT="false"\n')

                            fw(ident_step + 'image="%s 1 4 %s"\n' % (len(value), " ".join(value)))

                            fw(ident_step + '/>\n')

                            ident = ident[:-1]

                            fw('%s</field>\n' % ident)

                            #for i in range(0, 10, 4)
                            #value = ' '.join(['%d' % f for f in uniform['texpixels']])
                            # value = ' '.join(['%.6f' % (f / 256) for f in uniform['texpixels']])

                            #fw('%s<field name="%s" type="SFInt32" accessType="inputOutput" value="%s" />%s\n' % (ident, uniform['varname'], value, field_descr))
                            #print('test', len(uniform['texpixels']))
                    else:
                        assert(0)
                else:
                    print("SKIPPING", uniform['type'])

            file_frag = open(os.path.join(base_dst, shader_url_frag), 'w', encoding='utf-8')
            file_frag.write(gpu_shader['fragment'])
            file_frag.close()
            # patch it
            h3d_shader_glsl_frag_patch(os.path.join(base_dst, shader_url_frag),
                                       scene,
                                       frag_vars,
                                       frag_uniform_var_map,
                                       )

            file_vert = open(os.path.join(base_dst, shader_url_vert), 'w', encoding='utf-8')
            file_vert.write(gpu_shader['vertex'])
            file_vert.close()

            fw('%s<ShaderPart type="FRAGMENT" url=%s />\n' % (ident, quoteattr(shader_url_frag)))
            fw('%s<ShaderPart type="VERTEX" url=%s />\n' % (ident, quoteattr(shader_url_vert)))
            ident = ident[:-1]

            fw('%s</ComposedShader>\n' % ident)
    """

    def b2xImageTexture(image):
        image_id = unique_name(image, IM_ + image.name, uuid_cache_image, clean_func=clean_def, sep="_")

        if image.tag:
            imt = ImageTexture(USE=image_id)
        else:
            image.tag = True
            print(f"Saving {image.filepath}")
            image.save()
            imt = ImageTexture(DEF=image_id)

            # collect image paths, can load multiple
            # [relative, name-only, absolute]
            path_mode='AUTO'
            filepath = image.filepath
            filepath_full = bpy.path.abspath(filepath, library=image.library)
            filepath_ref = bpy_extras.io_utils.path_reference(filepath_full, base_src, base_dst, path_mode, "textures", copy_set, image.library)
            filepath_base = os.path.basename(filepath_full)

            images = [
                filepath_ref,
                filepath_base,
            ]
            if path_mode != 'RELATIVE':
                images.append(filepath_full)

            images = [f.replace('\\', '/') for f in images]
            images = [f for i, f in enumerate(images) if f not in images[:i]]

            #fw(ident_step + "url='%s'\n" % ' '.join(['%s' % escape(f) for f in images]))
            imt.url = ['%s' % escape(f) for f in images]
            return imt

    def b2xBackground(world):

        if world is None:
            return None

        # note, not re-used
        world_id = unique_name(world, WO_ + world.name, uuid_cache_world, clean_func=clean_def, sep="_")

        # XXX World changed a lot in 2.8... For now do minimal get-it-to-work job.
        # ~ blending = world.use_sky_blend, world.use_sky_paper, world.use_sky_real

        # ~ grd_triple = clamp_color(world.horizon_color)
        # ~ sky_triple = clamp_color(world.zenith_color)
        # ~ mix_triple = clamp_color((grd_triple[i] + sky_triple[i]) / 2.0 for i in range(3))

        blending = (False, False, False)

        grd_triple = clamp_color(world.color)
        sky_triple = clamp_color(world.color)
        mix_triple = clamp_color((grd_triple[i] + sky_triple[i]) / 2.0 for i in range(3))

        bg = Background(DEF= world_id)
        # No Skytype - just Hor color
        if blending == (False, False, False):
            bg.groundColor = grd_triple
            bg.skyColor = grd_triple
        # Blend Gradient
        elif blending == (True, False, False):
            bg.groundColor = (grd_triple + mix_triple)
            bg.skyColor = (sky_triple + mix_triple)
            bg.groundAngle = [1.57]
            bg.skyAngle = [1.57]
        # Blend+Real Gradient Inverse
        elif blending == (True, False, True):
            bg.groundColor = (sky_triple + grd_triple)
            bg.skyColor = (sky_triple + grd_triple + sky_triple)
            bg.groundAngle = [1.57]
            bg.skyAngle = [1.57,3.14159] 
        # Paper - just Zen Color
        elif blending == (False, False, True):
            bg.groundColor = sky_triple
            bg.skyColor = sky_triple
        # Blend+Real+Paper - komplex gradient
        elif blending == (True, True, True):
            bg.groundColor = (sky_triple + grd_triple)
            bg.skyColor = (sky_triple + grd_triple)
            bg.groundAngle = [1.57]
            bg.skyAngle = [1.57]

        # Any Other two colors
        else:
            bg.groundColor = grd_triple
            bg.skyColor = sky_triple

        for tex in bpy.data.textures:
            if tex.type == 'IMAGE' and tex.image:
                namemat = tex.name
                pic = tex.image
                basename = bpy.path.basename(pic.filepath)

                if namemat == 'back':
                    bg.backUrl = basename
                elif namemat == 'bottom':
                    bg.bottomkUrl = basename
                elif namemat == 'front':
                    bg.frontUrl = basename
                elif namemat == 'left':
                    bg.leftUrl = basename
                elif namemat == 'right':
                    bg.rightUrl = basename
                elif namemat == 'top':
                    bg.topkUrl = basename

        return bg

    # -------------------------------------------------------------------------
    # blender to x3d Object Hierarchy (recursively called)
    # -------------------------------------------------------------------------
    def b2x_object(obj_main_parent, obj_main, obj_children, x3dmodel_scene):
        matrix_fallback = mathutils.Matrix()
        world = scene.world
        derived_dict = create_derived_objects(depsgraph, [obj_main])
        derived = derived_dict.get(obj_main)

        top = Group()
        bottom = Group()
        if export_settings['x3dv_use_hierarchy']: 
            obj_main_matrix_world = obj_main.matrix_world
            if obj_main_parent:
                obj_main_matrix = obj_main_parent.matrix_world.inverted(matrix_fallback) @ obj_main_matrix_world
            else:
                obj_main_matrix = obj_main_matrix_world
            obj_main_matrix_world_invert = obj_main_matrix_world.inverted(matrix_fallback)

            obj_main_id = unique_name(obj_main, obj_main.name, uuid_cache_object, clean_func=clean_def, sep="_")

            trans = b2xTransform(obj_main_matrix if obj_main_parent else global_matrix @ obj_main_matrix, suffix_str(obj_main_id, _TRANSFORM))
            top.children.append(trans)
            bottom = trans
        # Set here just incase we dont enter the loop below.
        is_dummy_tx = False
        after = []

        for obj, obj_matrix in (() if derived is None else derived):
            obj_type = obj.type

            if export_settings['x3dv_use_hierarchy']:
                # make transform node relative
                obj_matrix = obj_main_matrix_world_invert @ obj_matrix
            else:
                obj_matrix = global_matrix @ obj_matrix

            # H3D - use for writing a dummy transform parent
            is_dummy_tx = False
            node = None
            children_processed = False
            if obj_type == 'CAMERA':
                node = b2xViewpoint(obj, obj_matrix)

                """
                if use_h3d and scene.camera == obj:
                    view_id = uuid_cache_view[obj]
                    fw('%s<Transform DEF="%s">\n' % (ident, H3D_CAMERA_FOLLOW))
                    h3d_material_route.extend([
                        '<ROUTE fromNode="%s" fromField="totalPosition" toNode="%s" toField="translation" />' % (view_id, H3D_CAMERA_FOLLOW),
                        '<ROUTE fromNode="%s" fromField="totalOrientation" toNode="%s" toField="rotation" />' % (view_id, H3D_CAMERA_FOLLOW),
                        ])
                    is_dummy_tx = True
                    ident += '\t'
               """
                if node != None:
                    bottom.children.append(node)

            elif obj_type in {'MESH', 'CURVE', 'SURFACE', 'FONT'}:
                if (obj_type != 'MESH') or (export_settings['x3dv_use_mesh_modifiers'] and obj.is_modified(scene, 'PREVIEW')):
                    obj_for_mesh = obj.evaluated_get(depsgraph) if export_settings['x3dv_use_mesh_modifiers'] else obj
                    try:
                        me = obj_for_mesh.to_mesh()
                    except:
                        me = None
                    do_remove = True
                else:
                    me = obj.data
                    do_remove = False

                if me is not None:
                    # ensure unique name, we could also do this by
                    # postponing mesh removal, but clearing data - TODO
                    if do_remove:
                        me_name_new = me_name_original = obj.name.rstrip("1234567890").rstrip(".")
                        count = 0
                        while me_name_new in mesh_name_set:
                            me_name_new = "%.17s.%03d" % (me_name_original, count)
                            count += 1
                        mesh_name_set.add(me_name_new)
                        mesh_name = me_name_new
                        del me_name_new, me_name_original, count
                    else:
                        mesh_name = me.name
                    # done

                    node = b2xIndexedFaceSet(obj, me, mesh_name, obj_matrix, world)
                    if node != None:
                        bottom.children.append(node)
                    # free mesh created with to_mesh()
                    if do_remove:
                        obj_for_mesh.to_mesh_clear()

            elif obj_type == 'LIGHT':
                data = obj.data
                datatype = data.type
                # print('obj type is LIGHT, datatype %s' % datatype)
                if datatype == 'POINT':
                    node = b2xPointLight( obj, obj_matrix, data, world)
                elif datatype == 'SPOT':
                    node = b2xSpotLight( obj, obj_matrix, data, world)
                elif datatype == 'SUN':
                    node = b2xDirectionalLight( obj, obj_matrix, data, world)
                else:
                    node = b2xDirectionalLight( obj, obj_matrix, data, world)
                if node != None:
                    bottom.children.append(node)
            elif obj_type == 'ARMATURE':
                data = obj.data
                node = b2xArmature(obj, obj_main, obj_children, obj_matrix, data, world)
                prior_after = after
                for obj_child, obj_child_children in obj_children:
                    [ x3dnodelist, after ] = b2x_object(obj_main, obj_child, obj_child_children, x3dmodel_scene)
                    for a in after:
                        prior_after.append(a)
                    if x3dnodelist:
                        for x3dnode in x3dnodelist:
                            x3dnode.scale = (1, 1, 1)
                            # x3dnode.rotation = (0, 1, 0, 3.1416)
                            node.skin.append(x3dnode)
                            for coord in b2xFindCoordinate(x3dnode):
                                # TODO handle skinCoord before skin
                                node.skinCoord = Coordinate(USE=coord)  # only one SFNode is allowed.
                after = prior_after
                if node != None:
                    bottom.children.append(node)
                interpolators = b2xHAnimNode(obj, None, obj.name, "HAnimInterpolators")
                print(f"Writing {len(interpolators)} nodes for animations.")
                for i in interpolators:
                    if isinstance(i, list):
                        print(f"Writing {len(i)} sub-nodes for animations.")
                        for j in i:
                            after.append(j)
                    else:
                        print(f"Writing {i} sub-node for animations.")
                        after.append(i)
                children_processed = True
            else:
                print("Info: Ignoring [%s], object type [%s] not handle yet" % (obj.name,obj_type))
                # pass

        # ---------------------------------------------------------------------
        # write out children recursively
        # ---------------------------------------------------------------------
        if not children_processed:
            prior_after = after
            for obj_child, obj_child_children in obj_children:
                # no need to combine after's
                [ x3dnodelist, after ] = b2x_object(obj_main, obj_child, obj_child_children, x3dmodel_scene)
                if x3dnodelist:
                    for x3dnode in x3dnodelist:
                        bottom.children.append(x3dnode)
                if after:
                    for a in after:
                        prior_after.append(a)
            after = prior_after
        if is_dummy_tx:
            is_dummy_tx = False

        print(f"returning {len(after)} sub-nodes for animations.")
        return [ top.children, after ]

    # -------------------------------------------------------------------------
    # Main Export Function
    # -------------------------------------------------------------------------
    def export_main():
        world = scene.world
        x3dmodel = X3D(profile='Immersive',version='4.0')
        x3dmodel.Scene = Scene()
        # tag un-exported IDs
        bpy.data.meshes.tag(False)
        bpy.data.materials.tag(False)
        bpy.data.images.tag(False)

        if export_settings['x3dv_selected']:
            objects = [obj for obj in view_layer.objects if obj.visible_get(view_layer=view_layer)
                       and obj.select_get(view_layer=view_layer)]
        else:
            objects = [obj for obj in view_layer.objects if obj.visible_get(view_layer=view_layer)]

        print('Info: starting X3D export to %r...' % export_settings['x3dv_filepath'])

        x3dmodel.head = b2xHeader()

        x3dmodel.Scene.children.append( b2xNavigationInfo(any(obj.type == 'LIGHT' for obj in objects)) )
        x3dmodel.Scene.children.append( b2xBackground( world) )

        fog = b2xFog(world)
        if(fog):
            x3dmodel.Scene.children.append(fog)

        if export_settings['x3dv_use_hierarchy']: 
            objects_hierarchy = build_hierarchy(objects)
        else:
            objects_hierarchy = ((obj, []) for obj in objects)

        # skeleton visualization
        x3dmodel.Scene.children.append(
            Transform( children=[
                Shape(
                    DEF="SiteShape",
                    geometry=Box(size = (0.05, 0.05, 0.05)),
                    appearance=Appearance(
                        material=Material(
                            diffuseColor = (0, 0, 1),
                            transparency = 0
                        ))
                )
            ])
        )
        #x3dmodel.Scene.children.append(
        #    Transform( children=[
        #        Shape(appearance=Appearance(lineProperties=LineProperties(linewidthScaleFactor=5)),
        #              geometry=LineSet(
        #                vertexCount=2,
        #                coord=Coordinate(point=MFVec3f([(0, 0, 0), (0, 0, 0)])),
        #                color=ColorRGBA(
        #                    DEF='SegmentLineColor',
        #                    color=MFColorRGBA([(1.0, 1.0, 1.0, 0.0), (1.0, 1.0, 1.0, 0.0)])
        #                )
        #        ))
        #    ])
        #)
        x3dmodel.Scene.children.append(
            Transform( children=[
                Shape(
                    DEF="JointShape",
                    geometry=Sphere(radius=0.06),
                    appearance=Appearance(
                        DEF="JointAppearance",
                        material=Material(
                            diffuseColor = (1, 0.5, 0),
                            transparency = 0.5
                        ))
                )
            ])
        )

        for obj_main, obj_main_children in objects_hierarchy:
            [ x3dnodelist, after ] = b2x_object(None, obj_main, obj_main_children, x3dmodel.Scene)
            if x3dnodelist:
                for x3dnode in x3dnodelist:
                    x3dmodel.Scene.children.append(x3dnode)
            if after:
                print(f"appending {len(after)} sub-nodes for scene children.")
                for a in after:
                    x3dmodel.Scene.children.append(a)
        # swap_USEbeforeDEF(node=x3dmodel.Scene)
        USEdict = {}
        DEFdict = {}
        USEbeforeDEFdict = {}
        return x3dmodel


    x3dmodel = export_main()

    # -------------------------------------------------------------------------
    # global cleanup
    # -------------------------------------------------------------------------

    #if use_h3d:
    #    bpy.data.materials.remove(gpu_shader_dummy_mat)

    # copy all collected files.
    # print(copy_set)
    bpy_extras.io_utils.path_reference_copy(copy_set)

    print('Info: finished X3D export to %r' % export_settings['x3dv_filepath']) 
    return x3dmodel

##########################################################
# Callbacks, needed before Main
##########################################################


def gzip_open_utf8(filepath, mode):
    """Workaround for py3k only allowing binary gzip writing"""

    import gzip

    # need to investigate encoding
    file = gzip.open(filepath, mode)
    write_real = file.write

    def write_wrap(data):
        return write_real(data.encode("utf-8"))

    file.write = write_wrap

    return file


def save_OLD(context,x3dv_export_settings):
    """
         filepath,
         *,
         use_selection=True,
         use_mesh_modifiers=False,
         use_triangulate=False,
         use_normals=False,
         use_compress=False,
         use_hierarchy=True,
         use_h3d=False,
         global_matrix=None,
         path_mode='AUTO',
         name_decorations=True
         ):
    """
    export_settings = x3dv_export_settings
    #bpy.path.ensure_ext(filepath, '.x3dz' if use_compress else '.x3d')

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')


    if global_matrix is None:
        global_matrix = mathutils.Matrix()
    export_settings['x3dv_global_matrix'] = global_matrix
    x3dstream = export()
    """
           file,
           global_matrix,
           context.evaluated_depsgraph_get(),
           context.scene,
           context.view_layer,
           use_mesh_modifiers=use_mesh_modifiers,
           use_selection=use_selection,
           use_triangulate=use_triangulate,
           use_normals=use_normals,
           use_hierarchy=use_hierarchy,
           use_h3d=use_h3d,
           path_mode=path_mode,
           name_decorations=name_decorations,
           )
    """
    if export_settings['x3dv_compress']:
        file = gzip_open_utf8(filepath, 'w')
    else:
        file = open(filepath, 'w', encoding='utf-8')

    file.write(stream)
    file.close()

    return {'FINISHED'}

def save(context,export_settings):
    """Start the x3dv export and saves to content file."""

    if bpy.context.active_object is not None:
        if bpy.context.active_object.mode != "OBJECT": # For linked object, you can't force OBJECT mode
            bpy.ops.object.mode_set(mode='OBJECT')

    original_frame = bpy.context.scene.frame_current
    if not export_settings['x3dv_current_frame']:
        bpy.context.scene.frame_set(0)

    __notify_start(context)
    start_time = time.time()
    x3dv_round_precision = export_settings['x3dv_round_precision']

    #x3dmodel = blender2x3d(export_settings) #test export of procedurally declared test scene
    x3dmodel = export(context, export_settings)
    format = export_settings['x3dv_format']
    blob = None
    if(format=='X3D'):
        blob = x3dmodel.XML()
    elif(format=='X3DV'):
        blob = x3dmodel.VRML(VRML97=False)
    elif(format=='HTML'):
        blob = x3dmodel.X3DOM()
    elif(format=='JSON'):
        blob = x3dmodel.JSON()
    else:
        print("No file format given")
    __write_file(blob,export_settings)


    end_time = time.time()
    __notify_end(context, end_time - start_time)

    if not export_settings['x3dv_current_frame']:
        bpy.context.scene.frame_set(int(original_frame))
    return {'FINISHED'}

"""
def blender2x3d(export_settings):
    print('__export(settings)')
    x3dmodel = X3D()
    x3dmodel = X3D(profile='Immersive',version='3.3',
      head=head(
        children=[
        meta(content='HelloWorld.x3d',name='title'),
        meta(content='Simple X3D scene example: Hello World!',name='description'),
        meta(content='30 October 2000',name='created'),
        meta(content='31 October 2019',name='modified'),
        meta(content='Don Brutzman',name='creator'),
        meta(content='HelloWorld.tall.png',name='Image'),
        meta(content='http://en.wikipedia.org/wiki/Hello_world',name='reference'),
        meta(content='https://en.wikipedia.org/wiki/Hello#.22Hello.2C_World.22_computer_program',name='reference'),
        meta(content='https://en.wikipedia.org/wiki/"Hello,_World!"_program',name='reference'),
        meta(content='http://en.wikibooks.org/w/index.php?title=Computer_Programming/Hello_world',name='reference'),
        meta(content='http://www.HelloWorldExample.net',name='reference'),
        meta(content='http://www.web3D.org',name='reference'),
        meta(content='http://www.web3d.org/realtime-3d/news/internationalization-x3d',name='reference'),
        meta(content='http://www.web3d.org/x3d/content/examples/HelloWorld.x3d',name='reference'),
        meta(content='http://X3dGraphics.com/examples/X3dForAdvancedModeling/HelloWorldScenes',name='reference'),
        meta(content='http://X3dGraphics.com/examples/X3dForWebAuthors/Chapter01TechnicalOverview/HelloWorld.x3d',name='identifier'),
        meta(content='http://www.web3d.org/x3d/content/examples/license.html',name='license'),
        meta(content='X3D-Edit 3.3, https://savage.nps.edu/X3D-Edit',name='generator'),
        #  Alternate encodings: VRML97, X3D ClassicVRML Encoding, X3D Compressed Binary Encoding (CBE), X3DOM, JSON 
        meta(content='HelloWorld.wrl',name='reference'),
        meta(content='HelloWorld.x3dv',name='reference'),
        meta(content='HelloWorld.x3db',name='reference'),
        meta(content='HelloWorld.xhtml',name='reference'),
        meta(content='HelloWorld.json',name='reference')]),
      Scene=Scene(
        #  Example scene to illustrate X3D nodes and fields (XML elements and attributes) 
        children=[
        WorldInfo(title='Hello World!'),
        WorldInfo(title="Hello ' apostrophe 1"),
        WorldInfo(title="Hello ' apostrophe 2"),
        WorldInfo(title='Hello " quotation mark 3'),
        WorldInfo(title='Hello " quotation mark 4'),
        MetadataSet(name="items'",
          value=[
          MetadataInteger(name='one',value=[1]),
          MetadataInteger(name='two',value=[2])]),
        Group(
          children=[
          Viewpoint(DEF='ViewUpClose',centerOfRotation=(0,-1,0),description='Hello world!',position=(0,-1,7)),
          #  insert commas to test removal when converted to ttl 
          Transform(DEF='TestWhitespaceCommas',rotation=(0,1,0,3),
            children=[
            Shape(
              geometry=Sphere(),
              appearance=Appearance(
                material=Material(DEF='MaterialLightBlue',diffuseColor=(0.1,0.5,1)),
                texture=ImageTexture(DEF='ImageCloudlessEarth',url=["earth-topo.png","earth-topo.jpg","earth-topo-small.gif","http://www.web3d.org/x3d/content/examples/Basic/earth-topo.png","http://www.web3d.org/x3d/content/examples/Basic/earth-topo.jpg","http://www.web3d.org/x3d/content/examples/Basic/earth-topo-small.gif"])))]),
          Transform(translation=(0,-2,0),
            children=[
            Shape(
              geometry=Text(DEF='TextMessage',string=["Hello","world!"],
                fontStyle=FontStyle(justify=["MIDDLE","MIDDLE"])),
              appearance=Appearance(
                material=Material(USE='MaterialLightBlue')))])])])
    ) # X3D model complete  

    return x3dmodel
"""

def __is_empty_collection(value):
    return (isinstance(value, dict) or isinstance(value, list)) and len(value) == 0


def __write_file(blob, export_settings):
    try:
        print('x3dv_io_export.save_x3d(data)')
        f = open(export_settings['x3dv_filepath'], "w+")
        f.write(blob)
        f.close()

    except AssertionError as e:
        _, _, tb = sys.exc_info()
        traceback.print_tb(tb)  # Fixed format
        tb_info = traceback.extract_tb(tb)
        for tbi in tb_info:
            filename, line, func, text = tbi
            print_console('ERROR', 'An error occurred on line {} in statement {}'.format(line, text))
        print_console('ERROR', str(e))
        raise e


def __notify_start(context):
    print_console('INFO', 'Starting x3dv export')
    context.window_manager.progress_begin(0, 100)
    context.window_manager.progress_update(0)


def __notify_end(context, elapsed):
    print_console('INFO', 'Finished x3dv export in {} s'.format(elapsed))
    context.window_manager.progress_end()
    print_newline()
