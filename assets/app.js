const storageKey = 'kimchistan-language';

function setLanguage(language) {
  if (!['en', 'ko'].includes(language)) return;
  document.documentElement.lang = language;
  document.querySelectorAll('[data-language]').forEach((button) => {
    button.setAttribute('aria-pressed', String(button.dataset.language === language));
  });
  document.querySelectorAll('[data-label-en]').forEach((element) => {
    element.setAttribute('aria-label', element.dataset[language === 'ko' ? 'labelKo' : 'labelEn']);
  });
  const description = document.querySelector('meta[name="description"]');
  if (description?.dataset[language]) description.content = description.dataset[language];
  try { localStorage.setItem(storageKey, language); } catch { /* Storage is optional. */ }
}

let language = document.documentElement.lang;
try { language = localStorage.getItem(storageKey) || language; } catch { /* Private browsing works too. */ }
setLanguage(language);
document.querySelectorAll('[data-language]').forEach((button) => {
  button.addEventListener('click', () => setLanguage(button.dataset.language));
});

const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#site-navigation');
function closeMenu() {
  if (!menuButton || !navigation) return;
  menuButton.setAttribute('aria-expanded', 'false');
  navigation.classList.remove('is-open');
}
menuButton?.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  navigation?.classList.toggle('is-open', open);
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
window.matchMedia('(min-width: 801px)').addEventListener('change', (event) => {
  if (event.matches) closeMenu();
});

document.querySelector('[data-print]')?.addEventListener('click', () => window.print());

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

// Small, keyboard-accessible gallery of the game's real Steam screenshots.
const gameplayImage = document.querySelector('#gameplay-image');
document.querySelectorAll('[data-screenshot]').forEach((button) => {
  button.addEventListener('click', () => {
    if (!gameplayImage) return;
    gameplayImage.src = button.dataset.screenshot;
    gameplayImage.alt = button.dataset.alt;
    document.querySelectorAll('[data-screenshot]').forEach((item) => {
      item.setAttribute('aria-pressed', String(item === button));
    });
  });
});
