# WoodDessign — NDS 2024 component-check Beta

Installable Python package and protected FastAPI service for a limited evaluation workflow. The website page is `/tools/wood-design` on Linkoteq.

## Current scope

Single rectangular, prismatic, unnotched sawn-lumber components. Includes engineer-supplied material/factor inputs with provenance, controlled ASD/LRFD duration/format chains, bending/shear/tension/bearing, beam stability from adjusted values, both column axes, compression–bending interaction without denominator clamping, and simply supported UDL live/total deflection.

The website's simple-beam workflow analyzes one full-span downward UDL. Design combination load and service loads are supplied separately; self-weight must already be included. It does not generate building-code load combinations.

Every result returns `whole_member_status=not-checked` and `engineering_approval=false`. Component PASS does not certify a complete member. Independent engineering review, built-up/glulam/SCL, manufacturer catalogs, connections, broader analysis and formal reports remain incomplete. CSA O86 is not implemented; NDS results must not be described as Canadian-code design.

## Development

```bash
pip install -e '.[dev]'
pytest -q
uvicorn wooddessign.api.app:app --reload
```

## API

- `GET /health`, `GET /version`: public service/readiness metadata.
- `POST /api/v1/nds2024/member-check`: scoped component checks.
- `POST /api/v1/nds2024/simple-beam`: simple-span UDL analysis and beam component checks.
- `POST /api/v1/calculate`: complete design remains unavailable (503 for authorized callers).

All `/api/` requests require a user Bearer JWT. The server calls Linkoteq's canonical execution authority with `tool=wood_design`; unauthenticated requests are 401, missing access is 403, and unavailable authorization fails closed. UI state is not an authorization mechanism. Do not set an environment switch to bypass authentication.

The geometry/action examples are synthetic test fixtures, not approved lumber catalog values. They can be evaluated directly with the same Python engine or sent to the protected API by a user with approved access. Source assumptions and factors must be replaced with project-specific evidence.

## Validation and provenance

`docs/source_register.md` records the approved equation-level v2 handoff and the inaccessible upstream implementation. `docs/implementation_matrix.md` states the remaining scope. The test suite covers hand arithmetic benchmarks, stability/axis regressions, strict invalid inputs, unrounded overcapacity, and direct API authorization.
