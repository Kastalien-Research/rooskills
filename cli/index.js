#!/usr/bin/env node

const { Command } = require('commander');
const chalk = require('chalk');
const packageJson = require('../package.json');
const { initCommand } = require('./commands/init');
const { generateCommand } = require('./commands/generate');

const program = new Command();

program
  .name('rooskills')
  .description('Bring Anthropic\'s Agent Skills to Roo Code')
  .version(packageJson.version);

program
  .command('init')
  .description('Initialize Roo Skills in your project')
  .option('-d, --dir <directory>', 'Target directory', process.cwd())
  .option('--no-install', 'Skip Python dependency installation')
  .option('--skills <skills...>', 'Specific skills to install (default: all)')
  .action(initCommand);

program
  .command('generate <url>')
  .description('Generate a new skill from documentation URL')
  .argument('<url>', 'Documentation URL to process')
  .argument('[skill-name]', 'Skill identifier in kebab-case (optional)')
  .option('--max-urls <number>', 'Maximum number of URLs to process', '20')
  .option('--output-dir <directory>', 'Output directory')
  .option('--verbose', 'Enable verbose logging')
  .action(generateCommand);

program
  .command('list')
  .description('List all available skills')
  .action(() => {
    console.log(chalk.blue.bold('\n📚 Available Roo Skills:\n'));
    console.log(chalk.cyan('Development & Technical:'));
    console.log('  • mcp-builder - Create MCP servers');
    console.log('  • model-enhancement-mcp - Advanced MCP examples');
    console.log('  • document-skills - Document creation (DOCX, PDF, PPTX, XLSX)');
    console.log(chalk.cyan('\nAI & Automation:'));
    console.log('  • lindy-expert - Lindy AI agent platform');
    console.log(chalk.cyan('\nDevelopment Tools:'));
    console.log('  • create-llmstxt-py - Generate llms.txt documentation');
    console.log('  • skill-creator - Create new skills');
    console.log('  • template-skill - Basic skill template');
    console.log(chalk.cyan('\nDocumentation:'));
    console.log('  • architecture - System architecture docs\n');
  });

program.parse();
