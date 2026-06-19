#!/usr/bin/env node
/* SPDX-License-Identifier: Apache-2.0 */
/*
 * Zero-dependency end-to-end test for the Node installer (bin/install.js).
 * Exercises non-interactive `init --yes` into a throwaway project that already
 * contains user files, and asserts the never-clobber invariant: pre-existing
 * differing files are backed up to <name>.gabbe-bak, never lost.
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

// 2. A pre-existing non-preserved file under docs/ is backed up, never clobbered.
test('pre-existing docs/ file is backed up to .gabbe-bak', (proj) => {
  const docs = path.join(proj, 'docs');
  fs.mkdirSync(docs, { recursive: true });
  // Use a name the kit also ships so a real collision occurs.
  const userDoc = path.join(docs, 'INSTALL.md');
  fs.writeFileSync(userDoc, 'USER OWNED INSTALL DOC\n');

  run(proj, ['init', '--yes', '--agents', 'claude']);

  const bak = userDoc + '.gabbe-bak';
  if (fs.existsSync(bak)) {
    assert.strictEqual(
      fs.readFileSync(bak, 'utf8'),
      'USER OWNED INSTALL DOC\n',
      'backup does not contain the user original'
    );
  } else {
    // If the kit did not ship docs/INSTALL.md there is no collision; the user
    // file must then be left exactly as-is.
    assert.strictEqual(fs.readFileSync(userDoc, 'utf8'), 'USER OWNED INSTALL DOC\n');
  }
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

if (failures) {
  console.error(`\n${failures} Node installer test(s) failed.`);
  process.exit(1);
}
console.log('\nAll Node installer tests passed.');
