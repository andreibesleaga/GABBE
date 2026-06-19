#!/usr/bin/env node
// SPDX-License-Identifier: Apache-2.0
//
// GABBE installer (Python-independent).
//
// This is the PRIMARY installer for `npx gabbe-kit init`. It bundles the Markdown
// kit (agents/, docs/) and wires it into the current project using only the
// Node standard library -- no npm dependencies, no Python required.
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

const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawnSync } = require('child_process');

// ---------------------------------------------------------------------------
// Paths / colors
// ---------------------------------------------------------------------------

// The bundled kit lives one level up from bin/ (the package root).
const KIT_ROOT = path.resolve(__dirname, '..');
const SOURCE_AGENTS_DIR = path.join(KIT_ROOT, 'agents');
const SOURCE_DOCS_DIR = path.join(KIT_ROOT, 'docs');
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

// Back up an existing target file to <name>.gabbe-bak before it is overwritten.
// The first backup wins (never overwrite an existing .gabbe-bak), so re-running
// install preserves the user's ORIGINAL, not a kit copy from a prior run.
function backupBeforeOverwrite(dst) {
  const backup = dst + '.gabbe-bak';
  if (!fs.existsSync(backup)) {
    try {
      fs.copyFileSync(dst, backup);
      log(`  ${yellow('!')} Backed up existing ${path.basename(dst)} -> ${path.basename(backup)}`);
    } catch (e) {
      /* best-effort backup */
    }
  }
}

// Copy a directory tree without ever losing user data. Preserved files are left
// untouched; any other differing pre-existing file is backed up to .gabbe-bak
// before being refreshed. With force=true, even preserved files are re-templated
// (still backed up first). Mirrors init.py safe_merge_directory.
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
    copied += 1;
  }
  return copied;
}

// Wire a rule file pointing at the kit's AGENTS.md. Prefer a relative symlink
// (like init.py); fall back to a copy on platforms/filesystems that refuse
// symlinks (e.g. Windows without privileges). Backs up existing non-symlink.
function wireAgentsLink(target, sourceAgentsMd) {
  fs.mkdirSync(path.dirname(target), { recursive: true });
  try {
    const st = fs.lstatSync(target);
    if (st.isSymbolicLink()) {
      fs.unlinkSync(target);
    } else {
      const backup = target + '.bak';
      fs.renameSync(target, backup);
      log(`  ${yellow('!')} Backed up existing ${path.basename(target)} -> ${path.basename(backup)}`);
    }
  } catch (e) {
    /* target does not exist */
  }
  const linkPath = path.relative(path.dirname(target), sourceAgentsMd);
  try {
    fs.symlinkSync(linkPath, target);
    log(`  ${green('✓')} Linked ${path.relative(PROJECT_ROOT, target)} -> ${linkPath}`);
  } catch (e) {
    fs.copyFileSync(sourceAgentsMd, target);
    log(`  ${green('✓')} Copied ${path.relative(PROJECT_ROOT, target)} (symlink fallback)`);
  }
}

// Emit the universal .agents/skills/<slug>/SKILL.md tree (agentskills.io).
// Reads every agents/skills/**/*.skill.md and writes a real SKILL.md file.
function emitUniversalSkills(skillsSrcDir, targetSkillsDir) {
  fs.mkdirSync(targetSkillsDir, { recursive: true });
  let count = 0;
  for (const skillFile of walk(skillsSrcDir)) {
    if (!skillFile.endsWith('.skill.md')) continue;
    const content = fs.readFileSync(skillFile, 'utf8');
    const meta = parseFrontmatter(content);
    const fallback = path.basename(skillFile).replace(/\.skill\.md$/, '');
    const slug = safeSlug(meta.name, fallback);
    const folder = path.join(targetSkillsDir, slug);
    fs.mkdirSync(folder, { recursive: true });
    fs.writeFileSync(path.join(folder, 'SKILL.md'), injectSchemaVersion(content));
    count += 1;
  }
  return count;
}

// Emit Cursor flat .mdc rules (.cursor/rules/<slug>.mdc) -- mirrors the Cursor
// branch of compile_skills.py.
function emitCursorRules(skillsSrcDir, cursorRulesDir) {
  fs.mkdirSync(cursorRulesDir, { recursive: true });
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
    fs.writeFileSync(path.join(cursorRulesDir, `${slug}.mdc`), cursorFm + '\n' + body);
    count += 1;
  }
  return count;
}

function writeJsonIfAbsent(filePath, obj) {
  if (fs.existsSync(filePath)) return false;
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(obj, null, 2) + '\n');
  return true;
}

// ---------------------------------------------------------------------------
// Per-agent wiring (mirrors scripts/init.py Step 5 conventions)
// ---------------------------------------------------------------------------

function wireAgent(agent, ctx) {
  const { skillsSrc, agentsMdSrc } = ctx;
  switch (agent) {
    case 'Claude Code':
      wireAgentsLink(path.join(PROJECT_ROOT, '.claude', 'CLAUDE.md'), agentsMdSrc);
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.claude', 'skills'));
      log(`  ${green('✓')} Wired Claude Code (.claude/CLAUDE.md + .claude/skills)`);
      break;
    case 'Cursor':
      wireAgentsLink(path.join(PROJECT_ROOT, '.cursorrules'), agentsMdSrc);
      emitCursorRules(skillsSrc, path.join(PROJECT_ROOT, '.cursor', 'rules'));
      log(`  ${green('✓')} Wired Cursor (.cursorrules + .cursor/rules)`);
      break;
    case 'Windsurf':
      wireAgentsLink(path.join(PROJECT_ROOT, '.windsurfrules'), agentsMdSrc);
      wireAgentsLink(path.join(PROJECT_ROOT, '.windsurf', 'skills', 'AGENTS.md'), agentsMdSrc);
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.windsurf', 'skills'));
      log(`  ${green('✓')} Wired Windsurf (.windsurfrules + .windsurf/skills)`);
      break;
    case 'Cline':
      wireAgentsLink(path.join(PROJECT_ROOT, '.clinerules'), agentsMdSrc);
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.cline', 'skills'));
      log(`  ${green('✓')} Wired Cline (.clinerules + .cline/skills)`);
      break;
    case 'Devin / Cognition':
      wireAgentsLink(path.join(PROJECT_ROOT, '.devinrules'), agentsMdSrc);
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.devin', 'skills'));
      log(`  ${green('✓')} Wired Devin (.devinrules + .devin/skills)`);
      break;
    case 'Aider': {
      const aiderConf = path.join(PROJECT_ROOT, '.aider.conf.yml');
      if (!fs.existsSync(aiderConf)) {
        fs.writeFileSync(aiderConf, 'read:\n  - agents/AGENTS.md\n  - agents/skills/\n');
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
      });
      wireAgentsLink(path.join(PROJECT_ROOT, 'GEMINI.md'), agentsMdSrc);
      log(`  ${green('✓')} Wired .gemini/settings.json + GEMINI.md`);
      break;
    }
    case 'Antigravity':
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.agents', 'skills'));
      log(`  ${green('✓')} Wired Antigravity (.agents/skills + root AGENTS.md)`);
      break;
    case 'OpenCode': {
      const opencodeConf = path.join(PROJECT_ROOT, 'opencode.json');
      writeJsonIfAbsent(opencodeConf, {
        $schema: 'https://opencode.ai/config.json',
        instructions: ['AGENTS.md', 'agents/skills/'],
      });
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.agents', 'skills'));
      log(`  ${green('✓')} Wired opencode.json + .agents/skills`);
      break;
    }
    case 'Zed':
      wireAgentsLink(path.join(PROJECT_ROOT, '.rules'), agentsMdSrc);
      log(`  ${green('✓')} Wired Zed (.rules)`);
      break;
    case 'Continue':
      wireAgentsLink(path.join(PROJECT_ROOT, '.continue', 'rules', 'agents.md'), agentsMdSrc);
      log(`  ${green('✓')} Wired Continue (.continue/rules/agents.md)`);
      break;
    case 'Roo Code':
      wireAgentsLink(path.join(PROJECT_ROOT, '.roo', 'rules', 'agents.md'), agentsMdSrc);
      log(`  ${green('✓')} Wired Roo Code (.roo/rules/agents.md)`);
      break;
    case 'Kilo Code':
      wireAgentsLink(path.join(PROJECT_ROOT, '.kilocode', 'rules', 'agents.md'), agentsMdSrc);
      log(`  ${green('✓')} Wired Kilo Code (.kilocode/rules/agents.md)`);
      break;
    case 'OpenAI / Codex':
      wireAgentsLink(path.join(PROJECT_ROOT, '.codex', 'AGENTS.md'), agentsMdSrc);
      log(`  ${green('✓')} Wired Codex (.codex/AGENTS.md)`);
      break;
    case 'GitHub Copilot':
      wireAgentsLink(path.join(PROJECT_ROOT, '.github', 'copilot-instructions.md'), agentsMdSrc);
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.github', 'skills'));
      log(`  ${green('✓')} Wired GitHub Copilot (.github/copilot-instructions.md + .github/skills)`);
      break;
    case 'VS Code':
      emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.github', 'skills'));
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
  --wizard          Delegate to the full Python wizard (scripts/init.py) if
                    python3 is available (interactive, richer configuration).
  --help, -h        Show this help.

What it does (Node path, no Python required):
  - Copies the bundled kit (agents/, docs/) into the current project.
  - Writes a root AGENTS.md (agents.md open standard).
  - Emits the universal .agents/skills/<slug>/SKILL.md tree.
  - Wires per-agent rule files for any agents passed via --agents.

Examples:
  npx gabbe-kit init --agents claude,cursor --yes
  npx gabbe-kit init --wizard
`;

function parseArgs(argv) {
  const opts = { command: null, agents: [], yes: false, wizard: false, help: false, force: false };
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
      log(red(`Unknown option: ${a}`));
      opts.help = true;
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

function delegateToPython() {
  const initPy = path.join(KIT_ROOT, 'scripts', 'init.py');
  if (!fs.existsSync(initPy)) {
    log(red(`Cannot find scripts/init.py at ${initPy}`));
    return 1;
  }
  for (const py of ['python3', 'python']) {
    const probe = spawnSync(py, ['--version'], { stdio: 'ignore' });
    if (probe.status === 0) {
      log(blue(`→ Delegating to the Python wizard (${py} ${initPy})...`));
      const res = spawnSync(py, [initPy], { stdio: 'inherit' });
      return res.status == null ? 1 : res.status;
    }
  }
  log(red('--wizard requested but python3/python is not available on PATH.'));
  log(yellow('Re-run without --wizard to use the pure-Node installer.'));
  return 1;
}

function runInit(opts) {
  if (opts.wizard) {
    return delegateToPython();
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

  // --- Copy the kit into the project (agents/ + docs/) ---
  log(yellow('Part 1: Copying kit'));
  const targetAgents = path.join(PROJECT_ROOT, 'agents');
  if (path.resolve(targetAgents) === path.resolve(SOURCE_AGENTS_DIR)) {
    log(`  ${blue('→')} Target agents/ is the source; skipping copy.`);
  } else {
    const n = safeCopyTree(SOURCE_AGENTS_DIR, targetAgents, opts.force);
    log(`  ${green('✓')} Copied agents/ (${n} files, user content preserved)`);
  }
  if (fs.existsSync(SOURCE_DOCS_DIR)) {
    const targetDocs = path.join(PROJECT_ROOT, 'docs');
    if (path.resolve(targetDocs) !== path.resolve(SOURCE_DOCS_DIR)) {
      const n = safeCopyTree(SOURCE_DOCS_DIR, targetDocs, opts.force);
      log(`  ${green('✓')} Copied docs/ (${n} files)`);
    }
  }

  const agentsMdSrc = path.join(targetAgents, 'AGENTS.md');
  const skillsSrc = path.join(targetAgents, 'skills');

  // --- Universal targets (always emitted) ---
  log('');
  log(yellow('Part 2: Universal wiring'));

  // Root AGENTS.md (agents.md open standard).
  const rootAgentsMd = path.join(PROJECT_ROOT, 'AGENTS.md');
  if (fs.existsSync(agentsMdSrc)) {
    if (path.resolve(rootAgentsMd) !== path.resolve(agentsMdSrc)) {
      wireAgentsLink(rootAgentsMd, agentsMdSrc);
      log(`  ${green('✓')} Wired root AGENTS.md (agents.md standard)`);
    }
  } else {
    log(`  ${yellow('!')} agents/AGENTS.md not found; root AGENTS.md not wired.`);
  }

  // Universal .agents/skills/<slug>/SKILL.md tree.
  if (fs.existsSync(skillsSrc)) {
    const n = emitUniversalSkills(skillsSrc, path.join(PROJECT_ROOT, '.agents', 'skills'));
    log(`  ${green('✓')} Emitted ${n} universal skills (.agents/skills/<slug>/SKILL.md)`);
  } else {
    log(`  ${yellow('!')} agents/skills not found; universal skills not emitted.`);
  }

  // --- Per-agent wiring ---
  const agents = resolveAgents(opts.agents);
  if (agents.length) {
    log('');
    log(yellow('Part 3: Per-agent wiring'));
    const ctx = { skillsSrc, agentsMdSrc };
    for (const agent of agents) {
      wireAgent(agent, ctx);
    }
  } else {
    log('');
    log(`  ${blue('→')} No --agents specified; only universal targets wired.`);
    log(`  ${blue('→')} Re-run with e.g. --agents claude,cursor to wire tools.`);
  }

  log('');
  log(green('Setup complete.'));
  log(`The kit is installed at: ${targetAgents}`);
  return 0;
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
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
