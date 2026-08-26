# Source Register

## Purpose

This register records the sources that are currently authorized to govern the WoodDessign implementation. It distinguishes architecture/process guidance from engineering calculation authority.

## Supplied implementation handoff

| Source | Edition / date | Role | Modules affected | Engineering authority |
|---|---|---|---|---|
| `WoodDessign_GPT3_Implementation_Instructions.docx` | Supplied 2026-08-25 | Project mission, architecture, hold points, provenance, testing, reporting, PyNDS audit requirements | Entire repository | Process/specification handoff only; it explicitly prohibits invented engineering provisions |
| `04_GITHUB_ARCHITECTURE_GUIDELINE.md` | Current supplied copy | Repository-first GitHub workflow | Repository structure, commits | No |
| `05_ENGINEERING_PLATFORM_GUIDELINE.md` | Current supplied copy | Shared engineering package boundary | Engine/API/client boundaries | No |
| `06_FASTAPI_GUIDELINE.md` | Current supplied copy | FastAPI responsibilities | `src/wooddessign/api` | No |
| `07_REACT_GUIDELINE.md` | Current supplied copy | Frontend boundary and API-only engineering consumption | Future `web/` | No |
| `08_REACT_THREE_FIBER_GUIDELINE.md` | Current supplied copy | Visualization boundary | Future visualization | No |
| `09_REPORT_AND_PDF_GUIDELINE.md` | Current supplied copy | Report preview/PDF authorization architecture | Future reporting | No |
| `13_MOBILE_REUSE_GUIDELINE.md` | Current supplied copy | Mobile reuse boundary | Shared contracts/future `mobile/` | No |
| `14_CHECKLIST.md` | Current supplied copy | Delivery gate | CI/release | No |
| `15_CHANGELOG.md` | Version 1.0 | Platform guideline history | Documentation | No |
| `16_OPEN_SOURCE_VISUALIZATION_GUIDELINE.md` | Current supplied copy | Visualization reuse/open-source policy | Future visualization | No |
| `10_CISC_DATA_GUIDELINE.md` | Current supplied copy | CISC data ingestion rules | Not applicable to wood product data unless steel components enter scope | No wood-design authority |
| `11_TESTING_AND_QA_GUIDELINE.md` | Current supplied copy | Required test layers/evidence | Tests/CI | No |
| `12_DEPLOYMENT_GUIDELINE.md` | Current supplied copy | Portable deployment requirements | Deployment/configuration | No |
| `Engineering_Frontend_Architecture_Guideline_FINAL_v2.docx` | Final supplied copy | Repository/domain/API/auth/report/mobile boundaries | Platform architecture | No |
| `GPT3_GitHub_Development_Guidelines.md` | Current supplied copy | GitHub implementation workflow | Git operations | No |

## Missing governing engineering sources

No Agent #1 Engineering Calculation Specification / Handoff, approved Agent #2 calculation package, NBCC edition, CSA O86 edition, NDS edition, authorized manufacturer design-value dataset, or independent benchmark set was supplied with the current task.

Therefore:

- no wood resistance equation is authorized for implementation;
- no adjustment/resistance factor is authorized for implementation;
- no load combination is authorized for implementation;
- no material/product design value is authorized for production use;
- no PASS/FAIL engineering result may be emitted.

## Hold point

**HP-01 remains OPEN.** Governing engineering code editions and validated calculation authority must be supplied before calculation modules are implemented.
