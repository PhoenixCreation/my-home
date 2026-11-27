"""Export the web model and embed it in index.html (run in Blender after build + furniture scripts).

Exports the apartment meshes, including the ceiling used in Walk mode, except labels and the floor
above. Furniture roots and hinges travel with their custom properties in glTF extras. The script
replaces the MODEL_BASE64 string in index.html.
"""
import bpy, base64, os, re, sys

ROOT = (os.path.dirname(bpy.data.filepath) if bpy.data.filepath
        else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "model_scripts"))
from wall_finishes import prepare_wall_finishes
prepare_wall_finishes()

SKIP = {"Labels", "Context Above (hidden)", "Photo Cameras"}
GLB = os.path.join(bpy.app.tempdir or "/tmp", "I-601_web.glb")

keep = []
for c in bpy.data.collections["I-601"].children:
    if c.name in SKIP:
        continue
    for o in c.objects:
        if o.type == "MESH" or o.get("furniture") or o.get("fold_hinge"):
            keep.append(o)

if bpy.context.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.select_all(action="DESELECT")
hidden = [(o, o.hide_get(), o.hide_viewport) for o in keep]
for o in keep:
    o.hide_viewport = False
bpy.context.view_layer.update()
for o in keep:
    if o.hide_get():
        o.hide_set(False)
    o.select_set(True)
bpy.context.view_layer.objects.active = keep[0]

try:
    bpy.ops.export_scene.gltf(
        filepath=GLB, export_format="GLB", use_selection=True, export_extras=True,
        export_yup=True, export_apply=False, export_cameras=False, export_lights=False,
        export_image_format="AUTO", export_animations=False)
finally:
    for o, was_hidden, viewport_hidden in hidden:
        if was_hidden or viewport_hidden:
            o.select_set(False)
        if was_hidden:
            o.hide_set(True)
        o.hide_viewport = viewport_hidden

data = open(GLB, "rb").read()
html_path = os.path.join(ROOT, "index.html")
html = open(html_path, encoding="utf-8").read()
b64 = base64.b64encode(data).decode("ascii")
html, n = re.subn(r"const MODEL_BASE64 = '[^']*';", lambda m: f"const MODEL_BASE64 = '{b64}';", html, count=1)
assert n == 1, "MODEL_BASE64 not found in index.html"
open(html_path, "w", encoding="utf-8").write(html)
print(f"exported {len(keep)} objects, {len(data) / 1024:.0f} KB glb -> index.html")
