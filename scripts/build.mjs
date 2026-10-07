import { readFile, writeFile, mkdir, readdir, cp, rm, stat } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const root = resolve(import.meta.dirname, '..');
const e = (value = '') => String(value).replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
const t = (en, ko, className = '') => `<span class="locale ${className}" lang="en">${en}</span><span class="locale ${className}" lang="ko">${ko}</span>`;
const arrow = '<svg class="arrow-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14" stroke="currentColor" stroke-width="1.7"/></svg>';
const sparkle = '<svg viewBox="0 0 32 32" fill="none" aria-hidden="true"><path d="m16 1 4 11 11 4-11 4-4 11-4-11-11-4 11-4z" fill="currentColor"/></svg>';

async function json(path) { return JSON.parse(await readFile(resolve(root, path), 'utf8')); }
function publicUrl(value, field) {
  const url = new URL(value);
  if (!['https:', 'http:'].includes(url.protocol)) throw new Error(`${field} must be an HTTP(S) URL.`);
  return url.href;
}
function localAsset(value, field) {
  if (!/^assets\/[a-zA-Z0-9_./-]+$/.test(value) || value.includes('..')) throw new Error(`${field} must be a path inside assets/.`);
  return value;
}
function requireText(value, field) {
  if (typeof value !== 'string' || !value.trim()) throw new Error(`${field} is required.`);
  return value;
}
function localized(value, field) {
  requireText(value?.en, `${field}.en`);
  requireText(value?.ko, `${field}.ko`);
  return t(e(value.en), e(value.ko));
}

export async function build({ outputDirectory = 'dist', noticesDirectory = 'content/notices', quiet = false } = {}) {
  const site = await json('content/site.json');
  const games = await json('content/games.json');
  requireText(site.name, 'site.name');
  if (!Array.isArray(games)) throw new Error('content/games.json must be an array.');
  if (site.email && !/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(site.email)) throw new Error('Invalid public contact email.');
  for (const game of games) {
    if (game.image) await stat(resolve(root, localAsset(game.image, 'game image')));
  }
  let origin = '';
  if (site.domain) {
    if (!/^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(site.domain)) throw new Error('site.domain must be a hostname, with no scheme or path.');
    origin = `https://${site.domain}`;
  }

  const notices = [];
  const noticeSource = resolve(root, noticesDirectory);
  for (const filename of (await readdir(noticeSource)).filter((name) => name.endsWith('.json'))) {
    const notice = JSON.parse(await readFile(resolve(noticeSource, filename), 'utf8'));
    if (notice.draft !== undefined && typeof notice.draft !== 'boolean') throw new Error(`${filename}: draft must be true or false.`);
    if (notice.draft === true) continue;
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(notice.slug || '')) throw new Error(`${filename}: slug must use lowercase letters, digits, and hyphens.`);
    requireText(notice.title, `${filename}: title`);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(notice.date || '') || new Date(`${notice.date}T00:00:00Z`).toISOString().slice(0, 10) !== notice.date) throw new Error(`${filename}: date must be a real YYYY-MM-DD date.`);
    if (!Array.isArray(notice.paragraphs) || !notice.paragraphs.length) throw new Error(`${filename}: at least one paragraph is required.`);
    notice.paragraphs.forEach((paragraph) => requireText(paragraph, `${filename}: paragraph`));
    for (const attachment of notice.attachments || []) {
      requireText(attachment.label, `${filename}: attachment label`);
      localAsset(attachment.path, `${filename}: attachment path`);
      await stat(resolve(root, attachment.path));
    }
    if (notices.some((existing) => existing.slug === notice.slug)) throw new Error(`Duplicate notice slug: ${notice.slug}`);
    notices.push(notice);
  }
  notices.sort((a, b) => b.date.localeCompare(a.date) || a.slug.localeCompare(b.slug));
  const output = resolve(root, outputDirectory);
  if (output === root || !output.startsWith(root + '/')) throw new Error('Output must be a subdirectory of the project.');
  await rm(output, { recursive: true, force: true });
  await mkdir(resolve(output, 'notices'), { recursive: true });
  await cp(resolve(root, 'assets'), resolve(output, 'assets'), { recursive: true });
  await writeFile(resolve(output, '.nojekyll'), '');

  function header(prefix, active = '') {
    return `<a class="skip-link" href="#main">${t('Skip to content', '본문 바로가기')}</a>
      <header class="site-header"><div class="container header-inner">
        <a class="brand" href="${prefix}index.html" aria-label="${e(site.name)} home">${e(site.name)}</a>
        <nav class="site-navigation" id="site-navigation" aria-label="Main navigation">
          <a href="${prefix}index.html#studio">${t('The studio', '스튜디오')}</a>
          <a href="${prefix}index.html#games">${t('Our games', '게임')}</a>
          <a href="${prefix}notices/" ${active === 'notices' ? 'aria-current="page"' : ''}>${t('Notices <span class="nav-korean">공고</span>', '전자공고')}</a>
          ${site.email ? `<a class="mobile-contact" href="${prefix}index.html#contact">${t('Get in touch', '문의하기')}${arrow}</a>` : ''}
        </nav>
        <div class="header-actions"><div class="language-switch" aria-label="Language / 언어"><button type="button" data-language="en" aria-pressed="true">EN</button><span aria-hidden="true">/</span><button type="button" data-language="ko" aria-pressed="false" lang="ko">KO</button></div>${site.email ? `<a class="header-contact" href="${prefix}index.html#contact">${t('Let’s talk', '문의하기')}${arrow}</a>` : ''}<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-navigation" aria-label="Open navigation" data-label-en="Open navigation" data-label-ko="메뉴 열기"><span></span><span></span></button></div>
      </div></header>`;
  }
  function footer(prefix) {
    const fields = [site.legalName, site.representative && `대표자 ${site.representative}`, site.registrationNumber && `사업자등록번호 ${site.registrationNumber}`, site.address?.ko].filter(Boolean);
    return `<footer class="site-footer"><div class="container"><div class="footer-top"><a class="brand footer-brand" href="${prefix}index.html">${e(site.name)}</a><p>${t('A little spice. A whole new world.', '작은 특별함으로, 새로운 세계를.')}</p><a class="footer-notices" href="${prefix}notices/">${t('Official notices · 공고', '전자공고')}${arrow}</a></div>${fields.length ? `<p class="company-legal" lang="ko">${fields.map(e).join(' <span aria-hidden="true">·</span> ')}</p>` : ''}<div class="footer-bottom"><span>© ${new Date().getFullYear()} ${e(site.name)}. ${t('All rights reserved.', 'All rights reserved.')}</span><span>${t('Made with a little extra flavor.', '우리만의 특별함을 담아.')}</span></div></div></footer>`;
  }
  async function page({ file, title, content, prefix = '', lang = 'en', active = '', description = site.description, robots = '' }) {
    const canonical = origin ? `${origin}/${file === 'index.html' ? '' : file === 'notices/index.html' ? 'notices/' : file}` : '';
    const html = `<!doctype html>
<html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f7f6ef"><title>${e(title)}</title><meta name="description" content="${e(description[lang])}" data-en="${e(description.en)}" data-ko="${e(description.ko)}">${robots ? `<meta name="robots" content="${robots}">` : ''}${canonical ? `<link rel="canonical" href="${e(canonical)}"><meta property="og:url" content="${e(canonical)}">` : ''}<meta property="og:type" content="website"><meta property="og:title" content="${e(title)}"><meta property="og:description" content="${e(description[lang])}"><meta property="og:site_name" content="${e(site.name)}"><meta name="twitter:card" content="summary"><link rel="icon" href="data:,"><link rel="preload" href="${prefix}assets/space-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="${prefix}assets/styles.css"><noscript><style>@media(max-width:800px){.header-inner{height:auto;flex-wrap:wrap;padding-block:20px}.site-navigation{display:flex;position:static;order:3;width:100%;flex-wrap:wrap;gap:20px;padding:0;border:0;box-shadow:none}.site-navigation a{padding:5px 0}.menu-toggle,.language-switch{display:none!important}}</style></noscript><script src="${prefix}assets/app.js" defer></script></head><body>${header(prefix, active)}<main id="main">${content}</main>${footer(prefix)}</body></html>`;
    await writeFile(resolve(output, file), html);
  }

  const gameCards = games.map((game, i) => {
    const title = localized(game.title, `games[${i}].title`);
    const summary = localized(game.summary, `games[${i}].summary`);
    const status = localized(game.status, `games[${i}].status`);
    const image = game.image ? `<img src="${e(localAsset(game.image, 'game image'))}" alt="${e(game.title.en)}" loading="lazy">` : `<div class="game-cover-placeholder">${sparkle}<span>${title}</span></div>`;
    const url = game.url ? publicUrl(game.url, 'game.url') : '';
    return `<article class="game-card">${image}<div class="game-card-copy"><span class="status-label">${status}</span><h3>${title}</h3><p>${summary}</p>${url ? `<a class="text-link" href="${e(url)}" target="_blank" rel="noopener noreferrer">${t('Explore game', '게임 살펴보기')}${arrow}</a>` : ''}</div></article>`;
  }).join('');

  const companyRows = [
    [t('Studio', '스튜디오'), e(site.name)],
    ...(site.legalName ? [[t('Legal name', '법인명'), e(site.legalName)]] : []),
    [t('What we do', '사업 분야'), t('Game development', '게임 개발')],
    ...(site.representative ? [[t('Representative', '대표자'), e(site.representative)]] : []),
    ...(site.address?.en || site.address?.ko ? [[t('Address', '주소'), t(e(site.address.en || site.address.ko), e(site.address.ko || site.address.en))]] : []),
    ...(site.registrationNumber ? [[t('Business registration', '사업자등록번호'), e(site.registrationNumber)]] : [])
  ];
  const noticesPreview = notices.length ? `<div class="home-notice-list">${notices.slice(0, 3).map((notice) => `<a href="notices/${e(notice.slug)}.html"><time datetime="${notice.date}">${notice.date.replaceAll('-', '.')}</time><span lang="ko">${e(notice.title)}</span>${arrow}</a>`).join('')}</div>` : `<div class="notice-summary"><span class="quiet-dot" aria-hidden="true"></span>${t('No notices at the moment.', '현재 등록된 공고가 없습니다.')}</div>`;
  await page({ file: 'index.html', title: `${site.name} — Games with character.`, content: `
    <section class="hero"><div class="container"><p class="eyebrow"><span class="live-dot" aria-hidden="true"></span>${t('KIMCHISTAN STUDIO / Game development', '킴치스탄 스튜디오 / 게임 개발')}</p><h1>${t('Games with<br>a little <span class="accent-word">character.</span>', '개성 있는 게임,<br>새로운 <span class="accent-word">즐거움.</span>')}</h1><div class="hero-bottom"><p class="hero-description">${t('We’re KIMCHISTAN STUDIO. A game studio creating new worlds with curiosity, care, and a little extra flavor.', '우리는 킴치스탄 스튜디오입니다. 호기심과 정성, 그리고 우리만의 특별함을 담아 새로운 세계를 만드는 게임 스튜디오입니다.')}</p><a class="button button-primary" href="#studio">${t('Meet the studio', '스튜디오 소개')}${arrow}</a></div></div></section>
    <section class="studio-section section" id="studio"><div class="container"><div class="section-heading"><p class="eyebrow"><span class="section-number">01 /</span>${t('The studio', '스튜디오')}</p></div><div class="studio-grid"><div><h2>${t('A new world<br>starts with an idea.', '새로운 세계는<br>하나의 생각에서.')}</h2><p class="studio-intro">${t('We make games with personality. Our goal is simple: create experiences that are fun to discover and worth coming back to.', '우리는 개성 있는 게임을 만듭니다. 발견하는 즐거움과 다시 찾고 싶은 경험을 만드는 것이 우리의 목표입니다.')}</p></div><dl class="company-details">${companyRows.map(([label, value]) => `<div><dt>${label}</dt><dd>${value}</dd></div>`).join('')}</dl></div></div></section>
    <section class="games-section section" id="games"><div class="container"><div class="section-heading"><p class="eyebrow"><span class="section-number">02 /</span>${t('Our games', '우리의 게임')}</p></div><div class="games-heading"><h2>${t('More to play.<br>More to discover.', '플레이의 즐거움,<br>발견하는 재미.')}</h2><p>${t('Discover the games and projects from KIMCHISTAN STUDIO.', '킴치스탄 스튜디오의 게임과 프로젝트를 소개합니다.')}</p></div>${gameCards ? `<div class="game-grid">${gameCards}</div>` : `<div class="games-empty"><span class="status-label"><span class="quiet-dot"></span>${t('Stay tuned', '새로운 소식을 기다려 주세요')}</span><h3>${t('Our next adventure starts here.', '새로운 모험이 이곳에서 시작됩니다.')}</h3><p>${t('Game announcements and product information will be shared here.', '게임 소식과 제품 정보는 이곳에 공개할 예정입니다.')}</p></div>`}</div></section>
    <section class="notices-section section" id="notices"><div class="container notice-home-grid"><div><p class="eyebrow"><span class="section-number">03 /</span>${t('Official notices · 공고', '전자공고')}</p><h2>${t('Official notices.', '전자공고.')}</h2><p>${t('Corporate announcements from KIMCHISTAN STUDIO.', '주식회사 김치스탄스튜디오의 공식 공고를 안내합니다.')}</p></div><div class="notice-home-right">${noticesPreview}<a class="button button-outline" href="notices/">${t('View all notices', '전자공고 바로가기')}${arrow}</a></div></div></section>
    ${site.email ? `<section class="contact-section section" id="contact"><div class="container contact-grid"><div><p class="eyebrow">${t('Get in touch', '문의하기')}</p><h2>${t('Say hello.', '함께 이야기해요.')}</h2></div><div><p>${t('For questions and collaboration, get in touch with our studio.', '문의 및 협업 제안은 아래 이메일로 보내 주세요.')}</p><a class="contact-email" href="mailto:${e(site.email)}">${e(site.email)}${arrow}</a></div></div></section>` : ''}
  ` });

  const noticeDescription = { en: `Official corporate notices from ${site.name}.`, ko: `${site.legalName || site.name}의 공식 전자공고 게시판입니다.` };
  const years = [...new Set(notices.map((notice) => notice.date.slice(0, 4)))];
  await page({ file: 'notices/index.html', prefix: '../', lang: 'ko', active: 'notices', title: `전자공고 | ${site.name}`, description: noticeDescription, content: `
    <section class="notice-page section"><div class="container"><a class="breadcrumb" href="../index.html">${t('Home', '홈')}<span aria-hidden="true">/</span>${t('Official notices', '전자공고')}</a><div class="notice-page-heading"><div><p class="eyebrow">KIMCHISTAN STUDIO / ${t('Official announcements', '공식 공고')}</p><h1>${t('Studio notices.', '전자공고.')}</h1><p>${t('Official announcements from KIMCHISTAN STUDIO.', '킴치스탄 스튜디오의 공식 공고를 안내합니다.')}</p></div><span class="notice-heading-icon" aria-hidden="true"><svg viewBox="0 0 64 64" fill="none"><path d="M18 9h21l11 11v35H18z" stroke="currentColor" stroke-width="2"/><path d="M39 9v12h11M26 30h16M26 38h16M26 46h10" stroke="currentColor" stroke-width="2"/></svg></span></div>
    ${notices.length ? `<div class="notice-tools"><label class="search-label">${t('Search notices', '공고 검색')}<input type="search" data-notice-search data-label-en="Search notices" data-label-ko="공고 검색" aria-label="공고 검색"></label><label class="year-label">${t('Year', '연도')}<select data-notice-year><option value="">${e('전체 / All years')}</option>${years.map((year) => `<option value="${year}">${year}</option>`).join('')}</select></label></div><p class="notice-count">${t('Notices', '전체 공고')} <span data-result-count>${notices.length}</span></p><div class="notice-table"><table><caption class="sr-only">${t('Corporate notices', '회사 전자공고 목록')}</caption><thead><tr><th scope="col">${t('No.', '번호')}</th><th scope="col">${t('Title', '제목')}</th><th scope="col">${t('Date', '공고일')}</th></tr></thead><tbody>${notices.map((notice, i) => `<tr data-notice-row data-search="${e((notice.title + ' ' + notice.date).normalize('NFKC').toLocaleLowerCase())}" data-year="${notice.date.slice(0, 4)}"><td>${String(notices.length - i).padStart(2, '0')}</td><td><a href="${e(notice.slug)}.html" lang="ko">${e(notice.title)}${arrow}</a></td><td><time datetime="${notice.date}">${notice.date.replaceAll('-', '.')}</time></td></tr>`).join('')}</tbody></table><div class="no-search-results" data-no-results hidden>${t('No notices match your search.', '검색 결과가 없습니다.')}</div></div>` : `<div class="notice-table empty-notice-table"><div class="notice-table-header"><span>${t('No.', '번호')}</span><span>${t('Title', '제목')}</span><span>${t('Date', '공고일')}</span></div><div class="notice-empty"><span class="empty-icon" aria-hidden="true">${sparkle}</span><h2>${t('Nothing to announce just yet.', '등록된 공고가 없습니다.')}</h2><p>${t('Official company notices will be published here.', '회사의 공식 공고는 이 페이지에 게시됩니다.')}</p></div></div>`}
    <div class="notice-information"><span class="quiet-dot" aria-hidden="true"></span><p>${t('This page is the official notice archive for KIMCHISTAN STUDIO. Notice documents are published in Korean.', '이 페이지는 킴치스탄 스튜디오의 공식 공고 게시판입니다. 공고 내용은 한국어로 제공됩니다.')}</p></div></div></section>` });

  for (const notice of notices) {
    const attachments = (notice.attachments || []).map((attachment) => `<a class="attachment-link" href="../${e(attachment.path)}" download>${e(attachment.label)}<span aria-hidden="true">↓</span></a>`).join('');
    await page({ file: `notices/${notice.slug}.html`, prefix: '../', lang: 'ko', active: 'notices', title: `${notice.title} | ${site.name}`, description: { en: `${notice.title} — ${site.name} official notice, ${notice.date}.`, ko: `${notice.title} — ${site.legalName || site.name}, ${notice.date} 공고.` }, content: `<section class="notice-detail section"><div class="container narrow"><a class="breadcrumb" href="./">${t('All notices', '전자공고 목록')}<span aria-hidden="true">/</span><span lang="ko">공고문</span></a><article class="notice-document" lang="ko"><p class="eyebrow">${e(site.legalName || site.name)} / 전자공고</p><h1>${e(notice.title)}</h1><div class="notice-metadata"><span>공고일 <time datetime="${notice.date}">${notice.date.replaceAll('-', '.')}</time></span>${notice.reference ? `<span>공고번호 ${e(notice.reference)}</span>` : ''}</div><div class="notice-body">${notice.paragraphs.map((paragraph) => `<p>${e(paragraph).replaceAll('\n', '<br>')}</p>`).join('')}</div>${notice.signatory ? `<p class="notice-signatory">${e(notice.signatory).replaceAll('\n', '<br>')}</p>` : ''}${attachments ? `<div class="notice-attachments"><h2>첨부파일</h2>${attachments}</div>` : ''}</article><div class="notice-detail-actions"><a class="button button-outline" href="./">${t('Back to notices', '목록으로')}<span aria-hidden="true">←</span></a><button class="text-link" type="button" data-print>${t('Print notice', '공고문 인쇄')}<span aria-hidden="true">↗</span></button></div></div></section>` });
  }

  // The relative asset base makes the custom 404 work at any missing URL on
  // both GitHub project pages and a custom domain, without a guessed hostname.
  await page({ file: '404.html', title: `Page not found | ${site.name}`, robots: 'noindex', content: `<section class="not-found section"><div class="container"><p class="eyebrow">404 / ${t('A wrong turn', '길을 잃었나요?')}</p><h1>${t('Uncharted<br>territory.', '아직 발견하지<br>못한 세계.')}</h1><p>${t('This page doesn’t exist. Let’s get you back to familiar ground.', '이 페이지를 찾을 수 없습니다. 홈으로 돌아가 다시 살펴보세요.')}</p><a class="button button-primary" href="index.html">${t('Back to the studio', '홈으로 돌아가기')}${arrow}</a></div></section>` });
  const notFoundFile = resolve(output, '404.html');
  const notFoundHtml = await readFile(notFoundFile, 'utf8');
  const baseScript = `<script>const base = ${JSON.stringify('')}; const parts = location.pathname.split('/').filter(Boolean); const repo = parts[0]; const path = base || (location.hostname.endsWith('.github.io') && repo && !repo.endsWith('.github.io') ? '/' + repo + '/' : '/'); document.write('<base href="' + path.replace(/[&<>"']/g, '') + '">');</script>`;
  await writeFile(notFoundFile, notFoundHtml.replace('<meta name="viewport"', `${baseScript}<meta name="viewport"`));
  if (origin) {
    await writeFile(resolve(output, 'CNAME'), `${site.domain}\n`);
    const pages = ['', 'notices/', ...notices.map((notice) => `notices/${notice.slug}.html`)];
    await writeFile(resolve(output, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${pages.map((path) => `<url><loc>${origin}/${path}</loc></url>`).join('')}</urlset>`);
    await writeFile(resolve(output, 'robots.txt'), `User-agent: *\nAllow: /\nSitemap: ${origin}/sitemap.xml\n`);
  } else {
    await writeFile(resolve(output, 'robots.txt'), 'User-agent: *\nAllow: /\n');
  }
  if (!quiet) console.log(`Built ${games.length} game(s), ${notices.length} notice(s), and the studio pages in ${outputDirectory}/.`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  await build();
}
