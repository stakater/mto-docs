(function () {
  const PANZOOM_SRC = "https://cdn.jsdelivr.net/npm/panzoom@9.4.3/dist/panzoom.min.js";

  function loadPanzoom() {
    return new Promise((resolve, reject) => {
      if (window.panzoom) return resolve(window.panzoom);
      const s = document.createElement("script");
      s.src = PANZOOM_SRC;
      s.onload = () => resolve(window.panzoom);
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  function enhance(svg) {
    const container = svg.parentElement;
    if (!container || container.dataset.zoomEnabled === "true") return;
    container.dataset.zoomEnabled = "true";
    container.classList.add("mermaid-zoom-container");

    const toolbar = document.createElement("div");
    toolbar.className = "mermaid-zoom-toolbar";

    const mkBtn = (label, title, onClick) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "mermaid-zoom-btn";
      b.title = title;
      b.setAttribute("aria-label", title);
      b.textContent = label;
      b.addEventListener("click", (e) => { e.preventDefault(); onClick(); });
      return b;
    };

    let pz = null;
    const ensurePanzoom = () => {
      if (pz) return Promise.resolve(pz);
      return loadPanzoom().then((panzoom) => {
        pz = panzoom(svg, { maxZoom: 8, minZoom: 0.3, bounds: false, smoothScroll: false });
        return pz;
      });
    };

    const zoomBy = (factor) => ensurePanzoom().then((p) => {
      const rect = svg.getBoundingClientRect();
      p.smoothZoom(rect.width / 2, rect.height / 2, factor);
    });

    const reset = () => {
      if (pz) { pz.dispose(); pz = null; }
      svg.style.transform = "";
    };

    const fullscreen = () => {
      if (document.fullscreenElement === container) {
        document.exitFullscreen();
      } else {
        container.requestFullscreen().catch(() => {});
      }
    };

    toolbar.appendChild(mkBtn("+", "Zoom in", () => zoomBy(1.4)));
    toolbar.appendChild(mkBtn("−", "Zoom out", () => zoomBy(0.7)));
    toolbar.appendChild(mkBtn("↻", "Reset", reset));
    toolbar.appendChild(mkBtn("⛶", "Fullscreen", fullscreen));

    container.appendChild(toolbar);
  }

  function scan() {
    document.querySelectorAll(".mermaid > svg, pre.mermaid > svg").forEach(enhance);
  }

  // Mermaid renders async; observe DOM until SVGs appear, then stop.
  function watch() {
    scan();
    const obs = new MutationObserver(() => scan());
    obs.observe(document.body, { childList: true, subtree: true });
    // Stop observing after 15s to keep things light.
    setTimeout(() => obs.disconnect(), 15000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", watch);
  } else {
    watch();
  }
})();
