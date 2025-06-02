const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

function findPythonExecutable() {
  // Try virtual environment first (for local development)
  const venvPython = path.join(__dirname, '..', '..', '.venv', 'bin', 'python');
  if (fs.existsSync(venvPython)) {
    return venvPython;
  }
  
  // Try system python executables (for CI environments)
  const systemPythons = ['python3', 'python'];
  for (const pythonCmd of systemPythons) {
    try {
      execFileSync('which', [pythonCmd], { stdio: 'pipe' });
      return pythonCmd;
    } catch (error) {
      // Continue to next option
    }
  }
  
  throw new Error('No Python executable found');
}

function generateTasksJson() {
  const tasksRoot = path.join(__dirname, '..', '..', '.tasks');
  const outputPath = path.join(__dirname, '..', 'public', 'tasks.json');
  const taskManagerDir = path.join(__dirname, '..', '..', 'task-manager');

  try {
    const pythonPath = findPythonExecutable();
    console.log(`Using Python: ${pythonPath}`);
    
    // Run as a module from the task-manager directory
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
