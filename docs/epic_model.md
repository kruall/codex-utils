# Epic Data Model

This document describes the structure of the **Epic** entity used by the task manager.

## Fields
- `id` - unique identifier (`epic-<number>`)
- `title` - short description
- `description` - detailed description
- `status` - either `open` or `done`
- `created_at` - creation timestamp
- `updated_at` - last modification timestamp
- `child_tasks` - list of task IDs contained in the epic
- `child_epics` - list of sub-epic IDs
- `parent_epic` - optional parent epic ID for reverse lookup

## Storage Layout
Epics are saved in the `.epics/` directory at the repository root. Each epic is
stored as a JSON file named `<epic-id>.json` using the fields defined above.

```text
.epics/
  epic-1.json
  epic-2.json
  ...
```

This flat structure mirrors the task storage convention and will be used by the
persistence layer implemented in later tasks.
