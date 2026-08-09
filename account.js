const authCard = document.querySelector("#authCard");
const authLoading = document.querySelector("#authLoading");
const authForms = document.querySelector("#authForms");
const accountDashboard = document.querySelector("#accountDashboard");
const authError = document.querySelector("#authError");
const nextParam = new URLSearchParams(window.location.search).get("next") || "";
const safeNext = nextParam.startsWith("/") && !nextParam.startsWith("//") ? nextParam : "builder.html";

async function api(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers: { "content-type": "application/json", ...(options.headers || {}) },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error?.message || "Something went wrong. Please try again.");
  return data;
}

function setSubmitting(form, submitting) {
  const button = form.querySelector('button[type="submit"]');
  if (!button) return;
  if (!button.dataset.label) button.dataset.label = button.textContent;
  button.disabled = submitting;
  button.textContent = submitting ? "Please wait…" : button.dataset.label;
}

function showDashboard(user) {
  authLoading.hidden = true;
  authForms.hidden = true;
  accountDashboard.hidden = false;
  document.querySelector("#dashboardName").textContent = `Hello, ${user.name.split(" ")[0]}`;
  document.querySelector("#dashboardEmail").textContent = user.email;
  document.querySelector("#dashboardCredits").textContent = String(user.downloadCredits || 0);
  document.querySelector("#continueEditing").href = safeNext;
}

function showForms() {
  authLoading.hidden = true;
  accountDashboard.hidden = true;
  authForms.hidden = false;
}

function selectTab(tab) {
  document.querySelectorAll("[data-auth-tab]").forEach((button) => button.classList.toggle("active", button.dataset.authTab === tab));
  document.querySelector("#loginForm").hidden = tab !== "login";
  document.querySelector("#registerForm").hidden = tab !== "register";
  document.querySelector("#authTitle").textContent = tab === "login" ? "Welcome back" : "Create your account";
  document.querySelector("#authSubtitle").textContent = tab === "login" ? "Sign in to access your downloads." : "Start editing free. Pay only when you export.";
  authError.textContent = "";
}

document.querySelectorAll("[data-auth-tab]").forEach((button) => button.addEventListener("click", () => selectTab(button.dataset.authTab)));

document.querySelector("#loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  authError.textContent = "";
  setSubmitting(form, true);
  try {
    const fields = new FormData(form);
    await api("/api/auth/login", { method: "POST", body: JSON.stringify({ email: fields.get("email"), password: fields.get("password") }) });
    window.location.assign(safeNext);
  } catch (error) {
    authError.textContent = error.message;
    setSubmitting(form, false);
  }
});

document.querySelector("#registerForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  authError.textContent = "";
  setSubmitting(form, true);
  try {
    const fields = new FormData(form);
    await api("/api/auth/register", { method: "POST", body: JSON.stringify({ name: fields.get("name"), email: fields.get("email"), password: fields.get("password") }) });
    window.location.assign(safeNext);
  } catch (error) {
    authError.textContent = error.message;
    setSubmitting(form, false);
  }
});

document.querySelector("#logoutButton").addEventListener("click", async () => {
  await api("/api/auth/logout", { method: "POST", body: "{}" }).catch(() => {});
  selectTab("login");
  showForms();
});

api("/api/me", { headers: {} })
  .then((data) => data.authenticated ? showDashboard(data.user) : showForms())
  .catch(() => {
    authCard.classList.add("auth-unavailable");
    showForms();
    authError.textContent = "Open this site through its Cloudflare or local development URL to sign in.";
  });
