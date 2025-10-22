const fs = require('fs-extra');
const path = require('path');
const chalk = require('chalk');
const ora = require('ora');
const inquirer = require('inquirer');
const { execFileSync } = require('child_process');
const { validatePath } = require('../utils/security');

async function initCommand(options) {
  console.log(chalk.blue.bold('\n🚀 Initializing Roo Skills in your project...\n'));

  // SECURITY: Validate and resolve target directory
  let targetDir;
  try {
    targetDir = validatePath(options.dir || '.', process.cwd());
  } catch (error) {
    console.error(chalk.red('\n✗ Invalid directory:'), error.message);
    process.exit(1);
  }
  
  // Check if already initialized
  const roomodesPath = path.join(targetDir, '.roomodes');
  const rooSkillsPath = path.join(targetDir, '.roo', 'skills');
  
  if (fs.existsSync(roomodesPath) || fs.existsSync(rooSkillsPath)) {
    const { overwrite } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'overwrite',
        message: 'Roo Skills appears to already be initialized. Overwrite?',
        default: false
      }
    ]);
    
    if (!overwrite) {
      console.log(chalk.yellow('❌ Initialization cancelled.'));
      return;
    }
  }

  const packageRoot = path.join(__dirname, '..', '..');

  try {
    // SECURITY: Ensure target directory exists and is writable
    await fs.ensureDir(targetDir);

    // Copy files with proper error handling
    const filesToCopy = [
      {
        src: path.join(packageRoot, '.roomodes'),
        dest: path.join(targetDir, '.roomodes'),
        name: '.roomodes configuration',
      },
      {
        src: path.join(packageRoot, '.roo', 'skills'),
        dest: path.join(targetDir, '.roo', 'skills'),
        name: 'skills directory',
      },
      {
        src: path.join(packageRoot, '.roo', 'commands'),
        dest: path.join(targetDir, '.roo', 'commands'),
        name: 'commands directory',
      },
      {
        src: path.join(packageRoot, 'agent_skills_spec.md'),
        dest: path.join(targetDir, 'agent_skills_spec.md'),
        name: 'agent skills specification',
      },
      {
        src: path.join(packageRoot, 'coding-agent-docs'),
        dest: path.join(targetDir, 'coding-agent-docs'),
        name: 'coding agent documentation',
      },
    ];

    for (const file of filesToCopy) {
      const spinner = ora(`Copying ${file.name}...`).start();
      try {
        await fs.copy(file.src, file.dest, {
          overwrite: true,
          errorOnExist: false,
        });
        spinner.succeed(chalk.green(`✓ ${file.name} copied`));
      } catch (error) {
        spinner.fail(chalk.red(`✗ Failed to copy ${file.name}`));
        throw new Error(`Failed to copy ${file.name}: ${error.message}`);
      }
    }

    // Copy .env.example if it doesn't exist
    const envExamplePath = path.join(targetDir, '.env.example');
    if (!(await fs.pathExists(envExamplePath))) {
      const spinner = ora('Creating .env.example...').start();
      try {
        await fs.copy(
          path.join(packageRoot, '.env.example'),
          envExamplePath
        );
        spinner.succeed(chalk.green('✓ .env.example created'));
      } catch (error) {
        spinner.warn(chalk.yellow('⚠ Could not create .env.example'));
      }
    }


    // Check for Python and offer to install dependencies
    if (options.install) {
      const { installPython } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'installPython',
          message: 'Install Python dependencies for skill generation?',
          default: true
        }
      ]);

      if (installPython) {
        const spinner = ora('Installing Python dependencies...').start();
        try {
          const requirementsPath = path.join(
            targetDir,
            '.roo',
            'skills',
            'scripts',
            'agent-skill-generator',
            'requirements.txt'
          );
          
          // SECURITY FIX: Use execFileSync instead of execSync to prevent shell injection
          execFileSync('pip', ['install', '-r', requirementsPath], {
            cwd: targetDir,
            stdio: 'pipe',
            timeout: 120000, // 2 minute timeout
          });
          spinner.succeed(chalk.green('✓ Python dependencies installed'));
        } catch (error) {
          spinner.fail(chalk.yellow('⚠ Failed to install Python dependencies'));
          console.log(chalk.yellow('  You can install them manually later with:'));
          console.log(chalk.gray('  pip install -r .roo/skills/scripts/agent-skill-generator/requirements.txt'));
          
          if (error.code === 'ETIMEDOUT') {
            console.log(chalk.yellow('  (Installation timed out - may need to run manually)'));
          }
        }
      }
    }

    // Success message
    console.log(chalk.green.bold('\n✨ Roo Skills initialized successfully!\n'));
    console.log(chalk.cyan('Next steps:'));
    console.log('  1. Copy .env.example to .env and add your API keys');
    console.log('  2. Restart Roo Code to auto-detect .roomodes configuration');
    console.log('  3. Use slash commands from .roo/commands/ in Roo Code');
    console.log('  4. Start using skills in your Roo Code workspace\n');
    console.log(chalk.gray('Generate a new skill:'));
    console.log(chalk.gray('  rooskills generate <documentation-url> [skill-name]\n'));
    console.log(chalk.gray('List available skills:'));
    console.log(chalk.gray('  rooskills list\n'));
    console.log(chalk.cyan('💡 Activate skills: Mention skill name in chat or use Roo Code mode selector\n'));

  } catch (error) {
    console.error(chalk.red('\n❌ Error during initialization:'), error.message);
    process.exit(1);
  }
}

module.exports = { initCommand };
