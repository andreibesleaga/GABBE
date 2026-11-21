/* SPDX-License-Identifier: Apache-2.0 */
// GABBE hook helper: read a shell command as DATA and say whether it is a commit, push, tag,
// publish or deploy, or a destructive git command. Nothing here runs, expands or evaluates any part of the command.
// Limits: aliases, shell functions, scripts that call git, and commands built from variables
// are not seen. See agents/guides/ops/hooks.md.
'use strict';

const ENV_RE = /^[A-Za-z_][A-Za-z0-9_]*=/;
const KEYWORDS = new Set(['{', '}', '!', 'if', 'then', 'else', 'elif', 'do', 'while', 'until']);
// wrapper program -> options that take a value
const WRAPPERS = {
  sudo: ['-u', '-g', '-h', '-p', '-C', '-U', '-r', '-t'],
  doas: ['-u', '-C'],
  env: ['-u', '-C', '-S'],
  nice: ['-n'],
  timeout: ['-s', '-k'],
  nohup: [],
  time: ['-f', '-o', '--format', '--output'],
  setsid: [],
  ionice: ['-c', '-n', '-p'],
  stdbuf: ['-i', '-o', '-e'],
  command: [],
  exec: ['-a'],
  builtin: [],
  xargs: ['-I', '-n', '-L', '-P', '-s', '-d', '-E', '-a'],
};
const SHELLS = new Set(['sh', 'bash', 'dash', 'zsh', 'ksh']);
const GIT_VALUE_OPTS = new Set(['-C', '-c', '--git-dir', '--work-tree', '--namespace', '--exec-path', '--super-prefix', '--config-env']);
const GIT_ASK = new Set(['commit', 'push', 'tag']);
// Destructive git commands (Article 0, destructive actions): the label the guard reports.
const DESTRUCTIVE = new Set(['git reset --hard', 'git clean -f', 'git checkout -- .', 'git restore .', 'git branch -D',
  'git push --force', 'git rebase', 'git filter-branch', 'git filter-repo']);
// Inline interpreters: program pattern -> the options that take program text.
const INLINE = [
  [/^(python[0-9.]*|py|pypy[0-9]*)$/, ['-c']],
  [/^(node|nodejs|bun|deno)$/, ['-e', '-p', '--eval', '--print']],
  [/^perl$/, ['-e', '-E']],
  [/^ruby$/, ['-e']],
  [/^php$/, ['-r']],
];
// program -> words that, among its first three non-option words, mean publish or deploy
const WATCH = {
  npm: ['publish'], pnpm: ['publish'], yarn: ['publish'], bun: ['publish'],
  twine: ['upload'], cargo: ['publish'], gem: ['push'], poetry: ['publish'], uv: ['publish'],
  docker: ['push'], dotnet: ['push'], mvn: ['deploy'], gradle: ['publish'], gradlew: ['publish'],
  kubectl: ['apply'], terraform: ['apply'], tofu: ['apply'], helm: ['install', 'upgrade'],
  railway: ['up', 'deploy'], fly: ['deploy'], flyctl: ['deploy'], vercel: ['deploy'],
  netlify: ['deploy'], firebase: ['deploy'], wrangler: ['deploy', 'publish'],
  serverless: ['deploy'], sls: ['deploy'], cdk: ['deploy'], pulumi: ['up'], gcloud: ['deploy'],
};
const FLAG_WATCH = { vercel: '--prod' };

// Split a command line into simple commands (arrays of words). Quotes are removed.
// Separators: ; & | newline ( ) and the start and end of $( ) and backticks.
function split(s) {
  const cmds = [];
  let words = [];
  let w = '';
  let inW = false;
  let mode = 'n'; // n = plain, d = double quotes, s = single quotes
  const stack = []; // frames to return to: { back, close }
  const flush = () => { if (inW) { words.push(w); w = ''; inW = false; } };
  const endCmd = () => { flush(); if (words.length) cmds.push(words); words = []; };
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (mode === 's') { if (c === "'") mode = 'n'; else { w += c; inW = true; } continue; }
    const top = stack[stack.length - 1];
    if (c === '\\') { i++; if (i < s.length && s[i] !== '\n') { w += s[i]; inW = true; } continue; }
    if (c === '$' && s[i + 1] === '(') { endCmd(); stack.push({ back: mode, close: ')' }); mode = 'n'; i++; continue; }
    if (c === '`') {
      endCmd();
      if (top && top.close === '`') { mode = stack.pop().back; } else { stack.push({ back: mode, close: '`' }); mode = 'n'; }
      continue;
    }
    if (mode === 'd') { if (c === '"') mode = 'n'; else { w += c; inW = true; } continue; }
    if (c === "'") { mode = 's'; inW = true; continue; }
    if (c === '"') { mode = 'd'; inW = true; continue; }
    if (c === '(') { endCmd(); stack.push({ back: 'n', close: ')' }); continue; }
    if (c === ')') { endCmd(); if (top && top.close === ')') mode = stack.pop().back; continue; }
    if (c === ';' || c === '&' || c === '|' || c === '\n') { endCmd(); continue; }
    if (c === '#' && !inW) { while (i < s.length && s[i] !== '\n') i++; endCmd(); continue; }
    if (c === ' ' || c === '\t' || c === '\r') { flush(); continue; }
    w += c; inW = true;
  }
  endCmd();
  return cmds;
}

function base(p) {
  return p.split(/[\\/]/).pop().toLowerCase().replace(/\.(exe|cmd|bat)$/, '');
}

// A destructive git command, or null. `sub` is the subcommand, `args` the words after it.
function destructiveGit(sub, args) {
  const has = (re) => args.some((a) => re.test(a));
  switch (sub) {
    case 'reset': return args.includes('--hard') ? 'git reset --hard' : null;
    case 'clean': return has(/^(--force|-[a-zA-Z]*f[a-zA-Z]*)$/) && !has(/^(--dry-run|-[a-zA-Z]*n[a-zA-Z]*)$/) ? 'git clean -f' : null;
    case 'checkout': return args.includes('.') || args.includes(':/') ? 'git checkout -- .' : null;
    case 'restore': return (args.includes('.') || args.includes(':/')) && !(args.includes('--staged') && !args.includes('--worktree')) ? 'git restore .' : null;
    case 'branch': return has(/^-[a-zA-Z]*D[a-zA-Z]*$/) || (has(/^(--delete|-d)$/) && has(/^(--force|-f)$/)) ? 'git branch -D' : null;
    case 'push': return has(/^(--force|--force-with-lease(=.*)?|--mirror|--delete|-f|\+.*)$/) ? 'git push --force' : 'git push';
    case 'rebase': return 'git rebase';
    case 'filter-branch': return 'git filter-branch';
    case 'filter-repo': return 'git filter-repo';
    default: return null;
  }
}

// The program text of an inline interpreter (python -c, node -e, perl -e ...) is not shell, so it
// is searched for a guarded command by pattern. A mention in a string asks too: asking is cheap.
const INLINE_PATTERNS = [
  [/\bgit\b[^\n]{0,80}?\b(push|commit|tag|rebase|filter-branch|filter-repo)\b/, (m) => 'git ' + m[1]],
  [/\bgit\b[^\n]{0,80}?\breset\b[^\n]{0,40}--hard\b/, () => 'git reset --hard'],
  [/\bgit\b[^\n]{0,80}?\bclean\b[^\n]{0,40}(--force|\s-[a-zA-Z]*f)/, () => 'git clean -f'],
  [/\bgit\b[^\n]{0,80}?\bbranch\b[^\n]{0,40}\s-[a-zA-Z]*D/, () => 'git branch -D'],
  [/\bgh\b[^\n]{0,20}?\b(pr\b[^\n]{0,8}merge|release\b[^\n]{0,8}create)\b/, (m) => 'gh ' + m[1].replace(/[^a-z]+/g, ' ')],
  ...Object.entries(WATCH).map(([prog, words]) => [
    new RegExp('\\b' + prog + '\\b[^\\n]{0,40}?\\b(' + words.join('|') + ')\\b'), (m) => prog + ' ' + m[1],
  ]),
];

function scanInline(text) {
  for (const [re, label] of INLINE_PATTERNS) {
    const m = re.exec(text);
    if (m) return label(m);
  }
  return null;
}

function classifyWords(words, depth) {
  let i = 0;
  for (;;) {
    const w = words[i];
    if (w === undefined) return null;
    if (ENV_RE.test(w) || KEYWORDS.has(w)) { i++; continue; }
    const opts = WRAPPERS[base(w)];
    if (!opts) break;
    const name = base(w);
    i++;
    while (i < words.length) {
      if (ENV_RE.test(words[i])) i++;
      else if (opts.includes(words[i])) i += 2;
      else if (words[i].startsWith('-')) i++;
      else break;
    }
    if (name === 'timeout' && /^[0-9]/.test(words[i] || '')) i++;
  }
  const prog = base(words[i]);
  const rest = words.slice(i + 1);
  if (SHELLS.has(prog)) {
    const j = rest.findIndex((x) => /^-[a-z]*c[a-z]*$/.test(x));
    if (j >= 0 && j + 1 < rest.length) return classify(rest[j + 1], depth + 1);
    return null;
  }
  if (prog === 'eval') return classify(rest.join(' '), depth + 1);
  for (const [re, flags] of INLINE) {
    if (re.test(prog) && rest.some((x) => flags.includes(x) || flags.some((f) => x.startsWith(f) && !x.startsWith('--')))) {
      const hit = scanInline(rest.join(' '));
      return hit ? `${hit} (inline ${prog} code)` : null;
    }
  }
  if (prog === 'git') {
    let k = 0;
    while (k < rest.length) {
      if (GIT_VALUE_OPTS.has(rest[k])) k += 2;
      else if (rest[k].startsWith('-')) k++;
      else break;
    }
    if (rest[k] === undefined) return null;
    const hit = destructiveGit(rest[k], rest.slice(k + 1));
    if (hit) return hit;
    return GIT_ASK.has(rest[k]) ? 'git ' + rest[k] : null;
  }
  const plain = rest.filter((x) => !x.startsWith('-'));
  if (prog === 'gh') {
    const key = plain.slice(0, 2).join(' ');
    return key === 'pr merge' || key === 'release create' ? 'gh ' + key : null;
  }
  const kw = WATCH[prog];
  if (kw) {
    const hit = plain.slice(0, 3).find((x) => kw.includes(x));
    if (hit) return prog + ' ' + hit;
  }
  if (FLAG_WATCH[prog] && rest.includes(FLAG_WATCH[prog])) return prog + ' ' + FLAG_WATCH[prog];
  return null;
}

// Returns a short label such as "git push", or null when the command is not one of the watched kinds.
function classify(command, depth = 0) {
  if (depth > 3 || typeof command !== 'string') return null;
  for (const words of split(command)) {
    const hit = classifyWords(words, depth);
    if (hit) return hit;
  }
  return null;
}

// Read all of stdin (at most 1 MB) and parse it as JSON. Throws on bad input.
function readInput() {
  const fs = require('fs');
  const chunks = [];
  const buf = Buffer.alloc(65536);
  let total = 0;
  for (;;) {
    let n = 0;
    try { n = fs.readSync(0, buf, 0, buf.length, null); } catch (e) { if (e.code === 'EOF') break; if (e.code === 'EAGAIN') continue; throw e; }
    if (n === 0) break;
    total += n;
    if (total > 1048576) throw new Error('input too large');
    chunks.push(Buffer.from(buf.subarray(0, n)));
  }
  const data = JSON.parse(Buffer.concat(chunks).toString('utf8'));
  if (data === null || typeof data !== 'object' || Array.isArray(data)) throw new Error('input is not an object');
  return data;
}

const ARTICLE0 = 'GABBE Article 0: no commit, push, tag, publish or deploy unless the human asked for it.';
const ARTICLE0_DESTRUCTIVE = 'GABBE Article 0, destructive actions: say what will be lost and get an explicit yes before deleting data or branches, force-pushing or rewriting history.';

// The question text for a label returned by classify.
function reasonFor(label) {
  const text = DESTRUCTIVE.has(label.split(' (')[0]) ? ARTICLE0_DESTRUCTIVE : ARTICLE0;
  return `${text} This command runs "${label}". Approve only if you asked for it.`;
}

module.exports = { classify, split, readInput, reasonFor, ARTICLE0 };
