import { readFile, writeFile, mkdir, readdir, cp, rm, stat } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const root = resolve(import.meta.dirname, '..');
const e = (value = '') => String(value).replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
const tLabel = (en, ko) => e(`${en} / ${ko}`);
const t = (en, ko, className = '') => `<span class="locale ${className}" lang="en">${en}</span><span class="locale ${className}" lang="ko">${ko}</span>`;
const arrow = '<svg class="arrow-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14" stroke="currentColor" stroke-width="1.7"/></svg>';
const brandMark = '<svg class="brand-mark" viewBox="0 0 40 40" fill="none" aria-hidden="true"><path d="M20 0 24.8 15.2 40 20 24.8 24.8 20 40 15.2 24.8 0 20 15.2 15.2Z" fill="currentColor"/><circle cx="20" cy="20" r="4" fill="var(--cream)"/></svg>';
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
  for (const [key, value] of Object.entries(site.links || {})) publicUrl(value, `site.links.${key}`);
  for (const game of games) {
    requireText(game.image, 'game.image');
    requireText(game.url, 'game.url');
    publicUrl(game.url, 'game.url');
    await stat(resolve(root, localAsset(game.image, 'game image')));
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

  const external = (url) => `href="${e(url)}" target="_blank" rel="noopener noreferrer"`;
  const socialLinks = () => [['Discord', site.links.discord], ['YouTube', site.links.youtube], ['X / Twitter', site.links.twitter], ['itch.io', site.links.itch]].map(([label, url]) => `<a ${external(url)}>${label}${arrow}</a>`).join('');
  const wordmark = `${brandMark}<span>KIMCHISTAN<span class="brand-subtitle">STUDIO</span></span>`;
  function header(prefix, active = '') {
    return `<a class="skip-link" href="#main">${t('Skip to content', '본문 바로가기')}</a>
      <header class="site-header"><div class="container header-inner">
        <a class="brand" href="${prefix}index.html" aria-label="${e(site.name)} home">${wordmark}</a>
        <nav class="site-navigation" id="site-navigation" aria-label="Main navigation">
          <a href="${prefix}index.html#orbit-foundry">Orbit Foundry</a>
          <a href="${prefix}index.html#games">${t('Our games', '게임')}</a>
          <a href="${prefix}index.html#studio">${t('The studio', '스튜디오')}</a>
          <a href="${prefix}notices/" ${active === 'notices' ? 'aria-current="page"' : ''}>${t('Notices <span class="nav-korean">공고</span>', '전자공고')}</a>
          <a class="mobile-contact" href="${prefix}index.html#contact">${t('Get in touch', '문의하기')}${arrow}</a>
        </nav>
        <div class="header-actions"><div class="language-switch" aria-label="Language / 언어"><button type="button" data-language="en" aria-pressed="true">EN</button><span aria-hidden="true">/</span><button type="button" data-language="ko" aria-pressed="false" lang="ko">KO</button></div><a class="header-contact" ${external(site.links.steam)}>${t('Wishlist on Steam', 'Steam 위시리스트')}${arrow}</a><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-navigation" aria-label="Open navigation" data-label-en="Open navigation" data-label-ko="메뉴 열기"><span></span><span></span></button></div>
      </div></header>`;
  }
  function footer(prefix) {
    return `<footer class="site-footer"><div class="container"><div class="footer-top"><a class="brand footer-brand" href="${prefix}index.html">${wordmark}</a><a class="footer-notices" href="${prefix}notices/">${t('Official notices · 전자공고', '전자공고')}${arrow}</a></div><div class="footer-details"><div class="company-legal"><p class="legal-name">${e(site.legalName)}</p><p lang="ko">${e(site.legalNameKo || '')}</p><address><span lang="en">${e(site.address.en)}</span><span lang="ko">${e(site.address.ko)}</span></address>${site.representative ? `<p>대표자 ${e(site.representative)}</p>` : ''}${site.registrationNumber ? `<p>사업자등록번호 ${e(site.registrationNumber)}</p>` : ''}<a href="mailto:${e(site.email)}">${e(site.email)}</a></div><div class="footer-socials">${socialLinks()}</div></div><div class="footer-wordmark" aria-hidden="true">KIMCHISTAN<span>✳</span></div><div class="footer-bottom"><span>© ${new Date().getFullYear()} ${e(site.legalName)} All rights reserved.</span><span>${t('Independent games. Made in South Korea.', '대한민국에서 만드는 인디 게임.')}${brandMark}</span></div></div></footer>`;
  }
  async function page({ file, title, content, prefix = '', lang = 'en', active = '', description = site.description, robots = '' }) {
    const canonical = origin ? `${origin}/${file === 'index.html' ? '' : file === 'notices/index.html' ? 'notices/' : file}` : '';
    const html = `<!doctype html>
<html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f4f1e8"><title>${e(title)}</title><meta name="description" content="${e(description[lang])}" data-en="${e(description.en)}" data-ko="${e(description.ko)}">${robots ? `<meta name="robots" content="${robots}">` : ''}${canonical ? `<link rel="canonical" href="${e(canonical)}"><meta property="og:url" content="${e(canonical)}">` : ''}<meta property="og:type" content="website"><meta property="og:title" content="${e(title)}"><meta property="og:description" content="${e(description[lang])}"><meta property="og:site_name" content="${e(site.name)}"><meta property="og:image" content="${origin}/assets/games/orbit-foundry-social.jpg"><meta property="og:image:alt" content="Orbit Foundry — coming soon from KIMCHISTAN STUDIO"><meta name="twitter:card" content="summary_large_image"><link rel="icon" type="image/svg+xml" href="${prefix}assets/favicon.svg"><link rel="preload" href="${prefix}assets/space-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="${prefix}assets/styles.css"><noscript><style>@media(max-width:800px){.header-inner{height:auto;flex-wrap:wrap;padding-block:20px}.site-navigation{display:flex;position:static;order:3;width:100%;flex-wrap:wrap;gap:20px;padding:0;border:0;box-shadow:none}.site-navigation a{padding:5px 0}.menu-toggle,.language-switch{display:none!important}}</style></noscript><script src="${prefix}assets/app.js" defer></script></head><body>${header(prefix, active)}<main id="main">${content}</main>${footer(prefix)}</body></html>`;
    await writeFile(resolve(output, file), html);
  }

  const gameCards = games.filter((game) => game.type !== 'asset').map((game, i) => {
    const title = localized(game.title, `games[${i}].title`);
    const summary = localized(game.summary, `games[${i}].summary`);
    const status = localized(game.status, `games[${i}].status`);
    const url = game.url ? publicUrl(game.url, 'game.url') : '';
    return `<article class="game-card"><a class="game-image-link" ${external(url)} tabindex="-1" aria-hidden="true"><img src="${e(localAsset(game.image, 'game image'))}" alt="" width="800" height="500" loading="lazy"><span class="game-image-arrow">${arrow}</span></a><div class="game-card-copy"><p class="status-label">${status}</p><h3><a ${external(url)}>${title}${arrow}</a></h3><p class="game-summary">${summary}</p><span class="game-platform">${t('Play in your browser', '브라우저에서 플레이')}<span aria-hidden="true">↗</span></span></div></article>`;
  }).join('');
  const assetCards = games.filter((game) => game.type === 'asset').map((game) => `<a class="resource-band" ${external(publicUrl(game.url, 'game.url'))}><img src="${e(localAsset(game.image, 'game image'))}" alt="" width="126" height="100" loading="lazy"><div><p class="eyebrow">${localized(game.status, 'asset.status')}</p><h3>${localized(game.title, 'asset.title')}</h3><p>${localized(game.summary, 'asset.summary')}</p></div>${arrow}</a>`).join('');
  const noticesPreview = notices.length ? `<div class="home-notice-list">${notices.slice(0, 3).map((notice) => `<a href="notices/${e(notice.slug)}.html"><time datetime="${notice.date}">${notice.date.replaceAll('-', '.')}</time><span lang="ko">${e(notice.title)}</span>${arrow}</a>`).join('')}</div>` : `<div class="notice-summary"><span class="quiet-dot" aria-hidden="true"></span>${t('There are currently no published notices.', '현재 등록된 공고가 없습니다.')}</div>`;
  await page({ file: 'index.html', title: `${site.name} — Orbit Foundry, coming soon.`, content: `
    <section class="hero"><div class="container"><div class="hero-kicker"><p class="eyebrow"><span class="live-dot" aria-hidden="true"></span>${t('Independent game studio · South Korea', '대한민국의 인디 게임 스튜디오')}</p><span class="hero-edition">${t('Curiosity, made playable.', '호기심을 플레이로.')}</span></div><div class="hero-grid"><div class="hero-copy"><h1>${t('Our next<br>adventure<br>is in <em>orbit.</em>', '우리의 다음<br>모험은<br><em>궤도 위에서.</em>')}</h1><p class="hero-description">${t('We’re KIMCHISTAN STUDIO. We make curious little worlds you can get lost in. Our next one starts with a star.', '우리는 김치스탄 스튜디오입니다. 호기심을 자극하고 빠져들게 하는 작은 세계를 만듭니다. 다음 세계는 하나의 별에서 시작됩니다.')}</p><a class="button button-primary" ${external(site.links.steam)}>${t('Wishlist Orbit Foundry', 'Orbit Foundry 위시리스트')}${arrow}</a><a class="hero-secondary" ${external(site.links.prototype)}>${t('Or try the free browser prototype', '무료 브라우저 프로토타입 플레이')}<span aria-hidden="true">↗</span></a></div><a class="hero-art" ${external(site.links.steam)} aria-label="Orbit Foundry — ${tLabel('coming soon to Steam', 'Steam 출시 예정')}"><img src="assets/games/orbit-foundry-orbit.webp" alt="A glowing magenta star surrounded by orbital factory machines in Orbit Foundry" width="2400" height="775" fetchpriority="high"><div class="hero-art-top"><span class="art-label">${t('Our next release', '차기 출시작')}</span><span class="release-badge"><span class="quiet-dot" aria-hidden="true"></span>${t('Coming soon', '출시 예정')}</span></div><div class="hero-art-bottom"><div><p class="art-genre">${t('A cosmic factory incremental', '우주 공장 인크리멘털 게임')}</p><h2>ORBIT<br><span>FOUNDRY</span></h2></div><span class="art-arrow">${arrow}</span></div></a></div><div class="hero-foot"><span>${t('Small studio. A universe of possibilities.', '작은 스튜디오, 무한한 가능성.')}</span><a href="#orbit-foundry">${t('Explore our worlds', '우리의 세계 둘러보기')}<span aria-hidden="true">↓</span></a></div></div></section>
    <section class="launch-section section" id="orbit-foundry"><div class="container"><div class="section-heading"><p class="eyebrow"><span class="section-number">01 /</span>${t('On the horizon', '다가오는 게임')}</p><span class="section-aside">Orbit Foundry</span></div><div class="launch-grid"><div class="launch-copy"><span class="mini-label">${t('Build. Connect. Reforge.', '건설. 연결. 리포지.')}</span><h2>${t('Start small.<br>Think astronomical.', '작게 시작해<br>우주로 확장하세요.')}</h2><p>${t('Turn a single star into the heart of an orbital factory. Arrange your machines, find the perfect production rhythm, and build something bigger with every Reforge.', '하나의 별을 궤도 공장의 중심으로 만드세요. 기계를 배치하고, 완벽한 생산 리듬을 찾고, 리포지할 때마다 더 큰 가능성을 열어 가세요.')}</p><ul class="feature-list"><li><span>01</span>${t('Build your orbital production line', '나만의 궤도 생산 라인 설계')}</li><li><span>02</span>${t('Time your pulses. Grow your output.', '펄스 타이밍을 맞추고 생산량 확장')}</li><li><span>03</span>${t('Reforge for lasting progress', '리포지로 영구적인 성장')}</li></ul><div class="launch-meta"><span>Windows + macOS</span><span>EN / 한국어</span></div><a class="text-link" ${external(site.links.steam)}>${t('Find it on Steam', 'Steam에서 자세히 보기')}${arrow}</a></div><div class="gameplay-gallery"><div class="gameplay-frame"><img id="gameplay-image" src="assets/games/orbit-foundry-screen-1.webp" alt="Orbit Foundry gameplay: orbital machinery around a star in the Prism Belt" width="1920" height="1080" loading="lazy"></div><div class="gallery-bottom"><p class="gallery-caption">${t('A glimpse inside Orbit Foundry', 'Orbit Foundry 미리 보기')}</p><div class="gallery-controls" role="group" aria-label="Gameplay screenshots / 게임 스크린샷">${[1,2,3].map((n) => `<button type="button" data-screenshot="assets/games/orbit-foundry-screen-${n}.webp" data-alt="${['Orbit Foundry gameplay: orbital machinery around a star in the Prism Belt', 'Orbit Foundry gameplay: factory progression and orbital production', 'Orbit Foundry gameplay: building an interconnected cosmic factory'][n-1]}" aria-label="${tLabel('Screenshot', '스크린샷')} ${n}" aria-pressed="${n===1}">0${n}</button>`).join('')}</div></div><a class="prototype-note" ${external(site.links.prototype)}><span class="prototype-icon" aria-hidden="true">↗</span><span><strong>${t('Can’t wait to get into orbit?', '지금 궤도에 진입하고 싶다면?')}</strong><span>${t('Try the free 2D desktop browser prototype on itch.io.', 'itch.io에서 무료 2D PC 브라우저 프로토타입을 플레이해 보세요.')}</span></span>${arrow}</a></div></div></div></section>
    <section class="games-section section" id="games"><div class="container"><div class="section-heading"><p class="eyebrow"><span class="section-number">02 /</span>${t('From our little universe', '우리의 작은 우주에서')}</p><a class="text-link" ${external(site.links.itch)}>${t('All projects on itch.io', 'itch.io에서 전체 프로젝트 보기')}${arrow}</a></div><div class="games-heading"><h2>${t('Different worlds.<br>Same curious spirit.', '서로 다른 세계,<br>같은 호기심.')}</h2><p>${t('Cozy corners, chaotic arenas, and a few goblins along the way. Meet the projects that brought us here.', '아늑한 공간부터 시끌벅적한 아레나, 그리고 고블린까지. 우리의 발자취를 담은 프로젝트를 만나보세요.')}</p></div><div class="game-grid">${gameCards}</div>${assetCards}</div></section>
    <section class="studio-section section" id="studio"><div class="container"><div class="section-heading"><p class="eyebrow"><span class="section-number">03 /</span>${t('Meet the makers', '우리를 소개합니다')}</p>${brandMark}</div><div class="studio-grid"><div><h2>${t('Built on curiosity.<br>Made in<br><em>South Korea.</em>', '호기심에서 시작해,<br><em>대한민국에서</em><br>만듭니다.')}</h2></div><div class="studio-story"><p class="studio-intro">${t('We’re an independent game studio based in Goyang, South Korea. We follow the ideas that make us curious — whether that’s a familiar room, a wonderfully messy machine, or a factory wrapped around a star.', '김치스탄 스튜디오는 경기도 고양시에 자리한 인디 게임 스튜디오입니다. 익숙한 방 한 칸, 엉뚱하고 복잡한 기계, 별 주위를 감싼 공장까지. 우리의 호기심이 향하는 곳에서 게임이 시작됩니다.')}</p><p>${t('Different games, one ambition: make something you’ll want to spend a little more time with.', '만드는 게임은 달라도 바람은 하나입니다. 조금 더 머물고 싶은 세계를 만드는 것.')}</p><dl class="company-details"><div><dt>${t('Company', '법인명')}</dt><dd>${e(site.legalName)}<span lang="ko">${e(site.legalNameKo)}</span></dd></div><div><dt>${t('Based in', '소재지')}</dt><dd>${t('Goyang, South Korea', '대한민국 경기도 고양시')}</dd></div><div><dt>${t('Our focus', '하는 일')}</dt><dd>${t('Independent game development', '인디 게임 개발')}</dd></div></dl></div></div></div></section>
    <section class="contact-section section" id="contact"><div class="container"><div class="section-heading"><p class="eyebrow"><span class="section-number">04 /</span>${t('Keep in the loop', '함께해요')}</p></div><div class="contact-grid"><div><h2>${t('Good things<br>start with <em>hello.</em>', '새로운 이야기는<br><em>인사에서 시작됩니다.</em>')}</h2><p>${t('Follow the next launch, share a thought, or talk about making something together.', '다음 출시 소식을 만나고, 의견을 나누고, 함께 만들어 갈 이야기를 들려주세요.')}</p><a class="contact-email" href="mailto:${e(site.email)}">${e(site.email)}${arrow}</a></div><div class="community-links"><a ${external(site.links.discord)}><span class="community-number">01</span><span><strong>${t('Join the Discord', 'Discord 참여하기')}</strong><small>${t('Share builds, ideas & feedback', '빌드, 아이디어, 피드백을 나눠요')}</small></span>${arrow}</a><a ${external(site.links.youtube)}><span class="community-number">02</span><span><strong>${t('Watch on YouTube', 'YouTube 시청하기')}</strong><small>${t('A closer look at our games', '우리의 게임을 더 가까이에서')}</small></span>${arrow}</a><a ${external(site.links.twitter)}><span class="community-number">03</span><span><strong>${t('Follow on X', 'X에서 팔로우하기')}</strong><small>@kimchistangames</small></span>${arrow}</a></div></div></div></section>
    <section class="notices-section section" id="notices"><div class="container notice-home-grid"><div><p class="eyebrow">${t('Company information', '회사 안내')}</p><h2>${t('Official notices <span lang="ko">전자공고</span>', '전자공고')}</h2><p>${t('Official corporate announcements from KIMCHISTANSTUDIO Inc.', '주식회사 김치스탄스튜디오의 공식 공고를 안내합니다.')}</p></div><div class="notice-home-right">${noticesPreview}<a class="text-link" href="notices/">${t('View notice archive', '전자공고 바로가기')}${arrow}</a></div></div></section>
  ` });

  const noticeDescription = { en: `Official corporate notices from ${site.name}.`, ko: `${site.legalName || site.name}의 공식 전자공고 게시판입니다.` };
  const years = [...new Set(notices.map((notice) => notice.date.slice(0, 4)))];
  await page({ file: 'notices/index.html', prefix: '../', lang: 'ko', active: 'notices', title: `전자공고 | ${site.name}`, description: noticeDescription, content: `
    <section class="notice-page section"><div class="container"><a class="breadcrumb" href="../index.html">${t('Home', '홈')}<span aria-hidden="true">/</span>${t('Official notices', '전자공고')}</a><div class="notice-page-heading"><div><p class="eyebrow">KIMCHISTAN STUDIO / ${t('Official announcements', '공식 공고')}</p><h1>${t('Studio notices.', '전자공고.')}</h1><p>${t('Official announcements from KIMCHISTAN STUDIO.', '김치스탄 스튜디오의 공식 공고를 안내합니다.')}</p></div><span class="notice-heading-icon" aria-hidden="true"><svg viewBox="0 0 64 64" fill="none"><path d="M18 9h21l11 11v35H18z" stroke="currentColor" stroke-width="2"/><path d="M39 9v12h11M26 30h16M26 38h16M26 46h10" stroke="currentColor" stroke-width="2"/></svg></span></div>
    ${notices.length ? `<div class="notice-tools"><label class="search-label">${t('Search notices', '공고 검색')}<input type="search" data-notice-search data-label-en="Search notices" data-label-ko="공고 검색" aria-label="공고 검색"></label><label class="year-label">${t('Year', '연도')}<select data-notice-year><option value="">${e('전체 / All years')}</option>${years.map((year) => `<option value="${year}">${year}</option>`).join('')}</select></label></div><p class="notice-count">${t('Notices', '전체 공고')} <span data-result-count>${notices.length}</span></p><div class="notice-table"><table><caption class="sr-only">${t('Corporate notices', '회사 전자공고 목록')}</caption><thead><tr><th scope="col">${t('No.', '번호')}</th><th scope="col">${t('Title', '제목')}</th><th scope="col">${t('Date', '공고일')}</th></tr></thead><tbody>${notices.map((notice, i) => `<tr data-notice-row data-search="${e((notice.title + ' ' + notice.date).normalize('NFKC').toLocaleLowerCase())}" data-year="${notice.date.slice(0, 4)}"><td>${String(notices.length - i).padStart(2, '0')}</td><td><a href="${e(notice.slug)}.html" lang="ko">${e(notice.title)}${arrow}</a></td><td><time datetime="${notice.date}">${notice.date.replaceAll('-', '.')}</time></td></tr>`).join('')}</tbody></table><div class="no-search-results" data-no-results hidden>${t('No notices match your search.', '검색 결과가 없습니다.')}</div></div>` : `<div class="notice-table empty-notice-table"><div class="notice-table-header"><span>${t('No.', '번호')}</span><span>${t('Title', '제목')}</span><span>${t('Date', '공고일')}</span></div><div class="notice-empty"><span class="empty-icon" aria-hidden="true">${sparkle}</span><h2>${t('Nothing to announce just yet.', '등록된 공고가 없습니다.')}</h2><p>${t('Official company notices will be published here.', '회사의 공식 공고는 이 페이지에 게시됩니다.')}</p></div></div>`}
    <div class="notice-information"><span class="quiet-dot" aria-hidden="true"></span><p>${t('This page is the official notice archive for KIMCHISTAN STUDIO. Notice documents are published in Korean.', '이 페이지는 김치스탄 스튜디오의 공식 공고 게시판입니다. 공고 내용은 한국어로 제공됩니다.')}</p></div></div></section>` });

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
