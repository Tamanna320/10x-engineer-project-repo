# CI Gate Evidence

## Baseline

The GitHub Actions CI pipeline passed successfully before the deliberate test failure.

The pipeline runs linting with Ruff and the test suite with pytest and pytest-cov. The workflow also enforces the minimum coverage requirement of 80%.

## Deliberate Test Failure

To verify that the CI pipeline actually gates broken code, one existing test assertion was intentionally changed.

Commit:
a784f37

The test `tests/test_api.py::TestRestore::test_restore_happy_path` was intentionally changed so that the expected HTTP status code was incorrect.

The test expected:
201
while the actual response status code was:
200

This was a deliberate test failure. No application code or CI workflow was changed for this test.

## Failed GitHub Actions Run

GitHub Actions run:
https://github.com/Tamanna320/10x-engineer-project-repo/actions/runs/35895269519

Failed test:
`tests/test_api.py::TestRestore::test_restore_happy_path`

Failure:
`assert 200 == 201`

The test run reported:
1 failed, 185 passed, 3 warnings

The workflow then reported:
Process completed with exit code 1.

This confirms that the GitHub Actions workflow failed when the test suite contained a failing test.

Coverage was still reported as 100%, so the failure was caused by the deliberately broken test assertion rather than insufficient coverage.

## Test Restoration

After capturing the failed CI run, the intentionally incorrect assertion was restored to its original expected value.

The restored test was committed and pushed.

Restoration commit:
ce26f04

## Successful GitHub Actions Run After Restoration

GitHub Actions run:
https://github.com/Tamanna320/10x-engineer-project-repo/actions/runs/35896333986

The workflow completed successfully after the test was restored.

Status:
Success

This confirms that the same CI pipeline returns to a passing state when the test is corrected.

## Conclusion

The CI pipeline was deliberately tested with a broken test.

The sequence was:

1. CI passed with the correct test suite.
2. A test assertion was deliberately changed.
3. Commit `a784f37` was pushed.
4. GitHub Actions detected the failing test.
5. The workflow failed with exit code 1.
6. The failed run was captured as evidence.
7. The test assertion was restored.
8. Commit `ce26f04` was pushed.
9. GitHub Actions passed successfully again.

This demonstrates that the CI pipeline detects failing tests and prevents broken code from passing the build.