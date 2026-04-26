// autoMate Bridge — service worker.
//
// Holds a WebSocket to the local autoMate server and dispatches commands to
// chrome.tabs / chrome.scripting / the content script. Auto-reconnects with
// exponential backoff. The keep-alive alarm prevents Manifest V3 from
// suspending the worker mid-call.

const DEFAULT_URL = "ws://127.0.0.1:8765/api/extension/ws";
let ws = null;
let backoff = 1000;
let serverUrl = DEFAULT_URL;

chrome.storage.local.get(["serverUrl"], ({ serverUrl: u }) => {
  if (u) serverUrl = u;
  connect();
});

chrome.alarms.create("keepalive", { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener((a) => {
  if (a.name === "keepalive" && ws?.readyState !== WebSocket.OPEN) connect();
});

function connect() {
  try { ws?.close(); } catch {}
  try {
    ws = new WebSocket(serverUrl);
  } catch (e) {
    scheduleReconnect();
    return;
  }
  ws.onopen = () => {
    backoff = 1000;
    ws.send(JSON.stringify({ hello: "automate-extension", version: "1.0.0", agent: navigator.userAgent }));
    setBadge("ON", "#10b981");
    chrome.storage.local.set({ status: "connected", lastConnectedAt: Date.now() });
  };
  ws.onmessage = async (ev) => {
    let msg;
    try { msg = JSON.parse(ev.data); } catch { return; }
    if (msg.hello) return;
    const { id, cmd, args } = msg;
    try {
      const result = await dispatch(cmd, args || {});
      ws.send(JSON.stringify({ id, ok: true, result }));
    } catch (e) {
      ws.send(JSON.stringify({ id, ok: false, error: String(e?.message || e) }));
    }
  };
  ws.onclose = () => {
    setBadge("OFF", "#9ca3af");
    chrome.storage.local.set({ status: "disconnected" });
    scheduleReconnect();
  };
  ws.onerror = () => { try { ws.close(); } catch {} };
}

function scheduleReconnect() {
  setTimeout(connect, backoff);
  backoff = Math.min(backoff * 2, 30000);
}

function setBadge(text, color) {
  chrome.action.setBadgeText({ text });
  chrome.action.setBadgeBackgroundColor({ color });
}

// ============== command dispatch ==============

async function activeTab() {
  const [tab] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
  if (!tab) throw new Error("no active tab");
  return tab;
}

async function dispatch(cmd, args) {
  switch (cmd) {
    case "tabs.list": {
      const tabs = await chrome.tabs.query({});
      return tabs.map(t => ({ id: t.id, title: t.title, url: t.url, active: t.active, windowId: t.windowId }));
    }
    case "tabs.open": {
      const tab = await chrome.tabs.create({ url: args.url, active: args.active !== false });
      return { id: tab.id, url: tab.url };
    }
    case "tabs.activate": {
      await chrome.tabs.update(args.tab_id, { active: true });
      return { ok: true };
    }
    case "tabs.close": {
      await chrome.tabs.remove(args.tab_id);
      return { ok: true };
    }
    case "tabs.navigate": {
      const tabId = args.tab_id ?? (await activeTab()).id;
      await chrome.tabs.update(tabId, { url: args.url });
      await waitForLoad(tabId);
      return { id: tabId };
    }
    case "tabs.screenshot": {
      const tab = await activeTab();
      const dataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, { format: "png" });
      const base64 = dataUrl.split(",")[1];
      return { format: "png", base64 };
    }
    case "dom.click":
    case "dom.type":
    case "dom.extract":
    case "dom.scroll":
      return await viaContent(cmd, args);
    case "dom.eval": {
      const tab = await activeTab();
      const [{ result }] = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        world: "MAIN",
        func: (expr) => {
          try { return { ok: true, value: eval(expr) }; }
          catch (e) { return { ok: false, error: String(e?.message || e) }; }
        },
        args: [args.expression],
      });
      if (!result?.ok) throw new Error(result?.error || "eval failed");
      try { return JSON.parse(JSON.stringify(result.value)); }
      catch { return String(result.value); }
    }
    default:
      throw new Error(`unknown cmd: ${cmd}`);
  }
}

async function viaContent(cmd, args) {
  const tab = await activeTab();
  // Re-inject content.js if the tab predates the extension install.
  try {
    await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["content.js"] });
  } catch {}
  return await chrome.tabs.sendMessage(tab.id, { cmd, args });
}

function waitForLoad(tabId, timeout = 10000) {
  return new Promise((resolve) => {
    const t = setTimeout(() => { chrome.tabs.onUpdated.removeListener(handler); resolve(); }, timeout);
    function handler(id, info) {
      if (id === tabId && info.status === "complete") {
        clearTimeout(t);
        chrome.tabs.onUpdated.removeListener(handler);
        resolve();
      }
    }
    chrome.tabs.onUpdated.addListener(handler);
  });
}

// Popup → background messages (e.g. server URL change)
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "setServerUrl") {
    serverUrl = msg.url;
    chrome.storage.local.set({ serverUrl }, () => {
      try { ws?.close(); } catch {}
      connect();
      sendResponse({ ok: true });
    });
    return true;
  }
  if (msg?.type === "status") {
    sendResponse({
      connected: ws?.readyState === WebSocket.OPEN,
      url: serverUrl,
    });
    return true;
  }
});
