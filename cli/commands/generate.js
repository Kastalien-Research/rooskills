const { execSync } = require('child_process');
const path = require('path');
const chalk = require('chalk');
const ora = require('ora');

async function generateCommand(url, skillName, options) {
  console.log(chalk.blue.bold('\n🔧 Generating new skill from documentation...\n'));
  console.log(chalk.gray(`URL: ${url}`));
  if (skillName) {
    console.log(chalk.gray(`Skill Name: ${skillName}`));
  }
  console.log(chalk.gray(`Max URLs: ${options.maxUrls}\n`));

  const scriptPath = path.join(
    process.cwd(),
    '.roo',
    'skills',
    'scripts',
    'commands',
    'generate-skill.sh'
  );

  // Build command arguments
  const args = [url];
  if (skillName) args.push(skillName);
  args.push('--max-urls', options.maxUrls);
  if (options.outputDir) args.push('--output-dir', options.outputDir);
  if (options.verbose) args.push('--verbose');

  const spinner = ora('Running skill generator...').start();

  try {
    const output = execSync(`"${scriptPath}" ${args.join(' ')}`, {
      cwd: process.cwd(),
      encoding: 'utf-8',
      stdio: options.verbose ? 'inherit' : 'pipe'
    });

    spinner.succeed(chalk.green('✓ Skill generated successfully!'));
    
    if (!options.verbose && output) {
      console.log(output);
    }

    console.log(chalk.green.bold('\n✨ Skill generation complete!\n'));
    console.log(chalk.cyan('The new skill has been added to .roo/skills/ and registered in .roomodes\n'));

  } catch (error) {
    spinner.fail(chalk.red('✗ Skill generation failed'));
    console.error(chalk.red('\nError:'), error.message);
    
    if (error.stderr) {
      console.error(chalk.red('\nDetails:'), error.stderr.toString());
    }
    
    console.log(chalk.yellow('\nTroubleshooting:'));
    console.log('  • Ensure .env file exists with required API keys');
    console.log('  • Check that Python dependencies are installed');
    console.log('  • Verify the documentation URL is accessible\n');
    
    process.exit(1);
  }
}

module.exports = { generateCommand };
