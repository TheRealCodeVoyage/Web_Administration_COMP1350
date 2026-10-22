// Dark/light mode toggle for the course site.
// The initial theme is set by an inline script in _layouts/default.html
// (dark unless the visitor previously chose light); this file wires up the
// toggle button and animates the switch.
(function () {
  var STORAGE_KEY = 'comp1350-theme';
  var root = document.documentElement;
  var toggle = document.getElementById('theme_toggle');
  if (!toggle) return;

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function current() {
    return root.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
  }

  function syncToggle() {
    var dark = current() === 'dark';
    toggle.setAttribute('aria-checked', dark ? 'true' : 'false');
    toggle.title = dark ? 'Switch to light mode' : 'Switch to dark mode';
  }

  function apply(theme) {
    root.setAttribute('data-theme', theme);
    try { localStorage.setItem(STORAGE_KEY, theme); } catch (e) {}
    syncToggle();
  }

  // Browsers without the View Transitions API get a cross-fade of colours.
  function crossFade(theme) {
    root.classList.add('theme-transition');
    apply(theme);
    window.setTimeout(function () {
      root.classList.remove('theme-transition');
    }, 600);
  }

  // Browsers with the View Transitions API get a circular reveal that grows
  // out of the toggle until it covers the whole viewport.
  function circularReveal(theme) {
    var rect = toggle.getBoundingClientRect();
    var x = rect.left + rect.width / 2;
    var y = rect.top + rect.height / 2;
    var radius = Math.hypot(
      Math.max(x, window.innerWidth - x),
      Math.max(y, window.innerHeight - y)
    );

    var transition = document.startViewTransition(function () { apply(theme); });
    transition.ready.then(function () {
      root.animate(
        {
          clipPath: [
            'circle(0px at ' + x + 'px ' + y + 'px)',
            'circle(' + radius + 'px at ' + x + 'px ' + y + 'px)'
          ]
        },
        {
          duration: 700,
          easing: 'cubic-bezier(0.65, 0, 0.35, 1)',
          pseudoElement: '::view-transition-new(root)'
        }
      );
    }).catch(function () {});
  }

  toggle.addEventListener('click', function () {
    var next = current() === 'dark' ? 'light' : 'dark';
    if (reduceMotion.matches) {
      apply(next);
    } else if (document.startViewTransition) {
      circularReveal(next);
    } else {
      crossFade(next);
    }
  });

  // Keep other open tabs of the site in step.
  window.addEventListener('storage', function (event) {
    if (event.key !== STORAGE_KEY) return;
    root.setAttribute('data-theme', event.newValue === 'light' ? 'light' : 'dark');
    syncToggle();
  });

  syncToggle();
})();
