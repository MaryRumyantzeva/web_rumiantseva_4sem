const themeToggle = document.getElementById('toggle-theme');
const htmlElement = document.documentElement;
const navbar = document.getElementById('main-navbar');
const footer = document.getElementById('main-footer');

function applyTheme(theme) {
  htmlElement.setAttribute('data-bs-theme', theme);
  localStorage.setItem('theme', theme);

  if (theme === 'dark') {
    navbar.classList.remove('navbar-light', 'bg-light');
    navbar.classList.add('navbar-dark', 'bg-dark');

    footer.classList.remove('bg-light', 'text-dark');
    footer.classList.add('bg-dark', 'text-light');
  } else {
    navbar.classList.remove('navbar-dark', 'bg-dark');
    navbar.classList.add('navbar-light', 'bg-light');

    footer.classList.remove('bg-dark', 'text-light');
    footer.classList.add('bg-light', 'text-dark');
  }
}

const savedTheme = localStorage.getItem('theme') || 'dark';
applyTheme(savedTheme);

themeToggle.addEventListener('click', () => {
  const newTheme = htmlElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
  applyTheme(newTheme);
});
