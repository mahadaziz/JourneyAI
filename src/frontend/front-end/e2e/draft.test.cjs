const assert = require('node:assert/strict');
const { randomUUID } = require('node:crypto');
const { test } = require('node:test');
const { chromium } = require('playwright-core');

const baseURL = process.env.JOURNEYAI_TEST_URL || 'http://localhost:3000';
const password = 'local-test-password';

async function signIn(page, email) {
  await page.goto('/login');
  await page.locator('input[name=email]').fill(email);
  await page.locator('input[name=password]').fill(password);
  await page.locator('form button[type=submit]').click();
  await page.waitForURL('**/homepage');
}

async function register(page) {
  const name = `writer-${randomUUID()}`;
  const email = `${name}@example.test`;
  await page.goto('/register');
  await page.locator('input[name=name]').fill(name);
  await page.locator('input[name=email]').fill(email);
  await page.locator('input[name=password]').fill(password);
  await page.locator('input[name=confirmPassword]').fill(password);
  await page.locator('form button[type=submit]').click();
  await page.waitForURL('**/login');
  await signIn(page, email);
  return email;
}

test('a writer can save and reopen formatted text without losing concurrent edits', async (t) => {
  const browser = await chromium.launch({ executablePath: process.env.JOURNEYAI_BROWSER_PATH });
  t.after(() => browser.close());
  const context = await browser.newContext({ baseURL });
  const page = await context.newPage();
  const email = await register(page);

  await page.getByRole('button', { name: 'Upload button' }).click();
  await page.locator('#title').fill('Original title');
  await page.locator('input[type=file]').setInputFiles({
    name: 'report.csv', mimeType: 'text/csv', buffer: Buffer.from('desk,stories\nLocal,4\nArts,3'),
  });
  await page.getByRole('button', { name: 'Submit', exact: true }).click();
  await page.waitForURL('**/dashboard?dataset=*');
  const dashboard = page.url();
  const stale = await context.newPage();
  await stale.goto(dashboard);
  await stale.getByLabel('Draft title').waitFor();
  await page.getByLabel('Draft title').fill('Stories by desk');
  const editor = page.locator('.tiptap[contenteditable=true]');
  const sentence = 'Local reporters filed four stories.';
  await editor.fill(sentence);
  await editor.press('ControlOrMeta+a');
  await page.getByRole('button', { name: 'bold button' }).click();
  assert.equal(await editor.locator('strong').textContent(), sentence);
  const save = page.waitForResponse((r) => r.url().endsWith('/draft') && r.request().method() === 'PUT');
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  const response = await save;
  assert.equal(response.status(), 200);
  assert.equal((await response.json()).revision, 1);
  const data = response.request().postDataJSON();
  assert.equal(data.content.content[0].content[0].text, sentence);
  const retry = await page.request.put(response.url(), { data });
  assert.equal((await retry.json()).revision, 1);

  await stale.locator('.tiptap').fill('My other draft text');
  await stale.getByRole('button', { name: 'Save', exact: true }).click();
  await stale.getByRole('alert').filter({ hasText: 'newer draft' }).waitFor();
  assert.equal(await stale.locator('.tiptap').innerText(), 'My other draft text');

  await page.goto('/api/auth/signout');
  await page.getByRole('button', { name: /sign out/i }).click();
  await page.waitForURL('**/login');
  await signIn(page, email);
  await page.getByText('Stories by desk', { exact: true }).click();
  await page.waitForURL(dashboard);
  assert.equal(await page.getByLabel('Draft title').inputValue(), 'Stories by desk');
  assert.equal(await editor.locator('strong').textContent(), sentence);

  const other = await browser.newContext({ baseURL });
  const otherPage = await other.newPage();
  await register(otherPage);
  const denied = await other.request.put(response.url(), { data });
  assert.equal(denied.status(), 404);
});
