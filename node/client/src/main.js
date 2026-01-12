import "./style.css";

const app = document.querySelector("#app");

app.innerHTML = `
  <h1>Encrypted Bitwarden Viewer <span class="badge">client-only</span></h1>
  <p class="small">
    Drag & drop your <code>*_reipur_encrypted.json</code> file here to view its contents in your browser.
    Nothing is uploaded anywhere.
  </p>

  <label class="dropzone" id="dropzone" for="fileInput">
    <strong>Drop JSON file here</strong><br/>
    <span class="small">or click to choose a file</span>
    <input id="fileInput" type="file" accept="application/json,.json" />
  </label>

  <div class="row">
    <div class="card">
      <h2>Summary</h2>
      <div id="summary" class="small">No file loaded.</div>
      <div style="margin-top:0.75rem; display:flex; gap:0.5rem; flex-wrap:wrap;">
        <button id="copyJson" disabled>Copy JSON</button>
        <button id="downloadJson" disabled>Download JSON</button>
      </div>
    </div>

    <div class="card">
      <h2>Preview</h2>
      <pre id="preview">(drop a file)</pre>
    </div>
  </div>
`;

const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const preview = document.getElementById("preview");
const summary = document.getElementById("summary");
const copyBtn = document.getElementById("copyJson");
const dlBtn = document.getElementById("downloadJson");

let lastJsonText = "";

function setLoadedState(enabled) {
  copyBtn.disabled = !enabled;
  dlBtn.disabled = !enabled;
}

function summarize(obj) {
  const encrypted = obj?.encrypted;
  const itemCount = Array.isArray(obj?.items) ? obj.items.length : 0;

  let encryptedPasswords = 0;
  let encryptedFieldValues = 0;

  if (Array.isArray(obj?.items)) {
    for (const item of obj.items) {
      if (item?.type === 1 && item?.login?.password?.startsWith?.("fernet:")) {
        encryptedPasswords++;
      }
      if (Array.isArray(item?.fields)) {
        for (const f of item.fields) {
          if (f?.value?.startsWith?.("fernet:")) encryptedFieldValues++;
        }
      }
    }
  }

  return `
    <div><strong>encrypted:</strong> ${String(encrypted)}</div>
    <div><strong>items:</strong> ${itemCount}</div>
    <div><strong>encrypted passwords:</strong> ${encryptedPasswords}</div>
    <div><strong>encrypted field values:</strong> ${encryptedFieldValues}</div>
  `;
}

async function handleFile(file) {
  if (!file) return;

  try {
    const text = await file.text();

    // Basic size guard (avoid freezing browser on huge files)
    if (text.length > 20_000_000) {
      throw new Error("File too large for in-browser preview (>20MB).");
    }

    const obj = JSON.parse(text);
    lastJsonText = JSON.stringify(obj, null, 2);

    summary.innerHTML = summarize(obj);
    preview.textContent = lastJsonText;
    setLoadedState(true);
  } catch (e) {
    lastJsonText = "";
    setLoadedState(false);
    summary.textContent = "Failed to load file.";
    preview.textContent = String(e?.message || e);
  }
}

dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
  const file = e.dataTransfer?.files?.[0];
  handleFile(file);
});

fileInput.addEventListener("change", () => {
  handleFile(fileInput.files?.[0]);
});

copyBtn.addEventListener("click", async () => {
  if (!lastJsonText) return;
  await navigator.clipboard.writeText(lastJsonText);
});

dlBtn.addEventListener("click", () => {
  if (!lastJsonText) return;
  const blob = new Blob([lastJsonText], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "preview.json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
});