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

function run(cwd, args) {
  return execFileSync('node', [INSTALL_JS, ...args], {
    cwd,
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
    run(proj, ['doctor']);
  } catch (e) {
    err = e;
  }
  assert.ok(err, 'unknown command did not fail');
  assert.strictEqual(err.status, 1, `exit status ${err.status}, expected 1`);
  assert.ok(/Unknown command: doctor/.test(err.stderr), 'no "Unknown command" message');
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

// 12. Install then `gabbe uninstall --purge` gives the project back unchanged.
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

if (failures) {
  console.error(`\n${failures} Node installer test(s) failed.`);
  process.exit(1);
}
console.log('\nAll Node installer tests passed.');
