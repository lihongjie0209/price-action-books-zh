/* GitBook-style bilingual optional reader */
(function () {
  const CATALOG_URL = "catalog.json";

  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];

  function params() {
    return new URLSearchParams(location.search);
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function loadCatalog() {
    const res = await fetch(CATALOG_URL, { cache: "no-cache" });
    if (!res.ok) throw new Error("无法加载 catalog.json");
    return res.json();
  }

  function bookById(catalog, id) {
    return (catalog.books || []).find((b) => b.id === id || b.slug === id);
  }

  /** Flatten hierarchical toc pages in order */
  function flattenPages(toc) {
    const out = [];
    const walk = (nodes) => {
      for (const n of nodes || []) {
        if (n.type === "page") out.push(n);
        else if (n.children) walk(n.children);
      }
    };
    walk(toc || []);
    return out;
  }

  function findPageMeta(book, chapterId) {
    const pages = flattenPages(book.toc);
    return pages.find((p) => p.id === chapterId) || null;
  }

  function findGroupPath(toc, chapterId, trail = []) {
    for (const n of toc || []) {
      if (n.type === "page" && n.id === chapterId) return trail;
      if (n.type === "group") {
        const found = findGroupPath(n.children, chapterId, trail.concat(n));
        if (found) return found;
      }
    }
    return null;
  }

  function rewriteMdAssets(md, bookPath) {
    return md
      .replace(/\]\((\.\.\/)+assets\/figures\//g, `](${bookPath}/assets/figures/`)
      .replace(/\]\(assets\/figures\//g, `](${bookPath}/assets/figures/`);
  }

  async function fetchText(url) {
    const res = await fetch(url, { cache: "no-cache" });
    if (!res.ok) throw new Error(`加载失败 ${url} (${res.status})`);
    return res.text();
  }

  function getMarked() {
    // UMD build exposes window.marked as the API object (has .parse)
    // Some builds also set marked.marked
    const m = typeof marked !== "undefined" ? marked : null;
    if (!m) return null;
    if (typeof m.parse === "function") return m;
    if (m.marked && typeof m.marked.parse === "function") return m.marked;
    if (typeof m === "function") return { parse: m, setOptions: m.setOptions?.bind(m) };
    return null;
  }

  function renderMarkdown(md, bookPath) {
    const fixed = rewriteMdAssets(md, bookPath);
    const m = getMarked();
    if (!m) {
      console.error("marked.js failed to load; showing plain text fallback");
      return `<pre class="md-fallback whitespace-pre-wrap text-sm text-slate-800">${escapeHtml(fixed)}</pre>`;
    }
    if (typeof m.setOptions === "function") {
      m.setOptions({ gfm: true, breaks: false });
    }
    return m.parse(fixed);
  }

  /* ---------- Home ---------- */
  async function initHome() {
    const grid = $("#book-grid");
    if (!grid) return;
    try {
      const catalog = await loadCatalog();
      grid.innerHTML = "";
      for (const b of catalog.books || []) {
        const a = document.createElement("a");
        a.href = `reader.html?book=${encodeURIComponent(b.id)}`;
        a.className =
          "group block rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-blue-300 hover:shadow-md";
        a.innerHTML = `
          <div class="flex items-start justify-between gap-3">
            <div>
              <h3 class="text-lg font-semibold text-slate-900 group-hover:text-blue-700">${escapeHtml(b.title_zh || b.title_en)}</h3>
              <p class="mt-1 text-sm text-slate-500">${escapeHtml(b.title_en || "")}</p>
            </div>
            <span class="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">阅读</span>
          </div>
          <p class="mt-3 text-sm leading-relaxed text-slate-600">${escapeHtml(b.description_zh || b.description_en || "")}</p>
          <div class="mt-4 flex flex-wrap gap-2 text-xs text-slate-500">
            <span class="rounded-full bg-slate-100 px-2 py-0.5">${b.chapter_count || flattenPages(b.toc).length} 篇</span>
            <span class="rounded-full bg-slate-100 px-2 py-0.5">${b.figure_count || 0} 图</span>
            <span>${escapeHtml(b.author || "")}</span>
          </div>`;
        grid.appendChild(a);
      }
    } catch (e) {
      grid.innerHTML = `<p class="text-red-600">${escapeHtml(e.message)}</p>`;
    }
  }

  /* ---------- Reader ---------- */
  let state = {
    book: null,
    pages: [],
    chapterId: "",
    showEn: false,
    enLoadedFor: null,
  };

  function setSidebarOpen(open) {
    const sb = $("#sidebar");
    const ov = $("#sidebar-overlay");
    if (!sb) return;
    if (open) {
      sb.classList.remove("-translate-x-full");
      ov && ov.classList.remove("hidden");
    } else {
      sb.classList.add("-translate-x-full");
      ov && ov.classList.add("hidden");
    }
  }

  function applyBilingualUI() {
    const panels = $("#panels");
    const enPanel = $("#en-panel");
    const zhLabel = $("#zh-label");
    const toggle = $("#toggle-en");
    if (toggle) toggle.checked = state.showEn;
    if (state.showEn) {
      panels.classList.add("bilingual");
      enPanel.classList.remove("hidden");
      zhLabel.classList.remove("hidden");
    } else {
      panels.classList.remove("bilingual");
      enPanel.classList.add("hidden");
      zhLabel.classList.add("hidden");
    }
  }

  function renderToc(book, chapterId) {
    const nav = $("#toc-nav");
    const toc = book.toc || [];
    nav.innerHTML = "";

    const activeTrail = findGroupPath(toc, chapterId) || [];
    const openIds = new Set(activeTrail.map((g) => g.id));

    for (const node of toc) {
      if (node.type === "group") {
        const wrap = document.createElement("div");
        wrap.className = "toc-group mb-1" + (openIds.has(node.id) ? " open" : "");
        wrap.dataset.groupId = node.id;

        const btn = document.createElement("button");
        btn.type = "button";
        btn.innerHTML = `<span class="chev">▶</span><span class="truncate">${escapeHtml(node.title_zh || node.title_en)}</span>`;
        btn.addEventListener("click", () => {
          wrap.classList.toggle("open");
        });
        wrap.appendChild(btn);

        const kids = document.createElement("div");
        kids.className = "toc-children space-y-0.5 py-0.5";
        for (const child of node.children || []) {
          if (child.type !== "page") continue;
          const a = document.createElement("a");
          a.className = "toc-page" + (child.id === chapterId ? " active" : "");
          a.href = readerUrl(book.id, child.id, state.showEn);
          a.textContent = child.title_zh || child.title_en;
          a.dataset.id = child.id;
          kids.appendChild(a);
        }
        wrap.appendChild(kids);
        nav.appendChild(wrap);
      } else if (node.type === "page") {
        const a = document.createElement("a");
        a.className = "toc-page mb-0.5" + (node.id === chapterId ? " active" : "");
        a.href = readerUrl(book.id, node.id, state.showEn);
        a.textContent = node.title_zh || node.title_en;
        nav.appendChild(a);
      }
    }
  }

  function readerUrl(bookId, chId, showEn) {
    const u = new URL("reader.html", location.href);
    u.searchParams.set("book", bookId);
    u.searchParams.set("ch", chId);
    if (showEn) u.searchParams.set("en", "1");
    else u.searchParams.delete("en");
    return u.pathname.split("/").pop() + u.search;
  }

  function updateNavLinks(book, chapterId) {
    const pages = state.pages;
    const idx = pages.findIndex((p) => p.id === chapterId);
    const bind = (el, target) => {
      if (!el) return;
      if (!target) {
        el.hidden = true;
        el.removeAttribute("href");
      } else {
        el.hidden = false;
        el.href = readerUrl(book.id, target.id, state.showEn);
      }
    };
    const prev = idx > 0 ? pages[idx - 1] : null;
    const next = idx >= 0 && idx < pages.length - 1 ? pages[idx + 1] : null;
    bind($("#nav-prev"), prev);
    bind($("#nav-next"), next);
    bind($("#nav-prev-bottom"), prev);
    bind($("#nav-next-bottom"), next);
  }

  function updateCrumb(book, chapterId) {
    const trail = findGroupPath(book.toc, chapterId) || [];
    const page = findPageMeta(book, chapterId);
    const parts = trail.map((g) => g.title_zh || g.title_en);
    if (page) parts.push(page.title_zh || page.title_en);
    $("#crumb").textContent = parts.join(" / ");
    $("#chapter-title").textContent = page
      ? page.title_zh || page.title_en
      : chapterId;
  }

  async function loadChapter(book, chapterId) {
    const page = findPageMeta(book, chapterId) || (book.chapters || []).find((c) => c.id === chapterId);
    const base = book.path || `books/${book.id}`;
    const file = page?.file || `${chapterId}.md`;
    const zhEl = $("#md-zh");
    const enEl = $("#md-en");

    zhEl.innerHTML = `<p class="text-slate-500">加载中…</p>`;
    try {
      const zhMd = await fetchText(`${base}/zh/chapters/${file}`);
      zhEl.innerHTML = renderMarkdown(zhMd, base);
    } catch (e) {
      zhEl.innerHTML = `<p class="text-red-600">${escapeHtml(e.message)}</p>`;
    }

    if (state.showEn) {
      await loadEnglish(book, file);
    } else {
      enEl.innerHTML = `<p class="text-slate-400 text-sm">勾选右上角「英文对照」后加载英文原文。</p>`;
      state.enLoadedFor = null;
    }

    state.chapterId = chapterId;
    renderToc(book, chapterId);
    updateNavLinks(book, chapterId);
    updateCrumb(book, chapterId);
    // scroll content top
    const sc = $("#content-scroll");
    if (sc) sc.scrollTop = 0;
    // close mobile sidebar after nav
    if (window.matchMedia("(max-width: 1023px)").matches) setSidebarOpen(false);
  }

  async function loadEnglish(book, file) {
    const base = book.path || `books/${book.id}`;
    const enEl = $("#md-en");
    const key = `${book.id}:${file}`;
    if (state.enLoadedFor === key) return;
    enEl.innerHTML = `<p class="text-slate-500">加载英文…</p>`;
    try {
      const enMd = await fetchText(`${base}/en/chapters/${file}`);
      enEl.innerHTML = renderMarkdown(enMd, base);
      state.enLoadedFor = key;
    } catch (e) {
      enEl.innerHTML = `<p class="text-red-600">${escapeHtml(e.message)}</p>`;
    }
  }

  async function initReader() {
    const p = params();
    const bookId = p.get("book") || "trading-price-action-trends";
    let chapterId = p.get("ch") || "";
    // Default: Chinese only. en=1 enables bilingual.
    state.showEn = p.get("en") === "1" || p.get("mode") === "bilingual";

    const catalog = await loadCatalog();
    const book = bookById(catalog, bookId);
    if (!book) {
      $("#md-zh").innerHTML = `<p class="text-red-600">未找到书籍：${escapeHtml(bookId)}</p>`;
      return;
    }
    state.book = book;
    state.pages = flattenPages(book.toc).length
      ? flattenPages(book.toc)
      : (book.chapters || []).map((c) => ({
          type: "page",
          id: c.id,
          file: c.file,
          title_zh: c.title_zh,
          title_en: c.title_en,
        }));

    if (!chapterId && state.pages.length) chapterId = state.pages[0].id;

    $("#book-title").textContent = book.title_zh || book.title_en;
    $("#book-author").textContent = book.author || "";
    $("#sidebar-brand").textContent = catalog.site_title || "译丛";

    applyBilingualUI();
    await loadChapter(book, chapterId);

    // sidebar mobile
    $("#sidebar-open")?.addEventListener("click", () => setSidebarOpen(true));
    $("#sidebar-close")?.addEventListener("click", () => setSidebarOpen(false));
    $("#sidebar-overlay")?.addEventListener("click", () => setSidebarOpen(false));

    // English toggle (optional)
    $("#toggle-en")?.addEventListener("change", async (ev) => {
      state.showEn = !!ev.target.checked;
      applyBilingualUI();
      const url = new URL(location.href);
      if (state.showEn) url.searchParams.set("en", "1");
      else url.searchParams.delete("en");
      // clean legacy mode param
      url.searchParams.delete("mode");
      history.replaceState(null, "", url);
      updateNavLinks(book, state.chapterId);
      // update toc links en flag
      renderToc(book, state.chapterId);
      if (state.showEn) {
        const page = findPageMeta(book, state.chapterId);
        await loadEnglish(book, page?.file || `${state.chapterId}.md`);
      }
    });

    // keyboard
    document.addEventListener("keydown", (ev) => {
      if (ev.target.matches("input,textarea,select")) return;
      const idx = state.pages.findIndex((c) => c.id === state.chapterId);
      if ((ev.key === "]" || ev.key === "ArrowRight") && idx < state.pages.length - 1) {
        location.href = readerUrl(book.id, state.pages[idx + 1].id, state.showEn);
      } else if ((ev.key === "[" || ev.key === "ArrowLeft") && idx > 0) {
        location.href = readerUrl(book.id, state.pages[idx - 1].id, state.showEn);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    const page = document.body.dataset.page;
    if (page === "home") initHome();
    if (page === "reader") {
      initReader().catch((e) => {
        const el = $("#md-zh") || document.body;
        el.innerHTML = `<p class="text-red-600 p-6">${escapeHtml(e.message)}</p>`;
      });
    }
  });
})();
