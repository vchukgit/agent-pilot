# Data Quality Report

## Current State

The system has loaded **27 week and SKU combinations**, and **27 of them have a clean row**. There are **0 combinations missing a clean row**.

## Excluded Rows

A total of **4 rows** were excluded from the clean dataset. All excluded rows were resolved by later batches, so no data is missing.

### Week 9, Chicken & Rice 15lb (batch 2, week_09_delta.csv)
- **Excluded:** 1 row
- **Reason:** Negative sales value
- **Resolution:** A later batch (batch 3) supplied a valid row for this week and SKU, so nothing is missing.

### Week 9, Chicken & Rice 4lb (batch 2, week_09_delta.csv)
- **Excluded:** 2 rows
- **Reason:** Superseded by later batch
- **Resolution:** A later batch (batch 3) supplied a valid row for this week and SKU, so nothing is missing.

### Week 9, Salmon & Sweet Potato 15lb (batch 2, week_09_delta.csv)
- **Excluded:** 1 row
- **Reason:** ACV out of range
- **Resolution:** A later batch (batch 3) supplied a valid row for this week and SKU, so nothing is missing.

## Items Needing Attention

Nothing needs attention.

## Test Results

All data quality tests are passing. No failing tests to report.