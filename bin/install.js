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
const PROJECT_ROOT = process.cwd();

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
const MANIFEST_FILE = path.join(PROJECT_ROOT, '.gabbe', 'manifest.json');
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
      if (e && typeof e.path === 'string') priorEntries.set(e.path, e);
    }
  } catch (e) {
    /* no earlier record */
  }
}

// True if `data` (the bytes of `file`) is exactly what an earlier install recorded.
function isUnchangedKitFile(file, data) {
  const entry = priorEntries.get(relToProject(file));
  return Boolean(entry && entry.hash && entry.hash === sha256(data));
}

// Record one created artifact. A link to the user's original (backup_of) that an
// earlier run recorded is kept: a re-run finds its own file and makes no backup.
function record(file, kind, agent, backupOf) {
  const rel = relToProject(file);
  const entry = { path: rel, kind, agent: agent || 'shared', backup_of: backupOf || null };
  if (kind === 'copy') entry.hash = sha256(fs.readFileSync(file));
  const earlier = recorded.get(rel) || priorEntries.get(rel);
  if (!entry.backup_of && earlier && earlier.backup_of) entry.backup_of = earlier.backup_of;
  recorded.set(rel, entry);
}

function writeManifest() {
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
  fs.mkdirSync(path.dirname(MANIFEST_FILE), { recursive: true });
  fs.writeFileSync(MANIFEST_FILE, JSON.stringify(manifest, null, 2) + '\n');
  log(`  ${green('✓')} Recorded ${recorded.size} paths in .gabbe/manifest.json (used by \`gabbe uninstall\`)`);
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
    return null;
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
    log(`  ${yellow('!')} Backed up existing ${path.basename(dst)} -> ${path.basename(backup)}`);
    return backup;
  } catch (e) {
    return null;
  }
}

// Copy a directory tree without ever losing user data. Preserved files are left
// untouched; any other differing pre-existing file is backed up before being
// refreshed. With force=true, even preserved files are re-templated (still backed
// up first). Every file written is recorded. Mirrors init.py safe_merge_directory.
function safeCopyTree(srcRoot, dstRoot, force) {
  if (!fs.existsSync(srcRoot)) return 0;
  let copied = 0;
  for (const src of walk(srcRoot)) {
    const rel = path.relative(srcRoot, src);
    const dst = path.join(dstRoot, rel);
    const fileName = path.basename(src);
    const exists = fs.existsSync(dst);
    if (exists && !force && shouldPreserve(rel, fileName)) {
      continue;
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
function addPointerBlock(target, kitAgentsMd, agent) {
  const text = fs.readFileSync(target, 'utf8');
  const name = path.basename(target);
  if (text.includes(POINTER_BEGIN)) {
    log(`  ${blue('→')} ${name} already points to the kit; left as is`);
    return;
  }
  const backup = backupBeforeOverwrite(target);
  let joiner = '\n\n';
  if (!text || text.endsWith('\n\n')) joiner = '';
  else if (text.endsWith('\n')) joiner = '\n';
  fs.writeFileSync(target, text + joiner + pointerBlock(kitAgentsMd));
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
function wireAgentsLink(target, sourceAgentsMd, agent, force) {
  fs.mkdirSync(path.dirname(target), { recursive: true });
  let backupOf = null;
  let st = null;
  try {
    st = fs.lstatSync(target);
  } catch (e) {
    /* target does not exist */
  }
  if (st && st.isSymbolicLink()) {
    fs.unlinkSync(target);
  } else if (st) {
    const ours = st.isFile() && isUnchangedKitFile(target, fs.readFileSync(target));
    if (st.isFile() && !ours && !force) {
      addPointerBlock(target, relToProject(sourceAgentsMd), agent);
      return;
    }
    if (ours) {
      fs.unlinkSync(target); // our own copy from an earlier run (symlink fallback)
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
}

// Write one generated file (an emitted skill or rule) and record it. A different
// file already at that path is the user's own, or a kit file the user edited: it
// is backed up first, and the backup is linked for restore on uninstall.
function writeGenerated(file, content, agent) {
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

// Emit the universal .agents/skills/<slug>/SKILL.md tree (agentskills.io).
// Reads every agents/skills/**/*.skill.md and writes a real SKILL.md file.
function emitUniversalSkills(skillsSrcDir, targetSkillsDir, agent) {
  let count = 0;
  for (const skillFile of walk(skillsSrcDir)) {
    if (!skillFile.endsWith('.skill.md')) continue;
    const content = fs.readFileSync(skillFile, 'utf8');
    const meta = parseFrontmatter(content);
    const fallback = path.basename(skillFile).replace(/\.skill\.md$/, '');
    const slug = safeSlug(meta.name, fallback);
    writeGenerated(path.join(targetSkillsDir, slug, 'SKILL.md'), injectSchemaVersion(content), agent);
    count += 1;
  }
  return count;
}

// Emit Cursor flat .mdc rules (.cursor/rules/<slug>.mdc) -- mirrors the Cursor
// branch of compile_skills.py.
function emitCursorRules(skillsSrcDir, cursorRulesDir, agent) {
  let count = 0;
  for (const skillFile of walk(skillsSrcDir)) {
    if (!skillFile.endsWith('.skill.md')) continue;
    const content = fs.readFileSync(skillFile, 'utf8');
    const meta = parseFrontmatter(content);
    const fallback = path.basename(skillFile).replace(/\.skill\.md$/, '');
    const slug = safeSlug(meta.name, fallback);
    const desc = meta.description || `Skill for ${meta.name || slug}`;
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
    count += 1;
  }
  return count;
}

// Create a config file only when none exists (a user's own config is never
// replaced), and record it.
function writeTextIfAbsent(filePath, text, agent) {
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
      wireAgentsLink(path.join(PROJECT_ROOT, '.windsurf', 'skills', 'AGENTS.md'), agentsMdSrc, slug, force);
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
// CLI
// ---------------------------------------------------------------------------

const USAGE = `gabbe - Generative Architectural Brain Base Engine (kit installer)

Usage:
  gabbe init [options]      Install the GABBE kit into the current directory
  gabbe --help              Show this help

Options:
  --agents <list>   Comma-separated agents to wire, e.g. claude,cursor,copilot.
                    Known: claude, cursor, windsurf, cline, aider, devin,
                    gemini, antigravity, opencode, zed, continue, roo, kilo,
                    codex, copilot, vscode.
  --yes, -y         Non-interactive: accept defaults, do not prompt.
  --force           Also refresh preserved files such as AGENTS.md and
                    CONSTITUTION.md, and replace an instruction file you
                    already had with a link to the kit's (the old copy is
                    backed up first; a backup is never overwritten).
  --wizard          Delegate to the full Python wizard (scripts/init.py) if
                    python3 is available (interactive, richer configuration).
  --help, -h        Show this help.

What it does (Node path, no Python required):
  - Copies the bundled kit into agents/ (nothing is written into your docs/).
  - Writes a root AGENTS.md (agents.md open standard). If you already have
    one it is kept, and a short block pointing to agents/AGENTS.md is added.
  - Emits the universal .agents/skills/<slug>/SKILL.md tree.
  - Wires per-agent rule files for any agents passed via --agents.
  - Writes BOOTSTRAP_MISSION.md, the first prompt for your agent.
  - Records every path in .gabbe/manifest.json so \`gabbe uninstall\` (the
    PyPI CLI) removes exactly what was installed.

Examples:
  npx gabbe-kit init --agents claude,cursor --yes
  npx gabbe-kit init --wizard
`;

function parseArgs(argv) {
  const opts = {
    command: null,
    agents: [],
    yes: false,
    wizard: false,
    help: false,
    force: false,
    unknown: [],
    badOption: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === 'init') {
      opts.command = 'init';
    } else if (a === '--help' || a === '-h') {
      opts.help = true;
    } else if (a === '--yes' || a === '-y') {
      opts.yes = true;
    } else if (a === '--force') {
      opts.force = true;
    } else if (a === '--wizard') {
      opts.wizard = true;
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
      const args = opts && opts.force ? [initPy, '--force'] : [initPy];
      const res = spawnSync(py, args, { stdio: 'inherit' });
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

  loadPriorManifest();

  // --- Copy the kit into the project (agents/ only; the project's docs/ is not touched) ---
  log(yellow('Part 1: Copying kit'));
  const targetAgents = path.join(PROJECT_ROOT, 'agents');
  const agentsMdSrc = path.join(targetAgents, 'AGENTS.md');
  const skillsSrc = path.join(targetAgents, 'skills');
  const ownAgentsMd = userOwnsKitEntryFile(agentsMdSrc);
  if (path.resolve(targetAgents) === path.resolve(SOURCE_AGENTS_DIR)) {
    log(`  ${blue('→')} Target agents/ is the source; skipping copy.`);
  } else {
    const n = safeCopyTree(SOURCE_AGENTS_DIR, targetAgents, opts.force);
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
      wireAgentsLink(rootAgentsMd, agentsMdSrc, 'shared', opts.force);
      log(`  ${green('✓')} Wired root AGENTS.md (agents.md standard)`);
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
  const agents = resolveAgents(opts.agents);
  if (agents.length) {
    log('');
    log(yellow('Part 3: Per-agent wiring'));
    const ctx = { skillsSrc, agentsMdSrc, force: opts.force };
    for (const agent of agents) {
      wireAgent(agent, ctx);
    }
  } else {
    log('');
    log(`  ${blue('→')} No --agents specified; only universal targets wired.`);
    log(`  ${blue('→')} Re-run with e.g. --agents claude,cursor to wire tools.`);
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
  writeManifest();

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
      'The npm package only installs the kit; `gabbe doctor` and the other CLI\n' +
        'commands come from the PyPI package (pipx install gabbe).\n\n'
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
  // `init` is the default command.
  if (opts.command === null) opts.command = 'init';
  if (opts.command === 'init') {
    return runInit(opts);
  }
  process.stdout.write(USAGE);
  return 0;
}

process.exit(main());
