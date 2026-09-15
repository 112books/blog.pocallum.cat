/* ── Nav mobile ─────────────────────────────────────────────────────────── */
(function () {
  const toggle = document.getElementById('js-nav-toggle');
  const menu   = document.getElementById('js-nav-menu');
  if (!toggle || !menu) return;

  toggle.addEventListener('click', () => {
    const open = menu.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', String(open));
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && menu.classList.contains('is-open')) {
      menu.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.focus();
    }
  });
})();

/* ── Header: estat en scroll (borda accent) ────────────────────────────── */
(function () {
  const header = document.getElementById('js-header');
  if (!header) return;
  const mark = () => header.classList.toggle('is-scrolled', window.scrollY > 8);
  mark();
  window.addEventListener('scroll', mark, { passive: true });
})();

/* ── Lightbox ───────────────────────────────────────────────────────────── */
(function () {
  const imgs = Array.from(document.querySelectorAll('.prose img'));
  if (!imgs.length) return;

  /* Construïm el lightbox al DOM */
  const lb   = document.createElement('div');
  lb.id      = 'js-lightbox';
  lb.className = 'lightbox';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Visualitzador d\'imatges');
  lb.hidden  = true;
  lb.innerHTML = `
    <button class="lightbox__close" aria-label="Tancar">&#x2715;</button>
    <button class="lightbox__prev" aria-label="Anterior">&#x2039;</button>
    <div class="lightbox__wrap">
      <img class="lightbox__img" src="" alt="">
      <p class="lightbox__caption"></p>
    </div>
    <button class="lightbox__next" aria-label="Següent">&#x203A;</button>`;
  document.body.appendChild(lb);

  const lbImg     = lb.querySelector('.lightbox__img');
  const lbCaption = lb.querySelector('.lightbox__caption');
  const btnClose  = lb.querySelector('.lightbox__close');
  const btnPrev   = lb.querySelector('.lightbox__prev');
  const btnNext   = lb.querySelector('.lightbox__next');

  let current = 0;
  let prevFocus = null;

  function show(i) {
    current = (i + imgs.length) % imgs.length;
    const img = imgs[current];
    lbImg.src = img.src;
    lbImg.alt = img.alt || '';
    lbCaption.textContent = img.alt || '';
    btnPrev.classList.toggle('is-hidden', imgs.length <= 1);
    btnNext.classList.toggle('is-hidden', imgs.length <= 1);
  }

  function open(i) {
    prevFocus = document.activeElement;
    lb.hidden = false;
    requestAnimationFrame(() => lb.classList.add('is-open'));
    show(i);
    document.body.style.overflow = 'hidden';
    btnClose.focus();
  }

  function close() {
    lb.classList.remove('is-open');
    lb.addEventListener('transitionend', () => {
      lb.hidden = true;
      document.body.style.overflow = '';
      if (prevFocus) prevFocus.focus();
    }, { once: true });
  }

  /* Marcar imatges i afegir click */
  imgs.forEach((img, i) => {
    img.classList.add('is-lightbox');
    img.addEventListener('click', () => open(i));
  });

  btnClose.addEventListener('click', close);
  btnPrev.addEventListener('click', () => show(current - 1));
  btnNext.addEventListener('click', () => show(current + 1));

  /* Clic al fons tanca */
  lb.addEventListener('click', (e) => { if (e.target === lb) close(); });

  /* Teclat */
  document.addEventListener('keydown', (e) => {
    if (lb.hidden) return;
    if (e.key === 'Escape')     { e.preventDefault(); close(); }
    if (e.key === 'ArrowLeft')  { e.preventDefault(); show(current - 1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); show(current + 1); }
  });

  /* Swipe tàctil */
  let touchX = 0;
  lb.addEventListener('touchstart', (e) => { touchX = e.changedTouches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', (e) => {
    const dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 50) dx < 0 ? show(current + 1) : show(current - 1);
  }, { passive: true });
})();

/* ── Comptador animat (home stats) ─────────────────────────────────────── */
(function () {
  const els = document.querySelectorAll('.js-count');
  if (!els.length) return;

  function fmt(n) {
    return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  }

  function animate(el, target, duration) {
    const start = performance.now();
    (function step(now) {
      const p = Math.min((now - start) / duration, 1);
      const ease = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(Math.round(ease * target));
      if (p < 1) requestAnimationFrame(step);
    })(start);
  }

  if ('IntersectionObserver' in window) {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        animate(e.target, parseInt(e.target.dataset.count, 10), 1600);
        obs.unobserve(e.target);
      });
    }, { threshold: 0.5 });
    els.forEach(el => obs.observe(el));
  } else {
    els.forEach(el => { el.textContent = fmt(parseInt(el.dataset.count, 10)); });
  }
})();

/* ── Back to top ────────────────────────────────────────────────────────── */
(function () {
  const btn = document.getElementById('js-back-top');
  if (!btn) return;
  const footer = document.querySelector('.site-footer');

  const show = () => {
    const sobrePeu = footer && footer.getBoundingClientRect().top < window.innerHeight;
    btn.hidden = window.scrollY < 600 || sobrePeu;
  };
  show();
  window.addEventListener('scroll', show, { passive: true });
  window.addEventListener('resize', show, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();