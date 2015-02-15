import bpy
import os
import json
import sys


# Rmove the default cube
for ob in bpy.context.scene.objects:
    ob.select = ob.type == 'MESH' and ob.name.startswith("Cube")
bpy.ops.object.delete()


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


def create_plane_for_image(location, rotation, image):

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

    plane.data.uv_textures.new()
    plane.data.materials.append(material)
    plane.data.uv_textures[0].data[0].image = img


directory = sys.argv[1]

print "Working on directory %s" % directory

with open(os.path.join(directory, "images.json"), "rb") as f:
    data = json.load(f)

for i, image in enumerate(data["images"]):
    create_plane_for_image(
        location=(i, i, i),
        rotation=(0, 0, 0),
        image=image
    )

bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(directory, "export.blend"))
