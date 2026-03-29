# AGENTS Instructions

## General workflow requirements
- When updating UI, always show a preview (multiple previews if possible).
- When training AI models, show graphs, training loss, and performance metrics.
- When done writing code, run formatters for all changed code.

## General Instructions
### Rules
- Any explicit instruction given in a message to overwrite a rule here must be respected.
- Run linters and formatters after writing code.
- If you can't fix a lint issue write it in the `AGENT_NOTES.md`.
- Use semantic versioning and increase the version number whenever you make changes.
  - `<major>.<minor>.<patch>`
  - Simple fixes get a patch increase.
  - Feature implementations get a minor increase.
  - Backward incompatible / breaking changes get a major increase.
  - Explicitly being told to increase the major after implementing a new feature increases the major.
- All the files below must be available in all projects. Please use all caps for the filenames (not the extensions).
- Create a link `agents.md` to `AGENTS.md` to support different implementations but keep the same file.

### Files
- `AGENT_NOTES.md` - keep concise memory of lessons learned; always read and write when discovering project details.
- `BACKLOG.md` - list ideas for future improvements and append while implementing features/fixes.
- `CHANGELOG.md` - list all changes with versioning and GMT+3 timestamp.
- `DESIGN.md` - design information.
- `README.md`

## Instructions for Web Apps
- Use Playwright / Selenium to test each UI.
- All assets must be included in the repo for immediate no-network setup.

## Flask module organization
Use this structure for Flask projects:

```text
app/
<module_1>/
<module_2>/
...
static/<module_1>/        # only for custom css and js
static/<module_2>/        # only for custom css and js
templates/<module_1>/
templates/<module_2>/

static/vendors/<vendor_name>/  # for third party libraries
```

## Instructions for AI training
- Display graphs for training loss, performance, and other related information very verbosely.

## Asset policy
- All referenced web assets must be kept as offline assets for immediate, no-network setup.

## Skills
A skill is a set of local instructions to follow that is stored in a `SKILL.md` file. Below is the list of skills that can be used. Each entry includes a name, description, and file path so you can open the source for full instructions when using a specific skill.

### Available skills
- skill-creator: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Codex's capabilities with specialized knowledge, workflows, or tool integrations. (file: /opt/codex/skills/.system/skill-creator/SKILL.md)
- skill-installer: Install Codex skills into $CODEX_HOME/skills from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill from another repo (including private repos). (file: /opt/codex/skills/.system/skill-installer/SKILL.md)

### How to use skills
- Discovery: The list above is the skills available in this session (name + description + file path). Skill bodies live on disk at the listed paths.
- Trigger rules: If the user names a skill (with `$SkillName` or plain text) OR the task clearly matches a skill's description shown above, you must use that skill for that turn. Multiple mentions mean use them all. Do not carry skills across turns unless re-mentioned.
- Missing/blocked: If a named skill isn't in the list or the path can't be read, say so briefly and continue with the best fallback.
- How to use a skill (progressive disclosure):
  1) After deciding to use a skill, open its `SKILL.md`. Read only enough to follow the workflow.
  2) When `SKILL.md` references relative paths (e.g., `scripts/foo.py`), resolve them relative to the skill directory listed above first, and only consider other paths if needed.
  3) If `SKILL.md` points to extra folders such as `references/`, load only the specific files needed for the request; don't bulk-load everything.
  4) If `scripts/` exist, prefer running or patching them instead of retyping large code blocks.
  5) If `assets/` or templates exist, reuse them instead of recreating from scratch.
- Coordination and sequencing:
  - If multiple skills apply, choose the minimal set that covers the request and state the order you'll use them.
  - Announce which skill(s) you're using and why (one short line). If you skip an obvious skill, say why.
- Context hygiene:
  - Keep context small: summarize long sections instead of pasting them; only load extra files when needed.
  - Avoid deep reference-chasing: prefer opening only files directly linked from `SKILL.md` unless you're blocked.
  - When variants exist (frameworks, providers, domains), pick only the relevant reference file(s) and note that choice.
- Safety and fallback: If a skill can't be applied cleanly (missing files, unclear instructions), state the issue, pick the next-best approach, and continue.
