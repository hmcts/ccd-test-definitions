---
name: ccd-json-excel-guard
description: Use this to enforce guard rails for JSON/Excel reconciliation in ccd-test-definitions: detect semantic discrepancies, preserve templated URLs, validate converter output, and trim normalization-only churn before commit.
---

# JSON-Excel Guard Rail

Use this skill whenever changes involve either JSON definitions or Excel definition workbooks.

## Objectives

- Prevent accidental semantic drift between source Excel and generated JSON.
- Preserve template placeholders required by environments.
- Keep commits focused by excluding formatting-only conversion churn.

## Guard rail workflow

1. Run conversion from Excel to JSON:

```bash
./gradlew definitionsToJson
```

2. Classify diffs:
- Semantic: IDs, `CaseEventID`, `CaseFieldID`, callbacks, conditions, states, `NullifyByDefault`, `Publish*` behavior.
- Non-semantic: date formatting (`LiveFrom`, `LiveTo`), whitespace, comma/array layout.

3. Enforce templating policy:
- Keep callback bases templated in source Excel/JSON where expected:
  - `${TEST_STUB_SERVICE_BASE_URL:http://ccd-test-stubs-service-aat.service.core-compute-aat.internal}`
  - `${MCA_API_BASE_URL:http://aac-manage-case-assignment-aat.service.core-compute-aat.internal}`
- Reject hardcoded local hosts in committed definitions unless explicitly requested.

4. If semantic discrepancy is required:
- Apply the change to source Excel so `definitionsToJson` reproduces it.
- Re-run `definitionsToJson` and confirm stability.

5. Validate template integrity:

```bash
rg -n '\$\{TEST_STUB_SERVICE_BASE_URL:\$\{TEST_STUB_SERVICE_BASE_URL:' src/main/resources/uk/gov/hmcts/ccd/test_definitions/valid -g '*.json'
```

6. Trim before commit:
- Keep intended source files and semantic generated JSON only.
- Restore normalization-only drift.

## Commit rule

A valid commit should be reproducible by running `./gradlew definitionsToJson` and should not introduce unintended semantic JSON changes.
