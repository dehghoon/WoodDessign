# Wood design source register — 2026-11-20

The prior repository scaffold did not include the subsequently approved engineering handoff. That older missing-source assessment is superseded for the NDS component scope by:

- `01_Wood_Engineering_Calculation_Specification_APPROVED_Equation_Level_v2(1).docx`, approved 2026-08-25, NDS 2024 plus applicable errata through March 2026. The current text was read in full; its equation register is retained in `approved-nds-2024-specification.txt`.
- `04_PyNDS_Open_Source_Audit_and_ReUse_Matrix_APPROVED(1).docx`, approved source basis. The later equation-level v2 register controls corrections and supersedes earlier source-confirmation holds.
- The audit pins CivilPy at `637ac23218bab70f9b1dc04310a4c5d9d238bb04`. Direct retrieval of that repository failed with an authentication/access error on this implementation run. Consequently no upstream implementation or material CSV was copied. The corrected kernels are implemented directly from the authorized equation-level handoff; this is the reason for not reusing unavailable upstream functions. No claim is made that CivilPy tests were run.

## Implemented boundary

NDS 2024 rectangular, prismatic, unnotched single sawn-member component checks, with explicit engineer-supplied material values and adjustment factors. ASD/LRFD duration and format factors are computed, property-specific factors are constrained, beam stability uses adjusted properties, both column axes are evaluated, and nonpositive interaction denominators fail without clamping. Simple-span UDL serviceability is isolated from supplied strength actions.

These checks do not verify the provenance/applicability of externally entered material values or modification factors. Every result retains those sources and returns `whole_member_status=not-checked` and `engineering_approval=false`. A passing component check is not complete member design approval.

## Not completed

Built-up fastening/detailing and the individual-lamination capacity-floor comparison; glulam/SCL/product-specific factor interactions; authorized built-in product catalog; broader analysis supports/loads; connections; complete member verification; formal reports; and CSA O86. No NDS equation is represented as CSA O86.

The API's original complete-design route remains unavailable. The new component-check endpoints are protected by canonical tool-scoped authorization. A limited Beta interface consumes the simple-span UDL workflow. Independent engineering review and the wider design scope remain incomplete.
