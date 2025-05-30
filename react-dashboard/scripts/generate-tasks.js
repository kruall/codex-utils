const { execFileSync } = require('child_process');
const path = require('path');

function generateTasksJson() {
  const tasksRoot = path.join(__dirname, '..', '..', '.tasks');
  const outputPath = path.join(__dirname, '..', 'public', 'tasks.json');
  const taskManagerDir = path.join(__dirname, '..', '..', 'task-manager');
  const pythonPath = path.join(__dirname, '..', '..', '.venv', 'bin', 'python');

  try {
    // Run as a module from the task-manager directory using venv python
    execFileSync(pythonPath, ['-m', 'task_manager.export_json', '--tasks-root', tasksRoot, '--output', outputPath], { 
      stdio: 'inherit',
      cwd: taskManagerDir
    });
  } catch (error) {
    console.error('Error executing Python script:', error.message);
    process.exit(1); // Exit with a non-zero status code to indicate failure
  }
}

if (require.main === module) {
  generateTasksJson();
}

module.exports = { generateTasksJson };
