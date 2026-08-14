# Agents

Repo-local workflow skills live under `docs/skills/`.

## CaseTypeTab ListElementCode

Skill doc: `docs/skills/CaseTypeTab_ListElementCode/SKILL.md`

Use for CCD-6251 `CaseTypeTab.ListElementCode` fixture work: valid/invalid workbooks, generated valid JSON, AC row comments, import constraints, and Excel package cleanup.

Trigger phrases:

- "Use CaseTypeTab_ListElementCode"
- "Update CaseTypeTab ListElementCode fixtures"

Core checks:

```bash
./gradlew definitionsToJson
./gradlew build
```

## Excel for Group Access

Skill doc: `docs/skills/excel_for_groupaccess/SKILL.md`

Use for `BEFTA_MASTER_GROUPACCESS.xlsx` workbook maintenance, especially cleanup after Excel/zip edits, table range repair, and import-readiness checks.

Trigger phrases:

- "Use excel_for_groupaccess"
- "Fix BEFTA_MASTER_GROUPACCESS.xlsx"

Core cleanup:

```bash
./scripts/fix_jurisdiction_rows.py
```
