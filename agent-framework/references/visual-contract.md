# 作图任务约定 / Visual task contract

## Before drawing

Record the visual's purpose, intended reader, type, source material, fact/interpretation/proposal status, protected geometry, essential labels, final viewing size, editable-source need and requested exports. Use `templates/visual-brief.md` for a substantive visual. A simple diagram may keep this brief local.

Choose the appropriate route:

- Analytical diagrams, relationship maps and spatial analysis: structured editable graphics; distinguish measured geometry from a conceptual relation.
- Data plots: genuine source data, explicit transformations, units, appropriate axes and uncertainty when material.
- Photographs, collages and material/texture studies: retain suitable raster media and original details at adequate output quality.
- Generative images and image edits: use the available image tool for the requested creative task; do not treat generated labels, geometry or measurements as verified data.
- Interfaces and spatial/CAD/prototype work: use available specialist tools and inspect the actual rendered result.

## Design from the argument

Select the layout because it makes the intended relationship legible. State whether the diagram explains a question, a process, a comparison, a location, an interpretation or a proposal. Keep entity names, numbering and directional relationships consistent with the source text. Do not add a false activity, route or adjacency for visual balance.

Derive typography, spacing, color, line weight, symbols and annotation conventions from the current project and medium. Use actual final viewing size; avoid a universal font-size rule detached from that size. Support non-color distinctions when information depends on color. A photograph is not defective because it is not a vector.

For quantitative charts, avoid misleading area, broken scale or emphasis. Bar lengths generally need an appropriate baseline; nonzero or logarithmic axes must be justified and clearly shown. Do not import an upstream axis rule as an excuse to exaggerate a small difference.

Write captions that identify the content and argument without claiming a finding that the visual does not establish. State a material limitation once in the appropriate place; keep internal audit caveats outside clean final captions.

## Inspect what was actually exported

Keep editable source and requested preview/export. Open the preview or output with a visual inspection tool and check legibility, missing elements, font rendering, overlaps, cropping, units/scale, arrow direction, image order and source/caption agreement. Record an inspection in `project/reviews.json` and reference it from the final asset.

A successful export proves conversion only. If visual inspection is unavailable, return the useful export with that check marked `inconclusive` or `not_run`, and do not say it was visually checked. Repair observed defects and recheck affected pages or figures rather than blindly regenerating everything.

Separate actual field photographs, generated images, renders, analytical transforms and physical prototype records in `assets.json`. Making an image visually plausible does not establish that the depicted space was built or used.
