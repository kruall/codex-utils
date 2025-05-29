#### Task Management

## Basic Usage

The task manager (`./tm`) is used to organize work into queues and tasks. All data is stored in `.tasks/` directory.

**📝 Note**: For detailed task requirements, specifications, and progress updates, use task comments instead of adding them to this file:
```bash
./tm task comment add --id <task-id> --comment "Detailed requirement or update"
```

### Queue Management
```bash
# List all queues
./tm queue list

# Create a new queue
./tm queue add --name "feature-queue" --title "Feature Development" --description "Queue for new features"
```

### Task Management
```bash
# List all tasks
./tm task list

# List tasks by status or queue
./tm task list --status todo
./tm task list --queue feature-queue

# Create a new task
./tm task add --title "Implement user auth" --description "Add authentication system" --queue feature-queue

# Show task details
./tm task show --id feature-queue-1

# Update task fields
./tm task update --id feature-queue-1 --field title --value "Updated title"
./tm task update --id feature-queue-1 --field status --value in_progress

# Start working on a task
./tm task start --id feature-queue-1

# Mark task as completed
./tm task done --id feature-queue-1
```

### Comment System
```bash
# Add a comment to a task
./tm task comment add --id feature-queue-1 --comment "Started implementation"

# List all comments for a task
./tm task comment list --id feature-queue-1

# Remove a specific comment
./tm task comment remove --id feature-queue-1 --comment-id 1
```

### Task Workflow
1. **Create queue** (if needed): `./tm queue add --name "my-queue" --title "My Queue" --description "Description"`
2. **Create task**: `./tm task add --title "Task title" --description "Description" --queue my-queue`
3. **Start task**: `./tm task start --id my-queue-1`
4. **Add comments** during work: `./tm task comment add --id my-queue-1 --comment "Progress update"`
5. **Complete task**: `./tm task done --id my-queue-1`


#### PR Instructions

* Title format: `[<task-id>] <Concise description>`.
* PR description must include:

  1. **What** changed and **why**.
  2. A brief summary of new tests or verification steps.

* **🚨 CRITICAL REQUIREMENT**: **ALWAYS** ensure task was started with `./tm task start --id <task-id>` before any work began
* **🚨 CRITICAL REQUIREMENT**: **ALWAYS** add comments using `./tm task comment add --id <task-id> --comment "<comment>"` after each significant step
* **🚨 CRITICAL REQUIREMENT**: **ALWAYS** call `./tm task done --id <task-id>` when work is completed

 
* Before opening a PR, ensure:
  • **MANDATORY**: Task was started with `./tm task start` command before work began
  • `pytest` passes,
  • `ruff check .` passes,
  • `mypy .` passes
