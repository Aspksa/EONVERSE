// Browser key entry. Nothing is stored in localStorage, the page URL, or world saves.
const keyInput = document.getElementById("cloud-key");
const status = document.getElementById("cloud-status");
const headers = {"Content-Type": "application/json", "X-Eonverse-Local-Settings": "1"};

async function request(path, options = {}) {
  const res = await fetch(path, {credentials: "same-origin", cache: "no-store",
    headers, ...options});
  if (!res.ok) throw new Error(res.status === 403
    ? "Настройки доступны только через localhost на этом компьютере."
    : "Сервер отказал в подключении (" + res.status + ").");
  return res.json();
}
function show(state) {
  status.textContent = state.enabled
    ? "Cloud.ru настроен и включён"
    : "ИИ отключён. Симуляция работает без Cloud.ru.";
}
async function refresh() {
  try { show(await request("/api/local/cloud/status")); }
  catch (err) { status.textContent = err.message; }
}
document.getElementById("cloud-save").addEventListener("click", async () => {
  const key = keyInput.value.trim();
  if (key.length < 8) { status.textContent = "Введите действительный API-ключ."; return; }
  status.textContent = "Сохраняю ключ в памяти локального сервера...";
  try {
    const state = await request("/api/local/cloud/configure", {
      method: "POST", body: JSON.stringify({key, model: "DeepSeek-V4-Flash"})
    });
    keyInput.value = "";
    show(state);
  } catch (err) { status.textContent = err.message; }
});
document.getElementById("cloud-disconnect").addEventListener("click", async () => {
  try { show(await request("/api/local/cloud/disconnect", {method: "POST"})); }
  catch (err) { status.textContent = err.message; }
});
refresh();
