import { Page, expect } from '@playwright/test';

/**
 * Common test utilities for Playwright tests
 */

/**
 * Wait for the application to load completely
 */
export async function waitForAppLoad(page: Page) {
  await page.waitForLoadState('networkidle');
  await expect(page.locator('body')).toBeVisible();
}

/**
 * Check if the navigation bar is present and functional
 */
export async function checkNavigation(page: Page) {
  const navbar = page.locator('nav, [role="navigation"], [data-testid="navbar"]');
  await expect(navbar).toBeVisible();
  return navbar;
}

/**
 * Navigate to a specific route and verify the URL
 */
export async function navigateToRoute(page: Page, route: string) {
  await page.goto(route);
  await expect(page).toHaveURL(new RegExp(`.*${route.replace('/', '\\/')}`));
  await waitForAppLoad(page);
}

/**
 * Check for common accessibility patterns
 */
export async function checkBasicAccessibility(page: Page) {
  // Check for semantic HTML elements
  const semanticElements = [
    'main', 
    'header', 
    'nav', 
    '[role="main"]', 
    '[role="navigation"]'
  ];
  
  let foundSemantic = false;
  for (const selector of semanticElements) {
    const element = page.locator(selector);
    if (await element.count() > 0) {
      foundSemantic = true;
      break;
    }
  }
  
  return foundSemantic;
}

/**
 * Test responsive design at different viewport sizes
 */
export async function testResponsiveDesign(page: Page, url: string = '/') {
  const viewports = [
    { width: 375, height: 667, name: 'Mobile' },
    { width: 768, height: 1024, name: 'Tablet' },
    { width: 1200, height: 800, name: 'Desktop' }
  ];
  
  for (const viewport of viewports) {
    await page.setViewportSize(viewport);
    await page.goto(url);
    await waitForAppLoad(page);
    
    // Basic check that content is still visible
    await expect(page.locator('body')).toBeVisible();
  }
}

/**
 * Common selectors for the application
 */
export const SELECTORS = {
  navbar: 'nav, [role="navigation"], [data-testid="navbar"]',
  chatContainer: '[class*="chat"], [data-testid="chat-container"]',
  agentSelector: '[class*="agent"], [data-testid*="agent"]',
  chatInput: 'textarea, input[type="text"], [contenteditable="true"], [placeholder*="message" i]',
  mainContainer: '[class*="chakra-container"], main, [role="main"]'
} as const; 