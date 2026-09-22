/* Collapsible "On this page" sections (see partials/toc-item.html and
   stylesheets/api-toc.css). Collapsing itself is pure CSS; script is only
   needed for deep links, which have to reveal the section holding the anchor,
   and for keyboard use, since a <label> does not toggle on Enter or Space. */
(function () {
  var roots = document.querySelectorAll(".md-nav--secondary");
  if (!roots.length) {
    return;
  }

  function itemToggle(item) {
    return item.querySelector(":scope > .md-nav__toggle");
  }

  function reveal(hash) {
    if (!hash) {
      return;
    }
    roots.forEach(function (root) {
      var target = null;
      root.querySelectorAll(".md-nav__link").forEach(function (link) {
        if (!target && link.hash === hash) {
          target = link;
        }
      });
      if (!target) {
        return;
      }
      var item = target.closest(".md-nav__item");
      while (item) {
        var toggle = itemToggle(item);
        if (toggle) {
          toggle.checked = true;
        }
        var parent = item.parentElement;
        item = parent ? parent.closest(".md-nav__item") : null;
      }
    });
  }

  reveal(window.location.hash);
  window.addEventListener("hashchange", function () {
    reveal(window.location.hash);
  });

  // Keep aria-expanded honest. Material maintains it for the primary nav's own
  // toggles, but not for these.
  roots.forEach(function (root) {
    root.addEventListener("change", function (event) {
      var toggle = event.target;
      if (!toggle.classList || !toggle.classList.contains("md-nav__toggle")) {
        return;
      }
      var nav = toggle.closest(".md-nav__item").querySelector(":scope > .md-nav");
      if (nav) {
        nav.setAttribute("aria-expanded", String(toggle.checked));
      }
    });
  });

  roots.forEach(function (root) {
    root.addEventListener("keydown", function (event) {
      if (event.key !== "Enter" && event.key !== " ") {
        return;
      }
      var label = event.target.closest(".md-nav__toc-toggle");
      if (!label) {
        return;
      }
      event.preventDefault();
      // Resolved through the DOM rather than the label's `for`, so it always
      // hits this copy of the TOC.
      var toggle = itemToggle(label.closest(".md-nav__item"));
      if (toggle) {
        toggle.checked = !toggle.checked;
      }
    });
  });
})();
