# Flat I-601: 3D Model Specification

Project: **SUN FOOTPRINTS** (Sun Builder, Ahmedabad). Architect: Mansi Shah Architects, project no. A-1012.
Unit: **I-601**, Block I, 6th floor. Unit type **"201-1401"**.

Everything in this document was extracted from the DWG/PDF files in `Diagrams/`. You should not need the drawings again. Companion image: `I-601_top_view.png`.

> **Update: checked against the site photos in `real_images/`.** The as-built flat matches this plan. Where the photos differ from or settle a question in the drawings, the photo wins. Those items are marked **[photo]** below and summarised in §12.

---

## 0. Sources and how I-601 maps to them

| File | Used for |
|---|---|
| `BLOCK-I___J_UNIT_PLAN_24-02-2026.dwg` / `.pdf` | Plan geometry, door/window schedule, safety-railing section |
| `BLOCK_I_201_-_1401_UNIT_FLOOR_PLAN.pdf` | The same 201-1401 sheet at A3, 1:50 (cross-check) |
| `BLOCK-I_TOILET_AND_KITCHEN_DETAIL_R3_12.3.26.dwg` | Toilet sections (tile height, fixtures). Drawn for unit 101; layout is identical to 201-1401 |
| `BLOCK-I_and_J_Kitchen_Detail_15.7.23.dwg` | Kitchen platform height and stone |
| `R0_TYP._FL._LTG_BLOCK-I_AND_J.dwg` | Lighting layout (not transcribed; see Missing #14) |

- The plan titled **"2ND TO 4TH. & 6TH. & 7TH. & 9TH. TO 12TH. & 14TH. FLOOR PLAN"** contains unit "201-1401", so the 6th floor uses this plan. Floors 5, 8 and 13 are different and are not covered.
- The A3 sheet title reads "FIRST FLOOR UNIT PLAN…201-1401". That title is wrong: the content is the typical-floor plan.
- Each floor has units x01–x06. **I-601 is the "01" unit** on the 6th floor of Block I.
- General note on the drawings: *all dimensions in mm, all measurements from the UNFINISHED surface* (brick/RCC face, before plaster).

---

## 1. Coordinate system used in this document

- Units are **mm**. Plan coordinates are `(x, y)`, height is `z`.
- **Origin (0,0)** is the outer bottom-left corner of Bedroom 1's corner column, in sheet orientation.
- **+x** runs to the right, from the bedrooms towards the kitchen/staircase side.
- **+y** runs up the sheet, from the toilets/duct side towards the drawing room and main door.
- **z = 0** is the structural slab top (SSL) of the 6th floor. Finished floor level **FFL = z +80**.
- All x/y values describe the unfinished masonry/RCC outline, matching the drawings.

### Real-world orientation of Block I
The architect draws the 201-1401 unit as the **Block J copy**, and the top-down image follows that orientation. In the site layout of the DWG, the Block I copy is the **same plan rotated 180° without mirroring**: DWG `X_I = 1747298 − X_J`, `Y_I = 1067543 − Y_J`.
- For a correctly oriented Block-I model, build in the local frame below and then rotate 180° about the z axis.
- In local terms: `x' = 8229 − x`, `y' = 9183 − y`.
- The plan is identical either way; only the compass direction changes, and no true north is given (see Missing #1).
- DWG reference: local (0,0) = J-copy model point (863286, 504339).

---

## 2. Overall envelope

| Item | Value |
|---|---|
| Main rectangle (outer faces) | x 0 – 8229, y 0 – 9183 |
| Projections outside the rectangle | ODU ledges at x −600 – 0 (two, on the bedroom side) |
| Inside the rectangle but not part of the flat | Lower-terrace void at x 115–2753, y 7354–9010, and the ODU ledge for W01 |
| Neighbours | +x side (x > 8229): common **staircase**. +y side (y > 9183): **lift** (x 4316–6296) and **lift lobby/passage** (x 6526–8229), y 9183–11391 |
| External faces (open air) | Left face x = 0; bottom face y = 0 (bedroom, duct, wash projection); terrace-void faces |

---

## 3. Walls (plan polygons, outer outline, unfinished)

Every wall is full height, from SSL to the slab soffit above. Exceptions are the openings in §5, which have beams/lintels over them.

**Thicknesses:**
- Most walls are **115 mm**, including the external walls at x = 0 and y = 0.
- **230 mm** walls: the right wall x 7999–8229 (stair side) and the top walls at y 8953–9183.
- Columns are 230 mm wide (§4).

| # | Wall | Polygon vertices (x, y) |
|---|---|---|
| W-A | Bottom wall of Bedroom 1, plus Bedroom 1 / Toilet 1 partition lower part | (0,0) (3583,0) (3583,2075) (3468,2075) (3468,115) (115,115) (115,1200) (0,1200) |
| W-B | Bedroom 1 left wall above window, and Bedroom 1 / Bedroom 2 partition | (0,2750) (115,2750) (115,4089) (3583,4089) (3583,4204) (115,4204) (115,4604) (0,4604) |
| W-C | Bedroom 2 left wall above window, top wall, and Bedroom 2 / Dining partition | (3583,7453) (3353,7453) (3353,7354) (0,7354) (0,6154) (115,6154) (115,7239) (3468,7239) (3468,5104) (3583,5104) |
| W-D | Toilet 1 walls: right side, bottom with V01, top towards dining, plus the partition stub between D03 and D02 | (3468,2825) (4883,2825) (4883,725) (4133,725) (4133,610) (4998,610) (4998,2940) (3583,2940) (3583,3189) (3468,3189) |
| W-E | Toilet 2 walls: bottom, right side towards wash, top with D03 | (4883,0) (6399,0) (6399,2325) (5748,2325) (5748,2210) (6284,2210) (6284,115) (4883,115) |
| W-F | Right wall (230, stair side), kitchen top wall, kitchen stub | (5733,4928) (5848,4928) (5848,5713) (7999,5713) (7999,0) (8229,0) (8229,9183) (7999,9183) (7999,5828) (5733,5828) |
| W-G | Top wall, left part (230) | (2753,8953) (4086,8953) (4086,9183) (2753,9183) |
| W-H | Top wall between lift core and main door (230) | (6526,8953) (6949,8953) (6949,9183) (6526,9183) |
| W-I | ODU ledge end wall, Bedroom 1 (L-shape) | (−600,900) (0,900) (0,1015) (−485,1015) (−485,1200) (−600,1200) |
| W-J | ODU ledge end wall, Bedroom 2 (L-shape) | (−600,6154) (−485,6154) (−485,6339) (0,6339) (0,6454) (−600,6454) |

Notes:
- The polygons overlap the columns in §4 at their ends. Model them as a union.
- From x 3583 to 4086, the drawing room's top wall is W-G. From x 4086 to 6526 it is the lift-core RCC wall (§4).
- Common-area walls, for context only: lift-shaft right wall (6296–6526, 9183–9762) and (6296–6526, 10812–11391), with the lift door gap at y 9762–10812. Lobby top wall (6526–8169, 11391–11506).

---

## 4. RCC columns and core (solid black on the drawings)

| Column | x range | y range | Size |
|---|---|---|---|
| C1 | 0 – 1200 | 0 – 230 | 1200 × 230 **[photo]**. The drawing shows 230 × 950 along the window wall, but the master-bedroom photo shows the pier on the bottom wall, like C3 in Bedroom 2 |
| C2 | 3353 – 3583 | 0 – 1200 | 230 × 1200 |
| C3 | 0 – 1200 | 7124 – 7354 | 1200 × 230 |
| C4 | 3353 – 3583 | 6154 – 7354 | 230 × 1200 on the drawing. **Not built [owner]**: the Bedroom 2 / drawing room wall is a plain 115 wall here; removed from the model |
| C5 | 7999 – 8229 | 610 – 1810 | 230 × 1200 |
| C6 | 7999 – 8229 | 3466 – 4666 | 230 × 1200 |
| C7 | 7999 – 8229 | 7983 – 9183 | 230 × 1200 |
| Lift core (C-shape) | outline (6526,11621) (4086,11621) (4086,8953) (6526,8953) (6526,9183) (4316,9183) (4316,11391) (6526,11391) | | 230 thick |

All columns are full height. Beam layout is not provided (Missing #4).

---

## 5. Openings

Heights are from **SSL (z=0)**. Add −80 to get heights above the finished floor. "Beam bottom" is **z = 2375**, which is the head of every door and window.

### 5.1 Doors (schedule: sill "–", lintel = BEAM BOTTOM)

| Tag | Room / use | Wall | Opening position | Width | Height (SSL) | Leaf / swing (as drawn) |
|---|---|---|---|---|---|---|
| D01 | Main door, from lobby into the drawing room | Top wall, y 8953–9183 | x 6949 – 7999 | 1050 | 0 – 2375 | **Not drawn** |
| D02 | Bedroom 2 (upper) | Partition x 3468–3583 | y 4204 – 5104 (frame jambs 50 each, clear 4254–5054 = 800) | 900 | 0 – 2375 | Leaf 800 × 30 drawn open **into Bedroom 2**. Hinge at x≈3533, y 4254 (bottom jamb) |
| D02 | Bedroom 1 (lower) | Partition x 3468–3583 | y 3189 – 4089 | 900 | 0 – 2375 | **Not drawn**. Assume the mirror of Bedroom 2's door: hinge at y≈4039, opening into Bedroom 1 |
| D03 | Toilet 1 (en-suite, from Bedroom 1) | Partition x 3468–3583 | y 2075 – 2825 (jambs 50, clear 2125–2775 = 650) | 750 | 0 – 2375 | Leaf 650 × 30 opens **into Toilet 1**. Hinge at x≈3533, y 2775 (top jamb) |
| D03 | Toilet 2 (common, from dining passage) | Wall y 2210–2325 | x 4998 – 5748 (jambs 50, clear 5048–5698 = 650) | 750 | 0 – 2375 | Leaf 650 × 30 opens **into Toilet 2**. Hinge at x≈5048, y 2275 (left jamb) |

Door frames are 50 mm wide jambs running the full wall depth. Door leaves are 30 mm thick.

### 5.2 Windows and ventilators

| Tag | Room | Wall | Opening position | Width | Sill (SSL) | Head (SSL) | Height | Frame line in plan |
|---|---|---|---|---|---|---|---|---|
| W01 | Drawing room, onto ODU ledge | x 3353–3583 (230 wall) | y 7453 – 8953 | 1500 | **830** (FFL +750) **[photo]** | 2375 | **1545** **[photo]**. The schedule's 2145 is a typo | x 3388–3418, y 7481–8918 |
| W02 | Bedroom 1, onto ODU ledge | x 0–115 | y 1200 – 2750 | 1550 | 830 (FFL +750) | 2375 | 1545 | x 35–80, y 1235–2715 |
| W02 | Bedroom 2, onto ODU ledge | x 0–115 | y 4604 – 6154 | 1550 | 830 (FFL +750) | 2375 | 1545 | x 35–80, y 4639–6119 |
| W03 | Wash | y 610–725 | x 6399 – 7999 | 1600 | 1130 (FFL +1050) | 2375 | 1245 | y 645–690, x 6434–7964 |
| V01 | Toilet 1, into duct | y 610–725 | x 3583 – 4133 | 550 | 1175 (derived) | 2375 | 1200 | y 645–690, x 3618–4098 |
| V02 | Toilet 2, into duct | x 4883–4998 | y 115 – 610 (≈472 clear) | 472 | 1775 (derived) | 2375 | 600 | x 4918–4948, y 150–575 |

- W02 section detail: sill stone at 830 SSL. The height 1545 is made up of 1465 plus 4 × 20 stone/plaster bands.
- The windows are sliding windows "as per vendor", with a 40×25 MS box section welded in.
- The toilet detail shows V01 framed by 20 mm stone. In the toilet elevation, V01 starts 1123 above the toilet floor and is 1172 + 2×20 high.

---

## 6. Rooms (clear internal sizes, unfinished)

| Room | x range | y range | Size (mm) | Area (m²) | Floor | Notes |
|---|---|---|---|---|---|---|
| Bedroom 1 (lower) | 115 – 3468 | 115 – 4089 | 3353 × 3974 | 13.32 | normal | Has W02, D02, and D03 to the en-suite |
| Bedroom 2 (upper) | 115 – 3468 | 4204 – 7239 | 3353 × 3035 | 10.18 | normal | Has W02 and D02. **No door to the lower terrace** |
| Toilet 1 (en-suite) | 3583 – 4883 | 725 – 2825 | 1300 × 2100 | 2.73 | sunk 300 | Has V01 |
| Toilet 2 (common) | 4998 – 6284 | 115 – 2210 | 1286 × 2095 | 2.69 | sunk 300 | Has V02 |
| Wash | 6399 – 7999 | 725 – 2325 | 1600 × 1600 | 2.56 | sunk 300 | Open to the kitchen at y 2325. Has W03 |
| Kitchen | 5848 – 7999 | 2940 – 5713 | 2151 × 2773 | 5.96 | normal | Open to the dining room (x < 5848, below y 4928) and to the wash |
| Dining + passage | 3583 – 5848 | 2940 – 5828 (passage to Toilet 2 at x 4998–5748, y 2325–2940) | ≈2150 × 2888 | ≈6.2 | normal | Open plan with the drawing room |
| Drawing room | 3583 – 7999 | 5828 – 8953 (open to the dining room below y 5828 for x < 5733) | 4416 × 3125 | 13.80 | normal | Has W01 and D01. The lift shaft is directly behind its top wall |

Check dimensions from the sheet:
- Bottom chain: 600 | 3583 | 1300 | 1517 | 1600 | 230.
- Right chain: 610 | 1200 | 1656 | 725 | 115 | 360 | 3316 | 1200.
- Drawing room 4417 wide. Dining-to-top 6013. Kitchen 2152 wide, 1988 + 785 deep.
- Top chain: 1334 | 1980 (lift interior) | … | 1050 (D01).

The sunk 300 mm slab covers x 3583–7999, y 840–2695 (both toilets and the wash) and x 4983–6299, y 100–610 (lower part of Toilet 2). It is filled back up to FFL. This only matters for a structural model; a visual model can ignore it.

---

## 7. External elements

| Element | Geometry | Level / detail |
|---|---|---|
| ODU ledge, Bedroom 1 | Slab x −600 – 0, y 1015 – 2900. End wall W-I at the y≈900–1200 end. Edge lines at x −600 / −575 / −510 / −485 and y 2785 / 2810 / 2875 / 2900 | "Projection @ beam bottom level". The slab top is ≈410 below room SSL (slab 125 + 20 tile + stone). An MS safety railing runs on the open sides (x = −600 and y = 2900), full height from the ledge to the projection above. Outdoor unit at x −358 to −142, y 1200–2000 |
| ODU ledge, Bedroom 2 | Slab x −600 – 0, y 4454 – 6339. End wall W-J at y 6154–6454. Railing on x = −600 and y = 4454 | Same as above. Outdoor unit at x −358 to −142, y 5354–6154 |
| ODU ledge for W01 | x 2753 – 3353, y 7354 – 8953. Railing/edge lines at x 2753, 2778, 2828 | Same detail. Outdoor unit at x 2995–3211, y 8084–8884 |
| Lower terrace (void) | x 115 – 2753, y 7354 – 9010. Edge/parapet lines at y 9010 and 9125 | **Not part of I-601.** Drawn in "below-cut" linetype, so it is the terrace roof of a lower floor (1st-floor unit 101 has a TERRACE here). No door opens to it from I-601 |
| Duct / shaft | x 3583 – 4883, y 0 – 610 (X-crossed) | Open service shaft, "Covering as per detail". Receives V01 and V02 |
| Wash projection | x 6399 – 7999, y 0 – 610 | Projection at beam-bottom level below W03. Drawing label: "Proj… @ beam bottom" |

**Safety railing (typical section):**
- 16 mm MS pipes, 20×40 MS box sections, and a 45×25 MS Z-section.
- 20 mm stone sill. Drip mould at the ledge edge.
- Runs from the ledge slab up to the projection/beam above.

---

## 8. Vertical data (typical floor section)

| Item | z from SSL | Notes |
|---|---|---|
| Structural slab top (SSL) | 0 | |
| Finished floor (FFL) | +80 | 80 mm floor finish |
| Window W02/W01 sill | +830 | FFL +750 |
| Wash W03 sill | +1130 | FFL +1050 |
| Beam bottom = door/window head | +2375 | FFL +2295 |
| Beam overall depth | 575 (beam bottom to the slab top above) | Drawing shows a "405" drop under the slab |
| Next slab top (SSL of the 7th floor) | +2950 | Floor-to-floor height 2950 |
| Slab thickness | ≈150–170 (derived, not dimensioned) | |
| Ceiling plaster | 20 | |
| Clear room height FFL → ceiling | ≈2700 | Modelling assumption |
| Kitchen platform top | ≈900 above floor | 20 mm Kadappa stone top |
| Toilet wall tiles | 2275 high from the toilet floor | Plaster above. Tiles laid with 4 mm grooves, horizontal + vertical fit joints |
| Toilet 2 ODU / exhaust | Exhaust fan and fixed glass in the ventilator (Toilet Section C) | |

If you model the 6th floor in the building: 6th-floor SSL = ground SSL + Σ(floor heights). Ground and first-floor heights are not given (Missing #9).

---

## 9. Fixtures (plan positions)

### Toilet 1 (x 3583–4883, y 725–2825)
- Basin counter 4433–4883 × 2325–2825 (450 × 500). Basin bowl Ø400 centred at (4658, 2575).
- Plumbing ledge/wall behind the WC: 4733–4883 × 1425–2325 (150 deep). Height ≈650 (Section C dimension, verify).
- WC bowl ≈600 × 380 centred at ≈(4420, 1870), facing −x. Section B shows an "open flush tank" above the WC.
- Shower zone at the bottom: mixer/diverter on wall x 4883 at y≈1063, floor trap at (4697, 1063).
- Geyser, mirror over the basin, and exhaust fan in V01.

### Toilet 2 (x 4998–6284, y 115–2210)
- Basin counter 5834–6284 × 1710–2210. Bowl Ø400 at (6059, 1960).
- Plumbing ledge 6135–6284 × 810–1710 (150 deep).
- WC centred at ≈(5820, 1250), facing −x.
- Shower at the bottom: mixer on wall x 6284 at y≈448, trap at (6098, 448). V02 is above, on the left wall.

### Kitchen and wash
- **As built [photo]:** an open 20 mm granite slab with **no cabinets underneath**. It sits on 40 mm granite supports: an end fin at y 2325–2365 rising to z≈1290 (between the sink and the wash), a mid support at y≈3500, and a support at the inner corner of run B (x≈7349). The hob is not installed; only a gas pipe and sockets are present. The fridge space is empty.
- L-shaped platform, 900 high:
  - Run A along the right wall: x 7349–7999 (650 deep), y 2325–5713.
  - Run B along the kitchen top wall: y 5078–5713 (635 deep), x 5833–7349.
- Sink 400 × 400 at x 7435–7835, y 2440–2840.
- Hob 438 × 600 at x 7411–7849, y 3510–4110.
- Fridge space (block 650 × 550) at x 5733–6383, y 2350–2900.
- Wash area: washing-machine inlet/outlet and bib cock (kitchen detail). Drain via the 300 sunk slab.

### AC indoor units (wall-mounted, 197 deep × 900 long) — drawn but not installed [photo]; not modelled
- Bedroom 1: x 100–297, y 1272–2172.
- Bedroom 2: x 100–297, y 5182–6082.
- Drawing room: x 3583–3780, y 6904–7804.

### Furniture (indicative, from the plan) — not modelled (flat is unfurnished)
- Beds 1650 × 1800: x 673–2323, y 245–2045 (Bedroom 1) and y 5309–7109 (Bedroom 2). Side tables 200 deep at the head.
- Wardrobes 560 deep: x 2898–3458, y 125–2005 (Bedroom 1) and y 5104–7229 (Bedroom 2).
- Dining table 1300 × 875 at x 4408–5708, y 4940–5815, with 4 chairs Ø350.
- Drawing room:
  - L-sofa along x 3607–4203 and y 8333–8928.
  - Centre table Ø750 at (5102, 7551).
  - Armchairs at x 5947–6585 and 6735–7374, y 5853–6469.
  - TV unit 200 × 1650 at x 7790–7990, y 6028–7678.
  - Side unit at x 6443–6613, y 8343–8928.

---

## 10. Suggested build recipe

1. Extrude every wall polygon (§3) and column (§4) from z=0 to z=2950−slab (≈2800). Union them.
2. Cut the openings (§5) from z=sill to z=2375. Doors start at z=0.
3. Add a lintel/beam band from z=2375 to the soffit over all openings. Beams on the wall lines are optional; the beam grid is unknown.
4. Floor slab: 150 thick below z=0, over the envelope polygon. Add the FFL topping at +80, except in wet areas if modelling the sunk slab.
5. Ceiling slab at z≈2800–2950.
6. Add the ledges/projections (§7) at z≈−410 (top), with open railings to z≈1230 (see §12).
7. Leave the lower-terrace area as a void.
8. Place the fixtures (§9).
9. Rotate 180° if you need Block-I site orientation.

---

## 11. Missing / ambiguous items (exactly what is not in the drawings)

| # | Missing item | Why it matters | What exists / what I assumed |
|---|---|---|---|
| 1 | **True north / site orientation** | Sun studies, real facade orientation | Only the generic title-block north block (rotation 0) and no site plan. Block I is the J plan rotated 180°. Absolute north is unknown; a site/key plan is needed |
| 2 | ~~W01 sill/height conflict~~ **Resolved [photo]** | Window shape in the drawing room | Photos show sill 830 / height 1545, like W02. The schedule's 2145 is a typo |
| 3 | **Slab thickness** | Exact floor/ceiling | Not dimensioned. Section implies ≈150–170 (beam depth 575, drop 405). Assumed 150 |
| 4 | **Beam layout / structural plan** (partly resolved [photo]) | Ceiling drops, bulkheads | Still no structural drawing. Bulkheads visible in the photos were located with the matched cameras (§12); exact beam widths are still assumed (230) |
| 5 | ~~Door swings~~ **Resolved [photo]** | Door placement | D01 opens inward, hinged on the x 7999 (stair-side) jamb. Bedroom 1 door hinged at the y 4089 end. The other doors match the drawn swings |
| 6 | **Door/window shutter types and frame profiles** | Detailed model | Only "sliding window as per vendor" and the main-door paneling elevation, which shows the passage between 102 and 105 rather than 601. Sliding-panel count and mullions not given |
| 7 | **Finishes** (mostly resolved [photo]) | Materials/texturing | See §12. Toilets were not photographed, so their tiles still follow the drawing (2275 high) |
| 8 | **False ceiling** | Ceiling geometry | None shown. Assume plain plastered slab |
| 9 | **Absolute levels** (ground and first-floor heights, 6th-floor SSL above ground) | Placing the flat in the building | Only the typical floor-to-floor of 2950 is given. Ground (shops) and 1st-floor heights are unknown |
| 10 | **Toilet floor drop / threshold heights** | Steps at toilet/wash doors | Sunk slab 300 is given; the finished toilet floor level relative to FFL (usually −10 to −20) is not |
| 11 | ~~Ledge railing height~~ **Resolved [photo]** | Railing model | Not a full-height grill. An open MS railing with posts at ≈600 c/c and a top rail at ≈+1.23 m above room SSL (measured 1.19–1.30 from three photos) |
| 12 | **Lower terrace status** | Whether it belongs to the flat | Labelled "LOWER TERRACE", no access door. Treated as a void open to the sky, not part of I-601 |
| 13 | **Floors 5 / 8 / 13 differ** | What is directly below/above the flat (5th and 7th) | The 7th floor is the same typical plan. The 5th-floor plan is not in the set, so what lies beneath the terrace void is unknown |
| 14 | **Electrical / lighting points** | Lights/switches in the model | A lighting DWG exists (`R0_TYP._FL._LTG…`) but positions were not transcribed. Ask if you want them |
| 15 | **Kitchen exhaust/chimney duct position** | Kitchen detail | Kitchen detail mentions "CHIMNEY DUCT / EXH. DUCT" and a socket for the chimney but gives no dimensioned location in the typical unit |
| 16 | **Exact WC/fixture models and heights** | Fixture detail | WC/basin plan footprints are approximate (±30 mm, read from the plan). Basin height not dimensioned; standard 800–850 assumed |
| 17 | **Wall plaster thickness** | Finished room sizes | Drawings are unfinished-surface. Internal plaster thickness is not given; typically 12–15 mm per face |

Everything else needed for a complete shell model (all walls, columns, openings, room sizes, ledges and main heights) is specified above.


---

## 12. As-built verification from site photos (`real_images/`)

All eight photos were camera-matched to the model. For each photo I solved the camera pose from known corners, door/window edges and floor lines. All photos share one focal length, ≈505 px at 1280 px width, i.e. a phone ultrawide with ≈103° horizontal FOV.

| Photo | Camera position (x, y, z m) | Fit error (rms px) |
|---|---|---|
| enterance | (7.88, 9.06, 1.65) | 2.6 |
| drawing_room_corner_shot | (7.37, 6.30, 1.57) | 5.5 |
| dinning_area | (4.53, 7.34, 1.66) | 4.4 |
| kitchen | (4.14, 4.84, 1.82) | 5.6 |
| kitchen_2 | (6.10, 3.06, 1.57) | 2.2 |
| wash_area | (6.69, 3.48, 1.50) | 7.1 |
| small_bedroom | (3.55, 4.98, 1.54) | 6.8 |
| msater_bedroom | (3.58, 3.22, 1.54) | 6.3 |

The low errors confirm the plan geometry: room sizes, all door and window positions, the open kitchen and the wash. The cameras are saved in `I-601_photo_cameras.json`. In the `.blend` file they appear as `PhotoCam_*` cameras with the photo as a background image.

**Corrections and additions taken from the photos:**
- **Column C1** runs along the bottom wall (0–1200 × 0–230), not along the window wall.
- **W01** has sill 830 and height 1545.
- **Beams** (bottom at z 2375, to the soffit), seen as bulkheads:
  - along the window walls (x 0–230);
  - Bedroom 1 bottom wall (y 0–230);
  - between the bedrooms (y 3974–4204);
  - Bedroom 2 top wall (y 7124–7354);
  - partition line x 3353–3583;
  - right wall;
  - top wall;
  - over W03/V01 (y 610–840);
  - across the dining/toilet/kitchen line (y 2710–2940, x 3583–7999);
  - across the kitchen/drawing line (y 5598–5828, x 3583–7999).
- **Ceiling** measures about 2.80–2.85 m above SSL, consistent with the assumed 2.80 soffit.
- **Floor**:
  - 600 × 600 (2 ft) white glossy vitrified tiles, axis-aligned, ~3 mm dark joints. Each zone has its own joint grid, measured by rectifying the floor in each photo (accuracy about ±2 cm):
    - Drawing + dining + kitchen (one continuous grid): full tiles start at the main-door corner. Joints at x = 7999 − 600n and y = 8953 − 600n, so the cut row is against the x 3583 wall (≈215 mm) and the toilet wall y 2940 lands on a joint.
    - Bedroom 1: joints at x = 3468 − 600n (full tiles from the door wall, ≈350 mm cut at the window wall) and y = 4054 − 600n (≈35 mm cut row along the shared bedroom wall).
    - Bedroom 2: joints at x = 3468 − 600n and y = 7239 − 600n (full tiles from the top wall, ≈35 mm cut row along the shared bedroom wall).
    - Skirting pieces are cut from the same tiles, and their joints line up with the floor joints.
  - About 100 mm tile skirting.
  - The wash has a dark grey anti-skid floor.
- **Walls**: all painted white, including columns and beams.
- **Kitchen**:
  - beige-brown 1200 × 300 wall tiles on the x 7999 wall, from the counter up to beam bottom (≈2.35–2.45 m measured);
  - no tiles on the run-B wall;
  - granite counter construction as in §9.
- **Wash**: beige-brown tiles on all three walls up to the W03 sill (z 1130, measured 1.11–1.15), with a granite capping.
- **Doors**: dark granite frames on all doors (wide on the main door) and white flush laminated internal leaves.
- **Windows**:
  - black aluminium 2-track sliding frames with a dark granite reveal lining;
  - W03 also has a fixed top light ≈420 mm deep.
- **Not installed**: AC indoor/outdoor units, hob, all furniture.

## 13. Planned furniture (in the model, movable in the web viewer)

Built by `model_scripts/furniture_blender.py`. Positions are the starting layout; each piece can be moved, rotated and reset in the web page.

| Piece | Footprint (x × y, mm) | Height | Notes |
|---|---|---|---|
| 3-seater sofa | 3603–4483 × 5340–7440 | 800 | Against the long solid wall shared with Bedroom 2 (x 3583), facing the drawing room |
| Small bedroom bed | 115–1537 × 5144–7124 | headboard 1000 | 4.5 × 6.25 ft mattress; head on the top wall (C3 face), side on the window wall, opposite the door |
| Small bedroom cupboard | 2858–3468 × 5104–7239 | to beam bottom (2295 above floor) | 2 ft deep, on the wall shared with the drawing/dining room |
| Master bed | 490–2369 × 230–2134 | headboard 1000 | 6 × 6 ft mattress; head on the wall opposite the shared bedroom wall |
| Master bedroom cupboard | 2743–3353 × 115–2075 | to beam bottom | 2 ft deep from the C2 column face, on the wall shared with Toilet 1, up to the toilet door |
| L-shaped computer table | 115–1615 × 3489–4089 and 115–715 × 2289–3489 | 750 | In the corner facing the entry door (window wall / shared bedroom wall) |
| Kitchen trolleys, sink side | under run A, y 2365–3480 (sink unit, 2 doors) and 3520–5078 (two 3-drawer trolleys) | under the counter | Between the existing granite supports |
| Kitchen trolleys, drawing-room side | under run B, x 5848–7349 | under the counter | Two 3-drawer trolleys |
| Kitchen wall cupboard | 5848–7991 × 5363–5713 | from 610 above the counter (z 1590) to the ceiling | Whole run-B wall; the loft part sits in front of the beam |
