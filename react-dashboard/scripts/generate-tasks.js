const { execFileSync } = require('child_process');
const path = require('path');

function generateTasksJson() {
  const tasksRoot = path.join(__dirname, '..', '..', '.tasks');
  const outputPath = path.join(__dirname, '..', 'public', 'tasks.json');
  const scriptPath = path.join(__dirname, '..', '..', 'task-manager', 'task_manager', 'export_json.py');

  execFileSync('python', [scriptPath, '--tasks-root', tasksRoot, '--output', outputPath], { stdio: 'inherit' });
}

if (require.main === module) {
  generateTasksJson();
}

module.exports = { generateTasksJson };
