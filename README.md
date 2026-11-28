# my-home

Interactive 3D walkthrough of flat I-601 (Block I), hosted on GitHub Pages.

**Live:** https://phoenixcreation.github.io/my-home/

## Contents

| Path | What |
| --- | --- |
| `index.html` | Self-contained Three.js walkthrough (the model is embedded) |
| `I-601_model.blend` | Blender source model |
| `I-601_3D_Spec.md` | Measured layout spec used to build the model |
| `I-601_top_view.png` | Top-down plan render |
| `I-601_photo_cameras.json` | Solved camera poses for the reference photos |
| `model_scripts/` | Blender build, furniture, web export and camera-solve scripts |
| `real_images/` | Reference photos of the flat |
| `Diagrams/` | Builder floor plans (DWG/PDF) |

## Rebuilding the model

Open `I-601_model.blend` in Blender and run these from `model_scripts/`, in order:

1. `build_blender.py`: walls, openings, finishes, floor tiles
2. `photo_cameras_blender.py`: cameras matched to the site photos
3. `furniture_blender.py`: the movable furniture
4. `export_web.py`: splits interior painted faces into room/wall finishes using `wall_finishes.py`, exports the model and embeds it in `index.html`

`finishes.py` regenerates `finish_strips.json` (skirting and wall tiles) and needs `shapely`.

## Wall finishes

Open **Wall color** to paint all walls, or expand a room for a room-wide color and
separate north/east/south/west wall colors. Directions follow the floor plan
(north is +Y in Blender). Opposite sides of shared partitions are independent.
Room resets inherit the whole-home paint; **Restore wall finish** clears all wall
customizations. Colors persist locally alongside furniture and door finishes.
The ceiling follows whole-home paint unless given its own color.

## Export and import

Open **Layouts** in the toolbar, then choose **Export** to download a JSON backup.
Use **Import** to load it on this or another device. Import replaces the current
layout, including furniture positions and rotations, folding/sliding configurations,
furniture visibility, furniture colors and uploaded textures, wall/room colors,
ceiling and door colors, and the camera view. Imported finishes and furniture are
also saved locally. Export first if you want to keep the layout you are replacing.
Files include the textures themselves; they do not need the original image files.
Invalid files or textures leave the current layout unchanged.

## Checks

Run `python3 tests/check_model.py`, `node tests/check_finishes.mjs`, and
`node tests/check_layouts.mjs` to check the
embedded room finishes, cupboard/loft bounds, saved colors, reset behavior, branding, layout round trips, and import failure handling.
