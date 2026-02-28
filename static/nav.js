document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('nav-links');

  if (!toggle || !nav) return;

  toggle.addEventListener('click', function (e) {
    const isOpen = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', isOpen);
    const icon = toggle.querySelector('i');
    if (icon) {
      icon.classList.toggle('fa-bars', !isOpen);
      icon.classList.toggle('fa-times', isOpen);
    }
  });

  // Close nav when clicking outside (mobile)
  document.addEventListener('click', function (e) {
    if (!nav.classList.contains('open')) return;
    const target = e.target;
    if (!nav.contains(target) && !toggle.contains(target)) {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      const icon = toggle.querySelector('i');
      if (icon) {
        icon.classList.remove('fa-times');
        icon.classList.add('fa-bars');
      }
    }
  });
});
