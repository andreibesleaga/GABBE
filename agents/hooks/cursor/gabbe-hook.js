#!/usr/bin/env node
/* SPDX-License-Identifier: Apache-2.0 */
// GABBE hook for Cursor (beforeShellExecution). Input: JSON on stdin with "command".
// Output: {"permission": "ask", ...} on stdout for a command it flags; {} (no decision) for the rest. Exit 0.
// Why {} and not "allow": Cursor's hooks page does not say whether "allow" skips the user's own
// allow-list or approval prompt; it only says that "ask" wins over "allow" when hooks disagree.
// A hook that may only add questions must not risk granting anything, so an unflagged command gets
// no decision and Cursor's own settings decide. The page also does not say what {} does; it is
// valid JSON and grants nothing. https://cursor.com/docs/agent/hooks, read 2026-11-21.
// Not checked in a running Cursor. The same page says a response that does not match the hook's
// schema blocks the action: if your Cursor blocks every command with this hook, set
// GABBE_CURSOR_UNFLAGGED=allow in the hook's environment; unflagged commands then get "allow".
// Failure direction: unreadable input => "ask". Exit 1 (if output cannot be written) lets the
// command run, because Cursor fails open unless "failClosed" is set.
// The command text is only parsed, never run.
'use strict';
const { classify, readInput, reasonFor } = require('../lib/shell-guard.js');

function out(permission, message) {
  const o = permission ? { permission } : {};
  if (message) { o.user_message = message; o.agent_message = message; }
  process.stdout.write(JSON.stringify(o));
}

try {
  const input = readInput();
  if (typeof input.command !== 'string') throw new Error('no command');
  const what = classify(input.command);
  if (what) out('ask', reasonFor(what));
  else out(process.env.GABBE_CURSOR_UNFLAGGED === 'allow' ? 'allow' : null);
} catch (e) {
  out('ask', 'GABBE hook could not read its input (' + e.message + '). It asks you instead of guessing.');
}
