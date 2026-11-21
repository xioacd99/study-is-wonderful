# Resource-source marks

The maintainer confirmed permission to use the universities' and companies' marks on 2026-11-16 and confirmed permission for the fourteen added source marks on 2026-11-21. These identify the sources of the linked learning resources; they do not imply sponsorship or endorsement. Trademark ownership remains with the respective organizations. This record is not a general license for downstream trademark use.

`sources.json` records the original asset URL, `upstream_sha256` (when rasterized/downsampled), active `sha256`, display name, and organization family order. All university and company marks are verified institutional seals, crests, or official brand logos:

- [Stanford identity guide](https://identity.stanford.edu/visual-identity/stanford-logos/university-seal/)
- [MIT brand guide](https://brand.mit.edu/logos-marks/mit-seal)
- [UC Berkeley brand guide](https://brand.berkeley.edu/visual-identity/icons-secondary-marks/uc-berkeley-seal/)
- [Carnegie Mellon brand guide](https://brand.cmu.edu/visual-identity/carnegie-mellon-trademarks/university-seal)
- [Stony Brook identity history](https://www.stonybrook.edu/commcms/libspecial/archives/logos)

Large university SVGs (`mit`, `stanford`, `cmu`, `berkeley`) are proportionally rasterized to `160×160` transparent PNGs and oversized raster marks are proportionally downsampled to at most `160px` without cropping or recoloring, keeping the generated source walls lightweight while preserving `upstream_sha256` and provenance notes in `sources.json`.

## Maintenance

Run `python3 tools/build_resource_map.py`, `python3 tools/build_resource_map.py --check`, and `python3 -m unittest discover -s tests -v`.

The generator derives the wall from primary and additional catalog links in both READMEs (strictly before `<!-- SOURCES:START -->`). Every displayed source requires an authentic, authorized mark registered in `sources.json`; unclassified hosts or unmatched inline icons fail the build.

For each group (`university`, `project`, `company`), the builder generates both light (`source-wall-{group}.svg`) and dark (`source-wall-{group}-dark.svg`) self-contained cards in the project's Teal + Gold palette, placing every mark inside a uniform white rounded emblem tile (`rx="10"`), arranging rows of six equal-width columns with any shorter final row centered, and emitting `<picture>` dark/light markup in both READMEs. Organization groups stay contiguous and sort alphabetically by `organization_names`, with marks sorted alphabetically within each organization.
