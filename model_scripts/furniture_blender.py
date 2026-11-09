"""Add movable furniture to the I-601 model (run after build_blender.py).

Each piece is an Empty named FURN_<key> at the centre of its footprint, on the finished floor, with
its parts as child meshes. The web viewer finds the pieces through the custom properties
(furniture / label / size_mm), which are exported to glTF as extras. Coordinates are in mm,
in the same local frame as build_blender.py (z = 0 at SSL, finished floor at +80).
"""
import bpy, bmesh

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
def mat(name, rgb, rough=0.6, metal=0.0):
    m = bpy.data.materials.new("I601F_" + name)
    m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    for ident, val in (("Base Color", (*rgb, 1.0)), ("Roughness", rough), ("Metallic", metal)):
        s = next(s for s in p.inputs if s.identifier == ident)
        s.default_value = val
    m.diffuse_color = (*rgb, 1.0)
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
)

# ---------------------------------------------------------------- helpers
class Piece:
    """Collect boxes (world mm) per material, then build child meshes around the footprint centre."""
    def __init__(self, key, label):
        self.key, self.label, self.parts = key, label, {}

    def box(self, material, x0, y0, x1, y1, z0, z1, bevel=0.0):
        self.parts.setdefault((material, bevel), []).append((x0, y0, x1, y1, z0, z1))
        return self

    def build(self):
        # footprint and size ignore the handles, so the reported depth is the carcass + shutter depth
        allb = [b for (m, _), bs in self.parts.items() if m is not M["steel"] for b in bs]
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
        coll.objects.link(emp)
        if root:
            emp.parent = root
        for i, ((material, bevel), bs) in enumerate(self.parts.items()):
            bm = bmesh.new()
            for (a0, b0, a1, b1, c0, c1) in bs:
                g = bmesh.ops.create_cube(bm, size=1.0)
                vs = g["verts"]
                for v in vs:
                    v.co.x = ((a0 if v.co.x < 0 else a1) - cx) * S
                    v.co.y = ((b0 if v.co.y < 0 else b1) - cy) * S
                    v.co.z = ((c0 if v.co.z < 0 else c1) - FFL) * S
                if bevel:
                    edges = list({e for v in vs for e in v.link_edges})
                    bmesh.ops.bevel(bm, geom=edges, offset=bevel * S, segments=2, affect="EDGES",
                                    profile=0.5, clamp_overlap=True)
            me = bpy.data.meshes.new(f"FURN_{self.key}_{material.name[6:]}")
            bm.to_mesh(me)
            bm.free()
            for poly in me.polygons:
                poly.use_smooth = bool(bevel)
            ob = bpy.data.objects.new(f"FURN_{self.key}_part{i}_{material.name[6:]}", me)
            ob.data.materials.append(material)
            coll.objects.link(ob)
            ob.parent = emp
        return emp

def shutters(p, fmat, along, a0, a1, n, plane0, plane1, z0, z1, gap=3, handle="v", hz=None):
    """n equal door/drawer fronts between a0..a1 on a front plane (plane0 < plane1, the carcass is
    behind plane1). along='y': fronts face -x (plane is x); along='x': fronts face -y (plane is y)."""
    w = (a1 - a0) / n
    for i in range(n):
        s0, s1 = a0 + i * w + gap / 2, a0 + (i + 1) * w - gap / 2
        if along == "y":
            p.box(fmat, plane0, s0, plane1, s1, z0 + gap / 2, z1 - gap / 2)
        else:
            p.box(fmat, s0, plane0, s1, plane1, z0 + gap / 2, z1 - gap / 2)
        # handle on the outer face; every front here faces towards the lower coordinate
        hp0, hp1 = plane0 - 22, plane0
        if handle == "v":                        # vertical bar near the meeting edge of door pairs
            edge = s1 - 40 if i % 2 == 0 else s0 + 40
            hz0, hz1 = (hz if hz else ((z0 + z1) / 2 - 180, (z0 + z1) / 2 + 180))
            if along == "y":
                p.box(M["steel"], hp0, edge - 8, hp1, edge + 8, hz0, hz1)
            else:
                p.box(M["steel"], edge - 8, hp0, edge + 8, hp1, hz0, hz1)
        elif handle == "h":                      # horizontal bar near the top edge (drawers)
            hzc = hz if hz else z1 - 45
            m0, m1 = (s0 + s1) / 2 - min(160, w / 3), (s0 + s1) / 2 + min(160, w / 3)
            if along == "y":
                p.box(M["steel"], hp0, m0, hp1, m1, hzc - 8, hzc + 8)
            else:
                p.box(M["steel"], m0, hp0, m1, hp1, hzc - 8, hzc + 8)

def F(h):
    """Height above the finished floor -> SSL z."""
    return FFL + h

# ---------------------------------------------------------------- drawing room: 3-seater sofa
# Back against the top wall (y 8953, lift side), facing the dining room, with one end about 300 from
# the W01 window wall (x 3583).
sofa = Piece("sofa", "3-seater sofa")
LEN, DEP, ARM = 2100, 880, 180
SX0, BACK = 3583 + 300, 8953 - 20             # left end (x) and back face (y)
def sbox(material, u0, v0, u1, v1, z0, z1, bevel=0.0):
    """u along the sofa from its x-start, v from the back towards the front (-y)."""
    sofa.box(material, SX0 + u0, BACK - v1, SX0 + u1, BACK - v0, z0, z1, bevel)
for (lu, lv) in ((40, 40), (40, DEP - 80), (LEN - 80, 40), (LEN - 80, DEP - 80)):
    sbox(M["black"], lu, lv, lu + 40, lv + 40, F(0), F(70))
sbox(M["fabric"], 0, 0, LEN, DEP, F(70), F(260), bevel=15)                         # base
sbox(M["fabric"], ARM, 0, LEN - ARM, 170, F(260), F(800), bevel=25)                # back frame
for u0, u1 in ((0, ARM), (LEN - ARM, LEN)):
    sbox(M["fabric"], u0, 0, u1, DEP, F(260), F(620), bevel=30)                    # arms
seat = (LEN - 2 * ARM) / 3
for i in range(3):
    a, b = ARM + i * seat + 4, ARM + (i + 1) * seat - 4
    sbox(M["cushion"], a, 340, b, DEP - 20, F(260), F(440), bevel=35)              # seat cushions
    sbox(M["cushion"], a, 170, b, 340, F(270), F(760), bevel=40)                   # back cushions
sofa.build()

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
    p.box(M["walnut"], fx0, hb0, fx1, hb1, F(0), F(head_h), bevel=8)                  # headboard
    p.box(M["walnut"], fx0, fy0, fx1, fy1, F(60), F(320), bevel=6)                    # bed box
    p.box(M["kick"], fx0 + 60, fy0 + 60, fx1 - 60, fy1 - 60, F(0), F(60))             # recessed plinth
    mx0, mx1 = fx0 + 25, fx1 - 25
    my0, my1 = (fy0 + 25, fy1) if head_side == "+y" else (fy0, fy1 - 25)
    p.box(M["mattress"], mx0, my0, mx1, my1, F(320), F(520), bevel=30)
    # throw over the foot half
    if head_side == "+y":
        ty0, ty1 = my0 - 15, my0 + (my1 - my0) * 0.55
    else:
        ty0, ty1 = my1 - (my1 - my0) * 0.55, my1 + 15
    p.box(M["throw"], mx0 - 15, ty0, mx1 + 15, ty1, F(470), F(535), bevel=20)
    # pillows at the head
    n = 2
    pw = (mx1 - mx0 - 60 * (n + 1)) / n
    for i in range(n):
        a = mx0 + 60 + i * (pw + 60)
        if head_side == "+y":
            p.box(M["pillow"], a, my1 - 420, a + pw, my1 - 60, F(520), F(640), bevel=45)
        else:
            p.box(M["pillow"], a, my0 + 60, a + pw, my0 + 420, F(520), F(640), bevel=45)
    return p.build()

# 4.5 x 6.25 ft mattress, in the corner opposite the door: head on the top wall (column C3 face, y 7124),
# long side along the window wall.
bed("bed_small", "Small bedroom bed (4.5 × 6.25 ft)", 1372, 1905, "+y", 115, 7124 - 75 - 1905)

def wardrobe(key, label, along, a0, a1, front, depth, z_top=BEAM, n=4, fmat=None):
    """Full-height cupboard against a wall. along='y': wall at x, cupboard runs along y.
    front: the x (or y) of the shutter face; depth measured from the front towards the wall."""
    p = Piece(key, label)
    fmat = fmat or M["walnut"]
    sign = 1 if depth > 0 else -1
    back = front + depth
    c0, c1 = sorted((front + sign * 18, back))
    s0, s1 = sorted((front, front + sign * 18))
    if along == "y":
        p.box(M["carcass"], c0, a0, c1, a1, F(0), z_top)
        p.box(M["kick"], s0, a0, s1, a1, F(0), F(80))
    else:
        p.box(M["carcass"], a0, c0, a1, c1, F(0), z_top)
        p.box(M["kick"], a0, s0, a1, s1, F(0), F(80))
    shutters(p, fmat, along, a0, a1, n, s0, s1, F(80), z_top, handle="v")
    return p.build()

# On the wall shared with the drawing/dining room (x 3468), 2 ft deep, from the door frame to the top wall.
wardrobe("cupboard_small", "Small bedroom cupboard", "y", 5104, 7239, 3468 - 610, 610)

# ---------------------------------------------------------------- Bedroom 1 (master)
# 6 x 6 ft bed, head on the wall opposite the shared bedroom wall (column C1 face, y 230),
# centred between the window wall and the cupboard.
bed("bed_master", "Master bed (6 × 6 ft)", 1829, 1829, "-y", 1429 - (1829 + 50) / 2, 230)

# Cupboard on the wall shared with Toilet 1, 2 ft deep and flush to that wall (x 3468), up to the toilet
# door. Column C2 (x 3353-3583, y 0-1200) is boxed in inside the cupboard.
wardrobe("cupboard_master", "Master bedroom cupboard", "y", 115, 2075, 3468 - 610, 610)

# Computer table along the shared bedroom wall (y 4089), from the window-wall corner.
desk = Piece("desk", "Computer table")
T = 25
H = 750
desk.box(M["oak"], 115, 3489, 1615, 4089, F(H - T), F(H), bevel=3)        # top, 1500 x 600
desk.box(M["white"], 1597, 3489, 1615, 4089, F(0), F(H - T))              # end panels
desk.box(M["white"], 115, 3489, 133, 4089, F(0), F(H - T))
desk.box(M["white"], 133, 4071, 1597, 4089, F(300), F(H - T))             # modesty panel
desk.build()

# ---------------------------------------------------------------- kitchen
# Base units (trolleys) under the open granite platform, between the existing granite supports.
KF = 20                  # fronts set back from the counter edge
KZ0, KZ1 = F(100), TOP - 20 - 4
runA = Piece("trolleys_sink", "Kitchen trolleys (sink side)")
fa0, fa1 = 7349 + KF, 7349 + KF + 18
runA.box(M["carcass"], fa1, 2365, 7979, 3480, KZ0, KZ1)
runA.box(M["carcass"], fa1, 3520, 7979, 5078, KZ0, KZ1)
runA.box(M["kick"], fa1 + 30, 2365, 7979, 3480, F(0), KZ0)
runA.box(M["kick"], fa1 + 30, 3520, 7979, 5078, F(0), KZ0)
shutters(runA, M["slate"], "y", 2365, 3480, 2, fa0, fa1, KZ0, KZ1, handle="h")          # sink unit, 2 doors
for a0, a1 in ((3520, 4299), (4299, 5078)):                                               # 3-drawer trolleys
    for z0, z1 in ((KZ0, F(360)), (F(360), F(620)), (F(620), KZ1)):
        shutters(runA, M["slate"], "y", a0, a1, 1, fa0, fa1, z0, z1, handle="h")
runA.build()

runB = Piece("trolleys_drawing", "Kitchen trolleys (drawing-room side)")
fb0, fb1 = 5078 + KF, 5078 + KF + 18
runB.box(M["carcass"], 5848, fb1, 7349, 5693, KZ0, KZ1)
runB.box(M["kick"], 5848, fb1 + 30, 7349, 5693, F(0), KZ0)
for a0, a1 in ((5848, 6599), (6599, 7349)):
    for z0, z1 in ((KZ0, F(360)), (F(360), F(620)), (F(620), KZ1)):
        shutters(runB, M["slate"], "x", a0, a1, 1, fb0, fb1, z0, z1, handle="h")
runB.build()

# Wall cupboard over the drawing-room-side counter: from 2 ft above the counter to the ceiling,
# along the whole wall (stub wall x 5848 to the tiled wall x 7991). The loft part sits in front of the beam.
WC0 = TOP + 610
wc = Piece("cupboard_kitchen", "Kitchen wall cupboard")
FY0, FY1 = 5713 - 350, 5713 - 350 + 18
wc.box(M["carcass"], 5848, FY1, 7991, 5713, WC0, BEAM)
wc.box(M["carcass"], 5848, FY1, 7991, 5598, BEAM, SOFFIT)
shutters(wc, M["white"], "x", 5848, 7991, 4, FY0, FY1, WC0, BEAM, handle="v", hz=(WC0 + 40, WC0 + 240))
shutters(wc, M["white"], "x", 5848, 7991, 4, FY0, FY1, BEAM, SOFFIT, handle="h", hz=BEAM + 40)
wc.build()

print("furniture:", [o.name for o in coll.objects if o.type == "EMPTY"])
