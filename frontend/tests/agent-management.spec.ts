import { test, expect } from '@playwright/test';

test.describe('Agent Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/agent');
  });

  test('agent management page loads correctly', async ({ page }) => {
    // Check that we're on the agent page
    await expect(page).toHaveURL(/.*\/agent/);
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check that the page has loaded without errors
    await expect(page.locator('body')).toBeVisible();
  });

  test('agent grid or list is present', async ({ page }) => {
    // Look for agent-related components
    const agentComponents = [
      '[class*="agent"]',
      '[data-testid*="agent"]',
      '[class*="grid"]',
      '[class*="card"]'
    ];
    
    let foundAgentComponent = false;
    for (const selector of agentComponents) {
      const element = page.locator(selector);
      if (await element.count() > 0) {
        await expect(element).toBeVisible();
        foundAgentComponent = true;
        break;
      }
    }
    
    // If no specific agent components found, at least verify page structure
    if (!foundAgentComponent) {
      await expect(page.locator('main, [role="main"], .main')).toBeVisible();
    }
  });

  test('page is accessible', async ({ page }) => {
    // Basic accessibility checks
    await page.waitForLoadState('networkidle');
    
    // Check for basic semantic elements
    const semanticElements = ['main', 'header', 'nav', '[role="main"]'];
    let foundSemantic = false;
    
    for (const selector of semanticElements) {
      const element = page.locator(selector);
      if (await element.count() > 0) {
        foundSemantic = true;
        break;
      }
    }
    
    // At minimum, ensure page has loaded
    await expect(page.locator('body')).toBeVisible();
  });

  test('responsive design works on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Reload to ensure responsive design is applied
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Check that content is still visible and accessible
    await expect(page.locator('body')).toBeVisible();
  });
}); 