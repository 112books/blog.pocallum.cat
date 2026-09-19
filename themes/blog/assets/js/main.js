/* ── Nav mobile ─────────────────────────────────────────────────────────── */
(function () {
  const toggle = document.getElementById('js-nav-toggle');
  const menu   = document.getElementById('js-nav-menu');
  if (!toggle || !menu) return;

  function setOpen(open) {
    menu.classList.toggle('is-open', open);
    menu.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
  }

  toggle.addEventListener('click', () => {
    setOpen(!menu.classList.contains('is-open'));
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && menu.classList.contains('is-open')) {
      setOpen(false);
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

/* ── Emails protegits anti-spam ─────────────────────────────────────────── */
(function () {
  document.querySelectorAll('.js-email').forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      window.location.href = 'mailto:' + el.dataset.u + '@' + el.dataset.d;
    });
  });
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
    const single = imgs.length <= 1;
    btnPrev.classList.toggle('is-hidden', single);
    btnNext.classList.toggle('is-hidden', single);
    btnPrev.setAttribute('aria-hidden', String(single));
    btnNext.setAttribute('aria-hidden', String(single));
    if (single) {
      btnPrev.setAttribute('tabindex', '-1');
      btnNext.setAttribute('tabindex', '-1');
    } else {
      btnPrev.removeAttribute('tabindex');
      btnNext.removeAttribute('tabindex');
    }
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
    /* Doble via de finalització: transitionend si hi ha transició, i un timeout
       de seguretat per si prefers-reduced-motion l'ha anul·lada. */
    let done = false;
    const final = () => {
      if (done) return;
      done = true;
      lb.hidden = true;
      document.body.style.overflow = '';
      if (prevFocus) prevFocus.focus();
    };
    lb.addEventListener('transitionend', final, { once: true });
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      final();
    }
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
    if (e.key === 'Tab') {
      /* Focus trap: mantenir el focus dins del lightbox */
      const focusables = Array.from(
        lb.querySelectorAll('button, [href], [tabindex]:not([tabindex="-1"])')
      ).filter((el) => !el.hasAttribute('hidden') && el.getAttribute('aria-hidden') !== 'true');
      if (!focusables.length) return;
      const first = focusables[0];
      const last  = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
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

/* ── Links externs al contingut → pestanya nova ─────────────────────────── */
(function () {
  document.querySelectorAll('.prose a[href]').forEach(function (a) {
    const href = a.getAttribute('href');
    if (href && (href.startsWith('http://') || href.startsWith('https://'))) {
      a.setAttribute('target', '_blank');
      a.setAttribute('rel', 'noopener noreferrer');
    }
  });
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

/* ── Tira de navegació entre posts ─────────────────────────────────────── */
(function () {
  var strip = document.getElementById('js-strip');
  if (!strip) return;
  var cur = strip.querySelector('.is-current');
  if (cur) strip.scrollLeft = cur.offsetLeft - (strip.offsetWidth / 2) + (cur.offsetWidth / 2);
  document.getElementById('js-strip-prev').addEventListener('click', function () { strip.scrollBy({ left: -220, behavior: 'smooth' }); });
  document.getElementById('js-strip-next').addEventListener('click', function () { strip.scrollBy({ left: 220, behavior: 'smooth' }); });
})();