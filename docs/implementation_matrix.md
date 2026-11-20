# Wood design implementation matrix — 2026-11-20

| Module | Current result | Verification |
| --- | --- | --- |
| Installable Python package and health API | Implemented; uvicorn dependency repaired | API tests and clean editable install |
| NDS single rectangular sawn-member component checks | Implemented from approved equation-level v2 handoff | Independent arithmetic fixtures plus regression/invalid-input tests |
| Beam and both column-axis stability | Corrected adjusted-property chain, unrounded arithmetic | B-NDS-02 through 05 and slenderness boundaries |
| ASD/LRFD controlled factors | Duration, format/resistance and time-effect chains | B-NDS-09 and unsupported-property factors |
| Bending, shear, tension and bearing | Supplied material/factor inputs, explicit sources | B-NDS-01, 06, 07; no whole-member approval |
| Simple-span UDL deflection | Implemented for live/total serviceability | B-NDS-08 closed-form fixture |
| Built-up, glulam and SCL design | Not implemented | No passing design output |
| Material catalog / product selection | Not implemented | No silent fallback to generic material |
| CSA O86 | Not implemented, independent Canadian profile required | NDS substitution rejected |
| Complete design API and formal reports | Unavailable | Existing fail-closed tests |
