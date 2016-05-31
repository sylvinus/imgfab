import bpy
import os
import json
import sys
import math


def create_material_for_texture(texture):
    # look for material with the needed texture
    for material in bpy.data.materials:
        slot = material.texture_slots[0]
        if slot and slot.texture == texture:
            return material

    # if no material found: create one
    name_compat = bpy.path.display_name_from_filepath(texture.image.filepath)
    material = bpy.data.materials.new(name=name_compat)
    slot = material.texture_slots.add()
    slot.texture = texture
    slot.texture_coords = 'UV'
    return material


def create_image_texture(image):
    fn_full = os.path.normpath(bpy.path.abspath(image.filepath))

    # look for texture with importsettings
    for texture in bpy.data.textures:
        if texture.type == 'IMAGE':
            tex_img = texture.image
            if (tex_img is not None) and (tex_img.library is None):
                fn_tex_full = os.path.normpath(bpy.path.abspath(tex_img.filepath))
                if fn_full == fn_tex_full:
                    return texture

    # if no texture is found: create one
    name_compat = bpy.path.display_name_from_filepath(image.filepath)
    texture = bpy.data.textures.new(name=name_compat, type='IMAGE')
    texture.image = image
    return texture


def create_plane_for_image(location, rotation, scale, image):

    bpy.ops.mesh.primitive_plane_add(
        location=location,
        rotation=rotation
    )
    plane = bpy.context.object

    if plane.mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    img = bpy.data.images.load(image["filepath"])

    texture = create_image_texture(img)
    material = create_material_for_texture(texture)
    material.specular_intensity = 0

    plane.data.uv_textures.new()
    plane.data.materials.append(material)
    plane.data.uv_textures[0].data[0].image = img

    if scale:
        plane.scale = scale


def setup_scene(layout):

    if layout in ["cube", "wall"]:

        # Rmove the default cube
        for ob in bpy.context.scene.objects:
            ob.select = (ob.type == 'MESH' or ob.type == 'LAMP')
            bpy.ops.object.delete()

        # Add 2 HEMI lamps with opposite positions for 100% lighting. + 1 for walls :/

        for lamp_i in [0, 1, 2]:
            lamp_data = bpy.data.lamps.new(name="Lamp%s" % lamp_i, type='HEMI')
            lamp_object = bpy.data.objects.new(name="Lamp%s" % lamp_i, object_data=lamp_data)
            bpy.context.scene.objects.link(lamp_object)
            lamp_object.location = [
                [5, 5, 5],
                [-5, -5, -5],
                [0, -5, 0]
            ][lamp_i]
            lamp_object.rotation_euler = [
                [-math.pi / 4, math.pi / 4, 0],
                [5 * math.pi / 4, 0, 3 * math.pi / 4],
                [math.pi / 2, 0, 0]
            ][lamp_i]

    elif layout == "louvre":
        bpy.ops.wm.open_mainfile(filepath="3dmodels/louvre.blend")
    elif layout == "artgallery":
        bpy.ops.wm.open_mainfile(filepath="3dmodels/artgallery/model.blend")


directory = sys.argv[-1]

print("Working on directory %s" % directory)

with open(os.path.join(directory, "images.json"), "r") as f:
    data = json.load(f)

layout = data.get("layout", "cube")


setup_scene(layout)

images_count = len(data["images"])

for i, image in enumerate(data["images"]):
    location = None
    rotation = None
    scale = None

    if layout == "cube":
        location = [
            [1, 0, 0],
            [0, 1, 0],
            [-1, 0, 0],
            [0, -1, 0],
            [0, 0, -1],
            [0, 0, 1],
        ][i % 6]

        rotation = [
            [math.pi / 2, 0, math.pi / 2],
            [- math.pi / 2, math.pi, 0],
            [math.pi / 2, 0, - math.pi / 2],
            [math.pi / 2, 0, 0],
            [math.pi, math.pi, 0],
            [0, 0, 0]
        ][i % 6]

    elif layout == "wall":

        rows = 3
        cols = math.ceil(images_count / 3)

        margin = 0.1

        row = i % rows
        col = int(i / rows)

        print("Image %s, row=%s col=%s" % (i, row, col))

        max_angle = math.pi * 2 / 3
        base_angle = max_angle / (cols + 1)

        angle = (math.pi - ((math.pi - max_angle) / 2) - base_angle) - (base_angle * col)
        height = (row - 1) * (2 + 2 * margin)

        print("Angles: max=%s, base=%s i=%s" % (max_angle, base_angle, angle))

        distance = 1.0 / (math.tan(base_angle * (1 - margin) / 2))

        offset = distance / 2

        location = (distance * math.cos(angle), distance * math.sin(angle) - offset, height)
        rotation = (math.pi / 2, 0, (math.pi / 2) + angle)

    elif layout == "louvre":

        face = int(i / 3)
        pos = i % 3
        size = i % 2

        # Space between picture centers
        spacing1 = 0.82
        spacing2 = 0.798

        # Distance to the walls
        wall1 = 1.196  # 1.1995
        wall2 = 1.225  # 1.228

        # Height of the centers
        height = -0.426

        rotation = (3 * math.pi / 2, 2 * math.pi / 2, (face + 1) * math.pi / 2)

        if size == 0:
            scale = (0.232, 0.232, 0.232)
        else:
            scale = (0.175, 0.175, 0.175)

        location = [
            (wall1, spacing1, height),
            (wall1, 0, height),
            (wall1, -spacing1, height),

            (spacing2, wall2, height),
            (0, wall2, height),
            (-spacing2, wall2, height),

            (-wall1, -spacing1, height),
            (-wall1, 0, height),
            (-wall1, spacing1, height),

            (spacing2, -wall2, height),
            (0, -wall2, height),
            (-spacing2, -wall2, height)
        ][i]

    elif layout == "artgallery":
        old_img = bpy.data.textures['Picture%02d' % (i + 1)].image
        bpy.data.textures['Picture%02d' % (i + 1)].image = None
        bpy.data.images.remove(old_img)
        bpy.data.textures['Picture%02d' % (i + 1)].image = bpy.data.images.load(image["filepath"])

    if location:

        create_plane_for_image(
            location=location,
            rotation=rotation,
            scale=scale,
            image=image
        )

bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(directory, "export.blend"))
