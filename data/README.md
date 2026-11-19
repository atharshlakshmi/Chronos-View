# Data handoff contract

- Place licensed source panoramic imagery in `data/raw/` (ignored by Git).
- Do not distribute copyrighted/terms-restricted panoramas via the repository.
- Use `data/source_manifest.csv` with one entry per image: image_id,source_url,creator,license,attribution,capture_date,location,notes.
- Crops: `data/crops/<image_id>/view_000.png`, `view_060.png`, ..., `view_300.png`.
- Depth: `data/depth/<image_id>/view_000.png`, etc.
- Every model compares the exact same crop at the exact same resolution.
- For legal sharing, use only images your group is permitted to copy, process and show, with attribution.
