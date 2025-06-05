const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

function findPythonExecutable() {
  const venvPython = path.join(__dirname, '..', '..', '.venv', 'bin', 'python');
  if (fs.existsSync(venvPython)) {
    return venvPython;
  }

  const systemPythons = ['python3', 'python'];
  for (const pythonCmd of systemPythons) {
    try {
      execFileSync('which', [pythonCmd], { stdio: 'pipe' });
      return pythonCmd;
    } catch (_) {}
  }

  throw new Error('No Python executable found');
}

function generateEpicsJson() {
  const tasksRoot = path.join(__dirname, '..', '..', '.tasks');
  const epicsRoot = path.join(__dirname, '..', '..', '.epics');
  const outputPath = path.join(__dirname, '..', 'public', 'epics.json');
  const taskManagerDir = path.join(__dirname, '..', '..', 'task-manager');

  try {
    const pythonPath = findPythonExecutable();
    console.log(`Using Python: ${pythonPath}`);

    const args = [
      '-m',
      'task_manager.export_epics',
      '--tasks-root',
      tasksRoot,
      '--epics-root',
      epicsRoot,
      '--output',
      outputPath,
    ];

    execFileSync(pythonPath, args, {
      stdio: 'inherit',
      cwd: taskManagerDir,
    });
  } catch (error) {
    console.error('Error executing Python script:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  generateEpicsJson();
}

module.exports = { generateEpicsJson };

