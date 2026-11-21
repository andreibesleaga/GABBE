#!/usr/bin/env node
/* SPDX-License-Identifier: Apache-2.0 */
// Merge a GABBE hook fragment into a tool's hooks file, or remove it again.
//   node merge-hooks.js <fragment.json> <target.json>            show the result, write nothing
//   node merge-hooks.js <fragment.json> <target.json> --write    write it (keeps the old file as <target>.gabbe-bak)
//   node merge-hooks.js <fragment.json> <target.json> --remove   take the GABBE entries out
// Safe rule: it only adds entries, never changes or removes anything else. If the target is not
// plain JSON or has an unexpected shape, it changes nothing, prints the fragment and exits 1.
// An entry is "ours" only when it is exactly one of the fragment's: same event, same matcher and
// the same command strings. --remove takes out those entries and nothing else.
// The installers (bin/install.js) require this file and use mergeFragment and removeFragment.
// No network, no command is run.
'use strict';
const fs = require('fs');
const path = require('path');

const cmdsOf = (item) => (item && Array.isArray(item.hooks) ? item.hooks.map((h) => h && h.command) : [item && item.command]);
const same = (a, b) => (a && a.matcher) === (b && b.matcher) && JSON.stringify(cmdsOf(a)) === JSON.stringify(cmdsOf(b));

class Unsafe extends Error {}

function checkShape(doc, fragment) {
  if (doc === null || typeof doc !== 'object' || Array.isArray(doc)) throw new Unsafe('target is not a JSON object');
  if (doc.hooks !== undefined && (doc.hooks === null || typeof doc.hooks !== 'object' || Array.isArray(doc.hooks))) {
    throw new Unsafe('"hooks" has an unexpected shape');
  }
  for (const event of Object.keys(fragment.hooks)) {
    if (doc.hooks && doc.hooks[event] !== undefined && !Array.isArray(doc.hooks[event])) throw new Unsafe(`hooks.${event} is not a list`);
  }
}

// Add the fragment's entries that are not there yet. Returns { doc, changed, addedVersion }.
// The input is not modified. Throws Unsafe when the shape is not what is expected.
function mergeFragment(input, fragment) {
  checkShape(input, fragment);
  const doc = JSON.parse(JSON.stringify(input));
  let changed = false;
  let addedVersion = false;
  for (const [event, items] of Object.entries(fragment.hooks)) {
    for (const item of items) {
      if (doc.hooks === undefined) doc.hooks = {};
      const list = doc.hooks[event] || (doc.hooks[event] = []);
      if (!list.some((x) => same(x, item))) { list.push(item); changed = true; }
    }
  }
  if (changed && fragment.version !== undefined && doc.version === undefined) { doc.version = fragment.version; addedVersion = true; }
  return { doc, changed, addedVersion };
}

// Take out exactly the fragment's entries (and the version this tool added, when told so).
// An event list or "hooks" left empty is removed. The input is not modified.
function removeFragment(input, fragment, opts) {
  checkShape(input, fragment);
  const doc = JSON.parse(JSON.stringify(input));
  if (doc.hooks) {
    for (const [event, items] of Object.entries(fragment.hooks)) {
      if (!doc.hooks[event]) continue;
      const kept = doc.hooks[event].filter((x) => !items.some((item) => same(x, item)));
      if (kept.length) doc.hooks[event] = kept; else delete doc.hooks[event];
    }
    if (Object.keys(doc.hooks).length === 0) delete doc.hooks;
  }
  if (opts && opts.addedVersion && doc.version === fragment.version) delete doc.version;
  return doc;
}

function bail(msg, fragment) {
  process.stderr.write(`merge-hooks: ${msg}. Nothing was changed. Add this by hand:\n${JSON.stringify(fragment, null, 2)}\n`);
  process.exit(1);
}

function main() {
  const [fragFile, target, flag] = process.argv.slice(2);
  if (!fragFile || !target || (flag && flag !== '--write' && flag !== '--remove')) {
    process.stderr.write('usage: node merge-hooks.js <fragment.json> <target.json> [--write|--remove]\n');
    process.exit(2);
  }
  const fragment = JSON.parse(fs.readFileSync(fragFile, 'utf8'));
  let doc = {};
  const exists = fs.existsSync(target);
  if (exists) {
    try { doc = JSON.parse(fs.readFileSync(target, 'utf8')); } catch (e) { bail('target is not plain JSON', fragment); }
  }
  try {
    if (flag === '--remove') {
      doc = removeFragment(doc, fragment);
      // A file that is only the version this tool added is left empty.
      if (Object.keys(doc).join() === 'version' && doc.version === fragment.version) delete doc.version;
    } else {
      doc = mergeFragment(doc, fragment).doc;
    }
  } catch (e) {
    if (e instanceof Unsafe) bail(e.message, fragment);
    throw e;
  }
  const text = JSON.stringify(doc, null, 2) + '\n';
  if (!flag) { process.stdout.write(text); return; }
  if (exists) {
    let backup = target + '.gabbe-bak';
    for (let n = 1; fs.existsSync(backup); n += 1) backup = `${target}.gabbe-bak.${n}`; // never overwrite a backup
    fs.copyFileSync(target, backup);
  }
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, text);
  process.stdout.write(`${flag === '--remove' ? 'removed from' : 'merged into'} ${target}\n`);
}

if (require.main === module) main();
module.exports = { mergeFragment, removeFragment, Unsafe };
