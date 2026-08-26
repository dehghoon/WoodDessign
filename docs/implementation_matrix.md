# Implementation Matrix

| Feature | Governing source | Code/table/equation | Planned module | Test | Report output | Status |
|---|---|---|---|---|---|---|
| API health/version | FastAPI Guideline | N/A | `wooddessign.api.app` | `tests/api/test_app.py` | N/A | Implemented |
| Fail-closed calculation endpoint | Implementation Handoff §13, FastAPI Guideline | N/A | `wooddessign.api.app` | `tests/api/test_app.py` | Structured error | Implemented |
| Canonical typed request envelope | FastAPI Guideline | N/A | `wooddessign.models.calculation` | API tests | Input metadata | Implemented |
| Structural beam analysis | Missing Agent #2 / engineering spec | Unverified | `analysis/beam.py` | benchmark required | reactions, diagrams, extrema | BLOCKED HP-01/HP-04 |
| Load combinations | Missing governing load standard | Unverified | `analysis/combinations.py` | benchmark required | governing combination | BLOCKED HP-01 |
| Bending design | Missing governing wood standard | Unverified | `codes/<standard>/bending.py` | benchmark required | demand/resistance/utilization | BLOCKED HP-01/HP-05 |
| Shear design | Missing governing wood standard | Unverified | `codes/<standard>/shear.py` | benchmark required | demand/resistance/utilization | BLOCKED HP-01/HP-05 |
| Compression design | Missing governing wood standard | Unverified | `codes/<standard>/compression.py` | benchmark required | demand/resistance/utilization | BLOCKED HP-01/HP-05 |
| Bearing design | Missing governing wood standard | Unverified | `codes/<standard>/bearing.py` | benchmark required | demand/resistance/utilization | BLOCKED HP-01/HP-05 |
| Stability/slenderness | Missing governing wood standard | Unverified | `codes/<standard>/stability.py` | benchmark required | factors/utilization | BLOCKED HP-01/HP-05 |
| Axial + bending interaction | Missing governing wood standard | Unverified | `codes/<standard>/interaction.py` | benchmark required | interaction utilization | BLOCKED HP-01/HP-05 |
| Serviceability/deflection | Missing governing engineering spec | Unverified | `analysis/deflection.py` | benchmark required | deflection/limit | BLOCKED HP-01/HP-04 |
| Product catalog | Missing authorized dataset | Unverified | `products/` | schema/provenance tests | source metadata | BLOCKED HP-06 |
| Product optimization | Depends on validated checks and product data | N/A | `design/optimizer.py` | integration tests | governing candidate/rejections | BLOCKED HP-05/HP-06 |
| Report preview | Agent #1 report specification missing | N/A | `reporting/` | report tests | preview | BLOCKED |
| Official PDF | Agent #1 report spec + auth/entitlement integration missing | N/A | report service | authorization/report tests | PDF | BLOCKED |
| React web calculator | Valid API/engine required | N/A | future `web/` | component/e2e tests | on-screen results | BLOCKED pending engine contract |
| R3F visualization | React/R3F guidelines | N/A | future `web/` | visualization tests | geometry only | Deferred until UI phase |
