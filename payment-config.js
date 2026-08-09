// Public product display configuration. API keys and webhook secrets live in
// Cloudflare Worker secrets and must never be placed in this browser file.
window.firstDraftPaymentConfig = Object.freeze({
  provider: "Creem",
  priceUsd: 5,
  downloadsPerPurchase: 3,
});
