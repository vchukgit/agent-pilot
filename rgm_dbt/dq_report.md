# Data Quality Report

**Report Date:** Current Snapshot  
**Prepared For:** Data Steward

---

## Executive Summary

✅ **Overall Health: HEALTHY**

The data pipeline is functioning normally with no test failures detected.

---

## Overall Data Quality Metrics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Rows Staged** | 31 | 100% |
| **Rows in Clean Dataset** | 27 | 87.1% |
| **Rows Excluded/Quarantined** | 4 | 12.9% |

### Health Assessment

- **87.1%** of staged data successfully made it into the clean dataset
- **4 rows** were excluded during the cleaning process
- **0 active test failures** - all data quality tests are passing

---

## Test Results

### ✅ All Tests Passing

No data quality test failures detected. All validation rules are currently satisfied.

The 4 rows that were excluded from the clean dataset were filtered out by the clean model's business logic (not due to test failures). This is expected behavior and represents normal data filtering operations such as:
- Deduplication logic
- Business rule exclusions
- Standard data transformations

---

## Recommendations

### Immediate Actions Required

**None** - No immediate action required. All data quality tests are passing.

### Monitoring Notes

1. **Review Excluded Rows**: While no test failures exist, consider periodically reviewing the 4 excluded rows to ensure the clean model's filtering logic is operating as intended.

2. **Maintain Baseline**: Current performance (87.1% pass-through rate) can serve as a baseline for future comparisons.

3. **Continue Monitoring**: Maintain regular data quality checks to ensure continued healthy pipeline operation.

---

## Detailed Test Failure Analysis

**No failing tests to report.**

All data quality validations are currently passing. The data pipeline is operating within expected parameters.

---

## Glossary

- **Staged Rows**: Raw data ingested into the staging layer before validation and cleaning
- **Clean Rows**: Validated data that passed all quality checks and business rules
- **Excluded Rows**: Records filtered out by business logic or failing quality tests
- **Safe to Auto-Resolve**: Issues that have been automatically handled (e.g., exact duplicates)
- **Must Stay Quarantined**: Issues requiring manual investigation before resolution

---

*End of Report*