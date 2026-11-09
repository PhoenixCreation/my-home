"""Build flat I-601 (Block I, unit type 201-1401) in Blender.

Local frame (see I-601_3D_Spec.md): mm, origin = outer bottom-left corner of Bedroom 1,
+x towards kitchen, +y towards drawing room, z = 0 at structural slab top (SSL), FFL = +80.
Blender units: metres. Re-running the script rebuilds everything.
"""
import bpy, bmesh, math

S = 0.001
FFL = 80
BEAM = 2375          # beam bottom = door/window head
SOFFIT = 2800        # underside of slab above (2950 floor-to-floor, ~150 slab)
FTF = 2950
LEDGE_TOP = -410
LEDGE_BOT = -535
ABOVE_BOT = FTF + LEDGE_BOT   # underside of the identical ledge one floor above

# ---------------------------------------------------------------- cleanup
def purge_collection(c):
    for ch in list(c.children):
        purge_collection(ch)
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(c)

if "I-601" in bpy.data.collections:
    purge_collection(bpy.data.collections["I-601"])
for n in ("Cube",):
    if n in bpy.data.objects and bpy.data.objects[n].type == "MESH":
        bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
for m in list(bpy.data.meshes):
    if m.users == 0:
        bpy.data.meshes.remove(m)
for c in list(bpy.data.curves):
    if c.users == 0:
        bpy.data.curves.remove(c)
for c in list(bpy.data.cameras):
    if c.users == 0 and c.name.startswith("PhotoCam_"):
        bpy.data.cameras.remove(c)
for m in list(bpy.data.materials):
    if m.name.startswith("I601_"):
        bpy.data.materials.remove(m)

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0

root_coll = bpy.data.collections.new("I-601")
scene.collection.children.link(root_coll)
COLL = {}
for name in ("Structure", "Finishes", "Windows & Doors", "Ledges & Railings", "Kitchen & Toilets",
             "Labels", "Common Areas", "Ceiling (hidden)", "Context Above (hidden)"):
    c = bpy.data.collections.new(name)
    root_coll.children.link(c)
    COLL[name] = c

root = bpy.data.objects.new("I-601_ROOT", None)
root.empty_display_type = "ARROWS"
root.empty_display_size = 1.0
root["note"] = ("Sheet orientation (Block J copy). For real Block I orientation rotate this empty "
                "180 deg about Z around the flat centre (4.1145, 4.5915).")
COLL["Structure"].objects.link(root)

# ---------------------------------------------------------------- materials
def set_input(node, ident, value):
    for s in node.inputs:
        if s.identifier == ident:
            try:
                s.default_value = value
            except Exception:
                pass
            return

def mat(name, rgb, rough=0.6, metal=0.0, alpha=1.0, transm=0.0):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    set_input(p, "Base Color", (*rgb, 1.0))
    set_input(p, "Roughness", rough)
    set_input(p, "Metallic", metal)
    set_input(p, "Alpha", alpha)
    set_input(p, "Transmission Weight", transm)
    m.diffuse_color = (*rgb, alpha)
    m.roughness = rough
    m.metallic = metal
    if alpha < 1.0:
        for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
            try:
                setattr(m, attr, val)
            except Exception:
                pass
    return m

M = dict(
    wall=mat("I601_Wall_Paint_White", (0.90, 0.90, 0.88), 0.85),
    rcc=mat("I601_RCC_Painted", (0.88, 0.88, 0.86), 0.85),
    common=mat("I601_Common_Wall", (0.70, 0.70, 0.70), 0.9),
    slab=mat("I601_Concrete_Slab", (0.45, 0.45, 0.45), 0.95),
    floor=mat("I601_Floor_Vitrified_White_600", (0.86, 0.86, 0.84), 0.12),
    wetfloor=mat("I601_Floor_Antiskid_Grey", (0.22, 0.22, 0.22), 0.7),
    ledge=mat("I601_Ledge_Stone", (0.62, 0.60, 0.55), 0.8),
    glass=mat("I601_Glass", (0.75, 0.88, 0.95), 0.02, 0.0, 0.25, 1.0),
    frame=mat("I601_Window_Frame_Black", (0.03, 0.03, 0.03), 0.4, 0.5),
    jamb=mat("I601_Granite_Frame", (0.10, 0.10, 0.10), 0.3),
    door=mat("I601_Door_Laminate_White", (0.88, 0.88, 0.86), 0.4),
    maindoor=mat("I601_Main_Door", (0.22, 0.19, 0.17), 0.45),
    rail=mat("I601_MS_Railing", (0.12, 0.12, 0.13), 0.5, 0.6),
    granite=mat("I601_Granite_Top", (0.09, 0.09, 0.09), 0.25),
    walltile=mat("I601_Wall_Tile_Beige", (0.42, 0.36, 0.30), 0.2),
    skirting=mat("I601_Skirting_Tile", (0.80, 0.80, 0.78), 0.2),
    steel=mat("I601_Steel", (0.80, 0.80, 0.82), 0.25, 1.0),
    ceramic=mat("I601_Ceramic_White", (0.95, 0.95, 0.95), 0.15),
    mirror=mat("I601_Mirror", (0.9, 0.9, 0.9), 0.0, 1.0),
    lift=mat("I601_Lift_Shaft", (0.25, 0.25, 0.27), 0.8),
    label=mat("I601_Label", (0.10, 0.10, 0.10), 0.9),
)

def add_tile_grid(m, w, h, grout_rgb, offset=(0.0, 0.0), axes="XY"):
    """Procedural tile joints (Brick Texture, no stagger) in object space; w/h in metres."""
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    base = next(s for s in p.inputs if s.identifier == "Base Color").default_value[:]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.0
    br.squash = 1.0
    def si(node, ident, val):
        for s in node.inputs:
            if s.identifier == ident:
                s.default_value = val
                return
    si(mp, "Location", (offset[0], offset[1], 0.0))
    si(br, "Color1", base); si(br, "Color2", base)
    si(br, "Mortar", (*grout_rgb, 1.0))
    si(br, "Scale", 1.0); si(br, "Mortar Size", 0.0025); si(br, "Mortar Smooth", 0.0)
    si(br, "Brick Width", w); si(br, "Row Height", h)
    out = lambda node, ident: next(s for s in node.outputs if s.identifier == ident)
    inp = lambda node, ident: next(s for s in node.inputs if s.identifier == ident)
    nt.links.new(out(tc, "Object"), inp(mp, "Vector"))
    nt.links.new(out(mp, "Vector"), inp(sep, "Vector"))
    a, b = axes[0], axes[1]
    nt.links.new(out(sep, a), inp(comb, "X"))
    nt.links.new(out(sep, b), inp(comb, "Y"))
    nt.links.new(out(comb, "Vector"), inp(br, "Vector"))
    nt.links.new(out(br, "Color"), inp(p, "Base Color"))

def tile_image(name, px, grout_px, base_srgb, grout_srgb):
    """One square tile with half a grout joint on every edge, so it repeats seamlessly (exports to glTF)."""
    import numpy as np
    old = bpy.data.images.get(name)
    if old:
        bpy.data.images.remove(old)
    img = bpy.data.images.new(name, px, px, alpha=False)
    a = np.empty((px, px, 4), np.float32)
    a[...] = (*base_srgb, 1.0)
    d = np.minimum(np.arange(px), np.arange(px)[::-1]).astype(np.float32) + 0.5   # distance to nearest edge
    w = np.clip(grout_px / 2 + 0.5 - d, 0, 1)                                      # 1 inside the joint, soft 1px edge
    m = np.maximum(w[:, None], w[None, :])[..., None]
    a[..., :3] = a[..., :3] * (1 - m) + np.array(grout_srgb, np.float32) * m
    img.pixels.foreach_set(a.ravel())
    img.update()
    img.pack()
    return img

def use_tile_image(m, img):
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Linear"
    tex.extension = "REPEAT"
    uvn = nt.nodes.new("ShaderNodeUVMap")
    nt.links.new(next(s for s in uvn.outputs if s.identifier == "UV"), next(s for s in tex.inputs if s.identifier == "Vector"))
    nt.links.new(next(s for s in tex.outputs if s.identifier == "Color"), next(s for s in p.inputs if s.identifier == "Base Color"))

# 600x600 (2 ft) vitrified floor tiles. The joint layout per room was measured from the site photos
# (see FLOOR_ZONES below); one texture repeat = one tile, laid out through each zone's UVs.
use_tile_image(M["floor"], tile_image("I601_Floor_Tile_600", 512, 4, (0.94, 0.94, 0.925), (0.40, 0.40, 0.38)))
add_tile_grid(M["wetfloor"], 0.3, 0.3, (0.12, 0.12, 0.12))

# ---------------------------------------------------------------- geometry helpers
def _clean(pts):
    pts = [tuple(p) for p in pts]
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts)))
    return pts if area > 0 else pts[::-1]

def bm_prism(bm, pts, z0, z1):
    pts = _clean(pts)
    vs = [bm.verts.new((x * S, y * S, z0 * S)) for x, y in pts]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=nv, vec=(0, 0, (z1 - z0) * S))

def bm_box(bm, x0, y0, x1, y1, z0, z1):
    bm_prism(bm, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1)

def bm_cyl(bm, cx, cy, rx, ry, z0, z1, seg=32):
    pts = [(cx + rx * math.cos(2 * math.pi * i / seg), cy + ry * math.sin(2 * math.pi * i / seg))
           for i in range(seg)]
    bm_prism(bm, pts, z0, z1)

def make(name, coll, material, builder):
    bm = bmesh.new()
    builder(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(material)
    COLL[coll].objects.link(ob)
    ob.parent = root
    return ob

def prism(name, coll, material, pts, z0, z1):
    return make(name, coll, material, lambda bm: bm_prism(bm, pts, z0, z1))

def boxes(name, coll, material, items):
    def b(bm):
        for it in items:
            bm_box(bm, *it)
    return make(name, coll, material, b)

def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

# ---------------------------------------------------------------- structure
WALLS = {
    "W-A_Bedroom1_Bottom": [(0,0),(3583,0),(3583,2075),(3468,2075),(3468,115),(115,115),(115,1200),(0,1200)],
    "W-B_Bedroom1_2_Partition": [(0,2750),(115,2750),(115,4089),(3583,4089),(3583,4204),(115,4204),(115,4604),(0,4604)],
    "W-C_Bedroom2_Top": [(3583,7453),(3353,7453),(3353,7354),(0,7354),(0,6154),(115,6154),(115,7239),(3468,7239),(3468,5104),(3583,5104)],
    "W-D_Toilet1": [(3468,2825),(4883,2825),(4883,725),(4133,725),(4133,610),(4998,610),(4998,2940),(3583,2940),(3583,3189),(3468,3189)],
    "W-E_Toilet2": [(4883,0),(6399,0),(6399,2325),(5748,2325),(5748,2210),(6284,2210),(6284,115),(4883,115)],
    "W-F_Right_Kitchen": [(5733,4928),(5848,4928),(5848,5713),(7999,5713),(7999,0),(8229,0),(8229,9183),(7999,9183),(7999,5828),(5733,5828)],
    "W-G_Top_Left": rect(2753, 8953, 4086, 9183),
    "W-H_Top_MainDoor": rect(6526, 8953, 6949, 9183),
}
for n, p in WALLS.items():
    prism(n, "Structure", M["wall"], p, 0, SOFFIT)

COLUMNS = {
    # C1: drawing shows 230x950 along the window wall; the master-bedroom photo shows it along the bottom wall
    # C4 (3353-3583 x 6154-7354, Bedroom 2 / drawing room wall) is on the drawing but not built.
    "C1": rect(0, 0, 1200, 230), "C2": rect(3353, 0, 3583, 1200), "C3": rect(0, 7124, 1200, 7354),
    "C5": rect(7999, 610, 8229, 1810),
    "C6": rect(7999, 3466, 8229, 4666), "C7": rect(7999, 7983, 8229, 9183),
}
for n, p in COLUMNS.items():
    prism("Column_" + n, "Structure", M["rcc"], p, 0, SOFFIT)

# openings: name, gap rect (in wall), sill z, kind
OPENINGS = [
    ("D01_Main",        (6949, 8953, 7999, 9183), 0,    "door"),
    ("D02_Bedroom2",    (3468, 4204, 3583, 5104), 0,    "door"),
    ("D02_Bedroom1",    (3468, 3189, 3583, 4089), 0,    "door"),
    ("D03_Toilet1",     (3468, 2075, 3583, 2825), 0,    "door"),
    ("D03_Toilet2",     (4998, 2210, 5748, 2325), 0,    "door"),
    ("W01_Drawing",     (3353, 7453, 3583, 8953), 830,  "win"),   # sill 830 / 1545 high, confirmed by photos
    ("W02_Bedroom1",    (0, 1200, 115, 2750),     830,  "win"),
    ("W02_Bedroom2",    (0, 4604, 115, 6154),     830,  "win"),
    ("W03_Wash",        (6399, 610, 7999, 725),   1130, "win"),
    ("V01_Toilet1",     (3583, 610, 4133, 725),   1175, "win"),
    ("V02_Toilet2",     (4883, 115, 4998, 610),   1775, "win"),
]
boxes("Lintels_over_openings", "Structure", M["wall"],
      [(*r, BEAM, SOFFIT) for _, r, _, _ in OPENINGS])
boxes("Sills_under_windows", "Structure", M["wall"],
      [(*r, 0, s) for _, r, s, k in OPENINGS if k == "win"])

# Dropped beams (bottom = beam bottom 2375 SSL). Layout inferred from the site photos:
# 230-wide beams on column lines; on 115 walls they project 115 into the room (bulkheads seen in photos).
BEAMS = {
    "Beam_WindowWall_x0":       (0, 0, 230, 7354),
    "Beam_Bedroom1_Bottom":     (0, 0, 3583, 230),
    "Beam_Bedroom1_2":          (115, 3974, 3468, 4204),
    "Beam_Bedroom2_Top":        (0, 7124, 3583, 7354),
    "Beam_Partition_x3583":     (3353, 0, 3583, 8953),
    "Beam_Right_x8229":         (7999, 0, 8229, 9183),
    "Beam_Top_y9183":           (2753, 8953, 8229, 9183),
    "Beam_W03_V01_y610":        (3583, 610, 7999, 840),
    "Beam_Toilet2_Bottom":      (4883, 0, 6399, 230),
    "Beam_Dining_Kitchen_y2940": (3583, 2710, 7999, 2940),
    "Beam_Kitchen_Drawing_y5828": (3583, 5598, 7999, 5828),
}
boxes("Beams", "Structure", M["wall"], [(*b, BEAM, SOFFIT) for b in BEAMS.values()])

FOOTPRINT = [(0,0),(3583,0),(3583,610),(4883,610),(4883,0),(6399,0),(6399,610),(7999,610),(7999,0),
             (8229,0),(8229,9183),(2753,9183),(2753,8953),(3353,8953),(3353,7354),(0,7354)]
prism("Floor_Slab_RCC", "Structure", M["slab"], FOOTPRINT, -150, 0)
WET = [rect(3583, 725, 4883, 2825), rect(4998, 115, 6284, 2210), rect(6399, 725, 7999, 2325)]

# Floor tiles: each zone is laid on its own 600 grid. A full tile starts at the anchor (a joint line in
# x and in y). Anchors were measured by rectifying the floor in each site photo:
#   main (drawing + dining + kitchen): full tiles from the main-door corner (x 7999 wall, y 8953 wall)
#   bedrooms: full tiles from the door wall (x 3468); Bedroom 2 also from its top wall (y 7239);
#   Bedroom 1 has a ~35 mm cut row against the shared wall (joint at y 4054).
# Zone borders run along the middle of the partition walls.
FLOOR_ZONES = {
    "Main": ([(3525,0),(3583,0),(3583,610),(4883,610),(4883,0),(6399,0),(6399,610),(7999,610),(7999,0),
              (8229,0),(8229,9183),(2753,9183),(2753,8953),(3353,8953),(3353,7354),(3525,7354)], (7999, 8953)),
    "Bedroom1": (rect(0, 0, 3525, 4146), (3468, 4054)),
    "Bedroom2": (rect(0, 4146, 3525, 7354), (3468, 7239)),
}
TILE = 600

def floor_zone(name, pts, anchor):
    def b(bm):
        bm_prism(bm, pts, 0, FFL)
        uv = bm.loops.layers.uv.new("UVMap")
        for f in bm.faces:
            for l in f.loops:
                x, y = l.vert.co.x / S, l.vert.co.y / S
                l[uv].uv = ((x - anchor[0]) / TILE, (y - anchor[1]) / TILE)
    return make(name, "Structure", M["floor"], b)

for zn, (pts, anchor) in FLOOR_ZONES.items():
    floor_zone(f"Floor_Finish_{zn} (600x600 vitrified)", pts, anchor)
boxes("Floor_Finish_Toilets_Wash (anti-skid)", "Structure", M["wetfloor"],
      [(p[0][0], p[0][1], p[2][0], p[2][1], 0, FFL + 1) for p in WET])
ceil = prism("Ceiling_Slab", "Ceiling (hidden)", M["slab"], FOOTPRINT, SOFFIT, FTF)

# ---------------------------------------------------------------- finishes (skirting, wall tiles)
import json as _json, os as _os
# Resolve relative to the saved .blend (project root); fall back to this script's folder.
_SCRIPTS = (_os.path.join(_os.path.dirname(bpy.data.filepath), "model_scripts") if bpy.data.filepath
            else _os.path.dirname(_os.path.abspath(__file__)))
_fin = _json.load(open(_os.path.join(_SCRIPTS, "finish_strips.json")))
boxes("Skirting_100mm", "Finishes", M["skirting"], [tuple(s) for s in _fin["skirting"]])
boxes("Toilet_Wall_Tiles_2275", "Finishes", M["walltile"], [tuple(s) for s in _fin["toilet_dado"]])
boxes("Wash_Wall_Tiles_to_sill", "Finishes", M["walltile"], [tuple(s) for s in _fin["wash_dado"]])
WASH_CAP = 1130
boxes("Wash_Tile_Granite_Capping", "Finishes", M["granite"],
      [(7979, 725, 7999, 2325, WASH_CAP, WASH_CAP + 20), (6399, 725, 6419, 2325, WASH_CAP, WASH_CAP + 20)])

# ---------------------------------------------------------------- windows
def window(name, gap, z0, z1, along, band, inset=35, fw=45, transom=None, lining=True):
    """along='y': wall runs along y (thickness in x); band = (d0,d1) frame depth across the wall.
    transom: height below head of a fixed top light (W03)."""
    x0, y0, x1, y1 = gap
    a0, a1 = (y0 + inset, y1 - inset) if along == "y" else (x0 + inset, x1 - inset)
    d0, d1 = band
    am = (a0 + a1) / 2
    def B(a_0, a_1, e0, e1, z_0, z_1):
        return (e0, a_0, e1, a_1, z_0, z_1) if along == "y" else (a_0, e0, a_1, e1, z_0, z_1)
    zs = z1 - transom if transom else z1           # top of sliding part
    fr = [B(a0, a1, d0, d1, z0, z0 + fw), B(a0, a1, d0, d1, z1 - fw, z1),
          B(a0, a0 + fw, d0, d1, z0, z1), B(a1 - fw, a1, d0, d1, z0, z1),
          B(am - fw / 2, am + fw / 2, d0, d1, z0, zs)]
    if transom:
        fr.append(B(a0, a1, d0, d1, zs - fw / 2, zs + fw / 2))
    boxes(name + "_Frame", "Windows & Doors", M["frame"], fr)
    dm = (d0 + d1) / 2
    gl = [B(a0 + fw, am + fw / 2, dm - 12, dm - 6, z0 + fw, zs - fw / 2),
          B(am - fw / 2, a1 - fw, dm + 6, dm + 12, z0 + fw, zs - fw / 2)]
    if transom:
        gl.append(B(a0 + fw, a1 - fw, dm - 3, dm + 3, zs + fw / 2, z1 - fw))
    boxes(name + "_Glass", "Windows & Doors", M["glass"], gl)
    if lining:   # dark granite reveal lining all round, as seen in the photos
        g = 20
        if along == "y":
            lin = [(x0, y0, x1, y1, z0 - g, z0), (x0, y0, x1, y1, z1, z1 + g),
                   (x0, y0, x1, y0 + g, z0, z1), (x0, y1 - g, x1, y1, z0, z1)]
        else:
            lin = [(x0, y0, x1, y1, z0 - g, z0), (x0, y0, x1, y1, z1, z1 + g),
                   (x0, y0, x0 + g, y1, z0, z1), (x1 - g, y0, x1, y1, z0, z1)]
        boxes(name + "_Granite_Lining", "Windows & Doors", M["jamb"], lin)

window("W01_Drawing", (3353, 7453, 3583, 8953), 830, BEAM, "y", (3388, 3433))
window("W02_Bedroom1", (0, 1200, 115, 2750), 830, BEAM, "y", (30, 75))
window("W02_Bedroom2", (0, 4604, 115, 6154), 830, BEAM, "y", (30, 75))
window("W03_Wash", (6399, 610, 7999, 725), 1130, BEAM, "x", (640, 685), transom=420)
window("V01_Toilet1", (3583, 610, 4133, 725), 1175, BEAM, "x", (645, 690), lining=False)
window("V02_Toilet2", (4883, 126, 4998, 598), 1775, BEAM, "y", (4918, 4948), inset=0, lining=False)

# ---------------------------------------------------------------- doors (granite frames, white flush leaves)
def door_frame(name, gap, along, jamb=50, arch=0):
    x0, y0, x1, y1 = gap
    if along == "y":
        it = [(x0 - arch, y0, x1 + arch, y0 + jamb, 0, BEAM), (x0 - arch, y1 - jamb, x1 + arch, y1, 0, BEAM),
              (x0 - arch, y0, x1 + arch, y1, BEAM - jamb, BEAM)]
    else:
        it = [(x0, y0 - arch, x0 + jamb, y1 + arch, 0, BEAM), (x1 - jamb, y0 - arch, x1, y1 + arch, 0, BEAM),
              (x0, y0 - arch, x1, y1 + arch, BEAM - jamb, BEAM)]
    boxes(name + "_Granite_Frame", "Windows & Doors", M["jamb"], it)

door_frame("D01_Main", (6949, 8953, 7999, 9183), "x", jamb=100, arch=10)
door_frame("D02_Bedroom2", (3468, 4204, 3583, 5104), "y", arch=8)
door_frame("D02_Bedroom1", (3468, 3189, 3583, 4089), "y", arch=8)
door_frame("D03_Toilet1", (3468, 2075, 3583, 2825), "y", arch=8)
door_frame("D03_Toilet2", (4998, 2210, 5748, 2325), "x", arch=8)
LEAF_TOP = BEAM - 50
# Hinge sides as drawn and confirmed by handle positions in the photos; leaves shown open 90 deg.
boxes("D01_Main_Leaf (open, hinged at x7999 jamb as in photo)", "Windows & Doors", M["maindoor"],
      [(7899, 8003, 7949, 8953, FFL, LEAF_TOP)])
boxes("D02_Bedroom2_Leaf", "Windows & Doors", M["door"], [(2733, 4254, 3533, 4289, FFL, LEAF_TOP)])
boxes("D02_Bedroom1_Leaf", "Windows & Doors", M["door"], [(2733, 4004, 3533, 4039, FFL, LEAF_TOP)])
boxes("D03_Toilet1_Leaf", "Windows & Doors", M["door"], [(3518, 2740, 4168, 2775, FFL, LEAF_TOP)])
boxes("D03_Toilet2_Leaf", "Windows & Doors", M["door"], [(5048, 1625, 5083, 2275, FFL, LEAF_TOP)])

# ---------------------------------------------------------------- ledges, railings
LEDGES = {"ODU_Ledge_Bedroom1": rect(-600, 900, 0, 2900),
          "ODU_Ledge_Bedroom2": rect(-600, 4454, 0, 6454),
          "ODU_Ledge_W01": rect(2753, 7354, 3353, 8953),
          "Projection_below_W03": rect(6399, 0, 7999, 610)}
for n, p in LEDGES.items():
    prism(n, "Ledges & Railings", M["ledge"], p, LEDGE_BOT, LEDGE_TOP)
    prism(n + "_above (7th floor)", "Context Above (hidden)", M["ledge"], p, ABOVE_BOT, ABOVE_BOT + 125)
prism("ODU_Ledge_Wall_Bedroom1", "Ledges & Railings", M["wall"],
      [(-600,900),(0,900),(0,1015),(-485,1015),(-485,1200),(-600,1200)], LEDGE_BOT, ABOVE_BOT)
prism("ODU_Ledge_Wall_Bedroom2", "Ledges & Railings", M["wall"],
      [(-600,6154),(-485,6154),(-485,6339),(0,6339),(0,6454),(-600,6454)], LEDGE_BOT, ABOVE_BOT)

RAIL_TOP = 1230   # top rail measured in photos at z ~1.19-1.30 (SSL)
def railing(name, p0, p1, z0=LEDGE_TOP, z1=RAIL_TOP, pitch=600, post=25, rails=(None, 150)):
    """Open MS railing as seen through the windows: square posts at ~600 c/c, top rail + bottom rail."""
    (xa, ya), (xb, yb) = p0, p1
    L = math.hypot(xb - xa, yb - ya)
    ux, uy = (xb - xa) / L, (yb - ya) / L
    it = []
    n = max(1, round(L / pitch))
    for i in range(n + 1):
        t = min(max(i * L / n, post / 2), L - post / 2)
        cx, cy = xa + ux * t, ya + uy * t
        it.append((cx - post / 2, cy - post / 2, cx + post / 2, cy + post / 2, z0, z1))
    xs, ys = sorted((xa, xb)), sorted((ya, yb))
    for zr, h in ((z1 - 40, 40), (z0 + 100, 25)):
        if abs(ux) > abs(uy):
            it.append((xs[0], ya - 20, xs[1], ya + 20, zr, zr + h))
        else:
            it.append((xa - 20, ys[0], xa + 20, ys[1], zr, zr + h))
    boxes(name, "Ledges & Railings", M["rail"], it)

railing("Railing_Bedroom1_outer", (-580, 1200), (-580, 2880))
railing("Railing_Bedroom1_end", (-580, 2880), (0, 2880))
railing("Railing_Bedroom2_outer", (-580, 4474), (-580, 6154))
railing("Railing_Bedroom2_end", (-580, 4474), (0, 4474))
railing("Railing_W01_Ledge", (2773, 7354), (2773, 8953))

# ---------------------------------------------------------------- kitchen (open granite platform, as built)
TOP = FFL + 900
boxes("Kitchen_Granite_Platform", "Kitchen & Toilets", M["granite"],
      [(7349, 2365, 7999, 5713, TOP - 20, TOP), (5848, 5078, 7349, 5713, TOP - 20, TOP)])
boxes("Kitchen_Granite_Supports", "Kitchen & Toilets", M["granite"],
      [(7349, 2325, 7999, 2365, FFL, 1290),            # end fin / splash between sink and wash
       (7349, 3480, 7999, 3520, FFL, TOP - 20),        # mid support under run A
       (7349, 5078, 7389, 5713, FFL, TOP - 20)])       # support at the inner corner (run B)
boxes("Kitchen_Sink", "Kitchen & Toilets", M["steel"], [(7462, 2467, 7809, 2813, TOP - 200, TOP + 2)])
boxes("Kitchen_Wall_Tiles (counter to beam bottom)", "Finishes", M["walltile"],
      [(7991, 2365, 7999, 5713, TOP, BEAM)])

# ---------------------------------------------------------------- toilets (from toilet detail drawing)
def toilet(tag, counter, bowl_c, ledge, wc_c, cistern, mirror, mixer_xy, wall_x):
    boxes(f"{tag}_Basin_Counter", "Kitchen & Toilets", M["granite"], [(*counter, FFL + 780, FFL + 800)])
    make(f"{tag}_Basin_Bowl", "Kitchen & Toilets", M["ceramic"],
         lambda bm: bm_cyl(bm, *bowl_c, 200, 200, FFL + 800, FFL + 950))
    boxes(f"{tag}_Plumbing_Ledge", "Kitchen & Toilets", M["walltile"], [(*ledge, FFL, FFL + 650)])
    make(f"{tag}_WC", "Kitchen & Toilets", M["ceramic"],
         lambda bm: bm_cyl(bm, *wc_c, 300, 190, FFL, FFL + 400))
    boxes(f"{tag}_Flush_Tank", "Kitchen & Toilets", M["ceramic"], [(*cistern, FFL + 650, FFL + 1000)])
    boxes(f"{tag}_Mirror", "Kitchen & Toilets", M["mirror"], [(*mirror, FFL + 1050, FFL + 1850)])
    mx, my = mixer_xy
    boxes(f"{tag}_Shower_Mixer_and_Head", "Kitchen & Toilets", M["steel"],
          [(wall_x - 60, my - 60, wall_x, my + 60, FFL + 950, FFL + 1070),
           (wall_x - 250, my - 50, wall_x, my + 50, FFL + 2050, FFL + 2080)])
    make(f"{tag}_Floor_Trap", "Kitchen & Toilets", M["steel"],
         lambda bm: bm_cyl(bm, mx, my, 70, 70, FFL + 1, FFL + 4, 16))

toilet("Toilet1", (4433, 2325, 4883, 2825), (4658, 2575), (4733, 1425, 4883, 2325), (4420, 1870),
       (4743, 1650, 4883, 2090), (4865, 2375, 4875, 2775), (4697, 1063), 4875)
toilet("Toilet2", (5834, 1710, 6284, 2210), (6059, 1960), (6135, 810, 6284, 1710), (5820, 1250),
       (6145, 1030, 6284, 1470), (6266, 1760, 6276, 2160), (6098, 448), 6276)

# ---------------------------------------------------------------- common areas (context)
CW = [rect(6296, 10812, 6526, 11391), rect(6296, 9183, 6526, 9762), rect(6526, 11391, 8169, 11506)]
for i, p in enumerate(CW):
    prism(f"Common_Wall_{i+1}", "Common Areas", M["common"], p, 0, SOFFIT)
prism("Lift_Core_RCC", "Common Areas", M["rcc"],
      [(6526,11621),(4086,11621),(4086,8953),(6526,8953),(6526,9183),(4316,9183),(4316,11391),(6526,11391)],
      -150, SOFFIT)
prism("Lift_Shaft_Pit", "Common Areas", M["lift"], rect(4316, 9183, 6296, 11391), -150, -140)
prism("Lobby_Floor", "Common Areas", M["slab"], rect(6526, 9183, 8229, 11391), -150, FFL)

# ---------------------------------------------------------------- labels
def label(text, x, y, size=0.22, rot=0.0):
    cu = bpy.data.curves.new("lbl_" + text, type="FONT")
    cu.body = text
    cu.size = size
    try:
        cu.align_x = "CENTER"; cu.align_y = "CENTER"
    except Exception:
        pass
    ob = bpy.data.objects.new("Label_" + text.replace("\n", " "), cu)
    ob.location = (x * S, y * S, (FFL + 5) * S)
    ob.rotation_euler = (0, 0, rot)
    ob.data.materials.append(M["label"])
    COLL["Labels"].objects.link(ob)
    ob.parent = root
for t, x, y in (("BEDROOM 1", 1790, 2900), ("BEDROOM 2", 1790, 4800), ("TOILET 1", 4100, 1300),
                ("TOILET 2", 5450, 650), ("WASH", 7199, 1500), ("KITCHEN", 6600, 4400),
                ("DINING", 4650, 3700), ("DRAWING ROOM", 5900, 7750), ("LOBBY", 7380, 10300),
                ("LIFT", 5306, 10287)):
    label(t, x, y)

# hide context collections by default
for cname in ("Ceiling (hidden)", "Context Above (hidden)"):
    for ob in COLL[cname].all_objects:
        ob.hide_set(True)
        ob.hide_render = True

# ---------------------------------------------------------------- light + camera
sun = bpy.data.objects.get("I601_Sun")
if sun is None:
    sd = bpy.data.lights.new("I601_Sun", type="SUN")
    sd.energy = 3.0
    sun = bpy.data.objects.new("I601_Sun", sd)
    scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(40), math.radians(15), math.radians(-35))
cam = scene.camera or bpy.data.objects.get("Camera")
if cam:
    cam.location = (-2.8, -4.2, 14.5)
    target = (4.1, 4.6, 0.0)
    d = [target[i] - cam.location[i] for i in range(3)]
    cam.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0]) - math.pi / 2)
    cam.data.lens = 30
old = bpy.data.objects.get("Light")
if old and old.type == "LIGHT":
    bpy.data.objects.remove(old, do_unlink=True)

print("I-601 built:", len(root_coll.all_objects), "objects")
