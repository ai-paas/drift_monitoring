# Drift Method Design Documents

This directory contains one design document per drift method from
`drift_methods_catalog.md`.

The files are generated from the method catalog and CSV mappings, then reviewed
before implementation. Regenerate skeletons with:

```powershell
python drift_algorithm\tools\generate_method_design_docs.py
```

Manual refinements should stay inside the generated section structure so the
manager review can compare method designs consistently.

