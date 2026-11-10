export const e = (value = '') => String(value).replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
export const t = (en, ko) => `<span class="locale" lang="en">${en}</span><span class="locale" lang="ko">${ko}</span>`;
export const arrow = '<svg class="arrow-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 18 18 6M8.5 6H18v9.5" stroke="currentColor" stroke-width="2.4" stroke-linecap="square"/></svg>';
export const brandMark = '<svg class="brand-mark" viewBox="0 0 40 40" aria-hidden="true"><path d="M20 0 24.8 15.2 40 20 24.8 24.8 20 40 15.2 24.8 0 20 15.2 15.2Z" fill="currentColor"/><circle cx="20" cy="20" r="3.5" fill="var(--mark-center, var(--paper))"/></svg>';
export const sparkle = brandMark;
export const external = (url) => `href="${e(url)}" target="_blank" rel="noopener noreferrer"`;
export const label = (en, ko, lang = 'en') => `aria-label="${e(lang === 'ko' ? ko : en)}" data-label-en="${e(en)}" data-label-ko="${e(ko)}"`;
export const alt = (en, ko) => `alt="${e(en)}" data-alt-en="${e(en)}" data-alt-ko="${e(ko)}"`;
export const localized = (value) => t(e(value.en), e(value.ko));
const phoneLink = (site) => `<a href="tel:+${e(site.phone.en.replace(/\s/g, ''))}">${localized(site.phone)}</a>`;

/* The five crafts, in menu order. Colors live in styles.css as --c-<key>. */
export const crafts = [
  { key: 'games', en: 'Games', ko: '게임', word: ['GAMES', '게임'] },
  { key: 'software', en: 'Software', ko: '소프트웨어', word: ['SOFTWARE', '소프트웨어'] },
  { key: 'agents', en: 'AI Agents', ko: 'AI 에이전트', word: ['AI AGENTS', 'AI 에이전트'] },
  { key: 'videos', en: 'Videos', ko: '영상', word: ['VIDEOS', '영상'] },
  { key: 'lettuce', en: 'Lettuce', ko: '상추', word: ['LETTUCE', '상추'] }
];

/* ---------- Inquiry templates ---------- */
const inquiries = {
  project: {
    en: ['Project inquiry', 'Name / company:\n\nWhat we want to build / the problem to solve:\n\nCurrent tools:\n\nTimeline:\n\nBudget range (optional):\n'],
    ko: ['프로젝트 문의', '이름 / 회사:\n\n만들고 싶은 것 / 해결할 문제:\n\n현재 사용하는 도구:\n\n희망 일정:\n\n예산 범위 (선택):\n']
  },
  games: {
    en: ['Game project', 'Name / company:\n\nGame idea or collaboration:\n\nPlatform:\n\nTimeline:\n\nBudget range (optional):\n'],
    ko: ['게임 프로젝트 문의', '이름 / 회사:\n\n게임 아이디어 또는 협업 내용:\n\n플랫폼:\n\n희망 일정:\n\n예산 범위 (선택):\n']
  },
  software: {
    en: ['Software project', 'Name / company:\n\nWhat we want to build / the problem to solve:\n\nCurrent tools:\n\nTimeline:\n\nBudget range (optional):\n'],
    ko: ['소프트웨어 프로젝트 문의', '이름 / 회사:\n\n만들고 싶은 것 / 해결할 문제:\n\n현재 사용하는 도구:\n\n희망 일정:\n\n예산 범위 (선택):\n']
  },
  agents: {
    en: ['AI agent project', 'Name / company:\n\nThe task we want an AI agent to help with:\n\nCurrent tools and data:\n\nWho reviews the results:\n\nTimeline:\n\nBudget range (optional):\n'],
    ko: ['AI 에이전트 프로젝트 문의', '이름 / 회사:\n\nAI 에이전트가 도와줬으면 하는 업무:\n\n현재 사용하는 도구와 데이터:\n\n결과를 검토할 담당자:\n\n희망 일정:\n\n예산 범위 (선택):\n']
  },
  videos: {
    en: ['Video project', 'Name / company:\n\nWhat the video should show or explain:\n\nLength and format:\n\nReference material (models, drawings, footage):\n\nTimeline:\n\nBudget range (optional):\n'],
    ko: ['영상 제작 문의', '이름 / 회사:\n\n영상으로 보여주거나 설명할 내용:\n\n길이와 형식:\n\n참고 자료 (모델, 도면, 촬영본):\n\n희망 일정:\n\n예산 범위 (선택):\n']
  },
  lettuce: {
    en: ['Lettuce order', 'Name / business:\n\nQuantity:\n\nDelivery area:\n\nPreferred date:\n\nContact number:\n'],
    ko: ['상추 주문 문의', '이름 / 상호:\n\n수량:\n\n배송 지역:\n\n희망 날짜:\n\n연락처:\n']
  }
};

export function inquiryHref(email, lang, topic = 'project') {
  const [subject, body] = (inquiries[topic] || inquiries.project)[lang === 'ko' ? 'ko' : 'en'];
  return `mailto:${email}?subject=${encodeURIComponent(subject + ' — KIMCHISTAN STUDIO')}&body=${encodeURIComponent(body)}`;
}

export function inquiryLink(site, className = 'button button-primary', en = 'Start a project', ko = '프로젝트 문의', topic = 'project', extra = '') {
  return `<a class="${className}" href="${e(inquiryHref(site.email, 'en', topic))}" data-href-en="${e(inquiryHref(site.email, 'en', topic))}" data-href-ko="${e(inquiryHref(site.email, 'ko', topic))}" ${extra}>${t(en, ko)}${arrow}</a>`;
}

/* ---------- Illustrations (original, drawn as inline SVG) ---------- */
const ink = '#100f0d';
const S = (w = 4) => `stroke="${ink}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;

function ruffle(cx, cy, rx, ry, waves, amp, phase = 0, points = 144) {
  let d = '';
  for (let i = 0; i < points; i += 1) {
    const a = (i / points) * Math.PI * 2;
    const k = 1 + amp * Math.sin(waves * a + phase) + amp * 0.35 * Math.sin(waves * 2.6 * a + phase * 1.7);
    d += `${i ? 'L' : 'M'}${(cx + Math.cos(a) * rx * k).toFixed(1)} ${(cy + Math.sin(a) * ry * k).toFixed(1)}`;
  }
  return d + 'Z';
}

export function lettuceArt(className = 'lettuce-art') {
  return `<svg class="${className}" viewBox="0 0 220 210" aria-hidden="true" focusable="false">
    <g class="leaf leaf-back"><path d="${ruffle(110, 116, 98, 84, 11, 0.07, 0.4)}" fill="#1f9d55" ${S()}/></g>
    <g class="leaf leaf-left"><path d="${ruffle(72, 120, 60, 66, 9, 0.085, 1.1)}" fill="#3dbb5c" ${S()}/><path d="M76 176C70 150 62 128 46 104" fill="none" ${S(3)} opacity=".55"/></g>
    <g class="leaf leaf-right"><path d="${ruffle(148, 120, 60, 66, 9, 0.085, 2.3)}" fill="#34ad52" ${S()}/><path d="M144 176C150 150 158 128 174 104" fill="none" ${S(3)} opacity=".55"/></g>
    <g class="leaf leaf-front"><path d="${ruffle(110, 134, 66, 60, 10, 0.08, 0.2)}" fill="#bdf246" ${S()}/><path d="M110 190V128M110 160 92 140M110 150l18-18" fill="none" ${S(3)} opacity=".6"/></g>
    <g class="leaf leaf-core"><path d="${ruffle(110, 140, 34, 28, 8, 0.1, 0.9)}" fill="#ecfccb" ${S()}/></g>
  </svg>`;
}

const leafShape = `<svg viewBox="0 0 60 80" aria-hidden="true" focusable="false"><path d="${ruffle(30, 40, 24, 34, 7, 0.09, 0.5, 72)}" fill="#3dbb5c" ${S(3)}/><path d="M30 74V16" fill="none" ${S(2.5)} opacity=".6"/></svg>`;
export const leafTemplate = `<template data-leaf-template>${leafShape}</template>`;

export const art = {
  games: `<svg class="sticker-art" viewBox="0 16 168 96" aria-hidden="true" focusable="false"><path d="M34 22h100a30 30 0 0 1 30 30v12a42 42 0 0 1-42 42c-15 0-22-13-38-13s-23 13-38 13A42 42 0 0 1 4 64V52a30 30 0 0 1 30-30Z" fill="#7c5cff" ${S()}/><path d="M40 44h12v12h12v12H52v12H40V68H28V56h12Z" fill="#fffaf0" ${S(3)}/><circle cx="120" cy="50" r="8.5" fill="#ffd23f" ${S(3)}/><circle cx="138" cy="66" r="8.5" fill="#ff5ca8" ${S(3)}/><circle cx="102" cy="66" r="8.5" fill="#bdf246" ${S(3)}/><circle cx="120" cy="82" r="8.5" fill="#2d5bff" ${S(3)}/></svg>`,
  software: `<svg class="sticker-art" viewBox="0 0 150 124" aria-hidden="true" focusable="false"><rect x="4" y="4" width="142" height="116" rx="18" fill="#2d5bff" ${S()}/><path d="M4 34h142" ${S()}/><circle cx="22" cy="19" r="5" fill="#ff4423"/><circle cx="38" cy="19" r="5" fill="#ffd23f"/><circle cx="54" cy="19" r="5" fill="#bdf246"/><path d="M50 58 32 77l18 19M100 58l18 19-18 19M84 52 66 102" fill="none" stroke="#fffaf0" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  agents: `<svg class="sticker-art" viewBox="0 -2 140 132" aria-hidden="true" focusable="false"><path d="M70 22v14" ${S()}/><path d="M70 0 74.5 9.5 84 14 74.5 18.5 70 28 65.5 18.5 56 14 65.5 9.5Z" fill="#ff4423" ${S(3)}/><rect x="4" y="66" width="14" height="30" rx="7" fill="#fffaf0" ${S()}/><rect x="122" y="66" width="14" height="30" rx="7" fill="#fffaf0" ${S()}/><rect x="16" y="34" width="108" height="92" rx="28" fill="#ffd23f" ${S()}/><rect x="32" y="52" width="76" height="46" rx="18" fill="${ink}"/><circle class="robot-eye" cx="54" cy="75" r="8" fill="#bdf246"/><circle class="robot-eye" cx="86" cy="75" r="8" fill="#bdf246"/><path d="M58 109q12 8 24 0" fill="none" ${S()}/></svg>`,
  videos: `<svg class="sticker-art" viewBox="0 0 152 132" aria-hidden="true" focusable="false"><rect x="8" y="46" width="136" height="80" rx="12" fill="#ff5ca8" ${S()}/><path d="M8 46h136v20H8Z" fill="#fffaf0" ${S()}/><path d="M30 46 20 66M60 46 50 66M90 46 80 66M120 46l-10 20" ${S(6)}/><g transform="rotate(-16 8 44)"><rect x="8" y="22" width="136" height="20" rx="4" fill="#fffaf0" ${S()}/><path d="M30 22 20 42M60 22 50 42M90 22 80 42M120 22l-10 20" ${S(6)}/></g><circle cx="34" cy="96" r="10" fill="#ff4423" ${S(3)}/><path d="M58 90h64M58 104h40" ${S(5)}/></svg>`,
  lettuce: lettuceArt('sticker-art')
};

export function badge(id = 'badge-path') {
  const words = 'GAMES • SOFTWARE • AI AGENTS • VIDEOS • LETTUCE • ';
  return `<svg class="spin-badge" viewBox="0 0 200 200" aria-hidden="true" focusable="false"><defs><path id="${id}" d="M100 100m-74 0a74 74 0 1 1 148 0a74 74 0 1 1-148 0"/></defs><circle cx="100" cy="100" r="96" fill="#ffd23f" ${S()}/><circle cx="100" cy="100" r="54" fill="#fffaf0" ${S(3)}/><g class="spin-badge-ring"><text font-size="13.5" font-weight="800" letter-spacing="1.2" fill="${ink}"><textPath href="#${id}" textLength="462" lengthAdjust="spacing">${words}</textPath></text></g><path d="M100 64 108.6 91.4 136 100 108.6 108.6 100 136 91.4 108.6 64 100 91.4 91.4Z" fill="#ff4423" ${S(3)}/></svg>`;
}

/* A marquee "tape". Content is decorative; the same words appear as real text elsewhere. */
export function tape(className, words) {
  const run = words.map((word) => `<span>${e(word)}</span><svg viewBox="0 0 40 40" aria-hidden="true"><path d="M20 0 24.8 15.2 40 20 24.8 24.8 20 40 15.2 24.8 0 20 15.2 15.2Z" fill="currentColor"/></svg>`).join('');
  return `<div class="tape ${className}" aria-hidden="true"><div class="tape-track"><div class="tape-run">${run.repeat(3)}</div><div class="tape-run">${run.repeat(3)}</div></div></div>`;
}

export const motionToggle = `<button class="motion-toggle js-only" type="button" data-motion-toggle aria-pressed="false"><span class="motion-icon" aria-hidden="true"></span><span class="motion-label">${t('Pause motion', '움직임 멈춤')}</span></button>`;

/* ---------- Page chrome ---------- */
export function header(prefix, active = '', lang = 'en') {
  const navLink = (href, en, ko, key, dot) => `<a href="${prefix}${href}" style="--dot:var(--c-${dot})" ${active === key ? 'aria-current="page"' : ''}>${t(en, ko)}</a>`;
  return `<a class="skip-link" href="#main">${t('Skip to content', '본문 바로가기')}</a>
    <header class="site-header"><div class="container header-inner">
      <a class="brand" href="${prefix}index.html" ${label('KIMCHISTAN STUDIO home', '김치스탄 스튜디오 홈', lang)}>${brandMark}<span>KIMCHISTAN<span class="brand-subtitle">STUDIO</span></span></a>
      <nav class="site-navigation" id="site-navigation" ${label('Main navigation', '주 메뉴', lang)}>
        ${navLink('games/', 'Games', '게임', 'games', 'games')}
        ${navLink('services/', 'Software & AI', '소프트웨어 & AI', 'services', 'software')}
        ${navLink('index.html#videos', 'Videos', '영상', 'videos', 'videos')}
        ${navLink('index.html#lettuce', 'Lettuce', '상추', 'lettuce', 'lettuce')}
        ${navLink('index.html#studio', 'Studio', '스튜디오', 'studio', 'agents')}
        ${navLink('notices/', 'Notices <span class="nav-korean" lang="ko">전자공고</span>', '전자공고', 'notices', 'brand')}
        <a class="mobile-contact" href="${prefix}index.html#contact">${t('Start a project', '프로젝트 문의')}${arrow}</a>
      </nav>
      <div class="header-actions">
        <div class="language-switch" aria-label="Language / 언어"><button type="button" data-language="en" aria-pressed="${lang === 'en'}">EN</button><button type="button" data-language="ko" aria-pressed="${lang === 'ko'}" lang="ko">KO</button></div>
        <a class="header-contact" href="${prefix}index.html#contact">${t('Start a project', '프로젝트 문의')}${arrow}</a>
        <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-navigation" ${label('Open navigation', '메뉴 열기', lang)}><span></span><span></span></button>
      </div>
    </div></header>`;
}

export function footer(site, prefix) {
  const letters = [...'KIMCHISTAN'].map((letter, i) => `<span style="--i:${i}">${letter}</span>`).join('');
  return `<footer class="site-footer"><div class="flag-stripes" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div><div class="container">
    <div class="footer-top"><a class="brand" href="${prefix}index.html">${brandMark}<span>KIMCHISTAN<span class="brand-subtitle">STUDIO</span></span></a><p>${t('Games, software, AI agents and videos,<br>made in South Korea. Plus fresh lettuce.', '게임, 소프트웨어, AI 에이전트, 영상을<br>대한민국에서 만듭니다. 신선한 상추도 함께.')}</p></div>
    <div class="footer-details"><div class="company-legal">
      <p class="legal-name">${e(site.legalName)}</p><p lang="ko">${e(site.legalNameKo)}</p>
      <address><span lang="en">${e(site.address.en)}</span><span lang="ko">${e(site.address.ko)}</span></address>
      ${site.representative ? `<p>대표자 ${e(site.representative)}</p>` : ''}
      ${site.registrationNumber ? `<p>사업자등록번호 ${e(site.registrationNumber)}</p>` : ''}
      <a href="mailto:${e(site.email)}">${e(site.email)}</a>
      <div>${phoneLink(site)}</div>
    </div><div class="footer-navigation">
      <a href="${prefix}games/">${t('Games', '게임')}${arrow}</a>
      <a href="${prefix}services/">${t('Software & AI', '소프트웨어 & AI')}${arrow}</a>
      <a href="${prefix}index.html#videos">${t('Videos', '영상')}${arrow}</a>
      <a href="${prefix}index.html#lettuce">${t('Lettuce', '상추')}${arrow}</a>
      <a href="${prefix}notices/">${t('Official notices · 전자공고', '전자공고')}${arrow}</a>
    </div><div class="footer-socials">${[['itch.io', site.links.itch], ['Discord', site.links.discord], ['YouTube', site.links.youtube], ['X / Twitter', site.links.twitter]].map(([name, url]) => `<a ${external(url)}>${name}${arrow}</a>`).join('')}</div></div>
    <div class="footer-wordmark" aria-hidden="true">${letters}</div>
    <div class="footer-bottom"><span>© ${new Date().getFullYear()} ${e(site.legalName)}</span><span>${t('Made with curiosity and kimchi.', '호기심과 김치로 만듭니다.')}</span>${motionToggle}<a href="${prefix}index.html#main">${t('Back to top', '맨 위로')} ↑</a></div>
  </div></footer>`;
}

/* ---------- Shared content blocks ---------- */
export function projectCard(game, prefix, { featured = false, eager = false } = {}) {
  const link = game.detailPath ? `href="${prefix}${e(game.detailPath)}"` : external(game.url);
  return `<article class="project-card ${featured ? 'project-featured' : ''}" ${featured ? 'id="orbit-foundry"' : ''} data-reveal>
    <a class="project-link" ${link}>
      <div class="project-image"><img src="${prefix}${e(game.image)}" alt="" width="${featured ? 1920 : 800}" height="${featured ? 1080 : 500}" ${eager ? '' : 'loading="lazy"'}><span class="project-tag">${localized(game.status)}</span>${featured ? `<span class="project-badge">${t('In development', '개발 중')}</span>` : ''}</div>
      <div class="project-caption"><h3>${localized(game.title)}</h3><span class="project-action">${game.detailPath ? t('Discover', '자세히 보기') : t('Play on itch.io', 'itch.io에서 플레이')}${arrow}</span></div>
    </a><p class="project-summary">${localized(game.summary)}</p>
  </article>`;
}

export function resourceLink(game, prefix) {
  return `<a class="resource-link" ${external(game.url)} data-reveal><img src="${prefix}${e(game.image)}" alt="" width="126" height="100" loading="lazy"><div><p class="eyebrow">${localized(game.status)}</p><h3>${localized(game.title)}</h3><p>${localized(game.summary)}</p></div><span class="resource-arrow">${arrow}</span></a>`;
}

export function community(site) {
  return `<div class="community-links">${[
    ['Discord', 'Share builds, ideas & feedback', '빌드와 아이디어, 피드백을 나눠요', site.links.discord],
    ['YouTube', 'A closer look at our games', '우리 게임을 더 가까이에서', site.links.youtube],
    ['X / Twitter', 'Follow the next chapter', '다음 이야기를 만나보세요', site.links.twitter]
  ].map(([name, en, ko, url]) => `<a ${external(url)}><span><strong>${name}</strong><small>${t(en, ko)}</small></span>${arrow}</a>`).join('')}</div>`;
}

const topicLabels = {
  games: ['Email us about a game', '게임 프로젝트 문의하기'],
  software: ['Email us about software', '소프트웨어 프로젝트 문의하기'],
  agents: ['Email us about an AI agent', 'AI 에이전트 프로젝트 문의하기'],
  videos: ['Email us about a video', '영상 제작 문의하기'],
  lettuce: ['Order fresh lettuce', '상추 주문 문의하기']
};

export function contact(site, { compact = false } = {}) {
  const topics = crafts.map((craft) => `<label class="topic-chip" style="--chip:var(--c-${craft.key})"><input type="radio" name="topic" value="${craft.key}" data-topic data-mail-en="${e(inquiryHref(site.email, 'en', craft.key))}" data-mail-ko="${e(inquiryHref(site.email, 'ko', craft.key))}" data-cta-en="${e(topicLabels[craft.key][0])}" data-cta-ko="${e(topicLabels[craft.key][1])}"><span>${t(craft.en, craft.ko)}</span></label>`).join('');
  return `<section class="contact-section section ${compact ? 'contact-compact' : ''}" id="contact"><div class="container">
    <p class="kicker"><span class="tag">${t('Order up', '주문 받습니다')}</span>${t('Have something in mind?', '생각하고 있는 프로젝트가 있나요?')}</p>
    <div class="contact-grid"><div><h2 class="display contact-title">${t('Let’s cook<br>something <em>up.</em>', '함께 맛있게<br><em>만들어 봐요.</em>')}</h2><p class="contact-intro">${t('A game. A useful tool. An AI agent that takes the busywork. A video that explains it all. Or a box of lettuce. Tell us where you’d like to start.', '게임, 꼭 필요한 도구, 번거로운 일을 맡아 줄 AI 에이전트, 한눈에 이해되는 영상, 혹은 상추 한 상자까지. 어디에서 시작하고 싶은지 들려주세요.')}</p></div>
    <div class="contact-card" data-reveal>
      <fieldset class="topic-picker js-only"><legend class="mini-label">${t('What are we making?', '무엇을 만들까요?')}</legend><div class="topic-chips">${topics}</div></fieldset>
      <h3>${t('Tell us what you’re building.', '만들고 싶은 것을 알려주세요.')}</h3><p>${t('Share your goal, current tools, and timing. Our email template gives you a starting point.', '목표와 현재 사용하는 도구, 희망 일정을 알려주세요. 이메일 양식에 간단히 적어 주시면 됩니다.')}</p>
      <a class="button button-primary" data-inquiry href="${e(inquiryHref(site.email, 'en'))}" data-href-en="${e(inquiryHref(site.email, 'en'))}" data-href-ko="${e(inquiryHref(site.email, 'ko'))}"><span data-inquiry-label>${t('Start a project', '프로젝트 문의')}</span>${arrow}</a>
      <div class="email-row"><a href="mailto:${e(site.email)}">${e(site.email)}</a><button type="button" class="copy-email" data-copy-email="${e(site.email)}" hidden>${t('Copy', '복사')}</button></div><p class="copy-status" data-copy-status role="status" aria-live="polite"></p>
      <div class="email-row">${phoneLink(site)}</div>
    </div></div>
    ${compact ? '' : `<div class="contact-community"><span>${t('Here for the games?', '게임 이야기를 나누고 싶다면?')}</span><a ${external(site.links.discord)}>Discord ${arrow}</a><a ${external(site.links.youtube)}>YouTube ${arrow}</a><a ${external(site.links.twitter)}>X / Twitter ${arrow}</a></div>`}
  </div></section>`;
}
