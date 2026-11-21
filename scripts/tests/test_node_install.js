#!/usr/bin/env node
/* SPDX-License-Identifier: Apache-2.0 */
/*
 * Zero-dependency end-to-end test for the Node installer (bin/install.js).
 * Exercises non-interactive `init --yes` into a throwaway project that already
 * contains user files, and asserts the never-clobber invariant: a file the user
 * already had is kept or backed up, never lost, and every path is recorded.
 *
 * Run: node scripts/tests/test_node_install.js
 */
'use strict';

const assert = require('assert');
const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const KIT_ROOT = path.resolve(__dirname, '..', '..');
const INSTALL_JS = path.join(KIT_ROOT, 'bin', 'install.js');

function mkTmp() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'gabbe-node-test-'));
}

// Every child process gets a HOME inside a temp folder and no global or system git settings, so
// the result never depends on the machine's own configuration (for example core.hooksPath).
const TEST_HOME = mkTmp();
process.on('exit', () => fs.rmSync(TEST_HOME, { recursive: true, force: true }));
const CHILD_ENV = {
  ...process.env,
  HOME: TEST_HOME,
  USERPROFILE: TEST_HOME,
  GIT_CONFIG_GLOBAL: os.devNull,
  GIT_CONFIG_NOSYSTEM: '1',
};

function run(cwd, args) {
  return execFileSync('node', [INSTALL_JS, ...args], {
    cwd,
    env: CHILD_ENV,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  });
}

function write(proj, rel, text) {
  fs.writeFileSync(path.join(proj, rel), text);
}

function read(proj, rel) {
  return fs.readFileSync(path.join(proj, rel), 'utf8');
}

// Every file and link under `root`, with its content or link target.
function snapshot(root, dir = '') {
  const out = {};
  for (const entry of fs.readdirSync(path.join(root, dir), { withFileTypes: true })) {
    const rel = path.posix.join(dir, entry.name);
    if (entry.isSymbolicLink()) out[rel] = `link:${fs.readlinkSync(path.join(root, rel))}`;
    else if (entry.isDirectory()) Object.assign(out, snapshot(root, rel));
    else out[rel] = fs.readFileSync(path.join(root, rel), 'utf8');
  }
  return out;
}

// Tests that need symbolic links or file modes skip cleanly on Windows, where a link
// may need privileges and the installer falls back to copies.
function skipOnWindows() {
  if (process.platform !== 'win32') return false;
  console.log('    (skipped: needs symbolic links or file modes)');
  return true;
}

let failures = 0;
function test(name, fn) {
  const proj = mkTmp();
  try {
    fn(proj);
    console.log(`  ok - ${name}`);
  } catch (e) {
    failures += 1;
    console.error(`  FAIL - ${name}\n    ${e.message}`);
  } finally {
    fs.rmSync(proj, { recursive: true, force: true });
  }
}

// 1. Non-interactive init creates the kit without touching unrelated user code.
test('init --yes copies kit and preserves unrelated user file', (proj) => {
  fs.writeFileSync(path.join(proj, 'my-app.js'), 'console.log(1)\n');
  run(proj, ['init', '--yes', '--agents', 'claude']);
  assert.ok(fs.existsSync(path.join(proj, 'agents', 'AGENTS.md')), 'agents/AGENTS.md missing');
  assert.strictEqual(
    fs.readFileSync(path.join(proj, 'my-app.js'), 'utf8'),
    'console.log(1)\n',
    'unrelated user file changed'
  );
});

// 2. The project's own docs/ folder is not touched (1.1.3 copied the kit's
//    documents into it and replaced files of the same name).
test('the project docs/ folder is left alone', (proj) => {
  const docs = path.join(proj, 'docs');
  fs.mkdirSync(docs, { recursive: true });
  const userDoc = path.join(docs, 'INSTALL.md');
  fs.writeFileSync(userDoc, 'USER OWNED INSTALL DOC\n');

  run(proj, ['init', '--yes', '--agents', 'claude']);

  assert.deepStrictEqual(fs.readdirSync(docs), ['INSTALL.md'], 'files were added to docs/');
  assert.strictEqual(fs.readFileSync(userDoc, 'utf8'), 'USER OWNED INSTALL DOC\n');
});

// 3. A pre-existing preserved file (AGENTS.md) is kept verbatim without --force.
test('preserve-set AGENTS.md kept verbatim without --force', (proj) => {
  const agents = path.join(proj, 'agents');
  fs.mkdirSync(agents, { recursive: true });
  fs.writeFileSync(path.join(agents, 'AGENTS.md'), 'USER AGENTS\n');

  run(proj, ['init', '--yes', '--agents', 'claude']);

  assert.strictEqual(
    fs.readFileSync(path.join(agents, 'AGENTS.md'), 'utf8'),
    'USER AGENTS\n',
    'preserved AGENTS.md was overwritten'
  );
});

// 4. An unknown word is rejected with the usage and exit 1, and installs nothing.
test('unknown command exits 1 with usage and copies nothing', (proj) => {
  let err = null;
  try {
    run(proj, ['route']);
  } catch (e) {
    err = e;
  }
  assert.ok(err, 'unknown command did not fail');
  assert.strictEqual(err.status, 1, `exit status ${err.status}, expected 1`);
  assert.ok(/Unknown command: route/.test(err.stderr), 'no "Unknown command" message');
  assert.ok(/Usage:/.test(err.stderr), 'usage text not shown');
  assert.ok(!fs.existsSync(path.join(proj, 'agents')), 'kit was copied for an unknown command');
});

// 5. The help text documents --force.
test('--help lists --force', (proj) => {
  assert.ok(/--force/.test(run(proj, ['--help'])), '--force missing from --help');
});

// 6. An unknown option is an error (1.1.3 printed the help and exited 0).
test('unknown option exits 2 and copies nothing', (proj) => {
  let err = null;
  try {
    run(proj, ['init', '--bogus']);
  } catch (e) {
    err = e;
  }
  assert.ok(err, 'unknown option did not fail');
  assert.strictEqual(err.status, 2, `exit status ${err.status}, expected 2`);
  assert.ok(!fs.existsSync(path.join(proj, 'agents')), 'kit was copied for an unknown option');
});

// 7. A root AGENTS.md and a Copilot file the user already had are kept; each gets
//    a pointer to the kit and the original is saved first.
test('existing instruction files are kept and pointed at the kit', (proj) => {
  if (skipOnWindows()) return;
  fs.mkdirSync(path.join(proj, '.github'));
  write(proj, 'AGENTS.md', 'MY AGENTS FILE\n');
  write(proj, '.github/copilot-instructions.md', 'MY COPILOT RULES\n');

  run(proj, ['init', '--yes', '--agents', 'copilot']);

  for (const rel of ['AGENTS.md', '.github/copilot-instructions.md']) {
    const file = path.join(proj, rel);
    assert.ok(!fs.lstatSync(file).isSymbolicLink(), `${rel} was replaced by a link`);
    const text = fs.readFileSync(file, 'utf8');
    assert.ok(text.startsWith('MY '), `${rel} lost the user's text`);
    assert.ok(text.includes('`agents/AGENTS.md`'), `${rel} has no pointer to the kit`);
    assert.ok(fs.readFileSync(file + '.gabbe-bak', 'utf8').startsWith('MY '), `${rel} not backed up`);
  }
  // A second run adds nothing.
  const once = read(proj, 'AGENTS.md');
  run(proj, ['init', '--yes', '--agents', 'copilot']);
  assert.strictEqual(read(proj, 'AGENTS.md'), once, 'second run changed AGENTS.md again');
});

// 8. --force replaces the user's file with a link, and never overwrites a backup.
test('--force moves the original to a backup name that is not in use', (proj) => {
  write(proj, 'AGENTS.md', 'MY AGENTS FILE\n');
  write(proj, 'AGENTS.md.bak', 'AN OLDER BACKUP\n');

  run(proj, ['init', '--yes', '--force']);

  assert.ok(fs.lstatSync(path.join(proj, 'AGENTS.md')).isSymbolicLink(), 'not linked');
  assert.strictEqual(read(proj, 'AGENTS.md.bak'), 'AN OLDER BACKUP\n', 'backup overwritten');
  assert.strictEqual(read(proj, 'AGENTS.md.bak.1'), 'MY AGENTS FILE\n', 'original not kept');
});

// 9. A user's own skill and rule files survive; a file with the same name as a
//    kit skill is saved next to the kit's file.
test("the user's own skills and rules are never lost", (proj) => {
  fs.mkdirSync(path.join(proj, '.claude', 'skills', 'mine'), { recursive: true });
  fs.mkdirSync(path.join(proj, '.claude', 'skills', 'tdd-cycle'), { recursive: true });
  fs.mkdirSync(path.join(proj, '.cursor', 'rules'), { recursive: true });
  write(proj, '.claude/skills/mine/SKILL.md', 'MY OWN SKILL\n');
  write(proj, '.claude/skills/tdd-cycle/SKILL.md', 'MY TDD SKILL\n');
  write(proj, '.cursor/rules/tdd-cycle.mdc', 'MY TDD RULE\n');

  run(proj, ['init', '--yes', '--agents', 'claude,cursor']);

  assert.strictEqual(read(proj, '.claude/skills/mine/SKILL.md'), 'MY OWN SKILL\n');
  assert.strictEqual(read(proj, '.claude/skills/tdd-cycle/SKILL.md.gabbe-bak'), 'MY TDD SKILL\n');
  assert.strictEqual(read(proj, '.cursor/rules/tdd-cycle.mdc.gabbe-bak'), 'MY TDD RULE\n');
});

// 10. Two edits of a kit file between three installs give two backups.
test('every edited version of a kit file is kept', (proj) => {
  const skill = 'agents/skills/core/research.skill.md';
  run(proj, ['init', '--yes']);
  fs.appendFileSync(path.join(proj, skill), 'EDIT1\n');
  run(proj, ['init', '--yes']);
  fs.appendFileSync(path.join(proj, skill), 'EDIT2\n');
  run(proj, ['init', '--yes']);

  assert.ok(read(proj, skill + '.gabbe-bak').endsWith('EDIT1\n'), 'first edit lost');
  assert.ok(read(proj, skill + '.gabbe-bak.1').endsWith('EDIT2\n'), 'second edit lost');
  assert.ok(!read(proj, skill).includes('EDIT'), 'kit file not refreshed');
});

// 11. The install is recorded, so `gabbe uninstall` can reverse it.
test('writes an install record with every path, and the first prompt', (proj) => {
  write(proj, 'AGENTS.md', 'MY AGENTS FILE\n');
  const out = run(proj, ['init', '--yes', '--agents', 'claude']);

  const manifest = JSON.parse(read(proj, '.gabbe/manifest.json'));
  assert.strictEqual(manifest.schema_version, 1);
  assert.deepStrictEqual(manifest.agents, ['claude-code']);
  const byPath = new Map(manifest.entries.map((e) => [e.path, e]));
  assert.strictEqual(byPath.get('AGENTS.md').kind, 'block');
  assert.strictEqual(byPath.get('AGENTS.md').backup_of, 'AGENTS.md.gabbe-bak');
  assert.strictEqual(byPath.get('.claude/CLAUDE.md').kind, 'symlink');
  assert.strictEqual(byPath.get('.claude/skills/tdd-cycle/SKILL.md').agent, 'claude-code');
  assert.strictEqual(byPath.get('.agents/skills/tdd-cycle/SKILL.md').agent, 'shared');
  assert.strictEqual(byPath.get('agents/CONSTITUTION.md').hash.length, 64);
  assert.ok(!manifest.entries.some((e) => e.kind === 'tree'), 'a directory was recorded');
  assert.ok(manifest.entries.every((e) => !e.path.includes('\\')), 'backslash in a path');

  assert.ok(read(proj, 'BOOTSTRAP_MISSION.md').includes('spec-writer'), 'no first prompt');
  assert.ok(/Read BOOTSTRAP_MISSION\.md and follow it/.test(out), 'next step not printed');
  assert.ok(/\[PLACEHOLDER\] fields/.test(out), 'placeholders not mentioned');
});

// 12. A link of the user's is never replaced and never written through.
test("the user's links are kept and nothing is written through them", (proj) => {
  if (skipOnWindows()) return;
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'gabbe-node-outside-'));
  try {
    write(proj, 'CLAUDE.md', 'MY RULES\n');
    fs.symlinkSync('CLAUDE.md', path.join(proj, 'AGENTS.md'));
    fs.mkdirSync(path.join(proj, '.claude'));
    fs.symlinkSync(outside, path.join(proj, '.claude', 'skills'));
    fs.writeFileSync(path.join(outside, 'opencode.json'), '{"mine": true}\n');
    fs.symlinkSync(path.join(outside, 'opencode.json'), path.join(proj, 'opencode.json'));

    const out = run(proj, ['init', '--yes', '--agents', 'claude,opencode']);

    assert.strictEqual(fs.readlinkSync(path.join(proj, 'AGENTS.md')), 'CLAUDE.md', 'link replaced');
    assert.strictEqual(read(proj, 'CLAUDE.md'), 'MY RULES\n');
    assert.deepStrictEqual(fs.readdirSync(outside), ['opencode.json'], 'wrote through a link');
    assert.strictEqual(fs.readFileSync(path.join(outside, 'opencode.json'), 'utf8'), '{"mine": true}\n');
    assert.ok(/is a link of yours/.test(out), 'the kept link is not reported');
    assert.ok(/path\(s\) alone because they are links/.test(out), 'skipped paths not reported');
  } finally {
    fs.rmSync(outside, { recursive: true, force: true });
  }
});

// 13. A read-only instruction file is left alone and the install completes.
test('a read-only instruction file does not stop the install', (proj) => {
  if (skipOnWindows()) return;
  write(proj, 'AGENTS.md', 'READ ONLY RULES\n');
  fs.chmodSync(path.join(proj, 'AGENTS.md'), 0o444);
  try {
    fs.accessSync(path.join(proj, 'AGENTS.md'), fs.constants.W_OK);
    console.log('    (skipped: read-only files are writable for this user)');
    return;
  } catch (e) {
    /* not writable: the case under test */
  }

  const out = run(proj, ['init', '--yes', '--agents', 'claude']);

  assert.strictEqual(read(proj, 'AGENTS.md'), 'READ ONLY RULES\n');
  assert.ok(/is read-only: left as is/.test(out), 'the skipped file is not reported');
  assert.ok(fs.existsSync(path.join(proj, '.gabbe', 'manifest.json')), 'no install record');
  assert.ok(!fs.existsSync(path.join(proj, 'AGENTS.md.gabbe-bak')), 'a backup was left behind');
});

// 14. The pointer block never changes the bytes of the user's text.
test('a non-UTF-8 file with Windows line ends keeps its bytes', (proj) => {
  const original = Buffer.from('caf\xe9 latin-1\r\nsecond line\r\n', 'latin1');
  fs.writeFileSync(path.join(proj, 'AGENTS.md'), original);

  run(proj, ['init', '--yes']);

  const blocked = fs.readFileSync(path.join(proj, 'AGENTS.md'));
  assert.ok(blocked.subarray(0, original.length).equals(original), 'the user\'s bytes changed');
  assert.ok(blocked.includes('GABBE-KIT:BEGIN'), 'no pointer block');
  assert.ok(!blocked.subarray(original.length).toString('latin1').replace(/\r\n/g, '').includes('\n'),
    'the block does not use the file\'s line end');
});

// 15. `agents` that is a regular file: a clear error, nothing written.
test('agents as a file is refused with a message', (proj) => {
  write(proj, 'agents', 'not a folder\n');
  let err = null;
  try {
    run(proj, ['init', '--yes']);
  } catch (e) {
    err = e;
  }
  assert.ok(err && err.status === 1, 'did not exit 1');
  assert.ok(/is not a folder/.test(err.stderr), 'no clear message');
  assert.deepStrictEqual(fs.readdirSync(proj), ['agents'], 'something was written');
});

// 16. --force after an earlier run: uninstall gives the original back, no block.
//     Needs the Python CLI; skipped when python3 is not available.
test('--force after a pointer block still uninstalls to the original', (proj) => {
  if (skipOnWindows()) return;
  const { spawnSync } = require('child_process');
  if (spawnSync('python3', ['-c', 'import yaml, jsonschema, requests']).status !== 0) {
    console.log('    (skipped: python3 with the CLI dependencies is not available)');
    return;
  }
  write(proj, 'AGENTS.md', 'MY AGENTS FILE\n');
  const before = snapshot(proj);

  run(proj, ['init', '--yes', '--agents', 'claude']);
  run(proj, ['init', '--yes', '--agents', 'claude', '--force']);
  assert.ok(fs.lstatSync(path.join(proj, 'AGENTS.md')).isSymbolicLink(), 'not linked by --force');
  const res = spawnSync('python3', ['-m', 'gabbe.main', 'uninstall'], {
    cwd: proj,
    encoding: 'utf8',
    env: { ...process.env, PYTHONPATH: KIT_ROOT },
  });

  assert.strictEqual(res.status, 0, `gabbe uninstall failed: ${res.stderr}`);
  assert.deepStrictEqual(snapshot(proj), before, 'project differs from its state before install');
});

// 17. Install then `gabbe uninstall --purge` gives the project back unchanged.
//     Needs the Python CLI; skipped when python3 is not available.
test('install then gabbe uninstall --purge restores the project', (proj) => {
  const { spawnSync } = require('child_process');
  if (spawnSync('python3', ['-c', 'import yaml, jsonschema, requests']).status !== 0) {
    console.log('    (skipped: python3 with the CLI dependencies is not available)');
    return;
  }
  fs.mkdirSync(path.join(proj, '.claude', 'skills', 'mine'), { recursive: true });
  write(proj, 'AGENTS.md', 'MY AGENTS FILE\n');
  write(proj, '.claude/skills/mine/SKILL.md', 'MY OWN SKILL\n');
  write(proj, 'app.js', 'console.log(1)\n');
  const before = snapshot(proj);

  run(proj, ['init', '--yes', '--agents', 'claude,cursor']);
  const res = spawnSync('python3', ['-m', 'gabbe.main', 'uninstall', '--purge'], {
    cwd: proj,
    encoding: 'utf8',
    env: { ...process.env, PYTHONPATH: KIT_ROOT },
  });

  assert.strictEqual(res.status, 0, `gabbe uninstall failed: ${res.stderr}`);
  assert.deepStrictEqual(snapshot(proj), before, 'project differs from its state before install');
});

// ---------------------------------------------------------------------------
// uninstall, update, doctor (1.2.0)
// ---------------------------------------------------------------------------

// Run and return { status, stdout, stderr } without throwing on a non-zero exit.
function tryRun(cwd, args) {
  const { spawnSync } = require('child_process');
  const res = spawnSync('node', [INSTALL_JS, ...args], { cwd, env: CHILD_ENV, encoding: 'utf8' });
  return { status: res.status, stdout: res.stdout, stderr: res.stderr };
}

// 18. --help lists the three commands.
test('--help lists uninstall, update and doctor', (proj) => {
  const out = run(proj, ['--help']);
  for (const word of ['uninstall', 'update', 'doctor', '--dry-run']) {
    assert.ok(out.includes(word), `${word} missing from --help`);
  }
});

// 19. Install then uninstall gives the project back unchanged (no Python needed).
test('uninstall restores the project after an install', (proj) => {
  if (skipOnWindows()) return;
  fs.mkdirSync(path.join(proj, '.claude', 'skills', 'mine'), { recursive: true });
  write(proj, 'AGENTS.md', 'MY AGENTS FILE\n');
  write(proj, '.claude/skills/mine/SKILL.md', 'MY OWN SKILL\n');
  write(proj, 'app.js', 'console.log(1)\n');
  const before = snapshot(proj);

  run(proj, ['init', '--yes', '--agents', 'claude,cursor,copilot']);
  const res = tryRun(proj, ['uninstall']);

  assert.strictEqual(res.status, 0, res.stderr);
  assert.ok(/^Removed \d+ path\(s\) from /m.test(res.stdout), `count line: ${res.stdout}`);
  assert.deepStrictEqual(snapshot(proj), before, 'project differs from its state before install');
  assert.ok(!fs.existsSync(path.join(proj, '.gabbe')), '.gabbe left behind');
});

// 20. --dry-run prints every path and changes nothing.
test('uninstall --dry-run lists the paths and changes nothing', (proj) => {
  run(proj, ['init', '--yes', '--agents', 'claude']);
  const before = snapshot(proj);
  const res = tryRun(proj, ['uninstall', '--dry-run']);

  assert.strictEqual(res.status, 0, res.stderr);
  const lines = res.stdout.split('\n');
  const count = Number(/^Would remove (\d+) path\(s\) from /m.exec(res.stdout)[1]);
  assert.strictEqual(lines.filter((l) => l.startsWith('  ')).length, count, 'path lines != count');
  assert.ok(lines.includes('  agents/AGENTS.md'), 'agents/AGENTS.md not listed');
  assert.deepStrictEqual(snapshot(proj), before, 'a dry run changed the project');
});

// 21. No record, or a damaged one: exit 1, an explanation, nothing removed.
test('uninstall refuses a missing or damaged record with exit 1', (proj) => {
  write(proj, 'app.js', 'x\n');
  let res = tryRun(proj, ['uninstall']);
  assert.strictEqual(res.status, 1);
  assert.ok(/No install record/.test(res.stderr), res.stderr);

  run(proj, ['init', '--yes']);
  write(proj, '.gabbe/manifest.json', '{ not json');
  const before = snapshot(proj);
  res = tryRun(proj, ['uninstall']);
  assert.strictEqual(res.status, 1);
  assert.ok(/install record is damaged/.test(res.stderr), res.stderr);
  assert.deepStrictEqual(snapshot(proj), before, 'a damaged record was acted on');
});

// 22. A recorded path that leaves the project is skipped; an edited file is kept as a backup.
test('uninstall skips an escaping path and keeps the files the user edited', (proj) => {
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'gabbe-node-outside-'));
  try {
    run(proj, ['init', '--yes']);
    fs.writeFileSync(path.join(outside, 'precious.txt'), 'keep\n');
    const file = path.join(proj, '.gabbe', 'manifest.json');
    const manifest = JSON.parse(fs.readFileSync(file, 'utf8'));
    manifest.entries.push({ path: path.relative(proj, path.join(outside, 'precious.txt')), kind: 'copy', agent: 'shared', hash: '', backup_of: null });
    fs.writeFileSync(file, JSON.stringify(manifest));
    const skill = '.agents/skills/tdd-cycle/SKILL.md';
    write(proj, skill, read(proj, skill) + 'MY EDIT\n');

    const res = tryRun(proj, ['uninstall']);

    assert.strictEqual(res.status, 0, res.stderr);
    assert.strictEqual(fs.readFileSync(path.join(outside, 'precious.txt'), 'utf8'), 'keep\n');
    assert.ok(/preserved your edits to 1 modified file/.test(res.stderr), res.stderr);
    assert.ok(read(proj, skill + '.gabbe-bak').includes('MY EDIT'), 'edit not kept');
  } finally {
    fs.rmSync(outside, { recursive: true, force: true });
  }
});

// 23. A recorded file the user turned into a folder is left alone.
test('uninstall leaves a path that is no longer what was recorded', (proj) => {
  run(proj, ['init', '--yes']);
  const target = path.join(proj, 'agents', 'guides', 'ai', 'ai-agentic.md');
  fs.rmSync(target);
  fs.mkdirSync(target);
  write(proj, 'agents/guides/ai/ai-agentic.md/mine.txt', 'mine\n');

  const res = tryRun(proj, ['uninstall']);

  assert.strictEqual(res.status, 0, res.stderr);
  assert.strictEqual(read(proj, 'agents/guides/ai/ai-agentic.md/mine.txt'), 'mine\n');
});

// 24. --agents removes one agent's wiring and keeps the other's.
test('uninstall --agents cursor keeps the other agents', (proj) => {
  if (skipOnWindows()) return;
  run(proj, ['init', '--yes', '--agents', 'claude,cursor']);
  const res = tryRun(proj, ['uninstall', '--agents', 'cursor']);

  assert.strictEqual(res.status, 0, res.stderr);
  assert.ok(!fs.existsSync(path.join(proj, '.cursorrules')), '.cursorrules left');
  assert.ok(!fs.existsSync(path.join(proj, '.cursor')), '.cursor left');
  assert.ok(fs.existsSync(path.join(proj, '.claude', 'CLAUDE.md')), 'claude link removed');
  assert.ok(fs.existsSync(path.join(proj, '.claude', 'skills', 'tdd-cycle', 'SKILL.md')));
  const manifest = JSON.parse(read(proj, '.gabbe/manifest.json'));
  assert.deepStrictEqual(manifest.agents, ['claude-code']);
});

// 25. doctor: consistent after an install, not after a file is lost.
test('doctor exits 0 on a consistent install and 1 when a recorded path is missing', (proj) => {
  assert.strictEqual(tryRun(proj, ['doctor']).status, 1, 'doctor passed with no kit');
  run(proj, ['init', '--yes', '--agents', 'claude']);
  let res = tryRun(proj, ['doctor']);
  assert.strictEqual(res.status, 0, res.stdout);
  assert.ok(/agents wired: claude-code/.test(res.stdout), res.stdout);
  assert.ok(/\[PLACEHOLDER\] field/.test(res.stdout), 'placeholders not reported');

  fs.rmSync(path.join(proj, 'agents', 'CONSTITUTION.md'));
  const before = snapshot(proj);
  res = tryRun(proj, ['doctor']);
  assert.strictEqual(res.status, 1);
  assert.ok(/1 missing/.test(res.stdout), res.stdout);
  assert.deepStrictEqual(snapshot(proj), before, 'doctor wrote something');
});

// 26. update refreshes the kit, keeps the user's edit as a backup, and wires no new agent.
test('update refreshes the kit with the recorded agents only', (proj) => {
  if (skipOnWindows()) return;
  assert.strictEqual(tryRun(proj, ['update']).status, 1, 'update ran without a record');
  run(proj, ['init', '--yes', '--agents', 'claude']);
  const guide = 'agents/guides/ai/ai-agentic.md';
  const original = read(proj, guide);
  write(proj, guide, original + 'MY EDIT\n');
  fs.rmSync(path.join(proj, 'agents', 'guides', 'ai', 'agent-only-swarms.md'));

  const res = tryRun(proj, ['update', '--agents', 'cursor']);

  assert.strictEqual(res.status, 0, res.stderr);
  assert.strictEqual(read(proj, guide), original, 'kit file not refreshed');
  assert.ok(read(proj, guide + '.gabbe-bak').includes('MY EDIT'), 'edit not kept');
  assert.ok(fs.existsSync(path.join(proj, 'agents', 'guides', 'ai', 'agent-only-swarms.md')));
  assert.ok(!fs.existsSync(path.join(proj, '.cursorrules')), 'update wired an agent');
  assert.ok(fs.existsSync(path.join(proj, '.claude', 'skills')), 'recorded agent lost');
});

// 27. Skill names are the folder slug (the agent-skills convention).
test('emitted skills carry a lowercase-hyphen name equal to the folder', (proj) => {
  run(proj, ['init', '--yes']);
  const root = path.join(proj, '.agents', 'skills');
  for (const slug of fs.readdirSync(root)) {
    const text = fs.readFileSync(path.join(root, slug, 'SKILL.md'), 'utf8');
    const name = /^name:\s*"?([^"\r\n]*)"?\s*$/m.exec(text);
    assert.ok(name && name[1] === slug, `${slug}: name is ${name && name[1]}`);
  }
});

// 28. A skill renamed between kit versions: the old generated copy is removed, safely.
function sha256Of(text) {
  return require('crypto').createHash('sha256').update(text).digest('hex');
}

// Simulate a 1.1.4 install: a generated file on disk plus its record entry.
function addOldGenerated(proj, rel, text, recordedText) {
  const file = path.join(proj, ...rel.split('/'));
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, text);
  const manifestFile = path.join(proj, '.gabbe', 'manifest.json');
  const manifest = JSON.parse(fs.readFileSync(manifestFile, 'utf8'));
  manifest.entries.push({
    path: rel,
    kind: 'copy',
    agent: 'claude-code',
    backup_of: null,
    hash: sha256Of(recordedText === undefined ? text : recordedText),
  });
  fs.writeFileSync(manifestFile, JSON.stringify(manifest, null, 2) + '\n');
}

function recordedPaths(proj) {
  return JSON.parse(read(proj, '.gabbe/manifest.json')).entries.map((e) => e.path);
}

const OLD_SKILL = '---\nname: old-name\ngabbe-schema-version: 1\n---\nold body\n';

test('a renamed skill leaves no stale generated copy, and the user files stay', (proj) => {
  run(proj, ['init', '--yes', '--agents', 'claude']);
  addOldGenerated(proj, '.claude/skills/old-name/SKILL.md', OLD_SKILL);
  addOldGenerated(proj, '.claude/skills/edited-name/SKILL.md', OLD_SKILL + 'MY EDIT\n', OLD_SKILL);
  fs.mkdirSync(path.join(proj, '.claude', 'skills', 'mine'), { recursive: true });
  write(proj, '.claude/skills/mine/SKILL.md', 'MY OWN SKILL\n');

  const out = run(proj, ['init', '--yes', '--agents', 'claude']);

  assert.ok(!fs.existsSync(path.join(proj, '.claude', 'skills', 'old-name')), 'stale folder kept');
  assert.ok(!recordedPaths(proj).includes('.claude/skills/old-name/SKILL.md'), 'stale entry kept');
  assert.ok(out.includes('Removed 1 generated file(s)'), out);
  assert.ok(read(proj, '.claude/skills/edited-name/SKILL.md').includes('MY EDIT'), 'edited copy removed');
  assert.ok(recordedPaths(proj).includes('.claude/skills/edited-name/SKILL.md'));
  assert.ok(out.includes('Kept 1 old generated file(s) you changed: .claude/skills/edited-name/SKILL.md'), out);
  assert.strictEqual(read(proj, '.claude/skills/mine/SKILL.md'), 'MY OWN SKILL\n');
});

test('a stale file under a folder this run did not emit into is not touched', (proj) => {
  run(proj, ['init', '--yes', '--agents', 'claude,windsurf']);
  addOldGenerated(proj, '.windsurf/skills/old-name/SKILL.md', OLD_SKILL);

  run(proj, ['init', '--yes', '--agents', 'claude']);

  assert.ok(fs.existsSync(path.join(proj, '.windsurf', 'skills', 'old-name', 'SKILL.md')));
  assert.ok(recordedPaths(proj).includes('.windsurf/skills/old-name/SKILL.md'));
});

test('a stale file with no marker, or behind a link, is kept', (proj) => {
  if (skipOnWindows()) return;
  run(proj, ['init', '--yes', '--agents', 'claude']);
  addOldGenerated(proj, '.claude/skills/no-marker/SKILL.md', 'plain text\n');
  addOldGenerated(proj, '.claude/skills/linked/SKILL.md', OLD_SKILL);
  fs.rmSync(path.join(proj, '.claude', 'skills', 'linked', 'SKILL.md'));
  fs.symlinkSync(path.join(proj, 'app-target.md'), path.join(proj, '.claude', 'skills', 'linked', 'SKILL.md'));

  run(proj, ['init', '--yes', '--agents', 'claude']);

  assert.ok(fs.existsSync(path.join(proj, '.claude', 'skills', 'no-marker', 'SKILL.md')));
  assert.ok(fs.lstatSync(path.join(proj, '.claude', 'skills', 'linked', 'SKILL.md')).isSymbolicLink());
});

// 29. After an update, the record and the generated files on disk agree.
test('update leaves the recorded generated skills equal to the generated files on disk', (proj) => {
  run(proj, ['init', '--yes', '--agents', 'claude,cursor']);
  addOldGenerated(proj, '.agents/skills/agent-interoperability/SKILL.md', OLD_SKILL);
  addOldGenerated(proj, '.cursor/rules/agent-interoperability.mdc', OLD_SKILL);

  const res = tryRun(proj, ['update']);
  assert.strictEqual(res.status, 0, res.stderr);

  const roots = ['.agents/skills', '.claude/skills', '.cursor/rules'];
  const onDisk = new Set();
  for (const root of roots) {
    const dir = path.join(proj, ...root.split('/'));
    const walkDir = (d) =>
      fs.readdirSync(d, { withFileTypes: true }).forEach((e) => {
        const f = path.join(d, e.name);
        if (e.isDirectory()) return walkDir(f);
        if (fs.readFileSync(f, 'utf8').includes('gabbe-schema-version:')) {
          onDisk.add(path.relative(proj, f).split(path.sep).join('/'));
        }
      });
    walkDir(dir);
  }
  const inRecord = new Set(
    recordedPaths(proj).filter((p) => roots.some((r) => p.startsWith(r + '/')) && /(SKILL\.md|\.mdc)$/.test(p))
  );
  assert.ok(onDisk.size > 0);
  assert.deepStrictEqual([...inRecord].sort(), [...onDisk].sort());
});

// 30. --hooks: optional hooks are merged, never replace the user's, and uninstall reverses them.
function gitInit(proj) {
  execFileSync('git', ['init', '-q'], { cwd: proj, env: CHILD_ENV });
}
const USER_SETTINGS =
  '{\n  "model": "x",\n  "hooks": {"PreToolUse": [{"matcher":"Bash","hooks":[{"type":"command","command":"mine.sh"}]}]}\n}\n';
const USER_GIT_HOOK = '#!/bin/sh\necho mine\n';

function hookProject(proj) {
  gitInit(proj);
  fs.mkdirSync(path.join(proj, '.claude'));
  write(proj, '.claude/settings.json', USER_SETTINGS);
  write(proj, '.git/hooks/pre-commit', USER_GIT_HOOK);
  fs.chmodSync(path.join(proj, '.git', 'hooks', 'pre-commit'), 0o755);
}

test('init --hooks adds the hooks once, keeps the user hook and keys, and uninstall restores the bytes', (proj) => {
  if (skipOnWindows()) return;
  hookProject(proj);
  const before = snapshot(proj);
  const out = run(proj, ['init', '--yes', '--agents', 'claude,cursor', '--hooks']);
  assert.ok(out.includes('not GABBE'), 'must say the user git hook was not replaced');
  const doc = JSON.parse(read(proj, '.claude/settings.json'));
  assert.strictEqual(doc.model, 'x');
  assert.strictEqual(doc.hooks.PreToolUse[0].hooks[0].command, 'mine.sh');
  assert.strictEqual(doc.hooks.PreToolUse.length, 3);
  assert.strictEqual(JSON.parse(read(proj, '.cursor/hooks.json')).version, 1);
  assert.strictEqual(read(proj, '.git/hooks/pre-commit'), USER_GIT_HOOK);
  assert.ok(read(proj, '.git/hooks/pre-push').includes('GABBE-HOOK'));
  assert.ok(fs.existsSync(path.join(proj, '.claude', 'settings.json.gabbe-bak')));
  const entries = JSON.parse(read(proj, '.gabbe/manifest.json')).entries;
  const merge = entries.find((e) => e.path === '.claude/settings.json');
  assert.strictEqual(merge.kind, 'hook-merge');
  assert.strictEqual(merge.backup_of, '.claude/settings.json.gabbe-bak');
  assert.strictEqual(merge.created, false);
  assert.strictEqual(entries.find((e) => e.path === '.cursor/hooks.json').created, true);
  assert.strictEqual(entries.find((e) => e.path === '.git/hooks/pre-push').kind, 'copy');
  assert.ok(!entries.some((e) => e.path === '.git/hooks/pre-commit'), 'the user git hook is not recorded');
  assert.ok(out.includes('hooks.md'), 'the guide is named');

  // A second run adds nothing: same settings bytes, no second backup.
  const settingsOnce = read(proj, '.claude/settings.json');
  run(proj, ['init', '--yes', '--agents', 'claude,cursor', '--hooks']);
  assert.strictEqual(read(proj, '.claude/settings.json'), settingsOnce);
  assert.ok(!fs.existsSync(path.join(proj, '.claude', 'settings.json.gabbe-bak.1')));

  // update keeps them and adds nothing by itself.
  run(proj, ['update']);
  assert.strictEqual(read(proj, '.claude/settings.json'), settingsOnce);
  assert.ok(fs.existsSync(path.join(proj, '.git', 'hooks', 'pre-push')));

  const dry = run(proj, ['uninstall', '--dry-run']);
  assert.ok(
    dry.includes('  .claude/settings.json\n') && dry.includes('  .git/hooks/pre-push\n'),
    `dry-run list lacks the hook paths: ${dry.split('\n').filter((l) => /settings|hooks\/pre/.test(l)).join(' | ')} / ${dry.slice(-200)}`
  );
  run(proj, ['uninstall']);
  assert.strictEqual(read(proj, '.claude/settings.json'), USER_SETTINGS, 'exact original bytes');
  assert.strictEqual(read(proj, '.git/hooks/pre-commit'), USER_GIT_HOOK);
  assert.ok(!fs.existsSync(path.join(proj, '.git', 'hooks', 'pre-push')));
  assert.ok(!fs.existsSync(path.join(proj, '.cursor')), 'the file the installer created is gone');
  const after = snapshot(proj);
  for (const k of Object.keys(before)) {
    if (!k.startsWith('.git/') || k.startsWith('.git/hooks/')) assert.strictEqual(after[k], before[k], k);
  }
});

test('without --hooks no hook file is written', (proj) => {
  if (skipOnWindows()) return;
  gitInit(proj);
  run(proj, ['init', '--yes', '--agents', 'claude,cursor']);
  assert.ok(!fs.existsSync(path.join(proj, '.claude', 'settings.json')));
  assert.ok(!fs.existsSync(path.join(proj, '.cursor', 'hooks.json')));
  assert.ok(!fs.existsSync(path.join(proj, '.git', 'hooks', 'pre-push')));
  assert.ok(!fs.existsSync(path.join(proj, '.git', 'hooks', 'pre-commit')));
  // update --hooks does not add them either.
  const out = run(proj, ['update', '--hooks']);
  assert.ok(out.includes('--hooks is ignored'));
  assert.ok(!fs.existsSync(path.join(proj, '.claude', 'settings.json')));
  assert.ok(!fs.existsSync(path.join(proj, '.git', 'hooks', 'pre-push')));
});

test('--hooks outside a git repository skips the git hooks with one line', (proj) => {
  const out = run(proj, ['init', '--yes', '--agents', 'claude', '--hooks']);
  assert.ok(out.includes('not a git repository'));
  assert.ok(fs.existsSync(path.join(proj, '.claude', 'settings.json')));
  run(proj, ['uninstall']);
  assert.ok(!fs.existsSync(path.join(proj, '.claude')), 'a settings file the installer created is removed');
});

test('--hooks leaves a settings file that is not plain JSON untouched and prints what to add', (proj) => {
  fs.mkdirSync(path.join(proj, '.claude'));
  const text = '{ // my comment\n  "model": "x"\n}\n';
  write(proj, '.claude/settings.json', text);
  const out = run(proj, ['init', '--yes', '--agents', 'claude', '--hooks']);
  assert.strictEqual(read(proj, '.claude/settings.json'), text);
  assert.ok(out.includes('Add this by hand') && out.includes('guard-bash'));
  assert.ok(!fs.existsSync(path.join(proj, '.claude', 'settings.json.gabbe-bak')));
  const entries = JSON.parse(read(proj, '.gabbe/manifest.json')).entries;
  assert.ok(!entries.some((e) => e.path === '.claude/settings.json'));
});

test('--hooks writes nothing through a .claude that is a link', (proj) => {
  if (skipOnWindows()) return;
  const elsewhere = path.join(proj, 'elsewhere');
  fs.mkdirSync(elsewhere);
  fs.symlinkSync(elsewhere, path.join(proj, '.claude'));
  const out = run(proj, ['init', '--yes', '--agents', 'claude', '--hooks']);
  assert.deepStrictEqual(fs.readdirSync(elsewhere), []);
  assert.ok(out.includes('link of yours'));
  assert.ok(fs.lstatSync(path.join(proj, '.claude')).isSymbolicLink());
});

test('--hooks stops for a git hooks folder set by core.hooksPath and for a hook of the user', (proj) => {
  gitInit(proj);
  execFileSync('git', ['config', 'core.hooksPath', '.githooks'], { cwd: proj, env: CHILD_ENV });
  const out = run(proj, ['init', '--yes', '--hooks']);
  assert.ok(out.includes('core.hooksPath is set'));
  assert.ok(!fs.existsSync(path.join(proj, '.git', 'hooks', 'pre-push')));
});

test('--help lists --hooks', (proj) => {
  assert.ok(run(proj, ['--help']).includes('--hooks'));
});


// ---------------------------------------------------------------------------
// A tampered install record (.gabbe/manifest.json) and links at the record (1.2.0)
// ---------------------------------------------------------------------------

function editRecord(proj, change) {
  const file = path.join(proj, '.gabbe', 'manifest.json');
  const record = JSON.parse(fs.readFileSync(file, 'utf8'));
  change(record);
  fs.writeFileSync(file, JSON.stringify(record, null, 2) + '\n');
}

const SKILL = '.agents/skills/tdd-cycle/SKILL.md';

test('a hostile record entry cannot make init or update delete a file in another project', (proj) => {
  const victim = path.join(proj, 'victimproj');
  const hostile = path.join(proj, 'hostile');
  fs.mkdirSync(victim);
  fs.mkdirSync(hostile);
  run(victim, ['init', '--yes']);
  run(hostile, ['init', '--yes']);
  const victimFile = path.join(victim, ...SKILL.split('/'));
  const published = sha256Of(fs.readFileSync(victimFile, 'utf8'));
  const before = fs.readFileSync(victimFile, 'utf8');
  for (const command of ['init', 'update']) {
    editRecord(hostile, (r) =>
      r.entries.push({
        path: '.agents/skills/../../../victimproj/' + SKILL,
        kind: 'copy',
        agent: 'claude-code',
        backup_of: null,
        hash: published,
      })
    );
    const res = tryRun(hostile, [command, ...(command === 'init' ? ['--yes'] : [])]);
    assert.strictEqual(res.status, 0, res.stderr);
    assert.strictEqual(fs.readFileSync(victimFile, 'utf8'), before, `${command} removed the other project's file`);
    assert.ok(res.stderr.includes('victimproj'), `${command}: the refused entry is not named: ${res.stderr}`);
    assert.ok(!recordedPaths(hostile).some((p) => p.includes('..')), 'the hostile entry stays in the record');
  }
});

// Each entry would reach the sentinel files under `outside` if the path were followed.
function hostileEntries(outside) {
  const hash = sha256Of('keep\n');
  const copy = (p, extra) => ({ path: p, kind: 'copy', agent: 'shared', hash, backup_of: null, ...extra });
  return [
    copy('..'),
    copy('x/../..'),
    copy('.'),
    copy(''),
    copy(path.join(outside, 'abs.txt')),
    copy('planted/linked.txt'),
    copy('../' + path.basename(outside) + '/up.txt'),
    copy('agents/guides/ai/ai-agentic.md', { backup_of: '../' + path.basename(outside) + '/orig.txt' }),
    copy('agents/guides/ai/agent-only-swarms.md', { backup_of: path.join(outside, 'abs-orig.txt') }),
  ];
}

test('uninstall and its dry run leave everything outside the target byte for byte', (proj) => {
  if (skipOnWindows()) return;
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), 'gabbe-node-outside-'));
  try {
    const target = path.join(parent, 'target');
    const outside = path.join(parent, 'outside');
    fs.mkdirSync(target);
    fs.mkdirSync(outside);
    for (const name of ['abs.txt', 'up.txt', 'linked.txt', 'orig.txt', 'abs-orig.txt']) {
      fs.writeFileSync(path.join(outside, name), 'keep\n');
    }
    fs.symlinkSync(outside, path.join(target, 'planted'));
    run(target, ['init', '--yes']);
    fs.rmSync(path.join(target, 'agents', 'guides', 'ai', 'ai-agentic.md'));
    fs.rmSync(path.join(target, 'agents', 'guides', 'ai', 'agent-only-swarms.md'));
    editRecord(target, (r) => r.entries.push(...hostileEntries(outside)));
    const outsideBefore = snapshot(parent, 'outside');

    const dry = tryRun(target, ['uninstall', '--dry-run']);
    assert.strictEqual(dry.status, 0, dry.stderr);
    const listed = dry.stdout.split('\n').filter((l) => l.startsWith('  '));
    for (const word of ['abs.txt', 'up.txt', 'linked.txt', 'outside']) {
      assert.ok(!listed.some((l) => l.includes(word)), `dry run lists ${word}`);
    }
    assert.deepStrictEqual(snapshot(parent, 'outside'), outsideBefore, 'the dry run changed the outside folder');

    const res = tryRun(target, ['uninstall']);
    assert.strictEqual(res.status, 0, res.stderr);
    assert.deepStrictEqual(snapshot(parent, 'outside'), outsideBefore, 'uninstall changed the outside folder');
    assert.ok(/skipped .*planted\/linked\.txt/.test(res.stderr), `the refused entry is not named: ${res.stderr}`);
    assert.ok(/skipped backup_of/.test(res.stderr), `the refused backup_of is not named: ${res.stderr}`);
    assert.ok(!fs.existsSync(path.join(target, 'agents', 'guides', 'ai', 'ai-agentic.md')), 'an outside file was moved in');
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test('a link at .gabbe/manifest.json is never written through: init, update and uninstall refuse', (proj) => {
  if (skipOnWindows()) return;
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'gabbe-node-outside-'));
  try {
    const victim = path.join(outside, 'victim.txt'); // does not exist
    const link = path.join(proj, '.gabbe', 'manifest.json');
    fs.mkdirSync(path.join(proj, '.gabbe'));
    fs.symlinkSync(victim, link);
    let res = tryRun(proj, ['init', '--yes']);
    assert.notStrictEqual(res.status, 0, 'init went on');
    assert.ok(res.stderr.includes(link), `the path is not named: ${res.stderr}`);
    assert.deepStrictEqual(fs.readdirSync(proj).sort(), ['.gabbe'], 'init wrote other files before it stopped');
    assert.ok(!fs.existsSync(victim), 'init wrote through the link');

    fs.rmSync(path.join(proj, '.gabbe'), { recursive: true });
    run(proj, ['init', '--yes']);
    fs.rmSync(link);
    fs.symlinkSync(victim, link);
    const before = snapshot(proj);
    for (const command of ['update', 'uninstall']) {
      res = tryRun(proj, [command]);
      assert.strictEqual(res.status, 1, `${command}: ${res.stdout}`);
      assert.ok(res.stderr.includes(link), `${command}: the path is not named: ${res.stderr}`);
      assert.ok(!fs.existsSync(victim), `${command} wrote through the link`);
      assert.deepStrictEqual(snapshot(proj), before, `${command} changed the project`);
    }
  } finally {
    fs.rmSync(outside, { recursive: true, force: true });
  }
});

test('the record is replaced through a temporary file and no temporary file is left', (proj) => {
  run(proj, ['init', '--yes']);
  run(proj, ['update']);
  assert.deepStrictEqual(fs.readdirSync(path.join(proj, '.gabbe')), ['manifest.json']);
});

// update: a kit file in the preserve set follows the same rule as every other kit file.
test('update replaces an unchanged AGENTS.md and CONSTITUTION.md and keeps a changed one', (proj) => {
  run(proj, ['init', '--yes']);
  const kit = (rel) => fs.readFileSync(path.join(KIT_ROOT, rel), 'utf8');
  const OLD = 'an older kit version\n';
  const point = (rel, text) => {
    write(proj, rel, text);
    editRecord(proj, (r) => {
      r.entries.find((e) => e.path === rel).hash = sha256Of(OLD);
    });
  };
  point('agents/CONSTITUTION.md', OLD); // as installed by an older kit, never changed
  point('agents/AGENTS.md', OLD);
  write(proj, 'agents/AGENTS.md', 'MY OWN AGENTS\n'); // changed since install

  const res = tryRun(proj, ['update']);

  assert.strictEqual(res.status, 0, res.stderr);
  assert.strictEqual(read(proj, 'agents/CONSTITUTION.md'), kit('agents/CONSTITUTION.md'), 'unchanged file not refreshed');
  assert.strictEqual(read(proj, 'agents/AGENTS.md'), 'MY OWN AGENTS\n', 'a changed file was replaced');
  assert.ok(!fs.existsSync(path.join(proj, 'agents', 'CONSTITUTION.md.gabbe-bak')), 'a backup of an unchanged file');
});

test('update puts the kit\'s new version beside a changed kit file, and never over one that is not ours', (proj) => {
  run(proj, ['init', '--yes']);
  const rel = 'agents/CONSTITUTION.md';
  const side = rel + '.gabbe-new';
  const kit = fs.readFileSync(path.join(KIT_ROOT, rel), 'utf8');
  write(proj, rel, 'MY CONSTITUTION\n');

  const res = tryRun(proj, ['update']);

  assert.strictEqual(res.status, 0, res.stderr);
  assert.strictEqual(read(proj, rel), 'MY CONSTITUTION\n');
  assert.strictEqual(read(proj, side), kit);
  assert.ok(
    res.stdout.includes(`kept your ${rel}; the kit's new version is ${side} (compare, merge, then delete it)`),
    res.stdout
  );
  assert.ok(recordedPaths(proj).includes(side), 'the new version is not recorded');
  assert.ok(tryRun(proj, ['uninstall', '--dry-run']).stdout.includes(`  ${side}\n`), 'dry run does not list it');

  // Unchanged since it was written: a later update may replace it (here: the same bytes again).
  assert.strictEqual(tryRun(proj, ['update']).status, 0);
  assert.strictEqual(read(proj, side), kit);

  // Changed by the user: left alone, with a message.
  write(proj, side, 'MY NOTES ON THE NEW VERSION\n');
  const again = tryRun(proj, ['update']);
  assert.strictEqual(read(proj, side), 'MY NOTES ON THE NEW VERSION\n');
  assert.ok(again.stdout.includes('not ours or was changed'), again.stdout);

  // A .gabbe-new that the record does not own is never overwritten.
  const proj2 = mkTmp();
  try {
    run(proj2, ['init', '--yes']);
    write(proj2, rel, 'MY CONSTITUTION\n');
    write(proj2, side, 'SOMEONE ELSE\n');
    tryRun(proj2, ['update']);
    assert.strictEqual(read(proj2, side), 'SOMEONE ELSE\n');
  } finally {
    fs.rmSync(proj2, { recursive: true, force: true });
  }
});

test('update writes no .gabbe-new when the changed file equals the kit, and uninstall removes an unchanged one', (proj) => {
  run(proj, ['init', '--yes']);
  const rel = 'agents/CONSTITUTION.md';
  editRecord(proj, (r) => {
    r.entries.find((e) => e.path === rel).hash = sha256Of('an older version\n');
  });
  tryRun(proj, ['update']); // the file equals the kit's: nothing to offer
  assert.ok(!fs.existsSync(path.join(proj, rel + '.gabbe-new')));

  write(proj, rel, 'MINE\n');
  tryRun(proj, ['update']);
  assert.ok(fs.existsSync(path.join(proj, rel + '.gabbe-new')));
  assert.strictEqual(tryRun(proj, ['uninstall']).status, 0);
  assert.ok(!fs.existsSync(path.join(proj, rel + '.gabbe-new')), 'uninstall left the new version');
  assert.strictEqual(read(proj, rel), 'MINE\n');
});

if (failures) {
  console.error(`\n${failures} Node installer test(s) failed.`);
  process.exit(1);
}
console.log('\nAll Node installer tests passed.');
