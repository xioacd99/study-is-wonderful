# Resource-source marks

The maintainer confirmed permission to use the universities' and companies' marks on 2026-11-16. These identify the sources of the linked learning resources; they do not imply sponsorship or endorsement. Trademark ownership remains with the respective organizations. This record is not a general license for downstream trademark use.

`sources.json` records the original asset URL, file hash, display name and family order. The university seals replace the previous text-only placeholder badges. Their exact SVG artwork was retrieved from the cited Wikimedia file pages and cross-checked against the institutions' identities:

- [Stanford identity guide](https://identity.stanford.edu/visual-identity/stanford-logos/university-seal/)
- [MIT brand guide](https://brand.mit.edu/logos-marks/mit-seal)
- [UC Berkeley brand guide](https://brand.berkeley.edu/visual-identity/icons-secondary-marks/uc-berkeley-seal/)
- [Carnegie Mellon brand guide](https://brand.cmu.edu/visual-identity/carnegie-mellon-trademarks/university-seal)
- [Stony Brook identity history](https://www.stonybrook.edu/commcms/libspecial/archives/logos)

Company marks retain their existing official website or official GitHub organization sources. Existing Bilibili and YouTube SVG assets are retained. Google and Clay assets are decoded to PNG solely for SVG renderer compatibility, without resizing, cropping or recoloring.

## Maintenance

Run `python tools/build_resource_map.py`, then `python tools/build_resource_map.py --check` and `python -m unittest discover -s tests -v`.

The generator derives the wall from actual body icons in both READMEs. It embeds the original files into `source-wall.svg`, uses six equal-width columns, preserves each mark's aspect ratio, and places the Google family together. No external asset request is needed to render the wall. New sources must be registered with a verified asset and hash; unused sources are not displayed. The README uses an accessible descriptive alt string; SVG title/description and visible names identify individual marks.

All marks must declare an `organization` in `sources.json`. The generator groups every organization contiguously, not only Google; register new marks with the same organization key as existing related brands. Organization groups sort by `organization_names` alphabetically (case-insensitive); sources within each group sort by display name alphabetically.
