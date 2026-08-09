# Cloudflare + Creem setup

ResumeNowOnline runs on a Cloudflare Worker, stores accounts and download credits in the `resume-now` D1 database, and uses Creem for a one-time payment.

## 1. Create the Creem product

In the Creem dashboard, create a **one-time** product with these values:

- Name: `ResumeNowOnline — 3 PDF Downloads`
- Price: `$5.00 USD`
- Description: `Three print-ready PDF resume exports. One-time purchase.`
- Billing type: `One-time`
- Tax category: the digital-goods or software category that best matches the product

Creem owns the checkout price, so the product must be set to $5 in both test and production environments. Test and production API keys and product IDs are separate.

Official guides: [Creem one-time payments](https://docs.creem.io/features/one-time-payment) and [API environments](https://docs.creem.io/api-reference/introduction).

## 2. Configure production Worker secrets

The project is currently configured for Creem **test mode**. The active test product ID is `prod_4rMvovCkBiYL9B4RqyvEk1`, which is a $5 USD one-time product. Add the two private test secrets:

```bash
npx wrangler secret put CREEM_API_KEY
npx wrangler secret put CREEM_WEBHOOK_SECRET
```

`CREEM_TEST_MODE` is currently `true`. Before accepting real payments, replace `CREEM_PRODUCT_ID` with the live product ID, replace `CREEM_API_KEY` with the live key, and set `CREEM_TEST_MODE` to `false`. Never put the API key or webhook secret in `payment-config.js` or any browser-delivered file.

## 3. Create the Creem webhook

In Creem, open **Developers → Webhooks** and create an endpoint for:

```text
https://resume-now.online/api/webhooks/creem
```

Enable these events:

- `checkout.completed` — grants 3 downloads once
- `refund.created` — revokes the credits for a full refund

Copy the webhook signing secret into the `CREEM_WEBHOOK_SECRET` Worker secret. The Worker verifies the raw request body with the `creem-signature` header before changing D1.

If Cloudflare Bot Fight Mode is enabled, it may challenge Creem's webhook requests. Disable Bot Fight Mode or configure the appropriate paid bot-management skip rule for `/api/webhooks/creem`.

Official guide: [Creem webhooks](https://docs.creem.io/code/webhooks).

## 4. Initialize D1 and deploy

```bash
npm install
npm run db:migrate:remote
npm run deploy
```

## Local test mode

Copy `.dev.vars.example` to `.dev.vars` and enter a **test-mode** API key, product ID, and webhook secret:

```bash
cp .dev.vars.example .dev.vars
npm run db:migrate:local
npm run dev
```

Use the Creem CLI or a public tunnel when Creem needs to deliver test webhooks to the local Worker. The checkout success redirect is only a user-facing confirmation; credits are granted exclusively by the signed webhook.
