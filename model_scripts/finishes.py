"""Precompute skirting and wall-tile (dado) strips with shapely; writes finish_strips.json."""
import json, os
from shapely.geometry import Polygon, box, LineString, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient

def rect(x0, y0, x1, y1):
    return box(x0, y0, x1, y1)

WALLS = [
    [(0,0),(3583,0),(3583,2075),(3468,2075),(3468,115),(115,115),(115,1200),(0,1200)],
    [(0,2750),(115,2750),(115,4089),(3583,4089),(3583,4204),(115,4204),(115,4604),(0,4604)],
    [(3583,7453),(3353,7453),(3353,7354),(0,7354),(0,6154),(115,6154),(115,7239),(3468,7239),(3468,5104),(3583,5104)],
    [(3468,2825),(4883,2825),(4883,725),(4133,725),(4133,610),(4998,610),(4998,2940),(3583,2940),(3583,3189),(3468,3189)],
    [(4883,0),(6399,0),(6399,2325),(5748,2325),(5748,2210),(6284,2210),(6284,115),(4883,115)],
    [(5733,4928),(5848,4928),(5848,5713),(7999,5713),(7999,0),(8229,0),(8229,9183),(7999,9183),(7999,5828),(5733,5828)],
]
SOLIDS = [Polygon(w) for w in WALLS] + [
    rect(2753, 8953, 4086, 9183), rect(6526, 8953, 6949, 9183),
    rect(0, 0, 1200, 230), rect(3353, 0, 3583, 1200), rect(0, 7124, 1200, 7354),
    rect(7999, 610, 8229, 1810), rect(7999, 3466, 8229, 4666), rect(7999, 7983, 8229, 9183),
    rect(4086, 8953, 6526, 9183),
]
WINDOW_GAPS = {  # gap rect -> sill z (SSL)
    (3353, 7453, 3583, 8953): 830, (0, 1200, 115, 2750): 830, (0, 4604, 115, 6154): 830,
    (6399, 610, 7999, 725): 1130, (3583, 610, 4133, 725): 1175, (4883, 115, 4998, 610): 1775,
}
SOLIDS += [rect(*g) for g in WINDOW_GAPS]
walls = unary_union(SOLIDS)
FOOT = Polygon([(0,0),(3583,0),(3583,610),(4883,610),(4883,0),(6399,0),(6399,610),(7999,610),(7999,0),
                (8229,0),(8229,9183),(2753,9183),(2753,8953),(3353,8953),(3353,7354),(0,7354)])
WET = {"toilet1": rect(3583, 725, 4883, 2825), "toilet2": rect(4998, 115, 6284, 2210),
       "wash": rect(6399, 725, 7999, 2325)}
free = FOOT.difference(walls)
dry = free.difference(unary_union(list(WET.values())))
wall_edge = walls.boundary.buffer(1.5)

def strips(poly, t, z0, ztop, window_cap=True):
    out = []
    polys = [poly] if poly.geom_type == "Polygon" else list(poly.geoms)
    for p in polys:
        p = orient(p, 1.0)
        for ring in [p.exterior] + list(p.interiors):
            cs = list(ring.coords)
            for a, b in zip(cs[:-1], cs[1:]):
                seg = LineString([a, b])
                on = seg.intersection(wall_edge)
                if on.is_empty:
                    continue
                parts = [on] if on.geom_type == "LineString" else [g for g in getattr(on, "geoms", []) if g.geom_type == "LineString"]
                dx, dy = b[0] - a[0], b[1] - a[1]
                L = (dx * dx + dy * dy) ** 0.5
                nx, ny = -dy / L, dx / L          # interior is on the left
                for q in parts:
                    (x0, y0), (x1, y1) = q.coords[0], q.coords[-1]
                    if ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5 < 20:
                        continue
                    # split along the segment at window gaps (tile stops at the sill there)
                    Lq = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
                    cuts = [(0.0, Lq, ztop)]
                    if window_cap:
                        line = LineString([(x0, y0), (x1, y1)])
                        for g, s in WINDOW_GAPS.items():
                            ov = line.intersection(box(*g).buffer(2))
                            if ov.is_empty or ov.length < 5 or s >= ztop:
                                continue
                            t0 = line.project(Point(ov.coords[0])); t1 = line.project(Point(ov.coords[-1]))
                            t0, t1 = sorted((t0, t1))
                            new = []
                            for c0, c1, zt in cuts:
                                if t1 <= c0 or t0 >= c1:
                                    new.append((c0, c1, zt)); continue
                                if t0 > c0: new.append((c0, t0, zt))
                                new.append((max(c0, t0), min(c1, t1), min(zt, s)))
                                if t1 < c1: new.append((t1, c1, zt))
                            cuts = new
                    ux, uy = (x1 - x0) / Lq, (y1 - y0) / Lq
                    for c0, c1, top in cuts:
                        if c1 - c0 < 5:
                            continue
                        ax, ay = x0 + ux * c0, y0 + uy * c0
                        bx, by = x0 + ux * c1, y0 + uy * c1
                        xs = [ax, bx, ax + nx * t, bx + nx * t]
                        ys = [ay, by, ay + ny * t, by + ny * t]
                        out.append([min(xs), min(ys), max(xs), max(ys), z0, top])
    return out

res = {
    "skirting": strips(dry, 10, 80, 180, window_cap=False),
    "toilet_dado": strips(WET["toilet1"], 8, 81, 81 + 2275) + strips(WET["toilet2"], 8, 81, 81 + 2275),
    "wash_dado": strips(WET["wash"], 8, 81, 1130),
}
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "finish_strips.json"), "w"))
print({k: len(v) for k, v in res.items()})
