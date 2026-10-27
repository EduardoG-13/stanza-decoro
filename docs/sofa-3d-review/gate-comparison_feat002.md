# Generator-Fidelity Gate — regenerated vs current GLBs

Executed before any FEAT-002 implementation edit, per the user's condition: run the ORIGINAL
`build_sofa.py` UNCHANGED in an isolated copy under bpy/Blender 5.0.1, regenerate BOTH GLBs to a
scratch path, and compare against the published GLBs on silhouette, assembly/hierarchy, materials,
textures, scale/bounds, and real-viewer behavior. Hash equality was NOT required; the goal was to
find RELEVANT content/appearance differences.

## How the gate was run

- Tool: `bpy` 5.0.1 (PyPI wheel) + GL runtime libs via `LD_LIBRARY_PATH=.agents/gllibs/...` (the
  honest version caveat from I.2 stands: the tracked `.blend` was authored in Blender 5.2 and opens
  in 5.0.1 in forward-compatibility mode; the generator rebuilds the scene from scratch, so this
  caveat does not affect the regenerated geometry — the script deletes all objects and re-creates
  them from the parametric literals).
- Isolation: the whole `assets/sofa-pilot/` tree was copied to `.agents/scratch/gate/sofa-pilot/`
  (gitignored). The copied, UNCHANGED `source/build_sofa.py` was run so ALL writes (both GLBs and
  `source/sofa.blend`) landed in the scratch copy. The published `models/*.glb` and tracked
  `source/sofa.blend` were never written.
- Original source preserved: `sha256(assets/sofa-pilot/source/sofa.blend)` =
  `709a52ee389cc9fb8a96ba8538b938715f93c05145a3d067d757e0a3dbf148e7` — CONFIRMED UNCHANGED after the
  whole gate (expected 709a52ee…). The two published GLBs also stayed at their tracked sha256
  (`c521e18b…` / `b482875c…`); `git status` clean on the tracked tree throughout.

Regenerated GLB hashes (scratch): `sofa.glb` = `c7b2b1e4…`, `sofa-mobile.glb` = `a247a1a4…`
(different from the published hashes, as the user anticipated — not a stop condition).

## Per-dimension comparison (current vs regenerated)

Structural data extracted by parsing the glTF JSON + BIN chunks of both files
(`.agents/scratch/glb_compare.py`; raw numbers in `.agents/scratch/gate/compare.json`).

### sofa.glb

| Dimension | Current | Regenerated | Verdict |
|---|---|---|---|
| Node count | 46 | 46 | identical |
| Node names (full set) | all 46 | all 46 | identical (incl. `sofa_root`, the 6 groups, `cushion_01..05` + `_cover`/`_welt`, seat/back covers, padding, frame, legs, suspension) |
| Triangles | 43 936 | 43 936 | identical |
| World bounds min | [-1.24335, 0, -0.54214] | [-1.24335, 0, -0.54214] | identical |
| World bounds max | [1.24335, 1.04422, 0.54214] | [1.24335, 1.04422, 0.54214] | identical |
| Dimensions (m) | [2.48669, 1.04422, 1.08427] | same | identical |
| Materials (names) | fabric_main, fabric_seam, frame_illustrative, legs_dark, padding_illustrative, suspension_illustrative | same 6 | identical |
| PBR params per material (base color, metallic, roughness, sheen, texture bindings) | — | — | identical for ALL 6 materials (byte-level JSON equality of the per-material parameter blocks) |
| Images | normal PNG 2 125 341 B; embedded-boucle-areia JPEG 26 088 B; embedded-boucle-roughness PNG **243 072 B** | normal PNG 2 125 341 B; areia JPEG **26 088 B (identical)**; roughness PNG **242 999 B** | one benign delta (see below) |
| File bytes | 3 970 980 | 3 970 908 (−72 B) | benign (PNG re-encode) |

### sofa-mobile.glb

| Dimension | Current | Regenerated | Verdict |
|---|---|---|---|
| Node count | 46 | 46 | identical |
| Triangles | 21 128 | 21 128 | identical |
| World bounds min/max | [-1.2432,0,-0.54199] / [1.2432,1.04422,0.54199] | same | identical |
| Materials (names + PBR params incl. sheen) | 6, as above | same | identical |
| Images | normal PNG 578 772 B; basecolor JPEG 26 088 B; roughness PNG **243 072 B** | normal PNG 578 772 B; basecolor JPEG **26 088 B (identical)**; roughness PNG **242 999 B** | one benign delta |
| File bytes | 1 686 720 | 1 686 648 (−72 B) | benign (PNG re-encode) |

## Differences found — classified

1. **roughness PNG re-encoded 73 bytes smaller (243 072 -> 242 999) in BOTH GLBs.** BENIGN. Same
   source `source/embedded-boucle-roughness.jpg` input; the glTF exporter re-encodes the embedded
   PNG and the byte length differs slightly between runs/zlib states. Pixel content of the rendered
   result is unchanged (proven by the pixel-identical viewer captures below). The embedded
   **base-color JPEG stayed byte-identical (26 088 B)** in both files — the baked areia tint is
   preserved exactly, so there is no risk to the intentional white-multiplier / no-double-tint path.
2. **Overall GLB shrank 72 bytes** in each file — fully accounted for by difference #1. BENIGN.
3. **GLB sha256 differs** from the published hashes. Expected and explicitly allowed by the user
   (exporter re-encode / tangent regen / image recompression). NOT a regression.

No differences were found in silhouette, node hierarchy, group names/counts, transforms, triangle
counts, scale/origin, bounds, material names, PBR parameters (including velvet sheen 0.72 /
sheenRoughness 0.55), or texture bindings. (Note: both current AND regenerated GLBs report a max-Y
world bound of 1.04422 m, whereas `manifest.json` records height 1.007378 m — this is a pre-existing
manifest/GLB mismatch present on `main`, identical in both files here, so it is NOT introduced by
regeneration. It will be reconciled when the manifest is refreshed for the real FEAT-002 change.)

## Khronos glTF-Validator (fresh reports, this run)

- regenerated `sofa.glb`:        0 errors, 0 warnings, 38 infos, 0 hints
- regenerated `sofa-mobile.glb`: 0 errors, 0 warnings, 38 infos, 0 hints

Same clean profile as the current published GLBs (I.6). The 38 infos are the known benign
UNUSED_MESH_TANGENT / UNUSED TEXCOORD_0 on untextured illustrative meshes.

## Real web-viewer behavior (regenerated asset)

The regenerated GLBs were placed into a copy of the built `dist/` (`.agents/scratch/gate-dist/`) and
served to the headless Chrome-for-Testing via the Playwright `page.route` fulfill-by-path trick. The
real `createSofaViewer` public API drove the asset (NOT a Blender render):

- `createSofaViewer` succeeded for both `main` and `mobile` variants.
- `setFinish` across ALL 12 fabric×color combos: OK, both variants.
- `setView` threequarter/detail/layers: OK.
- `setProgress` 0 / 0.5 / 0.7 / 1: OK (assembled at 0 and 1, separated at .5, structure at .7).
- `getSelection` returned the exact contract `{modelId:'stanza-organic-01', revision:'1.0.0',
  fabricId:'boucle', colorId:'areia'}` for both variants.
- **0 console errors, 0 page errors.**

### Pixel comparison vs the "before" captures (strongest evidence)

36 regenerated captures (`gate_regen_*`) were pixel-compared against the 36 pre-existing `before_*`
captures (same viewport, same API calls). Result:

**Mean-absolute-difference = 0.0000 and max per-pixel diff = 0 for ALL 36 pairs.**

The regenerated asset renders byte-for-byte identically to the current published asset in the real
WebGL viewer across every fabric/color combo, every camera, and every progress state, on both main
and mobile. Raw per-image numbers in `.agents/scratch/gate/img_diff.json`.

## Decision: PASS

No relevant regression. Silhouette, assembly, materials, textures (incl. the baked areia tint),
scale, validation, and real-viewer behavior are all preserved; the only differences are a 73-byte
benign PNG re-encode (and the consequent 72-byte file shrink and the expected hash change). Per the
user's authorization, implementation proceeds directly into the component-by-component sequence
starting with FEAT-002, without further approval for routine decisions.
