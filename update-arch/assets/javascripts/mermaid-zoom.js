(function () {
  const PANZOOM_SRC = "https://cdn.jsdelivr.net/npm/panzoom@9.4.3/dist/panzoom.min.js";

  function loadPanzoom() {
    return new Promise((resolve, reject) => {
      if (window.panzoom) return resolve(window.panzoom);
      const existing = document.querySelector('script[data-mermaid-zoom-panzoom]');
      if (existing) {
        existing.addEventListener("load", () => resolve(window.panzoom));
        return;
      }
      const s = document.createElement("script");
      s.src = PANZOOM_SRC;
      s.dataset.mermaidZoomPanzoom = "true";
      s.onload = () => resolve(window.panzoom);
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  function findContainer(svg) {
    // Walk up looking for a mermaid container (div.mermaid, pre.mermaid, or a div with class containing 'mermaid').
    let el = svg.parentElement;
    while (el && el !== document.body) {
      if (el.classList && (el.classList.contains("mermaid") || el.tagName === "PRE" && el.classList.contains("mermaid"))) {
        return el;
      }
      el = el.parentElement;
    }
    return svg.parentElement; // fallback
  }

  function enhance(svg) {
    if (svg.dataset.mzApplied === "true") return;
    const container = findContainer(svg);
    if (!container) return;
    if (container.dataset.zoomEnabled === "true") return;
    svg.dataset.mzApplied = "true";
    container.dataset.zoomEnabled = "true";
    container.classList.add("mermaid-zoom-container");

    // Ensure svg can be transformed
    svg.style.transformOrigin = "0 0";
    if (!svg.style.maxWidth) svg.style.maxWidth = "100%";

    const toolbar = document.createElement("div");
    toolbar.className = "mermaid-zoom-toolbar";

    const mkBtn = (label, title, onClick) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "mermaid-zoom-btn";
      b.title = title;
      b.setAttribute("aria-label", title);
      b.textContent = label;
      b.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        onClick();
      });
      return b;
    };

    let pz = null;
    const ensurePanzoom = () => {
      if (pz) return Promise.resolve(pz);
      return loadPanzoom().then((panzoom) => {
        if (!panzoom) throw new Error("panzoom failed to load");
        pz = panzoom(svg, {
          maxZoom: 8,
          minZoom: 0.3,
          bounds: false,
          smoothScroll: false,
          beforeWheel: () => false,
        });
        return pz;
      }).catch((err) => {
        console.error("[mermaid-zoom] panzoom load failed:", err);
      });
    };

    const zoomBy = (factor) =>
      ensurePanzoom().then((p) => {
        if (!p) return;
        const rect = svg.getBoundingClientRect();
        p.smoothZoom(rect.width / 2, rect.height / 2, factor);
      });

    const reset = () => {
      if (pz) { try { pz.dispose(); } catch (e) {} pz = null; }
      svg.style.transform = "";
    };

    const fullscreen = () => {
      if (document.fullscreenElement === container) {
        document.exitFullscreen();
      } else if (container.requestFullscreen) {
        container.requestFullscreen().catch((err) => console.warn("[mermaid-zoom] fullscreen denied:", err));
      }
    };

    toolbar.appendChild(mkBtn("+", "Zoom in", () => zoomBy(1.4)));
    toolbar.appendChild(mkBtn("−", "Zoom out", () => zoomBy(0.7)));
    toolbar.appendChild(mkBtn("↻", "Reset", reset));
    toolbar.appendChild(mkBtn("⛶", "Fullscreen", fullscreen));

    container.appendChild(toolbar);
  }

  function scan() {
    // Match SVGs inside anything labelled mermaid (div, pre, etc.)
    document.querySelectorAll(".mermaid svg, pre.mermaid svg").forEach(enhance);
  }

  function watch() {
    scan();
    const obs = new MutationObserver(() => scan());
    obs.observe(document.body, { childList: true, subtree: true });
    // Keep observing indefinitely — mermaid can render very late on slow connections
    // and the cost of one passive observer is negligible.
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", watch);
  } else {
    watch();
  }
})();
