// Runs in every page; resolves CSS / text= selectors and performs DOM actions.

(function () {
  if (window.__automateContentLoaded) return;
  window.__automateContentLoaded = true;

  function resolve(selector) {
    if (!selector) return null;
    if (selector.startsWith("text=")) {
      const needle = selector.slice(5).toLowerCase();
      const all = document.querySelectorAll("a,button,input,label,span,div,li,td,th,h1,h2,h3,h4,h5,h6,p");
      for (const el of all) {
        const t = (el.innerText || el.value || "").trim().toLowerCase();
        if (t && t.includes(needle)) return el;
      }
      return null;
    }
    return document.querySelector(selector);
  }

  function resolveAll(selector, limit) {
    if (!selector) return [];
    if (selector.startsWith("text=")) {
      const el = resolve(selector);
      return el ? [el] : [];
    }
    return Array.from(document.querySelectorAll(selector)).slice(0, limit);
  }

  function setNativeValue(el, value) {
    const proto = Object.getPrototypeOf(el);
    const setter = Object.getOwnPropertyDescriptor(proto, "value")?.set;
    if (setter) setter.call(el, value);
    else el.value = value;
  }

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    (async () => {
      try {
        const out = await handle(msg);
        sendResponse(out);
      } catch (e) {
        sendResponse({ __error: String(e?.message || e) });
      }
    })();
    return true; // async
  });

  async function handle({ cmd, args }) {
    if (cmd === "dom.click") {
      const el = resolve(args.selector);
      if (!el) throw new Error(`no element matches: ${args.selector}`);
      el.scrollIntoView({ block: "center" });
      el.click();
      return { clicked: args.selector, url: location.href };
    }

    if (cmd === "dom.type") {
      const el = resolve(args.selector);
      if (!el) throw new Error(`no element matches: ${args.selector}`);
      el.focus();
      setNativeValue(el, args.text);
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
      if (args.submit) {
        el.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", code: "Enter", which: 13, keyCode: 13, bubbles: true }));
        const form = el.closest && el.closest("form");
        if (form) form.requestSubmit?.();
      }
      return { typed: args.selector, value_length: args.text.length };
    }

    if (cmd === "dom.extract") {
      const { selector, kind = "text", limit = 50 } = args;
      if (kind === "meta") {
        return {
          title: document.title,
          url: location.href,
          description:
            document.querySelector('meta[name=description]')?.content ||
            document.querySelector('meta[property="og:description"]')?.content || "",
        };
      }
      if (!selector) {
        return { url: location.href, title: document.title, text: document.body.innerText.slice(0, 8000) };
      }
      const els = resolveAll(selector, limit);
      if (kind === "html") return { items: els.map(e => e.outerHTML) };
      if (kind === "links") return { items: els.map(e => e.href || e.getAttribute("href")).filter(Boolean) };
      return { items: els.map(e => (e.innerText || e.value || "").trim()) };
    }

    if (cmd === "dom.scroll") {
      const { direction = "down", amount = 600 } = args;
      if (direction === "top") window.scrollTo({ top: 0, behavior: "instant" });
      else if (direction === "bottom") window.scrollTo({ top: document.body.scrollHeight, behavior: "instant" });
      else if (direction === "up") window.scrollBy({ top: -amount, behavior: "instant" });
      else window.scrollBy({ top: amount, behavior: "instant" });
      return { y: window.scrollY };
    }

    throw new Error(`content.js does not handle: ${cmd}`);
  }
})();
