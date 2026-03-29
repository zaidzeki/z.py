# AGENTS Instructions

## General workflow requirements
- When updating UI, always show a preview (multiple previews if possible).
- When training AI models, show graphs, training loss, and performance metrics.
- When done writing code, run formatters for all changed code.

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

## Asset policy
- All referenced web assets must be kept as offline assets for immediate, no-network setup.
