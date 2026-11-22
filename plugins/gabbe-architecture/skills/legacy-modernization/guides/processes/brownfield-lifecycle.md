# Brownfield Lifecycle: Working on an Existing Codebase

> For code that already exists. Maps the work onto the normal lifecycle (S00 to S13 in
> `guides/processes/loki-sdlc-phases.md`). New projects use S00 onward directly.
> Stages: B0 Understand, B1 Characterise, B2 Make it safe, B3 Improve in small steps,
> B4 Add or change features.

## The path at a glance

| Stage | Question it answers | Main skill | Main output | Human decides |
|---|---|---|---|---|
| B0 Understand | What is here and does it run? | `skills/architecture/existing-project-onboarding.skill.md`, `skills/architecture/code-archaeology.skill.md` | `CODEBASE_MAP.md`, `ASSESSMENT.md` | Approves the assessment and the proposal |
| B1 Characterise | What does the code do today? | `skills/coding/characterization-tests.skill.md` | `project/CHARACTERIZATION.md`, pinned tests | Confirms any suspected bug before it is changed |
| B2 Make it safe | Are build, tests and CI green and recorded? | `skills/ops/dependency-upgrade.skill.md` (security fixes only), `skills/coding/testing-strategy.skill.md` | Recorded green baseline | Approves the plan for B3 |
| B3 Improve in small steps | Can the structure get better without a behaviour change? | `skills/coding/safe-refactoring.skill.md`, `skills/architecture/legacy-modernization.skill.md`, `skills/coding/refactor.skill.md` | Small reversible steps in `project/TASKS.md` | Deletions of old code; anything that touches production |
| B4 Add or change features | How does a feature go in without breakage? | `skills/coding/incremental-feature.skill.md` | Feature through S01 to S08 (S09 and S10 when it ships) | Gates S01, S02, S07, S08, S10 |

Persona that owns this work: `personas/eng-maintainer.md`.

## Human decision points

- B0 to B1: the human approves the assessment and the proposal. Nothing is characterised or changed before that.
- Before B3: the human approves the plan (the step list in `project/TASKS.md`). B3 does not start without that approval.
- B3 deletions and dependency majors: a separate yes each time.
- Each feature in B4 passes the human gates of the normal lifecycle: S01, S02, S07, S08 and, when it ships, S10. The B0 approval takes the place of the S00 go / no-go.
- Every production deploy is the S10 human gate: the human says "deploy now" in that request. No commit, push, tag, publish or deploy happens otherwise.
- Record each approval as one `HUMAN_APPROVED` row in `agents/memory/AUDIT_LOG.md` with the stage, the date and the human's words.

## B0 Understand

- Entry: the repository has source and `agents/memory/PROJECT_STATE.md` shows `NOT_STARTED` (or no GABBE state).
- Steps: run `existing-project-onboarding.skill`. It runs the existing build and tests once, maps the code (`code-archaeology.skill`), writes the assessment, records the state and proposes the next stage.
- Exit: `CODEBASE_MAP.md` has 5 of 5 spot checks verified; `ASSESSMENT.md` has build, test, CI and coverage state with evidence; `PROJECT_STATE.md` says `B0 DONE`; the human approved the proposal.
- Artefacts: `CODEBASE_MAP.md`, `ASSESSMENT.md` (templates `templates/architecture/CODEBASE_MAP_TEMPLATE.md`, `templates/architecture/ASSESSMENT_TEMPLATE.md`), `agents/memory/episodic/baseline-<date>.txt`.
- No source file is changed in this stage.

## B1 Characterise

- Entry: B0 approved; the areas to change are listed in the assessment.
- Steps: run `characterization-tests.skill` on those areas only: choose seams, golden master for large output, control the clock, randomness and network, check that each test can fail, run three times, pin suspected bugs and flag them.
- Exit: the units in scope are pinned; the suite is green three times in a row; baseline before and after is recorded; suspected bugs are listed for the human.
- Artefacts: `project/CHARACTERIZATION.md`, new tests and golden files.
- The 99% rule applies to new or changed behaviour. Untouched legacy code is not forced to 99%.

## B2 Make it safe

- Entry: B1 exit met for the areas in scope.
- Steps: confirm the existing build and the whole test suite pass and write the numbers in `PROJECT_STATE.md`. Record CI state (which workflow runs what, last result). Fix only what blocks a green baseline: a broken script, a missing install step. Apply known security fixes through `dependency-upgrade.skill`, same-major only. Behaviour does not change.
- Exit: build and tests green; CI state recorded (or "no CI" with the proposal to add one); the plan for B3 written in `project/TASKS.md` with one check and one undo per step; the human approved the plan.
- Artefacts: updated `PROJECT_STATE.md`, step list in `project/TASKS.md`.

## B3 Improve in small steps

- Entry: B2 exit met and the plan approved.
- Steps: run `safe-refactoring.skill`: strangler facade, branch by abstraction, parallel run or local clean-up, one reversible step at a time; full suite after each step; undo on red. Dependency upgrades are their own steps (`dependency-upgrade.skill`). Debt items come from `skills/ops/tech-debt.skill.md` and `skills/architecture/arch-debt.skill.md`.
- Exit: planned steps done or consciously left; pass count and coverage not below the B2 baseline; no new cycles; touched code at complexity 10 or less.
- Artefacts: `project/TASKS.md` with step results, `project/DEPENDENCY_UPGRADES.md` when used.
- Old code is removed last, after the new path served for the agreed period and the human said yes.

## B4 Add or change features

- Entry: B2 exit met (B3 is not a precondition).
- Steps: run `incremental-feature.skill`. It finds the seam, pins the surroundings, picks a flag or branch by abstraction if that lowers the risk, and then follows S01 to S08 at the size of the change. It continues to S09 and S10 when the feature ships.
- Exit: the feature's gates pass (G1 to G9; G7 and G8 recorded `N/A` with a reason when the project has no layers or no user interface); characterisation tests pass unchanged; the human approved the gates that apply.
- Artefacts: `project/EARS_REQUIREMENTS.md`, `PLAN.md`, tests, code, rollback note.
- Coverage: 99% for the new and changed lines; the project floor `coverage_min` in `AGENTS.md` is not lowered without the human.

## When something is missing

| Missing | What to do |
|---|---|
| No tests | Stay in B1 until the area in scope is pinned. Do not refactor or add features first. Start with the highest seam (route or public function). |
| No build or it does not run | Record the exact error in `ASSESSMENT.md`. In B2 fix only the blocker (a missing tool, a stale lock) and write it down. If the cause is unknown, ask the human before changing more. |
| Tests exist but are red | Record the failing list in the baseline. Ask the human: fix, quarantine with a reason, or accept as known. Never delete a failing test to get green. |
| No documentation | The code map is the first document. Put each unknown in the unknowns list with the question for the human. |
| Unknown owners | Write "owner unknown" and the history hint (`git shortlog -sn -- <path>`). The human names a contact or accepts the risk. |
| No CI | Record "no CI" in B2 and propose a minimal workflow that runs the test command; adding it is a change the human approves. |
| No version control history | Say so in the map (hot spots cannot be computed) and rely on the unknowns list. |

## Session start for a resumed brownfield project

1. Read `agents/memory/RESUME_POINTER.md` and `PROJECT_STATE.md`. The stage (`B0 DONE`, `B1 IN_PROGRESS`, and so on) tells where to continue.
2. Re-run the test command; the number must match the recorded baseline. A difference is reported before any work.
3. Continue the stage. Never redo an approved stage; ask if the repository changed a lot since the recorded commit.

## Related

- `skills/architecture/legacy-modernization.skill.md` (strangler plans for large legacy systems)
- `guides/principles/legacy-tech.md`
- `guides/processes/loki-sdlc-phases.md` (the S00–S13 specs used by B4)
- `skills/ops/dependency-lifecycle.skill.md` (dependency policy)
