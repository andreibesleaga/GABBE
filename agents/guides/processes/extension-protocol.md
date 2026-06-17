# The Extension Protocol: How to Extend GABBE Without Breaking It

GABBE is designed to absorb new methodologies, capabilities, and integrations over time without
ever forcing a breaking change on the people and agents already using it. The mechanism that makes
this safe is a single, strict rule: **extension is additive only**. You add new files and new keys;
you never remove a file, rename a key, retype an existing field, or change the meaning of something
that already exists. This guide is the canonical, step-by-step contract for adding each kind of
thing — a skill, a guide, a persona, a template, an agent-client emitter, an MCP server, or a model
— in a way that keeps every validator and backward-compatibility gate green.

## The one rule that makes everything else work

Backward compatibility is enforced, not merely encouraged. On every change GABBE runs six
backward-compatibility gates (via `scripts/gates/run_gates.sh`): API surface, CLI `--help`
byte-equality, config-schema superset, DB-schema superset, emitter golden vault, and CVE delta.
Read what "superset" implies: the new config schema and DB schema must be **supersets** of the old
ones. Adding a new optional key is a superset and passes; removing a key, making an optional key
required, or changing a key's type is not a superset and fails the gate. The same spirit applies to
the markdown kit. So before you add anything, internalize the rule:

- **Add** new files and new keys freely.
- **Never remove** an existing file, key, persona, skill, guide, or template.
- **Never rename or retype** an existing field — a rename is a remove plus an add, and the remove
  half breaks compatibility. If you must evolve a field, add a new one alongside and leave the old
  one working.
- **Never change the meaning** of an existing key, trigger, or phase id.

Everything below is just this rule applied to each artifact type.

## Adding a new skill

1. Create the file under the right category folder: `agents/skills/<category>/<name>.skill.md`
   (categories include `core`, `coordination`, `architecture`, `coding`, `ops`, `security`, `ai`,
   `data`, `product`, `industry`, `brain`).
2. Give it the required frontmatter contract — the same shape every existing skill uses:

   ```
   ---
   name: <slug matching the filename>
   description: <one line — what it does and when>
   triggers: [<natural-language phrases that should activate it>]
   tags: [<category>]
   core: <true|false>
   context_cost: <low|medium|high>
   ---
   ```

   `context_cost` is load-bearing: preflight ranks capabilities by relevance × (1 / context_cost),
   so set it honestly. Mark `core: true` only for skills that belong in the always-available set.
3. Write the body in the established skill shape (Goal, then Steps). Reference other skills,
   personas, and guides **by name in backticks** (e.g. `clarify.skill`, `prod-architect`) — never
   as markdown file-path links, which the link validator would have to resolve and which couple the
   doc to a path.
4. Register it additively in `agents/skills/00-index.md` by adding a new catalog row. Do not
   reorder or remove existing rows; append.
5. Keep the validators green (see the checklist at the end): `validate_skills.py` checks the
   frontmatter contract, `check_skills_docs.py` / frontmatter validators check consistency, and
   `validate_links.py` checks that no markdown link is broken.

## Adding a new guide

1. Create `agents/guides/<category>/<name>.md`. Guides are explanatory prose. Frontmatter is
   optional for guides (some existing guides carry a one-line `description:`, many carry none) —
   prefer self-contained prose and keep references in backticks by name, with no URLs and no
   markdown file-path links.
2. Register it additively in `agents/guides/00-index.md` by appending a new row under the correct
   domain section, and bump the displayed total if the index tracks one. Never remove or renumber
   existing entries.
3. A guide adds knowledge, not behavior, so it touches no schema and no emitter — the only gate it
   must satisfy is the link validator (no broken links) plus index consistency.

## Adding a new persona

1. Create `agents/personas/<swarm>-<role>.md` following the persona house style exactly: a
   `# Persona: <name>` heading and an HTML-comment subtitle, then the sections
   **Role**, **Does NOT**, **Context Scope**, **Primary Outputs**, **Skills Used**, a RARV cycle
   (the **RARV Notes** block: Reason / Act / Reflect / Verify), **Constraints**, and an
   **Invocation Example**. Match an existing persona such as `eng-qa` or `prod-pm` for structure.
2. In **Skills Used**, reference skills by name in backticks. If a referenced skill does not exist
   yet, add it first (additively, per the skill steps above) or state honestly that the persona
   defines the contract that skill must satisfy.
3. Register it additively in `agents/personas/00-index.md`: add the persona to the appropriate
   swarm table and bump the persona count the index reports. Never remove an existing persona — an
   agent or workflow may already invoke it by name.

## Adding a new template

1. Create the template under `agents/templates/<category>/<NAME>_TEMPLATE.md` (or the matching
   convention for that category). Templates are fill-in documents agents complete during specific
   lifecycle phases.
2. Register it additively in `agents/templates/00-index.md` with a new row and an updated total.
3. If a persona or skill is meant to produce the new template, reference it by name (in backticks)
   from that persona/skill — additively, without altering their existing outputs.

## Adding a new agent-client emitter

GABBE's kit is emitted into each agent's native location on install (for example
`.claude/skills/<slug>/SKILL.md` for Claude, `.cursor/rules/*.mdc` for Cursor, `.github/skills/`
for VS Code/Copilot, `.gemini/`, and the universal `.agents/skills/<slug>/SKILL.md` tree).

1. Add a **new** emitter that writes to the new agent's native path — never modify an existing
   emitter's output, because the **emitter golden vault** gate compares emitted output byte-for-byte
   against captured baselines. Changing an existing emitter's bytes fails that gate.
2. Capture a baseline for the new emitter (the gates use `scripts/gates/capture_emitter_baseline.py`
   and `scripts/gates/baselines/`) so the golden-vault gate has something to compare the new output
   against going forward.
3. Wire the new emitter into the install flow additively (Node installer `bin/install.js` and/or
   the Python/shell installers) so it runs alongside, not instead of, the existing emitters.
4. Confirm the existing emitters' baselines are still byte-identical — the whole point is that
   adding agent N does not perturb the output for agents 1..N-1.

## Adding a new MCP server

1. Document the new server additively in `docs/MCP_CONFIGURATIONS.md` and any MCP registry the kit
   ships — add an entry; do not change or remove existing entries.
2. If the optional `gabbe` CLI's MCP layer (`gabbe/mcp_server.py`) gains a new tool, add it as a
   **new** tool with a new name. Do not rename or change the signature of an existing MCP tool —
   that is part of the API surface the API-surface gate protects.
3. Keep secrets and endpoints out of committed config; reference them through the established
   secret/config mechanism. Default to fail-closed, consistent with the kit's security posture.

## Adding a new model

1. Register the model additively in the model configuration (`gabbe/config.py` and the config
   schema documented in `docs/SCHEMA.md`) as a **new** entry / new optional key. The config-schema
   gate requires the new schema to be a superset of the old, so a new optional model key passes
   while changing the type or default of an existing one fails.
2. Do not change existing model ids, defaults, or tiers — downstream configs and routing may depend
   on them. Add the new model as an additional choice and, if needed, an additional tier.
3. If you are configuring or reasoning about a Claude/Anthropic model specifically, consult the
   current `claude-api` reference rather than relying on memory for ids, pricing, or limits.

## The frontmatter + index-registration contract, in one place

Two invariants make a new artifact discoverable and selectable:

- **Frontmatter contract** (skills, and any artifact that carries it): the keys above must be
  present and well-formed; `name` must match the filename slug; `context_cost` must be set because
  selection ranking depends on it. Validators enforce this.
- **Index registration**: every artifact must be appended to its `00-index.md` (skills, guides,
  personas, templates) so preflight's cheap index scan can see it. Append; never reorder or remove.
  An artifact that exists on disk but is missing from its index is effectively invisible to the
  selection flow, and the consistency checks will flag the mismatch.

## The validators and gates that must stay green

Before you consider an extension done, the same checks CI runs must pass. `scripts/verify_all.sh`
orchestrates them; the ones you will most often touch are:

- **Backward-compat gates** — `scripts/gates/run_gates.sh`: API surface, CLI `--help` byte-equality,
  config-schema superset, DB-schema superset, emitter golden vault, CVE delta. These encode the
  additive-only rule mechanically.
- **`agents/scripts/validate_skills.py`** — skill frontmatter contract and structure.
- **`agents/scripts/validate_links.py`** — no broken markdown links. (Keeping references in
  backticks by name, rather than as bracket-and-parenthesis file-path links, is the simplest way
  to never break this.)
- **`agents/scripts/validate_integrity.py`** and the other consistency/capability validators
  (frontmatter, use-cases, triggers/MCP, methodology graph) — cross-file coherence, including that
  index registrations match the files on disk and that referenced phases/skills exist.

If all of these are green and you added only new files and new keys, your extension is, by
construction, backward compatible.

## Why this protocol is the absorption mechanism

Because every extension is additive and every existing surface is gate-protected, GABBE can take on
a new methodology — a new persona swarm, a new lifecycle phase id (the phase validator already
accepts extended Day-2 phases like S11/S12 alongside S01–S10), a new skill family, a new target
agent — by **adding** the artifacts that express it, never by mutating what is already there.
Nothing that works today stops working tomorrow. That is the contract that lets the system grow
indefinitely without a breaking change, and it is worth following exactly rather than approximately:
the gates do not negotiate, and that strictness is the feature.

## Honest limits

- The gates catch *compatibility* regressions, not *quality* — an additive change can be green and
  still be a bad idea. Review still matters.
- "Additive only" can accumulate cruft over time (deprecated-but-retained keys, superseded skills).
  GABBE accepts that cost deliberately as the price of never breaking callers; periodic curation is
  a separate, human-gated decision, not something this protocol authorizes you to do unilaterally.
- A new artifact is only as discoverable as its index entry and its `triggers`/`context_cost`; a
  technically-valid file with poor metadata may never get selected. Registration is necessary but
  not sufficient for the capability to actually be used.
