/* Replace only this URL to update every GitHub link on the page. */
const GITHUB_URL = 'https://github.com/Varun-2009';

document.querySelectorAll('[data-github]').forEach(link => {
  link.href = GITHUB_URL;
  if (!GITHUB_URL.includes('YOUR-USERNAME')) {
    link.querySelector('small')?.remove();
  }
});
if (!GITHUB_URL.includes('YOUR-USERNAME')) {
  document.getElementById('github-note').textContent = 'Explore my repositories on GitHub.';
}

const menuButton = document.querySelector('.menu-toggle');
const navigation = document.getElementById('navigation');
menuButton.hidden = false;
navigation.dataset.collapsible = 'true';
function closeMenu() {
  navigation.classList.remove('open');
  menuButton.setAttribute('aria-expanded', 'false');
}
menuButton.addEventListener('click', () => {
  const open = navigation.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(open));
});
navigation.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && navigation.classList.contains('open')) {
    closeMenu();
    menuButton.focus();
  }
});
document.getElementById('year').textContent = new Date().getFullYear();
