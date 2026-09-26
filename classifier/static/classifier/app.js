(() => {
  const toggle = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('[data-menu]');
  const overlay = document.querySelector('[data-menu-overlay]');
  const berandaLink = document.querySelector('[data-nav="beranda"]');
  const klasifikasiLink = document.querySelector('[data-nav="klasifikasi"]');
  const desktopBreakpoint = 760;

  if (!toggle || !menu) return;

  const isDesktop = () => window.innerWidth > desktopBreakpoint;

  const closeMenu = () => {
    document.body.classList.remove('menu-open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.querySelector('.sr-only').textContent = 'Buka menu navigasi';
    if (overlay) overlay.hidden = true;
  };

  const openMenu = () => {
    document.body.classList.add('menu-open');
    toggle.setAttribute('aria-expanded', 'true');
    toggle.querySelector('.sr-only').textContent = 'Tutup menu navigasi';
    if (overlay) overlay.hidden = false;
  };

  toggle.addEventListener('click', () => {
    if (document.body.classList.contains('menu-open')) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  menu.addEventListener('click', event => {
    if (event.target.closest('a')) closeMenu();
  });

  overlay?.addEventListener('click', closeMenu);

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeMenu();
  });

  window.addEventListener('resize', () => {
    if (isDesktop()) closeMenu();
  });

  const syncClassificationActiveState = () => {
    if (!berandaLink || !klasifikasiLink) return;
    const onHome = window.location.pathname === '/';
    const onClassification = onHome && window.location.hash === '#klasifikasi';

    if (onClassification) {
      klasifikasiLink.setAttribute('aria-current', 'page');
      berandaLink.removeAttribute('aria-current');
    } else if (berandaLink.hasAttribute('aria-current') || onHome) {
      klasifikasiLink.removeAttribute('aria-current');
    }
  };

  window.addEventListener('hashchange', syncClassificationActiveState);
  syncClassificationActiveState();
})();

// ===== Carousel foto observasi (di halaman hasil klasifikasi) =====
(() => {
  document.querySelectorAll('[data-carousel]').forEach((carousel) => {
    const slides = carousel.querySelectorAll('[data-carousel-slide]');
    const details = carousel.querySelectorAll('[data-carousel-details]');
    const counter = carousel.querySelector('[data-carousel-counter]');
    const prevBtn = carousel.querySelector('[data-carousel-prev]');
    const nextBtn = carousel.querySelector('[data-carousel-next]');

    if (slides.length <= 1) return; // cuma 1 foto, ga perlu navigasi

    let index = 0;

    const render = () => {
      slides.forEach((el, i) => el.classList.toggle('is-active', i === index));
      details.forEach((el, i) => el.classList.toggle('is-active', i === index));
      if (counter) counter.textContent = `${index + 1} / ${slides.length}`;
    };

    prevBtn?.addEventListener('click', () => {
      index = (index - 1 + slides.length) % slides.length;
      render();
    });

    nextBtn?.addEventListener('click', () => {
      index = (index + 1) % slides.length;
      render();
    });
  });
})();
