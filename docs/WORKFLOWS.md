# How to work with GABBE

Six situations, one section each. Each section says when to use it, what you need, what to tell the
agent, what the agent does, where you decide, what is written where, and how to stop and continue.

Terms used on this page:

- **Full kit**: installed with `npx gabbe-kit init` ([INSTALL.md](INSTALL.md)). It has `agents/AGENTS.md`,
  the Constitution, personas, guides and templates.
- **Plugin**: the Claude Code plugin `gabbe` (49 skills, no personas, no guides). Its skills are named
  `/gabbe:<skill>`. Start with `/gabbe:gabbe-start`.
- **Human gate**: a hard stop. The agent does not go on until you answer.
  There are six: S00, S01, S02, S07, S08, S10. The phases S00 to S13 are in `agents/guides/processes/loki-sdlc-phases.md`.
- **Memory files**: `agents/memory/RESUME_POINTER.md` (the next action), `PROJECT_STATE.md` (the phase),
  `CONTINUITY.md` (failures to avoid), `AUDIT_LOG.md` (one row per decision and gate).

In every situation the rules of Article 0 apply: the agent makes no commit, push, tag, publish or deploy
unless you ask in that request, and it asks before anything destructive.

## 1. A new project

**When:** you start something from nothing and it is larger than a one-file change.

**Needs:** the full kit for the whole lifecycle. The plugin works too: `gabbe-start` carries the rules and
the phase table, but a skill that is not in the plugin is marked with `*` and the agent cannot use it.

**First sentence:**

```
"Read AGENTS.md. I want to build [description]. Start with spec-writer skill."
```

Plugin: `/gabbe:gabbe-start` and then the same sentence.

**What the agent does:**

1. Runs `preflight`, then `clarify`: it reads the memory files and asks what is unclear.
2. S00 discovery (`ideation-facilitation`, `opportunity-assessment`): problem, users, go or no-go.
3. S01 requirements (`spec-writer`, `req-elicitation`, `req-review`, `security-baseline`): a PRD in EARS form.
4. S02 architecture (`arch-design`, `adr-writer`, `threat-model`): C4 model, decisions, threat model.
5. S03 and S04: technical spec, then tasks in `project/TASKS.md` (`decompose`).
6. S05 and S06: code written test first (`tdd-cycle`), then quality gates G1 to G9 and `final-review`.
7. S07 security review, S08 human review, S09 staging, S10 production.

**You decide:** the six gates S00, S01, S02, S07, S08 and S10. At S10 you say "deploy now" in that request.
The agent records each answer as a `HUMAN_APPROVED` row in `agents/memory/AUDIT_LOG.md`.

**Written:** requirements, plan and decisions as files in the project; tasks in `project/TASKS.md`;
phase and next action in the memory files.

**Stop and continue:** ask the agent to save its state (`state-preserve`). It writes `RESUME_POINTER.md`
and a checkpoint (`sdlc-checkpoint`). Later, see section 6.

## 2. An existing codebase

**When:** the repository already has code and no GABBE state. The agent does not start at S00. It first learns
what is there, in stages B0 to B4 (`agents/guides/processes/brownfield-lifecycle.md`).

**Needs:** the full kit, or the plugin: it has `existing-project-onboarding`, `code-archaeology`,
`characterization-tests`, `safe-refactoring`, `incremental-feature` and `dependency-upgrade`.

**First sentence:**

```
"Read AGENTS.md. This repository already has code. Use the existing-project-onboarding skill."
```

Plugin: `/gabbe:existing-project-onboarding`.

**What the agent does:**

1. B0 understand: runs the build and tests once, maps the code, writes `CODEBASE_MAP.md` and
   `ASSESSMENT.md`. It changes no source file. It ends with the question "Approve B1?".
2. B1 characterise (`characterization-tests`): writes tests that pin what the code does today.
3. B2 make safe: build and tests green and recorded; security fixes only (`dependency-upgrade`).
4. B3 improve in small steps (`safe-refactoring`): each step has one check and one undo.
5. B4 add features (`incremental-feature`): each feature goes through S01 to S08, and S09 and S10 when it ships.

**You decide:** you approve the assessment before B1 and the plan before B3. Deleting old code and a major
dependency upgrade each need a separate yes. Each feature in B4 passes the gates S01, S02, S07, S08 and S10.

**Written:** `CODEBASE_MAP.md` and `ASSESSMENT.md` in the repository root; `project/CHARACTERIZATION.md`
and `project/TASKS.md`; memory files, with the baseline output in `agents/memory/episodic/`.

**Stop and continue:** the stage is kept in `PROJECT_STATE.md` (for example `B0 DONE`). See section 6.

## 3. A single small change

**When:** one file, no new dependency, no public API or security effect, and you can undo it. This is the
small-change lane in `agents/AGENTS.md` section 5. Anything bigger uses section 1 or 2.

**Needs:** the plugin or the full kit.

**First sentence:**

```
"Read AGENTS.md. Bug: [description]. Use debug skill with TDD."
```

For a change that is not a bug, say "Small change: [description]. Use tdd-cycle."

**What the agent does:**

1. Reads `agents/memory/RESUME_POINTER.md` if it exists.
2. Writes a failing test (`tdd-cycle`; for a bug, `debug` finds the cause first).
3. Makes the change and runs the project's test and lint commands.
4. Appends one row to `agents/memory/AUDIT_LOG.md`.

**You decide:** there is no gate in this lane. You still decide on commit and push: the agent hands you the
commands. If the change turns out to touch more than one file or any public API, the agent stops and moves
to the full sequence.

**Written:** the test, the change, one `AUDIT_LOG.md` row.

**Stop and continue:** nothing to save beyond the audit row.

## 4. Brain mode

**When:** a complex goal where the cheapest way to do it is not clear: it chooses between a quick fix,
deeper thinking, or the full lifecycle.

**What it is not:** Brain mode is text that the agent follows. It is not a program. Its words (Active
Inference, free energy, surprise, OODA) are an analogy for a habit: predict, act, compare, adjust. Nothing
computes free energy, and it guarantees no result.

**Needs:** the full kit. The plugin `gabbe-brain` has the Brain skills, but they need the personas and guides
of the full kit. The `gabbe` command line is optional.

**First sentence** (only these phrases start it: `brain mode`, `activate brain`):

```
"Activate Brain Mode. Goal: [build X / migrate Y / solve Z]."
```

**What the agent does:**

1. B01 loads context: `PROJECT_STATE.md`, the last rows of `AUDIT_LOG.md`, earlier decision logs.
2. B02 chooses a strategy: A quick fix, B deep thinking (`sequential-thinking`), or C the lifecycle. C
   costs most, so it asks you first.
3. B03 runs and watches. After two identical failures it changes the prompt, adds knowledge or goes up one
   model tier (it asks before the top tier). After three it stops (`self-heal`).
4. B04 writes one decision-log entry in `agents/memory/episodic/` and says "leaving Brain mode".

**You decide:** the strategy when it is C; the top model tier; any swarm. If C runs, the six gates apply.

**Written:** `DECISION` rows in `AUDIT_LOG.md`, one decision log under `agents/memory/episodic/`.

**Stop and continue:** Brain mode ends at B04. If the task spans sessions, its state is in `RESUME_POINTER.md`.

## 5. Loki mode

**When:** a large build that does not fit one context: more than five features or twenty files.

**What it is not:** Loki mode is a text procedure. There is no scheduler. One agent plays the personas one
after another, or delegates to native subagents, and follows the lifecycle. Cost grows with every persona.

**Needs:** the full kit (personas in `agents/personas/`, the phase guide). The plugin cannot run it alone.

**First sentence** (only `loki mode`, `activate loki` or `run the lifecycle` start it):

```
"Activate `agents/skills/brain/loki-mode.skill.md`. Goal: [build X]. Work through the phases on your own and stop at every Human Approval Gate, before any commit, push, publish or deploy, and when a task requires True A2A Delegation."
```

**What the agent does:**

1. Runs `preflight`, `update-scan` and `clarify`.
2. Checks state: a project that is in progress is resumed (`session-resume`); a new project starts at S00
   (at S01 only if you say "skip discovery"); a repository with code goes to the existing-project path.
3. For each phase S00 to S13: the lead persona does the work, then `sdlc-checkpoint` saves a snapshot.
4. At S06 it runs the quality gates G1 to G9; the judge (`orch-judge`) may veto, which blocks the phase.

**You decide:** S00, S01, S02, S07, S08 and S10. Only you lift a veto.

**Written:** `PROJECT_STATE.md` (phase), `AUDIT_LOG.md`, `RESUME_POINTER.md`, snapshots under
`agents/memory/episodic/SESSION_SNAPSHOT/`, `project/TASKS.md`.

**Stop and continue:** the agent saves state after each step, not only on exit. On a stop it writes a
snapshot and a `SESSION_END` row. See section 6.

## 6. Resuming unfinished work

**When:** a new session, a new day, after an interruption, or after the agent's context was compacted.

**Needs:** the memory files from the earlier session, in `agents/memory/`. The plugin has `session-resume`;
if the files do not exist, it offers to create them and does so only if you agree.

**First sentence:**

```
"Read AGENTS.md and agents/memory/PROJECT_STATE.md. Resume the project."
```

Plugin: `/gabbe:session-resume`.

**What the agent does:**

1. Reads `RESUME_POINTER.md` first: its next action is where work continues.
2. Reads `PROJECT_STATE.md` (phase), `CONTINUITY.md` and the recent `AUDIT_LOG.md` rows.
3. Compares the checksums stored in the last snapshot with the three memory files; a mismatch is reported.
4. Runs `integrity-check` to compare the files with the project.
5. Writes a resume report: phase, last checkpoint, blockers, next action. Then it continues.

**You decide:** whether the report is right. A gate that was open stays open until you answer.

**Written:** a refreshed `RESUME_POINTER.md` after each meaningful step.

**Stop and continue:** to stop, ask the agent to save its state; it writes the pointer and a snapshot
first. After a context compaction or `/clear` in the same session, the agent re-reads `RESUME_POINTER.md` and the
file it was editing, then continues. To switch agent, `state-portability` exports and imports the state.
