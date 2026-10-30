import { readFile, writeFile, mkdir, readdir, cp, rm, stat } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { pathToFileURL } from 'node:url';
import { e, t, arrow, sparkle, header, footer } from './render.mjs';
import { homePage, gamesPage, servicesPage, orbitPage } from './pages.mjs';

const root = resolve(import.meta.dirname, '..');
const detailPaths = new Set(['games/orbit-foundry/']);
async function json(path) { return JSON.parse(await readFile(resolve(root, path), 'utf8')); }
function requireText(value, field) {
  if (typeof value !== 'string' || !value.trim()) throw new Error(`${field} is required.`);
}
function publicUrl(value, field) {
  const url = new URL(value);
  if (!['https:', 'http:'].includes(url.protocol)) throw new Error(`${field} must be an HTTP(S) URL.`);
}
function localAsset(value, field) {
  if (!/^assets\/[a-zA-Z0-9_./-]+$/.test(value) || value.includes('..')) throw new Error(`${field} must be a path inside assets/.`);
  return value;
}

export async function build({ outputDirectory = 'dist', noticesDirectory = 'content/notices', quiet = false } = {}) {
  const site = await json('content/site.json');
  const games = await json('content/games.json');
  requireText(site.name, 'site.name');
  if (!Array.isArray(games)) throw new Error('content/games.json must be an array.');
  if (site.email && !/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(site.email)) throw new Error('Invalid public contact email.');
  for (const [key, value] of Object.entries(site.links || {})) publicUrl(value, `site.links.${key}`);
  for (const [i, game] of games.entries()) {
    for (const field of ['title', 'summary', 'status']) {
      for (const lang of ['en', 'ko']) requireText(game[field]?.[lang], `games[${i}].${field}.${lang}`);
    }
    requireText(game.image, 'game.image');
    requireText(game.url, 'game.url');
    publicUrl(game.url, 'game.url');
    await stat(resolve(root, localAsset(game.image, 'game image')));
    if (game.detailPath !== undefined && !detailPaths.has(game.detailPath)) throw new Error('game.detailPath must name a generated project page.');
  }
  if (games.filter((game) => game.detailPath === 'games/orbit-foundry/').length !== 1) throw new Error('Exactly one Orbit Foundry detail-page project is required.');
  let origin = '';
  if (site.domain) {
    if (!/^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(site.domain)) throw new Error('site.domain must be a hostname, with no scheme or path.');
    origin = `https://${site.domain}`;
  }
  const notices = [];
  for (const filename of (await readdir(resolve(root, noticesDirectory))).filter((name) => name.endsWith('.json'))) {
    const notice = JSON.parse(await readFile(resolve(root, noticesDirectory, filename), 'utf8'));
    if (notice.draft !== undefined && typeof notice.draft !== 'boolean') throw new Error(`${filename}: draft must be true or false.`);
    if (notice.draft === true) continue;
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(notice.slug || '')) throw new Error(`${filename}: slug must use lowercase letters, digits, and hyphens.`);
    requireText(notice.title, `${filename}: title`);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(notice.date || '') || new Date(`${notice.date}T00:00:00Z`).toISOString().slice(0, 10) !== notice.date) throw new Error(`${filename}: date must be a real YYYY-MM-DD date.`);
    if (!Array.isArray(notice.paragraphs) || !notice.paragraphs.length) throw new Error(`${filename}: at least one paragraph is required.`);
    notice.paragraphs.forEach((paragraph) => requireText(paragraph, `${filename}: paragraph`));
    for (const attachment of notice.attachments || []) {
      requireText(attachment.label, `${filename}: attachment label`);
      await stat(resolve(root, localAsset(attachment.path, `${filename}: attachment path`)));
    }
    if (notices.some((existing) => existing.slug === notice.slug)) throw new Error(`Duplicate notice slug: ${notice.slug}`);
    notices.push(notice);
  }
  notices.sort((a, b) => b.date.localeCompare(a.date) || a.slug.localeCompare(b.slug));
  const output = resolve(root, outputDirectory);
  if (output === root || !output.startsWith(root + '/')) throw new Error('Output must be a subdirectory of the project.');
  await rm(output, { recursive: true, force: true });
  await mkdir(output, { recursive: true });
  await cp(resolve(root, 'assets'), resolve(output, 'assets'), { recursive: true });
  await writeFile(resolve(output, '.nojekyll'), '');
  const publishedPaths = [];
  async function page({ file, title, content, lang = 'en', active = '', description = site.description, robots = '' }) {
    const prefix = '../'.repeat(file.split('/').length - 1);
    const publicPath = file.replace(/index\.html$/, '');
    const canonical = origin ? origin + '/' + publicPath : '';
    const titles = typeof title === 'string' ? { en: title, ko: title } : title;
    const meta = (name, values, property = false) => `<meta ${property ? 'property' : 'name'}="${name}" content="${e(values[lang])}" data-content-en="${e(values.en)}" data-content-ko="${e(values.ko)}">`;
    const baseScript = file === '404.html' ? `<script>const parts=location.pathname.split('/').filter(Boolean);const repo=parts[0];const path=location.hostname.endsWith('.github.io')&&repo&&!repo.endsWith('.github.io')?'/'+repo+'/':'/';document.write('<base href="'+path.replace(/[&<>"']/g,'')+'">');</script>` : '';
    const html = `<!doctype html>
<html lang="${lang}"><head><meta charset="utf-8">${baseScript}<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f4f1e8">
<title data-text-en="${e(titles.en)}" data-text-ko="${e(titles.ko)}">${e(titles[lang])}</title>
${meta('description', description)}${robots ? `<meta name="robots" content="${robots}">` : ''}
${canonical ? `<link rel="canonical" href="${e(canonical)}"><meta property="og:url" content="${e(canonical)}">` : ''}
<meta property="og:type" content="website">${meta('og:title', titles, true)}${meta('og:description', description, true)}<meta property="og:site_name" content="${e(site.name)}"><meta property="og:image" content="${origin ? origin + '/' : prefix}assets/studio-social.png">${meta('og:image:alt', { en: 'KIMCHISTAN STUDIO — Playful worlds. Useful software.', ko: '김치스탄 스튜디오 — 게임은 즐겁게. 일은 더 편하게.' }, true)}<meta name="twitter:card" content="summary_large_image">${meta('twitter:title', titles)}${meta('twitter:description', description)}
<script>try{const l=localStorage.getItem('kimchistan-language');if(l==='en'||l==='ko')document.documentElement.lang=l;}catch{}</script>
<link rel="icon" type="image/svg+xml" href="${prefix}assets/favicon.svg"><link rel="preload" href="${prefix}assets/space-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="${prefix}assets/fonts/pretendardvariable-dynamic-subset.css"><link rel="stylesheet" href="${prefix}assets/styles.css">
<noscript><style>@media(max-width:959px){.site-header{position:static}.header-inner{height:auto;flex-wrap:wrap;padding-block:20px}.site-navigation{display:flex;position:static;order:3;width:100%;flex-wrap:wrap;padding:12px 0 0;border:0;gap:4px 20px;background:none}.site-navigation a{padding:8px 0}.header-actions{margin-left:auto}}.menu-toggle,.language-switch,.js-only{display:none!important}</style></noscript><script src="${prefix}assets/app.js" defer></script></head>
<body>${header(prefix, active, lang)}<main id="main" tabindex="-1">${content}</main>${footer(site, prefix)}</body></html>`;
    await mkdir(dirname(resolve(output, file)), { recursive: true });
    await writeFile(resolve(output, file), html);
    if (!robots.includes('noindex')) publishedPaths.push(publicPath);
  }
  await page({ file: 'index.html', title: { en: site.name + ' — Games, software & AI', ko: site.name + ' — 게임, 소프트웨어 & AI' }, content: homePage(site, games, notices) });
  await page({ file: 'games/index.html', active: 'games', title: { en: 'Games & experiments | ' + site.name, ko: '게임과 실험 | ' + site.name }, description: { en: 'Explore Orbit Foundry, Korean Kindergarten, Goblin Scrap Co., and free resources from KIMCHISTAN STUDIO.', ko: '김치스탄 스튜디오의 Orbit Foundry, Korean Kindergarten, Goblin Scrap Co.와 무료 리소스를 만나보세요.' }, content: gamesPage(site, games) });
  await page({ file: 'services/index.html', active: 'services', title: { en: 'Software & AI services | ' + site.name, ko: '소프트웨어 & AI 서비스 | ' + site.name }, description: { en: 'Custom applications, internal tools, and AI workflow integration for small businesses and teams.', ko: '작은 비즈니스와 팀을 위한 맞춤형 애플리케이션, 내부 업무 도구, AI 업무 연동을 제공합니다.' }, content: servicesPage(site) });
  await page({ file: 'games/orbit-foundry/index.html', active: 'games', title: { en: 'Orbit Foundry — A cosmic factory incremental | ' + site.name, ko: 'Orbit Foundry — 우주 공장 증분 게임 | ' + site.name }, description: { en: 'Build a factory around a star. Explore Orbit Foundry, wishlist on Steam, or try the free desktop-browser prototype.', ko: '별 주위에 나만의 공장을 만드세요. Orbit Foundry를 Steam 위시리스트에 추가하거나 무료 PC 브라우저 프로토타입을 체험해 보세요.' }, content: orbitPage(site) });

  const noticeDescription = { en: `Official corporate notices from ${site.name}.`, ko: `${site.legalName || site.name}의 공식 전자공고 게시판입니다.` };
  const years = [...new Set(notices.map((notice) => notice.date.slice(0, 4)))];
  await page({ file: 'notices/index.html', prefix: '../', lang: 'ko', active: 'notices', title: `전자공고 | ${site.name}`, description: noticeDescription, content: `
    <section class="notice-page section"><div class="container"><a class="breadcrumb" href="../index.html">${t('Home', '홈')}<span aria-hidden="true">/</span>${t('Official notices', '전자공고')}</a><div class="notice-page-heading"><div><p class="eyebrow">KIMCHISTAN STUDIO / ${t('Official announcements', '공식 공고')}</p><h1>${t('Studio notices.', '전자공고.')}</h1><p>${t('Official announcements from KIMCHISTAN STUDIO.', '김치스탄 스튜디오의 공식 공고를 안내합니다.')}</p></div><span class="notice-heading-icon" aria-hidden="true"><svg viewBox="0 0 64 64" fill="none"><path d="M18 9h21l11 11v35H18z" stroke="currentColor" stroke-width="2"/><path d="M39 9v12h11M26 30h16M26 38h16M26 46h10" stroke="currentColor" stroke-width="2"/></svg></span></div>
    ${notices.length ? `<div class="notice-tools"><label class="search-label">${t('Search notices', '공고 검색')}<input type="search" data-notice-search data-label-en="Search notices" data-label-ko="공고 검색" aria-label="공고 검색"></label><label class="year-label">${t('Year', '연도')}<select data-notice-year><option value="" data-text-en="All years" data-text-ko="전체">전체</option>${years.map((year) => `<option value="${year}">${year}</option>`).join('')}</select></label></div><p class="notice-count">${t('Notices', '전체 공고')} <span data-result-count aria-live="polite">${notices.length}</span></p><div class="notice-table"><table><caption class="sr-only">${t('Corporate notices', '회사 전자공고 목록')}</caption><thead><tr><th scope="col">${t('No.', '번호')}</th><th scope="col">${t('Title', '제목')}</th><th scope="col">${t('Date', '공고일')}</th></tr></thead><tbody>${notices.map((notice, i) => `<tr data-notice-row data-search="${e((notice.title + ' ' + notice.date).normalize('NFKC').toLocaleLowerCase())}" data-year="${notice.date.slice(0, 4)}"><td>${String(notices.length - i).padStart(2, '0')}</td><td><a href="${e(notice.slug)}.html" lang="ko">${e(notice.title)}${arrow}</a></td><td><time datetime="${notice.date}">${notice.date.replaceAll('-', '.')}</time></td></tr>`).join('')}</tbody></table><div class="no-search-results" data-no-results hidden>${t('No notices match your search.', '검색 결과가 없습니다.')}</div></div>` : `<div class="notice-table empty-notice-table"><div class="notice-table-header"><span>${t('No.', '번호')}</span><span>${t('Title', '제목')}</span><span>${t('Date', '공고일')}</span></div><div class="notice-empty"><span class="empty-icon" aria-hidden="true">${sparkle}</span><h2>${t('Nothing to announce just yet.', '등록된 공고가 없습니다.')}</h2><p>${t('Official company notices will be published here.', '회사의 공식 공고는 이 페이지에 게시됩니다.')}</p></div></div>`}
    <div class="notice-information"><span class="quiet-dot" aria-hidden="true"></span><p>${t('This page is the official notice archive for KIMCHISTAN STUDIO. Notice documents are published in Korean.', '이 페이지는 김치스탄 스튜디오의 공식 공고 게시판입니다. 공고 내용은 한국어로 제공됩니다.')}</p></div></div></section>` });

  for (const notice of notices) {
    const attachments = (notice.attachments || []).map((attachment) => `<a class="attachment-link" href="../${e(attachment.path)}" download>${e(attachment.label)}<span aria-hidden="true">↓</span></a>`).join('');
    await page({ file: `notices/${notice.slug}.html`, lang: 'ko', prefix: '../', lang: 'ko', active: 'notices', title: `${notice.title} | ${site.name}`, description: { en: `${notice.title} — ${site.name} official notice, ${notice.date}.`, ko: `${notice.title} — ${site.legalName || site.name}, ${notice.date} 공고.` }, content: `<section class="notice-detail section"><div class="container narrow"><a class="breadcrumb" href="./">${t('All notices', '전자공고 목록')}<span aria-hidden="true">/</span><span lang="ko">공고문</span></a><article class="notice-document" lang="ko"><p class="eyebrow">${e(site.legalName || site.name)} / 전자공고</p><h1>${e(notice.title)}</h1><div class="notice-metadata"><span>공고일 <time datetime="${notice.date}">${notice.date.replaceAll('-', '.')}</time></span>${notice.reference ? `<span>공고번호 ${e(notice.reference)}</span>` : ''}</div><div class="notice-body">${notice.paragraphs.map((paragraph) => `<p>${e(paragraph).replaceAll('\n', '<br>')}</p>`).join('')}</div>${notice.signatory ? `<p class="notice-signatory">${e(notice.signatory).replaceAll('\n', '<br>')}</p>` : ''}${attachments ? `<div class="notice-attachments"><h2>첨부파일</h2>${attachments}</div>` : ''}</article><div class="notice-detail-actions"><a class="button button-outline" href="./">${t('Back to notices', '목록으로')}<span aria-hidden="true">←</span></a><button class="text-link js-only" type="button" data-print>${t('Print notice', '공고문 인쇄')}<span aria-hidden="true">↗</span></button></div></div></section>` });
  }

  await page({ file: '404.html', title: { en: 'Page not found | ' + site.name, ko: '페이지를 찾을 수 없습니다 | ' + site.name }, robots: 'noindex', content: `<section class="not-found section"><div class="container"><p class="eyebrow">404 / ${t('A wrong turn', '길을 잃었나요?')}</p><h1>${t('Uncharted<br><em>territory.</em>', '아직 발견하지<br><em>못한 세계.</em>')}</h1><p>${t('This page doesn’t exist. Let’s get you back to the studio.', '이 페이지를 찾을 수 없습니다. 스튜디오로 돌아가 볼까요?')}</p><a class="button button-primary" href="index.html">${t('Back to the studio', '홈으로 돌아가기')}${arrow}</a></div></section>` });
  if (origin) {
    await writeFile(resolve(output, 'CNAME'), site.domain + '\n');
    await writeFile(resolve(output, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${publishedPaths.map((path) => `<url><loc>${origin}/${e(path)}</loc></url>`).join('')}</urlset>`);
    await writeFile(resolve(output, 'robots.txt'), `User-agent: *\nAllow: /\nSitemap: ${origin}/sitemap.xml\n`);
  } else {
    await writeFile(resolve(output, 'robots.txt'), 'User-agent: *\nAllow: /\n');
  }
  if (!quiet) console.log(`Built 4 studio pages, ${games.length} projects, and ${notices.length} published notices in ${outputDirectory}/.`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  await build();
}
