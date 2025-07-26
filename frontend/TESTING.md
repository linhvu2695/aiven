# Playwright Testing Setup

This project uses [Playwright](https://playwright.dev/) for end-to-end testing of the React frontend application.

## Getting Started

### Installation

First, install the dependencies:

```bash
npm install
```

Then install Playwright browsers:

```bash
npx playwright install
```

### Running Tests

```bash
# Run all tests
npm run test

# Run tests with UI mode (interactive)
npm run test:ui

# Run tests in headed mode (see browser)
npm run test:headed

# Debug tests
npm run test:debug

# View test reports
npm run test:report
```

## Test Structure

Tests are organized in the `tests/` directory:

- `basic.spec.ts` - Basic app functionality and navigation
- `chat.spec.ts` - Chat page functionality
- `agent-management.spec.ts` - Agent management page functionality
- `test-utils.ts` - Common utilities and helpers

## Configuration

The Playwright configuration is in `playwright.config.ts` and includes:

- **Multiple browsers**: Chromium, Firefox, Safari
- **Mobile testing**: Chrome and Safari mobile viewports
- **Auto-wait**: Automatically waits for elements to be ready
- **Screenshots/Videos**: Captures on test failures
- **Local dev server**: Automatically starts your dev server

## Writing Tests

### Basic Test Example

```typescript
import { test, expect } from '@playwright/test';

test('example test', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('h1')).toHaveText('Welcome');
});
```

### Using Test Utilities

```typescript
import { test, expect } from '@playwright/test';
import { navigateToRoute, waitForAppLoad, SELECTORS } from './test-utils';

test('navigation test', async ({ page }) => {
  await navigateToRoute(page, '/chat');
  await expect(page.locator(SELECTORS.chatContainer)).toBeVisible();
});
```

## Best Practices

1. **Use data-testid attributes** for stable selectors
2. **Wait for network idle** before assertions
3. **Use page.locator()** instead of page.$()
4. **Group related tests** with test.describe()
5. **Use beforeEach** for common setup

## CI/CD

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

Test reports and artifacts are uploaded and available for 30 days.

## Debugging

### Local Debugging

```bash
# Debug mode - opens browser inspector
npm run test:debug

# UI mode - interactive test runner
npm run test:ui
```

### VS Code Extension

Install the [Playwright Test for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-playwright.playwright) extension for:
- Running tests from the editor
- Setting breakpoints
- Live debugging

## Common Issues

### Port Conflicts
If you get port conflicts, update the `baseURL` in `playwright.config.ts`.

### Slow Tests
Tests may be slow on first run while browsers download. Subsequent runs will be faster.

### Element Not Found
Use `page.waitForSelector()` or increase timeouts for slow-loading components.

## Extending Tests

To add new tests:

1. Create a new `.spec.ts` file in the `tests/` directory
2. Follow the existing pattern and naming conventions
3. Use the utilities in `test-utils.ts` for common operations
4. Add appropriate assertions and error handling

For more advanced testing patterns, see the [Playwright documentation](https://playwright.dev/docs/intro). 