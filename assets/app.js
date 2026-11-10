const storageKey = 'kimchistan-language';
const motionKey = 'kimchistan-motion';
const root = document.documentElement;
root.classList.add('js');
const currentLanguage = () => root.lang === 'ko' ? 'ko' : 'en';
const finePointer = window.matchMedia('(pointer: fine)');
let copyState = '';

/* ---------- Motion: one switch for the pause control and reduced-motion ---------- */
const motionPaused = () => root.classList.contains('motion-paused');
function setMotion(paused, persist = false) {
  root.classList.toggle('motion-paused', paused);
  document.querySelectorAll('[data-motion-toggle]').forEach((button) => button.setAttribute('aria-pressed', String(paused)));
  if (persist) {
    try { localStorage.setItem(motionKey, paused ? 'paused' : 'playing'); } catch { /* Storage is optional. */ }
  }
  if (!paused) scheduleWord();
}

/* ---------- Language ---------- */
function setLanguage(language) {
  if (!['en', 'ko'].includes(language)) return;
  root.lang = language;
  document.querySelectorAll('[data-language]').forEach((button) => {
    button.setAttribute('aria-pressed', String(button.dataset.language === language));
  });
  for (const [attribute, key] of [['aria-label', 'label'], ['alt', 'alt'], ['href', 'href'], ['content', 'content']]) {
    document.querySelectorAll(`[data-${key}-en]`).forEach((element) => {
      element.setAttribute(attribute, element.dataset[key + (language === 'ko' ? 'Ko' : 'En')]);
    });
  }
  document.querySelectorAll('[data-text-en]').forEach((element) => {
    element.textContent = element.dataset[language === 'ko' ? 'textKo' : 'textEn'];
  });
  updateCopyStatus();
  updateMenuLabel();
  sizeRotators();
  try { localStorage.setItem(storageKey, language); } catch { /* Language switching works without storage. */ }
}

/* ---------- Navigation ---------- */
const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#site-navigation');
function updateMenuLabel() {
  if (!menuButton) return;
  const open = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-label', currentLanguage() === 'ko' ? (open ? '메뉴 닫기' : '메뉴 열기') : (open ? 'Close navigation' : 'Open navigation'));
}
function closeMenu() {
  if (!menuButton || !navigation) return;
  menuButton.setAttribute('aria-expanded', 'false');
  navigation.classList.remove('is-open');
  document.body.style.overflow = '';
  updateMenuLabel();
}

/* ---------- Hero word rotator ---------- */
const hero = document.querySelector('[data-hero]');
const words = ['games', 'software', 'agents', 'videos', 'lettuce'];
let wordIndex = 0;
let wordTimer = 0;
let heroVisible = true;
function sizeRotators() {
  document.querySelectorAll('[data-rotator]').forEach((rotator) => {
    const active = rotator.querySelector('.is-active');
    if (active && rotator.offsetParent !== null) rotator.style.width = `calc(${active.offsetWidth}px + .28em)`;
  });
}
function showWord(index) {
  const key = words[index];
  hero.dataset.word = key;
  document.querySelectorAll('[data-rotator] .rotator-word').forEach((word) => {
    const on = word.dataset.word === key;
    if (!on && word.classList.contains('is-active')) {
      word.classList.remove('is-active');
      word.classList.add('is-leaving');
      setTimeout(() => word.classList.remove('is-leaving'), 600);
    } else if (on) {
      word.classList.remove('is-leaving');
      word.classList.add('is-active');
    }
  });
  sizeRotators();
}
function scheduleWord() {
  if (!hero) return;
  clearTimeout(wordTimer);
  if (motionPaused()) return;
  wordTimer = setTimeout(() => {
    if (!motionPaused() && heroVisible && !document.hidden) {
      wordIndex = (wordIndex + 1) % words.length;
      showWord(wordIndex);
    }
    scheduleWord();
  }, words[wordIndex] === 'lettuce' ? 3600 : 2000);
}
if (hero) {
  new IntersectionObserver(([entry]) => { heroVisible = entry.isIntersecting; }).observe(hero);
  window.addEventListener('resize', sizeRotators);
  document.fonts?.ready.then(sizeRotators);
}

(() => {
  let saved = null;
  try { saved = localStorage.getItem(motionKey); } catch { /* Storage is optional. */ }
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  setMotion(saved === 'paused' || (saved !== 'playing' && reduce));
})();
document.querySelectorAll('[data-motion-toggle]').forEach((button) => button.addEventListener('click', () => setMotion(!motionPaused(), true)));

let language = currentLanguage();
try {
  const saved = localStorage.getItem(storageKey);
  if (saved === 'en' || saved === 'ko') language = saved;
} catch { /* Storage is optional. */ }
setLanguage(language);
document.querySelectorAll('[data-language]').forEach((button) => button.addEventListener('click', () => setLanguage(button.dataset.language)));
menuButton?.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  navigation?.classList.toggle('is-open', open);
  document.body.style.overflow = open ? 'hidden' : '';
  updateMenuLabel();
  if (open) navigation?.querySelector('a')?.focus();
});
navigation?.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menuButton.focus();
  }
});
document.addEventListener('click', (event) => {
  if (!navigation?.contains(event.target) && !menuButton?.contains(event.target)) closeMenu();
});
document.addEventListener('focusin', (event) => {
  if (!navigation?.contains(event.target) && !menuButton?.contains(event.target) && !event.target.closest?.('.header-inner')) closeMenu();
});
window.matchMedia('(min-width: 1180px)').addEventListener('change', (event) => { if (event.matches) closeMenu(); });

/* ---------- Draggable stickers ---------- */
let stickerZ = 10;
document.querySelectorAll('[data-sticker]').forEach((sticker) => {
  let start = null;
  let moved = false;
  sticker.addEventListener('dragstart', (event) => event.preventDefault());
  sticker.addEventListener('pointerdown', (event) => {
    if (event.pointerType === 'touch' || event.button !== 0) return;
    event.preventDefault();
    const dx = parseFloat(sticker.style.getPropertyValue('--dx')) || 0;
    const dy = parseFloat(sticker.style.getPropertyValue('--dy')) || 0;
    start = { x: event.clientX - dx, y: event.clientY - dy, sx: event.clientX, sy: event.clientY };
    moved = false;
    sticker.setPointerCapture(event.pointerId);
    sticker.classList.add('is-dragging');
    sticker.style.zIndex = String(++stickerZ);
  });
  sticker.addEventListener('pointermove', (event) => {
    if (!start) return;
    if (Math.hypot(event.clientX - start.sx, event.clientY - start.sy) > 5) moved = true;
    sticker.style.setProperty('--dx', `${event.clientX - start.x}px`);
    sticker.style.setProperty('--dy', `${event.clientY - start.y}px`);
  });
  const end = () => {
    if (!start) return;
    start = null;
    sticker.classList.remove('is-dragging');
    if (moved) document.querySelector('.drag-hint')?.classList.add('is-done');
  };
  sticker.addEventListener('pointerup', (event) => {
    end();
    if (event.pointerType === 'touch' && !motionPaused()) {
      sticker.classList.remove('wiggle');
      void sticker.offsetWidth;
      sticker.classList.add('wiggle');
    }
  });
  sticker.addEventListener('pointercancel', end);
  sticker.addEventListener('click', (event) => {
    if (moved) { event.preventDefault(); moved = false; }
  });
});

/* ---------- Tilt on menu tiles ---------- */
document.querySelectorAll('[data-tilt]').forEach((tile) => {
  tile.addEventListener('pointermove', (event) => {
    if (!finePointer.matches || motionPaused()) return;
    const box = tile.getBoundingClientRect();
    const x = (event.clientX - box.left) / box.width - 0.5;
    const y = (event.clientY - box.top) / box.height - 0.5;
    tile.style.setProperty('--ry', `${(x * 7).toFixed(2)}deg`);
    tile.style.setProperty('--rx', `${(-y * 7).toFixed(2)}deg`);
  });
  tile.addEventListener('pointerleave', () => {
    tile.style.setProperty('--rx', '0deg');
    tile.style.setProperty('--ry', '0deg');
  });
});

/* ---------- Scroll reveals ---------- */
const reveals = document.querySelectorAll('[data-reveal]');
if ('IntersectionObserver' in window) {
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-in');
      revealObserver.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -6% 0px', threshold: 0.08 });
  reveals.forEach((element) => revealObserver.observe(element));
} else {
  reveals.forEach((element) => element.classList.add('is-in'));
}

/* ---------- Goyang clock & camera timecode ---------- */
const clocks = document.querySelectorAll('[data-clock]');
if (clocks.length) {
  const format = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Seoul', hour: '2-digit', minute: '2-digit', hour12: false });
  const tick = () => { const time = `${format.format(new Date())} KST`; clocks.forEach((clock) => { clock.textContent = time; }); };
  tick();
  setInterval(tick, 15000);
}
const timecodes = new Set();
const allTimecodes = document.querySelectorAll('[data-timecode]');
if (allTimecodes.length) {
  const started = performance.now();
  const timecodeObserver = new IntersectionObserver((entries) => entries.forEach((entry) => {
    if (entry.isIntersecting) timecodes.add(entry.target); else timecodes.delete(entry.target);
  }));
  allTimecodes.forEach((element) => timecodeObserver.observe(element));
  setInterval(() => {
    if (motionPaused() || document.hidden || !timecodes.size) return;
    const frames = Math.floor(((performance.now() - started) / 1000) * 24);
    const text = [Math.floor(frames / 86400), Math.floor(frames / 1440) % 60, Math.floor(frames / 24) % 60, frames % 24].map((n) => String(n).padStart(2, '0')).join(':');
    timecodes.forEach((element) => { element.textContent = text; });
  }, 1000 / 24);
}

/* ---------- Lettuce: pick a leaf ---------- */
const harvest = document.querySelector('[data-harvest]');
if (harvest) {
  const fall = document.querySelector('[data-leaf-fall]');
  const template = document.querySelector('[data-leaf-template]');
  const count = document.querySelector('[data-harvest-count]');
  let picked = 0;
  harvest.addEventListener('click', () => {
    picked += 1;
    if (count) count.textContent = String(picked);
    if (motionPaused() || !fall || !template) return;
    const leaf = document.createElement('span');
    leaf.className = 'falling-leaf';
    leaf.append(template.content.cloneNode(true));
    leaf.style.left = `${32 + Math.random() * 30}%`;
    leaf.style.top = `${22 + Math.random() * 18}%`;
    leaf.style.setProperty('--fx', `${Math.round(Math.random() * 260 - 130)}px`);
    leaf.style.setProperty('--fy', `${Math.round(240 + Math.random() * 140)}px`);
    leaf.style.setProperty('--fr', `${Math.round(Math.random() * 540 - 270)}deg`);
    leaf.addEventListener('animationend', () => leaf.remove());
    fall.append(leaf);
    harvest.classList.remove('is-shaking');
    void harvest.offsetWidth;
    harvest.classList.add('is-shaking');
  });
}

/* ---------- Contact topics rewrite the email template ---------- */
const inquiry = document.querySelector('[data-inquiry]');
document.querySelectorAll('[data-topic]').forEach((radio) => radio.addEventListener('change', () => {
  if (!radio.checked || !inquiry) return;
  inquiry.dataset.hrefEn = radio.dataset.mailEn;
  inquiry.dataset.hrefKo = radio.dataset.mailKo;
  inquiry.href = currentLanguage() === 'ko' ? radio.dataset.mailKo : radio.dataset.mailEn;
  const labelElement = inquiry.querySelector('[data-inquiry-label]');
  if (labelElement) {
    labelElement.querySelector('[lang=en]').textContent = radio.dataset.ctaEn;
    labelElement.querySelector('[lang=ko]').textContent = radio.dataset.ctaKo;
  }
  if (!motionPaused()) {
    inquiry.classList.remove('is-bump');
    void inquiry.offsetWidth;
    inquiry.classList.add('is-bump');
  }
}));

/* ---------- Existing utilities ---------- */
document.querySelector('[data-print]')?.addEventListener('click', () => window.print());
const copyButton = document.querySelector('[data-copy-email]');
function updateCopyStatus() {
  if (!copyState) return;
  const messages = copyState === 'success'
    ? { en: 'Email address copied.', ko: '이메일 주소를 복사했습니다.' }
    : { en: 'Select the email address to copy it.', ko: '주소를 직접 선택해 복사해 주세요.' };
  document.querySelector('[data-copy-status]').textContent = messages[currentLanguage()];
}
if (copyButton && navigator.clipboard?.writeText) {
  copyButton.hidden = false;
  copyButton.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(copyButton.dataset.copyEmail);
      copyState = 'success';
    } catch {
      copyState = 'error';
    }
    updateCopyStatus();
  });
}

const search = document.querySelector('[data-notice-search]');
const yearFilter = document.querySelector('[data-notice-year]');
function filterNotices() {
  const query = (search?.value || '').normalize('NFKC').trim().toLocaleLowerCase();
  const year = yearFilter?.value || '';
  let count = 0;
  document.querySelectorAll('[data-notice-row]').forEach((row) => {
    const matches = row.dataset.search.includes(query) && (!year || row.dataset.year === year);
    row.hidden = !matches;
    if (matches) count += 1;
  });
  const empty = document.querySelector('[data-no-results]');
  if (empty) empty.hidden = count !== 0;
  const countElement = document.querySelector('[data-result-count]');
  if (countElement) countElement.textContent = String(count);
}
search?.addEventListener('input', filterNotices);
yearFilter?.addEventListener('change', filterNotices);

const gameplayImage = document.querySelector('#gameplay-image');
document.querySelectorAll('[data-screenshot]').forEach((button) => {
  button.addEventListener('click', () => {
    if (!gameplayImage) return;
    gameplayImage.src = button.dataset.screenshot;
    gameplayImage.dataset.altEn = button.dataset.screenAltEn;
    gameplayImage.dataset.altKo = button.dataset.screenAltKo;
    const caption = document.querySelector('[data-gallery-caption]');
    caption.dataset.textEn = button.dataset.captionEn;
    caption.dataset.textKo = button.dataset.captionKo;
    gameplayImage.alt = button.dataset[currentLanguage() === 'ko' ? 'screenAltKo' : 'screenAltEn'];
    caption.textContent = button.dataset[currentLanguage() === 'ko' ? 'captionKo' : 'captionEn'];
    document.querySelectorAll('[data-screenshot]').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
    const status = document.querySelector('[data-gallery-status]');
    status.dataset.textEn = button.dataset.captionEn;
    status.dataset.textKo = button.dataset.captionKo;
    status.textContent = caption.textContent;
  });
});
