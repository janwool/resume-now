const $ = (selector, scope = document) => scope.querySelector(selector);
const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];
const importedTemplateCatalog = window.resumeTemplateManifest || [];
const importedTemplateOverlays = window.resumeTemplateOverlays || {};
const escapeHTML = (value = "") => String(value).replace(/[&<>'"]/g, (character) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
}[character]));
const normalizeImportedText = (value = "") => String(value)
  .replace(/([A-Za-z]{4,})\s*\n\s*([A-Za-z]{1,2})(?=\s|$)/g, "$1$2")
  .replace(/\s*\n\s*/g, " ")
  .replace(/\s+/g, " ")
  .trim();

const colorAssets = {
  black: "黑色",
  blue: "蓝色",
  green: "绿色",
  orange: "橙色",
  cyan: "青色",
};

const templateCatalog = {
  strategist: { name: "The Strategist", subtitle: "Professional résumé template", tagline: "Built for clarity.", description: "A structured layout for experienced candidates who want their impact understood at a glance." },
  operator: { name: "The Operator", subtitle: "Technical résumé template", tagline: "Precise, direct and easy to scan.", description: "A focused template for engineering, operations and product candidates." },
  storyteller: { name: "The Storyteller", subtitle: "Creative résumé template", tagline: "Make the work feel memorable.", description: "A confident layout for marketing, brand and creative professionals." },
  analyst: { name: "The Analyst", subtitle: "Finance résumé template", tagline: "Structure that makes results visible.", description: "A rigorous template for finance, data and analytical career paths." },
  director: { name: "The Director", subtitle: "Leadership résumé template", tagline: "Lead with scope and outcomes.", description: "A polished layout for senior leaders and experienced managers." },
  consultant: { name: "The Consultant", subtitle: "Strategy résumé template", tagline: "Clear thinking, clearly presented.", description: "A clean template for consulting, strategy and client-facing work." },
  maker: { name: "The Maker", subtitle: "Design résumé template", tagline: "A little personality, carefully applied.", description: "A flexible layout for designers, writers and creative makers." },
  classic: { name: "The Classic", subtitle: "ATS résumé template", tagline: "Timeless and dependable.", description: "A familiar, recruiter-friendly layout for almost any role." },
};

const resumeThemes = {
  black: { accent: "#a9abad", dark: "#000000", paper: "#f0f1f1" },
  blue: { accent: "#08b5d4", dark: "#303536", paper: "#edf8fc" },
  green: { accent: "#b1d832", dark: "#254b4b", paper: "#f5faed" },
  orange: { accent: "#e7a744", dark: "#5c2a1f", paper: "#f5fae9" },
  cyan: { accent: "#de7379", dark: "#303b49", paper: "#eff5fb" },
};
const pageParams = new URLSearchParams(window.location.search);
const requestedTemplateKey = pageParams.get("template");
const importedSelectedTemplate = importedTemplateCatalog.find((template) => template.id === requestedTemplateKey);
const selectedTemplateKey = importedSelectedTemplate?.id || (templateCatalog[requestedTemplateKey] ? requestedTemplateKey : "strategist");
const selectedTemplate = importedSelectedTemplate || templateCatalog[selectedTemplateKey];

const assetPath = (color, type = "resume", ext = "jpg") =>
  `(118)/${colorAssets[color]}/flat ${type} A4.${ext}`;

const navToggle = $(".nav-toggle");
const mainNav = $(".main-nav");
if (navToggle && mainNav) {
  navToggle.addEventListener("click", () => {
    const open = mainNav.classList.toggle("open");
    navToggle.setAttribute("aria-expanded", String(open));
  });
  $$("a", mainNav).forEach((link) => link.addEventListener("click", () => {
    mainNav.classList.remove("open");
    navToggle.setAttribute("aria-expanded", "false");
  }));
}

const toast = $(".toast");
let toastTimer;
function showToast(message) {
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 2200);
}

let accountState = { loaded: false, authenticated: false, user: null };
let accountRequest = null;
async function apiRequest(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers: { "content-type": "application/json", ...(options.headers || {}) },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.error?.message || "Something went wrong. Please try again.");
    error.code = data.error?.code || "request_failed";
    throw error;
  }
  return data;
}

function accountReturnUrl() {
  return `${window.location.pathname}${window.location.search}`;
}

function renderAccountAccess() {
  let link = $("#globalAccountLink");
  const target = accountState.authenticated ? "account.html" : `account.html?next=${encodeURIComponent(accountReturnUrl())}`;
  const label = accountState.authenticated ? `${accountState.user.name.split(" ")[0]} · ${accountState.user.downloadCredits || 0}` : "Sign in";
  if (!link && mainNav) {
    link = document.createElement("a");
    link.id = "globalAccountLink";
    mainNav.appendChild(link);
  }
  if (!link && $(".app-actions")) {
    link = document.createElement("a");
    link.id = "globalAccountLink";
    link.className = "account-nav-link";
    $(".app-actions").insertBefore(link, $("#previewButton"));
  }
  if (link) {
    link.href = target;
    link.textContent = label;
    link.classList.toggle("signed-in", accountState.authenticated);
  }
}

async function loadAccount(force = false) {
  if (accountRequest && !force) return accountRequest;
  accountRequest = apiRequest("/api/me", { headers: {} })
    .then((data) => {
      accountState = { loaded: true, authenticated: Boolean(data.authenticated), user: data.user || null };
      renderAccountAccess();
      return accountState;
    })
    .catch(() => {
      accountState = { loaded: true, authenticated: false, user: null };
      renderAccountAccess();
      return accountState;
    })
    .finally(() => { accountRequest = null; });
  return accountRequest;
}

loadAccount();

function templatePublicUrl(template) {
  if (window.location.protocol === "file:") return `template-detail.html?template=${encodeURIComponent(template.id)}`;
  return `/resume-templates/${encodeURIComponent(template.slug)}/`;
}

function templateCardMarkup(template, catalog = true) {
  const categories = escapeHTML(template.category || "professional");
  const cardClass = catalog ? "template-card catalog-card" : "template-card";
  return `<article class="${cardClass}" data-name="${escapeHTML(`${template.name} ${template.subtitle}`)}" data-category="${categories}">
    <a class="template-thumb" href="${templatePublicUrl(template)}"><img src="${escapeHTML(template.preview)}" alt="${escapeHTML(template.name)} preview" loading="lazy" /></a>
    <div class="template-meta"><div><h3>${escapeHTML(template.name)}</h3><p>${escapeHTML(template.subtitle)}</p></div><button class="heart" aria-label="Save ${escapeHTML(template.name)}"><svg class="icon" viewBox="0 0 24 24"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21l7.8-7.5 1.1-1.1a5.5 5.5 0 0 0-.1-7.8Z"/></svg></button><span>Edit free</span></div>
  </article>`;
}

const catalogGrid = $("#catalogGrid");
if (catalogGrid && importedTemplateCatalog.length) {
  catalogGrid.innerHTML = importedTemplateCatalog.map((template) => templateCardMarkup(template)).join("");
  const total = $("#catalogTotal");
  if (total) total.textContent = `${importedTemplateCatalog.length} original templates, ready to use`;
}

const featuredTemplateGrid = $("#featuredTemplateGrid");
if (featuredTemplateGrid && importedTemplateCatalog.length) {
  featuredTemplateGrid.innerHTML = importedTemplateCatalog.slice(0, 4).map((template) => templateCardMarkup(template, false)).join("");
}

$$(".heart").forEach((button) => {
  button.addEventListener("click", (event) => {
    event.preventDefault();
    const saved = button.classList.toggle("saved");
    button.setAttribute("aria-pressed", String(saved));
    showToast(saved ? "Saved to favorites" : "Removed from favorites");
  });
});

const catalogCards = $$(".catalog-card");
const catalogSearch = $("#templateSearch");
const catalogFilters = $$("[data-template-filter]");
let templateFilter = "all";

function filterCatalog() {
  if (!catalogCards.length) return;
  const query = (catalogSearch?.value || "").trim().toLowerCase();
  let visible = 0;
  catalogCards.forEach((card) => {
    const category = (card.dataset.category || "").toLowerCase();
    const haystack = `${card.dataset.name || ""} ${category}`.toLowerCase();
    const matchesCategory = templateFilter === "all" || category.includes(templateFilter);
    const matchesSearch = !query || haystack.includes(query);
    const show = matchesCategory && matchesSearch;
    card.classList.toggle("is-hidden", !show);
    if (show) visible += 1;
  });
  const count = $("#resultCount");
  if (count) count.textContent = `${visible} template${visible === 1 ? "" : "s"}`;
  const empty = $("#catalogEmpty");
  if (empty) empty.hidden = visible !== 0;
}

catalogFilters.forEach((button) => {
  button.addEventListener("click", () => {
    catalogFilters.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    templateFilter = button.dataset.templateFilter;
    filterCatalog();
  });
});
catalogSearch?.addEventListener("input", filterCatalog);
filterCatalog();

const productMainImage = $("#productMainImage");
let productColor = importedSelectedTemplate?.color || (colorAssets[pageParams.get("color")] ? pageParams.get("color") : "black");
let productType = "resume";

function updateProductImage() {
  if (!productMainImage) return;
  productMainImage.style.opacity = ".25";
  setTimeout(() => {
    productMainImage.src = importedSelectedTemplate ? importedSelectedTemplate.preview : assetPath(productColor, productType);
    productMainImage.alt = importedSelectedTemplate ? `${importedSelectedTemplate.name} preview` : `${productColor} ${productType} template preview`;
    productMainImage.style.opacity = "1";
  }, 140);
  if (importedSelectedTemplate) {
    const previews = $("#previewThumbs");
    const colors = $("#productColors");
    if (previews) previews.hidden = true;
    if (colors) colors.hidden = true;
    const download = $("#useTemplate");
    if (download) download.href = `builder.html?template=${encodeURIComponent(selectedTemplateKey)}`;
    return;
  }
  $$("[data-preview-type]").forEach((button) => {
    const image = $("img", button);
    if (image) image.src = assetPath(productColor, button.dataset.previewType);
  });
  const download = $("#useTemplate");
  if (download) download.href = `builder.html?template=${selectedTemplateKey}&color=${productColor}`;
}

if (productMainImage) {
  $("#productTitle").textContent = selectedTemplate.name;
  $("#productSubtitle").textContent = selectedTemplate.subtitle;
  $("#breadcrumbTemplate").textContent = selectedTemplate.name;
  $("#productTagline").textContent = importedSelectedTemplate ? "An original template from your complete collection." : `${selectedTemplate.tagline} Free to make your own.`;
  $("#productDescription").textContent = importedSelectedTemplate ? selectedTemplate.description : `${selectedTemplate.description} Edit it free, then get 3 PDF downloads for $5.`;
  document.title = `${selectedTemplate.name} — ResumeNowOnline`;
  const descriptionMeta = $('meta[name="description"]');
  if (descriptionMeta && importedSelectedTemplate) descriptionMeta.content = selectedTemplate.description;
  $$("[data-product-color]").forEach((button) => button.classList.toggle("active", button.dataset.productColor === productColor));
  updateProductImage();
}

$$("[data-preview-type]").forEach((button) => {
  button.addEventListener("click", () => {
    $$("[data-preview-type]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    productType = button.dataset.previewType;
    updateProductImage();
  });
});

$$("[data-product-color]").forEach((button) => {
  button.addEventListener("click", () => {
    $$("[data-product-color]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    productColor = button.dataset.productColor;
    updateProductImage();
  });
});

$("#useTemplate")?.addEventListener("click", () => showToast("Opening the free editor"));

$$(".accordion-header").forEach((button) => {
  button.addEventListener("click", () => button.closest(".accordion").classList.toggle("open"));
});

const bindText = (inputSelector, outputSelector) => {
  const input = $(inputSelector);
  const output = $(outputSelector);
  if (!input || !output) return;
  input.addEventListener("input", () => {
    output.textContent = input.value || input.placeholder;
    const saved = $(".save-state span:last-child");
    if (saved) {
      saved.textContent = "Saving…";
      setTimeout(() => { saved.textContent = "Saved"; }, 500);
    }
  });
};

bindText("#nameInput", "#resumeName");
bindText("#titleInput", "#resumeTitle");
bindText("#summaryInput", "#resumeSummary");
bindText("#jobInput", "#resumeJob");
bindText("#companyInput", "#resumeCompany");

const editableResume = $(".resume-document");
let persistImportedEdits = null;
let reflowImportedPage = () => {};
const photoStorageKey = `first-draft-photo:${selectedTemplateKey}`;
let photoState = { src: "", scale: 100, positionX: 50, positionY: 50 };
try { photoState = { ...photoState, ...JSON.parse(localStorage.getItem(photoStorageKey) || "{}") }; } catch (_) { photoState = { src: "", scale: 100, positionX: 50, positionY: 50 }; }
if (editableResume) {
  document.body.classList.add("direct-template-editor");
  editableResume.classList.add(`template-${selectedTemplateKey}`);
  const builderName = $("#builderTemplateName");
  if (builderName) builderName.textContent = `${selectedTemplate.name} · Editor`;
  document.title = `${selectedTemplate.name} Editor — ResumeNowOnline`;

  if (importedSelectedTemplate && !importedSelectedTemplate.supportsOnlineEdit) {
    document.body.classList.add("imported-template-builder");
    editableResume.classList.add("imported-template-document");
    editableResume.setAttribute("aria-label", `Directly editable ${importedSelectedTemplate.name}`);
    const overlay = importedTemplateOverlays[importedSelectedTemplate.id];
    const storageKey = `first-draft-edits:${importedSelectedTemplate.id}`;
    let storedEdits = {};
    try { storedEdits = JSON.parse(localStorage.getItem(storageKey) || "{}"); } catch (_) { storedEdits = {}; }
    const pages = overlay?.pages || (overlay ? [{ ...overlay, preview: importedSelectedTemplate.preview }] : []);
    const pageMarkup = pages.map((page, pageIndex) => {
      const blockMarkup = (page.blocks || []).map((block) => {
        const stored = storedEdits[block.id];
        const storedValue = typeof stored === "string" ? stored : stored?.text;
        const storedStyle = typeof stored === "object" && stored ? stored.style || {} : {};
        const normalizedText = normalizeImportedText(block.text);
        const value = storedValue ?? normalizedText;
        const changed = Object.prototype.hasOwnProperty.call(storedEdits, block.id);
        const style = [
          `--edit-x:${block.x}%`, `--edit-y:${block.y}%`, `--edit-w:${block.w}%`, `--edit-h:${block.h}%`,
          `--edit-size:${block.fontSize}cqw`, `--edit-color:${storedStyle.color || block.color}`, `--edit-bg:${block.background}`,
          `--edit-weight:${block.weight}`, `--edit-style:${block.italic ? "italic" : "normal"}`,
          `--edit-line-height:${block.lineHeight || 1}`, `--edit-align:${block.align || "left"}`,
          storedStyle.fontFamily ? `font-family:${storedStyle.fontFamily}` : "",
          storedStyle.fontSize ? `font-size:${storedStyle.fontSize}` : "",
          storedStyle.fontWeight ? `font-weight:${storedStyle.fontWeight}` : "",
          storedStyle.fontStyle ? `font-style:${storedStyle.fontStyle}` : "",
          storedStyle.textDecoration ? `text-decoration:${storedStyle.textDecoration}` : "",
          storedStyle.textAlign ? `text-align:${storedStyle.textAlign}` : "",
          storedStyle.lineHeight ? `line-height:${storedStyle.lineHeight}` : "",
        ].filter(Boolean).join(";");
        const keepOnOneLine = Number(block.fontSizePoints || 0) <= 14 && normalizedText.length <= 52;
        return `<div class="resume-edit-block${changed ? " is-changed" : ""}" contenteditable="true" role="textbox" aria-label="Edit ${escapeHTML(block.text.slice(0, 44))}" spellcheck="true" data-edit-id="${escapeHTML(block.id)}" data-original="${escapeHTML(block.text)}" data-original-top="${block.y}" data-original-height="${block.h}" data-original-left="${block.x}" data-original-width="${block.w}" data-multiline="${block.text.includes("\n")}" data-nowrap="${keepOnOneLine}" data-font-size-points="${block.fontSizePoints || ""}" data-page-width="${page.width}" style="${escapeHTML(style)}">${escapeHTML(value)}</div>`;
      }).join("");
      const maskMarkup = (page.blocks || []).map((block) => `<span class="resume-original-text-mask" data-mask-for="${escapeHTML(block.id)}" style="--mask-x:${block.x}%;--mask-y:${block.y}%;--mask-w:${block.w}%;--mask-h:${block.h}%;--mask-bg:${block.background}"></span>`).join("");
      const photoMarkup = (page.photoRegions || []).map((photo) => `<button class="resume-photo-slot photo-shape-${escapeHTML(photo.shape || "rounded")}" type="button" data-photo-id="${escapeHTML(photo.id)}" aria-label="Upload profile photo" style="--photo-x:${photo.x}%;--photo-y:${photo.y}%;--photo-w:${photo.w}%;--photo-h:${photo.h}%"><img class="resume-photo-image" alt="Uploaded profile photo" /><span class="photo-upload-affordance">↥ Photo</span></button>`).join("");
      return `<section class="imported-resume-page" data-page-number="${pageIndex + 1}" style="aspect-ratio:${page.width} / ${page.height}" aria-label="Résumé page ${pageIndex + 1} of ${pages.length}"><img class="imported-template-preview-image" src="${escapeHTML(page.preview || importedSelectedTemplate.preview)}" alt="${escapeHTML(importedSelectedTemplate.name)} page ${pageIndex + 1}" /><div class="resume-edit-layer" aria-label="Editable text on page ${pageIndex + 1}">${photoMarkup}${maskMarkup}${blockMarkup}</div><span class="imported-page-label">Page ${pageIndex + 1}</span></section>`;
    }).join("");
    editableResume.style.removeProperty("aspect-ratio");
    editableResume.innerHTML = pageMarkup;

    // Measure every block in its original text/style state. Word's exported
    // rectangle can be a few pixels shorter than the browser's line box, so
    // comparing against the raw rectangle causes false reflows and mask bands.
    $$(".resume-edit-block", editableResume).forEach((field) => {
      const clone = field.cloneNode(false);
      clone.className = "resume-edit-block";
      clone.removeAttribute("contenteditable");
      clone.removeAttribute("role");
      clone.removeAttribute("aria-label");
      ["font-family", "font-size", "font-weight", "font-style", "text-decoration", "text-align", "line-height"].forEach((property) => clone.style.removeProperty(property));
      clone.style.visibility = "hidden";
      clone.style.pointerEvents = "none";
      clone.textContent = normalizeImportedText(field.dataset.original || "");
      field.parentElement?.appendChild(clone);
      field.dataset.baseContentHeight = String(clone.scrollHeight);
      clone.remove();
    });

    const canvas = $(".builder-canvas");
    const hint = document.createElement("div");
    hint.className = "direct-edit-hint";
    const blocks = pages.flatMap((page) => page.blocks || []);
    hint.innerHTML = `<span class="direct-edit-icon">✎</span><div><strong>Edit directly on the résumé</strong><span>Hybrid layout · text flows inside each column</span></div><span class="direct-edit-count">${pages.length} ${pages.length === 1 ? "page" : "pages"} · ${blocks.length} areas</span>`;
    canvas?.insertBefore(hint, editableResume);
    const footerPage = $(".canvas-footer > span");
    if (footerPage) footerPage.textContent = `${pages.length} ${pages.length === 1 ? "page" : "pages"}`;

    const horizontalFlowOverlap = (first, second) => {
      const left = Math.max(first.left, second.left);
      const right = Math.min(first.right, second.right);
      const overlap = Math.max(0, right - left);
      return overlap / Math.max(1, Math.min(first.width, second.width)) >= .48;
    };
    reflowImportedPage = (pageElement) => {
      if (!pageElement) return;
      const pageRect = pageElement.getBoundingClientRect();
      const fields = $$(".resume-edit-block", pageElement).map((field) => {
        field.classList.remove("is-reflowed");
        field.style.removeProperty("top");
        field.dataset.flowShift = "0";
        const mask = $$(".resume-original-text-mask", pageElement).find((item) => item.dataset.maskFor === field.dataset.editId);
        mask?.classList.remove("is-visible");
        const top = Number(field.dataset.originalTop) / 100 * pageRect.height;
        const height = Number(field.dataset.originalHeight) / 100 * pageRect.height;
        const left = Number(field.dataset.originalLeft) / 100 * pageRect.width;
        const width = Number(field.dataset.originalWidth) / 100 * pageRect.width;
        return { field, mask, top, height, left, width, right: left + width };
      }).sort((first, second) => first.top - second.top || first.left - second.left);

      const flowing = [];
      fields.forEach((item) => {
        const upstream = flowing.filter((previous) => previous.top <= item.top && horizontalFlowOverlap(previous, item));
        const shift = upstream.length ? Math.max(...upstream.map((previous) => previous.shift + previous.extra)) : 0;
        const isChanged = item.field.classList.contains("is-changed");
        const participates = isChanged || shift > .5;
        if (shift > .5) {
          item.field.style.top = `calc(${item.field.dataset.originalTop}% + ${shift.toFixed(2)}px)`;
          item.field.dataset.flowShift = shift.toFixed(2);
          item.field.classList.add("is-reflowed");
          item.mask?.classList.add("is-visible");
        }
        const baseContentHeight = Number(item.field.dataset.baseContentHeight) || item.height;
        const extra = isChanged ? Math.max(0, item.field.scrollHeight - baseContentHeight) : 0;
        if (participates) flowing.push({ ...item, shift, extra });
      });

      const reachesEdge = flowing.some((item) => item.top + item.height + item.shift + item.extra > pageRect.height - 10);
      pageElement.classList.toggle("has-flow-overflow", reachesEdge);
      const pageLabel = $(".imported-page-label", pageElement);
      if (pageLabel) pageLabel.textContent = reachesEdge ? `Page ${pageElement.dataset.pageNumber} · Content full` : `Page ${pageElement.dataset.pageNumber}`;
    };

    let saveTimer;
    persistImportedEdits = () => {
      const edits = {};
      $$(".resume-edit-block.is-changed", editableResume).forEach((item) => {
        edits[item.dataset.editId] = {
          text: item.innerText || "",
          style: {
            fontFamily: item.style.fontFamily,
            fontSize: item.style.fontSize,
            color: item.style.getPropertyValue("--edit-color"),
            fontWeight: item.style.fontWeight,
            fontStyle: item.style.fontStyle,
            textDecoration: item.style.textDecoration,
            textAlign: item.style.textAlign,
            lineHeight: item.style.lineHeight,
          },
        };
      });
      localStorage.setItem(storageKey, JSON.stringify(edits));
      const saved = $(".save-state span:last-child");
      if (saved) saved.textContent = "Saving…";
      clearTimeout(saveTimer);
      saveTimer = setTimeout(() => { if (saved) saved.textContent = "Saved"; }, 450);
    };
    $$(".resume-edit-block", editableResume).forEach((field) => {
      field.addEventListener("focus", () => {
        const selection = window.getSelection();
        if (!selection || !field.textContent) return;
        const range = document.createRange();
        range.selectNodeContents(field);
        selection.removeAllRanges();
        selection.addRange(range);
      });
      field.addEventListener("keydown", (event) => {
        if (event.key !== "Enter") return;
        event.preventDefault();
        if (field.dataset.multiline === "true") document.execCommand("insertLineBreak", false);
      });
      field.addEventListener("paste", (event) => {
        event.preventDefault();
        document.execCommand("insertText", false, event.clipboardData?.getData("text/plain") || "");
      });
      field.addEventListener("input", () => {
        field.classList.add("is-changed");
        reflowImportedPage(field.closest(".imported-resume-page"));
        persistImportedEdits();
      });
    });
    requestAnimationFrame(() => $$(".imported-resume-page", editableResume).forEach((pageElement) => reflowImportedPage(pageElement)));
    if (!blocks.length) hint.innerHTML = `<span class="direct-edit-icon">!</span><div><strong>Preview ready</strong><span>Direct-edit data is still being prepared for this template.</span></div>`;
  } else {
    editableResume.setAttribute("aria-label", `Directly editable ${selectedTemplate.name} résumé template`);
    $$("h1, h2, h3, h4, p, dt, dd, li, .flat-resume-footer span", editableResume).forEach((node) => {
      if (!node.closest('[contenteditable="true"]')) node.setAttribute("contenteditable", "true");
    });
    const flatPhoto = $(".flat-photo", editableResume);
    if (flatPhoto) flatPhoto.insertAdjacentHTML("beforeend", `<button class="resume-photo-slot flat-photo-slot photo-shape-rounded" type="button" data-photo-id="flat-profile-photo" aria-label="Upload profile photo"><img class="resume-photo-image" alt="Uploaded profile photo" /><span class="photo-upload-affordance">↥ Photo</span></button>`);
    const directFields = $$('[contenteditable="true"]', editableResume);
    const canvas = $(".builder-canvas");
    const hint = document.createElement("div");
    hint.className = "direct-edit-hint";
    hint.innerHTML = `<span class="direct-edit-icon">✎</span><div><strong>Edit directly on the résumé</strong><span>Click any text to replace it</span></div><span class="direct-edit-count">${directFields.length} editable areas</span>`;
    canvas?.insertBefore(hint, editableResume);
    const footerPage = $(".canvas-footer > span");
    if (footerPage) footerPage.textContent = "1 page";
  }
}

let selectedEditableElement = null;
let selectedPhotoSlot = null;
const elementInspector = $("#elementInspector");
const elementTools = $("#elementTools");
const elementInspectorEmpty = $("#elementInspectorEmpty");
const photoTools = $("#photoTools");
const photoFileInput = document.createElement("input");
photoFileInput.type = "file";
photoFileInput.accept = "image/jpeg,image/png,image/webp";
photoFileInput.id = "profilePhotoInput";
photoFileInput.className = "visually-hidden-upload";
photoFileInput.setAttribute("aria-label", "Profile photo file");
document.body.appendChild(photoFileInput);

function savePhotoState() {
  try {
    if (photoState.src) localStorage.setItem(photoStorageKey, JSON.stringify(photoState));
    else localStorage.removeItem(photoStorageKey);
  } catch (_) {
    showToast("The image is too large to save in this browser");
  }
}

function updatePhotoControls() {
  if ($("#photoScale")) $("#photoScale").value = String(photoState.scale);
  if ($("#photoScaleValue")) $("#photoScaleValue").value = `${photoState.scale}%`;
  if ($("#photoPositionX")) $("#photoPositionX").value = String(photoState.positionX);
  if ($("#photoPositionXValue")) $("#photoPositionXValue").value = `${photoState.positionX}%`;
  if ($("#photoPositionY")) $("#photoPositionY").value = String(photoState.positionY);
  if ($("#photoPositionYValue")) $("#photoPositionYValue").value = `${photoState.positionY}%`;
  if ($("#removePhoto")) $("#removePhoto").disabled = !photoState.src;
  if ($("#changePhoto strong")) $("#changePhoto strong").textContent = photoState.src ? "Replace photo" : "Choose photo";
}

function applyPhotoState() {
  // Keep a 20% overscan around the photo and pan the image itself. Unlike
  // object-position, this remains visible even when one axis has no crop area.
  const translateX = (50 - Number(photoState.positionX)) / 6;
  const translateY = (50 - Number(photoState.positionY)) / 6;
  $$(".resume-photo-slot", editableResume || document).forEach((slot) => {
    const image = $(".resume-photo-image", slot);
    if (image) {
      if (photoState.src) image.src = photoState.src;
      else image.removeAttribute("src");
    }
    slot.style.setProperty("--photo-scale", String(photoState.scale / 100));
    slot.style.setProperty("--photo-translate-x", `${translateX}%`);
    slot.style.setProperty("--photo-translate-y", `${translateY}%`);
    slot.classList.toggle("has-uploaded-photo", Boolean(photoState.src));
    slot.closest(".flat-photo")?.classList.toggle("has-uploaded-photo", Boolean(photoState.src));
    const affordance = $(".photo-upload-affordance", slot);
    if (affordance) affordance.textContent = photoState.src ? "Edit" : "↥ Photo";
  });
  updatePhotoControls();
}

function selectPhotoSlot(slot, openPicker = false) {
  if (!slot || !elementInspector) return;
  const previousPage = selectedEditableElement?.closest?.(".imported-resume-page");
  selectedEditableElement?.classList.remove("is-selected");
  selectedEditableElement = null;
  reflowImportedPage(previousPage);
  selectedPhotoSlot?.classList.remove("is-selected");
  selectedPhotoSlot = slot;
  slot.classList.add("is-selected");
  elementInspector.classList.add("has-selection");
  if (elementInspectorEmpty) elementInspectorEmpty.hidden = true;
  if (elementTools) elementTools.hidden = true;
  if (photoTools) photoTools.hidden = false;
  updatePhotoControls();
  if (openPicker) photoFileInput.click();
}

function resizeUploadedPhoto(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = reject;
    reader.onload = () => {
      const source = new Image();
      source.onerror = reject;
      source.onload = () => {
        const limit = 1200;
        const scale = Math.min(1, limit / Math.max(source.width, source.height));
        const canvas = document.createElement("canvas");
        canvas.width = Math.max(1, Math.round(source.width * scale));
        canvas.height = Math.max(1, Math.round(source.height * scale));
        const context = canvas.getContext("2d");
        context.fillStyle = "#ffffff";
        context.fillRect(0, 0, canvas.width, canvas.height);
        context.drawImage(source, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL("image/jpeg", .88));
      };
      source.src = String(reader.result || "");
    };
    reader.readAsDataURL(file);
  });
}

photoFileInput.addEventListener("change", async () => {
  const file = photoFileInput.files?.[0];
  photoFileInput.value = "";
  if (!file) return;
  if (!file.type.startsWith("image/") || file.size > 12 * 1024 * 1024) {
    showToast("Choose a JPG, PNG or WebP image under 12 MB");
    return;
  }
  try {
    photoState = { src: await resizeUploadedPhoto(file), scale: 100, positionX: 50, positionY: 50 };
    savePhotoState();
    applyPhotoState();
    showToast("Profile photo updated");
  } catch (_) {
    showToast("This image could not be opened");
  }
});

editableResume?.addEventListener("click", (event) => {
  const slot = event.target.closest?.(".resume-photo-slot");
  if (!slot) return;
  event.preventDefault();
  event.stopPropagation();
  selectPhotoSlot(slot, !photoState.src);
});

$("#changePhoto")?.addEventListener("click", () => photoFileInput.click());
$("#removePhoto")?.addEventListener("click", () => {
  photoState = { src: "", scale: 100, positionX: 50, positionY: 50 };
  savePhotoState();
  applyPhotoState();
  showToast("Uploaded photo removed");
});
[["#photoScale", "scale"], ["#photoPositionX", "positionX"], ["#photoPositionY", "positionY"]].forEach(([selector, key]) => {
  $(selector)?.addEventListener("input", (event) => {
    photoState[key] = Number(event.target.value);
    applyPhotoState();
    savePhotoState();
  });
});
applyPhotoState();

function colorAsHex(color) {
  if (/^#[0-9a-f]{6}$/i.test(color || "")) return color;
  const channels = (color || "").match(/[\d.]+/g)?.slice(0, 3).map(Number);
  if (!channels || channels.length < 3) return "#1d1d1f";
  return `#${channels.map((value) => Math.max(0, Math.min(255, Math.round(value))).toString(16).padStart(2, "0")).join("")}`;
}

function fontChoice(fontFamily) {
  const family = (fontFamily || "").toLowerCase();
  if (family.includes("avenir")) return "'Avenir Next', Avenir, sans-serif";
  if (family.includes("georgia")) return "Georgia, serif";
  if (family.includes("times")) return "'Times New Roman', serif";
  if (family.includes("arial")) return "Arial, Helvetica, sans-serif";
  return "-apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif";
}

function setInspectorSelection(field) {
  if (!field || !elementInspector) return;
  selectedPhotoSlot?.classList.remove("is-selected");
  selectedPhotoSlot = null;
  if (photoTools) photoTools.hidden = true;
  const previousPage = selectedEditableElement?.closest?.(".imported-resume-page");
  selectedEditableElement?.classList.remove("is-selected");
  selectedEditableElement = field;
  field.classList.add("is-selected");
  if (previousPage && previousPage !== field.closest(".imported-resume-page")) reflowImportedPage(previousPage);
  reflowImportedPage(field.closest(".imported-resume-page"));
  elementInspector.classList.add("has-selection");
  if (elementInspectorEmpty) elementInspectorEmpty.hidden = true;
  if (elementTools) elementTools.hidden = false;

  const computed = getComputedStyle(field);
  const previewName = (field.textContent || "Selected text").trim().replace(/\s+/g, " ").slice(0, 52);
  if ($("#selectedElementName")) $("#selectedElementName").textContent = previewName || "Empty text";
  if ($("#elementFont")) $("#elementFont").value = fontChoice(computed.fontFamily);
  if ($("#elementFontSize")) {
    const pointSize = Number(field.dataset.fontSizePoints) || Number.parseFloat(computed.fontSize) * 0.75;
    $("#elementFontSize").value = Math.max(5, Math.min(96, pointSize)).toFixed(1);
  }
  const color = colorAsHex(field.style.getPropertyValue("--edit-color") || computed.color);
  if ($("#elementColor")) $("#elementColor").value = color;
  elementInspector.style.setProperty("--element-color", color);
  const lineHeight = Number.parseFloat(computed.lineHeight) / Math.max(1, Number.parseFloat(computed.fontSize));
  const normalizedLineHeight = Number.isFinite(lineHeight) ? Math.max(.8, Math.min(2, lineHeight)) : 1;
  if ($("#elementLineHeight")) $("#elementLineHeight").value = normalizedLineHeight.toFixed(2);
  if ($("#elementLineHeightValue")) $("#elementLineHeightValue").value = normalizedLineHeight.toFixed(2);
  $$('[data-element-style="bold"]').forEach((button) => button.classList.toggle("active", Number(computed.fontWeight) >= 600));
  $$('[data-element-style="italic"]').forEach((button) => button.classList.toggle("active", computed.fontStyle === "italic"));
  $$('[data-element-style="underline"]').forEach((button) => button.classList.toggle("active", computed.textDecorationLine.includes("underline")));
  $$('[data-element-align]').forEach((button) => button.classList.toggle("active", button.dataset.elementAlign === computed.textAlign || (button.dataset.elementAlign === "left" && computed.textAlign === "start")));
}

function commitElementStyle() {
  if (!selectedEditableElement) return;
  selectedEditableElement.classList.add("is-changed");
  reflowImportedPage(selectedEditableElement.closest(".imported-resume-page"));
  persistImportedEdits?.();
  const saved = $(".save-state span:last-child");
  if (saved) saved.textContent = "Saved";
}

editableResume?.addEventListener("focusin", (event) => {
  const field = event.target.closest?.('[contenteditable="true"]');
  if (field && editableResume.contains(field)) setInspectorSelection(field);
});
editableResume?.addEventListener("click", (event) => {
  const field = event.target.closest?.('[contenteditable="true"]');
  if (field) setInspectorSelection(field);
});
$(".builder-canvas")?.addEventListener("click", (event) => {
  if (event.target.closest?.('[contenteditable="true"], .resume-photo-slot')) return;
  const previousPage = selectedEditableElement?.closest?.(".imported-resume-page");
  selectedEditableElement?.classList.remove("is-selected");
  selectedEditableElement = null;
  selectedPhotoSlot?.classList.remove("is-selected");
  selectedPhotoSlot = null;
  reflowImportedPage(previousPage);
  elementInspector?.classList.remove("has-selection");
  if (elementInspectorEmpty) elementInspectorEmpty.hidden = false;
  if (elementTools) elementTools.hidden = true;
  if (photoTools) photoTools.hidden = true;
});

$("#elementFont")?.addEventListener("change", (event) => {
  if (!selectedEditableElement) return;
  selectedEditableElement.style.fontFamily = event.target.value;
  commitElementStyle();
});
$("#elementFontSize")?.addEventListener("input", (event) => {
  if (!selectedEditableElement) return;
  const points = Math.max(5, Math.min(96, Number(event.target.value) || 10));
  if (selectedEditableElement.classList.contains("resume-edit-block")) {
    const pageWidth = Number(selectedEditableElement.dataset.pageWidth) || 612;
    selectedEditableElement.style.fontSize = `${(points / pageWidth * 100).toFixed(4)}cqw`;
    selectedEditableElement.dataset.fontSizePoints = String(points);
  } else {
    selectedEditableElement.style.fontSize = `${points}pt`;
  }
  commitElementStyle();
});
$("#elementColor")?.addEventListener("input", (event) => {
  if (!selectedEditableElement) return;
  selectedEditableElement.style.setProperty("--edit-color", event.target.value);
  selectedEditableElement.style.color = event.target.value;
  elementInspector?.style.setProperty("--element-color", event.target.value);
  commitElementStyle();
});
$("#elementLineHeight")?.addEventListener("input", (event) => {
  if (!selectedEditableElement) return;
  selectedEditableElement.style.lineHeight = event.target.value;
  if ($("#elementLineHeightValue")) $("#elementLineHeightValue").value = Number(event.target.value).toFixed(2);
  commitElementStyle();
});
$$('[data-element-align]').forEach((button) => button.addEventListener("click", () => {
  if (!selectedEditableElement) return;
  selectedEditableElement.style.textAlign = button.dataset.elementAlign;
  $$('[data-element-align]').forEach((item) => item.classList.toggle("active", item === button));
  commitElementStyle();
}));
$$('[data-element-style]').forEach((button) => button.addEventListener("click", () => {
  if (!selectedEditableElement) return;
  const active = button.classList.toggle("active");
  if (button.dataset.elementStyle === "bold") selectedEditableElement.style.fontWeight = active ? "700" : "400";
  if (button.dataset.elementStyle === "italic") selectedEditableElement.style.fontStyle = active ? "italic" : "normal";
  if (button.dataset.elementStyle === "underline") selectedEditableElement.style.textDecoration = active ? "underline" : "none";
  commitElementStyle();
}));

function applyResumeTheme(themeKey) {
  const resume = $(".resume-document");
  const theme = resumeThemes[themeKey] || resumeThemes.black;
  if (!resume) return;
  resume.style.setProperty("--resume-accent", theme.accent);
  resume.style.setProperty("--resume-dark", theme.dark);
  resume.style.setProperty("--resume-paper", theme.paper);
  $$("[data-resume-theme]").forEach((item) => item.classList.toggle("active", item.dataset.resumeTheme === themeKey));
}

if (editableResume) applyResumeTheme(productColor);

$$("[data-resume-theme]").forEach((button) => {
  button.addEventListener("click", () => {
    applyResumeTheme(button.dataset.resumeTheme);
  });
});

$("#headingSize")?.addEventListener("input", (event) => {
  $(".resume-document")?.style.setProperty("--resume-title", `${event.target.value}px`);
});
$("#lineSpacing")?.addEventListener("input", (event) => {
  $(".resume-document")?.style.setProperty("--resume-line", event.target.value);
});

$("#photoToggle")?.addEventListener("click", (event) => {
  event.currentTarget.classList.toggle("on");
  const enabled = event.currentTarget.classList.contains("on");
  event.currentTarget.setAttribute("aria-pressed", String(enabled));
  $(".resume-document")?.classList.toggle("photo-hidden", !enabled);
  showToast(enabled ? "Profile photo enabled" : "Profile photo hidden");
});

$("#typeface")?.addEventListener("change", (event) => {
  const resume = $(".resume-document");
  if (resume) resume.style.fontFamily = `"${event.target.value}", sans-serif`;
});

$$('.resume-document [contenteditable="true"]').forEach((field) => {
  field.addEventListener("input", () => {
    const saved = $(".save-state span:last-child");
    if (!saved) return;
    saved.textContent = "Saving…";
    clearTimeout(field._saveTimer);
    field._saveTimer = setTimeout(() => { saved.textContent = "Saved"; }, 500);
  });
});

let zoom = 100;
function updateZoom() {
  const label = $("#zoomLabel");
  const resume = $(".resume-document");
  if (label) label.textContent = `${zoom}%`;
  if (resume && window.innerWidth > 560) resume.style.transform = `scale(${zoom / 100})`;
}
$("#zoomIn")?.addEventListener("click", () => { zoom = Math.min(120, zoom + 10); updateZoom(); });
$("#zoomOut")?.addEventListener("click", () => { zoom = Math.max(70, zoom - 10); updateZoom(); });

const downloadModal = $("#downloadModal");
const paymentConfig = {
  provider: "Creem",
  priceUsd: 5,
  downloadsPerPurchase: 3,
  ...(window.firstDraftPaymentConfig || {}),
};

function getDownloadCredits() {
  return accountState.authenticated ? Math.max(0, Number(accountState.user?.downloadCredits) || 0) : 0;
}

function updateDownloadUI() {
  const remaining = getDownloadCredits();
  const topLabel = $("#downloadButtonLabel");
  const action = $("#payDownload");
  const status = $("#downloadCreditStatus");
  if (topLabel) topLabel.textContent = remaining ? `Download PDF · ${remaining} left` : `${paymentConfig.downloadsPerPurchase} downloads · $${paymentConfig.priceUsd}`;
  if (action) action.textContent = !accountState.authenticated ? "Sign in to purchase" : remaining ? `Download PDF · ${remaining} remaining` : `Pay $${paymentConfig.priceUsd} with ${paymentConfig.provider}`;
  if (status) status.innerHTML = !accountState.authenticated
    ? `<span>Save downloads to your account</span><strong>Sign in</strong>`
    : remaining
    ? `<span>Your download balance</span><strong>${remaining} of ${paymentConfig.downloadsPerPurchase} left</strong>`
    : `<span>${paymentConfig.downloadsPerPurchase}-download pack</span><strong>$${Number(paymentConfig.priceUsd).toFixed(2)}</strong>`;
  downloadModal?.classList.toggle("has-credits", remaining > 0);
}

async function exportResumeAsPdf() {
  const remaining = getDownloadCredits();
  if (!remaining) return false;
  const result = await apiRequest("/api/downloads/claim", {
    method: "POST",
    body: JSON.stringify({ templateId: selectedTemplateKey }),
  });
  accountState.user.downloadCredits = result.remaining;
  renderAccountAccess();
  updateDownloadUI();
  setDownloadModal(false);
  showToast(`PDF export opened · ${result.remaining} download${result.remaining === 1 ? "" : "s"} left`);
  requestAnimationFrame(() => window.print());
  return true;
}

async function syncCreditsAfterCheckout() {
  const action = $("#payDownload");
  if (action) action.textContent = "Confirming payment…";
  for (let attempt = 0; attempt < 15; attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, attempt ? 1000 : 350));
    await loadAccount(true);
    if (getDownloadCredits() > 0) {
      updateDownloadUI();
      setDownloadModal(true);
      showToast(`${getDownloadCredits()} PDF downloads are ready`);
      return;
    }
  }
  updateDownloadUI();
  showToast("Payment received. Your downloads will appear shortly.");
}

function clearPaymentReturnParams() {
  const url = new URL(window.location.href);
  ["payment", "checkout_id", "order_id", "customer_id", "product_id"].forEach((key) => url.searchParams.delete(key));
  window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
}

function setDownloadModal(open) {
  if (!downloadModal) return;
  loadAccount(true).then(updateDownloadUI);
  downloadModal.classList.toggle("open", open);
  downloadModal.setAttribute("aria-hidden", String(!open));
  document.body.classList.toggle("download-open", open);
}
$("#downloadPdf")?.addEventListener("click", () => setDownloadModal(true));
$$("[data-close-download]").forEach((button) => button.addEventListener("click", () => setDownloadModal(false)));
$("#payDownload")?.addEventListener("click", async (event) => {
  const action = event.currentTarget;
  action.disabled = true;
  try {
    await loadAccount(true);
    if (!accountState.authenticated) {
      window.location.assign(`account.html?next=${encodeURIComponent(accountReturnUrl())}`);
      return;
    }
    if (await exportResumeAsPdf()) return;
    action.textContent = "Opening secure checkout…";
    const checkout = await apiRequest("/api/checkout", { method: "POST", body: "{}" });
    window.location.assign(checkout.checkoutUrl);
  } catch (error) {
    showToast(error.message);
  } finally {
    action.disabled = false;
    updateDownloadUI();
  }
});
window.addEventListener("load", () => {
  const returnedFromPayment = pageParams.get("payment") === "success" || pageParams.has("checkout_id");
  loadAccount(true).then(() => {
    updateDownloadUI();
    if (returnedFromPayment) {
      clearPaymentReturnParams();
      syncCreditsAfterCheckout();
    }
  });
});
updateDownloadUI();
document.addEventListener("keydown", (event) => { if (event.key === "Escape") setDownloadModal(false); });
$("#previewButton")?.addEventListener("click", () => {
  $(".builder-sidebar--left")?.classList.toggle("preview-hidden");
  $(".builder-sidebar--right")?.classList.toggle("preview-hidden");
  showToast("Preview mode toggled");
});

$$(".faq-question").forEach((button) => {
  button.addEventListener("click", () => {
    const item = button.closest(".faq-item");
    const open = item.classList.toggle("open");
    button.setAttribute("aria-expanded", String(open));
  });
});

const articleCards = $$(".article-card");
const categoryButtons = $$("[data-article-filter]");
categoryButtons.forEach((button) => {
  button.addEventListener("click", () => {
    categoryButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    const filter = button.dataset.articleFilter;
    articleCards.forEach((card) => {
      card.classList.toggle("is-hidden", filter !== "all" && card.dataset.category !== filter);
    });
  });
});

$("#joinEdit")?.addEventListener("click", () => showToast("Thanks — newsletter signup is coming soon"));
