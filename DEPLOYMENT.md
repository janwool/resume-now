# Cloudflare deployment

ResumeNowOnline runs on a Cloudflare Worker and uses the `resume-now` D1 database for optional accounts. Resume editing and PDF downloads are free. The editor exports through the browser print dialog and does not call a checkout or download-credit API.

## Install and deploy

```bash
npm install
npm run db:migrate:remote
npm run deploy
```

The build command recreates `dist/`, generates the SEO landing pages and sitemap, and copies the browser assets needed by the editor.

## Local development

```bash
npm run db:migrate:local
npm run dev
```

Open the local URL printed by Wrangler. Choose a template, edit it, and select **Download PDF**. The browser print dialog should open immediately without requiring an account or payment.

## Retired payment integration

The public checkout and download-credit endpoints return HTTP `410 Gone`. Existing D1 order and credit columns are intentionally retained so historical records are not destroyed.

The historical webhook route remains available only to handle earlier transaction support. It is not used to unlock downloads. Remove its remote secret and provider configuration after any historical refund window has closed.
