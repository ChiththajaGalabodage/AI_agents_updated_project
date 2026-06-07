# Final Comparison Report

Generated: 2026-06-07T06:21:12.614229+00:00

This report compares the traditional pytest baseline with the agentic continuous-testing pipeline using the proposal metrics: test coverage, defect detection, and execution efficiency. It also reports predictive test-selection footprint and self-healing attempts for the agentic method.

## Benchmark Totals

| Strategy | Test cases | Tests passed | Tests failed |
|---|---:|---:|---:|
| agentic | 158 | 114 | 44 |
| traditional | 150 | 110 | 40 |

## Comparison Matrix

| Metric | Agentic | Traditional | Delta (A - T) | Better | Winner |
|---|---:|---:|---:|---|---|
| Pass rate (%) | 0 | 0 | 0 | Higher | Tie |
| Avg execution time per test (s) | 0.05 | 0.06 | -0.005 | Lower | Agentic |
| Avg pipeline duration (s) | 16.88 | 0 | 16.882 | Lower | Traditional |
| Avg coverage (%) | 39.58 | 37.5 | 2.08 | Higher | Agentic |
| Avg defects detected | 44 | 40 | 4 | Higher | Agentic |
| Avg tests selected | 2 | 1 | 1 | Lower | Traditional |
| Avg heal attempts | 1 | 0 | 1 | Lower | Traditional |
| Avg test cases | 158 | 150 | 8 | Higher | Agentic |
| Avg tests passed | 114 | 110 | 4 | Higher | Agentic |
| Avg tests failed | 44 | 40 | 4 | Lower | Traditional |

**Weighted score**: Agentic 67 vs Traditional 41. Overall winner: Agentic.

## Summary

| Strategy | Runs | Pass Rate % | Test Cases | Passed | Failed | Avg Execution Time / Test (s) | Avg Pipeline Duration (s) | Avg Coverage % | Avg Defects Detected | Avg Tests Selected | Avg Heal Attempts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| agentic | 1 | 0 | 158 | 114 | 44 | 0.05 | 16.88 | 39.58 | 44 | 2 | 1 |
| traditional | 1 | 0 | 150 | 110 | 40 | 0.06 | 0 | 37.5 | 40 | 1 | 0 |

## Delta (Agentic - Traditional)

- Pass rate percent: 0
- Execution time per test seconds: -0.005
- Coverage percent: 2.08
- Defects detected: 4
- Selected tests: 1
- Heal attempts: 1

## Per-Run Details

| Strategy | Run | Passed | Duration (s) | Tests (passed/total) | Defects | Selected Tests | Coverage % |
|---|---:|---|---:|---|---:|---:|---:|
| agentic | 1 | False | 8.537 | 114/158 | 44 | 2 | 39.58 |
| traditional | 1 | False | 8.862 | 110/150 | 40 | 1 | 37.5 |
