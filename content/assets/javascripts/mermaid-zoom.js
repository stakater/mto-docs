(function () {
  let dialog = null;
  let stage = null;
  let scaleEl = null;
  let scale = 1;
  let panX = 0;
  let panY = 0;
  let dragging = false;
  let dragStart = null;

  function buildDialog() {
    dialog = document.createElement("dialog");
    dialog.className = "mermaid-zoom-dialog";

    const toolbar = document.createElement("div");
    toolbar.className = "mermaid-zoom-dialog-toolbar";

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

    toolbar.appendChild(mkBtn("+", "Zoom in", () => zoom(1.25)));
    toolbar.appendChild(mkBtn("−", "Zoom out", () => zoom(0.8)));
    toolbar.appendChild(mkBtn("↻", "Reset", reset));
    toolbar.appendChild(mkBtn("✕", "Close", () => dialog.close()));

    stage = document.createElement("div");
    stage.className = "mermaid-zoom-dialog-stage";

    scaleEl = document.createElement("div");
    scaleEl.className = "mermaid-zoom-dialog-scale";
    stage.appendChild(scaleEl);

    dialog.appendChild(toolbar);
    dialog.appendChild(stage);

    // Close on backdrop click.
    dialog.addEventListener("click", (e) => {
      if (e.target === dialog) dialog.close();
    });

    // Wheel = zoom around cursor.
    stage.addEventListener("wheel", (e) => {
      e.preventDefault();
      const rect = stage.getBoundingClientRect();
      const cx = e.clientX - rect.left;
      const cy = e.clientY - rect.top;
      const factor = e.deltaY < 0 ? 1.15 : 0.87;
      zoomAt(cx, cy, factor);
    }, { passive: false });

    // Drag to pan.
    stage.addEventListener("mousedown", (e) => {
      dragging = true;
      dragStart = { x: e.clientX - panX, y: e.clientY - panY };
      stage.classList.add("is-dragging");
    });
    window.addEventListener("mousemove", (e) => {
      if (!dragging) return;
      panX = e.clientX - dragStart.x;
      panY = e.clientY - dragStart.y;
      applyTransform();
    });
    window.addEventListener("mouseup", () => {
      dragging = false;
      stage.classList.remove("is-dragging");
    });

    dialog.addEventListener("close", () => {
      scaleEl.innerHTML = "";
      reset();
    });

    document.body.appendChild(dialog);
  }

  function applyTransform() {
    scaleEl.style.transform = `translate(${panX}px, ${panY}px) scale(${scale})`;
  }

  function zoom(factor) {
    scale = Math.max(0.2, Math.min(10, scale * factor));
    applyTransform();
  }

  function zoomAt(cx, cy, factor) {
    const newScale = Math.max(0.2, Math.min(10, scale * factor));
    const k = newScale / scale;
    panX = cx - k * (cx - panX);
    panY = cy - k * (cy - panY);
    scale = newScale;
    applyTransform();
  }

  function reset() {
    scale = 1;
    panX = 0;
    panY = 0;
    applyTransform();
  }

  function getSvg(host) {
    if (host.shadowRoot) return host.shadowRoot.querySelector("svg");
    return host.querySelector("svg");
  }

  function openFor(host) {
    const svg = getSvg(host);
    if (!svg) return;
    if (!dialog) buildDialog();
    const clone = svg.cloneNode(true);
    // Strip any inline width/height so the SVG scales to the stage.
    clone.removeAttribute("width");
    clone.removeAttribute("height");
    clone.style.width = "auto";
    clone.style.height = "auto";
    clone.style.maxWidth = "100%";
    clone.style.maxHeight = "100%";
    scaleEl.innerHTML = "";
    scaleEl.appendChild(clone);
    reset();
    dialog.showModal();
  }

  function enhance(host) {
    if (host.dataset.zoomEnabled === "true") return;
    if (!getSvg(host)) return;
    host.dataset.zoomEnabled = "true";
    host.classList.add("mermaid-zoom-host");

    const hint = document.createElement("button");
    hint.type = "button";
    hint.className = "mermaid-zoom-open";
    hint.title = "Click to zoom";
    hint.setAttribute("aria-label", "Open diagram in zoom view");
    hint.textContent = "⤢";
    hint.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      openFor(host);
    });
    host.appendChild(hint);

    host.addEventListener("click", (e) => {
      // Don't trigger when clicking the hint button itself (handled above).
      if (e.target.closest(".mermaid-zoom-open")) return;
      openFor(host);
    });
  }

  const watchedShadows = new WeakSet();

  function scan() {
    document.querySelectorAll(".mermaid, pre.mermaid").forEach((host) => {
      if (getSvg(host)) {
        enhance(host);
      } else if (host.shadowRoot && !watchedShadows.has(host.shadowRoot)) {
        watchedShadows.add(host.shadowRoot);
        const obs = new MutationObserver(() => {
          if (getSvg(host)) {
            enhance(host);
            obs.disconnect();
          }
        });
        obs.observe(host.shadowRoot, { childList: true, subtree: true });
      }
    });
  }

  function watch() {
    scan();
    const obs = new MutationObserver(() => scan());
    obs.observe(document.body, { childList: true, subtree: true });
    let ticks = 0;
    const poll = setInterval(() => {
      scan();
      if (++ticks > 20) clearInterval(poll);
    }, 250);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", watch);
  } else {
    watch();
  }
})();
