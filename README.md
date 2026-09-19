<div align="center">

# Framework Brief Desk

**Packed via Axiox Media**

A local step wizard that turns a game framework or a short investor plan into JSON, DOCX, or PDF.

<p>
  <a href="docs/README-zh.md"><img src="https://img.shields.io/badge/中文说明-README--zh-e7c07a?style=for-the-badge" alt="Chinese README" /></a>
</p>

<p>
  <a href="#install">Install</a> ·
  <a href="#features">Features</a> ·
  <a href="#requirements">Requirements</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#documentation">FAQ</a>
</p>

<p>
  <img src="https://img.shields.io/badge/platform-Windows_10%2F11-0b0d12?style=flat-square" alt="Windows" />
  <img src="https://img.shields.io/badge/python-3.11%2B-e7c07a?style=flat-square" alt="Python" />
  <img src="https://img.shields.io/badge/ui-zh%20%2F%20en-7ee0c6?style=flat-square" alt="i18n" />
  <img src="https://img.shields.io/badge/export-JSON%20DOCX%20PDF-c9a227?style=flat-square" alt="export" />
</p>

</div>

<div align="center">
<img src="docs/APPCap.png" width="100%">
</div>

> [!NOTE]
> The Windows EXE is unsigned. SmartScreen may warn on first launch.

---

## At a glance

| Item | Value |
|---|---|
| Product | Framework Brief Desk |
| UI | Step wizard, zh / en |
| First choice | Game framework brief or investor plan |
| Export | Per step, per numeric sub-step, or full file |

<a id="install"></a>

## Install

### 1. GitHub Deploy Desk (recommended)

One-click deploy this repository with [GitHub Deploy Desk](https://github.com/axioxmedia/github-deployer).

1. Get the deployer: https://github.com/axioxmedia/github-deployer
2. Paste this repo URL into Deploy Desk.
3. Read the README in the app, then confirm deploy.

That is the supported install path. Use the source / EXE steps below only if you are already building from a local checkout.

### 2. Run from source or freeze an EXE

| Path | Command |
|---|---|
| Source | `start.bat` after Python 3.11+ |
| EXE | `build_exe.bat` → `dist\FrameworkBriefDesk.exe` |

<a id="features"></a>

## Features

| Action | Detail |
|---|---|
| Choose deliverable | Game framework brief or investor plan |
| Jump any step | Step rail stays visible |
| Autosave | Status chip shows saved state |
| Category library | Fourteen play-shape presets |
| Numeric subs | Growth, combat, economy, social, grants |
| Loop and habit | Closed-loop design plus offline recall |
| Export | JSON / DOCX / PDF per step or whole |

<a id="requirements"></a>

## Requirements

| | Minimum | Recommended |
|---|---|---|
| OS | Windows 10 | Windows 11 |
| Python | 3.11 | 3.12 |
| RAM | 4 GB | 8 GB |

<a id="architecture"></a>

## Architecture

```
pywebview window
    → FastAPI on 127.0.0.1
        → static wizard (schema-driven)
        → data/projects/*.json
        → exporter (json / docx / pdf)
```

<a id="documentation"></a>

## Documentation

<details>
<summary>Where are projects stored?</summary>

Next to the EXE under `data/projects`. Source runs use the project folder `data/`.

</details>

<details>
<summary>How do I add a screenshot to GitHub?</summary>

Drop `APPCap.png` into `docs/` locally, or upload it to `docs/` on the default branch.

</details>

Packed via Axiox Media · [axiox.media](https://axiox.media)
