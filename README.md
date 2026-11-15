# Terra Analog

Terra Analog is a regional terrain-comparison prototype. It compares selected Earth terrain measurements with measured reference profiles for Jezero crater on Mars and the Moon's south polar region, then shows ranked candidate cells on an interactive map.

## Current status

The integrated MVP supports real, versioned regional Earth datasets for Atacama / Andes, Hawaii Big Island, and the Himalaya; three topographic criteria; weighted pixel ranking; distinct-area selection; result explanations; and an OpenStreetMap basemap with separately controlled result layers. The demo is **regional**. Global search is not available: the API returns `SCOPE_UNAVAILABLE` for global requests. There is no verified public deployment or anonymous demo link.

The result is a configured terrain-similarity index, not probability, habitability, or proof that two environments are equivalent. Only the measurements, scales, sources, and limitations documented for a run should be interpreted. A missing measurement is not zero. Synthetic fixtures are separate from Live data and must remain visibly labelled.

## Get started

Read [the product and repository guide](docs/README.md), then follow the component-specific instructions:

- [Web application](apps/web/README.md)
- [API](apps/api/README.md)
- [Data pipeline](pipeline/README.md)
- [Data inventory](data/README.md)
- [API contracts and fixtures](contracts/README.md)

The repository pins Python 3.12 dependencies in `pyproject.toml` and `uv.lock`, and web dependencies in `apps/web/package.json` and `apps/web/package-lock.json`. Do not commit downloaded raw datasets; manifests and the small versioned regional derived tables are tracked.

## Project map

| Path | Purpose |
|---|---|
| `apps/web/` | User interface, map, controls, result ranking and explanations |
| `apps/api/` | Versioned catalogue, regional analysis, map tiles and pixel details |
| `pipeline/` | Reproducible source downloads, quality checks, profiles and derived features |
| `contracts/` | API schemas, OpenAPI, synthetic fixtures and contract tests |
| `data/` | Data manifests, reports and compact derived regional packages |
| `design/` | Product-flow and interaction design handoffs |
| `docs/` | Product, methodology, data, architecture, validation and submission guidance |
| `tasks/` | Shared task queue and task history for both workstreams |
| `handoffs/` | Implementation and review evidence exchanged between owners |
| `submission/` | English jury materials and demo artifacts |
| `prompts/` | Agent work guides; formal submission remains human-only |
| `tools/` | Repository planning and consistency checks |

For keep/archive/remove decisions, see [Repository guide](docs/REPOSITORY_GUIDE.md). The authoritative task status is in each linked card in the [task index](tasks/README.md).

## Important project rules

- Evaluate every eligible cell within the declared dataset and scope before selecting the pixel Top 10. A regional ranking is not a global ranking.
- Preserve isolated high-scoring pixels. The distinct-area mode is a separate ranking with an explicit separation distance.
- Keep the map, ranking and explanation tied to one `analysis_id`. A new request must not display stale results as current.
- Keep basemap visibility, result-cell visibility, marker visibility and analysis criteria independent.
- Record units, scale, source, version, missing-data reasons and quality flags. Never convert missing values to zero.
- Do not describe lithology as mineralogy or NDVI as evidence of life on Mars.
- Keep source, licence, and attribution records. Incidental tool references do not belong in product UI.
- Only Kamil or Ewelina may submit the project or make required attestations.

## Project documentation

- [Product scope and current limits](docs/PRODUCT.md)
- [Scientific method and score interpretation](docs/METHODOLOGY.md)
- [Data sources, versions and provenance](docs/DATA.md)
- [API and data-flow architecture](docs/ARCHITECTURE.md)
- [API and frontend contracts](docs/CONTRACTS.md)
- [Validation evidence](docs/VALIDATION.md)
- [Submission requirements and human checklist](docs/SUBMISSION.md)
- [Organizer source snapshots](docs/sources/README.md)
- [Collaboration and Git workflow](docs/COLLABORATION.md)
- [Third-party software and data notices](THIRD_PARTY.md)

## License

Project code is offered under the [MIT License](LICENSE). Data and third-party materials retain their own terms; see [THIRD_PARTY.md](THIRD_PARTY.md), the data manifests, and the cited source records.
