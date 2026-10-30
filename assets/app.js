const storageKey = 'kimchistan-language';
document.documentElement.classList.add('js');
const currentLanguage = () => document.documentElement.lang === 'ko' ? 'ko' : 'en';
let copyState = '';

function setLanguage(language) {
  if (!['en', 'ko'].includes(language)) return;
  document.documentElement.lang = language;
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
  try { localStorage.setItem(storageKey, language); } catch { /* Language switching works without storage. */ }
}

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
  updateMenuLabel();
}
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
  if (!navigation?.contains(event.target) && !menuButton?.contains(event.target)) closeMenu();
});
window.matchMedia('(min-width: 960px)').addEventListener('change', (event) => { if (event.matches) closeMenu(); });

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
