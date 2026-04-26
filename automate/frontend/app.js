document.addEventListener("alpine:init", () => {
  Alpine.data("app", () => ({
    tabs: [
      { id: "chat",         label: "Chat" },
      { id: "models",       label: "Models" },
      { id: "integrations", label: "Tools" },
      { id: "history",      label: "History" },
      { id: "help",         label: "Help" },
    ],
    active: "chat",
    region: "",
    status: null,
    welcomeOpen: false,
    catalog: [],
    catalogById: {},
    providers: [],
    integrations: [],
    tools: [],

    editingProvider: null,
    editForm: { api_key: "", base_url: "", default_model: "" },
    testResult: null,

    editingIntegration: null,
    integrationForm: { token: "", client_id: "", client_secret: "" },

    messages: [],
    liveEvents: [],
    input: "",
    busy: false,
    ws: null,

    runs: [],

    quickPrompts: [
      "在当前目录运行 `git status` 并总结",
      "Open https://news.ycombinator.com and list the top 5 story titles",
      "Create a GitHub issue in <owner>/<repo> titled 'demo from autoMate'",
      "Take a screenshot of my desktop",
    ],

    helpExamples: [
      { kind: "shell",        text: "git status this folder and summarise what changed",
        note: "Uses shell.exec — runs from the folder where automate started." },
      { kind: "browser",      text: "Open https://news.ycombinator.com and list the top 5 story titles",
        note: "Uses browser.* (Playwright). Install Chromium first: python -m playwright install chromium" },
      { kind: "real browser", text: "Read the visible text on my active tab and summarise it",
        note: "Uses bx.* — needs the autoMate Bridge browser extension installed." },
      { kind: "github",       text: "List the 5 most recent issues in microsoft/playwright",
        note: "Uses the GitHub integration — connect it in the Tools tab first." },
      { kind: "script",       text: "Write a Python script that prints prime numbers up to 100 and run it",
        note: "Uses script.run — saves the file under ~/.automate/scripts/ for replay." },
    ],

    async init() {
      await this.refreshAll();
      this.connectWS();
      setInterval(() => this.refreshStatus(), 5000);
      // First-run welcome: auto-open if the user hasn't dismissed it yet AND
      // no provider has an API key configured.
      const dismissed = localStorage.getItem("automate-welcomed") === "1";
      if (!dismissed && this.status && this.status.providers_configured === 0) {
        this.welcomeOpen = true;
      }
    },

    dismissWelcome(jumpToModels) {
      localStorage.setItem("automate-welcomed", "1");
      this.welcomeOpen = false;
      if (jumpToModels) this.active = "models";
    },

    async refreshAll() {
      await Promise.all([
        this.refreshStatus(),
        this.loadCatalog(),
        this.loadProviders(),
        this.loadIntegrations(),
        this.loadTools(),
        this.loadRuns(),
      ]);
    },

    async refreshStatus() { this.status = await api("/api/status"); },
    async loadCatalog() {
      this.catalog = await api("/api/models/catalog");
      this.catalogById = Object.fromEntries(this.catalog.map(p => [p.id, p]));
    },
    async loadProviders() { this.providers = await api("/api/models"); },
    async loadIntegrations() { this.integrations = await api("/api/integrations"); },
    async loadTools() {
      const grouped = await api("/api/tools");
      this.tools = grouped;
    },
    async loadRuns() { this.runs = await api("/api/agent/runs"); },

    get filteredProviders() {
      if (!this.region) return this.providers;
      return this.providers.filter(p => {
        const meta = this.catalogById[p.id];
        return meta && meta.region === this.region;
      });
    },

    get groupedIntegrations() {
      const out = {};
      for (const i of this.integrations) {
        (out[i.category] ||= []).push(i);
      }
      return out;
    },

    get toolsByCategory() {
      // tools is grouped { category: [...] } already
      return this.tools || {};
    },

    get totalToolCount() {
      return Object.values(this.tools || {}).reduce((acc, arr) => acc + arr.length, 0);
    },

    // ---- providers ----
    openProvider(p) {
      this.editingProvider = p;
      this.editForm = {
        api_key: "",
        base_url: p.base_url || "",
        default_model: p.default_model || "",
      };
      this.testResult = null;
    },
    async saveProvider() {
      const id = this.editingProvider.id;
      await api(`/api/models/${id}`, "PATCH", this.editForm);
      await this.loadProviders();
      this.editingProvider = null;
    },
    async testProvider(id) {
      this.testResult = { ok: false, message: "Calling provider…" };
      try {
        // First persist any changes the user typed.
        await api(`/api/models/${id}`, "PATCH", this.editForm);
        const r = await api(`/api/models/${id}/test`, "POST");
        this.testResult = { ok: true, message: `OK · reply: ${r.reply}` };
      } catch (e) {
        this.testResult = { ok: false, message: e.message };
      }
    },
    async setActive(id) {
      const meta = this.catalogById[id];
      const prov = this.providers.find(p => p.id === id);
      await api("/api/models/active", "POST", {
        provider_id: id,
        model: prov?.default_model || meta?.models?.[0],
      });
      await this.refreshStatus();
    },

    // ---- integrations ----
    openIntegration(i) {
      this.editingIntegration = i;
      const meta = i.metadata || {};
      this.integrationForm = {
        token: "",
        client_id: meta.client_id || "",
        client_secret: "",
      };
    },
    async connectApiKey() {
      const id = this.editingIntegration.id;
      await api(`/api/integrations/${id}/apikey`, "POST", { token: this.integrationForm.token });
      await this.loadIntegrations();
      await this.loadTools();
      this.editingIntegration = null;
    },
    async saveOAuthApp() {
      const id = this.editingIntegration.id;
      await api(`/api/integrations/${id}/oauth-app`, "POST", {
        client_id: this.integrationForm.client_id,
        client_secret: this.integrationForm.client_secret,
      });
      await this.loadIntegrations();
    },
    async beginOAuth() {
      // Persist credentials first (in case the user typed without clicking Save).
      if (this.integrationForm.client_id && this.integrationForm.client_secret) {
        await this.saveOAuthApp();
      }
      const id = this.editingIntegration.id;
      const r = await api(`/api/integrations/${id}/connect`);
      window.open(r.authorize_url, "_blank", "width=600,height=720");
    },
    async disconnect() {
      const id = this.editingIntegration.id;
      await api(`/api/integrations/${id}/disconnect`, "POST");
      await this.loadIntegrations();
      this.editingIntegration = null;
    },

    // ---- chat ----
    connectWS() {
      const proto = location.protocol === "https:" ? "wss" : "ws";
      this.ws = new WebSocket(`${proto}://${location.host}/api/sessions/ws`);
      this.ws.onmessage = (e) => {
        const ev = JSON.parse(e.data);
        if (ev.kind === "done") { this.busy = false; this.loadRuns(); return; }
        if (ev.kind === "final") {
          this.messages.push({ role: "assistant", text: ev.payload.text });
          this.liveEvents = [];
          this.$nextTick(() => this.scrollChat());
          return;
        }
        if (ev.kind === "error") {
          this.messages.push({ role: "assistant", text: "⚠ " + ev.payload.message });
          this.liveEvents = [];
          this.busy = false;
          return;
        }
        this.liveEvents.push(ev);
        this.$nextTick(() => this.scrollChat());
      };
      this.ws.onclose = () => setTimeout(() => this.connectWS(), 1500);
    },
    scrollChat() {
      const el = this.$refs.chatScroll;
      if (el) el.scrollTop = el.scrollHeight;
    },
    send() {
      if (!this.input.trim() || this.busy) return;
      const prompt = this.input.trim();
      this.messages.push({ role: "user", text: prompt });
      this.input = "";
      this.liveEvents = [];
      this.busy = true;
      this.ws.send(JSON.stringify({ prompt }));
    },
  }));
});

async function api(path, method = "GET", body) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const r = await fetch(path, opts);
  if (!r.ok) {
    let msg = await r.text();
    try { msg = JSON.parse(msg).detail || msg; } catch {}
    throw new Error(`${r.status}: ${msg}`);
  }
  if (r.status === 204) return null;
  return r.json();
}
