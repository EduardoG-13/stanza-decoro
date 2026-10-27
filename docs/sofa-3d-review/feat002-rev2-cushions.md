# FEAT-002 rev2: refitting the loose cushions (revision 1.3.0)

This replaces [feat002-before-after.md](feat002-before-after.md). The first FEAT-002 fix was rejected
because the five cushions still looked bunched, passed through each other and sank into the backrest.
**The rejection was correct.** The metric used to accept that fix was wrong, and the fix also deformed
the wrong face. Everything below was measured or captured again for this revision; no earlier
evidence is reused.

Before = commit `4830ea4` (revision 1.2.0). The deploy preview served byte-identical GLBs (sha256
`d37860160d55721b…` / `87b37c88be7854ef…`, `max-age=0,must-revalidate`), so caching was ruled out
and the geometry was the cause.

## 1. Findings that correct earlier conclusions

### 1.1 The "~0 % embedded" metric (INSPECTION I.4) was wrong
I.4 counted ray-parity crossings against `seat_cover` after the 1.5 mm SOLIDIFY had been applied.
That makes the seat a double shell. A point deep inside the seat crosses both skins, gets an even
count and is classed as "outside", so only points inside the 1.5 mm skin were counted. Running that
same I.4 test again on the 4830ea4 geometry gives 1–4 vertices "inside" per cushion. The corrected
test gives **69–101 vertices inside, up to 89 mm deep**.

Corrected method (`validation/feat002-rev2/*.json`): the closest-point distance to single, closed
outer shells (`seat_cover` / `back_cover` mesh data *without* the solidify, each `cushion_0N_cover`),
with inside/outside decided by a majority vote of ray parity in three directions. Both directions of
each pair are tested (A's vertices in B and B's vertices in A), plus the welt tube vertices.

**What this means:** the earlier conclusion that the cushions "only graze the seat, so no reseating
is needed" was false. In 4830ea4 every cushion was buried 67–89 mm into the seat. cushion_01 was
113 mm inside the arm. All four neighbour pairs overlapped by 46–72 mm.

### 1.2 The `flatten` thinned the rear face, not the base
`pillow()` builds the cushion in local XZ (X = width, Z = height, v = −1 is the lower edge), with
thickness along local Y. Transforming the axes with each holder's world matrix (Blender: +Y = back,
+Z = up) gives:

| cushion | local +Y (pillow side=+1) → world | local +Z (height) → world |
|---|---|---|
| 01 | (0.16, **0.97**, −0.20) | (−0.26, 0.24, **0.94**) |
| 02 | (−0.14, **0.94**, −0.30) | (0.21, 0.32, **0.92**) |
| 03 | (0.12, **0.96**, −0.25) | (−0.17, 0.27, **0.95**) |
| 04 | (0.02, **0.96**, −0.28) | (−0.30, 0.27, **0.92**) |
| 05 | (0.33, **0.88**, −0.33) | (−0.36, 0.45, **0.82**) |

So `side=+1` is the **rear face** (it points towards the backrest). It is not the part that rests on
the seat. The old side-probe had compared the centroid heights of the two faces. Those differ by only
about 2–3 cm because of the backward tilt, which is how it came to label the rear face "lower". The
`flatten` term removed up to 70 % of that face's fill. The result was a half-thickness slab with a
planar facet and a crease, while the lower edge still sank into the seat. That facet is the sharp flat
patch visible in the old close-up.

### 1.3 Placement compared with SOFA-2.jpg
In 4830ea4 the cushion centres sat 30–35 cm in front of the backrest face (y −0.09…−0.23 vs backrest
y ≈ +0.28…+0.30). They stood mid-seat on their buried lower edges and touched nothing behind them.
cushion_01 (x −1.175…−0.682) was inside the arm loft, whose inner face is at x ≈ −1.0. In the photo
the cushions stand fairly upright, lean back and rest their lower edges on the rear of the seat. They
are staggered in depth and finish before the chaise.

### 1.4 Side finding: the frame poked through the cover (FEAT-003 regression)
The front and rear rails were straight boxes at y = −0.50 / +0.46, and the strap anchors sat at those
same y values. Where the bean outline curves inward, they came through the seat cover by up to
146 mm. That is the wooden bar visible under the seat in every earlier exterior render, including the
1.2.0 poster. This revision fixes it (see §2.4) because it was visibly wrong in the same acceptance
views.

## 2. What changed in `assets/sofa-pilot/source/build_sofa.py`

1. **`flatten` removed.** `pillow_shape()` keeps the knife-edge cushion (tapered seams, edge gathers)
   with a per-cushion `loft` (fill) and no whole-face thinning.
2. **Solved placement.** The new `CUSHIONS` literals (position, rotation, half-size, loft) were not
   guessed. An offline solver (sandbox-only, not shipped) translated each undeformed cushion until it
   overlapped the seat by 10 mm and what it leans on by 12 mm (backrest or arm) or 8 mm (a
   neighbour). It worked in `SETTLE_ORDER` (02, 04 against the backrest; then 03, 01, 05). Sizes are
   about 10–15 % smaller and the fill is thinner (0.07–0.084 vs 0.112), which suits a 45–50 cm cushion
   on this seat depth. Rotations were tuned by eye against renders. The composition matches the
   photo: 01 sits in the low arm/back corner and leans on 02; 02 and 04 rest against the backrest;
   03 (the tallest) and 05 sit one row forward and lean on their neighbours; 05 is tilted and ends
   before the chaise.
3. **`settle_contacts()`: localized contact deformation.** Each cushion is deformed in world space
   against the outer shells it touches: seat, backrest/arm and any cushion already settled.
   - Vertices that penetrate are pushed out along the collider normal. The displacement field is then
     Gaussian-smoothed over the cushion surface (45 mm radius) for 10 rounds, so the compression
     spreads as a soft falloff patch. On the seat this is the lower-edge band; against the backrest,
     arm or a neighbour it is a rear-face patch.
   - A difference-of-Gaussians ring adds a slight outward bulge around each patch, standing in for
     the displaced fill.
   - A final projection pass limits each contact to an allowed soft compression of 1.2 mm (seat and
     back) or 0.8 mm (cushion to cushion).
   - Measured result: the maximum displacement is 8.8–10.8 mm, and only 57–168 of 882 vertices per
     cushion move by more than 1 mm. The rest of the cushion is unchanged. There is no whole-face
     thinning and no planar facet.
4. **The welt follows the deformed knife edge.** It runs along the midpoint of the deformed front and
   rear perimeter rows and is kept 0.8 mm proud of every collider, so the seam stays visible. A
   welt-tube vertex can still sit at most 0.6–0.8 mm into the seat skin.
5. **Seat dimple (`seat_dimple()`).** It is now a shallow band, at most 16 mm deep (was 26 mm),
   centred under each cushion's real lower edge (5 cm forward of the holder). The seam tube still
   uses the same function.
6. **Frame fitted inside the contour.** The rails and the ends of the webbing straps are placed inside
   the upholstered outline. Same objects, materials and groups.

Unchanged: the 6 public groups; nodes `cushion_01..05` (+`_cover`/`_welt`); all materials and
bindings; FEAT-003 interior components; the FEAT-004 stages; triangles 49 064 / 24 280. The `.blend`
and both GLBs were regenerated together in one generator pass (bpy 5.0.1).

## 3. Before → after (corrected metric)

True maximum penetration depth in mm (0 = clear; ≤ 2 mm is the intended soft compression). Main
variant; mobile figures are in `validation/feat002-rev2/summary.json` and agree within 0.6 mm.

| cushion | seat: before → after | backrest/arm: before → after | contact type after |
|---|---|---|---|
| 01 | **89.4** → 1.2 (lower edge + lower-left corner) | **112.9 into the arm** (both faces + left edge) → 1.2 | lower-edge band on seat (67 cm² < 2 mm); rear-face left edge resting on the arm (39 cm²) |
| 02 | **88.0** → 1.2 | clear (151 mm away) → 1.7 | lower-edge band; rear-face patch on backrest (220 cm²) |
| 03 | **67.0** → 1.2 | clear → clear (92 mm; it leans on 02) | lower-edge band; rests on 02 |
| 04 | **73.3** → 1.3 | clear (267 mm away) → 1.4 | lower-edge band; rear-face patch on backrest (200 cm²) |
| 05 | **86.1** → 1.4 | clear → clear (123 mm; it leans on 04) | lower-edge band; rests on 04 |

| pair | before | after | contact after |
|---|---|---|---|
| 01-02 | **47.1** mm, 25 welt vertices inside the other | 1.9 mm, 0 welt | 01 rear right edge on 02 front face (82 cm²) |
| 02-03 | **62.8** mm, 59 welt | 1.2 mm, 0 welt | 03 rear left edge on 02 front face (62 cm²) |
| 03-04 | **46.4** mm, 120 welt | clear, 29 mm gap | none (only overlaps in front-view projection) |
| 04-05 | **72.2** mm, 69 welt | 1.2 mm, 0 welt | 05 rear upper-left corner on 04 front face (45 cm²) |
| non-adjacent | none touch (≥ 239 mm) | none touch (≥ 216 mm) | — |

**Projection vs volume:** in the front view, 01/02, 02/03, 03/04 and 04/05 overlap on screen. The
horizontal section at z = 0.62 m (diagnostics image, d3) shows five separate footprints, touching
only at the contacts listed above.

## 4. Visual acceptance (real web viewer, progress 0)

All images come from the real `createSofaViewer` (same `sofa-viewer.js` module, the same embedded
bouclé-areia finish and lighting) loaded in a capture-only harness page. The harness takes over the
viewer's own camera and OrbitControls for the custom close-ups. BEFORE = the 4830ea4 GLB through
`modelUrl`; AFTER = the new GLB. Same camera for each pair of images.

| image | what it shows |
|---|---|
| [feat002rev2_global_main.jpg](images/feat002rev2_global_main.jpg) | front, three-quarter left/right, side left/right, elevated top, cushion row |
| [feat002rev2_pairs_main.jpg](images/feat002rev2_pairs_main.jpg) | close-ups of pairs 01-02, 02-03, 03-04, 04-05 (front and from above) |
| [feat002rev2_backrest_main.jpg](images/feat002rev2_backrest_main.jpg) | cushion_01 against the arm; each cushion against the backrest from above |
| [feat002rev2_backrest_side_main.jpg](images/feat002rev2_backrest_side_main.jpg) | each cushion against backrest/neighbour, low three-quarter |
| [feat002rev2_seat_main.jpg](images/feat002rev2_seat_main.jpg) | each cushion's lower edge and welt on the seat (low camera) |
| [feat002rev2_mobile.jpg](images/feat002rev2_mobile.jpg), [feat002rev2_mobile_closeups.jpg](images/feat002rev2_mobile_closeups.jpg) | `sofa-mobile.glb`: key views and close-ups |
| [feat002rev2_velvet_grafite_main.jpg](images/feat002rev2_velvet_grafite_main.jpg) | the same fit in the dark velvet-grafite finish |
| [feat002rev2_layers_stages.jpg](images/feat002rev2_layers_stages.jpg) | layered opening at 0/.2/.35/.5/.6/.7/.85/1, before vs after (main) and after (mobile) |
| [feat002rev2_diagnostics_main.jpg](images/feat002rev2_diagnostics_main.jpg) | **DIAGNOSTIC, not acceptance:** a distinct debug colour per cushion; horizontal section z=0.62; vertical section at each cushion's X |

**Visual assessment, after.** The cushions read as five separate loose cushions. They stand upright
and lean back, their lower edges and welts sit on the seat, and 02/04 press lightly into the backrest.
Nothing passes through anything else: no welt disappears into a neighbour or the backrest. The
before images clearly show cushions merged into one another and the lower edges cut off flat by the
seat.

**Still imperfect (honest):**
- The contact compression is deliberately small: about 1 cm, spread out. On the light bouclé it
  reads mainly as a soft rounded rest with a contact shadow, not as an obvious dent.
- Cushions 03/04 do not touch (29 mm apart in volume). In the front view they look as if they
  overlap.
- The cushions are a little smaller than in the photo.
- With no fabric simulation, the shapes stay idealised knife-edge cushions.
- The overall model height dropped from 1.042 m to 0.993 m. The old maximum was cushion_03 poking
  ~8 cm above the backrest. The tallest cushion now finishes about level with the backrest top,
  closer to the photo.
- The wooden rail is no longer visible from outside (§1.4).

## 5. Revalidation (fresh, this revision)

- **Layers:** progress 0 → 1 after 5 full forward/back cycles through 13 points, in both variants.
  Group positions are identical; the 0 and 1 renders are pixel-identical to the initial 0
  (MAD 0.0, max 0). Relative to the upholstery, the cushion offset is ≥ 0 in Y (up) and ≥ 0 in Z
  (towards the front) at every stage, so the cushions only move away from the seat and backrest they
  rest on (stages image).
- **Customisation:** 6 combinations per variant on the product page. The fabric materials change on
  body, cushions and welts (velvet-terracota, linen-oliva renders). Returning to bouclé-areia uses the
  embedded maps and is pixel-identical to the initial render. `getSelection()` =
  `{modelId:'stanza-organic-01', revision:'1.3.0', fabricId, colorId}`. The quote redirect is
  unchanged (`npm test`). Per-cushion colour remains a separate proposal.
- **Validator:** Khronos glTF-Validator 2.0.0-dev.3.10. Both GLBs: 0 errors, 0 warnings, 56 infos
  (UNUSED_OBJECT / UNUSED_MESH_TANGENT on untextured illustrative meshes). Reports:
  `validation/gltf-validation-sofa*.json`.
- **Product page check** (`validation/feat002-rev2/viewer-check.json`): load, setFinish, setView (5
  presets), setProgress, getSelection; 0 console/page errors in main and mobile.
- `npm test` 19/19. `scripts/build.py --ignore-local-config --production --no-source-entries` and
  `scripts/check_site.py --production` OK (the manifest sha256 match the real bytes).

LIMITATION: WebGL runs on SwiftShader (software), headless; no physical phone, Safari or Firefox.
bpy 5.0.1 is used rather than Blender 5.2.
