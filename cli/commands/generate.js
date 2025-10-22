const { execFileSync } = require('child_process');
const path = require('path');
const chalk = require('chalk');
const ora = require('ora');
const {
  validateGenerateParams,
  SecurityValidationError,
} = require('../utils/security');

async function generateCommand(url, skillName, options) {
  console.log(chalk.blue.bold('\n🔧 Generating new skill from documentation...\n'));

  // SECURITY: Validate all inputs before processing
  let validatedParams;
  try {
    validatedParams = validateGenerateParams({
      url,
      skillName,
      maxUrls: options.maxUrls,
      outputDir: options.outputDir,
      verbose: options.verbose,
    });
  } catch (error) {
    if (error instanceof SecurityValidationError) {
      console.error(chalk.red('\n✗ Validation Error:'), error.message);
      console.error(chalk.yellow(`  Field: ${error.field}\n`));
      process.exit(1);
    }
    throw error;
  }

  console.log(chalk.gray(`URL: ${validatedParams.url}`));
  if (validatedParams.skillName) {
    console.log(chalk.gray(`Skill Name: ${validatedParams.skillName}`));
  }
  console.log(chalk.gray(`Max URLs: ${validatedParams.maxUrls}\n`));

  const scriptPath = path.join(
    process.cwd(),
    '.roo',
    'skills',
    'scripts',
    'commands',
    'generate-skill.sh'
  );

  // Build command arguments array (no shell interpretation)
  const args = [validatedParams.url];
  if (validatedParams.skillName) {
    args.push(validatedParams.skillName);
  }
  args.push('--max-urls', String(validatedParams.maxUrls));
  if (validatedParams.outputDir) {
    args.push('--output-dir', validatedParams.outputDir);
  }
  if (validatedParams.verbose) {
    args.push('--verbose');
  }

  const spinner = ora('Running skill generator...').start();

  try {
    // SECURITY FIX: Use execFileSync instead of execSync
    // This prevents shell interpretation and command injection
    const output = execFileSync(scriptPath, args, {
      cwd: process.cwd(),
      encoding: 'utf-8',
      stdio: validatedParams.verbose ? 'inherit' : 'pipe',
      timeout: 300000, // 5 minute timeout
      maxBuffer: 10 * 1024 * 1024, // 10MB max buffer
    });

    spinner.succeed(chalk.green('✓ Skill generated successfully!'));
    
    if (!validatedParams.verbose && output) {
      console.log(output);
    }

    console.log(chalk.green.bold('\n✨ Skill generation complete!\n'));
    console.log(chalk.cyan('The new skill has been added to .roo/skills/ and registered in .roomodes'));
    console.log(chalk.cyan('💡 Activate it: Mention the skill name in chat or use Roo Code mode selector\n'));

  } catch (error) {
    spinner.fail(chalk.red('✗ Skill generation failed'));
    
    // Provide safe error messages
    if (error.code === 'ETIMEDOUT') {
      console.error(chalk.red('\nError: Operation timed out after 5 minutes'));
    } else if (error.code === 'ENOENT') {
      console.error(chalk.red('\nError: Script not found'));
      console.error(chalk.gray(`  Looking for: ${scriptPath}`));
    } else {
      console.error(chalk.red('\nError:'), error.message);
    }
    
    if (error.stderr) {
      console.error(chalk.red('\nDetails:'), error.stderr.toString());
    }
    
    console.log(chalk.yellow('\nTroubleshooting:'));
    console.log('  • Ensure .env file exists with required API keys');
    console.log(chalk.gray('    → cp .env.example .env && nano .env'));
    console.log('  • Check that Python dependencies are installed');
    console.log(chalk.gray('    → pip install -r .roo/skills/scripts/agent-skill-generator/requirements.txt'));
    console.log('  • Verify the documentation URL is accessible');
    console.log(chalk.gray('    → Test the URL in your browser first'));
    console.log('  • Ensure the generate-skill.sh script has execute permissions');
    console.log(chalk.gray('    → chmod +x .roo/skills/scripts/commands/generate-skill.sh\n'));
    
    process.exit(1);
  }
}

module.exports = { generateCommand };
