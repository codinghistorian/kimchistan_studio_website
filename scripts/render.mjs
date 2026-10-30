export const e = (value = '') => String(value).replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
export const t = (en, ko) => `<span class="locale" lang="en">${en}</span><span class="locale" lang="ko">${ko}</span>`;
export const arrow = '<svg class="arrow-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14" stroke="currentColor" stroke-width="1.6"/></svg>';
export const brandMark = '<svg class="brand-mark" viewBox="0 0 40 40" aria-hidden="true"><path d="M20 0 24.8 15.2 40 20 24.8 24.8 20 40 15.2 24.8 0 20 15.2 15.2Z" fill="currentColor"/><circle cx="20" cy="20" r="3.5" fill="var(--mark-center, var(--cream))"/></svg>';
export const sparkle = brandMark;
export const external = (url) => `href="${e(url)}" target="_blank" rel="noopener noreferrer"`;
export const label = (en, ko, lang = 'en') => `aria-label="${e(lang === 'ko' ? ko : en)}" data-label-en="${e(en)}" data-label-ko="${e(ko)}"`;
export const alt = (en, ko) => `alt="${e(en)}" data-alt-en="${e(en)}" data-alt-ko="${e(ko)}"`;
export const localized = (value) => t(e(value.en), e(value.ko));

export function inquiryHref(email, lang) {
  const subject = lang === 'ko' ? '프로젝트 문의 — KIMCHISTAN STUDIO' : 'Project inquiry — KIMCHISTAN STUDIO';
  const body = lang === 'ko'
    ? '이름 / 회사:\n\n만들고 싶은 것 / 해결할 문제:\n\n현재 사용하는 도구:\n\n희망 일정:\n\n예산 범위 (선택):\n'
    : 'Name / company:\n\nWhat we want to build / the problem to solve:\n\nCurrent tools:\n\nTimeline:\n\nBudget range (optional):\n';
  return `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

export function inquiryLink(site, className = 'button button-primary', en = 'Start a project', ko = '프로젝트 문의') {
  return `<a class="${className}" href="${e(inquiryHref(site.email, 'en'))}" data-href-en="${e(inquiryHref(site.email, 'en'))}" data-href-ko="${e(inquiryHref(site.email, 'ko'))}">${t(en, ko)}${arrow}</a>`;
}

export function header(prefix, active = '', lang = 'en') {
  const navLink = (href, en, ko, key) => `<a href="${prefix}${href}" ${active === key ? 'aria-current="page"' : ''}>${t(en, ko)}</a>`;
  return `<a class="skip-link" href="#main">${t('Skip to content', '본문 바로가기')}</a>
    <header class="site-header"><div class="container header-inner">
      <a class="brand" href="${prefix}index.html" ${label('KIMCHISTAN STUDIO home', '김치스탄 스튜디오 홈', lang)}>${brandMark}<span>KIMCHISTAN<span class="brand-subtitle">STUDIO</span></span></a>
      <nav class="site-navigation" id="site-navigation" ${label('Main navigation', '주 메뉴', lang)}>
        ${navLink('games/', 'Games', '게임', 'games')}
        ${navLink('services/', 'Software & AI', '소프트웨어 & AI', 'services')}
        ${navLink('index.html#studio', 'Studio', '스튜디오', 'studio')}
        ${navLink('notices/', 'Notices <span class="nav-korean" lang="ko">전자공고</span>', '전자공고', 'notices')}
        <a class="mobile-contact" href="${prefix}index.html#contact">${t('Start a project', '프로젝트 문의')}${arrow}</a>
      </nav>
      <div class="header-actions">
        <div class="language-switch" aria-label="Language / 언어"><button type="button" data-language="en" aria-pressed="${lang === 'en'}">EN</button><span aria-hidden="true">/</span><button type="button" data-language="ko" aria-pressed="${lang === 'ko'}" lang="ko">KO</button></div>
        <a class="header-contact" href="${prefix}index.html#contact">${t('Start a project', '프로젝트 문의')}${arrow}</a>
        <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-navigation" ${label('Open navigation', '메뉴 열기', lang)}><span></span><span></span></button>
      </div>
    </div></header>`;
}

export function footer(site, prefix) {
  return `<footer class="site-footer"><div class="container">
    <div class="footer-top"><a class="brand" href="${prefix}index.html">${brandMark}<span>KIMCHISTAN<span class="brand-subtitle">STUDIO</span></span></a><p>${t('Independent spirit.<br>Made in South Korea.', '독립적인 시선으로.<br>대한민국에서 만듭니다.')}</p></div>
    <div class="footer-details"><div class="company-legal">
      <p class="legal-name">${e(site.legalName)}</p><p lang="ko">${e(site.legalNameKo)}</p>
      <address><span lang="en">${e(site.address.en)}</span><span lang="ko">${e(site.address.ko)}</span></address>
      ${site.representative ? `<p>대표자 ${e(site.representative)}</p>` : ''}
      ${site.registrationNumber ? `<p>사업자등록번호 ${e(site.registrationNumber)}</p>` : ''}
      <a href="mailto:${e(site.email)}">${e(site.email)}</a>
    </div><div class="footer-navigation">
      <a href="${prefix}games/">${t('Games', '게임')}${arrow}</a>
      <a href="${prefix}services/">${t('Software & AI', '소프트웨어 & AI')}${arrow}</a>
      <a href="${prefix}notices/">${t('Official notices · 전자공고', '전자공고')}${arrow}</a>
    </div><div class="footer-socials">${[['itch.io', site.links.itch], ['Discord', site.links.discord], ['YouTube', site.links.youtube], ['X / Twitter', site.links.twitter]].map(([name, url]) => `<a ${external(url)}>${name}${arrow}</a>`).join('')}</div></div>
    <div class="footer-wordmark" aria-hidden="true">KIMCHISTAN<span>✳</span></div>
    <div class="footer-bottom"><span>© ${new Date().getFullYear()} ${e(site.legalName)}</span><span>${t('Games. Software. A little curiosity.', '게임. 소프트웨어. 그리고 호기심.')}</span><a href="${prefix}index.html#main">${t('Back to top', '맨 위로')} ↑</a></div>
  </div></footer>`;
}

export function projectCard(game, prefix, { featured = false } = {}) {
  const link = game.detailPath ? `href="${prefix}${e(game.detailPath)}"` : external(game.url);
  return `<article class="project-card ${featured ? 'project-featured' : ''}" ${featured ? 'id="orbit-foundry"' : ''}>
    <a class="project-link" ${link}>
      <div class="project-image"><img src="${prefix}${e(game.image)}" alt="" width="${featured ? 1920 : 800}" height="${featured ? 1080 : 500}" loading="lazy"><span class="project-open">${arrow}</span>${featured ? `<span class="project-badge">${t('In development', '개발 중')}</span>` : ''}</div>
      <div class="project-caption"><div><p class="project-category">${localized(game.status)}</p><h3>${localized(game.title)}</h3></div><span class="project-action">${game.detailPath ? t('Discover the game', '게임 자세히 보기') : t('Play on itch.io', 'itch.io에서 플레이')}${arrow}</span></div>
    </a><p class="project-summary">${localized(game.summary)}</p>
  </article>`;
}

export function resourceLink(game, prefix) {
  return `<a class="resource-link" ${external(game.url)}><img src="${prefix}${e(game.image)}" alt="" width="126" height="100" loading="lazy"><div><p class="eyebrow">${localized(game.status)}</p><h3>${localized(game.title)}</h3><p>${localized(game.summary)}</p></div><span class="resource-arrow">${arrow}</span></a>`;
}

export function community(site) {
  return `<div class="community-links">${[
    ['Discord', 'Share builds, ideas & feedback', '빌드와 아이디어, 피드백을 나눠요', site.links.discord],
    ['YouTube', 'A closer look at our games', '우리 게임을 더 가까이에서', site.links.youtube],
    ['X / Twitter', 'Follow the next chapter', '다음 이야기를 만나보세요', site.links.twitter]
  ].map(([name, en, ko, url]) => `<a ${external(url)}><span><strong>${name}</strong><small>${t(en, ko)}</small></span>${arrow}</a>`).join('')}</div>`;
}

export function contact(site, { compact = false } = {}) {
  return `<section class="contact-section section ${compact ? 'contact-compact' : ''}" id="contact"><div class="container">
    <p class="eyebrow"><span class="accent-dot"></span>${t('Have something in mind?', '생각하고 있는 프로젝트가 있나요?')}</p>
    <div class="contact-grid"><div><h2>${t('Let’s make<br>it <em>happen.</em>', '함께<br><em>만들어 봐요.</em>')}</h2><p class="contact-intro">${t('A useful tool. A new workflow. An idea you’re ready to explore. Tell us where you’d like to start.', '필요한 도구부터 새로운 업무 방식, 구체화하고 싶은 아이디어까지. 어디에서 시작하고 싶은지 들려주세요.')}</p></div>
    <div class="contact-action"><p class="mini-label">${t('Your next step', '이렇게 시작해요')}</p><h3>${t('Tell us what you’re building.', '만들고 싶은 것을 알려주세요.')}</h3><p>${t('Share your goal, current tools, and timing. Our email template gives you a starting point.', '목표와 현재 사용하는 도구, 희망 일정을 알려주세요. 이메일 양식에 간단히 적어 주시면 됩니다.')}</p>${inquiryLink(site)}
      <div class="email-row"><a href="mailto:${e(site.email)}">${e(site.email)}</a><button type="button" class="copy-email" data-copy-email="${e(site.email)}" hidden>${t('Copy', '복사')}</button></div><p class="copy-status" data-copy-status role="status" aria-live="polite"></p>
    </div></div>
    ${compact ? '' : `<div class="contact-community"><span>${t('Here for the games?', '게임 이야기를 나누고 싶다면?')}</span><a ${external(site.links.discord)}>Discord ${arrow}</a><a ${external(site.links.youtube)}>YouTube ${arrow}</a><a ${external(site.links.twitter)}>X / Twitter ${arrow}</a></div>`}
  </div></section>`;
}
