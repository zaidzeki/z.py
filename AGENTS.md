# AGENTS Instructions

## General workflow requirements
- Any explicit instruction given in a message to overwrite a rule here must be respected.
- When updating UI, always show a preview (multiple previews if possible).
- When training AI models, show graphs, training loss, and performance metrics.
- When done writing code, run formatters for all changed code.
- Run linters and formatters after writing code.
- If you can't fix a lint issue write it in the `AGENT_NOTES.md`.
- Use semantic versioning and increase the version whenever you make changes:
  - `<major>.<minor>.<patch>`
  - simple fixes => patch increase
  - feature implementations => minor increase
  - backward incompatible changes => major increase
  - explicitly being told to increase major after a new feature => major increase
- Ensure these files exist in all projects: `AGENT_NOTES.md`, `BACKLOG.md`, `CHANGELOG.md`, `DESIGN.md`, `README.md`.
- Keep filenames uppercase (extensions may vary).
- Create a link `agents.md` to `AGENTS.md`.

## Files
- `AGENT_NOTES.md` - concise persistent memory; always read/write when discovering project facts.
- `BACKLOG.md` - append-only list of future improvements.
- `CHANGELOG.md` - list all changes with versioning and GMT+3 timestamp.
- `DESIGN.md` - design-related information.
- `README.md`.

## Instructions for Web Apps
- Use playwright/selenium to test each UI.
- All referenced web assets must be kept as offline assets for immediate, no-network setup.

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
- Display graphs for training loss, performance, and related metrics very verbosely.
