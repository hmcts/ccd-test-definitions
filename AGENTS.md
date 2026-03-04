# Agents Guide

## Skills In This Repo

Use these skills explicitly in prompts when working on definition reconciliation:

1. `ccd-excel-json-guard`
- Purpose: repo-specific workflow for Excel/JSON reconciliation and templated callback safety.
- Trigger examples:
  - `Use ccd-excel-json-guard to reconcile these callback changes.`
  - `$ccd-excel-json-guard`

2. `ccd-json-excel-guard`
- Purpose: generic guard rails for semantic discrepancy detection, templating validation, and trimming normalization-only churn.
- Trigger examples:
  - `Use ccd-json-excel-guard before commit and keep only semantic changes.`
  - `$ccd-json-excel-guard`

## Recommended Usage

- Use `ccd-json-excel-guard` for general safety checks.
- Use `ccd-excel-json-guard` when working on callback templating and BEFTA/CCD workbook reconciliation specifics.
