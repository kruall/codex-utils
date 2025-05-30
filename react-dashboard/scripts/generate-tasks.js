const { execFileSync } = require('child_process');
const path = require('path');

function generateTasksJson() {
  const tasksRoot = path.join(__dirname, '..', '..', '.tasks');
  const outputPath = path.join(__dirname, '..', 'public', 'tasks.json');
  const scriptPath = path.join(__dirname, '..', '..', 'task-manager', 'task_manager', 'export_json.py');

  try {
    execFileSync('python', [scriptPath, '--tasks-root', tasksRoot, '--output', outputPath], { stdio: 'inherit' });
  } catch (error) {
    console.error('Error executing Python script:', error.message);
    process.exit(1); // Exit with a non-zero status code to indicate failure
  }
}

if (require.main === module) {
  generateTasksJson();
}

module.exports = { generateTasksJson };
