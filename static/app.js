/* Framework Brief Desk */
const AXIOXMEDIA_BRAND = "Axiox Media";
const AIO_WATERMARK = "axioxmedia";

let schema = null;
let lang = "zh";
let projectId = null;
let data = {};
let currentStep = 0;
let currentSub = 0;
let saveTimer = null;
let visited = new Set([0]);

function detectUiLang() {
  const stored = localStorage.getItem("aio.uiLang");
  if (stored === "zh" || stored === "en") return stored;
  return (navigator.language || "zh").toLowerCase().startsWith("zh") ? "zh" : "en";
}

function tNode(node) {
  if (!node) return "";
  if (typeof node === "string") return node;
  return node[lang] || node.zh || node.en || "";
}

function ui(key) {
  return tNode((schema && schema.ui && schema.ui[key]) || {});
}

function steps() {
  const type = data.docType === "business" ? "business" : "game";
  return type === "business" ? schema.businessSteps : schema.gameSteps;
}

function stepAt(i) {
  return steps()[i];
}

function applyI18n() {
  if (!schema) return;
  document.getElementById("appTitle").textContent = tNode(schema.ui.appTitle);
  document.getElementById("appSubtitle").textContent = tNode(schema.ui.appSubtitle);
  document.getElementById("btnNew").textContent = ui("newProject");
  document.getElementById("btnOpen").textContent = ui("load");
  document.getElementById("btnBack").textContent = ui("back");
  document.getElementById("btnNext").textContent = ui("next");
  document.getElementById("btnPreset").textContent = ui("applyPreset");
  document.getElementById("btnImport").textContent = ui("importJson");
  document.getElementById("importTitle").textContent = ui("importTitle");
  document.getElementById("importPick").textContent = ui("importPick");
  document.getElementById("importClose").textContent = ui("importClose");
  document.getElementById("addOptTitle").textContent = ui("addOption");
  document.getElementById("addOptOk").textContent = ui("addConfirm");
  document.getElementById("addOptCancel").textContent = ui("addCancel");
  const expect = data.docType === "business" ? "business" : "game";
  document.getElementById("importLead").textContent = expect === "business" ? ui("importLeadBiz") : ui("importLeadGame");
  document.querySelector('[data-export="step-json"]').textContent = ui("exportStepJson");
  document.querySelector('[data-export="step-docx"]').textContent = ui("exportStepDocx");
  document.querySelector('[data-export="step-pdf"]').textContent = ui("exportStepPdf");
  document.getElementById("fullJson").textContent = ui("exportFullJson");
  document.getElementById("fullDocx").textContent = ui("exportFullDocx");
  document.getElementById("fullPdf").textContent = ui("exportFullPdf");
  document.getElementById("openTitle").textContent = ui("load");
  document.querySelectorAll("[data-ui-lang]").forEach((btn) => {
    btn.classList.toggle("on", btn.getAttribute("data-ui-lang") === lang);
  });
}

function hideAllStages() {
  /* single card reused */
}

function renderStepNav() {
  const nav = document.getElementById("stepNav");
  nav.innerHTML = "";
  steps().forEach((s, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "step-pill";
    if (i === currentStep) b.classList.add("on");
    if (visited.has(i) && i !== currentStep) b.classList.add("done");
    b.textContent = s.no + " " + tNode(s.title);
    b.addEventListener("click", () => goStep(i));
    nav.appendChild(b);
  });
}

function visibleFields(step) {
  const docType = data.docType || "game";
  return (step.fields || []).filter((f) => !f.when || f.when === docType);
}

function setVal(key, value) {
  data[key] = value;
  scheduleSave();
  if (key === "docType") {
    currentStep = Math.min(currentStep, steps().length - 1);
    renderStepNav();
    paintCard();
  }
}

function scheduleSave() {
  const chip = document.getElementById("saveChip");
  chip.textContent = ui("saving");
  chip.classList.remove("ok");
  clearTimeout(saveTimer);
  saveTimer = setTimeout(persist, 400);
}

async function persist() {
  if (!projectId) return;
  const res = await fetch("/api/project/" + projectId, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      data,
      step: (stepAt(currentStep) || {}).id || "",
      sub: ((stepAt(currentStep) || {}).subs || [])[currentSub]?.id || "",
      lang,
    }),
  });
  if (res.ok) {
    const chip = document.getElementById("saveChip");
    chip.textContent = ui("saved");
    chip.classList.add("ok");
  }
}

function choiceClass(on) {
  return "choice" + (on ? " on" : "");
}

function customBucket(key) {
  if (!data.__customOptions || typeof data.__customOptions !== "object") data.__customOptions = {};
  if (!Array.isArray(data.__customOptions[key])) data.__customOptions[key] = [];
  return data.__customOptions[key];
}

function fieldOptions(f) {
  const base = Array.isArray(f.options) ? f.options.slice() : [];
  const extra = customBucket(f.key);
  const seen = new Set(base.map((o) => o.id));
  extra.forEach((o) => {
    if (o && o.id && !seen.has(o.id)) {
      base.push(o);
      seen.add(o.id);
    }
  });
  return base;
}

let addOptTarget = null;

function openAddOption(field) {
  addOptTarget = field;
  document.getElementById("addOptTitle").textContent = ui("addOption");
  document.getElementById("addOptLead").textContent = ui("addPrompt") + " — " + tNode(field.label);
  document.getElementById("addOptOk").textContent = ui("addConfirm");
  document.getElementById("addOptCancel").textContent = ui("addCancel");
  document.getElementById("addOptAlert").textContent = "";
  document.getElementById("addOptInput").value = "";
  document.getElementById("addOptModal").classList.add("on");
  setTimeout(() => document.getElementById("addOptInput").focus(), 30);
}

function slugOption(label) {
  const raw = String(label || "").trim();
  const ascii = raw.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
  return "custom_" + (ascii || Date.now().toString(36));
}

function confirmAddOption() {
  if (!addOptTarget) return;
  const label = document.getElementById("addOptInput").value.trim();
  if (!label) {
    document.getElementById("addOptAlert").textContent = ui("addPrompt");
    return;
  }
  const key = addOptTarget.key;
  const bucket = customBucket(key);
  let id = slugOption(label);
  const used = new Set(fieldOptions(addOptTarget).map((o) => o.id));
  while (used.has(id)) id = id + "_" + Math.floor(Math.random() * 99);
  bucket.push({ id, zh: label, en: label });
  data.__customOptions[key] = bucket;
  if (addOptTarget.kind === "check") {
    const cur = Array.isArray(data[key]) ? data[key].slice() : [];
    if (!cur.includes(id)) cur.push(id);
    data[key] = cur;
  } else {
    data[key] = id;
  }
  document.getElementById("addOptModal").classList.remove("on");
  addOptTarget = null;
  scheduleSave();
  paintCard();
}

function makeAddButton(field) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "choice choice-add";
  btn.textContent = "+";
  btn.title = ui("addOption");
  btn.addEventListener("click", (ev) => {
    ev.preventDefault();
    openAddOption(field);
  });
  return btn;
}

function renderField(f) {
  const wrap = document.createElement("div");
  wrap.className = "field-block";
  const title = document.createElement("div");
  title.className = "field-title";
  title.textContent = tNode(f.label);
  const hint = document.createElement("div");
  hint.className = "field-hint";
  hint.textContent = tNode(f.hint);
  wrap.appendChild(title);
  wrap.appendChild(hint);

  const kind = f.kind;
  const key = f.key;
  const val = data[key];

  if (kind === "text" || kind === "number") {
    const input = document.createElement("input");
    input.type = kind === "number" ? "number" : "text";
    input.value = val == null ? "" : val;
    input.placeholder = tNode(f.placeholder || {});
    input.addEventListener("input", () => setVal(key, kind === "number" ? Number(input.value) : input.value));
    wrap.appendChild(input);
  } else if (kind === "textarea") {
    const ta = document.createElement("textarea");
    ta.value = val == null ? "" : val;
    ta.addEventListener("input", () => setVal(key, ta.value));
    wrap.appendChild(ta);
  } else if (kind === "select") {
    const row = document.createElement("div");
    row.className = "choice-row";
    if (key !== "docType") row.appendChild(makeAddButton(f));
    const sel = document.createElement("select");
    const empty = document.createElement("option");
    empty.value = "";
    empty.textContent = "—";
    sel.appendChild(empty);
    fieldOptions(f).forEach((opt) => {
      const o = document.createElement("option");
      o.value = opt.id;
      o.textContent = tNode(opt);
      sel.appendChild(o);
    });
    sel.value = val || "";
    sel.addEventListener("change", () => setVal(key, sel.value));
    sel.style.flex = "1";
    sel.style.minWidth = "220px";
    row.appendChild(sel);
    wrap.appendChild(row);
  } else if (kind === "radio") {
    const row = document.createElement("div");
    row.className = "choice-row";
    if (key !== "docType") row.appendChild(makeAddButton(f));
    fieldOptions(f).forEach((opt) => {
      const lab = document.createElement("label");
      lab.className = choiceClass(val === opt.id);
      const inp = document.createElement("input");
      inp.type = "radio";
      inp.name = key;
      inp.value = opt.id;
      inp.checked = val === opt.id;
      lab.appendChild(inp);
      lab.appendChild(document.createTextNode(tNode(opt)));
      lab.addEventListener("click", (ev) => {
        ev.preventDefault();
        setVal(key, opt.id);
        paintCard();
      });
      row.appendChild(lab);
    });
    wrap.appendChild(row);
  } else if (kind === "check") {
    const row = document.createElement("div");
    row.className = "choice-row";
    if (key !== "docType") row.appendChild(makeAddButton(f));
    const selected = Array.isArray(val) ? val : [];
    fieldOptions(f).forEach((opt) => {
      const lab = document.createElement("label");
      const on = selected.includes(opt.id);
      lab.className = choiceClass(on);
      const inp = document.createElement("input");
      inp.type = "checkbox";
      inp.checked = on;
      lab.appendChild(inp);
      lab.appendChild(document.createTextNode(tNode(opt)));
      lab.addEventListener("click", (ev) => {
        ev.preventDefault();
        const next = new Set(Array.isArray(data[key]) ? data[key] : []);
        if (next.has(opt.id)) next.delete(opt.id);
        else next.add(opt.id);
        setVal(key, Array.from(next));
        paintCard();
      });
      row.appendChild(lab);
    });
    wrap.appendChild(row);
  } else if (kind === "range") {
    const input = document.createElement("input");
    input.type = "range";
    input.min = f.min || 1;
    input.max = f.max || 5;
    input.value = val == null ? 3 : val;
    const read = document.createElement("div");
    read.className = "field-hint";
    read.textContent = String(input.value);
    input.addEventListener("input", () => {
      setVal(key, Number(input.value));
      read.textContent = input.value;
    });
    wrap.appendChild(input);
    wrap.appendChild(read);
  }
  return wrap;
}

function paintCard() {
  const step = stepAt(currentStep);
  if (!step) return;
  document.getElementById("cardKicker").textContent = "STEP " + step.no;
  document.getElementById("cardTitle").textContent = tNode(step.title);
  document.getElementById("cardLead").textContent = tNode(step.lead);
  document.getElementById("cardAlert").textContent = "";

  const last = currentStep === steps().length - 1;
  document.getElementById("fullJson").hidden = !last;
  document.getElementById("fullDocx").hidden = !last;
  document.getElementById("fullPdf").hidden = !last;
  document.getElementById("btnBack").disabled = currentStep === 0;
  document.getElementById("btnNext").disabled = last;
  document.getElementById("btnPreset").hidden = !(step.id === "charter" && data.docType !== "business");
  document.getElementById("btnImport").hidden = step.id !== "charter";

  const rail = document.getElementById("subRail");
  const mount = document.getElementById("formMount");
  mount.innerHTML = "";
  if (step.subs && step.subs.length) {
    rail.hidden = false;
    rail.innerHTML = "";
    step.subs.forEach((sub, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "sub-pill" + (i === currentSub ? " on" : "");
      b.textContent = sub.no + " " + tNode(sub.title);
      b.addEventListener("click", () => {
        currentSub = i;
        paintCard();
      });
      rail.appendChild(b);
    });
    const hint = document.createElement("div");
    hint.className = "field-hint";
    hint.textContent = ui("subHint");
    mount.appendChild(hint);
    const sub = step.subs[currentSub] || step.subs[0];
    (sub.fields || []).forEach((f) => mount.appendChild(renderField(f)));
    const extra = document.createElement("div");
    extra.className = "actions";
    ["json", "docx", "pdf"].forEach((fmt) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "soft";
      btn.textContent = ui("exportSub" + fmt[0].toUpperCase() + fmt.slice(1)) || ("sub " + fmt);
      btn.addEventListener("click", () => doExport("sub", fmt));
      extra.appendChild(btn);
    });
    mount.appendChild(extra);
  } else {
    rail.hidden = true;
    rail.innerHTML = "";
    visibleFields(step).forEach((f) => mount.appendChild(renderField(f)));
  }
  applyI18n();
}

function goStep(n) {
  const max = steps().length - 1;
  currentStep = Math.max(0, Math.min(n, max));
  currentSub = 0;
  visited.add(currentStep);
  hideAllStages();
  document.getElementById("stageCard").classList.add("on");
  renderStepNav();
  paintCard();
  applyI18n();
  scheduleSave();
}

function requiredOk() {
  const step = stepAt(currentStep);
  const fields = step.subs ? (step.subs[currentSub] || {}).fields || [] : visibleFields(step);
  for (const f of fields) {
    if (!f.required) continue;
    const v = data[f.key];
    if (v == null || v === "" || (Array.isArray(v) && !v.length)) return false;
  }
  return true;
}

async function ensureProject() {
  if (projectId) return;
  const res = await fetch("/api/project/new", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ docType: data.docType || "game", projectName: data.projectName || "" }),
  });
  const doc = await res.json();
  projectId = doc.id;
  data = Object.assign({}, doc.data || {}, data);
}

function toast(text, ok) {
  const chip = document.getElementById("saveChip");
  chip.textContent = text;
  chip.classList.toggle("ok", !!ok);
}

async function pickSavePath(filename) {
  try {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.pick_save) {
      const path = await window.pywebview.api.pick_save(filename);
      return path || "";
    }
  } catch (err) {
    /* fall through */
  }
  if (window.showSaveFilePicker) {
    try {
      const handle = await window.showSaveFilePicker({
        suggestedName: filename,
      });
      return handle;
    } catch (err) {
      if (err && err.name === "AbortError") return "";
    }
  }
  return null;
}

async function writePickedHandle(handle, token) {
  const fileRes = await fetch("/api/export/file/" + token);
  const blob = await fileRes.blob();
  const writable = await handle.createWritable();
  await writable.write(blob);
  await writable.close();
}

async function doExport(scope, format) {
  await persist();
  const step = stepAt(currentStep);
  document.getElementById("loading").classList.add("on");
  document.getElementById("loadingText").textContent = format.toUpperCase();
  try {
    const res = await fetch("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: projectId,
        scope,
        step: step.id,
        sub: (step.subs || [])[currentSub]?.id || "",
        format,
        lang,
      }),
    });
    const out = await res.json();
    if (!res.ok || !out.token) {
      toast(ui("exportFail"), false);
      return;
    }
    const picked = await pickSavePath(out.filename);
    if (picked === "") {
      toast(ui("exportCancel"), false);
      return;
    }
    if (typeof picked === "string") {
      const saved = await fetch("/api/export/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: out.token, path: picked }),
      });
      if (!saved.ok) {
        toast(ui("exportFail"), false);
        return;
      }
      toast(ui("exportSaved"), true);
      return;
    }
    if (picked && typeof picked.createWritable === "function") {
      await writePickedHandle(picked, out.token);
      toast(ui("exportSaved"), true);
      return;
    }
    const fileRes = await fetch(out.url);
    const blob = await fileRes.blob();
    const objectUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = out.filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(objectUrl), 2000);
    toast(ui("exportSaved"), true);
  } catch (err) {
    toast(ui("exportFail"), false);
  } finally {
    document.getElementById("loading").classList.remove("on");
  }
}

async function openList() {
  const res = await fetch("/api/projects");
  const out = await res.json();
  const box = document.getElementById("projList");
  box.innerHTML = "";
  if (!out.items.length) {
    box.textContent = ui("emptySave");
  }
  out.items.forEach((it) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "proj-item";
    b.textContent = (it.projectName || it.id) + " · " + it.docType + " · " + (it.updated || "");
    b.addEventListener("click", async () => {
      const rec = await (await fetch("/api/project/" + it.id)).json();
      projectId = rec.id;
      data = rec.data || {};
      currentStep = 0;
      visited = new Set([0]);
      document.getElementById("openModal").classList.remove("on");
      goStep(0);
    });
    box.appendChild(b);
  });
  document.getElementById("openModal").classList.add("on");
}

function typeName(code) {
  const node = schema && schema.typeLabel && schema.typeLabel[code];
  return tNode(node) || code;
}

function mismatchText(found, expected) {
  if (lang === "en") {
    return `JSON import failed: the file is a ${typeName(found)}. Please import a ${typeName(expected)} file.`;
  }
  return `json导入失败，原因是导入了${typeName(found)}的json文件，请确认导入的是 ${typeName(expected)} 文件`;
}

function showImportError(text) {
  const el = document.getElementById("importError");
  el.hidden = !text;
  el.textContent = text || "";
}

function openImport() {
  showImportError("");
  document.getElementById("importFile").value = "";
  applyI18n();
  document.getElementById("importModal").classList.add("on");
}

async function handleImportFile(ev) {
  const file = ev.target.files && ev.target.files[0];
  ev.target.value = "";
  if (!file) return;
  let payload;
  try {
    payload = JSON.parse(await file.text());
  } catch (err) {
    showImportError(ui("importBadFile"));
    return;
  }
  const expected = data.docType === "business" ? "business" : "game";
  const res = await fetch("/api/project/" + projectId + "/import", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ payload, expected }),
  });
  let body = {};
  try {
    body = await res.json();
  } catch (err) {
    body = {};
  }
  if (!res.ok) {
    const detail = body.detail || body;
    const found = detail.found || "unknown";
    const expect = detail.expected || expected;
    if (detail.code === "unknown") {
      showImportError(mismatchText("unknown", expect));
    } else {
      showImportError(mismatchText(found, expect));
    }
    return;
  }
  data = body.data || data;
  showImportError("");
  document.getElementById("importModal").classList.remove("on");
  const chip = document.getElementById("saveChip");
  chip.textContent = ui("importOk");
  chip.classList.add("ok");
  renderStepNav();
  paintCard();
}

async function boot() {
  lang = detectUiLang();
  const def = await (await fetch("/api/defaults")).json();
  document.getElementById("appVersion").textContent = "v" + def.version;
  schema = await (await fetch("/api/schema")).json();
  applyI18n();
  await ensureProject();
  goStep(0);

  document.getElementById("uiLangSwitch").addEventListener("click", (ev) => {
    const btn = ev.target.closest("[data-ui-lang]");
    if (!btn) return;
    lang = btn.getAttribute("data-ui-lang");
    localStorage.setItem("aio.uiLang", lang);
    applyI18n();
    renderStepNav();
    paintCard();
  });
  document.getElementById("btnBack").addEventListener("click", () => goStep(currentStep - 1));
  document.getElementById("btnNext").addEventListener("click", () => {
    if (!requiredOk()) {
      document.getElementById("cardAlert").textContent = ui("langNeed");
      return;
    }
    goStep(currentStep + 1);
  });
  document.getElementById("btnNew").addEventListener("click", async () => {
    projectId = null;
    data = { docType: "game" };
    visited = new Set([0]);
    await ensureProject();
    goStep(0);
  });
  document.getElementById("btnOpen").addEventListener("click", openList);
  document.getElementById("btnImport").addEventListener("click", openImport);
  document.getElementById("importClose").addEventListener("click", () => {
    document.getElementById("importModal").classList.remove("on");
  });
  document.getElementById("importPick").addEventListener("click", () => {
    document.getElementById("importFile").click();
  });
  document.getElementById("importFile").addEventListener("change", handleImportFile);
  document.getElementById("addOptOk").addEventListener("click", confirmAddOption);
  document.getElementById("addOptCancel").addEventListener("click", () => {
    document.getElementById("addOptModal").classList.remove("on");
    addOptTarget = null;
  });
  document.getElementById("addOptInput").addEventListener("keydown", (ev) => {
    if (ev.key === "Enter") confirmAddOption();
  });
  document.getElementById("closeOpen").addEventListener("click", () => {
    document.getElementById("openModal").classList.remove("on");
  });
  document.getElementById("btnPreset").addEventListener("click", async () => {
    if (!data.genre) return;
    const rec = await (
      await fetch("/api/project/" + projectId + "/preset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ genre: data.genre }),
      })
    ).json();
    data = rec.data || data;
    const chip = document.getElementById("saveChip");
    chip.textContent = ui("presetApplied");
    chip.classList.add("ok");
    paintCard();
  });
  document.querySelectorAll("[data-export]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const [scope, format] = btn.getAttribute("data-export").split("-");
      doExport(scope, format);
    });
  });
}

boot().catch((err) => {
  document.getElementById("cardAlert").textContent = String(err);
});
