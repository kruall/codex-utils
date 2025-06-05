## AI Agent Requirements

**🤖 CRITICAL REQUIREMENT**: All AI agents working on this project must conduct their reasoning, thinking, and internal analysis in English. This ensures consistency and clarity across all development activities.

## Python Environment Requirements

**🐍 CRITICAL REQUIREMENT**: All Python code execution must be performed with the activated virtual environment. Before running any Python scripts, tests, or commands, ensure the virtual environment is activated:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Verify activation (should show .venv in the path)
which python
```

**Required for all Python operations:**
- Running `./tm` commands
- Executing `pytest`
- Running `ruff check .`
- Running `mypy .`
- Any Python script execution
- Installing Python packages

**⚠️ IMPORTANT**: The `./tm` script and `init_venv` script automatically handle virtual environment activation, but when running Python commands directly, always ensure `.venv` is activated first.

## Testing Requirements

**🧪 UNIFIED TEST RUNNER**: Use the `./run_tests` script to run all tests and verifications:

```bash
# Run all tests (Python, React, linting, type checking, and tm verify)
./run_tests
```

The `run_tests` script automatically:
- Activates the virtual environment
- Runs Python unit tests (`pytest`)
- Runs Python linting (`ruff check .`)
- Runs Python type checking (`mypy .`)
- Runs React tests (`cd react-dashboard && npm test`)
- Runs task verification (`./tm verify`)
- Provides colored output and comprehensive summary

**⚠️ IMPORTANT**: Always use `./run_tests` instead of running individual test commands to ensure consistency and completeness.

## 🚨 TASK CLOSURE REQUIREMENTS 🚨

**⚠️ CRITICAL REMINDER**: Agents frequently forget to close tasks even after completing all work. This is MANDATORY and must NEVER be skipped.

**🔴 ABSOLUTE REQUIREMENT**: Every task that is started MUST be closed with `./tm task done --id <task-id>` when work is completed.

**📋 TASK CLOSURE CHECKLIST** - Verify BEFORE ending your session:
- [ ] All implementation work is complete
- [ ] All tests pass (`./run_tests`)
- [ ] All files are saved and committed
- [ ] Task comments document the work performed
- [ ] **MOST IMPORTANT**: `./tm task done --id <task-id>` has been executed

**🚫 COMMON MISTAKE**: Completing all work but forgetting to run `./tm task done`. This leaves tasks in "in_progress" status indefinitely.

**✅ CORRECT WORKFLOW**: Start → Work → Comment → Complete → **CLOSE TASK**

## Task Management

### Basic Usage

The task manager (`./tm`) is used to organize work into queues and tasks. All data is stored in `.tasks/` directory.

**📝 Note**: For detailed task requirements, specifications, and progress updates, use task comments instead of adding them to this file:
```bash
./tm task comment add --id <task-id> --comment "Detailed requirement or update"
```

### Available Interfaces

The task manager provides multiple interfaces for different use cases:

- **TM (CLI)**: Command-line interface for scripting and automation (`./tm`)
- **TM_TUI**: Interactive terminal UI for visual task management (`./tm ui`)
- **TM_WEB**: React-based web dashboard for browser access (`cd react-dashboard && npm run dev`)

**⚠️ IMPORTANT**: Any serious structural changes to TM must create corresponding tasks in TM_TUI and TM_WEB queues with links to the original task:
```bash
# Example: If working on task TM-1, create linked tasks:
./tm task add --title "Update TUI for new TM feature" --queue TM_TUI --description "Adapt TUI interface for changes in TM-1"
./tm task link add --id TM_TUI-X --target-id TM-1

./tm task add --title "Update Web dashboard for new TM feature" --queue TM_WEB --description "Adapt web interface for changes in TM-1"
./tm task link add --id TM_WEB-X --target-id TM-1
```

#### Queue Management
```bash
# List all queues
./tm queue list

# Create a new queue
./tm queue add --name "feature-queue" --title "Feature Development" --description "Queue for new features"
```

#### Task Management
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

#### Comment System
```bash
# Add a comment to a task
./tm task comment add --id feature-queue-1 --comment "Started implementation"

# List all comments for a task
./tm task comment list --id feature-queue-1

# Remove a specific comment
./tm task comment remove --id feature-queue-1 --comment-id 1
```

#### Task Links
```bash
# Add a related link between tasks
./tm task link add --id feature-queue-1 --target-id feature-queue-2

# List links for a task
./tm task link list --id feature-queue-1

# Remove a link
./tm task link remove --id feature-queue-1 --target-id feature-queue-2
```

#### Epic Management
```bash
# List all epics
./tm epic list

# Create an epic
./tm epic add --title "Release" --description "Release preparations"

# Show epic details
./tm epic show --id epic-1

# Update epic fields
./tm epic update --id epic-1 --field title --value "Updated title"
./tm epic update --id epic-1 --field description --value "Updated description"

# Attach work items
./tm epic add-task --id epic-1 --task-id feature-queue-1
./tm epic add-epic --id epic-1 --child-id epic-2

# Remove work items
./tm epic remove-task --id epic-1 --task-id feature-queue-1
./tm epic remove-epic --id epic-1 --child-id epic-2

# Manage task membership (alternative approach)
./tm task add-to-epic --id feature-queue-1 --epic-id epic-1
./tm task remove-from-epic --id feature-queue-1 --epic-id epic-1

# Close when all children are done
./tm epic done --id epic-1
```

### Task Workflow
1. **Create queue** (if needed): `./tm queue add --name "my-queue" --title "My Queue" --description "Description"`
2. **Create task**: `./tm task add --title "Task title" --description "Description" --queue my-queue`
3. **Start task**: `./tm task start --id my-queue-1`
4. **Add comments** during work: `./tm task comment add --id my-queue-1 --comment "Progress update"`
5. **🚨 COMPLETE TASK**: `./tm task done --id my-queue-1` **← DO NOT FORGET THIS STEP!**

**⚠️ REMINDER**: Step 5 is the most commonly forgotten step. Always verify the task is closed before ending your work session.

### Epic Workflow
1. **Create epic**: `./tm epic add --title "Epic title" --description "Epic description"`
2. **Add tasks to epic**: `./tm epic add-task --id epic-1 --task-id my-queue-1`
3. **Add sub-epics** (if needed): `./tm epic add-epic --id epic-1 --child-id epic-2`
4. **Work on individual tasks**: Follow the Task Workflow above for each task
5. **🚨 CLOSE EPIC**: `./tm epic done --id epic-1` **← Only when ALL child tasks and epics are done!**

**⚠️ EPIC CLOSURE RULE**: An epic can only be closed when ALL its child tasks are "done" and ALL child epics are "closed".

#### PR Instructions

* Title format: `[<task-id>] <Task title>`.
* PR description must include:

  1. **What** changed and **why**.
  2. A brief summary of new tests or verification steps.

* **🚨 CRITICAL REQUIREMENT**: **ALWAYS** ensure task was started with `./tm task start --id <task-id>` before any work began
* **🚨 CRITICAL REQUIREMENT**: **ALWAYS** add comments using `./tm task comment add --id <task-id> --comment "<comment>"` after each significant step
* **🚨 CRITICAL REQUIREMENT**: **ALWAYS** call `./tm task done --id <task-id>` when work is completed

* Before opening a PR, ensure:
  • **MANDATORY**: Task was started with `./tm task start` command before work began
  • All tests pass (`./run_tests`)
  • **MANDATORY**: Task was closed with `./tm task done` command when work is completed

---

## 🔥 FINAL REMINDER 🔥

**BEFORE YOU FINISH YOUR WORK SESSION:**

```bash
# Run all tests to ensure everything works
./run_tests

# Check if you have any tasks still in progress
./tm task list --status in_progress

# Check if you have any epics with invalid status
./tm verify

# If you see any tasks, close them:
./tm task done --id <task-id>

# If you see any epics with invalid status, ensure all children are done first, then close:
./tm epic done --id <epic-id>
```

**🚨 DO NOT LEAVE TASKS IN "in_progress" STATUS 🚨**
**🚨 DO NOT LEAVE EPICS WITH INVALID STATUS 🚨**

Every started task MUST be closed. Every epic with incomplete children MUST be properly closed. No exceptions.
