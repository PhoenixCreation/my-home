"""Solve pinhole cameras for the real photos from point + line correspondences.

World frame = model local frame in metres (x, y, z), z = 0 at SSL, FFL = 0.08.
Point:  (X, Y, Z) -> (u, v)
Line:   3D line given by two points A, B; image samples (u, v) must lie on its projection.
"""
import json, sys
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation as Rot

W, H = 1280, 721
CX, CY = W / 2, H / 2

PHOTOS = {
    "enterance": dict(
        pts=[((5.733, 5.828, 0.08), (517, 490)),
             ((3.583, 5.104, 0.08), (641, 418)), ((3.583, 5.104, 2.375), (642, 222)),
             ((3.583, 4.204, 0.08), (590, 408)), ((3.583, 4.204, 2.375), (590, 225)),
             ((3.583, 4.089, 0.08), (580, 403)), ((3.583, 4.089, 2.375), (580, 230)),
             ((3.583, 3.189, 0.08), (537, 392)), ((3.583, 3.189, 2.375), (537, 232)),
             ((3.583, 7.453, 2.375), (849, 200)), ((3.583, 7.453, 0.83), (846, 385))],
        lines=[(((0, 5.828, 0.08), (10, 5.828, 0.08)), [(150, 609), (350, 545)]),
               (((3.583, 0, 0.08), (3.583, 10, 0.08)), [(800, 455)])],
        init=dict(pos=(7.3, 9.0, 1.4), look=(3.6, 4.2, 1.2))),
    "drawing_room_corner_shot": dict(
        pts=[((3.583, 8.953, 0.08), (570, 470)),
             ((3.583, 8.953, 2.375), (568, 228)), ((3.583, 8.953, 0.83), (568, 393)),
             ((3.583, 7.453, 2.375), (385, 208)), ((3.583, 7.453, 0.83), (392, 412)),
             ((6.949, 8.953, 0.08), (1010, 666)), ((6.949, 8.953, 2.375), (1055, 126))],
        lines=[(((3.583, 0, 0.08), (3.583, 10, 0.08)), [(100, 585), (300, 535)]),
               (((0, 8.953, 0.08), (10, 8.953, 0.08)), [(700, 524), (900, 608)])],
        init=dict(pos=(7.2, 6.3, 1.4), look=(3.6, 8.9, 1.2))),
    "dinning_area": dict(
        pts=[((3.583, 5.104, 0.08), (812, 608)), ((3.583, 5.104, 2.375), (850, 108)),
             ((3.583, 4.204, 0.08), (772, 522)), ((3.583, 4.204, 2.375), (790, 150)),
             ((3.583, 4.089, 0.08), (766, 505)), ((3.583, 4.089, 2.375), (772, 168)),
             ((3.583, 3.189, 0.08), (733, 463)), ((3.583, 3.189, 2.375), (745, 182)),
             ((3.583, 2.940, 0.08), (728, 450)),
             ((4.998, 2.325, 0.08), (570, 432)), ((4.998, 2.325, 2.375), (569, 200)),
             ((5.748, 2.325, 0.08), (502, 430)), ((5.748, 2.325, 2.375), (500, 201)),
             ((6.399, 2.325, 0.08), (432, 430)), ((6.399, 2.325, 2.375), (430, 195)),
             ((5.733, 4.928, 0.08), (390, 580))],
        lines=[],
        init=dict(pos=(5.0, 7.0, 1.4), look=(5.0, 2.3, 1.2))),
    "kitchen": dict(
        pts=[((4.998, 2.325, 0.08), (838, 560)), ((4.998, 2.325, 2.375), (842, 136)),
             ((5.748, 2.325, 0.08), (770, 535)), ((5.748, 2.325, 2.375), (770, 150)),
             ((4.998, 2.940, 0.08), (838, 650)),
             ((6.399, 2.325, 0.08), (680, 500)), ((6.399, 2.325, 2.375), (680, 155))],
        lines=[(((7.349, 0, 0.98), (7.349, 10, 0.98)), [(200, 455), (450, 405)]),
               (((7.999, 0, 0.98), (7.999, 10, 0.98)), [(200, 422), (450, 385)]),
               (((5.733, 4.928, 0), (5.733, 4.928, 3)), [(98, 150), (160, 500)])],
        init=dict(pos=(5.0, 6.5, 1.4), look=(7.0, 2.5, 1.0))),
    "kitchen_2": dict(
        pts=[((7.999, 5.713, 0.98), (552, 404)), ((7.349, 5.078, 0.98), (525, 440))],
        lines=[(((7.349, 0, 0.98), (7.349, 10, 0.98)), [(700, 491), (1000, 578)]),
               (((0, 5.078, 0.98), (10, 5.078, 0.98)), [(250, 503), (450, 457)]),
               (((7.999, 0, 0.98), (7.999, 10, 0.98)), [(900, 462)]),
               (((0, 5.713, 0.98), (10, 5.713, 0.98)), [(300, 455)]),
               (((7.999, 5.713, 0), (7.999, 5.713, 3)), [(550, 250), (550, 350)])],
        init=dict(pos=(6.2, 3.2, 1.4), look=(7.9, 5.6, 0.9))),
    "wash_area": dict(
        pts=[((7.999, 0.725, 2.375), (472, 118)), ((6.399, 0.725, 2.375), (780, 110)),
             ((7.999, 0.725, 1.13), (478, 333)), ((6.399, 0.725, 1.13), (770, 338))],
        lines=[(((6.399, 2.325, 0), (6.399, 2.325, 3)), [(872, 10), (836, 460)]),
               (((7.999, 0, 1.13), (7.999, 10, 1.13)), [(250, 395), (400, 355)]),
               (((6.399, 0, 1.13), (6.399, 10, 1.13)), [(790, 390), (820, 440)])],
        init=dict(pos=(7.2, 3.2, 1.4), look=(7.2, 0.7, 1.4))),
    "small_bedroom": dict(
        pts=[((0.115, 4.204, 0.08), (90, 590)), ((0.115, 7.124, 0.08), (585, 460)),
             ((1.200, 7.124, 0.08), (690, 505)),
             ((0.115, 4.604, 2.375), (108, 103)), ((0.115, 4.604, 0.83), (152, 432)),
             ((0.115, 6.154, 2.375), (455, 160)), ((0.115, 6.154, 0.83), (465, 392))],
        lines=[(((0, 7.239, 0.08), (10, 7.239, 0.08)), [(800, 550), (1000, 640)])],
        init=dict(pos=(3.0, 4.5, 1.4), look=(0.5, 7.0, 1.2))),
    "msater_bedroom": dict(
        pts=[((0.115, 1.2, 2.375), (567, 222)), ((0.115, 1.2, 0.83), (570, 418)),
             ((0.115, 2.75, 2.375), (775, 207)), ((0.115, 2.75, 0.83), (768, 440)),
             ((0.115, 4.089, 0.08), (970, 585))],
        lines=[(((0.115, 0, 0.08), (0.115, 10, 0.08)), [(600, 515), (850, 562)])],
        init=dict(pos=(3.2, 3.6, 1.4), look=(0.1, 1.8, 1.2))),
}


def look_rot(pos, look):
    f = np.array(look, float) - np.array(pos, float)
    f /= np.linalg.norm(f)
    r = np.cross(f, [0, 0, 1.0]); r /= np.linalg.norm(r)
    d = np.cross(f, r)                        # image-down direction
    Rcw = np.stack([r, d, f])                 # rows: cam axes in world (cv convention)
    return Rcw


def project(params, X):
    rv, C, fpx = params[:3], params[3:6], params[6]
    R = Rot.from_rotvec(rv).as_matrix()
    Xc = (R @ (np.asarray(X) - C).T).T
    return np.stack([fpx * Xc[:, 0] / Xc[:, 2] + CX, fpx * Xc[:, 1] / Xc[:, 2] + CY], 1), Xc[:, 2]


def residuals(params, d):
    res = []
    if d["pts"]:
        X = np.array([p[0] for p in d["pts"]]); u = np.array([p[1] for p in d["pts"]], float)
        uv, z = project(params, X)
        res.extend((uv - u).ravel())
        res.extend(np.minimum(z, 0.2) * 0 + np.where(z < 0.2, (0.2 - z) * 1e3, 0))
    for (A, B), samples in d["lines"]:
        uv, _ = project(params, np.array([A, B], float))
        a, b = uv
        n = np.array([b[1] - a[1], a[0] - b[0]]); n /= np.linalg.norm(n) + 1e-12
        for s in samples:
            res.append(float(np.dot(np.array(s, float) - a, n)))
    return np.array(res)


def solve(name, d):
    best = None
    R0 = look_rot(d["init"]["pos"], d["init"]["look"])
    rv0 = Rot.from_matrix(R0).as_rotvec()
    for f0 in (380, 450, 520, 600, 700, 850):
        for dp in ((0, 0, 0), (0.6, 0, 0), (-0.6, 0, 0), (0, 0.6, 0), (0, -0.6, 0)):
            x0 = np.r_[rv0, np.array(d["init"]["pos"]) + dp, f0]
            lb = [-np.inf] * 3 + [-2, -2, 0.6] + [250]
            ub = [np.inf] * 3 + [11, 13, 2.2] + [1500]
            try:
                r = least_squares(residuals, x0, args=(d,), bounds=(lb, ub), loss="soft_l1", f_scale=6)
            except Exception:
                continue
            if best is None or r.cost < best.cost:
                best = r
    p = best.x
    res = residuals(p, d)
    npts = 2 * len(d["pts"])
    rms_p = float(np.sqrt(np.mean(res[:npts] ** 2))) if npts else 0.0
    rms_l = float(np.sqrt(np.mean(res[npts + len(d["pts"]):] ** 2))) if d["lines"] else 0.0
    R = Rot.from_rotvec(p[:3]).as_matrix()
    out = dict(name=name, R_cw=R.tolist(), C=p[3:6].tolist(), f_px=float(p[6]),
               rms_pts=rms_p, rms_lines=rms_l, hfov_deg=float(2 * np.degrees(np.arctan(CX / p[6]))))
    return out


if __name__ == "__main__":
    names = sys.argv[1:] or list(PHOTOS)
    allres = {}
    for n in names:
        o = solve(n, PHOTOS[n])
        allres[n] = o
        print(f"{n:26s} C=({o['C'][0]:.2f},{o['C'][1]:.2f},{o['C'][2]:.2f}) f={o['f_px']:.0f}px "
              f"hfov={o['hfov_deg']:.0f} rms_pts={o['rms_pts']:.1f} rms_lines={o['rms_lines']:.1f}")
    json.dump(allres, open("/tmp/opencode/sf/cams.json", "w"), indent=1)


F_FIXED = 505.0

def solve_fixed(name, d, f=F_FIXED):
    R0 = look_rot(d["init"]["pos"], d["init"]["look"]); rv0 = Rot.from_matrix(R0).as_rotvec()
    best = None
    for dp in ((0, 0, 0), (0.6, 0, 0), (-0.6, 0, 0), (0, 0.6, 0), (0, -0.6, 0), (0, 0, 0.3)):
        x0 = np.r_[rv0, np.array(d["init"]["pos"]) + dp]
        kw = {}
        if "bounds" in d:
            lo, hi = d["bounds"]
            x0[3:6] = np.clip(x0[3:6], np.array(lo) + 1e-3, np.array(hi) - 1e-3)
            kw["bounds"] = ([-np.inf] * 3 + list(lo), [np.inf] * 3 + list(hi))
        r = least_squares(lambda p: residuals(np.r_[p, f], d), x0, loss="soft_l1", f_scale=6, **kw)
        if best is None or r.cost < best.cost:
            best = r
    p = np.r_[best.x, f]
    res = residuals(p, d)
    npts = 2 * len(d["pts"])
    per = [float(np.hypot(res[2 * i], res[2 * i + 1])) for i in range(len(d["pts"]))]
    return dict(name=name, R_cw=Rot.from_rotvec(p[:3]).as_matrix().tolist(), C=p[3:6].tolist(), f_px=f,
                rms_pts=float(np.sqrt(np.mean(res[:npts] ** 2))) if npts else 0.0,
                per_point=per, line_res=[float(v) for v in res[npts + len(d["pts"]):]])

def run_fixed(names=None):
    out = {}
    for n in names or PHOTOS:
        o = solve_fixed(n, PHOTOS[n]); out[n] = o
        print(f"{n:26s} C=({o['C'][0]:.2f},{o['C'][1]:.2f},{o['C'][2]:.2f}) rms={o['rms_pts']:.1f} "
              f"pts={[round(v) for v in o['per_point']]} lines={[round(v) for v in o['line_res']]}")
    return out
