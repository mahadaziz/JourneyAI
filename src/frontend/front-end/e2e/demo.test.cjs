const assert = require('node:assert/strict');
const { readFile } = require('node:fs/promises');
const path = require('node:path');
const { test } = require('node:test');
const { chromium } = require('playwright-core');

test('a signed-out reader can explore the public vehicle example', async (t) => {
  const browser = await chromium.launch({ executablePath: process.env.JOURNEYAI_BROWSER_PATH });
  t.after(() => browser.close());
  const context = await browser.newContext({
    baseURL: process.env.JOURNEYAI_TEST_URL || 'http://localhost:3000',
    viewport: { width: 1280, height: 900 },
  });
  const page = await context.newPage();
  const requests = [];
  page.on('request', (req) => requests.push(req));
  assert.equal((await page.goto('/demo')).status(), 200);
  await page.getByRole('heading', { name: 'How did city fuel use change?' }).waitFor();
  const finding = page.locator('[aria-live="polite"]');
  assert.match(await finding.innerText(), /10\.6 L\/100 km in 2018 and 9\.2 L\/100 km in 2023/);
  await page.getByRole('img', { name: /Average city fuel use/ }).locator('path').first().waitFor();
  await page.getByLabel('Vehicle class').selectOption('SUV');
  await page.getByText('6 sample records', { exact: true }).waitFor();
  assert.match(await finding.innerText(), /13\.4 L\/100 km in 2018 and 11\.8 L\/100 km in 2023/);
  await page.getByText('View chart data').click();
  const table = page.getByRole('table', { name: /SUV/ });
  assert.equal(await table.locator('tbody tr').count(), 6);
  assert.equal(await table.locator('tbody td').last().textContent(), '11.8');

  const samplePath = await page.getByRole('link', { name: 'Download the sample CSV' }).getAttribute('href');
  const response = await context.request.get(samplePath);
  assert.equal(response.status(), 200);
  const original = await readFile(path.join(__dirname, '../../../../examples/vehicles.csv'), 'utf8');
  assert.equal((await response.text()).replaceAll('\r\n', '\n'), original.replaceAll('\r\n', '\n'));
  assert.equal(requests.some((req) => req.method() !== 'GET' || new URL(req.url()).pathname.startsWith('/api/')), false);
  await page.setViewportSize({ width: 375, height: 812 });
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true);
  await page.getByRole('link', { name: 'Sign in', exact: true }).click();
  await page.waitForURL('**/login');
  await page.getByRole('link', { name: 'Explore the sample dashboard' }).click();
  await page.waitForURL('**/demo');
  await page.goto('/dashboard');
  await page.waitForURL('**/login');
});
