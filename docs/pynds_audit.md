# PyNDS Audit

## Audit status

**Result: NOT VERIFIED — DO NOT INTEGRATE OR VENDOR**

Audit date: 2026-08-25

## Required identity

The implementation handoff refers to a possible open-source, NDS-oriented Python project called `PyNDS`, but explicitly requires verification of its authoritative repository, license, version/commit, and technical scope before reuse.

## Investigation result

Public GitHub/web search for `PyNDS` did not identify an authoritative structural wood-design library matching the handoff description. The prominent repositories named `PyNDS` found during the audit are Nintendo DS emulator projects and are unrelated to the National Design Specification for Wood Construction.

A separate project, `CivilPy`, publicly describes NDS wood-design features, but it is not named PyNDS and therefore cannot be assumed to be the intended upstream dependency. It has not been approved as an engineering source for this project.

## Checklist

- [ ] Authoritative structural-engineering PyNDS GitHub URL verified
- [ ] Repository owner verified
- [ ] Compatible license identified
- [ ] Commit SHA/tag pinned
- [ ] Supported Python version identified
- [ ] NDS edition/design method identified
- [ ] Upstream tests reviewed
- [ ] Relevant modules mapped
- [x] No CSA/NBCC equivalence assumed
- [x] No vendoring performed
- [x] No upstream attribution removed
- [ ] Independent benchmark tests created

## Decision

`vendor/pynds/` must not be created and no `PyNDS` dependency must be added until the exact upstream project is independently verified and approved.

**HP-02 remains OPEN.**
