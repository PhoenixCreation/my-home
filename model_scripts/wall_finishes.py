"""Give interior painted faces room/wall materials before web export.

Split shared structure at room boundaries so opposite sides of a partition and
long beams can be painted independently. Tile, wood, glass and ceilings are untouched.
Directions follow the drawing: north is +Y, east is +X.
"""
import bpy
import bmesh
from mathutils import Vector

# Interior bounds in metres, including beam/column projections.
ROOMS = {
    'master': (0.115, 0.115, 3.468, 4.089),
    'small': (0.115, 4.204, 3.468, 7.239),
    'ensuite': (3.583, 0.725, 4.883, 2.825),
    'bathroom': (4.998, 0.115, 6.284, 2.210),
    'wash': (6.399, 0.725, 7.999, 2.710),
    'dining': (3.583, 2.940, 5.733, 5.713),
    'kitchen': (5.848, 2.940, 7.999, 5.713),
    'drawing': (3.583, 5.828, 7.999, 8.953),
}


def prepare_wall_finishes():
    materials = {}
    for obj in bpy.data.collections['I-601'].all_objects:
        if obj.type != 'MESH' or not any(
            m and m.name in {'I601_Wall_Paint_White', 'I601_RCC_Painted'}
            for m in obj.data.materials
        ):
            continue
        if any(m and m.name.startswith('I601_Paint_') for m in obj.data.materials):
            continue  # Already prepared in a saved model; exporting again is a no-op.
        # The dedicated Walk ceiling follows its own finish control.
        if obj.get('walk_ceiling'):
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        for axis in (0, 1):
            cuts = sorted({bounds[i] for bounds in ROOMS.values() for i in (axis, axis + 2)})
            for cut in cuts:
                point, normal = Vector((0, 0, 0)), Vector((0, 0, 0))
                point[axis], normal[axis] = cut, 1
                bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                                      dist=0.00001, plane_co=point, plane_no=normal)
        bm.normal_update()
        for face in bm.faces:
            if abs(face.normal.z) > 0.5:
                continue
            original = obj.data.materials[face.material_index]
            if original.name not in {'I601_Wall_Paint_White', 'I601_RCC_Painted'}:
                continue
            # Probe into the room on the visible side of this face.
            p = face.calc_center_median() + face.normal * 0.04
            room = next((key for key, (x0, y0, x1, y1) in ROOMS.items()
                         if x0 < p.x < x1 and y0 < p.y < y1), None)
            if not room:
                continue
            if abs(face.normal.x) > abs(face.normal.y):
                side = 'west' if face.normal.x > 0 else 'east'
            else:
                side = 'south' if face.normal.y > 0 else 'north'
            key = (room, side, original.name)
            if key not in materials:
                material = original.copy()
                material.name = f'I601_Paint_{room}_{side}_{original.name}'
                materials[key] = material
            material = materials[key]
            if material.name not in obj.data.materials:
                obj.data.materials.append(material)
            face.material_index = obj.data.materials.find(material.name)
        bm.to_mesh(obj.data)
        bm.free()
    print(f'Prepared {len(materials)} room wall finishes')
