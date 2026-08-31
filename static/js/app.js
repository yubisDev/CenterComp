(function () {
  var sidebar = document.getElementById('appSidebar');
  var toggle = document.getElementById('sidebarToggle');
  var backdrop = document.getElementById('sidebarBackdrop');
  if (!sidebar || !toggle || !backdrop) return;

  function close() {
    sidebar.classList.remove('open');
    backdrop.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
  }

  function open() {
    sidebar.classList.add('open');
    backdrop.classList.add('open');
    toggle.setAttribute('aria-expanded', 'true');
  }

  toggle.addEventListener('click', function () {
    if (sidebar.classList.contains('open')) close();
    else open();
  });
  backdrop.addEventListener('click', close);
  sidebar.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', close);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') close();
  });
})();

(function () {
  var root = document.documentElement;
  var themeBtn = document.getElementById('themeToggle');
  var collapseBtn = document.getElementById('sidebarCollapseBtn');

  if (themeBtn) {
    var syncThemeLabel = function () {
      var isDark = root.getAttribute('data-theme') === 'dark';
      themeBtn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
      themeBtn.setAttribute('aria-label', isDark ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro');
    };
    syncThemeLabel();
    themeBtn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('isyn-theme', next); } catch (e) {}
      syncThemeLabel();
    });
  }

  if (collapseBtn) {
    var syncCollapseLabel = function () {
      var collapsed = root.getAttribute('data-sidebar') === 'collapsed';
      collapseBtn.setAttribute('aria-pressed', collapsed ? 'true' : 'false');
      collapseBtn.setAttribute('aria-label', collapsed ? 'Mostrar navegación' : 'Ocultar navegación');
    };
    syncCollapseLabel();
    collapseBtn.addEventListener('click', function () {
      var collapsed = root.getAttribute('data-sidebar') === 'collapsed';
      if (collapsed) {
        root.removeAttribute('data-sidebar');
        try { localStorage.removeItem('isyn-sidebar'); } catch (e) {}
      } else {
        root.setAttribute('data-sidebar', 'collapsed');
        try { localStorage.setItem('isyn-sidebar', 'collapsed'); } catch (e) {}
      }
      syncCollapseLabel();
    });
  }
})();
