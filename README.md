# WoodDessign

Production-oriented structural wood design calculator scaffold.

## Status

This repository is currently in **engineering hold** for calculation modules.

The application architecture, provenance records, API shell, and validation scaffolding are initialized. Engineering design calculations are intentionally not implemented until the governing engineering specification and validated Agent #2 calculation package are supplied and approved.

### Current hold points

- HP-01: Governing code editions and engineering calculation specification are not available in the supplied project materials.
- HP-02: No authoritative structural-engineering project named `PyNDS` has been verified. Public GitHub search results for `PyNDS` currently resolve to Nintendo DS emulator projects, not an NDS wood-design engine.
- HP-05: No code-design module may be represented as validated until independent benchmark cases are available.
- HP-06: No manufacturer/product dataset is included because authorized provenance has not been supplied.

## Architecture

```text
src/wooddessign/
  api/          FastAPI transport layer
  models/       Typed application contracts
  codes/        Design-standard adapters (blocked pending validated engine)
  reporting/    Report contracts (no engineering reinterpretation)
docs/
  source_register.md
  implementation_matrix.md
  pynds_audit.md
tests/
  api/
```

Engineering calculations must remain in the validated Python engine/package. FastAPI and future web/mobile clients must consume the same approved outputs and must not reimplement formulas.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn wooddessign.api.app:app --reload
b``

## Available API

- `GET /health`
- `GET /version`
- `POST /api/v1/calculate` — fails closed with HTTP 503 until a validated engineering engine is integrated.

## Safety

WoodDessign is an engineering calculation aid. Unsupported or unvalidated design conditions must fail closed. No code-compliance claim is made for calculation modules until the governing source, implementation, and benchmark validation are approved.
