<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# GABBE v1.0 Release Checklist

A human-runnable release gate that mirrors the v1.0 acceptance matrix in
`GABBE-v1.0-MASTER-PLAN.md`. Tag `v1.0.0` only when **every** box below is
ticked on a clean checkout and in CI. No item may be waived.

Run all commands from the repository root. Each section maps to one acceptance
item; commands are shown in fenced blocks so they are not link-checked.

> **Honesty note.** Property-based / metamorphic tests and evals **sample** an
> input space and **raise confidence** — they do not prove correctness.
> LLM-as-judge is biased-but-useful and calibrated against human labels, never
> treated as ground truth. The AI-risk standards map documents **coverage, not
> certification**. These checks establish a verifiable readiness bar, not literal
> perfection.

---

## 1. Methodology layer valid & self-consistent

```bash
python3 agents/scripts/validate_skills.py            # frontmatter parses; required keys present
python3 agents/scripts/validate_links.py             # zero broken [text](path) links, all files
python3 agents/scripts/validate_integrity.py         # required dirs/structure intact
python3 agents/scripts/verify_triggers_and_mcps.py   # triggers non-empty; referenced MCPs exist
python3 agents/scripts/verify_use_cases.py           # every documented scenario resolves to real skills
python3 agents/scripts/validate_methodology_graph.py # lifecycle DAG + persona handoffs + memory state coherent
```

- [ ] `validate_skills.py` exits 0
- [ ] `validate_links.py` exits 0 (zero broken links, all markdown files)
- [ ] `validate_integrity.py` exits 0
- [ ] `verify_triggers_and_mcps.py` exits 0 (triggers non-empty/non-placeholder; referenced MCPs exist)
- [ ] `verify_use_cases.py` exits 0 (every documented scenario resolves to real skills)
- [ ] `validate_methodology_graph.py` exits 0 (lifecycle state machine is a valid DAG with human-approval gates; persona handoffs resolve; memory state model coherent; skill shape valid)
- [ ] Manual cross-check: every `S00`–`S13` phase + every new gate (`S02.5`/`S04.5`/`S06.5`/`S07.5`) references an existing skill/template/persona, and every new skill/template/persona appears in its `00-index.md`

## 2. Backward-compatibility gates green

```bash
bash scripts/gates/run_gates.sh
```

- [ ] Gate 1 `api-surface` green (no removed/changed public signatures — additions only)
- [ ] Gate 2 `cli-help` green (byte-equal; only `cli_help/verify.txt` regenerated for the additive `--chaos` flag, plus any documented additive carve-out for new `uninstall`/`update`/`doctor`/`eval` help)
- [ ] Gate 3 `config-schema` green (additive only)
- [ ] Gate 3b `db-schema` green (additive only)
- [ ] Gate 4 `emitter-vault` green (every prior client's output byte-compatible; new agents add new paths only)
- [ ] Gate 6 `cve-delta` green (no new CVEs)

## 3. Python suite green (deterministic, per-commit)

```bash
pip install -e ".[dev]"
pytest gabbe/tests/ scripts/tests/ -v -m "not slow and not live_llm and not mutation"
ruff check . && black --check . && mypy gabbe
```

- [ ] `pytest -m "not slow and not live_llm and not mutation"` passes (includes `test_mcp_contract.py`, `test_brain_invariants.py`, `test_loki_shadow.py`, `test_autodetect.py`, `test_one_command_install.py`, and the assertions-only `eval_skills` subset)
- [ ] `ruff check .` clean
- [ ] `black --check .` clean
- [ ] `mypy gabbe` clean (`--strict` on core modules)

## 4. Self-* capabilities each demonstrated (claim → proof)

```bash
pytest gabbe/tests/test_brain_properties.py          # self-evolving: gene generation increments; reward loop closes
pytest gabbe/tests/test_route_properties.py          # self-adaptive: PII→LOCAL; complexity routing
pytest gabbe/tests/test_chaos_fault_injection.py     # self-healing: escalation/hardstop after repeated failure
python3 agents/scripts/verify_use_cases.py           # dynamic-load-or-ask scenario for dynamic-capability-loading.md
gabbe verify --chaos                                 # all fault-injection self-checks PASS
```

- [ ] Self-evolving demonstrated (brain property test: generation increments, reward closes the loop)
- [ ] Self-adaptive demonstrated (route property test: PII→LOCAL, complexity routing)
- [ ] Self-healing demonstrated (chaos fault-injection test: escalation/hardstop after repeated failure)
- [ ] Dynamic-load-or-ask scenario passes for `dynamic-capability-loading.md`
- [ ] `gabbe verify --chaos` → all fault-injection self-checks PASS

## 5. Compatibility & emission proven (works standalone, every target agent)

```bash
# For each supported client (claude, cursor, copilot, gemini, codex, + new additive ones):
python3 agents/scripts/compile_skills.py --platform <client> --skills-dir agents/skills --target-dir /tmp/gabbe-<client>
python3 scripts/init.py     # (or: npx gabbe init) — clean init succeeds end-to-end with new content
```

- [ ] `compile_skills.py` emits successfully for every supported client (claude, cursor, copilot, gemini, codex, and each additive client)
- [ ] New skills / personas / templates appear in each client's emitted output
- [ ] Clean `python3 scripts/init.py` (or `npx gabbe init`) succeeds end-to-end with the new content

## 6. Release mechanics complete

- [ ] Version = `1.0.0` in `pyproject.toml`, `package.json`, and `gabbe/__init__.py`
- [ ] `CHANGELOG.md` has the v1.0.0 entry (dated 2026-06-17) as the top entry
- [ ] `README.md` and `llms.txt` refreshed (v1.0 line: cradle-to-grave ADLC, evals + guardrails, advanced testing, one-command multi-OS install with autodetect) with honest world-first framing preserved
- [ ] Full CI green (validate matrix py3.9–3.13 + lint + gates)

## 7. Forward-adaptability proven

- [ ] `extension-protocol.md` walkthrough adds a throwaway sample skill/template/persona/MCP, and all validators + gates pass (proving new things can always be added additively); then the sample is reverted
- [ ] Confirms any future methodology can be absorbed without a breaking change

## 8. Install / update / uninstall reversible & isolated (multi-OS)

```bash
pytest scripts/tests/test_install_manifest.py scripts/tests/test_uninstall.py \
       scripts/tests/test_install_isolation.py scripts/tests/test_remove_agents.py -v
```

- [ ] Install-manifest, uninstall, isolation, and remove-agents tests pass
- [ ] Manual matrix (tmp dirs) for scope ∈ {project, custom-dir, global}: install → only target written (zero writes outside target except `--global`) → `update` (user/preserve files intact) → `uninstall --dry-run` (no change) → `uninstall` → target byte-identical to pre-install state, `.bak` restored
- [ ] Install verified from each channel (`npx gabbe init` / `pipx install gabbe` / `curl -fsSL …/install.sh | sh` / `git clone` + `python3 scripts/init.py`)
- [ ] Unselected agents get zero files; `--remove-agents` removes only the named agent
- [ ] CI `install-matrix` green on {ubuntu, macos, windows} × {npx / pip|pipx / curl|sh | install.ps1}: install → `gabbe doctor` (detects OS/arch, runtimes, agents, scope; all checks PASS) → emit for every detected agent → `update` → `uninstall` → byte-identical restore

## 9. Evals & standards-grounded guardrails proven (Track E)

```bash
python3 agents/scripts/eval_skills.py                # assertions-only subset (per-commit, green)
# nightly / opt-in:
GABBE_LIVE_LLM=1 python3 agents/scripts/eval_skills.py --live   # scorecard within threshold of baseline (non-blocking)
```

- [ ] `eval_skills.py` assertions-only subset green per-commit
- [ ] Nightly `--live` scorecard within threshold of the stored baseline (non-blocking; no prompt-drift regression on the seeded golden set)
- [ ] `agents/guides/security/ai-risk-standards-map.md` present and validated: **every OWASP LLM01–LLM10 row maps to ≥1 named GABBE skill/gate/persona**
- [ ] `prompt-injection-defense` + `output-validation` skills registered in `00-index.md` and reachable from `ai-safety-guardrails.skill.md`

## 10. Published library — one-command install, autodetect, multi-OS, reversible (Track E8)

```bash
pytest scripts/tests/test_autodetect.py scripts/tests/test_one_command_install.py -v
```

- [ ] `test_autodetect.py` + `test_one_command_install.py` pass (each channel's single command lands the kit into a tmp target; autodetect populates `.gabbe/manifest.json`)
- [ ] `release-verify` installs the **published** package (npm / PyPI / raw URL) on the OS matrix and passes the same smoke checks (single-command install → `gabbe doctor` → emit → `update` → `uninstall` → byte-identical restore)
- [ ] Unknown / absent agents are skipped cleanly (never error)

---

**Definition of done for v1.0:** items 1–10 all green on a clean checkout and in
CI. No item may be waived.
