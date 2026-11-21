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

The generator derives the wall from primary and additional catalog links in both READMEs, including sources only credited in text. Register each new hostname with its actual source. For a hosted article that explicitly credits a separate publisher, use a reviewed host/path rule (e.g. ggml-org on Hugging Face), not a guess based on the title. Unclassified links fail the build. It embeds the original files into `source-wall.svg`, uses six equal-width columns, preserves each mark's aspect ratio, and places the Google family together. No external asset request is needed to render the wall. Register verified marks with their provenance and hash. If permission or provenance has not been verified, omit the asset path and use the generated name badge. Text badges do not represent an official logo. For verified course producers whose recordings are linked through a third-party platform, record the course ID, exact resource URL, and attribution evidence in `course_credits`; an unrelated link change invalidates that attribution until reviewed. Source credit is not a claim that the linked recording matches a particular official edition. Unused sources are not displayed. The README uses an accessible descriptive alt string; SVG title/description and visible names identify individual marks.

All marks must declare an `organization` in `sources.json`. The generator groups every organization contiguously, not only Google; register new marks with the same organization key as existing related brands. Organization groups sort by `organization_names` alphabetically (case-insensitive); sources within each group sort by display name alphabetically.

## November 21 source audit

Both README bodies at `0dad2ce` contain 154 courses, 64 articles and the same 239 catalog link occurrences across 32 hostnames. The audit also matched current video IDs and exact collection URLs against the [original catalog before regrouping](https://github.com/xioacd99/study-is-wonderful/blob/6ceb171ca6881eddd81e8a6654726b69b591e444/README.md) and checked course pages and publisher credits where available. Text marks restore missing source names without claiming permission for their logos. Historical credits (including the entry historically labeled Cambridge aesthetics) identify the previous catalog's stated provider, not an independently verified mirror edition. A lecturer’s affiliation alone, an article subject, or an uncorroborated mirror is not a source attribution. In particular, the Compilers and Statistical Learning entries share the same Bilibili ID; the audit preserves the links and does not attach a Compilers claim to that ID. Some supplemental lectures and personal uploads remain attributed only to their confirmed host.
