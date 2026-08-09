const encoder = new TextEncoder();
const SESSION_COOKIE = "fd_session";
const SESSION_SECONDS = 60 * 60 * 24 * 30;
const PASSWORD_ITERATIONS = 210000;
const DOWNLOADS_PER_ORDER = 3;

const responseHeaders = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
};

function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), { status, headers: { ...responseHeaders, ...extraHeaders } });
}

function apiError(message, status = 400, code = "bad_request") {
  return json({ ok: false, error: { code, message } }, status);
}

function bytesToBase64Url(bytes) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function base64UrlToBytes(value) {
  const base64 = value.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(value.length / 4) * 4, "=");
  return Uint8Array.from(atob(base64), (character) => character.charCodeAt(0));
}

function randomToken(size = 32) {
  const bytes = new Uint8Array(size);
  crypto.getRandomValues(bytes);
  return bytesToBase64Url(bytes);
}

async function sha256(value) {
  return bytesToBase64Url(new Uint8Array(await crypto.subtle.digest("SHA-256", encoder.encode(value))));
}

async function derivePasswordHash(password, salt, iterations = PASSWORD_ITERATIONS) {
  const key = await crypto.subtle.importKey("raw", encoder.encode(password), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits({ name: "PBKDF2", hash: "SHA-256", salt, iterations }, key, 256);
  return bytesToBase64Url(new Uint8Array(bits));
}

function safeEqual(first, second) {
  if (first.length !== second.length) return false;
  let mismatch = 0;
  for (let index = 0; index < first.length; index += 1) mismatch |= first.charCodeAt(index) ^ second.charCodeAt(index);
  return mismatch === 0;
}

function normalizeEmail(value) {
  return String(value || "").trim().toLowerCase();
}

function validEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) && value.length <= 254;
}

function cookieValue(request, name) {
  const cookies = request.headers.get("cookie") || "";
  const match = cookies.match(new RegExp(`(?:^|;\\s*)${name}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : "";
}

function sessionCookie(request, token, maxAge = SESSION_SECONDS) {
  const secure = new URL(request.url).protocol === "https:" ? "; Secure" : "";
  return `${SESSION_COOKIE}=${encodeURIComponent(token)}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${maxAge}${secure}`;
}

function assertSameOrigin(request) {
  const origin = request.headers.get("origin");
  return !origin || origin === new URL(request.url).origin;
}

async function readBody(request) {
  const contentType = request.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) throw new Error("JSON_REQUIRED");
  return request.json();
}

async function currentUser(request, env) {
  const token = cookieValue(request, SESSION_COOKIE);
  if (!token) return null;
  const tokenHash = await sha256(token);
  const now = new Date().toISOString();
  const user = await env.DB.prepare(`
    SELECT users.id, users.email, users.name, users.download_credits, sessions.expires_at
    FROM sessions JOIN users ON users.id = sessions.user_id
    WHERE sessions.token_hash = ? AND sessions.expires_at > ?
  `).bind(tokenHash, now).first();
  if (!user) return null;
  env.DB.prepare("UPDATE sessions SET last_seen_at = ? WHERE token_hash = ?").bind(now, tokenHash).run().catch(() => {});
  return { id: user.id, email: user.email, name: user.name, downloadCredits: user.download_credits };
}

async function createSession(request, env, userId) {
  const token = randomToken();
  const tokenHash = await sha256(token);
  const now = new Date();
  const expiresAt = new Date(now.getTime() + SESSION_SECONDS * 1000).toISOString();
  await env.DB.prepare("DELETE FROM sessions WHERE expires_at <= ?").bind(now.toISOString()).run();
  await env.DB.prepare(`
    INSERT INTO sessions (token_hash, user_id, expires_at, created_at, last_seen_at, user_agent)
    VALUES (?, ?, ?, ?, ?, ?)
  `).bind(tokenHash, userId, expiresAt, now.toISOString(), now.toISOString(), (request.headers.get("user-agent") || "").slice(0, 300)).run();
  return token;
}

async function register(request, env) {
  if (!assertSameOrigin(request)) return apiError("Invalid request origin.", 403, "invalid_origin");
  const body = await readBody(request);
  const name = String(body.name || "").trim().replace(/\s+/g, " ");
  const email = normalizeEmail(body.email);
  const password = String(body.password || "");
  if (name.length < 2 || name.length > 80) return apiError("Enter your name.", 422, "invalid_name");
  if (!validEmail(email)) return apiError("Enter a valid email address.", 422, "invalid_email");
  if (password.length < 10 || password.length > 128) return apiError("Use at least 10 characters for your password.", 422, "weak_password");

  const existing = await env.DB.prepare("SELECT id FROM users WHERE email = ?").bind(email).first();
  if (existing) return apiError("An account already exists for this email.", 409, "email_exists");

  const id = crypto.randomUUID();
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const passwordHash = await derivePasswordHash(password, salt);
  const now = new Date().toISOString();
  try {
    await env.DB.prepare(`
      INSERT INTO users (id, email, name, password_hash, password_salt, password_iterations, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(id, email, name, passwordHash, bytesToBase64Url(salt), PASSWORD_ITERATIONS, now, now).run();
  } catch (error) {
    if (String(error).toLowerCase().includes("unique")) return apiError("An account already exists for this email.", 409, "email_exists");
    throw error;
  }
  const token = await createSession(request, env, id);
  return json({ ok: true, user: { id, email, name, downloadCredits: 0 } }, 201, { "set-cookie": sessionCookie(request, token) });
}

async function login(request, env) {
  if (!assertSameOrigin(request)) return apiError("Invalid request origin.", 403, "invalid_origin");
  const body = await readBody(request);
  const email = normalizeEmail(body.email);
  const password = String(body.password || "");
  const user = await env.DB.prepare(`
    SELECT id, email, name, password_hash, password_salt, password_iterations, download_credits
    FROM users WHERE email = ?
  `).bind(email).first();
  if (!user) return apiError("Email or password is incorrect.", 401, "invalid_credentials");
  const passwordHash = await derivePasswordHash(password, base64UrlToBytes(user.password_salt), user.password_iterations);
  if (!safeEqual(passwordHash, user.password_hash)) return apiError("Email or password is incorrect.", 401, "invalid_credentials");
  const token = await createSession(request, env, user.id);
  return json({ ok: true, user: { id: user.id, email: user.email, name: user.name, downloadCredits: user.download_credits } }, 200, { "set-cookie": sessionCookie(request, token) });
}

async function logout(request, env) {
  if (!assertSameOrigin(request)) return apiError("Invalid request origin.", 403, "invalid_origin");
  const token = cookieValue(request, SESSION_COOKIE);
  if (token) await env.DB.prepare("DELETE FROM sessions WHERE token_hash = ?").bind(await sha256(token)).run();
  return json({ ok: true }, 200, { "set-cookie": sessionCookie(request, "", 0) });
}

async function me(request, env) {
  const user = await currentUser(request, env);
  return json(user ? { ok: true, authenticated: true, user } : { ok: true, authenticated: false });
}

async function createCheckout(request, env) {
  if (!assertSameOrigin(request)) return apiError("Invalid request origin.", 403, "invalid_origin");
  const user = await currentUser(request, env);
  if (!user) return apiError("Sign in before purchasing downloads.", 401, "authentication_required");
  if (!env.CREEM_API_KEY || !env.CREEM_PRODUCT_ID) {
    return apiError("Checkout is not configured yet.", 503, "checkout_not_configured");
  }
  const origin = new URL(request.url).origin;
  const isCreemTest = env.CREEM_TEST_MODE === "true" || String(env.CREEM_API_KEY).startsWith("creem_test_");
  const apiOrigin = isCreemTest ? "https://test-api.creem.io" : "https://api.creem.io";
  const body = {
    product_id: String(env.CREEM_PRODUCT_ID),
    request_id: `resume_${crypto.randomUUID()}`,
    units: 1,
    customer: { email: user.email },
    success_url: `${origin}/builder.html?payment=success`,
    metadata: {
      user_id: user.id,
      product: "resume-export-pack",
      downloads: DOWNLOADS_PER_ORDER,
    },
  };
  const checkoutResponse = await fetch(`${apiOrigin}/v1/checkouts`, {
    method: "POST",
    headers: {
      accept: "application/json",
      "content-type": "application/json",
      "x-api-key": env.CREEM_API_KEY,
    },
    body: JSON.stringify(body),
  });
  const checkout = await checkoutResponse.json();
  if (!checkoutResponse.ok) {
    console.error("Creem checkout error", checkoutResponse.status, JSON.stringify(checkout));
    return apiError("Unable to start checkout. Please try again.", 502, "checkout_failed");
  }
  if (!checkout.checkout_url) return apiError("Payment provider returned an invalid checkout.", 502, "invalid_checkout");
  return json({ ok: true, checkoutUrl: checkout.checkout_url });
}

async function verifyWebhook(rawBody, signature, secret) {
  if (!signature || !secret) return false;
  const key = await crypto.subtle.importKey("raw", encoder.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const digest = new Uint8Array(await crypto.subtle.sign("HMAC", key, encoder.encode(rawBody)));
  const expected = [...digest].map((byte) => byte.toString(16).padStart(2, "0")).join("");
  return safeEqual(expected, signature.toLowerCase());
}

function objectId(value) {
  if (!value) return "";
  return String(typeof value === "object" ? value.id || "" : value);
}

async function creemWebhook(request, env) {
  const rawBody = await request.text();
  const signature = request.headers.get("creem-signature") || "";
  if (!(await verifyWebhook(rawBody, signature, env.CREEM_WEBHOOK_SECRET))) {
    return apiError("Invalid webhook signature.", 401, "invalid_signature");
  }
  const event = JSON.parse(rawBody);
  const eventName = String(event.eventType || "");
  const eventObject = event.object || {};
  const now = new Date().toISOString();

  if (eventName === "checkout.completed") {
    const order = eventObject.order || {};
    const userId = String(eventObject.metadata?.user_id || "");
    const orderId = objectId(order);
    const productId = objectId(eventObject.product || order.product);
    if (eventObject.status !== "completed" || order.status !== "paid") return json({ ok: true, ignored: true });
    if (!userId || !orderId) return apiError("Webhook is missing order identity.", 422, "invalid_webhook");
    if (productId !== String(env.CREEM_PRODUCT_ID || "")) return json({ ok: true, ignored: true });
    const user = await env.DB.prepare("SELECT id FROM users WHERE id = ?").bind(userId).first();
    if (!user) return apiError("Webhook user does not exist.", 404, "user_not_found");
    const customer = eventObject.customer || {};
    await env.DB.batch([
      env.DB.prepare(`
        INSERT OR IGNORE INTO orders
          (provider_order_id, provider, user_id, order_identifier, customer_email, amount, currency, status, credits_granted, created_at)
        VALUES (?, 'creem', ?, ?, ?, ?, ?, 'paid', 0, ?)
      `).bind(orderId, userId, String(eventObject.request_id || eventObject.id || ""), normalizeEmail(customer.email), Number(order.amount_paid ?? order.amount ?? 0), String(order.currency || "USD").toUpperCase(), now),
      env.DB.prepare(`
        UPDATE users SET download_credits = download_credits + ?, updated_at = ?
        WHERE id = ? AND EXISTS (
          SELECT 1 FROM orders WHERE provider_order_id = ? AND provider = 'creem' AND credits_granted = 0
        )
      `).bind(DOWNLOADS_PER_ORDER, now, userId, orderId),
      env.DB.prepare("UPDATE orders SET credits_granted = ? WHERE provider_order_id = ? AND provider = 'creem' AND credits_granted = 0").bind(DOWNLOADS_PER_ORDER, orderId),
    ]);
    return json({ ok: true, creditsGranted: DOWNLOADS_PER_ORDER });
  }

  if (eventName === "refund.created") {
    const transaction = eventObject.transaction || {};
    if (eventObject.status !== "succeeded") return json({ ok: true, ignored: true });
    const orderId = objectId(transaction.order);
    if (!orderId) return apiError("Refund webhook is missing its order.", 422, "invalid_webhook");
    const order = await env.DB.prepare(`
      SELECT user_id, credits_granted FROM orders
      WHERE provider_order_id = ? AND provider = 'creem'
    `).bind(orderId).first();
    if (!order) return apiError("Refunded order does not exist yet.", 404, "order_not_found");
    const refundAmount = Number(eventObject.refund_amount || 0);
    const paidAmount = Number(transaction.amount_paid || transaction.amount || 0);
    const isFullRefund = transaction.status === "refunded" || (paidAmount > 0 && refundAmount >= paidAmount);
    if (!isFullRefund) {
      await env.DB.prepare("UPDATE orders SET status = 'partially_refunded' WHERE provider_order_id = ? AND provider = 'creem'").bind(orderId).run();
      return json({ ok: true, creditsRevoked: 0, partialRefund: true });
    }
    await env.DB.batch([
      env.DB.prepare(`
        UPDATE users SET download_credits = MAX(0, download_credits - COALESCE((
          SELECT credits_granted FROM orders
          WHERE provider_order_id = ? AND provider = 'creem' AND refunded_at IS NULL
        ), 0)), updated_at = ? WHERE id = ?
      `).bind(orderId, now, order.user_id),
      env.DB.prepare("UPDATE orders SET status = 'refunded', refunded_at = ? WHERE provider_order_id = ? AND provider = 'creem' AND refunded_at IS NULL").bind(now, orderId),
    ]);
    return json({ ok: true, creditsRevoked: Number(order.credits_granted || 0) });
  }
  return json({ ok: true, ignored: true });
}

async function claimDownload(request, env) {
  if (!assertSameOrigin(request)) return apiError("Invalid request origin.", 403, "invalid_origin");
  const user = await currentUser(request, env);
  if (!user) return apiError("Sign in to download your résumé.", 401, "authentication_required");
  const body = await readBody(request);
  const templateId = String(body.templateId || "").slice(0, 100);
  const now = new Date().toISOString();
  const result = await env.DB.prepare(`
    UPDATE users SET download_credits = download_credits - 1, updated_at = ?
    WHERE id = ? AND download_credits > 0
  `).bind(now, user.id).run();
  if (!result.meta?.changes) return apiError("You do not have any downloads remaining.", 402, "no_download_credits");
  await env.DB.prepare(`
    INSERT INTO downloads (id, user_id, template_id, created_at, user_agent) VALUES (?, ?, ?, ?, ?)
  `).bind(crypto.randomUUID(), user.id, templateId, now, (request.headers.get("user-agent") || "").slice(0, 300)).run();
  const updated = await env.DB.prepare("SELECT download_credits FROM users WHERE id = ?").bind(user.id).first();
  return json({ ok: true, remaining: updated?.download_credits || 0 });
}

async function handleApi(request, env) {
  const { pathname } = new URL(request.url);
  try {
    if (pathname === "/api/auth/register" && request.method === "POST") return register(request, env);
    if (pathname === "/api/auth/login" && request.method === "POST") return login(request, env);
    if (pathname === "/api/auth/logout" && request.method === "POST") return logout(request, env);
    if (pathname === "/api/me" && request.method === "GET") return me(request, env);
    if (pathname === "/api/checkout" && request.method === "POST") return createCheckout(request, env);
    if (pathname === "/api/downloads/claim" && request.method === "POST") return claimDownload(request, env);
    if (pathname === "/api/webhooks/creem" && request.method === "POST") return creemWebhook(request, env);
    return apiError("API route not found.", 404, "not_found");
  } catch (error) {
    if (String(error?.message) === "JSON_REQUIRED") return apiError("Send a JSON request body.", 415, "json_required");
    console.error("API error", pathname, error?.stack || error);
    return apiError("Something went wrong. Please try again.", 500, "internal_error");
  }
}

export default {
  async fetch(request, env) {
    const pathname = new URL(request.url).pathname;
    if (pathname.startsWith("/api/")) return handleApi(request, env);
    const assetResponse = await env.ASSETS.fetch(request);
    const headers = new Headers(assetResponse.headers);
    headers.set("x-content-type-options", "nosniff");
    headers.set("referrer-policy", "strict-origin-when-cross-origin");
    headers.set("permissions-policy", "camera=(), microphone=(), geolocation=()");
    return new Response(assetResponse.body, { status: assetResponse.status, statusText: assetResponse.statusText, headers });
  },
};
