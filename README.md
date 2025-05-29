# codex-utils

A collection of tools for managing development tasks.

## Task Manager CLI

The `tm` script provides a lightweight interface for tracking work. All data is stored in the `.tasks/` directory.

### Textual UI
Launch the interactive Textual interface:
```bash
./tm ui
```

### Queue Management
```bash
# List available queues
./tm queue list

# Create a new queue
./tm queue add --name "feature-queue" --title "Feature Development" --description "Queue for new features"

# Delete a queue
./tm queue delete --name "feature-queue"
```

### Task Management
```bash
# List tasks
./tm task list

# Filter tasks
./tm task list --status todo
./tm task list --queue feature-queue

# Create a task
./tm task add --title "Implement user auth" --description "Add authentication system" --queue feature-queue

# Show task details
./tm task show --id feature-queue-1

# Update fields
./tm task update --id feature-queue-1 --field title --value "Updated title"
./tm task update --id feature-queue-1 --field status --value in_progress

# Start or finish work
./tm task start --id feature-queue-1
./tm task done --id feature-queue-1

# Delete a task
./tm task delete --id feature-queue-1
```

### Comment System
```bash
# Add a comment
./tm task comment add --id feature-queue-1 --comment "Started implementation"

# List comments
./tm task comment list --id feature-queue-1

# Remove a comment
./tm task comment remove --id feature-queue-1 --comment-id 1
```

### Task Links
```bash
# Add a related link between tasks
./tm task link add --id feature-queue-1 --target-id feature-queue-2

# List links for a task
./tm task link list --id feature-queue-1

# Remove a link
./tm task link remove --id feature-queue-1 --target-id feature-queue-2
```

### Typical Workflow
1. **Create a queue**: `./tm queue add --name "my-queue" --title "My Queue" --description "Description"`.
2. **Add a task**: `./tm task add --title "Task title" --description "Description" --queue my-queue`.
3. **Start the task**: `./tm task start --id my-queue-1`.
4. **Add progress comments**: `./tm task comment add --id my-queue-1 --comment "Progress update"`.
5. **Mark completion**: `./tm task done --id my-queue-1`.

### Running Without Internet
Set `TM_NO_INSTALL=1` when invoking the script to skip package installation in offline environments:
```bash
TM_NO_INSTALL=1 ./tm task list
```

### Static Dashboard
Generate an HTML dashboard listing all tasks:

```bash
./tm dashboard
```

The page is written to `docs/index.html` and can be published with GitHub Pages.
This repository includes a GitHub Actions workflow that automatically deploys
the `docs/` folder to GitHub Pages whenever changes are pushed to `main`.


### React Dashboard
A Next.js frontend under `react-dashboard/` renders tasks. The task list, kanban board, and individual task view are available on separate pages.
Navigate to `/task/<task-id>` to view and edit a single task.
To develop locally:
```bash
cd react-dashboard
npm install
npm run dev
```
Use `npm run build` to generate a static site in `out/` for GitHub Pages deployment.

