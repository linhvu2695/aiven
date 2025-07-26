import { test, expect } from '@playwright/test';

test.describe('Basic App Functionality', () => {
  test('app loads successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check that the page loads without errors
    await expect(page).toHaveTitle(/Aiven/);
    
    // Check that the navbar is visible
    await expect(page.locator('nav')).toBeVisible();
  });

  test('navigation bar is present', async ({ page }) => {
    await page.goto('/');
    
    // Check if navbar component is rendered
    // This will need to be updated based on your actual navbar implementation
    const navbar = page.locator('nav');
    await expect(navbar).toBeVisible();
  });

  test('can navigate to chat page', async ({ page }) => {
    await page.goto('/');
    
    // Navigate to chat route
    await page.goto('/chat');
    
    // Check that we're on the chat page
    await expect(page).toHaveURL(/.*\/chat/);
  });

  test('can navigate to agent management page', async ({ page }) => {
    await page.goto('/');
    
    // Navigate to agent route  
    await page.goto('/agent');
    
    // Check that we're on the agent page
    await expect(page).toHaveURL(/.*\/agent/);
  });

  test('app is responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Check that the navbar is visible
    await expect(page.locator('nav')).toBeVisible();
  });
}); 