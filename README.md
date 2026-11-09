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
4. `export_web.py`: exports the model and embeds it in `index.html`

`finishes.py` regenerates `finish_strips.json` (skirting and wall tiles) and needs `shapely`.
