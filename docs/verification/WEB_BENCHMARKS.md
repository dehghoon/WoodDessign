# External wood resistance benchmarks — 20 November 2026

Source: https://calcs.com/docs/calculators/us/beams/timberBeamLRFDNDS-2024

The page's worked examples explicitly use NDS2018, despite its 2024 guide
title. Tests therefore do not present these as complete NDS2024 validation.
They compare at the adjusted-property boundary: printed adjusted stresses
are explicit test inputs, not a claimed species/grade database or inferred
factor chain. Actual section dimensions are1.5×5.5in.

| Published case | Printed reference | Calculated | Tolerance |
|---|---|---|---|
| ASD moment resistance |1177.7 lbft |1178.4895833333 lbft |0.1% for printed rounding |
| ASD shear resistance |1237.5 lbf |1237.5 lbf |1e-12 relative |
| LRFD moment at adjusted-stress boundary |1627.3 lbft |1627.1979166667 lbft |0.1% for printed rounding |
| LRFD shear at adjusted-stress boundary |1710 lbf |1710.5 lbf |0.1% for printed rounding |
| LRFD shear adjusted stress |311 psi |311.04 psi |0.05psi |

Instantaneous bending deflection tests remain separate. The source's
long-term deflections include creep and are not claimed to match our model.
Full printed loading and tributary widths were not available in the text;
this is not a reproduction of the source's full demand analysis.

The comparison exposed a missing continuous-bracing input. The API now
accepts an explicit bracing declaration and uses CL=1 for a uniaxial beam
without axial force. Unsupported axial/biaxial uses of this override reject
rather than hiding instability. Default remains unbraced.

Official amendment review source:
https://awc.org/wp-content/uploads/2026/09/2024-NDS-Errata-and-Addenda-UPDATED-09.22.26.pdf
The reviewed corrections include connections/notches/glulam beyond our
single unnotched sawn-member scope; they do not establish complete coverage.
The entire member still returns not-checked, including connections, fire,
creep, shear deformation and other excluded checks. CSA O86 is not implemented.
