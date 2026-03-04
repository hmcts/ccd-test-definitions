---
name: ccd-excel-json-guard
description: Use this when reconciling CCD test definition Excel and generated JSON, especially callback URL templating (TEST_STUB_SERVICE_BASE_URL and MCA_API_BASE_URL), guarding semantic discrepancies, and trimming normalization-only drift after definitionsToJson.
---

# CCD Excel/JSON Guard

Use this skill when a change must be made in Excel and verified through `definitionsToJson` without losing templated callback URLs or important FT_MasterCaseType rows.

## Source of truth

- For routine updates, Excel is source of truth and JSON is generated.
- If a known semantic discrepancy exists in JSON and must be preserved, first sync that behavior into Excel, then regenerate JSON.

## Required workflow

1. Run conversion:

```bash
./gradlew definitionsToJson
```

2. Classify diff:
- Semantic changes: IDs, CaseEventID, callback fields (`CallBackURL*`, `CallbackGetCaseUrl`), `NullifyByDefault`, states/conditions.
- Normalization-only: date string formatting (`LiveFrom`, `LiveTo`), array/comma layout, whitespace.

3. Preserve templating in Excel (never commit hardcoded local hosts for these):
- `${TEST_STUB_SERVICE_BASE_URL:http://ccd-test-stubs-service-aat.service.core-compute-aat.internal}`
- `${MCA_API_BASE_URL:http://aac-manage-case-assignment-aat.service.core-compute-aat.internal}`

4. If semantic discrepancies appear after conversion (missing/changed event IDs, callback fields, conditions, or field mappings):
- Identify expected JSON behavior and replicate it in the corresponding Excel sheet rows/cells.
- If needed, regenerate Excel from JSON as a one-time reconciliation step:

```bash
./gradlew definitionsToExcel
```

- Sync the relevant source workbook from generated workbook:
  - `excel_generated/BEFTA_MASTER.xlsx` -> `excel/BEFTA_Master_Definition.xlsx`
- Re-apply required templating in source Excel if converter introduced hardcoded hosts.

5. Re-run:

```bash
./gradlew definitionsToJson
```

6. Validate:
- No nested templates in JSON:

```bash
rg -n '\$\{TEST_STUB_SERVICE_BASE_URL:\$\{TEST_STUB_SERVICE_BASE_URL:' src/main/resources/uk/gov/hmcts/ccd/test_definitions/valid -g '*.json'
```

- Expected semantic rows/values are preserved after conversion.

7. Trim drift before commit:
- Keep intended source Excel changes.
- Restore JSON files that only differ by normalization/formatting.

## Commit guidance

Prefer commits containing:
- source Excel file(s) changed intentionally
- only JSON changes that are semantic and expected from those Excel updates

Avoid committing large converter churn when it is formatting-only.
