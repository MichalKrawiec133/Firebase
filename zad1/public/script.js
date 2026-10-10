const themeToggle = document.getElementById('theme-toggle');
const countOutput = document.getElementById('count');
let count = 0;
themeToggle?.addEventListener('click', () => {
  const dark = document.body.classList.toggle('dark');
  themeToggle.setAttribute('aria-pressed', String(dark));
  themeToggle.textContent = dark ? 'Jasny motyw' : 'Ciemny motyw';
});
document.getElementById('increment').addEventListener('click', () => {
  countOutput.textContent = String(++count);
});
document.getElementById('reset').addEventListener('click', () => {
  count = 0;
  countOutput.textContent = String(count);
});
document.getElementById('year').textContent = String(new Date().getFullYear());

