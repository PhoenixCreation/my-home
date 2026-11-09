import bpy, json, math, os
from mathutils import Matrix, Vector
cams = json.load(open("/run/media/phoenix/P3/Projects/Sun Footprints/I-601_photo_cameras.json"))
IMG_DIR = "/run/media/phoenix/P3/Projects/Sun Footprints/real_images"
root = bpy.data.objects.get("I-601_ROOT")
coll = bpy.data.collections.get("Photo Cameras")
if coll is None:
    coll = bpy.data.collections.new("Photo Cameras")
    bpy.data.collections["I-601"].children.link(coll)
for o in list(coll.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
scene.render.resolution_x, scene.render.resolution_y = 1280, 721
scene.render.resolution_percentage = 100
for name, c in cams.items():
    R = Matrix(c["R_cw"])            # rows: cv cam axes (x right, y down, z fwd) in world
    r, d, f = R[0], R[1], R[2]
    M = Matrix((r, -d, -f)).transposed().to_4x4()
    M.translation = Vector(c["C"])
    cd = bpy.data.cameras.new("PhotoCam_" + name)
    cd.sensor_fit = "HORIZONTAL"
    cd.sensor_width = 36.0
    cd.lens = c["f_px"] * 36.0 / 1280.0
    cd.clip_start = 0.3
    cd.show_background_images = True
    img_path = os.path.join(IMG_DIR, name + ".jpg")
    img = bpy.data.images.load(img_path, check_existing=True)
    bg = cd.background_images.new()
    bg.image = img
    bg.alpha = 0.6
    try:
        bg.display_depth = "FRONT"
    except Exception:
        pass
    ob = bpy.data.objects.new("PhotoCam_" + name, cd)
    coll.objects.link(ob)
    ob.matrix_world = M
    if root:
        ob.parent = root
        ob.matrix_parent_inverse = root.matrix_world.inverted()
print("cams", len(cams))
