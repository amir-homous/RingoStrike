# Living Space room art generator (Visual v1)

Python (Pillow) scripts that produced the pixel-art room in `frontend/src/assets/room/`
(B18, approved 2026-10-19). Kept for future regeneration.

- Spec: `docs/product/LIVING_SPACE_VISUAL_V1_SPEC.md` and its addendum
  `docs/product/LIVING_SPACE_VISUAL_V1_ADDENDUM.md` (perspective model, layer order, asset contract).
- `scene.py` builds the room and zone props, `sprites.py` Ringo/markers, `render.py` lights/dim/vignette,
  `lib.py` shared palette and drawing helpers, `export.py` writes all PNGs and `room_layout.json`.

## Regenerate

```bash
cd tools/room_art
python3 export.py          # needs Pillow; writes ./export/room/ (deletes ./export first)
```

Then review the output and copy `export/room/` over `frontend/src/assets/room/`.
`room_layout.json` is the source of truth for positions; the frontend reads only it and the PNGs.
Any hand-made replacement must keep the same size, anchor and perspective (addendum §1).
