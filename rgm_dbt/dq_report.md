# Data Quality Report

**Report Generated:** As of latest ingestion  
**Data Steward Review Required**

---

## Executive Summary

### Overall Data Health

- **Total Rows Staged:** 28
- **Total Rows in Clean Dataset:** 25
- **Rows Excluded (Quarantined):** 3
- **Data Quality Success Rate:** 89.3% (25/28 rows passed validation)

**Status:** ⚠️ **ATTENTION REQUIRED** - 3 rows have been quarantined due to data quality failures across 3 different validation rules.

---

## Failing Test Details & Recommendations

### 1. ❌ Test: `assert_acv_in_range`

**Failing Row Count:** 1

**What Went Wrong:**  
ACV (All Commodity Volume) distribution percentage must fall between 0% and 100%, representing the percentage of stores carrying a product. The following row contains an ACV value of **150.0%**, which is impossible as it exceeds 100%.

**Offending Row Details:**
- **Week:** 9
- **SKU:** Salmon & Sweet Potato 15lb
- **UPC:** 00012345603
- **ACV Distribution %:** 150.0 ❌ (Valid range: 0-100)
- **Unit Sales:** 450
- **Dollar Sales:** $17,995.50
- **Source File:** week_09_delta.csv
- **Batch ID:** 2

**Root Cause Analysis:**  
This appears to be a data entry error or upstream system corruption. The value may represent a typo (possibly meant to be 15.0% or 50.0%) or a calculation error in the source system.

**Recommendation:** ⛔ **MUST STAY QUARANTINED PENDING INVESTIGATION**

**Rationale:** We cannot safely guess the correct ACV percentage. Using the corrupted value would distort distribution analytics and market coverage calculations. This requires coordination with the data provider to determine the actual ACV value for Salmon & Sweet Potato 15lb in week 9.

---

### 2. ❌ Test: `assert_no_negative_sales`

**Failing Row Count:** 1

**What Went Wrong:**  
Dollar sales values must be non-negative (zero or positive). The following row contains **negative dollar sales of -$33,950.30**, while the base dollar sales field shows the positive value of $33,950.30. Additionally, incremental dollar sales shows -$67,900.60.

**Offending Row Details:**
- **Week:** 9
- **SKU:** Chicken & Rice 15lb
- **UPC:** 00012345602
- **ACV Distribution %:** 89.5%
- **Unit Sales:** 970 (positive)
- **Dollar Sales:** -$33,950.30 ❌ (should be non-negative)
- **Base Dollar Sales:** $33,950.30 (positive)
- **Incremental Dollar Sales:** -$67,900.60 ❌
- **Source File:** week_09_delta.csv
- **Batch ID:** 2

**Root Cause Analysis:**  
This appears to be a sign error where the dollar_sales field was incorrectly negated. The unit sales (970) is positive and the base_dollar_sales ($33,950.30) is positive, suggesting the actual sales amount should be positive. This is likely a data transformation error in the upstream system.

**Recommendation:** ⛔ **MUST STAY QUARANTINED PENDING INVESTIGATION**

**Rationale:** While we might suspect the value should be positive $33,950.30 based on the base_dollar_sales field, we cannot automatically correct this without confirmation. The negative incremental dollar sales (-$67,900.60) adds complexity and may indicate returns, refunds, or promotional allowances that need to be properly understood. Auto-correcting could mask a legitimate business event or perpetuate an upstream error. The data provider must confirm the correct values.

---

### 3. ❌ Test: `assert_unique_week_sku`

**Failing Row Count:** 2

**What Went Wrong:**  
Each combination of week and SKU should appear only once in the dataset. The following duplicate rows were found for **Week 9** and **Chicken & Rice 4lb**, with completely identical values across all fields.

**Offending Row Details (Both Identical):**
- **Week:** 9
- **SKU:** Chicken & Rice 4lb
- **UPC:** 00012345601
- **Pack Size:** 4 lbs
- **ACV Distribution %:** 93.1%
- **Unit Sales:** 1,850
- **Dollar Sales:** $24,024.15
- **Base Unit Sales:** 1,850
- **Base Dollar Sales:** $24,024.15
- **Is Promo:** False
- **Incremental Dollar Sales:** $0.00
- **Incremental Unit Sales:** 0
- **Source File:** week_09_delta.csv
- **Batch ID:** 2

**Root Cause Analysis:**  
These are exact duplicates with identical values across all dimensions and measures. This represents a duplicate transmission of the same record, not two separate sales events. Including both rows would double-count sales for this SKU in week 9.

**Recommendation:** ✅ **SAFE TO AUTO-RESOLVE**

**Rationale:** Since both rows are identical across all fields (including metadata like source file and ingestion timestamp), this is clearly a duplicate send of the same record. The system should deduplicate by keeping one record and discarding the duplicate(s). This is a common data transmission issue that can be safely handled automatically through deduplication logic (e.g., keeping the first occurrence or using a DISTINCT clause). No business information is lost by removing the exact duplicate.

**Suggested Auto-Resolution Logic:** Retain one row per (week, sku) combination when all other fields are identical.

---

## Action Items

### Immediate Actions Required:

1. **ACV Out of Range (1 row):**
   - Contact data provider for week_09_delta.csv
   - Request correction for Salmon & Sweet Potato 15lb ACV value in week 9
   - Keep row quarantined until corrected value received

2. **Negative Sales (1 row):**
   - Contact data provider for week_09_delta.csv
   - Request clarification on Chicken & Rice 15lb sales values in week 9
   - Determine if negative values represent returns/allowances or are errors
   - Keep row quarantined until confirmed

3. **Duplicate Records (2 rows → 1 valid):**
   - Implement automatic deduplication for exact duplicates
   - Can be resolved immediately without provider contact
   - Will recover 1 row to clean dataset once deduplicated

### Expected Recovery:

- **Current Clean Rows:** 25
- **After Deduplication:** 26 (1 row recovered)
- **Remaining Quarantined:** 2 (pending provider corrections)
- **Maximum Possible Clean Rows:** 28 (if all issues resolved)

---

## Summary

The current data quality state shows good overall health at 89.3% pass rate, with 3 issues requiring attention. One issue (duplicate records) can be safely auto-resolved through deduplication, which will improve the clean dataset to 26 rows (92.9% pass rate). The remaining 2 rows contain corrupted values that cannot be safely corrected without upstream investigation and must remain quarantined to prevent analytical errors.

**Next Review:** After provider responds to data correction requests for batch 2 (week_09_delta.csv)