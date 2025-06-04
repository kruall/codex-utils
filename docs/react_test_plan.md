# React Dashboard Test Plan

This document outlines the testing strategy for the TM_WEB React dashboard. It covers unit tests, integration tests, and component testing.

## Goals
- Verify that all UI components render correctly and handle user interactions.
- Ensure integration with the task manager API functions properly.
- Provide confidence during refactoring through high test coverage.

## Testing Framework
- **Jest** for running the test suites.
- **React Testing Library** for DOM interactions and component behavior.
- **msw (Mock Service Worker)** for mocking API responses during integration tests.

## Test Types
### Unit Tests
Focus on isolated components and utility functions. Stub external modules and assert rendering and callbacks.

### Integration Tests
Test multiple components working together, including API hooks. Use `msw` to simulate backend responses.

### Component Snapshot Tests
Use Jest snapshots sparingly to detect unintentional UI changes. Update snapshots only when visual changes are intentional.

## Coverage Requirements
- Aim for **80% line coverage** across the `components/`, `hooks/`, and `lib/` directories.
- Critical components such as the task list and task detail views should approach **100% coverage**.

## Continuous Integration
All tests run through the `./run_tests` script, which invokes `npm test` inside `react-dashboard/`.

## Directory Structure
```
react-dashboard/
  components/      # UI components
  hooks/           # React hooks
  lib/             # Utility modules
  __tests__/       # Shared test utilities
```

## Writing New Tests
1. Place test files alongside the component using `*.test.tsx` or `*.test.ts`.
2. Import utilities from `@testing-library/react` to render components.
3. Mock API calls with `msw` handlers defined in `__tests__/mocks`.
4. Use `npm test -- -u` to update snapshots when needed.

## Running Tests Locally
```
cd react-dashboard
npm install
npm test
```

The Jest configuration is in `react-dashboard/jest.config.js` and automatically loads `jest.setup.js` before each test run.

