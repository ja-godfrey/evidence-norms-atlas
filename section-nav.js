(() => {
  const links = Array.from(document.querySelectorAll('.section-nav a'));
  const sections = links.map(link => document.getElementById(link.hash.slice(1)));
  if (!links.length || sections.some(section => !section)) return;

  let scheduled = false;
  function update() {
    scheduled = false;
    const marker = Math.min(180, window.innerHeight * .25);
    let current = 0;
    sections.forEach((section, index) => {
      if (section.getBoundingClientRect().top <= marker) current = index;
    });
    // The final section can be shorter than the viewport.
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2) {
      current = sections.length - 1;
    }
    links.forEach((link, index) => {
      if (index === current) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }

  function scheduleUpdate() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(update);
  }

  window.addEventListener('scroll', scheduleUpdate, {passive: true});
  window.addEventListener('resize', scheduleUpdate);
  window.addEventListener('hashchange', scheduleUpdate);
  window.addEventListener('pageshow', scheduleUpdate);
  // Search results, expanded notes and media can change the section positions.
  if ('ResizeObserver' in window) {
    new ResizeObserver(scheduleUpdate).observe(document.querySelector('main'));
  }
  update();
})();
