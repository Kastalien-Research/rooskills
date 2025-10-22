const fs = require('fs-extra');
const path = require('path');
const chalk = require('chalk');
const ora = require('ora');
const inquirer = require('inquirer');
const { execSync } = require('child_process');

async function initCommand(options) {
  console.log(chalk.blue.bold('\n🚀 Initializing Roo Skills in your project...\n'));

  const targetDir = path.resolve(options.dir);
  
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
    // Copy .roomodes file
    let spinner = ora('Copying .roomodes configuration...').start();
    await fs.copy(
      path.join(packageRoot, '.roomodes'),
      path.join(targetDir, '.roomodes')
    );
    spinner.succeed(chalk.green('✓ .roomodes configuration copied'));

    // Copy .roo/skills directory
    spinner = ora('Copying skills directory...').start();
    await fs.copy(
      path.join(packageRoot, '.roo', 'skills'),
      path.join(targetDir, '.roo', 'skills')
    );
    spinner.succeed(chalk.green('✓ Skills directory copied'));

    // Copy .roo/commands directory
    spinner = ora('Copying commands directory...').start();
    await fs.copy(
      path.join(packageRoot, '.roo', 'commands'),
      path.join(targetDir, '.roo', 'commands')
    );
    spinner.succeed(chalk.green('✓ Commands directory copied'));

    // Copy .env.example if it doesn't exist
    const envExamplePath = path.join(targetDir, '.env.example');
    if (!fs.existsSync(envExamplePath)) {
      spinner = ora('Creating .env.example...').start();
      await fs.copy(
        path.join(packageRoot, '.env.example'),
        envExamplePath
      );
      spinner.succeed(chalk.green('✓ .env.example created'));
    }

    // Copy agent_skills_spec.md
    spinner = ora('Copying agent skills specification...').start();
    await fs.copy(
      path.join(packageRoot, 'agent_skills_spec.md'),
      path.join(targetDir, 'agent_skills_spec.md')
    );
    spinner.succeed(chalk.green('✓ Agent skills specification copied'));
    // Copy coding-agent-docs directory
    spinner = ora('Copying coding agent documentation...').start();
    await fs.copy(
      path.join(packageRoot, 'coding-agent-docs'),
      path.join(targetDir, 'coding-agent-docs')
    );
    spinner.succeed(chalk.green('✓ Coding agent documentation copied'));


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
        spinner = ora('Installing Python dependencies...').start();
        try {
          const requirementsPath = path.join(
            targetDir,
            '.roo',
            'skills',
            'scripts',
            'agent-skill-generator',
            'requirements.txt'
          );
          
          execSync(`pip install -r "${requirementsPath}"`, {
            cwd: targetDir,
            stdio: 'pipe'
          });
          spinner.succeed(chalk.green('✓ Python dependencies installed'));
        } catch (error) {
          spinner.fail(chalk.yellow('⚠ Failed to install Python dependencies'));
          console.log(chalk.yellow('  You can install them manually later with:'));
          console.log(chalk.gray(`  pip install -r .roo/skills/scripts/agent-skill-generator/requirements.txt`));
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
