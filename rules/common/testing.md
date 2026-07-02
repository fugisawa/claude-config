# Testing Requirements

## Minimum Test Coverage: 80%

Test Types (ALL required):
1. **Unit Tests** - Individual functions, utilities, components
2. **Integration Tests** - API endpoints, database operations
3. **E2E Tests** - Critical user flows (framework chosen per language)

## Test-Driven Development

MANDATORY workflow:
1. Write test first (RED)
2. Run test - it should FAIL
3. Write minimal implementation (GREEN)
4. Run test - it should PASS
5. Refactor (IMPROVE)
6. Verify coverage (80%+)

## Seams — where tests go

A **seam** is the public boundary you test at. Tests live at seams, never against internals.
- **Agree seams up front**: before writing any test, list the seams under test and confirm them with the user ("What's the public interface, and which seams should we test?"). No test at an unconfirmed seam.
- Prefer existing seams to new ones; prefer the highest seam possible. Fewer seams = better.

## Anti-patterns (reject on sight)

- **Implementation-coupled** — mocks internal collaborators, tests private methods, or verifies through a side channel. Tell: the test breaks on refactor though behavior didn't change.
- **Tautological** — the assertion recomputes the expected value the same way the code does (`expect(add(a,b)).toBe(a+b)`), so it passes by construction. Expected values must come from an independent source of truth: a known-good literal, a worked example, the spec.
- **Horizontal slicing** — writing all tests first, then all implementation. Work in **vertical slices** instead: one test → one implementation → repeat, each test a tracer bullet informed by the last cycle.

## Troubleshooting Test Failures

1. Use **tdd-guide** agent
2. Check test isolation
3. Verify mocks are correct
4. Fix implementation, not tests (unless tests are wrong)

## Agent Support

- **tdd-guide** - Use PROACTIVELY for new features, enforces write-tests-first
