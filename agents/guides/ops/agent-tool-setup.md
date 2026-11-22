# Agent Tool Setup

> Read this when you set up or debug how a coding tool finds the kit. It is not loaded at session start.
> Everything below is what `bin/install.js` (the npm installer) and `scripts/init.py` (the wizard) write.
> It says nothing about how a vendor's tool behaves. For that, read the tool's own current documentation.

## What the installers write

The kit's rules live in `agents/AGENTS.md`. Each tool gets a pointer to it, a relative symlink where the
system allows one and a copy where it does not. Both installers keep a file or link you already had
(see "Your own files" below).

| Tool (installer name) | Instruction file written | Skills written |
|---|---|---|
| Claude Code | `.claude/CLAUDE.md` | `.claude/skills/<slug>/SKILL.md` |
| Cursor | `.cursorrules` | `.cursor/rules/<slug>.mdc` (npm) |
| Windsurf | `.windsurfrules`, and a link to `AGENTS.md` inside `.windsurf/skills/` (npm) | `.windsurf/skills/<slug>/SKILL.md` |
| Cline | `.clinerules` | `.cline/skills/<slug>/SKILL.md` |
| Devin / Cognition | `.devinrules` | `.devin/skills/<slug>/SKILL.md` |
| Aider | `.aider.conf.yml` with `read:` for `agents/AGENTS.md` and `agents/skills/` | none |
| Gemini | `GEMINI.md` (link) and `.gemini/settings.json` (a JSON file, not a link) | none |
| Antigravity | root `AGENTS.md` | `.agents/skills/<slug>/SKILL.md` |
| OpenCode | `opencode.json` with an `instructions` array | `.agents/skills/<slug>/SKILL.md` |
| Zed | `.rules` | none |
| Continue | `.continue/rules/agents.md` | none |
| Roo Code | `.roo/rules/agents.md` | none |
| Kilo Code | `.kilocode/rules/agents.md` | none |
| OpenAI / Codex | `.codex/AGENTS.md` | none |
| GitHub Copilot | `.github/copilot-instructions.md` | `.github/skills/<slug>/SKILL.md` |
| VS Code | none | `.github/skills/<slug>/SKILL.md` |

The wizard also writes a root `AGENTS.md` link (the agents.md convention) once, for all tools.
The list of tools the installers know is in the `--agents` help of `npx gabbe-kit init --help`.

Notes that follow from the code:

- `.gemini/settings.json` holds three kit keys: `agent_instructions_file`, `skills_directory` and
  `contextFileName` (`GEMINI.md`). The kit writes it only when it is absent; an existing one is left alone.
  Whether the Gemini tool reads those keys is the tool's business; the kit only writes them.
- Claude Code discovers `<slug>/SKILL.md` folders, so the installers generate those. They do not link the
  source `agents/skills/*.skill.md` tree for it.
- `opencode.json` is written only when absent.
- The skills folders hold generated copies. After you change a skill in `agents/skills/`, rerun the installer
  (or `agents/scripts/setup-context.sh`) so the copies follow.

## Your own files

If a tool's instruction file already exists and is yours, the npm installer keeps it and adds a pointer
block to the kit's `agents/AGENTS.md`. If the file is a link of yours, it leaves it and says so; point it
at the kit yourself. `npx gabbe-kit init --force` replaces such files with the kit's link; it moves yours
to a backup name first. `gabbe uninstall` reverses an install from the manifest it recorded. Read the
installer's output: it says for each file what it did.

## What you do in each tool

These are conventions the kit asks of agents. None is enforced by the kit.

- Claude Code: invoke a skill by its slug as a slash command if the tool lists it. If the skill menu is
  cut short, read `agents/skills/00-index-lite.md` and open the skill file. Task lists are the tool's own;
  the kit's task file is `project/TASKS.md`.
- Cursor, Copilot, Windsurf and other rule-based tools: name the skill file in the conversation, or open it,
  before you ask for the work.
- Any tool: the kit's memory is plain files in `agents/memory/`. They work in every tool.

## MCP servers

`agents/templates/core/MCP_CONFIG_TEMPLATE.json` is a starting list of MCP servers (it names a library
documentation server, `context7`, among others). Copy it into your tool's MCP configuration only for the
servers you will use. Where your tool's own configuration location is different, follow the tool's
documentation. A library documentation server helps when you use a library you do not know well. It is not
required for every project.

## Check the wiring

```bash
ls -l .claude/CLAUDE.md .cursorrules GEMINI.md 2>/dev/null     # links point to agents/AGENTS.md
python3 agents/scripts/validate_links.py                       # kit links resolve
gabbe doctor                                                   # if the CLI is installed
```

A dangling link (the target moved) is the usual fault. Rerun the installer to rewrite it.
