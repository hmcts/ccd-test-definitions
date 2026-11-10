# CaseTypeTab ListElementCode

## Requirement

Add support for specifying a subfield of a complex case field to be displayed on its own within Case View screens on ExUI.

Currently, `CaseTypeTab` can reference a full `CaseFieldID`. If that field is complex, the full complex object is displayed. The new `ListElementCode` column allows a definition author to target one subfield path under that complex field.

Example:

| CaseFieldID | ListElementCode |
|---|---|
| Applicant | Address.Postcode |

This means ExUI should display only `Applicant.Address.Postcode`, not the full `Applicant` complex object.

## CaseTypeTab Column

Add `ListElementCode` to `CaseTypeTab`, positioned next to `CaseFieldID`.

Expected order:

| ... | CaseFieldID | ListElementCode | TabFieldDisplayOrder | ... |
|---|---|---|---|---|

## Behaviour

| Scenario | Expected behaviour |
|---|---|
| `CaseFieldID` is complex and `ListElementCode` is a valid subfield path | Definition imports successfully |
| `CaseFieldID` is complex and `ListElementCode` is not a valid subfield path | Definition import fails |
| `ListElementCode` is blank | Existing behaviour is preserved; the whole `CaseFieldID` field is targeted |
| `ListElementCode` column is missing from an older definition file | Existing behaviour is preserved; the whole `CaseFieldID` field is targeted |
| `CaseFieldID` is simple and `ListElementCode` is populated | Definition import fails because subfields are only valid for complex fields |
| `CaseFieldID` is complex with nested complex fields and `ListElementCode` is a valid nested path | Definition imports successfully |
| Multiple `CaseTypeTab` rows target different valid subfields of the same complex `CaseFieldID` | Definition imports successfully and each row targets its own subfield |
| `CaseFieldID` is a collection and `ListElementCode` is populated | Definition import fails because CaseTypeTab subfield resolution is not supported for collections |

## Test Definition Files

Add dedicated shared CCD definition Excel files in `src/main/resources/uk/gov/hmcts/ccd/test_definitions` for this behaviour.

Where possible, use one valid workbook and one invalid workbook, with separate case types inside each workbook to cover the individual scenarios.

Any comments added to workbook rows should include the AC marker, FT case type name, and scenario intent, for example: `AC1 - FT_CTT_Subfield_Valid - valid direct complex subfield`.

Keep fixture `CaseType.ID` and `CaseType.Name` values short enough for import validation. `CaseType.Name` must be 30 characters or fewer, so use short names such as `FT_CTT_Subfield_Valid`, `FT_CTT_Subfield_Blank`, `FT_CTT_Subfield_Nested`, `FT_CTT_Subfield_Multiple`, `FT_CTT_Subfield_BadPath`, `FT_CTT_Subfield_Simple`, and `FT_CTT_Subfield_Collection`.

After zip-level workbook edits, clean the Excel package before committing:

- remove empty cell records that have no value, formula, inline string, or style
- preserve cells that have row comments, including blank `ListElementCode` comment cells, with explicit empty inline strings
- normalise worksheet namespace prefixes with `./scripts/normalise_xlsx_namespaces.py <workbook.xlsx>` after POI or zip-level edits
- keep empty/header-only worksheets unless import testing proves they can be removed safely
- validate by opening/saving with POI or Excel so the workbook does not trigger Excel recovery

For the valid workbook, generate the matching JSON under `src/main/resources/uk/gov/hmcts/ccd/test_definitions/valid` by running:

```bash
./gradlew definitionsToJson
```

BEFTA high-level setup imports valid JSON by default, not invalid Excel fixtures. Keep generated JSON for `CCD_BEFTA_CTT_LISTELEMENCODE.xlsx` under `valid/CCD_BEFTA_CTT_LISTELEMENCODE`. The invalid workbook is for explicit negative import tests in the consuming implementation.

After generation, review the diff carefully and keep only the intended workbook/header additions plus the intended valid JSON definition changes. Do not keep unrelated converter churn such as date normalisation, row reordering, whitespace-only output changes, or formatting-only workbook changes.

| Test definition file | Suggested case type | Intent | Expected result |
|---|---|---|---|
| `excel/CCD_BEFTA_CTT_LISTELEMENCODE.xlsx` | `FT_CTT_Subfield_Valid` | Valid direct subfield under a complex field | Import succeeds |
| `excel/CCD_BEFTA_CTT_LISTELEMENCODE.xlsx` | `FT_CTT_Subfield_Blank` | Blank value keeps whole-field behaviour | Import succeeds and targets the whole field |
| `excel/CCD_BEFTA_CTT_LISTELEMENCODE.xlsx` | `FT_CTT_Subfield_Nested` | Valid nested path under a complex field | Import succeeds |
| `excel/CCD_BEFTA_CTT_LISTELEMENCODE.xlsx` | `FT_CTT_Subfield_Multiple` | Multiple valid subfields from the same complex field | Import succeeds |
| `invalid/CCD_BEFTA_CTT_LISTELEMENCODE_invalid.xlsx` | `FT_CTT_Subfield_BadPath` | Invalid path should fail validation | Import fails: subfield does not exist |
| `invalid/CCD_BEFTA_CTT_LISTELEMENCODE_invalid.xlsx` | `FT_CTT_Subfield_Simple` | Simple fields must not accept subfield paths | Import fails: subfields are only valid for complex fields |
| `invalid/CCD_BEFTA_CTT_LISTELEMENCODE_invalid.xlsx` | `FT_CTT_Subfield_Collection` | Collection subfield resolution is unsupported for CaseTypeTab | Import fails with collection-not-supported error |
| Existing older definition without `ListElementCode` | Existing legacy case type | Older files without the new column remain compatible | Import succeeds and targets the whole field |
| Latest valid template or generated definition | Template/header check | Latest template exposes the new column in the right place | `ListElementCode` appears next to `CaseFieldID` on `CaseTypeTab` |

## Recommended Existing BEFTA Content To Reuse

Use `BEFTA_Master_Definition.xlsx` as the base where possible, because it already contains case types and complex structures that suit this change.

Fixture case types:

| Fixture case type | Use for | CaseTypeTab values |
|---|---|---|
| `FT_CTT_Subfield_Valid` | Valid direct complex path | `CaseFieldID=MySchool`, `ListElementCode=Name` |
| `FT_CTT_Subfield_Nested` | Valid nested complex path | `CaseFieldID=FamilyDetails`, `ListElementCode=FamilyAddress.Country` |
| `FT_CTT_Subfield_Simple` | Simple-field negative validation | `CaseFieldID=Homeless`, `ListElementCode=Name` |
| `FT_CTT_Subfield_Collection` | Collection-not-supported validation | `CaseFieldID=MyCompany`, `ListElementCode=Name`; `CaseFieldID=CollectionComplexField`, `ListElementCode=AddressLine1` |

Suggested workbook structure:

| Workbook | Coverage | Case types | Rows to add |
|---|---|---|---|
| `excel/CCD_BEFTA_CTT_LISTELEMENCODE.xlsx` | Valid direct subfield, blank value, valid nested path, and multiple subfields | `FT_CTT_Subfield_Valid`, `FT_CTT_Subfield_Blank`, `FT_CTT_Subfield_Nested`, `FT_CTT_Subfield_Multiple` | `MySchool` + `Name`, blank `ListElementCode`, `FamilyDetails` + `FamilyAddress.Country`, and `MySchool` + `Name` plus `MySchool` + `Number` |
| `invalid/CCD_BEFTA_CTT_LISTELEMENCODE_invalid.xlsx` | Invalid path, simple-field subfield, and collection subfield | `FT_CTT_Subfield_BadPath`, `FT_CTT_Subfield_Simple`, `FT_CTT_Subfield_Collection` | `MySchool` + `DoesNotExist`, `Homeless` + `Name`, `MyCompany` + `Name`, and `CollectionComplexField` + `AddressLine1` |

`ListElementCode` should be added next to `CaseFieldID` on `CaseTypeTab` in these workbooks.

## Current Fixture State

- Valid workbook: `excel/CCD_BEFTA_CTT_LISTELEMENCODE.xlsx`
- Invalid workbook: `invalid/CCD_BEFTA_CTT_LISTELEMENCODE_invalid.xlsx`
- Generated valid JSON: `valid/CCD_BEFTA_CTT_LISTELEMENCODE`
- Multiple-subfield case type: `FT_CTT_Subfield_Multiple`
- Valid AC comments: 5
- Invalid AC comments: 4
- Excel cleanup: no empty cell records; comment cells preserved; worksheet namespace prefixes normalised after POI resave
