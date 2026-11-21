#!/usr/bin/env node
// SPDX-License-Identifier: Apache-2.0
//
// GABBE installer (Python-independent).
//
// This is the PRIMARY installer for `npx gabbe-kit init`. It bundles the Markdown
// kit (agents/) and wires it into the current project using only the Node
// standard library -- no npm dependencies, no Python required.
//
// Safety rules (same as scripts/init.py and gabbe/installer.py):
//   - back up first, and never overwrite an existing backup;
//   - a file the user already had is kept; an instruction file gets a pointer
//     block instead of being replaced;
//   - everything written is recorded in .gabbe/manifest.json, so `gabbe uninstall`
//     removes exactly that and nothing else.
//
// Conventions mirror scripts/init.py and agents/scripts/compile_skills.py:
//   - safe_slug()                  -> compile_skills.py safe_slug()
//   - .agents/skills/<slug>/SKILL.md (agentskills.io "Universal" target)
//   - root AGENTS.md               -> agents.md open standard
//   - per-agent rule files         -> .claude/CLAUDE.md, .cursorrules, etc.
//
// Besides `init`, it has `update`, `uninstall` and `doctor`, so a user without Python can
// refresh and reverse an install. `uninstall` mirrors gabbe/installer.py (the reference).
//
// If `python3` is available the full interactive wizard (scripts/init.py) can
// be delegated to with `--wizard`, but the Node path works WITHOUT Python.

'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

// ---------------------------------------------------------------------------
// Paths / colors
// ---------------------------------------------------------------------------

// The bundled kit lives one level up from bin/ (the package root).
const KIT_ROOT = path.resolve(__dirname, '..');
const SOURCE_AGENTS_DIR = path.join(KIT_ROOT, 'agents');
// The project is the current folder, or the folder given with --dir (setProjectRoot, once, in main).
let PROJECT_ROOT = process.cwd();

const useColor = process.stdout.isTTY && !process.env.NO_COLOR;
const c = (code, s) => (useColor ? `[${code}m${s}[0m` : s);
const green = (s) => c('0;32', s);
const yellow = (s) => c('1;33', s);
const blue = (s) => c('0;34', s);
const red = (s) => c('0;31', s);

function log(msg) {
  process.stdout.write(msg + '\n');
}

// ---------------------------------------------------------------------------
// Agent registry: canonical name -> CLI alias(es) accepted in --agents
// ---------------------------------------------------------------------------

const AGENT_ALIASES = {
  claude: 'Claude Code',
  'claude-code': 'Claude Code',
  cursor: 'Cursor',
  windsurf: 'Windsurf',
  cline: 'Cline',
  aider: 'Aider',
  devin: 'Devin / Cognition',
  cognition: 'Devin / Cognition',
  gemini: 'Gemini',
  antigravity: 'Antigravity',
  opencode: 'OpenCode',
  zed: 'Zed',
  continue: 'Continue',
  roo: 'Roo Code',
  'roo-code': 'Roo Code',
  kilo: 'Kilo Code',
  'kilo-code': 'Kilo Code',
  codex: 'OpenAI / Codex',
  openai: 'OpenAI / Codex',
  copilot: 'GitHub Copilot',
  'github-copilot': 'GitHub Copilot',
  vscode: 'VS Code',
  'vs-code': 'VS Code',
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// Mirror of compile_skills.py safe_slug(): lowercase, collapse non [a-z0-9]
// runs into single hyphens, strip leading/trailing hyphens, prevent traversal.
function safeSlug(rawName, fallback) {
  let slug = (rawName || '').toLowerCase().trim();
  slug = slug.replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  if (!slug || slug === '.' || slug === '..') {
    const fb = String(fallback || 'skill')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
    slug = fb || 'skill';
  }
  return slug;
}

// Minimal YAML frontmatter reader: returns { name, description } parsed from a
// leading `---` block. Enough for slug + description; we never re-serialize.
function parseFrontmatter(content) {
  const meta = {};
  if (!content.startsWith('---')) return meta;
  const end = content.indexOf('---', 3);
  if (end === -1) return meta;
  const block = content.slice(3, end);
  for (const line of block.split('\n')) {
    const idx = line.indexOf(':');
    if (idx === -1) continue;
    const key = line.slice(0, idx).trim();
    let val = line.slice(idx + 1).trim();
    // Strip a single pair of surrounding quotes.
    if (
      (val.startsWith('"') && val.endsWith('"')) ||
      (val.startsWith("'") && val.endsWith("'"))
    ) {
      val = val.slice(1, -1);
    }
    if (key) meta[key] = val;
  }
  return meta;
}

// Idempotent: inject `gabbe-schema-version: 1` into a leading frontmatter block
// (matches compile_skills.py inject_schema_version()).
const GABBE_SCHEMA_VERSION = 1;
function injectSchemaVersion(content) {
  if (content.includes('gabbe-schema-version:')) return content;
  if (content.startsWith('---')) {
    const end = content.indexOf('---', 3);
    if (end !== -1) {
      const head = content.slice(0, 3);
      const block = content.slice(3, end).replace(/\n+$/, '');
      const tail = content.slice(end);
      return head + block + `\ngabbe-schema-version: ${GABBE_SCHEMA_VERSION}\n` + tail;
    }
  }
  return content;
}

// The agent-skills convention wants `name:` to equal the folder's lowercase-hyphen slug;
// a few kit skills carry a display name ("System Benchmark"). Only the first name line
// of the frontmatter is changed.
function withSlugName(content, slug) {
  if (!content.startsWith('---')) return content;
  const end = content.indexOf('---', 3);
  if (end === -1) return content;
  return content.slice(0, end).replace(/^name:[^\r\n]*/m, `name: ${slug}`) + content.slice(end);
}

function readOrEmpty(file) {
  try {
    return fs.readFileSync(file);
  } catch (e) {
    return Buffer.alloc(0);
  }
}

// Build leftovers of a used checkout (the npm package excludes them too): never copied.
function isBuildLeftover(name, isDir) {
  return isDir ? name === '__pycache__' : /\.py[co]$/.test(name);
}

function walk(dir) {
  const out = [];
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch (e) {
    return out;
  }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (isBuildLeftover(entry.name, entry.isDirectory())) continue;
    if (entry.isDirectory()) {
      out.push(...walk(full));
    } else if (entry.isFile()) {
      out.push(full);
    }
  }
  return out;
}

// PRESERVE_FILES mirrors init.py: never clobber user-authored content.
const PRESERVE_FILES = new Set([
  'AGENTS.md',
  'CONSTITUTION.md',
  'TASKS.md',
  'policies.yml',
  'config.json',
]);

function shouldPreserve(relPath, fileName) {
  const parts = relPath.split(path.sep);
  if (parts.includes('memory')) return true;
  if (parts.includes('project')) return true;
  if (PRESERVE_FILES.has(fileName)) return true;
  if (fileName.startsWith('PROJECT') && fileName.endsWith('.md')) return true;
  return false;
}

// ---------------------------------------------------------------------------
// Install record (.gabbe/manifest.json) -- same schema as gabbe/installer.py
// ---------------------------------------------------------------------------

const MANIFEST_SCHEMA_VERSION = 1;
let MANIFEST_FILE = path.join(PROJECT_ROOT, '.gabbe', 'manifest.json');

function setProjectRoot(dir) {
  PROJECT_ROOT = dir;
  MANIFEST_FILE = path.join(PROJECT_ROOT, '.gabbe', 'manifest.json');
}
const recorded = new Map(); // manifest path -> entry written by this run
let priorEntries = new Map(); // manifest path -> entry of an earlier install

// Manifest paths always use forward slashes, on every platform.
function relToProject(file) {
  return path.relative(PROJECT_ROOT, file).split(path.sep).join('/');
}

function sha256(data) {
  return crypto.createHash('sha256').update(data).digest('hex');
}

function loadPriorManifest() {
  priorEntries = new Map();
  try {
    const prior = JSON.parse(fs.readFileSync(MANIFEST_FILE, 'utf8'));
    for (const e of prior.entries || []) {
      if (e && typeof e.path === 'string') {
        const safe = safeRecordedEntry(e);
        if (safe) priorEntries.set(e.path, safe);
      }
    }
  } catch (e) {
    /* no earlier record */
  }
}

// ---------------------------------------------------------------------------
// What a record entry may make the installers do
// ---------------------------------------------------------------------------
// The record is data from the project folder, so it is never trusted. These rules are the same
// in gabbe/installer.py: an entry is acted on only as follows, and a refused entry is kept
// with one line `kept <path>: <why>` and never stops the others.
//   R1 a kind the installers do not write is kept;
//   R2 a copy is removed only when it is a regular file whose bytes hash to the recorded hash;
//   R3 a backup is used only when its name is <path>.gabbe-bak[.<n>] (or <path>.bak[.<n>], which
//      `--force` writes) and it is a regular file; it is moved back only after the entry's own
//      file was removed or is absent;
//   R4 a hook-merge entry is only for a settings file the installers write, and only the hook
//      entries that are the kit's own are removed (removeHookMerge);
//   R5 under .git/ only hooks/pre-commit and hooks/pre-push are touched;
//   R6 every path is looked at again just before it is acted on (inspectPath): no link above it
//      and none at the leaf, unless a link was recorded.

const RECORD_KINDS = new Set(['copy', 'skill-emit', 'block', 'symlink', 'tree', 'hook-merge']);
const HASHED_KINDS = new Set(['copy', 'skill-emit']);
const BACKUP_SUFFIX = /^\.(gabbe-bak|bak)(\.[0-9]+)?$/;
const QUIET = { line() {}, warn() {} };
const LOUD = { line: (t) => log(t), warn: (t) => process.stderr.write(`warning: ${t}\n`) };

function recordedParts(rel) {
  return rel.split(/[\\/]/).filter((p) => p !== '' && p !== '.');
}

// Why an entry is not acted on, judged from the record alone (nothing is read), or null.
function entryProblem(entry, needHash) {
  if (!RECORD_KINDS.has(entry.kind)) return `unknown record kind '${String(entry.kind).replace(/[\x00-\x1f\x7f-\x9f]/g, '')}'`;
  const gitHooks = GIT_HOOKS.map((n) => `.git/hooks/${n}`);
  if (recordedParts(entry.path).some((p) => p.toLowerCase() === '.git') && !(entry.kind === 'copy' && gitHooks.includes(entry.path))) {
    return 'it is under .git/ and is not one of the GABBE git hooks';
  }
  if (entry.kind === 'hook-merge' && !HOOK_MERGES.some((s) => s.target.join('/') === entry.path)) {
    return 'hook-merge is only valid for a settings file the installers write';
  }
  if (needHash && HASHED_KINDS.has(entry.kind) && !(typeof entry.hash === 'string' && entry.hash !== '')) {
    return 'the record holds no hash for it';
  }
  return null;
}

function backupNameOk(entry) {
  const name = entry.backup_of;
  return typeof name === 'string' && name.startsWith(entry.path) && BACKUP_SUFFIX.test(name.slice(entry.path.length));
}

// Look at a recorded path now, without following links: every folder above it must be a real
// folder and the leaf must not be a link (unless leafMayBeLink). Returns { file, st, problem };
// st is null when nothing is there. Throws for a path that is not a plain relative path.
function inspectPath(rel, leafMayBeLink) {
  checkRecordedPath(rel);
  const base = fs.realpathSync(PROJECT_ROOT);
  const parts = recordedParts(rel);
  let current = base;
  for (let i = 0; i < parts.length; i += 1) {
    current = path.join(current, parts[i]);
    let st;
    try {
      st = fs.lstatSync(current);
    } catch (e) {
      if (e.code === 'ENOENT' || e.code === 'ENOTDIR') return { file: path.join(base, ...parts), st: null, problem: null };
      return { file: current, st: null, problem: `it cannot be inspected (${e.code || e.message})` };
    }
    const last = i === parts.length - 1;
    if (st.isSymbolicLink() && !(last && leafMayBeLink)) {
      return { file: current, st, problem: last ? 'it is a link' : 'a folder above it is a link' };
    }
    if (last) return { file: current, st, problem: null };
    if (!st.isDirectory()) return { file: path.join(base, ...parts), st: null, problem: null };
  }
  throw new Error(`refusing an empty recorded path: ${rel}`);
}

// The path of the entry's backup_of when the record may name it (inside the project, and a
// backup name of this entry's own path: R3), else null after one warning.
function allowedBackup(entry, out) {
  if (!entry.backup_of) return null;
  const refuse = (why) => {
    out.warn(`skipped backup_of of '${entry.path}': ${why}`);
    return null;
  };
  let file;
  try {
    file = resolveWithin(entry.backup_of);
  } catch (e) {
    return refuse(e.message);
  }
  return backupNameOk(entry) ? file : refuse(`'${entry.backup_of}' is not a backup name of this path`);
}

// The backup an entry may bring back (R3): the allowed one, a regular file (a real folder is also
// accepted for a link or a folder entry: the wizard records `skills.bak` folders), no link above it.
function usableBackup(entry, out) {
  const file = allowedBackup(entry, out);
  if (!file) return null;
  const spot = inspectPath(entry.backup_of, false);
  if (spot.problem) {
    out.warn(`skipped backup_of of '${entry.path}': ${spot.problem}`);
    return null;
  }
  if (!spot.st) return null;
  const folderOk = (entry.kind === 'symlink' || entry.kind === 'tree') && spot.st.isDirectory();
  if (!spot.st.isFile() && !folderOk) {
    out.warn(`skipped backup_of of '${entry.path}': it is not a regular file`);
    return null;
  }
  return file;
}

// The backup of a kept entry stays where it is: its manifest name, when it exists.
function heldBackup(entry) {
  try {
    if (backupNameOk(entry) && inspectPath(entry.backup_of, false).st) return entry.backup_of;
  } catch (e) {
    /* a backup_of that cannot be looked at is not held */
  }
  return null;
}

// The one place that decides what happens to an entry (R1-R7). Looks at the disk now.
// Returns { action: 'remove', entry, file, backup } or { action: 'keep', entry, reason, held }.
// reason is null when a warning already said why.
function decideEntry(entry, out) {
  const keep = (reason) => ({ action: 'keep', entry, reason, held: heldBackup(entry) });
  try {
    resolveWithin(entry.path);
  } catch (e) {
    out.warn(`skipped record entry ${JSON.stringify(entry.path)}: ${e.message}`);
    return keep(null);
  }
  const problem = entryProblem(entry, true);
  if (problem) return keep(problem);
  const spot = inspectPath(entry.path, entry.kind === 'symlink');
  if (spot.problem) return keep(spot.problem);
  const wrong = notWhatWasRecorded(entry, spot);
  if (wrong) return keep(wrong);
  return { action: 'remove', entry, file: spot.file, backup: usableBackup(entry, out) };
}

// R7: a recorded link is removed only while it is a link that points into the project's agents/ folder.
function linkProblem(spot) {
  if (!spot.st.isSymbolicLink()) return 'it is no longer the link the install made';
  const target = path.resolve(path.dirname(spot.file), fs.readlinkSync(spot.file));
  const kit = path.join(fs.realpathSync(PROJECT_ROOT), 'agents');
  return target === kit || target.startsWith(kit + path.sep) ? null : "it is a link, but it does not point into the project's agents/ folder";
}

function notWhatWasRecorded(entry, spot) {
  const st = spot.st;
  if (!st) return null;
  if (entry.kind === 'symlink') return linkProblem(spot);
  if (entry.kind === 'tree') return st.isDirectory() ? null : 'it is not a folder';
  if (!st.isFile()) return 'it is not a regular file';
  if (HASHED_KINDS.has(entry.kind)) {
    try {
      const data = fs.readFileSync(spot.file);
      if (sha256(data) !== entry.hash) return 'it changed since the install';
      if (entry.path.startsWith('.git/') && !data.includes(HOOK_MARK)) return `it has no ${HOOK_MARK} mark`; // R5
    } catch (e) {
      return `it cannot be read (${e.code || e.message})`;
    }
  }
  return null;
}

function printKept(d) {
  if (d.action !== 'keep') return;
  if (d.reason) log(`kept ${d.entry.path}: ${d.reason}`);
  if (d.held) log(`kept ${d.held}: ${d.entry.path} was kept, so its backup stays where it is`);
}

// An earlier record is not trusted either: an entry that is not acted on is dropped from the
// map (and so from the new record), a backup_of that is not allowed is cleared; each with one line.
function safeRecordedEntry(entry) {
  if (!resolveOrWarn(entry.path, `record entry ${JSON.stringify(entry.path)}`)) return null;
  const problem = entryProblem(entry, false);
  if (problem) {
    log(`kept ${entry.path}: ${problem}`);
    return null;
  }
  if (HASHED_KINDS.has(entry.kind) && !entry.hash) log(`kept ${entry.path}: the record holds no hash for it`);
  if (!entry.backup_of) return entry;
  return allowedBackup(entry, LOUD) ? entry : { ...entry, backup_of: null };
}

// True if `data` (the bytes of `file`) is exactly what an earlier install recorded.
function isUnchangedKitFile(file, data) {
  const entry = priorEntries.get(relToProject(file));
  return Boolean(entry && entry.hash && entry.hash === sha256(data));
}

// Record one created artifact. A link to the user's original (backup_of) that an
// earlier run recorded is kept: a re-run finds its own file and makes no backup.
function record(file, kind, agent, backupOf, extra) {
  const rel = relToProject(file);
  const entry = { path: rel, kind, agent: agent || 'shared', backup_of: backupOf || null, ...(extra || {}) };
  if (kind === 'copy') entry.hash = sha256(fs.readFileSync(file));
  const earlier = recorded.get(rel) || priorEntries.get(rel);
  if (!entry.backup_of && earlier && earlier.backup_of) entry.backup_of = earlier.backup_of;
  recorded.set(rel, entry);
}

// Why the install record may not be written, or null. A link at the record's own path is the
// project's: writing would follow it to wherever it points (docs/INSTALL.md: nothing is
// written through a link of yours).
function recordLinkProblem() {
  try {
    if (fs.lstatSync(MANIFEST_FILE).isSymbolicLink()) {
      return `${MANIFEST_FILE} is a symbolic link; the install record must be a regular file`;
    }
  } catch (e) {
    /* no record file yet */
  }
  return null;
}

// Write the record through a temporary file in the same folder and rename it into place, so
// nothing is written through a link and a stop part-way leaves the old record whole.
function writeRecordFile(manifest) {
  const problem = recordLinkProblem();
  if (problem) {
    const err = new Error(`${problem}. No install record was written.`);
    err.gabbeFatal = true;
    throw err;
  }
  fs.mkdirSync(path.dirname(MANIFEST_FILE), { recursive: true });
  const tmp = `${MANIFEST_FILE}.${process.pid}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(manifest, null, 2) + '\n', { flag: 'wx' });
  fs.renameSync(tmp, MANIFEST_FILE);
}

function writeManifest() {
  try {
    if (fs.lstatSync(path.dirname(MANIFEST_FILE)).isSymbolicLink()) {
      log(`  ${yellow('!')} .gabbe is a link of yours: no install record was written`);
      return;
    }
  } catch (e) {
    /* .gabbe does not exist yet */
  }
  const merged = new Map(priorEntries);
  for (const [rel, entry] of recorded) merged.set(rel, entry);
  const entries = [...merged.values()].sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));
  const agents = [...new Set(entries.map((e) => e.agent).filter((a) => a && a !== 'shared'))].sort();
  let version = 'node-installer';
  try {
    version = require(path.join(KIT_ROOT, 'package.json')).version;
  } catch (e) {
    /* keep the fallback */
  }
  const manifest = {
    schema_version: MANIFEST_SCHEMA_VERSION,
    installer_version: version,
    timestamp: '',
    agents,
    entries,
  };
  writeRecordFile(manifest);
  log(`  ${green('✓')} Recorded ${entries.length} paths in .gabbe/manifest.json (used by \`gabbe uninstall\`)`);
}

// Same slug rule as scripts/init.py, so `gabbe uninstall --agents cursor` matches.
function agentSlug(agent) {
  return agent.toLowerCase().replace(/[^a-z0-9_-]/g, '-').replace(/^-+|-+$/g, '') || 'shared';
}

// ---------------------------------------------------------------------------
// Backups: back up first, never overwrite an existing backup
// ---------------------------------------------------------------------------

function pathTaken(p) {
  try {
    fs.lstatSync(p);
    return true;
  } catch (e) {
    return false;
  }
}

// First unused backup name: <name>.gabbe-bak, then <name>.gabbe-bak.1, ...
function freeBackupPath(file, suffix) {
  const sfx = suffix || '.gabbe-bak';
  let candidate = file + sfx;
  for (let n = 1; pathTaken(candidate); n += 1) candidate = `${file}${sfx}.${n}`;
  return candidate;
}

// Back up an existing file before it is overwritten; returns the backup path.
// The first backup keeps the user's ORIGINAL; a later, different version gets the
// next free name. No new backup when the same bytes are already backed up, or when
// the file is one an earlier install wrote and nobody changed.
function backupBeforeOverwrite(dst) {
  let data;
  try {
    data = fs.readFileSync(dst);
  } catch (e) {
    throw backupFailed(dst, e);
  }
  const first = dst + '.gabbe-bak';
  if (isUnchangedKitFile(dst, data)) return fs.existsSync(first) ? first : null;
  const dir = path.dirname(dst);
  const prefix = path.basename(dst) + '.gabbe-bak';
  for (const name of fs.readdirSync(dir).filter((n) => n.startsWith(prefix)).sort()) {
    const existing = path.join(dir, name);
    try {
      if (fs.readFileSync(existing).equals(data)) return existing;
    } catch (e) {
      /* not a readable file: ignore */
    }
  }
  const backup = freeBackupPath(dst);
  try {
    fs.copyFileSync(dst, backup);
  } catch (e) {
    throw backupFailed(dst, e);
  }
  log(`  ${yellow('!')} Backed up existing ${path.basename(dst)} -> ${path.basename(backup)}`);
  return backup;
}

// Without a backup the file would be the user's only copy: stop the install.
function backupFailed(file, error) {
  const err = new Error(
    `Could not back up ${file} (${error.message}). Nothing was overwritten; ` +
      'fix the cause and run the installer again.'
  );
  err.gabbeFatal = true;
  return err;
}

// True if `file` is a symbolic link, or a directory between the project root and
// it is one. Such a path is the user's: writing there could land outside the
// project (or inside the kit, when a tool linked .claude/skills to agents/skills).
const skippedLinks = [];
const emittedDirs = new Set(); // skills and rules folders this run emitted into (manifest paths)
function behindLink(file) {
  let current = PROJECT_ROOT;
  for (const part of path.relative(PROJECT_ROOT, file).split(path.sep)) {
    current = path.join(current, part);
    let st;
    try {
      st = fs.lstatSync(current);
    } catch (e) {
      return false; // nothing here yet, so nothing below it either
    }
    if (st.isSymbolicLink()) return true;
  }
  return false;
}

// Remember a path that was not written because of a link; reported once at the end.
function skipLink(file) {
  skippedLinks.push(relToProject(file));
  return true;
}

// `update` kept your changed copy of a kit file: put the kit's new version beside it as
// <name>.gabbe-new and record it as a kit-owned copy (uninstall removes it, a later update
// replaces it while it is unchanged). Only for a file an earlier record names, never for the
// folders memory/ and project/, never over a .gabbe-new that is not ours or was changed, never
// through a link, and nothing is written when your file equals the kit's.
function offerNewVersion(src, dst, rel) {
  if (!priorEntries.has(relToProject(dst)) || /(^|[\\/])(memory|project)[\\/]/.test(rel)) return;
  const kit = fs.readFileSync(src);
  const mine = readOrEmpty(dst);
  const side = dst + '.gabbe-new';
  if (kit.equals(mine) || behindLink(side)) return;
  const ours = isUnchangedKitFile(side, readOrEmpty(side));
  if (pathTaken(side) && !ours) {
    log(`  ${yellow('!')} kept your ${relToProject(dst)}; ${relToProject(side)} is not ours or was changed: left alone`);
    return;
  }
  fs.writeFileSync(side, kit);
  record(side, 'copy', 'shared', null);
  log(`  ${yellow('!')} kept your ${relToProject(dst)}; the kit's new version is ${relToProject(side)} (compare, merge, then delete it)`);
}

// Copy a directory tree without ever losing user data. Preserved files are left
// untouched; any other differing pre-existing file is backed up before being
// refreshed. With force=true, even preserved files are re-templated (still backed
// up first). Every file written is recorded. Mirrors init.py safe_merge_directory.
function safeCopyTree(srcRoot, dstRoot, force, sideBySide) {
  if (!fs.existsSync(srcRoot)) return 0;
  let copied = 0;
  for (const src of walk(srcRoot)) {
    const rel = path.relative(srcRoot, src);
    const dst = path.join(dstRoot, rel);
    const fileName = path.basename(src);
    if (behindLink(dst) && skipLink(dst)) continue;
    const exists = fs.existsSync(dst);
    if (exists && !force && shouldPreserve(rel, fileName) && !isUnchangedKitFile(dst, readOrEmpty(dst))) {
      if (sideBySide) offerNewVersion(src, dst, rel); // yours (changed since install): kept
      continue; // an unchanged recorded copy is refreshed instead
    }
    if (exists) {
      let differs = true;
      try {
        differs = !fs.readFileSync(src).equals(fs.readFileSync(dst));
      } catch (e) {
        differs = true;
      }
      if (differs) backupBeforeOverwrite(dst);
    }
    fs.mkdirSync(path.dirname(dst), { recursive: true });
    fs.copyFileSync(src, dst);
    // Link the FIRST backup (the user's original) for restore on uninstall.
    const first = dst + '.gabbe-bak';
    record(dst, 'copy', 'shared', fs.existsSync(first) ? relToProject(first) : null);
    copied += 1;
  }
  return copied;
}

// The block appended to an instruction file the user already had. scripts/init.py
// writes the same text; `gabbe uninstall` removes it by its two marker lines.
const POINTER_BEGIN =
  '<!-- GABBE-KIT:BEGIN (added by the GABBE installer; delete this block to detach the kit) -->';
const POINTER_END = '<!-- GABBE-KIT:END -->';

function pointerBlock(kitAgentsMd) {
  return (
    `${POINTER_BEGIN}\n` +
    '## GABBE kit\n\n' +
    `This project also uses the GABBE engineering kit. Read \`${kitAgentsMd}\` together with\n` +
    "this file: it holds the kit's rules, lifecycle and skills index. Where the two disagree,\n" +
    'this file wins.\n' +
    `${POINTER_END}\n`
  );
}

// Keep the user's own instruction file and append a pointer to the kit's file.
// The original is backed up first and the change is recorded, so `gabbe uninstall`
// takes the block out again. Idempotent.
// Works on bytes and uses the file's own line ending, so the user's encoding and
// line endings are never changed.
function withPointerBlock(data, kitAgentsMd) {
  const nl = data.includes('\r\n') ? '\r\n' : '\n';
  const block = Buffer.from(pointerBlock(kitAgentsMd).replace(/\n/g, nl));
  const endsWith = (s) => data.length >= s.length && data.subarray(data.length - s.length).equals(Buffer.from(s));
  let joiner = nl + nl;
  if (!data.length || endsWith(nl + nl)) joiner = '';
  else if (endsWith(nl)) joiner = nl;
  return Buffer.concat([data, Buffer.from(joiner), block]);
}

// The bytes of a user's file without the pointer block and the blank line put
// before it (same rule as gabbe/installer.py strip_pointer_block).
function withoutPointerBlock(data) {
  const begin = data.indexOf('<!-- GABBE-KIT:BEGIN');
  const endMarker = data.indexOf(POINTER_END, begin);
  if (begin === -1 || endMarker === -1) return data;
  let end = endMarker + POINTER_END.length;
  if (data[end] === 0x0d && data[end + 1] === 0x0a) end += 2;
  else if (data[end] === 0x0a) end += 1;
  let before = data.subarray(0, begin);
  const tail = before.subarray(Math.max(0, before.length - 4)).toString('latin1');
  if (tail.endsWith('\r\n\r\n')) before = before.subarray(0, before.length - 2);
  else if (tail.endsWith('\n\n')) before = before.subarray(0, before.length - 1);
  return Buffer.concat([before, data.subarray(end)]);
}

function trimLineEnds(data) {
  let end = data.length;
  while (end > 0 && (data[end - 1] === 0x0a || data[end - 1] === 0x0d)) end -= 1;
  return data.subarray(0, end);
}

function addPointerBlock(target, kitAgentsMd, agent) {
  const data = fs.readFileSync(target);
  const name = path.basename(target);
  if (data.includes(POINTER_BEGIN)) {
    log(`  ${blue('→')} ${name} already points to the kit; left as is`);
    return;
  }
  try {
    fs.accessSync(target, fs.constants.W_OK);
  } catch (e) {
    log(
      `  ${yellow('!')} ${relToProject(target)} is read-only: left as is. Add a line that points to` +
        ` ${kitAgentsMd} yourself`
    );
    return;
  }
  const backup = backupBeforeOverwrite(target);
  fs.writeFileSync(target, withPointerBlock(data, kitAgentsMd));
  record(target, 'block', agent, backup ? relToProject(backup) : null);
  log(
    `  ${yellow('!')} Kept your ${name} and added a pointer to ${kitAgentsMd}` +
      ` (original saved as ${backup ? path.basename(backup) : 'a backup'})`
  );
}

// Wire a rule file pointing at the kit's AGENTS.md. Prefer a relative symlink
// (like init.py); fall back to a copy on platforms/filesystems that refuse
// symlinks (e.g. Windows without privileges).
// A file the user already had is kept and gets a pointer block. Only --force
// replaces it, after moving it to a backup name that is not in use.
// Returns true when the link (or its copy) was put in place.
function wireAgentsLink(target, sourceAgentsMd, agent, force) {
  if (behindLink(path.dirname(target)) && skipLink(target)) return false;
  fs.mkdirSync(path.dirname(target), { recursive: true });
  let backupOf = null;
  let st = null;
  try {
    st = fs.lstatSync(target);
  } catch (e) {
    /* target does not exist */
  }
  if (st && st.isSymbolicLink() && !isOurLink(target, sourceAgentsMd)) {
    // A link of the user's (for example AGENTS.md -> CLAUDE.md): keep it.
    if (!force) {
      log(
        `  ${yellow('!')} ${relToProject(target)} is a link of yours: left as is. Point it at the kit` +
          ' yourself, or re-run with --force (it is moved to a backup first)'
      );
      return false;
    }
    const backup = freeBackupPath(target, '.bak');
    fs.renameSync(target, backup);
    backupOf = relToProject(backup);
    log(`  ${yellow('!')} Moved your link ${path.basename(target)} to ${path.basename(backup)}`);
  } else if (st && st.isSymbolicLink()) {
    fs.unlinkSync(target);
  } else if (st) {
    const ours = st.isFile() && isUnchangedKitFile(target, fs.readFileSync(target));
    if (st.isFile() && !ours && !force) {
      addPointerBlock(target, relToProject(sourceAgentsMd), agent);
      return false;
    }
    if (ours) {
      fs.unlinkSync(target); // our own copy from an earlier run (symlink fallback)
    } else if (st.isFile() && fs.readFileSync(target).includes(POINTER_BEGIN)) {
      // --force after an earlier run that added the pointer block: put the user's
      // file back without the block before it is moved aside.
      backupOf = moveAsideWithoutBlock(target);
    } else {
      const backup = freeBackupPath(target, '.bak');
      fs.renameSync(target, backup);
      backupOf = relToProject(backup);
      log(`  ${yellow('!')} Backed up existing ${path.basename(target)} -> ${path.basename(backup)}`);
    }
  }
  const linkPath = path.relative(path.dirname(target), sourceAgentsMd);
  try {
    fs.symlinkSync(linkPath, target);
    record(target, 'symlink', agent, backupOf);
    log(`  ${green('✓')} Linked ${path.relative(PROJECT_ROOT, target)} -> ${linkPath}`);
  } catch (e) {
    fs.copyFileSync(sourceAgentsMd, target);
    record(target, 'copy', agent, backupOf);
    log(`  ${green('✓')} Copied ${path.relative(PROJECT_ROOT, target)} (symlink fallback)`);
  }
  return true;
}

// Remove `target` (a user's file that carries the pointer block) so a link can take
// its place; return the manifest path of the backup that holds the user's text. If
// the file is unchanged since the block was added, the backup made then already is
// the original. Otherwise the text without the block goes to a new .bak.
function moveAsideWithoutBlock(target) {
  const stripped = withoutPointerBlock(fs.readFileSync(target));
  const entry = priorEntries.get(relToProject(target));
  if (entry && entry.backup_of) {
    const earlier = resolveOrWarn(entry.backup_of, `backup_of of ${JSON.stringify(entry.path)}`);
    try {
      if (!earlier) throw new Error('backup_of refused');
      if (trimLineEnds(fs.readFileSync(earlier)).equals(trimLineEnds(stripped))) {
        fs.unlinkSync(target);
        return entry.backup_of;
      }
    } catch (e) {
      /* the earlier backup is gone: fall through and write a new one */
    }
  }
  const backup = freeBackupPath(target, '.bak');
  fs.writeFileSync(backup, stripped);
  fs.unlinkSync(target);
  log(`  ${yellow('!')} Moved your ${path.basename(target)} to ${path.basename(backup)}`);
  return relToProject(backup);
}

// True if the link at `target` was made by an installer: an earlier install
// recorded it, or it already points at the kit file we are about to link.
function isOurLink(target, sourceAgentsMd) {
  const entry = priorEntries.get(relToProject(target));
  if (entry && entry.kind === 'symlink') return true;
  try {
    return fs.realpathSync(target) === fs.realpathSync(sourceAgentsMd);
  } catch (e) {
    return false;
  }
}

// Write one generated file (an emitted skill or rule) and record it. A different
// file already at that path is the user's own, or a kit file the user edited: it
// is backed up first, and the backup is linked for restore on uninstall.
function writeGenerated(file, content, agent) {
  if (behindLink(file) && skipLink(file)) return;
  let backupOf = null;
  let old = null;
  try {
    old = fs.readFileSync(file);
  } catch (e) {
    /* new file */
  }
  if (old !== null && !old.equals(Buffer.from(content)) && !isUnchangedKitFile(file, old)) {
    const backup = backupBeforeOverwrite(file);
    if (backup) {
      backupOf = relToProject(backup);
      log(`  ${yellow('!')} Kept your ${relToProject(file)} as ${path.basename(backup)}`);
    }
  }
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, content);
  record(file, 'copy', agent, backupOf);
}

// Frontmatter keys a generated skill file may carry. The same list as ALLOWED_FRONTMATTER_KEYS
// in agents/scripts/compile_skills.py: the keys the kit's own skills use, plus `version`, `author`
// and the schema version. Anything else (`allowed-tools`, `hooks`, `model`, ...) is left out, so
// an imported skill cannot grant itself tools or hooks.
const ALLOWED_FRONTMATTER_KEYS = new Set([
  'name', 'description', 'tags', 'triggers', 'context_cost', 'core', 'role', 'tools',
  'version', 'author', 'gabbe-schema-version',
]);

// The folders of the kit's own skills under agents/skills (KIT_SKILL_DIRS in compile_skills.py).
// A skill in any other folder was imported (scripts/registry_import.py writes to a namespace folder).
const KIT_SKILL_DIRS = new Set([
  'ai', 'architecture', 'brain', 'coding', 'coordination', 'core', 'data', 'industry', 'ops',
  'product', 'security',
]);

// Mirror of compile_skills.py one_line(): every line break and control character becomes one
// space, so a frontmatter value copied into a generated file cannot add keys (`alwaysApply: true`).
function oneLine(value) {
  return String(value).replace(/[\x00-\x1f\x7f-\x9f\u2028\u2029]+/g, ' ').trim();
}

const FRONTMATTER_KEY = /^["']?([A-Za-z0-9_-]+)["']?\s*:/;
const YAML_BREAKS = /\r\n|[\n\r\x85\u2028\u2029]/;
const NOT_A_KEY_LINE_OK = /^(\s|-(\s|$)|#|$)/; // blank, comment, indented, or a list item

// Drop the frontmatter keys outside ALLOWED_FRONTMATTER_KEYS (and a key given twice, and a line that
// is not part of any key). Splits on every line break YAML knows, so a key hidden behind a lone
// carriage return is seen. A file with only allowed keys comes back byte for byte.
// Returns { content, dropped }.
function filterFrontmatter(content) {
  const end = content.startsWith('---') ? content.indexOf('---', 3) : -1;
  if (end === -1) return { content, dropped: [] };
  const block = content.slice(3, end);
  const kept = [];
  const dropped = [];
  const seen = new Set();
  let skipping = false;
  for (const line of block.split(YAML_BREAKS)) {
    const m = FRONTMATTER_KEY.exec(line);
    if (m) {
      skipping = !ALLOWED_FRONTMATTER_KEYS.has(m[1]) || seen.has(m[1]);
      seen.add(m[1]);
      if (skipping) dropped.push(m[1]);
    } else if (!NOT_A_KEY_LINE_OK.test(line)) {
      dropped.push('(a line that is not a key)');
      continue;
    }
    if (!skipping) kept.push(line);
  }
  if (!dropped.length && !/\r(?!\n)|[\x85\u2028\u2029]/.test(block)) return { content, dropped };
  return { content: '---' + kept.join('\n') + content.slice(end), dropped };
}

// The kit's skill files, the kit's own folders first and imported ones after, each group in path
// order (the order of compile_skills.py), so on a name collision the kit's skill is the one that stays.
function skillSources(skillsSrcDir) {
  const compare = (a, b) => {
    for (let i = 0; i < Math.min(a.length, b.length); i += 1) {
      if (a[i] !== b[i]) return a[i] < b[i] ? -1 : 1;
    }
    return a.length - b.length;
  };
  return walk(skillsSrcDir)
    .filter((f) => f.endsWith('.skill.md'))
    .map((file) => {
      const parts = path.relative(skillsSrcDir, file).split(path.sep);
      return { file, parts, imported: parts.length > 1 && !KIT_SKILL_DIRS.has(parts[0]) };
    })
    .sort((a, b) => Number(a.imported) - Number(b.imported) || compare(a.parts, b.parts));
}

const announced = new Set(); // each collision / left-out-keys line is printed once per run, not once per agent
function announce(text) {
  if (announced.has(text)) return;
  announced.add(text);
  log(text);
}

// Call visit({ content, meta, slug }) once for each output slug; the content has its frontmatter
// filtered. A second skill with the same slug is not emitted and the collision is printed.
function eachSkill(skillsSrcDir, visit) {
  const owners = new Map();
  let count = 0;
  for (const src of skillSources(skillsSrcDir)) {
    const shown = 'agents/skills/' + src.parts.join('/');
    const { content, dropped } = filterFrontmatter(fs.readFileSync(src.file, 'utf8'));
    const meta = parseFrontmatter(content);
    const slug = safeSlug(meta.name, path.basename(src.file).replace(/\.skill\.md$/, ''));
    if (owners.has(slug)) {
      announce(`  ${red('!')} Name collision '${slug}': keeping ${owners.get(slug)}, ignoring ${shown}`);
      continue;
    }
    owners.set(slug, shown);
    if (dropped.length) announce(`  ${yellow('!')} ${shown}: left out frontmatter keys ${dropped.join(', ')}`);
    visit({ content, meta, slug });
    count += 1;
  }
  return count;
}

// Emit the universal .agents/skills/<slug>/SKILL.md tree (agentskills.io).
// Reads every agents/skills/**/*.skill.md and writes a real SKILL.md file.
function emitUniversalSkills(skillsSrcDir, targetSkillsDir, agent) {
  emittedDirs.add(relToProject(targetSkillsDir));
  return eachSkill(skillsSrcDir, ({ content, slug }) => {
    const text = injectSchemaVersion(withSlugName(content, slug));
    writeGenerated(path.join(targetSkillsDir, slug, 'SKILL.md'), text, agent);
  });
}

// Emit Cursor flat .mdc rules (.cursor/rules/<slug>.mdc) -- mirrors the Cursor
// branch of compile_skills.py.
function emitCursorRules(skillsSrcDir, cursorRulesDir, agent) {
  emittedDirs.add(relToProject(cursorRulesDir));
  return eachSkill(skillsSrcDir, ({ content, meta, slug }) => {
    const desc = oneLine(meta.description || `Skill for ${meta.name || slug}`);
    let body = content;
    if (content.startsWith('---')) {
      const end = content.indexOf('---', 3);
      if (end !== -1) body = content.slice(end + 3).replace(/^\s+/, '');
    }
    const cursorFm =
      '---\n' +
      `description: ${desc}\n` +
      'alwaysApply: false\n' +
      `gabbe-schema-version: ${GABBE_SCHEMA_VERSION}\n` +
      '---\n';
    writeGenerated(path.join(cursorRulesDir, `${slug}.mdc`), cursorFm + '\n' + body, agent);
  });
}

// Create a config file only when none exists (a user's own config is never
// replaced), and record it.
function writeTextIfAbsent(filePath, text, agent) {
  if (behindLink(filePath) && skipLink(filePath)) return false;
  if (fs.existsSync(filePath)) return false;
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, text);
  record(filePath, 'copy', agent);
  return true;
}

function writeJsonIfAbsent(filePath, obj, agent) {
  return writeTextIfAbsent(filePath, JSON.stringify(obj, null, 2) + '\n', agent);
}

// ---------------------------------------------------------------------------
// Per-agent wiring (mirrors scripts/init.py Step 5 conventions)
// ---------------------------------------------------------------------------

function wireAgent(agent, ctx) {
  const { skillsSrc, agentsMdSrc, force } = ctx;
  const slug = agentSlug(agent);
  switch (agent) {
    case 'Claude Code':
      wireAgentsLink(path.join(PROJECT_ROOT, '.claude', 'CLAUDE.md'), agentsMdSrc, slug, force);
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.claude', 'skills'), slug);
      log(`  ${green('✓')} Wired Claude Code (.claude/CLAUDE.md + .claude/skills)`);
      break;
    case 'Cursor':
      wireAgentsLink(path.join(PROJECT_ROOT, '.cursorrules'), agentsMdSrc, slug, force);
      emitCursorRules(skillsSrc, path.join(PROJECT_ROOT, '.cursor', 'rules'), slug);
      log(`  ${green('✓')} Wired Cursor (.cursorrules + .cursor/rules)`);
      break;
    case 'Windsurf':
      wireAgentsLink(path.join(PROJECT_ROOT, '.windsurfrules'), agentsMdSrc, slug, force);
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.windsurf', 'skills'), slug);
      log(`  ${green('✓')} Wired Windsurf (.windsurfrules + .windsurf/skills)`);
      break;
    case 'Cline':
      wireAgentsLink(path.join(PROJECT_ROOT, '.clinerules'), agentsMdSrc, slug, force);
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.cline', 'skills'), slug);
      log(`  ${green('✓')} Wired Cline (.clinerules + .cline/skills)`);
      break;
    case 'Devin / Cognition':
      wireAgentsLink(path.join(PROJECT_ROOT, '.devinrules'), agentsMdSrc, slug, force);
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.devin', 'skills'), slug);
      log(`  ${green('✓')} Wired Devin (.devinrules + .devin/skills)`);
      break;
    case 'Aider': {
      const aiderConf = path.join(PROJECT_ROOT, '.aider.conf.yml');
      if (writeTextIfAbsent(aiderConf, 'read:\n  - agents/AGENTS.md\n  - agents/skills/\n', slug)) {
        log(`  ${green('✓')} Wired .aider.conf.yml`);
      } else {
        log(`  ${blue('→')} .aider.conf.yml exists, leaving as-is`);
      }
      break;
    }
    case 'Gemini': {
      const geminiDir = path.join(PROJECT_ROOT, '.gemini');
      fs.mkdirSync(geminiDir, { recursive: true });
      const relAgents = path.relative(PROJECT_ROOT, agentsMdSrc);
      const relSkills = path.relative(PROJECT_ROOT, skillsSrc);
      writeJsonIfAbsent(path.join(geminiDir, 'settings.json'), {
        agent_instructions_file: relAgents,
        skills_directory: relSkills,
        contextFileName: 'GEMINI.md',
        'gabbe-schema-version': GABBE_SCHEMA_VERSION,
        notes: 'Managed by gabbe (Node installer)',
      }, slug);
      wireAgentsLink(path.join(PROJECT_ROOT, 'GEMINI.md'), agentsMdSrc, slug, force);
      log(`  ${green('✓')} Wired .gemini/settings.json + GEMINI.md`);
      break;
    }
    case 'Antigravity':
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.agents', 'skills'), 'shared');
      log(`  ${green('✓')} Wired Antigravity (.agents/skills + root AGENTS.md)`);
      break;
    case 'OpenCode': {
      const opencodeConf = path.join(PROJECT_ROOT, 'opencode.json');
      writeJsonIfAbsent(opencodeConf, {
        $schema: 'https://opencode.ai/config.json',
        instructions: ['AGENTS.md', 'agents/skills/'],
      }, slug);
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.agents', 'skills'), 'shared');
      log(`  ${green('✓')} Wired opencode.json + .agents/skills`);
      break;
    }
    case 'Zed':
      wireAgentsLink(path.join(PROJECT_ROOT, '.rules'), agentsMdSrc, slug, force);
      log(`  ${green('✓')} Wired Zed (.rules)`);
      break;
    case 'Continue':
      wireAgentsLink(path.join(PROJECT_ROOT, '.continue', 'rules', 'agents.md'), agentsMdSrc, slug, force);
      log(`  ${green('✓')} Wired Continue (.continue/rules/agents.md)`);
      break;
    case 'Roo Code':
      wireAgentsLink(path.join(PROJECT_ROOT, '.roo', 'rules', 'agents.md'), agentsMdSrc, slug, force);
      log(`  ${green('✓')} Wired Roo Code (.roo/rules/agents.md)`);
      break;
    case 'Kilo Code':
      wireAgentsLink(path.join(PROJECT_ROOT, '.kilocode', 'rules', 'agents.md'), agentsMdSrc, slug, force);
      log(`  ${green('✓')} Wired Kilo Code (.kilocode/rules/agents.md)`);
      break;
    case 'OpenAI / Codex':
      wireAgentsLink(path.join(PROJECT_ROOT, '.codex', 'AGENTS.md'), agentsMdSrc, slug, force);
      log(`  ${green('✓')} Wired Codex (.codex/AGENTS.md)`);
      break;
    case 'GitHub Copilot':
      wireAgentsLink(path.join(PROJECT_ROOT, '.github', 'copilot-instructions.md'), agentsMdSrc, slug, force);
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.github', 'skills'), slug);
      log(`  ${green('✓')} Wired GitHub Copilot (.github/copilot-instructions.md + .github/skills)`);
      break;
    case 'VS Code':
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.github', 'skills'), slug);
      log(`  ${green('✓')} Wired VS Code (.github/skills)`);
      break;
    default:
      log(`  ${yellow('!')} Unknown agent "${agent}", skipped`);
  }
}

// ---------------------------------------------------------------------------
// uninstall, update, doctor
// ---------------------------------------------------------------------------
// `uninstall` follows gabbe/installer.py (the reference): it acts only on what
// .gabbe/manifest.json records, and prints the same wording as `gabbe uninstall`.

// ---------------------------------------------------------------------------
// Optional hooks (--hooks): off unless asked. Reversed by `uninstall` from the record.
// ---------------------------------------------------------------------------

const HOOK_MARK = 'GABBE-HOOK';
const GIT_HOOKS = ['pre-commit', 'pre-push'];
// agent -> the fragment to merge, the file it goes into, and the script the fragment runs
const HOOK_MERGES = [
  { agent: 'Claude Code', fragment: 'claude-code/settings.fragment.json', target: ['.claude', 'settings.json'], script: 'claude-code/gabbe-hook.js', guards: 'shell guard, edit guard, session start' },
  { agent: 'Cursor', fragment: 'cursor/hooks.fragment.json', target: ['.cursor', 'hooks.json'], script: 'cursor/gabbe-hook.js', guards: 'shell guard' },
];
const hookLines = []; // one line per hook installed, printed at the end

function mergeLib() {
  return require(path.join(SOURCE_AGENTS_DIR, 'hooks', 'merge-hooks.js'));
}

function sameJson(a, b) {
  return require('util').isDeepStrictEqual(a, b);
}

function byHand(rel, why, fragment) {
  log(`  ${yellow('!')} ${rel}: ${why}. Nothing was changed. Add this by hand:`);
  log(JSON.stringify(fragment, null, 2).split('\n').map((l) => '      ' + l).join('\n'));
}

// Merge one fragment into the project's hooks file of one agent. Returns true when handled.
function installHookMerge(spec, targetAgents) {
  const target = path.join(PROJECT_ROOT, ...spec.target);
  const rel = relToProject(target);
  const fragRel = 'agents/hooks/' + spec.fragment;
  const fragment = JSON.parse(fs.readFileSync(path.join(SOURCE_AGENTS_DIR, 'hooks', spec.fragment), 'utf8'));
  if (!fs.existsSync(path.join(targetAgents, 'hooks', spec.script))) {
    log(`  ${yellow('!')} ${rel}: the hook script agents/hooks/${spec.script} is not in the project, so no hook was installed`);
    return false;
  }
  if (behindLink(target) && skipLink(target)) {
    log(`  ${yellow('!')} ${rel}: a link of yours, or behind one; hooks not installed there`);
    return false;
  }
  let st = null;
  try {
    st = fs.lstatSync(target);
  } catch (e) {
    /* no file yet */
  }
  if (st && !st.isFile()) {
    log(`  ${yellow('!')} ${rel} is not a regular file; hooks not installed there`);
    return false;
  }
  let doc = {};
  if (st) {
    try {
      doc = JSON.parse(fs.readFileSync(target, 'utf8'));
    } catch (e) {
      byHand(rel, 'it is not plain JSON (comments?)', fragment);
      return false;
    }
  }
  let merged;
  try {
    merged = mergeLib().mergeFragment(doc, fragment);
  } catch (e) {
    if (!(e instanceof mergeLib().Unsafe)) throw e;
    byHand(rel, e.message, fragment);
    return false;
  }
  if (!merged.changed) {
    log(`  ${blue('→')} ${rel}: the GABBE hook entries are already there`);
    return true;
  }
  const earlier = priorEntries.get(rel);
  const wasOurs = Boolean(earlier && earlier.kind === 'hook-merge');
  const created = !st && !wasOurs ? true : Boolean(wasOurs && earlier.created);
  let backupRel = wasOurs ? earlier.backup_of || null : null;
  if (st && !(wasOurs && earlier.created)) {
    const backup = backupBeforeOverwrite(target);
    if (backup && !wasOurs) backupRel = relToProject(backup);
  }
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, JSON.stringify(merged.doc, null, 2) + '\n');
  record(target, 'hook-merge', agentSlug(spec.agent), backupRel, {
    fragment: fragRel,
    fragment_doc: fragment,
    created,
    added_version: Boolean(merged.addedVersion || (wasOurs && earlier.added_version)),
  });
  hookLines.push(`${spec.agent} hooks (${spec.guards}) -> ${rel}`);
  return true;
}

function gitOut(args) {
  const r = spawnSync('git', args, { cwd: PROJECT_ROOT, encoding: 'utf8' });
  return r.status === 0 && !r.error ? r.stdout.trim() : null;
}

// The two git hooks, by the rules of agents/hooks/git/install.sh: never replace a hook that is not
// ours (it has no GABBE-HOOK mark); stop when core.hooksPath is set. Only fixed git arguments run.
function installGitHooks() {
  const common = gitOut(['rev-parse', '--git-common-dir']);
  if (common === null) {
    log(`  ${blue('→')} Git hooks skipped: this folder is not a git repository`);
    return;
  }
  if (gitOut(['config', '--get', 'core.hooksPath'])) {
    log(`  ${yellow('!')} Git hooks not installed: core.hooksPath is set. Call agents/hooks/git/pre-commit and pre-push from your own hooks (see agents/guides/ops/hooks.md)`);
    return;
  }
  const hooksDir = path.join(path.resolve(PROJECT_ROOT, common), 'hooks');
  const base = fs.realpathSync(PROJECT_ROOT);
  const real = realpathLoose(hooksDir);
  if (real !== base && !real.startsWith(base + path.sep)) {
    log(`  ${yellow('!')} Git hooks not installed: the git folder is outside the project (worktree or submodule). Run "sh agents/hooks/git/install.sh" there yourself`);
    return;
  }
  for (const name of GIT_HOOKS) {
    const dst = path.join(hooksDir, name);
    const rel = relToProject(dst);
    const data = fs.readFileSync(path.join(SOURCE_AGENTS_DIR, 'hooks', 'git', name));
    if (behindLink(dst) && skipLink(dst)) {
      log(`  ${yellow('!')} ${rel} is a link of yours, or behind one: left alone`);
      continue;
    }
    let st = null;
    try {
      st = fs.lstatSync(dst);
    } catch (e) {
      /* no hook yet */
    }
    if (st && (!st.isFile() || !fs.readFileSync(dst).includes(HOOK_MARK))) {
      log(`  ${yellow('!')} ${rel} already exists and is not GABBE's: not replaced. To chain, add a line to it that runs agents/hooks/git/${name} "$@"`);
      continue;
    }
    if (st && !fs.readFileSync(dst).equals(data)) backupBeforeOverwrite(dst);
    if (!st || !fs.readFileSync(dst).equals(data)) {
      fs.mkdirSync(path.dirname(dst), { recursive: true });
      fs.writeFileSync(dst, data);
    }
    fs.chmodSync(dst, 0o755);
    record(dst, 'copy', 'shared');
    hookLines.push(`git ${name} hook -> ${rel}`);
  }
}

// Which hooks an earlier install recorded, for `update`: the merged files (as manifest paths) and the
// git hooks. A hook-merge entry counts only when the record holds hook entries that are the kit's own (R4),
// and a git hook only while the file is there with its GABBE-HOOK mark (R5): `update` never adds a hook to a
// settings file or a repository because a record says so.
function recordedHooks(record) {
  const entries = (record.entries || []).filter((e) => e && typeof e.path === 'string');
  const isKitMerge = (e) => {
    const spec = HOOK_MERGES.find((m) => m.target.join('/') === e.path);
    return e.kind === 'hook-merge' && Boolean(spec) && ownedHookFragment(e, spec).fromRecord > 0;
  };
  const isLiveGitHook = (e) => {
    if (e.kind !== 'copy' || !GIT_HOOKS.some((n) => e.path === `.git/hooks/${n}`)) return false;
    try {
      const spot = inspectPath(e.path, false);
      return !spot.problem && Boolean(spot.st) && spot.st.isFile() && fs.readFileSync(spot.file).includes(HOOK_MARK);
    } catch (err) {
      return false;
    }
  };
  return { merges: new Set(entries.filter(isKitMerge).map((e) => e.path)), git: entries.some(isLiveGitHook) };
}

// scope: { agents: [canonical names], merges: Set of paths or null for all, git: boolean }
function installHooks(scope, targetAgents) {
  log('');
  log(yellow('Part 3b: Optional hooks (--hooks)'));
  let any = false;
  for (const spec of HOOK_MERGES) {
    if (!scope.agents.includes(spec.agent)) continue;
    if (scope.merges && !scope.merges.has(relToProject(path.join(PROJECT_ROOT, ...spec.target)))) continue;
    any = true;
    installHookMerge(spec, targetAgents);
  }
  if (scope.git) installGitHooks();
  if (!any && !scope.agents.length && scope.git) {
    log(`  ${blue('→')} No hook-capable agent named in --agents (claude, cursor): only the git hooks apply.`);
  }
  hookLines.forEach((l) => log(`  ${green('✓')} Installed ${l}`));
  if (hookLines.length) {
    log('  Guide: agents/guides/ops/hooks.md. Remove them with `gabbe uninstall` (1.2.0 or later).');
  }
}

const GENERATED_MARKER = 'gabbe-schema-version:';

function isRealFile(p) {
  try {
    return fs.lstatSync(p).isFile();
  } catch (e) {
    return false;
  }
}

function isRealDir(p) {
  try {
    return fs.lstatSync(p).isDirectory();
  } catch (e) {
    return false;
  }
}

// Why the install record cannot be used, or null when it is absent or valid.
function recordProblem() {
  try {
    if (fs.lstatSync(path.dirname(MANIFEST_FILE)).isSymbolicLink()) {
      return `${path.dirname(MANIFEST_FILE)} is a symbolic link; the install record must be a real folder`;
    }
  } catch (e) {
    return null; // no .gabbe folder: no record
  }
  const linked = recordLinkProblem();
  if (linked) return linked;
  if (!fs.existsSync(MANIFEST_FILE)) return null;
  let record;
  try {
    record = JSON.parse(fs.readFileSync(MANIFEST_FILE, 'utf8'));
  } catch (e) {
    return `${MANIFEST_FILE} cannot be read as JSON (${e.message})`;
  }
  if (!record || typeof record !== 'object' || !Array.isArray(record.entries)) {
    return `${MANIFEST_FILE} is not an install record (no list of entries)`;
  }
  return null;
}

function readRecord() {
  return JSON.parse(fs.readFileSync(MANIFEST_FILE, 'utf8'));
}

// Stops with the same explanation as `gabbe uninstall` when there is no usable record.
// Returns the record, or null after printing why (the caller exits 1).
function requireRecord(nothingDone) {
  const problem = recordProblem();
  if (problem) {
    process.stderr.write(
      red(`The install record is damaged: ${problem}. ${nothingDone}`) + '\n' +
        'Restore the file from version control or a backup, or re-run the installer you used ' +
        'to write a new record.\n'
    );
    return null;
  }
  if (!fs.existsSync(MANIFEST_FILE)) {
    process.stderr.write(
      red(`No install record (${MANIFEST_FILE}): ${nothingDone.toLowerCase()}`) + '\n' +
        'Installs made by `npx gabbe-kit init` before 1.1.4 wrote no record. ' +
        'Re-run `npx gabbe-kit init` (1.1.4 or later) with the same --agents to create one, ' +
        "then run `gabbe uninstall` again; or remove the kit by hand (docs/INSTALL.md, 'Uninstalling').\n"
    );
    return null;
  }
  return readRecord();
}

function realpathLoose(p) {
  try {
    return fs.realpathSync(p);
  } catch (e) {
    const parent = path.dirname(p);
    return parent === p ? p : path.join(realpathLoose(parent), path.basename(p));
  }
}

// A recorded path must be a plain relative path: text, not empty, not `.`, not absolute,
// no `..` part. Throws otherwise.
function checkRecordedPath(rel) {
  if (typeof rel !== 'string' || rel === '' || rel === '.') {
    throw new Error(`refusing an empty or non-text recorded path: ${JSON.stringify(rel)}`);
  }
  if (rel.includes('\0') || path.isAbsolute(rel) || path.win32.isAbsolute(rel) || /^[\\/]/.test(rel)) {
    throw new Error(`refusing an absolute recorded path: ${rel}`);
  }
  const parts = rel.split(/[\\/]/);
  if (parts.includes('..') || parts.every((p) => p === '' || p === '.')) {
    throw new Error(`refusing a recorded path that climbs out of the project: ${rel}`);
  }
}

// The ONE function that turns a field of the install record into a path (entry.path,
// entry.backup_of, entry.fragment). Returns the path, or null after one message naming `what`.
function resolveOrWarn(rel, what) {
  try {
    return resolveWithin(rel);
  } catch (e) {
    process.stderr.write(`warning: skipped ${what}: ${e.message}\n`);
    return null;
  }
}

// Resolve a recorded path under the project. The leaf is not followed, so a recorded
// link is acted on itself. A path that leaves the project throws (it is skipped).
function resolveWithin(rel) {
  checkRecordedPath(rel);
  const base = fs.realpathSync(PROJECT_ROOT);
  const raw = path.resolve(base, rel);
  const parent = realpathLoose(path.dirname(raw));
  if (parent !== base && !parent.startsWith(base + path.sep)) {
    throw new Error(`refusing path outside the project: ${rel}`);
  }
  const result = path.join(parent, path.basename(raw));
  if (result === base) throw new Error(`refusing the project folder itself: ${rel}`);
  return result;
}

function isModifiedCopy(entry, file) {
  if (entry.kind !== 'copy' || !entry.hash) return false;
  try {
    return fs.lstatSync(file).isFile() && sha256(fs.readFileSync(file)) !== entry.hash;
  } catch (e) {
    return false;
  }
}

// Files inside a directory that an installer generated (they carry the kit's marker).
function generatedFiles(tree) {
  return walk(tree)
    .filter((f) => {
      const head = Buffer.alloc(4096);
      const fd = fs.openSync(f, 'r');
      try {
        return head.subarray(0, fs.readSync(fd, head, 0, 4096, 0)).includes(GENERATED_MARKER);
      } finally {
        fs.closeSync(fd);
      }
    })
    .sort();
}

// Split the record into entries to remove and entries to keep (rules R1-R7 above; the same as
// gabbe/installer.py). `agents` is null for all agents. Prints one line for each kept entry.
function planRemoval(entries, agents) {
  const toRemove = [];
  const kept = [];
  for (const entry of entries) {
    const inScope = entry && typeof entry === 'object' && (agents === null || (agents.includes(entry.agent) && entry.agent !== 'shared'));
    if (!inScope) {
      kept.push(entry);
      continue;
    }
    const decision = decideEntry(entry, LOUD);
    printKept(decision);
    if (decision.action === 'remove') toRemove.push(decision);
    else kept.push(entry);
  }
  return { toRemove, kept };
}

function removedPaths(toRemove) {
  const base = fs.realpathSync(PROJECT_ROOT);
  const paths = [];
  for (const { entry, file } of toRemove) {
    if (entry.kind === 'tree' && isRealDir(file)) {
      for (const f of generatedFiles(file)) paths.push(path.relative(base, f).split(path.sep).join('/'));
    } else {
      paths.push(entry.path);
    }
  }
  return paths;
}

// Take the pointer block out of the user's file; put the exact original back from the
// backup when nothing else in the file changed.
function removeBlock(file, backup) {
  let st;
  try {
    st = fs.lstatSync(file);
  } catch (e) {
    return;
  }
  if (!st.isFile()) return;
  const stripped = withoutPointerBlock(fs.readFileSync(file));
  if (backup && isRealFile(backup)) {
    if (trimLineEnds(fs.readFileSync(backup)).equals(trimLineEnds(stripped))) {
      fs.renameSync(backup, file);
      return;
    }
  }
  fs.writeFileSync(file, stripped);
}

// The kit's own hook fragment for a settings file, or null when the package does not hold it.
function kitFragment(spec) {
  try {
    return JSON.parse(fs.readFileSync(path.join(SOURCE_AGENTS_DIR, 'hooks', spec.fragment), 'utf8'));
  } catch (e) {
    return null;
  }
}

function commandsOfHook(item) {
  if (!item || typeof item !== 'object') return [];
  return Array.isArray(item.hooks) ? item.hooks.map((h) => h && h.command) : [item.command];
}

function allCommands(fragment) {
  const found = new Set();
  for (const items of Object.values((fragment && fragment.hooks) || {})) {
    if (Array.isArray(items)) items.forEach((item) => commandsOfHook(item).forEach((c) => found.add(c)));
  }
  return found;
}

// R4: the hook entries to take out. An entry is the kit's when every command in it is one that the
// kit's own fragment holds, or, when the package has no fragment, contains both `agents/hooks/`
// and `gabbe-hook.js`. The record's fragment_doc only supplies entries that pass. With no usable
// fragment_doc, the kit's own fragment is used. Returns { fragment, ignored, fromRecord }: how many
// record entries were ignored, and how many passed.
function ownedHookFragment(entry, spec) {
  const kit = kitFragment(spec);
  const known = kit ? allCommands(kit) : null;
  const isKit = (c) => (known ? known.has(c) : typeof c === 'string' && c.includes('agents/hooks/') && c.includes('gabbe-hook.js'));
  const doc = entry.fragment_doc;
  if (!doc || typeof doc.hooks !== 'object' || doc.hooks === null) return { fragment: kit || { hooks: {} }, ignored: 0, fromRecord: 0 };
  const hooks = {};
  let ignored = 0;
  let fromRecord = 0;
  for (const [event, items] of Object.entries(doc.hooks)) {
    for (const item of Array.isArray(items) ? items : []) {
      const commands = commandsOfHook(item);
      if (commands.length && commands.every(isKit)) {
        (hooks[event] = hooks[event] || []).push(item);
        fromRecord += 1;
      } else {
        ignored += 1;
      }
    }
  }
  return { fragment: { hooks, version: kit ? kit.version : doc.version }, ignored, fromRecord };
}

// True for nothing but empty folders of JSON: {}, {"a": {}}, [] (a file with only that is not content).
function isEmptyStructure(value) {
  if (Array.isArray(value)) return value.length === 0;
  if (value && typeof value === 'object') return Object.values(value).every(isEmptyStructure);
  return false;
}

// Take the kit's own hook entries out of a settings file the installer merged into (R4). The file
// is deleted only when nothing but empty structure is left and the record says the install created
// it; otherwise the user's file stays, and is not written at all when nothing in it was the kit's.
// When the file minus our entries equals the backup (as JSON), the backup's exact bytes come back.
function removeHookMerge(entry, file, backup) {
  const spec = HOOK_MERGES.find((s) => s.target.join('/') === entry.path);
  const lib = mergeLib();
  let original;
  let cleaned;
  try {
    original = JSON.parse(fs.readFileSync(file, 'utf8'));
    const owned = ownedHookFragment(entry, spec);
    if (owned.ignored) log(`ignored ${owned.ignored} hook entr${owned.ignored === 1 ? 'y' : 'ies'} in the record for ${entry.path}: not the kit's own`);
    cleaned = lib.removeFragment(original, owned.fragment, { addedVersion: entry.added_version === true });
  } catch (e) {
    process.stderr.write(`warning: ${entry.path} was left as it is (${e.message}); remove the GABBE hook entries by hand\n`);
    return;
  }
  if (entry.created === true && !sameJson(original, cleaned) && isEmptyStructure(cleaned)) {
    fs.unlinkSync(file);
    return;
  }
  if (backup) {
    try {
      if (sameJson(JSON.parse(fs.readFileSync(backup, 'utf8')), cleaned)) {
        fs.renameSync(backup, file);
        return;
      }
    } catch (e) {
      /* the backup is not JSON: keep it and write the cleaned file */
    }
  }
  if (!sameJson(original, cleaned)) fs.writeFileSync(file, JSON.stringify(cleaned, null, 2) + '\n');
}

// The generated files of a recorded folder (tree), each looked at again before it is removed.
function removeGenerated(dir) {
  const base = fs.realpathSync(PROJECT_ROOT);
  for (const f of generatedFiles(dir)) {
    const spot = inspectPath(path.relative(base, f).split(path.sep).join('/'), false);
    if (!spot.problem && spot.st && spot.st.isFile()) fs.unlinkSync(spot.file);
  }
}

// Carry out one decision of decideEntry (the entry's file and backup were just inspected).
function applyRemoval({ entry, file, backup }) {
  if (entry.kind === 'block') {
    removeBlock(file, backup);
    return;
  }
  if (entry.kind === 'hook-merge') {
    removeHookMerge(entry, file, backup);
    return;
  }
  if (entry.kind === 'tree') removeGenerated(file);
  else if (pathTaken(file)) fs.unlinkSync(file);
  if (backup && !pathTaken(file)) fs.renameSync(backup, file); // R3: only once the entry's own file is gone
}

// Remove one planned entry after looking at it again (R6). Returns the paths removed, or null
// when it is kept now (the disk changed since the plan).
function removeEntry(planned) {
  const now = decideEntry(planned.entry, QUIET);
  if (now.action !== 'remove') {
    log(`skipped ${planned.entry.path}: ${now.reason || 'it cannot be used now'} (changed since the plan)`);
    return null;
  }
  const paths = removedPaths([now]);
  applyRemoval(now);
  return paths;
}

function isEmptyRealDir(dir) {
  return isRealDir(dir) && fs.readdirSync(dir).length === 0;
}

// Why this exists: a skill that is renamed between kit versions is emitted under a
// new folder or file name, and the copy an older install recorded would stay beside
// it (the same skill twice). At the end of a run, remove such a leftover, only when
// ALL hold: an earlier record names it; this run did not write it; it lies under a
// skills or rules folder this run emitted into; it is a recorded copy with the kit's
// marker in its first 4 KB; it is a regular file with no link on its path; and its
// bytes still equal the recorded hash. A leftover the user changed is kept, reported.
function hasMarkerInHead(file) {
  const head = Buffer.alloc(4096);
  const fd = fs.openSync(file, 'r');
  try {
    return head.subarray(0, fs.readSync(fd, head, 0, 4096, 0)).includes(GENERATED_MARKER);
  } finally {
    fs.closeSync(fd);
  }
}

function removeStaleGenerated() {
  let removed = 0;
  const kept = [];
  for (const [rel, entry] of [...priorEntries]) {
    if (recorded.has(rel) || entry.kind !== 'copy' || !entry.hash) continue;
    if (!(rel.endsWith('/SKILL.md') || rel.endsWith('.mdc'))) continue;
    if (![...emittedDirs].some((d) => rel.startsWith(d + '/'))) continue;
    const file = resolveOrWarn(rel, `record entry ${JSON.stringify(rel)}`);
    if (!file) continue;
    try {
      if (behindLink(file) || !fs.lstatSync(file).isFile() || !hasMarkerInHead(file)) continue;
      if (sha256(fs.readFileSync(file)) !== entry.hash) {
        kept.push(rel);
        continue;
      }
      fs.unlinkSync(file);
      priorEntries.delete(rel);
      removed += 1;
      const folder = path.dirname(file);
      if (rel.endsWith('/SKILL.md') && isEmptyRealDir(folder)) fs.rmdirSync(folder);
    } catch (e) {
      /* unreadable or already gone: leave it to uninstall */
    }
  }
  if (removed) log(`  ${green('✓')} Removed ${removed} generated file(s) the kit no longer emits (renamed skills)`);
  if (kept.length) {
    log(`  ${yellow('!')} Kept ${kept.length} old generated file(s) you changed: ${kept.slice(0, 5).join(', ')}`);
  }
}

// Remove folders that became empty once their entries were removed, up to the project. Each
// folder is looked at again first: a link anywhere on its path stops it (R6).
function pruneEmptyAncestors(base, removed) {
  for (const rel of removed) {
    if (rel.startsWith('.git/')) continue; // git's own folders are never pruned
    let dir = path.dirname(path.join(base, rel));
    while (dir !== base && dir.startsWith(base + path.sep)) {
      const spot = inspectPath(path.relative(base, dir).split(path.sep).join('/'), false);
      if (spot.problem || !spot.st || !spot.st.isDirectory() || !isEmptyRealDir(dir)) break;
      fs.rmdirSync(dir);
      dir = path.dirname(dir);
    }
  }
}

function dirsUnder(root) {
  const dirs = [];
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue; // a link to a folder is not a folder here
    const full = path.join(root, entry.name);
    dirs.push(...dirsUnder(full), full);
  }
  return dirs; // deepest first
}

// The installer's own folders once empty, and the empty folders left under agents/.
function pruneEmptyDirs(base) {
  for (const name of ['.gabbe-agents', '.gabbe']) {
    if (isEmptyRealDir(path.join(base, name))) fs.rmdirSync(path.join(base, name));
  }
  const kit = path.join(base, 'agents');
  if (!isRealDir(kit)) return;
  for (const dir of dirsUnder(kit)) {
    if (isEmptyRealDir(dir)) fs.rmdirSync(dir);
  }
  if (isEmptyRealDir(kit)) fs.rmdirSync(kit);
}

// Files still under agents/ after an uninstall: the user's own, changed, memory, backups.
function remainingKitFiles(base) {
  const kit = path.join(base, 'agents');
  if (!isRealDir(kit)) return [];
  const found = [];
  const visit = (dir) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) visit(full);
      else found.push(full);
    }
  };
  visit(kit);
  return found;
}

// `--agents` words become the slugs the record uses: `claude` -> `claude-code`.
function agentSlugsFromArgs(words) {
  const given = words.map((w) => w.trim()).filter(Boolean);
  if (!words.some((w) => w !== '')) return null; // no --agents: all agents
  return given.map((w) => (AGENT_ALIASES[w.toLowerCase()] ? agentSlug(AGENT_ALIASES[w.toLowerCase()]) : w));
}

function runUninstall(opts) {
  try {
    return uninstallNow(opts);
  } catch (e) {
    if (!e.gabbeFatal) throw e;
    process.stderr.write(red(`Error: ${e.message}`) + '\n');
    return 1;
  }
}

function uninstallNow(opts) {
  const record = requireRecord('Nothing was removed.');
  if (!record) return 1;
  const base = fs.realpathSync(PROJECT_ROOT);
  const agents = agentSlugsFromArgs(opts.agents);
  const { toRemove, kept } = planRemoval(record.entries, agents);
  const removed = removedPaths(toRemove);
  if (opts.dryRun) {
    removed.forEach((p) => log(`  ${p}`));
    log(`Would remove ${removed.length} path(s) from ${base}`);
    return 0;
  }
  const removedNow = [];
  for (const planned of toRemove) {
    const paths = removeEntry(planned);
    if (paths) removedNow.push(...paths);
    else kept.push(planned.entry); // skipped now: it stays in the record
  }
  if (kept.length && agents !== null) {
    record.entries = kept;
    record.agents = (record.agents || []).filter((a) => !agents.includes(a));
    writeRecordFile(record);
  } else if (fs.existsSync(MANIFEST_FILE)) {
    fs.unlinkSync(MANIFEST_FILE);
  }
  pruneEmptyAncestors(base, removedNow);
  pruneEmptyDirs(base);
  log(`Removed ${removedNow.length} path(s) from ${base}`);
  const left = agents && agents.length ? [] : remainingKitFiles(base);
  if (left.length) {
    log(
      `Kept ${left.length} file(s) under agents/ that the install did not create or that you ` +
        'changed (your own files, memory, backups). Delete them yourself if you no longer need them.'
    );
  }
  return 0;
}

// The agents an install record names, as canonical names (for `update`).
function recordedAgents(record) {
  const slugs = new Set(record.agents || []);
  record.entries.forEach((e) => e && e.agent && e.agent !== 'shared' && slugs.add(e.agent));
  const names = [...new Set(Object.values(AGENT_ALIASES))];
  const known = names.filter((n) => slugs.has(agentSlug(n)));
  const unknown = [...slugs].filter((s) => !names.some((n) => agentSlug(n) === s));
  return { known, unknown };
}

// update = init with the agents the record already names: the same safe-copy rules,
// no agent added or removed.
function runUpdate(opts) {
  const record = requireRecord('Nothing was changed.');
  if (!record) return 1;
  const { known, unknown } = recordedAgents(record);
  log(`update: refreshing the kit copy from this package, the same as \`init\` with the agents the record names (${known.join(', ') || 'none'}).`);
  log('Files you changed are backed up first. No agent is added or removed.');
  if (opts.agents.some(Boolean)) log(`  ${yellow('!')} --agents is ignored: update never changes which agents are wired`);
  if (opts.hooks) log(`  ${yellow('!')} --hooks is ignored: update keeps the hooks the record names and never adds any`);
  if (unknown.length) log(`  ${yellow('!')} Not re-wired (not an agent of this installer): ${unknown.join(', ')}`);
  return runInit({ ...opts, wizard: false, hooks: false, agents: [], recordedAgents: known, keepHooks: recordedHooks(record) });
}

// Read-only report. Exit 0 when the install is consistent, 1 when not.
function runDoctor() {
  let problems = 0;
  const report = (ok, text) => {
    if (!ok) problems += 1;
    log(`  ${ok ? green('✓') : red('x')} ${text}`);
  };
  const kitMd = path.join(PROJECT_ROOT, 'agents', 'AGENTS.md');
  report(fs.existsSync(kitMd), fs.existsSync(kitMd) ? 'kit: agents/AGENTS.md present' : 'kit: agents/AGENTS.md is missing');
  const problem = recordProblem();
  const hasRecord = !problem && fs.existsSync(MANIFEST_FILE);
  if (problem) report(false, `install record: ${problem}`);
  else report(hasRecord, hasRecord ? 'install record: readable' : 'install record: none (.gabbe/manifest.json)');
  if (hasRecord) {
    const record = readRecord();
    const missing = [];
    const dangling = [];
    let changed = 0;
    for (const entry of record.entries) {
      let file;
      try {
        file = resolveWithin(entry && entry.path);
      } catch (e) {
        report(false, `record names a path outside the project: ${entry && entry.path}`);
        continue;
      }
      const refused = entryProblem(entry, false);
      if (refused) {
        log(`kept ${entry.path}: ${refused}`);
        continue;
      }
      if (!pathTaken(file)) missing.push(entry.path);
      else if (entry.kind === 'symlink' && !fs.existsSync(file)) dangling.push(entry.path);
      else if (entry.kind === 'copy' && isModifiedCopy(entry, file)) changed += 1;
      else if (entry.kind === 'block' && fs.lstatSync(file).isFile() && !fs.readFileSync(file).includes(POINTER_BEGIN)) changed += 1;
    }
    report(missing.length === 0, `${record.entries.length} recorded paths: ${missing.length} missing` + (missing.length ? ` (${missing.slice(0, 3).join(', ')}${missing.length > 3 ? ', ...' : ''})` : ''));
    report(dangling.length === 0, `${dangling.length} dangling link(s)` + (dangling.length ? `: ${dangling.join(', ')}` : ''));
    log(`  ${blue('→')} ${changed} recorded file(s) changed since install (yours: normal)`);
    log(`  ${blue('→')} agents wired: ${(record.agents || []).join(', ') || 'none (universal targets only)'}`);
  }
  log(`  ${blue('→')} ${countPlaceholders(kitMd)} [PLACEHOLDER] field(s) left in agents/AGENTS.md (your agent fills them: step 2 of BOOTSTRAP_MISSION.md)`);
  log(problems ? red(`Not consistent: ${problems} problem(s).`) : green('Consistent.'));
  return problems ? 1 : 0;
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

const USAGE = `gabbe - Generative Architectural Brain Base Engine (kit installer)

Usage:
  gabbe init [options]        Install the GABBE kit into the current directory
  gabbe update [--force]      Refresh the kit copy; re-wire only the agents the record names
  gabbe uninstall [options]   Reverse an install from .gabbe/manifest.json
  gabbe doctor                Read-only check of the install (exit 1 when not consistent)
  gabbe --help                Show this help

Every command acts on the current folder, or on the folder given with --dir.

Options (all commands):
  --dir <path>      The project folder to act on instead of the current folder; it must
                    exist. Run the package from another folder and name the project here:
                    a project's own .npmrc and node_modules then do not decide what runs.

Options (init):
  --agents <list>   Comma-separated agents to wire, e.g. claude,cursor,copilot.
                    Known: claude, cursor, windsurf, cline, aider, devin,
                    gemini, antigravity, opencode, zed, continue, roo, kilo,
                    codex, copilot, vscode.
  --yes, -y         Non-interactive: accept defaults, do not prompt.
  --force           Also refresh preserved files such as AGENTS.md and
                    CONSTITUTION.md, and replace an instruction file you
                    already had with a link to the kit's (the old copy is
                    backed up first; a backup is never overwritten).
  --hooks           Also install the optional enforcement hooks (off unless
                    given): for claude and cursor if named in --agents, a merge
                    into .claude/settings.json / .cursor/hooks.json; in a git
                    repository, the pre-commit and pre-push hooks. Nothing of
                    yours is replaced; \`uninstall\` reverses it.
  --wizard          Delegate to the full Python wizard (scripts/init.py) if
                    python3 is available (interactive, richer configuration).
  --help, -h        Show this help.

Options (uninstall):
  --dry-run         Print every path that would be removed; change nothing.
  --agents <list>   Deselect only these agents' wiring (default: all).
  --purge           Accepted for compatibility; the same as a plain uninstall.

What init does (Node path, no Python required):
  - Copies the bundled kit into agents/ (nothing is written into your docs/).
  - Writes a root AGENTS.md (agents.md open standard). If you already have
    one it is kept, and a short block pointing to agents/AGENTS.md is added.
  - Emits the universal .agents/skills/<slug>/SKILL.md tree.
  - Wires per-agent rule files for any agents passed via --agents.
  - Writes BOOTSTRAP_MISSION.md, the first prompt for your agent.
  - Records every path in .gabbe/manifest.json so \`uninstall\` removes
    exactly what was installed (and nothing else).

Examples:
  npx gabbe-kit init --agents claude,cursor --yes
  npx gabbe-kit init --agents claude --hooks
  npx gabbe-kit uninstall --dry-run
  npx gabbe-kit@<version> init --yes --dir /path/to/project   (from another folder)
  npx gabbe-kit update
  npx gabbe-kit init --wizard
`;

const COMMANDS = ['init', 'update', 'uninstall', 'doctor'];

function parseArgs(argv) {
  const opts = {
    command: null,
    agents: [],
    yes: false,
    wizard: false,
    help: false,
    force: false,
    hooks: false,
    dryRun: false,
    dir: null,
    unknown: [],
    badOption: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (COMMANDS.includes(a) && (opts.command === null || opts.command === a)) {
      opts.command = a;
    } else if (a === '--dry-run') {
      opts.dryRun = true;
    } else if (a === '--purge') {
      /* accepted for compatibility with `gabbe uninstall --purge` */
    } else if (a === '--help' || a === '-h') {
      opts.help = true;
    } else if (a === '--yes' || a === '-y') {
      opts.yes = true;
    } else if (a === '--force') {
      opts.force = true;
    } else if (a === '--hooks') {
      opts.hooks = true;
    } else if (a === '--wizard') {
      opts.wizard = true;
    } else if (a === '--dir') {
      if (i + 1 >= argv.length) {
        process.stderr.write(red('--dir needs a path') + '\n');
        opts.badOption = true;
      } else {
        opts.dir = argv[++i];
      }
    } else if (a.startsWith('--dir=')) {
      opts.dir = a.slice('--dir='.length);
    } else if (a === '--agents') {
      opts.agents = (argv[++i] || '').split(',');
    } else if (a.startsWith('--agents=')) {
      opts.agents = a.slice('--agents='.length).split(',');
    } else if (a.startsWith('-')) {
      process.stderr.write(red(`Unknown option: ${a}`) + '\n');
      opts.badOption = true;
    } else {
      // An unknown word (e.g. `gabbe doctor`, a command of the PyPI CLI) must
      // not fall through to the default `init` and copy the kit.
      opts.unknown.push(a);
    }
  }
  return opts;
}

// `--dir <path>` makes that folder the project. Returns an error text, or null when it is set.
function chooseProject(dir) {
  if (dir === null) return null;
  try {
    const real = fs.realpathSync(path.resolve(process.cwd(), dir));
    if (!fs.statSync(real).isDirectory()) throw new Error('not a folder');
    setProjectRoot(real);
    return null;
  } catch (e) {
    return `--dir ${JSON.stringify(dir)}: there is no such folder. Nothing was changed.`;
  }
}

function resolveAgents(rawList) {
  const resolved = [];
  const seen = new Set();
  for (const raw of rawList) {
    const key = String(raw || '').trim().toLowerCase();
    if (!key) continue;
    const canonical = AGENT_ALIASES[key];
    if (!canonical) {
      log(`  ${yellow('!')} Unknown agent "${raw}" -- skipping`);
      continue;
    }
    if (!seen.has(canonical)) {
      seen.add(canonical);
      resolved.push(canonical);
    }
  }
  return resolved;
}

function delegateToPython(opts) {
  const initPy = path.join(KIT_ROOT, 'scripts', 'init.py');
  if (!fs.existsSync(initPy)) {
    log(red(`Cannot find scripts/init.py at ${initPy}`));
    return 1;
  }
  for (const py of ['python3', 'python']) {
    const probe = spawnSync(py, ['--version'], { stdio: 'ignore' });
    if (probe.status === 0) {
      log(blue(`→ Delegating to the Python wizard (${py} ${initPy})...`));
      const args = [initPy, ...(opts && opts.force ? ['--force'] : []), ...(opts && opts.hooks ? ['--hooks'] : [])];
      const res = spawnSync(py, args, { stdio: 'inherit', cwd: PROJECT_ROOT });
      return res.status == null ? 1 : res.status;
    }
  }
  log(red('--wizard requested but python3/python is not available on PATH.'));
  log(yellow('Re-run without --wizard to use the pure-Node installer.'));
  return 1;
}

function runInit(opts) {
  if (opts.wizard) {
    return delegateToPython(opts);
  }

  if (!fs.existsSync(SOURCE_AGENTS_DIR)) {
    log(red(`Error: bundled kit not found at ${SOURCE_AGENTS_DIR}`));
    log(yellow('The gabbe package appears to be incomplete (missing agents/).'));
    return 1;
  }

  log(blue('='.repeat(60)));
  log(blue('GABBE - Agentic Engineering Kit installer (Node)'));
  log(blue('='.repeat(60)));
  log(`Source kit : ${KIT_ROOT}`);
  log(`Target     : ${PROJECT_ROOT}`);
  log('');

  const linked = recordLinkProblem();
  if (linked) {
    process.stderr.write(red(`Error: ${linked}. Move it away and run the installer again.`) + ' Nothing was changed.\n');
    return 1;
  }
  loadPriorManifest();

  // --- Copy the kit into the project (agents/ only; the project's docs/ is not touched) ---
  log(yellow('Part 1: Copying kit'));
  const targetAgents = path.join(PROJECT_ROOT, 'agents');
  if (fs.existsSync(targetAgents) && !fs.statSync(targetAgents).isDirectory()) {
    process.stderr.write(
      red(`Error: ${targetAgents} exists and is not a folder. Move it away and run the installer again.`) +
        ' Nothing was changed.\n'
    );
    return 1;
  }
  const agentsMdSrc = path.join(targetAgents, 'AGENTS.md');
  const skillsSrc = path.join(targetAgents, 'skills');
  const ownAgentsMd = userOwnsKitEntryFile(agentsMdSrc);
  if (path.resolve(targetAgents) === path.resolve(SOURCE_AGENTS_DIR)) {
    log(`  ${blue('→')} Target agents/ is the source; skipping copy.`);
  } else {
    const n = safeCopyTree(SOURCE_AGENTS_DIR, targetAgents, opts.force, Boolean(opts.recordedAgents));
    log(`  ${green('✓')} Copied agents/ (${n} files, user content preserved)`);
  }
  if (ownAgentsMd && !opts.force) {
    log(`  ${yellow('!')} agents/AGENTS.md already existed and was kept. It is not the kit's file,`);
    log('    so the kit has no entry file of its own. To install the kit\'s file, re-run');
    log('    with --force (yours is backed up first as agents/AGENTS.md.gabbe-bak).');
  }

  // --- Universal targets (always emitted) ---
  log('');
  log(yellow('Part 2: Universal wiring'));

  // Root AGENTS.md (agents.md open standard).
  const rootAgentsMd = path.join(PROJECT_ROOT, 'AGENTS.md');
  if (fs.existsSync(agentsMdSrc)) {
    if (path.resolve(rootAgentsMd) !== path.resolve(agentsMdSrc)) {
      if (wireAgentsLink(rootAgentsMd, agentsMdSrc, 'shared', opts.force)) {
        log(`  ${green('✓')} Wired root AGENTS.md (agents.md standard)`);
      }
    }
  } else {
    log(`  ${yellow('!')} agents/AGENTS.md not found; root AGENTS.md not wired.`);
  }

  // Universal .agents/skills/<slug>/SKILL.md tree.
  if (fs.existsSync(skillsSrc)) {
    const n = emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.agents', 'skills'), 'shared');
    log(`  ${green('✓')} Emitted ${n} universal skills (.agents/skills/<slug>/SKILL.md)`);
  } else {
    log(`  ${yellow('!')} agents/skills not found; universal skills not emitted.`);
  }

  // --- Per-agent wiring ---
  const agents = opts.recordedAgents || resolveAgents(opts.agents);
  if (agents.length) {
    log('');
    log(yellow('Part 3: Per-agent wiring'));
    const ctx = { skillsSrc, agentsMdSrc, force: opts.force };
    for (const agent of agents) {
      wireAgent(agent, ctx);
    }
  } else if (opts.recordedAgents) {
    log('');
    log(`  ${blue('→')} The install record names no agent; only universal targets refreshed.`);
  } else {
    log('');
    log(`  ${blue('→')} No --agents specified; only universal targets wired.`);
    log(`  ${blue('→')} Re-run with e.g. --agents claude,cursor to wire tools.`);
  }

  // --- Optional hooks: only when asked (init --hooks), or kept by update when the record names them ---
  if (opts.hooks || opts.keepHooks) {
    const keep = opts.keepHooks;
    const scope = keep
      ? { agents: agents, merges: keep.merges, git: keep.git }
      : { agents: agents, merges: null, git: true };
    if (!keep || keep.merges.size || keep.git) installHooks(scope, targetAgents);
  }

  // --- First prompt + install record ---
  log('');
  log(yellow('Part 4: First prompt and install record'));
  const missionFile = path.join(PROJECT_ROOT, 'BOOTSTRAP_MISSION.md');
  if (writeTextIfAbsent(missionFile, BOOTSTRAP_MISSION, 'shared')) {
    log(`  ${green('✓')} Wrote BOOTSTRAP_MISSION.md (the first prompt for your agent)`);
  } else {
    log(`  ${blue('→')} BOOTSTRAP_MISSION.md exists, leaving as-is`);
  }
  removeStaleGenerated();
  writeManifest();
  if (skippedLinks.length) {
    const shown = skippedLinks.slice(0, 5).join(', ') + (skippedLinks.length > 5 ? ', ...' : '');
    log(
      `  ${yellow('!')} Left ${skippedLinks.length} path(s) alone because they are links of yours, or sit` +
        ` behind one: ${shown}`
    );
  }

  log('');
  log(green('Setup complete.'));
  log(`The kit is installed at: ${targetAgents}`);
  const placeholders = countPlaceholders(agentsMdSrc);
  if (placeholders) {
    log(
      `${yellow('!')} agents/AGENTS.md has ${placeholders} [PLACEHOLDER] fields (commands, stack, repository).`
    );
    log('  Your agent fills them in as the first step of BOOTSTRAP_MISSION.md, or edit the file yourself.');
  }
  log('Next step: open your coding agent in this folder and tell it:');
  log('  "Read BOOTSTRAP_MISSION.md and follow it."');
  return 0;
}

// True when agents/AGENTS.md is there before the copy, no earlier install recorded
// it, and it is not the kit's file: the user's own file in the user's own agents/.
function userOwnsKitEntryFile(agentsMd) {
  if (!fs.existsSync(agentsMd) || priorEntries.has(relToProject(agentsMd))) return false;
  try {
    const kit = fs.readFileSync(path.join(SOURCE_AGENTS_DIR, 'AGENTS.md'));
    return !fs.readFileSync(agentsMd).equals(kit);
  } catch (e) {
    return false;
  }
}

function countPlaceholders(agentsMd) {
  try {
    return (fs.readFileSync(agentsMd, 'utf8').match(/\[PLACEHOLDER/g) || []).length;
  } catch (e) {
    return 0;
  }
}

// The first prompt. The wizard (scripts/init.py) writes a project-specific one
// from its questions; this installer asks nothing, so the agent does step 2.
const BOOTSTRAP_MISSION = `# BOOTSTRAP MISSION: first session with the GABBE kit

Tell your coding agent: "Read BOOTSTRAP_MISSION.md and follow it."

## 1. Read

- \`AGENTS.md\` and \`agents/AGENTS.md\`: rules, commands, lifecycle, skills index.
- \`agents/CONSTITUTION.md\`: the project law.

## 2. Fill in the project facts

\`agents/AGENTS.md\` has \`[PLACEHOLDER]\` fields (commands, stack, repository, conventions).
Fill in the ones you can verify from this repository: package files, scripts, CI
configuration. Ask the human for the rest. Do not guess.

## 3. Ask the human which case this is, then stop for the answer

- **New project:** ask what to build, then use \`agents/skills/product/spec-writer.skill.md\`
  to write the requirements. Wait for the human's approval before any design or code.
- **Existing codebase:** change nothing yet. Map the code, get the existing build and tests
  running, record what you found in \`agents/memory/PROJECT_STATE.md\`, and propose a
  short plan. \`agents/skills/architecture/legacy-modernization.skill.md\` describes the method.
- **Returning to earlier work:** use \`agents/skills/core/session-resume.skill.md\`.

## Rules for this session

- Stop at every Human Approval Gate.
- No commit, push, tag, publish or deploy unless the human asks for it in that request.
- Report what you did and what you could not verify.
`;

function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.unknown.length) {
    process.stderr.write(red(`Unknown command: ${opts.unknown.join(' ')}`) + '\n');
    process.stderr.write(
      'The npm package has init, update, uninstall and doctor; the other CLI commands\n' +
        '(route, brain, gateway, ...) come from the PyPI package (pipx install gabbe).\n\n'
    );
    process.stderr.write(USAGE);
    return 1;
  }
  if (opts.badOption) {
    process.stderr.write(USAGE);
    return 2;
  }
  if (opts.help) {
    process.stdout.write(USAGE);
    return 0;
  }
  const dirError = chooseProject(opts.dir);
  if (dirError) {
    process.stderr.write(red(`Error: ${dirError}`) + '\n');
    return 2;
  }
  // `init` is the default command.
  if (opts.command === null) opts.command = 'init';
  if (opts.command === 'uninstall') return runUninstall(opts);
  if (opts.command === 'doctor') return runDoctor();
  if (opts.command === 'init' || opts.command === 'update') {
    try {
      return opts.command === 'update' ? runUpdate(opts) : runInit(opts);
    } catch (e) {
      // Record what was written before the stop, so it can still be uninstalled.
      if (recorded.size) {
        try {
          writeManifest();
        } catch (e2) {
          /* the original error is the one to report */
        }
      }
      if (!e.gabbeFatal) throw e;
      process.stderr.write(red(`Error: ${e.message}`) + '\n');
      return 1;
    }
  }
  process.stdout.write(USAGE);
  return 0;
}

// Output to a pipe is asynchronous in Node on POSIX: process.exit() right after a write can cut
// the rest of the output when the pipe is small or its reader is slow (the exit code stays 0).
// Make both streams blocking before anything is printed, so every line is written before exit.
function makeOutputBlocking() {
  for (const stream of [process.stdout, process.stderr]) {
    try {
      if (stream._handle && typeof stream._handle.setBlocking === 'function') {
        stream._handle.setBlocking(true);
      }
    } catch (_) { /* a stream that cannot be made blocking stays as it is */ }
  }
}

makeOutputBlocking();
process.exit(main());
