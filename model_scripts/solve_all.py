import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import camsolve as cs
d = cs.PHOTOS["kitchen"]
d["pts"] = [p for p in d["pts"] if p[0][:2] not in ((4.998, 2.325), (4.998, 2.940))]
d["lines"] = [l for l in d["lines"] if l[0][0][:2] != (5.733, 4.928)]
d["lines"].append((((4.998, 2.940, 0), (4.998, 2.940, 3)), [(856, 100), (845, 400), (838, 640)]))
m = cs.PHOTOS["msater_bedroom"]
m["pts"] += [((0.115, 0.230, 0.08), (465, 490)), ((1.2, 0.115, 0.08), (330, 531)), ((1.2, 0.230, 0.08), (345, 526)),
             ((0.115, 0.230, 2.375), (455, 232))]
m["bounds"] = ((0.3, 3.2, 1.2), (3.58, 4.05, 1.8))
m["init"] = dict(pos=(3.3, 3.6, 1.5), look=(0.1, 1.8, 1.2))
cs.PHOTOS["small_bedroom"]["bounds"] = ((0.3, 4.25, 1.2), (3.9, 7.0, 1.8))
o = cs.run_fixed()
json.dump(o, open(os.path.join(ROOT, "I-601_photo_cameras.json"), "w"), indent=1)
