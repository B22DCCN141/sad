(function () {
  const AI_API = "http://localhost:8000/api/ai";

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function formatPrice(value) {
    if (value === null || value === undefined || value === "") {
      return "Đang cập nhật";
    }
    const numberValue = Number(value);
    if (!Number.isFinite(numberValue) || numberValue <= 0) {
      return "Đang cập nhật";
    }
    return numberValue.toLocaleString("vi-VN") + "đ";
  }

  function getCatalogItems() {
    if (Array.isArray(window.__BOOKSTORE_CATALOG__)) return window.__BOOKSTORE_CATALOG__;
    return [];
  }

  function getLookup() {
    if (typeof window.__BOOKSTORE_CATALOG_LOOKUP__ === "function") {
      return window.__BOOKSTORE_CATALOG_LOOKUP__;
    }
    const catalog = getCatalogItems();
    return function (productId) {
      return catalog.find((item) => String(item.id) === String(productId));
    };
  }

  function fallbackImage(text) {
    const safeText = escapeHtml(String(text || "Product").slice(0, 28));
    const svg = `
      <svg xmlns="http://www.w3.org/2000/svg" width="600" height="800" viewBox="0 0 600 800">
        <defs>
          <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#0f172a"/>
            <stop offset="100%" stop-color="#334155"/>
          </linearGradient>
        </defs>
        <rect width="600" height="800" fill="url(#g)"/>
        <rect x="86" y="108" width="428" height="584" rx="30" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.14)"/>
        <text x="50%" y="44%" text-anchor="middle" font-family="Arial, sans-serif" font-size="30" font-weight="700" fill="#ffffff">Bookstore</text>
        <text x="50%" y="53%" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" fill="#cbd5e1">${safeText}</text>
        <text x="50%" y="89%" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#e2e8f0">No image</text>
      </svg>`;
    return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
  }

  function resolveCard(card) {
    const item = getLookup()(card.product_id);
    const parsedPrice = item?.price !== undefined && item?.price !== null ? Number(item.price) : null;
    return {
      id: card.product_id,
      name: item?.name || `Sản phẩm #${card.product_id}`,
      subtitle: item?.subtitle || card.reason || "Từ KB_Graph",
      price: Number.isFinite(parsedPrice) && parsedPrice > 0 ? parsedPrice : null,
      image: item?.image_url || fallbackImage(item?.name || `#${card.product_id}`),
      detailUrl: item?.detailUrl || "#",
      typeLabel: item?.typeLabel || "AI",
      reason: card.reason,
      score: card.score,
    };
  }

  function renderCards(container, cards, emptyText) {
    if (!container) return;
    if (!cards || !cards.length) {
      container.innerHTML = `<div class="rounded-2xl border border-dashed border-slate-300 bg-white/80 p-5 text-slate-500 italic">${escapeHtml(emptyText || "Chưa có gợi ý.")}</div>`;
      return;
    }

    container.innerHTML = cards
      .map((card) => {
        const item = resolveCard(card);
        return `
          <div class="group overflow-hidden rounded-2xl border border-white/10 bg-slate-900/90 text-white shadow-2xl transition hover:-translate-y-1 hover:shadow-cyan-500/20">
            <div class="grid grid-cols-[92px_1fr] gap-4 p-4">
              <div class="h-24 w-24 overflow-hidden rounded-xl border border-white/10 bg-slate-800">
                <img src="${escapeHtml(item.image)}" alt="${escapeHtml(item.name)}" class="h-full w-full object-cover" onerror="this.onerror=null;this.src='${fallbackImage('Product')}'">
              </div>
              <div class="min-w-0">
                <div class="flex items-center justify-between gap-3">
                  <span class="inline-flex rounded-full bg-cyan-400/20 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide text-cyan-200">${escapeHtml(item.typeLabel)}</span>
                  <span class="text-[11px] text-slate-400">score ${Number(item.score || 0).toFixed(2)}</span>
                </div>
                <h4 class="mt-2 truncate text-lg font-extrabold text-white">${escapeHtml(item.name)}</h4>
                <p class="mt-1 line-clamp-2 text-sm text-slate-300">${escapeHtml(item.subtitle)}</p>
                <div class="mt-3 flex items-center justify-between gap-3">
                  <span class="text-base font-black text-amber-300">${formatPrice(item.price)}</span>
                  <button class="ai-open-product rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-white/10" data-product-id="${escapeHtml(item.id)}">Xem chi tiết</button>
                </div>
                <div class="mt-2 text-[11px] uppercase tracking-[0.18em] text-cyan-200/80">${escapeHtml(item.reason || "KB_Graph suggestion")}</div>
              </div>
            </div>
          </div>
        `;
      })
      .join("");

    container.querySelectorAll(".ai-open-product").forEach((button) => {
      button.addEventListener("click", () => {
        const productId = button.getAttribute("data-product-id");
        const item = getLookup()(productId);
        if (item?.detailUrl && item.detailUrl !== "#") {
          window.location.href = item.detailUrl;
        }
      });
    });
  }

  async function fetchJson(path, options = {}) {
    const response = await fetch(`${AI_API}${path}`, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `HTTP ${response.status}`);
    }
    return response.json();
  }

  async function search(query) {
    const result = await fetchJson(`/search/?q=${encodeURIComponent(query || "")}&limit=8`);
    const cards = result.cards || [];
    renderCards(document.getElementById("ai-search-results"), cards, "Không có gợi ý từ KB_Graph.");

    const info = document.getElementById("ai-search-insights");
    if (info) {
      info.innerHTML = (result.insights || [])
        .map((text) => `<div class="rounded-xl bg-cyan-50 px-4 py-3 text-sm font-medium text-cyan-900">${escapeHtml(text)}</div>`)
        .join("") || `<div class="rounded-xl bg-slate-100 px-4 py-3 text-sm text-slate-500">Không có insight bổ sung.</div>`;
    }

    return result;
  }

  async function chat(message, options = {}) {
    const result = await fetchJson(`/chat/`, {
      method: "POST",
      body: JSON.stringify({ message, top_k: options.top_k || 6 }),
    });
    return result;
  }

  async function cart(payload) {
    const result = await fetchJson(`/cart/`, {
      method: "POST",
      body: JSON.stringify(payload || {}),
    });
    const container = document.getElementById("ai-cart-suggestions");
    renderCards(container, result.cards || [], "Chưa có gợi ý giỏ hàng.");

    const info = document.getElementById("ai-cart-insights");
    if (info) {
      info.innerHTML = (result.insights || [])
        .map((text) => `<div class="rounded-xl bg-amber-50 px-4 py-3 text-sm font-medium text-amber-900">${escapeHtml(text)}</div>`)
        .join("") || `<div class="rounded-xl bg-slate-100 px-4 py-3 text-sm text-slate-500">Chưa có insight giỏ hàng.</div>`;
    }

    return result;
  }

  // Chat history management
  const CHAT_STORAGE_KEY = "bookstore_chat_history";
  
  function getChatHistory() {
    try {
      const stored = localStorage.getItem(CHAT_STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (e) {
      return [];
    }
  }

  function saveChatHistory(history) {
    try {
      localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(history));
    } catch (e) {
      console.warn("Failed to save chat history:", e);
    }
  }

  function addChatMessage(role, text, cards = null) {
    const history = getChatHistory();
    history.push({ role, text, cards, timestamp: new Date().toISOString() });
    // Keep only last 50 messages
    if (history.length > 50) {
      history.shift();
    }
    saveChatHistory(history);
    return history;
  }

  function createChatDock() {
    if (document.getElementById("ai-dock-root")) return;

    const root = document.createElement("div");
    root.id = "ai-dock-root";
    root.innerHTML = `
      <div id="ai-dock-launcher" class="fixed bottom-5 right-5 z-[160] flex cursor-pointer items-center gap-3 rounded-full border border-white/10 bg-slate-950/90 px-4 py-3 text-white shadow-2xl shadow-slate-900/30 backdrop-blur-md transition hover:scale-[1.02]">
        <span class="flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 via-sky-500 to-indigo-600 shadow-lg shadow-cyan-500/30">
          <i class="fas fa-robot text-xl"></i>
        </span>
        <span class="hidden text-sm font-bold tracking-wide sm:block">AI Chat</span>
        <span class="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-400 text-[10px] font-black text-slate-950 shadow-sm">ON</span>
      </div>
      <div id="ai-dock-panel" class="fixed bottom-24 right-5 z-[160] hidden h-[78vh] max-h-[820px] min-h-[440px] w-[680px] max-w-[calc(100vw-2rem)] overflow-hidden rounded-[28px] border border-white/10 bg-slate-950/95 text-white shadow-[0_30px_80px_rgba(15,23,42,0.55)] backdrop-blur-xl flex flex-col">
        <div class="border-b border-white/10 bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 p-4 flex-shrink-0">
          <div class="flex items-center justify-between gap-3">
            <div>
              <div class="text-[11px] uppercase tracking-[0.35em] text-cyan-200/90">Bookstore AI</div>
              <div class="mt-1 text-lg font-black">Robot Concierge</div>
            </div>
            <div class="flex items-center gap-2">
              <button id="ai-clear-history" class="rounded-full bg-white/10 px-3 py-2 text-xs font-semibold hover:bg-red-500/20 text-red-200" title="Xóa lịch sử chat">
                <i class="fas fa-trash-alt"></i>
              </button>
              <button id="ai-dock-close" class="rounded-full bg-white/10 px-3 py-2 text-xs font-semibold hover:bg-white/20">Đóng</button>
            </div>
          </div>
        </div>
        <div id="ai-chat-stream" class="flex-1 min-h-0 space-y-3 overflow-y-auto overscroll-y-contain p-4"></div>
        <div class="border-t border-white/10 p-4 flex-shrink-0 space-y-3">
          <div class="flex flex-wrap gap-2">
            <button class="ai-chip rounded-full bg-white/10 px-3 py-1.5 text-xs font-semibold hover:bg-white/20" data-q="gợi ý sản phẩm hot nhất">Top hot</button>
            <button class="ai-chip rounded-full bg-white/10 px-3 py-1.5 text-xs font-semibold hover:bg-white/20" data-q="khách hàng đang click gì nhiều">Xu hướng click</button>
            <button class="ai-chip rounded-full bg-white/10 px-3 py-1.5 text-xs font-semibold hover:bg-white/20" data-q="gợi ý add_to_cart">Mua tiếp</button>
          </div>
          <div class="flex gap-2">
            <input id="ai-chat-input" type="text" placeholder="Hỏi AI về sản phẩm, hành vi, giỏ hàng..." class="min-w-0 flex-1 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm outline-none placeholder:text-slate-400 focus:border-cyan-400/60">
            <button id="ai-chat-send" class="rounded-2xl bg-gradient-to-r from-cyan-400 to-indigo-500 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-cyan-500/20">Gửi</button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(root);

    const launcher = document.getElementById("ai-dock-launcher");
    const panel = document.getElementById("ai-dock-panel");
    const closeButton = document.getElementById("ai-dock-close");
    const clearButton = document.getElementById("ai-clear-history");
    const input = document.getElementById("ai-chat-input");
    const send = document.getElementById("ai-chat-send");
    const stream = document.getElementById("ai-chat-stream");

    function appendMessage(role, text, cards) {
      const bubble = document.createElement("div");
      bubble.className = role === "user" ? "ml-8 rounded-2xl rounded-br-md bg-cyan-500/15 border border-cyan-300/20 p-3 text-sm text-cyan-50" : "mr-8 rounded-2xl rounded-bl-md bg-white/8 border border-white/10 p-3 text-sm text-slate-100";
      bubble.innerHTML = `<div class="text-[11px] uppercase tracking-[0.25em] font-bold ${role === 'user' ? 'text-cyan-200' : 'text-cyan-400'}">${role === 'user' ? '👤 Bạn' : '🤖 AI Robot'}</div><div class="mt-2 whitespace-pre-line leading-6">${escapeHtml(text)}</div>`;
      stream.appendChild(bubble);

      // Show answer first, then products below
      if (cards && cards.length) {
        const cardsWrap = document.createElement("div");
        cardsWrap.className = "space-y-3 mt-3";
        cardsWrap.innerHTML = `<div class="mx-8 text-[11px] uppercase tracking-[0.25em] text-cyan-300/90 font-semibold">📦 Sản phẩm liên quan</div>`;
        const inner = document.createElement("div");
        inner.className = "space-y-3";
        cardsWrap.appendChild(inner);
        stream.appendChild(cardsWrap);
        renderCards(inner, cards, "");
      }

      stream.scrollTop = stream.scrollHeight;
    }

    function loadChatHistory() {
      const history = getChatHistory();
      stream.innerHTML = "";
      
      if (history.length === 0) {
        appendMessage("assistant", "Tôi có thể gợi ý sản phẩm từ KB_Graph, giải thích hành vi người dùng, hoặc phân tích giỏ hàng theo ngữ cảnh.");
      } else {
        history.forEach((msg) => {
          appendMessage(msg.role, msg.text, msg.cards);
        });
      }
    }

    async function handleSend(query) {
      const text = (query || input.value || "").trim();
      if (!text) return;
      input.value = "";
      appendMessage("user", text);
      addChatMessage("user", text);
      
      try {
        const result = await chat(text);
        const answer = result.answer || "Không có phản hồi.";
        const cards = result.cards || [];
        appendMessage("assistant", answer, cards);
        addChatMessage("assistant", answer, cards);
      } catch (error) {
        const errorMsg = `Lỗi khi kết nối AI: ${error.message}`;
        appendMessage("assistant", errorMsg);
        addChatMessage("assistant", errorMsg);
      }
    }

    launcher.addEventListener("click", () => {
      panel.classList.toggle("hidden");
      if (!panel.classList.contains("hidden")) {
        input.focus();
        // Reload history each time panel opens
        loadChatHistory();
      }
    });
    
    closeButton.addEventListener("click", () => panel.classList.add("hidden"));
    
    clearButton.addEventListener("click", () => {
      if (confirm("Bạn có chắc muốn xóa toàn bộ lịch sử chat?")) {
        localStorage.removeItem(CHAT_STORAGE_KEY);
        stream.innerHTML = "";
        appendMessage("assistant", "Lịch sử chat đã được xóa. Tôi có thể gợi ý sản phẩm từ KB_Graph, giải thích hành vi người dùng, hoặc phân tích giỏ hàng theo ngữ cảnh.");
      }
    });
    
    send.addEventListener("click", () => handleSend());
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") handleSend();
    });
    panel.querySelectorAll(".ai-chip").forEach((chip) => {
      chip.addEventListener("click", () => handleSend(chip.getAttribute("data-q")));
    });

    // Load initial history
    loadChatHistory();
  }

  function bindSearchControls() {
    const input = document.getElementById("ai-search-input");
    const button = document.getElementById("ai-search-button");
    if (input && button) {
      const runSearch = () => search(input.value);
      button.addEventListener("click", runSearch);
      input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") runSearch();
      });
    }
  }

  function bindCartInsights() {
    const payload = window.__BOOKSTORE_CART_AI_PAYLOAD__;
    if (!payload || !document.getElementById("ai-cart-suggestions")) return;
    cart(payload).catch(() => {
      const info = document.getElementById("ai-cart-insights");
      if (info) {
        info.innerHTML = `<div class="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">Không tải được gợi ý AI giỏ hàng.</div>`;
      }
    });
  }

  function init() {
    createChatDock();
    bindSearchControls();
    bindCartInsights();
  }

  window.BookstoreAI = {
    init,
    search,
    chat,
    cart,
    renderCards,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
