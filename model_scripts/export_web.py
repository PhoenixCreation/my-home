"""Export the web model and embed it in index.html (run in Blender after build + furniture scripts).

Exports every visible mesh of the I-601 collection except labels, the ceiling, the floor above and the
photo cameras, plus the furniture empties (their custom properties travel as glTF extras), then
replaces the MODEL_BASE64 string in index.html.
"""
import bpy, base64, os, re

ROOT = (os.path.dirname(bpy.data.filepath) if bpy.data.filepath
        else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKIP = {"Labels", "Ceiling (hidden)", "Context Above (hidden)", "Photo Cameras"}
GLB = os.path.join(bpy.app.tempdir or "/tmp", "I-601_web.glb")

keep = []
for c in bpy.data.collections["I-601"].children:
    if c.name in SKIP:
        continue
    for o in c.objects:
        if o.type == "MESH" or (o.type == "EMPTY" and o.get("furniture")):
            keep.append(o)

if bpy.context.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.select_all(action="DESELECT")
for o in keep:
    o.hide_set(False)
    o.select_set(True)
bpy.context.view_layer.objects.active = keep[0]

bpy.ops.export_scene.gltf(
    filepath=GLB, export_format="GLB", use_selection=True, export_extras=True,
    export_yup=True, export_apply=False, export_cameras=False, export_lights=False,
    export_image_format="AUTO", export_animations=False)

data = open(GLB, "rb").read()
html_path = os.path.join(ROOT, "index.html")
html = open(html_path, encoding="utf-8").read()
b64 = base64.b64encode(data).decode("ascii")
html, n = re.subn(r"const MODEL_BASE64 = '[^']*';", lambda m: f"const MODEL_BASE64 = '{b64}';", html, count=1)
assert n == 1, "MODEL_BASE64 not found in index.html"
open(html_path, "w", encoding="utf-8").write(html)
print(f"exported {len(keep)} objects, {len(data) / 1024:.0f} KB glb -> index.html")
