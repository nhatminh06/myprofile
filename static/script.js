// Dropdown menu logic for avatar
const avatarMini = document.querySelector('.dashboard-avatar-mini');
const dropdownMenu = document.querySelector('.dropdown-menu');

if (avatarMini && dropdownMenu) {
  avatarMini.addEventListener('click', (event) => {
    event.stopPropagation();
    dropdownMenu.style.opacity = dropdownMenu.style.opacity === '1' ? '0' : '1';
    dropdownMenu.style.visibility = dropdownMenu.style.visibility === 'visible' ? 'hidden' : 'visible';
    dropdownMenu.style.transform = dropdownMenu.style.opacity === '1' ? 'translateY(0)' : 'translateY(-10px)';
  });
  document.addEventListener('click', (event) => {
    if (!dropdownMenu.contains(event.target) && event.target !== avatarMini) {
      dropdownMenu.style.opacity = '0';
      dropdownMenu.style.visibility = 'hidden';
      dropdownMenu.style.transform = 'translateY(-10px)';
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const main = document.querySelector('main');
  if (main) {
    main.id ||= 'main-content';
    const skipLink = document.createElement('a');
    skipLink.className = 'skip-link';
    skipLink.href = `#${main.id}`;
    skipLink.textContent = 'Skip to main content';
    document.body.prepend(skipLink);
  }

  document.querySelectorAll('a[target="_blank"]').forEach((link) => {
    link.rel = 'noopener noreferrer';
  });

  const filterButtons = document.querySelectorAll('.filter-btn');
  const blogCards = document.querySelectorAll('.blog-card');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (filterButtons.length > 0 && blogCards.length > 0) {
    filterButtons.forEach((button) => {
      button.setAttribute('aria-pressed', button.classList.contains('active') ? 'true' : 'false');
      button.addEventListener('click', function() {
        const filter = this.getAttribute('data-filter');

        filterButtons.forEach((item) => {
          item.classList.remove('active');
          item.setAttribute('aria-pressed', 'false');
        });
        this.classList.add('active');
        this.setAttribute('aria-pressed', 'true');

        blogCards.forEach((card) => {
          const tags = card.getAttribute('data-tags');
          const visible = filter === 'all' || (tags && tags.includes(filter));
          card.style.display = visible ? 'block' : 'none';

          if (visible && !reduceMotion) {
            card.style.animation = 'fadeSlideUp 0.6s ease forwards';
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
              card.style.opacity = '1';
              card.style.transform = 'translateY(0)';
            }, 100);
          }
        });
      });
    });
  }
});
