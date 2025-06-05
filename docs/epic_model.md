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

## CLI Usage
The `tm` command offers helpers for managing epics from the command line:

```bash
# Create and list epics
./tm epic add --title "Release" --description "Release tasks"
./tm epic list

# Relate tasks or sub epics
./tm epic add-task --id epic-1 --task-id q-1
./tm epic add-epic --id epic-1 --child-id epic-2

# Close an epic when all children are done
./tm epic done --id epic-1
```

## EpicManager Service

Epic operations are handled by a dedicated `EpicManager` service class. This
object encapsulates persistence and lookup logic so higher level components only
interact with its public API.

```python
from pathlib import Path
from task_manager.epic_manager import EpicManager

manager = EpicManager(Path('.epics'))
for epic in manager.list_epics():
    print(epic['id'], epic['title'])
```
