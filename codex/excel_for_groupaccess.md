# Excel for Group Access

## Requests captured
- Create `BEFTA_MASTER_GROUPACCESS.xlsx` from `BEFTA_Master_Definition.xlsx`, copying only rows that mention `FT_CaseAccessGroups`.
- Keep all tabs that contain matching rows; preserve headers and data order.
- Treat rows 1-3 as headers; always include rows 1-2; include row 3 only when it has content.
- Preserve formulas, values, styles (including background color), column widths, row heights, and merged cells.
- Preserve Excel tables (ListObjects) so sort/filter controls appear.
- Keep table filters only when the source table had a filter; do not add filters where none exist.
- Restore custom table style definitions so header colors show (e.g., `TableStyleDefinitionsTab`).

## Source and output
- Source: `src/main/resources/uk/gov/hmcts/ccd/test_definitions/excel/BEFTA_Master_Definition.xlsx`
- Output: `src/main/resources/uk/gov/hmcts/ccd/test_definitions/excel/BEFTA_MASTER_GROUPACCESS.xlsx`

## Included tabs
- CaseType
- CaseField
- AuthorisationComplexType
- EventToComplexTypes
- ChallengeQuestion
- CaseTypeTab
- State
- CaseEvent
- CaseEventToFields
- SearchInputFields
- SearchCasesResultFields
- SearchResultFields
- WorkBasketInputFields
- WorkBasketResultFields
- AuthorisationCaseType
- AuthorisationCaseField
- CaseRoles
- AuthorisationCaseEvent
- AuthorisationCaseState
- RoleToAccessProfiles
- AccessType
- AccessTypeRole

## Tabs with empty row 3 in source (row 3 omitted in output)
- None

## Import fixes applied
- Removed empty cell records from all sheets (cells with no value/formula/inline string) to avoid POI `getRawValue()` NPE.
- Tightened table ranges to the last row with actual data; auto-filters updated to match.
- Added full `ComplexTypes` tab from source with empty rows removed; table refs updated and missing cells within table ranges filled to avoid POI `getRawValue()` NPE.
- Added deterministic cleanup: delete empty rows from `Jurisdiction` tab (rows >=5) and re-scope its table range.
- Filled missing cells across header width (rows 1-3) for all rows in each sheet to avoid POI `getRawValue()` nulls.
- Added full `FixedLists` tab from source with empty rows removed; table refs updated and missing cells across header width filled.
- Ensured every cell has a raw value: any cell without v/f/inline string now gets an empty string value to prevent POI `getRawValue()` NPE.
- Removed all empty cells (no value/formula/inline string) and re-scoped table ranges to last non-empty row; this mirrors manual cleanup of empty rows that fixed the POI NPE.
- Added full `UserProfile` tab from source with empty rows removed; table refs updated.
- Updated `UserProfile` WorkBasketDefaultCaseType for master users to `FT_CaseAccessGroups` to match available CaseType.
- Added full `Categories` tab from source with empty rows removed; table refs updated.
- Updated `Categories` CaseTypeId values from `FT_MasterCaseType` to `FT_CaseAccessGroups` to match available CaseType.
- Removed `ComplexTypes` rows where CategoryID == `evidenceDocs` (invalid CategoryID).
- Cleared `CategoryID` values in `ComplexTypes` (removed all category references).
- Tightened `Jurisdiction` sheet dimension range to actual used cells (A1:E4) to prevent POI NPE; main file imports successfully.
- Removed `BEFTA_MASTER_GROUPACCESS_v2.xlsx` after confirming main file import.
- Re-applied Jurisdiction row deletion (5-100) and dimension tightening on main file; no rows remained to delete, dimension set to A1:E4.
- Added new CaseType `FT_CaseAccessGroups_Align_Befta` by duplicating `FT_CaseAccessGroups` rows across all tabs with CaseTypeID/CaseTypeId/WorkBasketDefaultCaseType references.
- Replaced `FT_CaseAccessGroups_Align_Befta` with `FT_CaseProfessionalGroupAccess` across the workbook.
- Replaced OrganisationProfileIDs `groupaccesstest_solicitor`/`groupaccesstest_ogd` with `SOLICITOR_PROFILE`/`GOVERNMENT_ORGANISATION_PROFILE`.
- Updated AccessTypeRole for `FT_CaseProfessionalGroupAccess` + `SOLICITOR_PROFILE` to set `OrganisationalRoleName=CaseProfessionalGroupAccess_Org_Role` and `GroupRoleName=CaseProfessionalGroupAccess_GA_Role`.
- Deleted all rows containing `FT_CaseAccessGroups`.
- Re-saved the workbook with `openpyxl` to clear Excel recovery warnings after zip-level edits.

## Post-edit cleanup (required)
After any manual Excel edits, run the cleanup script to avoid POI NPEs during import:

```
./scripts/fix_jurisdiction_rows.py
```

This removes rows 5–100 from `Jurisdiction`, tightens the sheet dimension, and re-scopes its table range.

## How to use this workbook
1) Edit `BEFTA_MASTER_GROUPACCESS.xlsx` in Excel as needed and save.
2) Run the cleanup script:
```
./scripts/fix_jurisdiction_rows.py
```
3) Import the Excel file into CCD.

## How to use this MD in the future
- Append any new fixes or changes to the “Import fixes applied” and “Current state summary” sections.
- If you add new scripts, include them in “Post-edit cleanup (required)” with the exact command.
- Keep the “Current state summary” accurate after each successful import.

## Current state summary
- `BEFTA_MASTER_GROUPACCESS.xlsx` imports successfully after running `./scripts/fix_jurisdiction_rows.py`.
- CaseType is now `FT_CaseProfessionalGroupAccess` (all `FT_CaseAccessGroups_Align_Befta` references replaced).
- All rows containing `FT_CaseAccessGroups` were removed.
- `AccessType` OrganisationProfileIDs are now `SOLICITOR_PROFILE` and `GOVERNMENT_ORGANISATION_PROFILE`.
- `AccessTypeRole` for `FT_CaseProfessionalGroupAccess` + `SOLICITOR_PROFILE` uses `OrganisationalRoleName=CaseProfessionalGroupAccess_Org_Role` and `GroupRoleName=CaseProfessionalGroupAccess_GA_Role`.
- Workbook re-saved with `openpyxl` to prevent Excel recovery prompts.
- `Categories` and `ComplexTypes` remain present with CategoryID cleared (no category references).
