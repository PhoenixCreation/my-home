"""Add movable furniture to the I-601 model (run after build_blender.py).

Each piece is an Empty named FURN_<key> at the centre of its footprint, on the finished floor, with
its parts as child meshes. The web viewer finds the pieces through the custom properties
(furniture / label / size_mm), which are exported to glTF as extras. Coordinates are in mm,
in the same local frame as build_blender.py (z = 0 at SSL, finished floor at +80).
"""
import bpy, bmesh, math

S = 0.001
FFL = 80
BEAM = 2375
SOFFIT = 2800
TOP = FFL + 900          # kitchen counter top

# ---------------------------------------------------------------- cleanup
coll = bpy.data.collections.get("Furniture")
if coll:
    for o in list(coll.objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    coll = bpy.data.collections.new("Furniture")
    bpy.data.collections["I-601"].children.link(coll)
for m in list(bpy.data.meshes):
    if m.users == 0:
        bpy.data.meshes.remove(m)
for m in list(bpy.data.materials):
    if m.name.startswith("I601F_"):
        bpy.data.materials.remove(m)
root = bpy.data.objects.get("I-601_ROOT")

# ---------------------------------------------------------------- materials
def mat(name, rgb, rough=0.6, metal=0.0, alpha=1.0):
    m = bpy.data.materials.new("I601F_" + name)
    m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    for ident, val in (("Base Color", (*rgb, 1.0)), ("Roughness", rough), ("Metallic", metal), ("Alpha", alpha)):
        s = next(s for s in p.inputs if s.identifier == ident)
        s.default_value = val
    m.diffuse_color = (*rgb, alpha)
    if alpha < 1.0:
        m.surface_render_method = "BLENDED"
    return m

M = dict(
    fabric=mat("Sofa_Fabric_Sage", (0.20, 0.25, 0.20), 0.95),
    cushion=mat("Sofa_Cushion_Sage", (0.26, 0.31, 0.25), 0.95),
    walnut=mat("Laminate_Walnut", (0.20, 0.11, 0.06), 0.55),
    oak=mat("Laminate_Light_Oak", (0.55, 0.38, 0.22), 0.5),
    white=mat("Laminate_Warm_White", (0.80, 0.78, 0.74), 0.35),
    slate=mat("Laminate_Slate_Grey", (0.12, 0.13, 0.14), 0.4),
    carcass=mat("Carcass_Grey", (0.55, 0.55, 0.53), 0.6),
    kick=mat("Plinth_Dark", (0.04, 0.04, 0.04), 0.6),
    steel=mat("Handle_Steel", (0.75, 0.75, 0.77), 0.25, 1.0),
    black=mat("Metal_Black", (0.03, 0.03, 0.03), 0.4, 0.6),
    mattress=mat("Mattress_White", (0.86, 0.86, 0.84), 0.9),
    sheet=mat("Bed_Sheet_Ivory", (0.80, 0.76, 0.68), 0.9),
    throw=mat("Bed_Throw_Blue", (0.10, 0.17, 0.27), 0.95),
    pillow=mat("Pillow_White", (0.90, 0.90, 0.88), 0.95),
    mirror=mat("Mirror_Glass", (0.72, 0.79, 0.81), 0.16, 0.35),
    glass=mat("Clear_Glass", (0.85, 0.94, 0.96), 0.18, alpha=0.22),
)

# ---------------------------------------------------------------- helpers
class Piece:
    """Collect boxes by editable section and build meshes around the footprint centre."""
    def __init__(self, key, label, *, fixed=False, fold_pivot=None):
        self.key, self.label, self.parts = key, label, {}
        self.fixed = fixed
        self.fold_pivot = fold_pivot

    def box(self, material, x0, y0, x1, y1, z0, z1, bevel=0.0, *, section, folds=False, slide=False):
        self.parts.setdefault((section, material, bevel, folds, slide), []).append((x0, y0, x1, y1, z0, z1))
        return self

    def build(self):
        # footprint and size ignore the handles, so the reported depth is the carcass + shutter depth
        allb = [b for (_, m, _, _, _), bs in self.parts.items() if m is not M["steel"] for b in bs]
        x0 = min(b[0] for b in allb); y0 = min(b[1] for b in allb)
        x1 = max(b[2] for b in allb); y1 = max(b[3] for b in allb)
        z0 = min(b[4] for b in allb); z1 = max(b[5] for b in allb)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        emp = bpy.data.objects.new("FURN_" + self.key, None)
        emp.empty_display_type = "PLAIN_AXES"
        emp.empty_display_size = 0.3
        emp.location = (cx * S, cy * S, FFL * S)
        emp["furniture"] = 1
        emp["label"] = self.label
        emp["size_mm"] = [round(x1 - x0), round(y1 - y0), round(z1 - z0)]   # along x, along y, height
        emp["elev_mm"] = round(z0 - FFL)                                    # bottom above the floor
        if self.fixed:
            emp["fixed"] = 1
        coll.objects.link(emp)
        if root:
            emp.parent = root
        pivot = None
        if self.fold_pivot:
            px, py, pz = self.fold_pivot
            pivot = bpy.data.objects.new(emp.name + "_Hinge", None)
            coll.objects.link(pivot)
            pivot.parent = emp
            pivot.location = ((px - cx) * S, (py - cy) * S, (pz - FFL) * S)
            pivot.rotation_euler.y = math.pi / 2
            pivot["fold_hinge"] = 1
        for i, ((section, material, bevel, folds, slide), bs) in enumerate(self.parts.items()):
            ox, oy, oz = self.fold_pivot if folds else (cx, cy, FFL)
            bm = bmesh.new()
            for (a0, b0, a1, b1, c0, c1) in bs:
                g = bmesh.ops.create_cube(bm, size=1.0)
                vs = g["verts"]
                for v in vs:
                    v.co.x = ((a0 if v.co.x < 0 else a1) - ox) * S
                    v.co.y = ((b0 if v.co.y < 0 else b1) - oy) * S
                    v.co.z = ((c0 if v.co.z < 0 else c1) - oz) * S
                if bevel:
                    edges = list({e for v in vs for e in v.link_edges})
                    bmesh.ops.bevel(bm, geom=edges, offset=bevel * S, segments=2, affect="EDGES",
                                    profile=0.5, clamp_overlap=True)
            # Planar UVs keep grain vertical on upright faces and map one repeat per metre.
            bm.normal_update()
            uv_layer = bm.loops.layers.uv.new("UVMap")
            for face in bm.faces:
                axis = max(range(3), key=lambda dim: abs(face.normal[dim]))
                u, v = ((1, 2), (0, 2), (0, 1))[axis]
                for loop in face.loops:
                    loop[uv_layer].uv = (loop.vert.co[u], loop.vert.co[v])
            me = bpy.data.meshes.new(f"FURN_{self.key}_{material.name[6:]}")
            bm.to_mesh(me)
            bm.free()
            for poly in me.polygons:
                poly.use_smooth = bool(bevel)
            ob = bpy.data.objects.new(f"FURN_{self.key}_part{i}_{material.name[6:]}", me)
            ob.data.materials.append(material)
            ob["color_section"] = section
            if slide:
                ob["mirror_slide"] = 1
            coll.objects.link(ob)
            ob.parent = pivot if folds else emp
        return emp

def shutters(p, fmat, along, a0, a1, n, plane0, plane1, z0, z1, *, label, gap=3, handle="v", hz=None):
    """n equal door/drawer fronts between a0..a1 on a front plane (plane0 < plane1, the carcass is
    behind plane1). along='y': fronts face -x (plane is x); along='x': fronts face -y (plane is y)."""
    w = (a1 - a0) / n
    for i in range(n):
        s0, s1 = a0 + i * w + gap / 2, a0 + (i + 1) * w - gap / 2
        section = f"{label} {i + 1}" if n > 1 else label
        if along == "y":
            p.box(fmat, plane0, s0, plane1, s1, z0 + gap / 2, z1 - gap / 2, section=section)
        else:
            p.box(fmat, s0, plane0, s1, plane1, z0 + gap / 2, z1 - gap / 2, section=section)
        # handle on the outer face; every front here faces towards the lower coordinate
        hp0, hp1 = plane0 - 22, plane0
        if handle == "v":                        # vertical bar near the meeting edge of door pairs
            edge = s1 - 40 if i % 2 == 0 else s0 + 40
            hz0, hz1 = (hz if hz else ((z0 + z1) / 2 - 180, (z0 + z1) / 2 + 180))
            if along == "y":
                p.box(M["steel"], hp0, edge - 8, hp1, edge + 8, hz0, hz1, section="Handles")
            else:
                p.box(M["steel"], edge - 8, hp0, edge + 8, hp1, hz0, hz1, section="Handles")
        elif handle == "h":                      # horizontal bar near the top edge (drawers)
            hzc = hz if hz else z1 - 45
            m0, m1 = (s0 + s1) / 2 - min(160, w / 3), (s0 + s1) / 2 + min(160, w / 3)
            if along == "y":
                p.box(M["steel"], hp0, m0, hp1, m1, hzc - 8, hzc + 8, section="Handles")
            else:
                p.box(M["steel"], m0, hp0, m1, hp1, hzc - 8, hzc + 8, section="Handles")

def F(h):
    """Height above the finished floor -> SSL z."""
    return FFL + h


def glass_door(p, material, x0, x1, y0, y1, z0, z1, *, frame, pane):
    rail = 26
    for x in (x0, x1 - rail):
        p.box(material, x, y0, x + rail, y1, z0, z1, section=frame)
    for z in (z0, z1 - rail):
        p.box(material, x0 + rail, y0, x1 - rail, y1, z, z + rail, section=frame)
    middle = (y0 + y1) / 2
    p.box(M["glass"], x0 + rail, middle - 1.5, x1 - rail, middle + 1.5,
          z0 + rail, z1 - rail, section=pane)


# ---------------------------------------------------------------- drawing room: 3-seater sofa
# Back against the top wall (y 8953, lift side), facing the dining room, with one end about 300 from
# the W01 window wall (x 3583).
sofa = Piece("sofa", "3-seater sofa")
LEN, DEP, ARM = 2100, 880, 180
SX0, BACK = 3583 + 300, 8953 - 20             # left end (x) and back face (y)
def sbox(section, material, u0, v0, u1, v1, z0, z1, bevel=0.0):
    """u along the sofa from its x-start, v from the back towards the front (-y)."""
    sofa.box(material, SX0 + u0, BACK - v1, SX0 + u1, BACK - v0, z0, z1, bevel, section=section)
for (lu, lv) in ((40, 40), (40, DEP - 80), (LEN - 80, 40), (LEN - 80, DEP - 80)):
    sbox("Feet", M["black"], lu, lv, lu + 40, lv + 40, F(0), F(70))
sbox("Base", M["fabric"], 0, 0, LEN, DEP, F(70), F(260), bevel=15)
sbox("Back frame", M["fabric"], ARM, 0, LEN - ARM, 170, F(260), F(800), bevel=25)
sbox("Window-side arm", M["fabric"], 0, 0, ARM, DEP, F(260), F(620), bevel=30)
sbox("Opposite arm", M["fabric"], LEN - ARM, 0, LEN, DEP, F(260), F(620), bevel=30)
seat = (LEN - 2 * ARM) / 3
for i in range(3):
    a, b = ARM + i * seat + 4, ARM + (i + 1) * seat - 4
    sbox(f"Seat cushion {i + 1}", M["cushion"], a, 340, b, DEP - 20, F(260), F(440), bevel=35)
    sbox(f"Back cushion {i + 1}", M["cushion"], a, 170, b, 340, F(270), F(760), bevel=40)
sofa.build()

# ---------------------------------------------------------------- dining: fold-up tabletop on the kitchen stub
table = Piece("dining_table", "Folding dining table", fixed=True, fold_pivot=(5688, 5378, F(735)))
table.box(M["oak"], 5715, 4953, 5733, 5803, F(635), F(773), bevel=3, section="Wall mount")
table.box(M["oak"], 4638, 4953, 5688, 5803, F(735), F(760), bevel=5, section="Tabletop", folds=True)
for y in (5013, 5703):
    table.box(M["black"], 5488, y, 5715, y + 40, F(710), F(735), section="Hinges", folds=True)
table.build()

# ---------------------------------------------------------------- Bedroom 2 (small): bed + cupboard
def bed(key, label, mx, my, head_side, x0, y0, head_h=1000):
    """mx, my: mattress size (mm) along x / y. head_side: '+y' or '-y' (headboard wall).
    Frame overhangs the mattress by 25 on the sides and foot; headboard 50 thick."""
    p = Piece(key, label)
    fx0, fx1 = x0, x0 + mx + 50
    if head_side == "+y":
        hb0, hb1 = y0 + my + 25, y0 + my + 75
        fy0, fy1 = y0, hb0
    else:
        hb0, hb1 = y0, y0 + 50
        fy0, fy1 = hb1, hb1 + my + 25
    p.box(M["walnut"], fx0, hb0, fx1, hb1, F(0), F(head_h), bevel=8, section="Headboard")
    p.box(M["walnut"], fx0, fy0, fx1, fy1, F(60), F(320), bevel=6, section="Frame")
    p.box(M["kick"], fx0 + 60, fy0 + 60, fx1 - 60, fy1 - 60, F(0), F(60), section="Plinth")
    mx0, mx1 = fx0 + 25, fx1 - 25
    my0, my1 = (fy0 + 25, fy1) if head_side == "+y" else (fy0, fy1 - 25)
    p.box(M["mattress"], mx0, my0, mx1, my1, F(320), F(520), bevel=30, section="Mattress")
    # throw over the foot half
    if head_side == "+y":
        ty0, ty1 = my0 - 15, my0 + (my1 - my0) * 0.55
    else:
        ty0, ty1 = my1 - (my1 - my0) * 0.55, my1 + 15
    p.box(M["throw"], mx0 - 15, ty0, mx1 + 15, ty1, F(470), F(535), bevel=20, section="Bed throw")
    # pillows at the head
    n = 2
    pw = (mx1 - mx0 - 60 * (n + 1)) / n
    for i in range(n):
        a = mx0 + 60 + i * (pw + 60)
        if head_side == "+y":
            p.box(M["pillow"], a, my1 - 420, a + pw, my1 - 60, F(520), F(640),
                  bevel=45, section=f"Pillow {i + 1}")
        else:
            p.box(M["pillow"], a, my0 + 60, a + pw, my0 + 420, F(520), F(640),
                  bevel=45, section=f"Pillow {i + 1}")
    return p.build()

# 4.5 x 6.25 ft mattress, in the corner opposite the door: head on the top wall (column C3 face, y 7124),
# long side along the window wall.
bed("bed_small", "Small bedroom bed (4.5 × 6.25 ft)", 1372, 1905, "+y", 115, 7124 - 75 - 1905)

WARDROBE_BACK = 3468
WARDROBE_FRONT = WARDROBE_BACK - 610
MIRROR_WIDTH = 220

def wardrobe(key, label, a0, a1, *, mirror_at_start, single_width=0):
    p = Piece(key, label)
    front, back = WARDROBE_FRONT, WARDROBE_BACK
    base = F(80)
    p.box(M["kick"], front, a0, back, a1, F(0), base, section="Plinth")
    p.box(M["carcass"], front, a0, back, a1, BEAM - 20, BEAM, section="Cabinet frame")
    p.box(M["carcass"], back - 18, a0, back, a1, base, BEAM - 20, section="Cabinet frame")

    m0, m1 = (a0, a0 + MIRROR_WIDTH) if mirror_at_start else (a1 - MIRROR_WIDTH, a1)
    s0, s1 = (m1, a1) if mirror_at_start else (a0 + single_width, m0)
    for edge in sorted({a0, a1 - 18, s0, s1 - 18}):
        p.box(M["carcass"], front + 50, edge, back - 18, edge + 18, base, BEAM - 20,
              section="Cabinet frame")
    p.box(M["walnut"], front, m0 + 3, front + 18, m1 - 3, base + 3, BEAM - 23,
          section="Slim pull-out front", slide=True)
    # The dressing mirror is mounted on the broad side, facing the adjoining sliders.
    pane_y = m1 - 31 if mirror_at_start else m0 + 28
    p.box(M["carcass"], front + 18, pane_y - 10, back - 40, pane_y + 14, base + 60, BEAM - 70,
          section="Pull-out frame", slide=True)
    glass_y = pane_y + 14 if mirror_at_start else pane_y - 13
    p.box(M["mirror"], front + 50, glass_y, back - 70, glass_y + 3, base + 180, BEAM - 140,
          section="Dressing mirror", slide=True)
    p.box(M["steel"], front - 22, (m0 + m1) / 2 - 8, front, (m0 + m1) / 2 + 8,
          F(880), F(1240), section="Mirror pull", slide=True)

    for z in (base, BEAM - 31):
        p.box(M["black"], front, s0, front + 46, s1, z, z + 10, section="Sliding tracks")
    mid = (s0 + s1) / 2
    for i, (d0, d1, plane) in enumerate(((s0 + 3, mid + 12, front), (mid - 12, s1 - 3, front + 24)), 1):
        p.box(M["walnut"], plane, d0, plane + 18, d1, base + 10, BEAM - 31,
              section=f"Sliding door {i}")
        pull = d0 + 37 if i == 1 else d1 - 37
        p.box(M["steel"], plane - 4, pull - 9, plane, pull + 9, F(900), F(1200),
              section="Handles")
    if single_width:
        shutters(p, M["walnut"], "y", a0, s0, 1, front, front + 18, base, BEAM - 20,
                 label="Single hinged door")
    p.build()


def bedroom_loft(key, label, y0, y1, doors):
    p = Piece(key, label, fixed=True)
    front = WARDROBE_FRONT
    back = 3353  # behind this line the main partition beam occupies the storage height
    p.box(M["carcass"], front + 18, y0, back, y1, BEAM, BEAM + 18, section="Cabinet frame")
    p.box(M["carcass"], front + 18, y0, back, y1, SOFFIT - 18, SOFFIT, section="Cabinet frame")
    p.box(M["carcass"], front + 18, y0, back, y1, 2570, 2588, section="Shelf")
    for i in range(doors + 1):
        y = min(y1 - 18, y0 + (y1 - y0) * i / doors)
        p.box(M["carcass"], front + 18, y, back, y + 18, BEAM + 18, SOFFIT - 18,
              section="Cabinet frame")
    shutters(p, M["walnut"], "y", y0, y1, doors, front, front + 18, BEAM, SOFFIT,
             label="Loft door", handle="h", hz=BEAM + 55)
    p.build()


wardrobe("cupboard_small", "Small bedroom cupboard", 5104, 7239,
         mirror_at_start=False, single_width=450)
bedroom_loft("loft_small", "Small bedroom overhead storage", 4204, 7124, 5)

# ---------------------------------------------------------------- Bedroom 1 (master)
# Head on the column face; long side against the window wall.
bed("bed_master", "Master bed (6 × 6 ft)", 1829, 1829, "-y", 115, 230)
wardrobe("cupboard_master", "Master bedroom cupboard", 115, 2075, mirror_at_start=True)
bedroom_loft("loft_master", "Master bedroom overhead storage", 230, 3974, 6)

# The 115 mm recess between the wall and the C1 face runs behind the headboard.
# End the cabinet at the aisle-side edge of the bed so the lower drawers face that aisle.
recess = Piece("bedside_storage", "Master bedside storage", fixed=True)
X0, X1 = 1200, 1994
Y0, Y1 = 115, 230
Z0, Z1 = F(1000), BEAM
recess.box(M["oak"], X0, Y0, X1, Y0 + 8, Z0, Z1, section="Cabinet interior")
for x0, x1 in ((X0, X0 + 16), (X1 - 16, X1)):
    recess.box(M["walnut"], x0, Y0 + 8, x1, Y1, Z0, Z1, section="Cabinet frame")
for z in (Z0, Z0 + 320, Z0 + 640, Z0 + 960, Z1 - 16):
    section = "Cabinet frame" if z in (Z0, Z1 - 16) else "Shelf boards"
    recess.box(M["walnut"] if section == "Cabinet frame" else M["oak"],
               X0 + 16, Y0 + 8, X1 - 16, Y1 - 15, z, z + 16, section=section)

# Recessed glass within a single framed door facing the bed. The pull is beside the aisle.
glass_door(recess, M["walnut"], X0 + 18, X1 - 18, Y1 - 15, Y1, Z0 + 18, Z1 - 18,
           frame="Glass door frame", pane="Glass pane")
recess.box(M["steel"], X1 - 37, Y1, X1 - 25, Y1 + 16, Z0 + 85, Z0 + 230, section="Glass door pull")

# The headboard hides the lower cabinet front. The four drawer fronts face +x.
recess.box(M["walnut"], X1 - 400, Y0, X1 - 2, Y1, F(0), F(75), section="Drawer housing")
recess.box(M["walnut"], X1 - 400, Y1 - 14, X1 - 2, Y1, F(75), Z0, section="Drawer housing")
for i in range(4):
    z = F(75 + i * 227)
    recess.box(M["walnut"], X1 - 17, Y0 + 3, X1, Y1 - 17, z + 2, z + 225, section=f"Drawer front {i + 1}")
    recess.box(M["steel"], X1, Y0 + 25, X1 + 12, Y1 - 39, z + 184, z + 197, section="Drawer pulls")
recess.build()

# Computer table along the shared bedroom wall (y 4089), from the window-wall corner.
desk = Piece("desk", "Computer table")
T = 25
H = 750
desk.box(M["oak"], 115, 3489, 1615, 4089, F(H - T), F(H), bevel=3, section="Desktop")        # top, 1500 x 600
desk.box(M["white"], 1597, 3489, 1615, 4089, F(0), F(H - T), section="Outer side panel")
desk.box(M["white"], 115, 3489, 133, 4089, F(0), F(H - T), section="Window-side panel")
desk.box(M["white"], 133, 4071, 1597, 4089, F(300), F(H - T), section="Back panel")
desk.build()

# ---------------------------------------------------------------- kitchen
# Base units (trolleys) under the open granite platform, between the existing granite supports.
KF = 20                  # fronts set back from the counter edge
KZ0, KZ1 = F(100), TOP - 20 - 4
runA = Piece("trolleys_sink", "Kitchen trolleys (sink side)")
fa0, fa1 = 7349 + KF, 7349 + KF + 18
runA.box(M["carcass"], fa1, 2365, 7979, 3480, KZ0, KZ1, section="Cabinet frame")
runA.box(M["carcass"], fa1, 3520, 7979, 5078, KZ0, KZ1, section="Cabinet frame")
runA.box(M["kick"], fa1 + 30, 2365, 7979, 3480, F(0), KZ0, section="Plinth")
runA.box(M["kick"], fa1 + 30, 3520, 7979, 5078, F(0), KZ0, section="Plinth")
shutters(runA, M["slate"], "y", 2365, 3480, 2, fa0, fa1, KZ0, KZ1, label="Sink door", handle="h")          # sink unit, 2 doors
for unit, (a0, a1) in enumerate(((3520, 4299), (4299, 5078)), 1):                                               # 3-drawer trolleys
    for drawer, (z0, z1) in enumerate(((KZ0, F(360)), (F(360), F(620)), (F(620), KZ1)), 1):
        shutters(runA, M["slate"], "y", a0, a1, 1, fa0, fa1, z0, z1, label=f"Unit {unit} · Drawer {drawer}", handle="h")
runA.build()

runB = Piece("trolleys_drawing", "Kitchen trolleys (drawing-room side)")
fb0, fb1 = 5078 + KF, 5078 + KF + 18
runB.box(M["carcass"], 5848, fb1, 7349, 5693, KZ0, KZ1, section="Cabinet frame")
runB.box(M["kick"], 5848, fb1 + 30, 7349, 5693, F(0), KZ0, section="Plinth")
for unit, (a0, a1) in enumerate(((5848, 6599), (6599, 7349)), 1):
    for drawer, (z0, z1) in enumerate(((KZ0, F(360)), (F(360), F(620)), (F(620), KZ1)), 1):
        shutters(runB, M["slate"], "x", a0, a1, 1, fb0, fb1, z0, z1, label=f"Unit {unit} · Drawer {drawer}", handle="h")
runB.build()

# Wall cupboard over the drawing-room-side counter: from 2 ft above the counter to the ceiling,
# along the whole wall (stub wall x 5848 to the tiled wall x 7991). The loft part sits in front of the beam.
WC0 = TOP + 610
wc = Piece("cupboard_kitchen", "Kitchen wall cupboard")
FY0, FY1 = 5713 - 350, 5713 - 350 + 18
KX0, KX1 = 5848, 7991
for z in (WC0, BEAM - 18):
    wc.box(M["carcass"], KX0, FY1, KX1, 5713, z, z + 18, section="Cabinet frame")
wc.box(M["carcass"], KX0, 5703, KX1, 5713, WC0 + 18, BEAM - 18, section="Cabinet frame")
door_width = (KX1 - KX0) / 4
for i in range(5):
    x = min(KX1 - 16, KX0 + i * door_width)
    wc.box(M["carcass"], x, FY1, x + 16, 5703, WC0 + 18, BEAM - 18, section="Cabinet frame")
for i in range(4):
    x = KX0 + i * door_width
    glass_door(wc, M["white"], x + 1.5, x + door_width - 1.5, FY0, FY1, WC0 + 1.5, BEAM - 1.5,
               frame=f"Lower door {i + 1}", pane=f"Lower glass pane {i + 1}")
    pull = x + (door_width - 15 if i % 2 == 0 else 15)
    wc.box(M["steel"], pull - 6, FY0 - 22, pull + 6, FY0, WC0 + 40, WC0 + 240, section="Handles")
    wc.box(M["carcass"], x + 16, FY1 + 12, min(KX1 - 16, x + door_width), 5703,
           WC0 + 390, WC0 + 408, section="Shelf boards")
wc.box(M["carcass"], KX0, FY1, KX1, 5598, BEAM, SOFFIT, section="Cabinet frame")
shutters(wc, M["white"], "x", KX0, KX1, 4, FY0, FY1, BEAM, SOFFIT, label="Loft door", handle="h", hz=BEAM + 40)
wc.build()

print("furniture:", [o.name for o in coll.objects if o.type == "EMPTY"])
