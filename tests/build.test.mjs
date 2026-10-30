import test, { before, after } from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir, rm, stat } from 'node:fs/promises';
import { resolve, dirname, relative } from 'node:path';
import { build } from '../scripts/build.mjs';
import { inquiryHref } from '../scripts/render.mjs';

const root = resolve(import.meta.dirname, '..');
const sandbox = `.artifacts/build-test-${process.pid}`;
const outputDirectory = sandbox + '/empty';
const populatedDirectory = sandbox + '/published';
const routes = ['', 'games/', 'services/', 'games/orbit-foundry/', 'notices/'];
const html = (route, output = outputDirectory) => readFile(resolve(root, output, route + 'index.html'), 'utf8');
const exists = async (path) => { await stat(path); };
const decode = (value) => value.replaceAll('&amp;', '&').replaceAll('&quot;', '"').replaceAll('&#39;', "'").replaceAll('&lt;', '<').replaceAll('&gt;', '>');

before(async () => {
  await mkdir(resolve(root, sandbox, 'notices'), { recursive: true });
  await mkdir(resolve(root, sandbox, 'empty-notices'), { recursive: true });
  await build({ outputDirectory, noticesDirectory: sandbox + '/empty-notices', quiet: true });
  const notice = { title: '정기 주주총회 <소집> 공고', date: '2026-10-01', paragraphs: ['승인된 공고 내용입니다.\n두 번째 줄입니다.', '보존해야 할 원문 & 기호'], signatory: '주식회사 김치스탄스튜디오\n대표이사', attachments: [{ label: '첨부 자료', path: 'assets/studio-social.png' }] };
  for (const [name, data] of Object.entries({
    recent: { ...notice, slug: 'recent-notice' },
    older: { ...notice, title: '2025년 공고', slug: 'older-notice', date: '2025-10-01' },
    draft: { draft: true, slug: 'draft-notice', title: '공개 금지 초안' }
  })) await writeFile(resolve(root, sandbox, 'notices', name + '.json'), JSON.stringify(data));
  await build({ outputDirectory: populatedDirectory, noticesDirectory: sandbox + '/notices', quiet: true });
});
after(async () => { await rm(resolve(root, sandbox), { recursive: true, force: true }); });

test('all public destinations have unique canonical URLs and appear in the sitemap', async () => {
  const sitemap = await readFile(resolve(root, outputDirectory, 'sitemap.xml'), 'utf8');
  for (const route of routes) {
    const source = await html(route);
    assert.ok(source.includes(`<link rel="canonical" href="https://kimchistan.kr/${route}">`), route);
    assert.ok(sitemap.includes(`<loc>https://kimchistan.kr/${route}</loc>`), route);
    assert.equal((source.match(/<h1\b/g) || []).length, 1, route);
    assert.ok(source.includes('<html lang="' + (route === 'notices/' ? 'ko' : 'en') + '">'));
    assert.ok(source.includes('data-text-en=') && source.includes('data-text-ko='));
  }
  assert.ok(!sitemap.includes('404'));
  await exists(resolve(root, outputDirectory, 'CNAME'));
  await exists(resolve(root, outputDirectory, '.nojekyll'));
});

test('all local links, images, scripts, styles, and fragments resolve at every page depth', async () => {
  const files = [...routes.map((route) => route + 'index.html'), 'notices/recent-notice.html', 'notices/older-notice.html'];
  for (const file of files) {
    const source = await readFile(resolve(root, populatedDirectory, file), 'utf8');
    const ids = [...source.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]);
    assert.equal(new Set(ids).size, ids.length, 'Duplicate IDs in ' + file);
    for (const match of source.matchAll(/<(?:a|link|img|script)\b[^>]*?\b(?:href|src)="([^"]+)"/g)) {
      const href = decode(match[1]);
      if (/^(?:https?:|mailto:|data:)/.test(href)) continue;
      const url = new URL(href, 'https://example.test/' + file);
      let target = resolve(root, populatedDirectory, '.' + decodeURIComponent(url.pathname));
      if (url.pathname.endsWith('/')) target = resolve(target, 'index.html');
      assert.ok(target.startsWith(resolve(root, populatedDirectory) + '/'));
      await assert.doesNotReject(exists(target), file + ' -> ' + href);
      if (url.hash) {
        const targetHtml = await readFile(target, 'utf8');
        assert.ok(targetHtml.includes('id="' + decodeURIComponent(url.hash.slice(1)) + '"'), file + ' -> ' + href);
      }
    }
  }
});

test('all vendored font URLs resolve inside the published assets', async () => {
  const cssFile = resolve(root, outputDirectory, 'assets/fonts/pretendardvariable-dynamic-subset.css');
  const css = await readFile(cssFile, 'utf8');
  for (const [, url] of css.matchAll(/url\(([^)]+)\)/g)) {
    const path = resolve(dirname(cssFile), url);
    assert.ok(!relative(resolve(root, outputDirectory, 'assets'), path).startsWith('..'));
    await exists(path);
  }
  await exists(resolve(dirname(cssFile), 'PRETENDARD-LICENSE.txt'));
});

test('legacy homepage destinations and project store links are preserved', async () => {
  const home = await html('');
  for (const id of ['work', 'games', 'services', 'orbit-foundry', 'studio', 'contact', 'notices']) assert.ok(home.includes('id="' + id + '"'), id);
  assert.match(home, /fetchpriority="high"/);
  const orbit = await html('games/orbit-foundry/');
  for (const href of ['https://store.steampowered.com/app/5275040/Orbit_Foundry/', 'https://kimchistan.itch.io/orbit-foundry']) assert.ok(orbit.includes(href));
  assert.match(orbit, /Prototype: desktop browser/);
  const games = await html('games/');
  for (const slug of ['korean-kindergarten', 'goblin-scrap-co', 'daycare-everyday-interiors-240']) assert.ok(games.includes('https://kimchistan.itch.io/' + slug));
});

test('bilingual project briefs are complete, correctly encoded mailto URLs', () => {
  for (const lang of ['en', 'ko']) {
    const url = new URL(inquiryHref('kimmchistanstudio@gmail.com', lang));
    assert.equal(url.protocol, 'mailto:');
    assert.equal(url.pathname, 'kimmchistanstudio@gmail.com');
    assert.ok(url.searchParams.get('subject').includes('KIMCHISTAN STUDIO'));
    const body = url.searchParams.get('body');
    assert.ok(body.includes(lang === 'en' ? 'Current tools:' : '현재 사용하는 도구:'));
    assert.ok(body.includes(lang === 'en' ? 'Budget range (optional):' : '예산 범위 (선택):'));
    assert.ok(body.includes('\n\n'));
  }
});

test('empty notices remain accessible and do not offer nonfunctional filters', async () => {
  const source = await html('notices/');
  assert.ok(source.includes('등록된 공고가 없습니다.'));
  assert.ok(!source.includes('data-notice-search'));
  assert.ok((await html('')).includes('There are currently no published notices.'));
});

test('published notices retain their original text, dates, attachments, and ordering; drafts stay private', async () => {
  const archive = await html('notices/', populatedDirectory);
  assert.ok(archive.indexOf('recent-notice.html') < archive.indexOf('older-notice.html'));
  assert.ok(archive.includes('data-notice-search') && archive.includes('data-notice-year'));
  assert.ok(!archive.includes('draft-notice') && !archive.includes('공개 금지 초안'));
  const notice = await readFile(resolve(root, populatedDirectory, 'notices/recent-notice.html'), 'utf8');
  assert.ok(notice.includes('<article class="notice-document" lang="ko">'));
  assert.ok(notice.includes('승인된 공고 내용입니다.<br>두 번째 줄입니다.'));
  assert.ok(notice.includes('보존해야 할 원문 &amp; 기호'));
  assert.ok(notice.includes('정기 주주총회 &lt;소집&gt; 공고'));
  assert.ok(notice.includes('datetime="2026-10-01"'));
  assert.ok(notice.includes('href="../assets/studio-social.png" download'));
  assert.ok(notice.includes('data-print'));
  await assert.rejects(exists(resolve(root, populatedDirectory, 'notices/draft-notice.html')), { code: 'ENOENT' });
  const sitemap = await readFile(resolve(root, populatedDirectory, 'sitemap.xml'), 'utf8');
  assert.ok(sitemap.includes('notices/recent-notice.html') && !sitemap.includes('draft-notice'));
});

test('nested 404s retain their root-aware asset base and remain unindexed', async () => {
  const source = await readFile(resolve(root, outputDirectory, '404.html'), 'utf8');
  assert.ok(source.includes('name="robots" content="noindex"'));
  assert.ok(source.includes("location.hostname.endsWith('.github.io')"));
  assert.ok(source.includes("document.write('<base href="));
});
