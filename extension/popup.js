const $ = (id) => document.getElementById(id);

function refresh() {
  chrome.runtime.sendMessage({ type: "status" }, (r) => {
    if (!r) return;
    $("dot").classList.toggle("on", r.connected);
    $("row-status").textContent = r.connected ? "Connected to autoMate" : "Disconnected — autoMate not running?";
    if (!$("url").value) $("url").value = r.url;
  });
}

$("save").addEventListener("click", () => {
  const url = $("url").value.trim() || "ws://127.0.0.1:8765/api/extension/ws";
  chrome.runtime.sendMessage({ type: "setServerUrl", url }, () => setTimeout(refresh, 400));
});

refresh();
setInterval(refresh, 1500);
