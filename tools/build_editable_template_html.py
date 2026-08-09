#!/usr/bin/env python3
"""Export every imported Word resume to same-origin editable HTML."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import build_template_catalog as catalog


ROOT = catalog.ROOT
OUTPUT_ROOT = ROOT / "assets" / "template-html"
SOFFICE = Path("/Users/chengwuxue/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/soffice")


EDITOR_STYLE = """
<meta name="viewport" content="width=794, initial-scale=1">
<style id="first-draft-editor">
  html { width: 794px; min-height: 1122px; margin: 0; background: #fff; }
  body { width: 794px; min-height: 1122px; margin: 0; overflow: hidden; outline: none; background: #fff; }
  body:focus { outline: none; }
  img { pointer-events: none !important; user-select: none !important; }
  .sd-abs-pos, .sd-abs-pos img { z-index: 0 !important; }
  [data-edit-block] { position: relative !important; z-index: 3 !important; cursor: text; caret-color: #0071e3; transition: outline-color .15s ease, background .15s ease; }
  [data-edit-block]:hover { outline: 2px dashed rgba(0,113,227,.58); outline-offset: 2px; background: rgba(255,255,255,.1); }
  [data-edit-block]:focus { outline: 2px solid #0071e3; outline-offset: 2px; background: rgba(255,255,255,.16); }
</style>
<script id="first-draft-editor-script">
document.addEventListener('DOMContentLoaded', function () {
  document.body.contentEditable = 'false';
  var candidates = document.querySelectorAll('p');
  var index = 0;
  var editableBlocks = [];
  candidates.forEach(function (block) {
    if (!block.innerText || !block.innerText.trim()) return;
    block.contentEditable = 'true';
    block.spellcheck = true;
    block.dataset.editBlock = 'edit-' + (++index);
    editableBlocks.push({ id: block.dataset.editBlock, text: block.innerText });
    block.addEventListener('focus', function () {
      window.parent.postMessage({ source: 'first-draft-template', type: 'selection', id: block.dataset.editBlock, text: block.innerText }, '*');
    });
    block.addEventListener('input', function () {
      window.parent.postMessage({ source: 'first-draft-template', type: 'changed', id: block.dataset.editBlock, text: block.innerText }, '*');
    });
  });
  window.addEventListener('message', function (event) {
    var message = event.data || {};
    if (message.source !== 'first-draft-builder' || message.type !== 'update') return;
    var target = document.querySelector('[data-edit-block="' + message.id + '"]');
    if (target) {
      target.innerText = message.text;
      window.parent.postMessage({ source: 'first-draft-template', type: 'changed', id: message.id, text: target.innerText }, '*');
    }
  });
  window.parent.postMessage({ source: 'first-draft-template', type: 'ready', count: index, blocks: editableBlocks }, '*');
});
</script>
"""


def export_one(item: tuple[str, Path]) -> tuple[str, str | None]:
    template_id, source = item
    output_dir = OUTPUT_ROOT / template_id
    index_path = output_dir / "index.html"
    if index_path.exists() and index_path.stat().st_mtime >= max(source.stat().st_mtime, Path(__file__).stat().st_mtime):
        return template_id, None

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"first-draft-{template_id}-") as temp_name:
        temp_dir = Path(temp_name)
        copied_docx = temp_dir / f"{template_id}.docx"
        profile_dir = temp_dir / "lo-profile"
        shutil.copy2(source, copied_docx)
        command = [
            str(SOFFICE), "--headless", f"-env:UserInstallation={profile_dir.as_uri()}",
            "--convert-to", "html", "--outdir", str(output_dir), str(copied_docx),
        ]
        env = os.environ.copy()
        try:
            subprocess.run(command, cwd=ROOT, env=env, check=True, capture_output=True, text=True, timeout=120)
            generated = output_dir / f"{template_id}.html"
            if not generated.exists():
                return template_id, "LibreOffice did not create HTML"
            html = generated.read_text(encoding="utf-8", errors="replace")
            html = html.replace("<head>", f"<head>{EDITOR_STYLE}", 1)
            html = html.replace("<body ", '<body contenteditable="true" spellcheck="true" ', 1)
            html = html.replace("<body>", '<body contenteditable="true" spellcheck="true">', 1)
            index_path.write_text(html, encoding="utf-8")
            generated.unlink()
            return template_id, None
        except Exception as error:
            return template_id, str(error)


def main() -> int:
    paths = sorted((path for path in ROOT.rglob("*.docx") if catalog.is_resume_candidate(path)), key=catalog.natural_key)
    work = [(f"template-{index:03d}", path) for index, path in enumerate(paths, start=1)]
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    failures = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(export_one, item): item for item in work}
        for completed, future in enumerate(as_completed(futures), start=1):
            template_id, error = future.result()
            if error:
                failures.append((template_id, error))
            print(f"[{completed}/{len(work)}] {template_id}{' FAILED' if error else ''}", flush=True)
    if failures:
        for template_id, error in failures:
            print(f"FAILED {template_id}: {error}")
    return 0 if len(failures) < len(work) else 1


if __name__ == "__main__":
    raise SystemExit(main())
