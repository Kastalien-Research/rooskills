/**
 * Environment Configuration Validator
 * 
 * Validates required environment variables on application startup
 */

const chalk = require('chalk');

/**
 * Configuration schema
 */
const CONFIG_SCHEMA = {
  FIRECRAWL_API_KEY: {
    required: true,
    type: 'string',
    minLength: 10,
    pattern: /^fc_/,
    description: 'Firecrawl API key (starts with fc_)',
  },
  ANTHROPIC_API_KEY: {
    required: true,
    type: 'string',
    minLength: 20,
    pattern: /^sk-ant-/,
    description: 'Anthropic API key (starts with sk-ant-)',
  },
  EXA_API_KEY: {
    required: false,
    type: 'string',
    minLength: 10,
    description: 'Exa API key (optional)',
  },
  LOG_LEVEL: {
    required: false,
    type: 'string',
    enum: ['debug', 'info', 'warn', 'error'],
    default: 'info',
    description: 'Logging level',
  },
  TIMEOUT_MS: {
    required: false,
    type: 'number',
    min: 1000,
    max: 300000,
    default: 30000,
    description: 'Request timeout in milliseconds',
  },
  MAX_RETRIES: {
    required: false,
    type: 'number',
    min: 0,
    max: 10,
    default: 3,
    description: 'Maximum retry attempts',
  },
  NODE_ENV: {
    required: false,
    type: 'string',
    enum: ['development', 'production', 'test'],
    default: 'development',
    description: 'Node environment',
  },
};

/**
 * Configuration error class
 */
class ConfigurationError extends Error {
  constructor(message, errors = []) {
    super(message);
    this.name = 'ConfigurationError';
    this.errors = errors;
  }
}

/**
 * Validate a single configuration value
 */
function validateValue(key, value, schema) {
  const errors = [];

  // Check required
  if (schema.required && !value) {
    errors.push(`${key} is required but not set`);
    return errors;
  }

  // If not required and not provided, use default
  if (!value) {
    return errors; // Will use default later
  }

  // Type validation
  if (schema.type === 'number') {
    const num = Number(value);
    if (isNaN(num)) {
      errors.push(`${key} must be a number, got: ${value}`);
      return errors;
    }

    if (schema.min !== undefined && num < schema.min) {
      errors.push(`${key} must be at least ${schema.min}`);
    }

    if (schema.max !== undefined && num > schema.max) {
      errors.push(`${key} must be at most ${schema.max}`);
    }
  } else if (schema.type === 'string') {
    if (typeof value !== 'string') {
      errors.push(`${key} must be a string`);
      return errors;
    }

    if (schema.minLength && value.length < schema.minLength) {
      errors.push(
        `${key} must be at least ${schema.minLength} characters long`
      );
    }

    if (schema.pattern && !schema.pattern.test(value)) {
      errors.push(`${key} format is invalid`);
    }

    if (schema.enum && !schema.enum.includes(value)) {
      errors.push(
        `${key} must be one of: ${schema.enum.join(', ')}`
      );
    }
  }

  return errors;
}

/**
 * Validate all configuration
 */
function validateConfig(silent = false) {
  const config = {};
  const allErrors = [];

  for (const [key, schema] of Object.entries(CONFIG_SCHEMA)) {
    const value = process.env[key];
    const errors = validateValue(key, value, schema);

    if (errors.length > 0) {
      allErrors.push(...errors);
      continue;
    }

    // Set value or default
    if (value) {
      if (schema.type === 'number') {
        config[key] = Number(value);
      } else {
        config[key] = value;
      }
    } else if (schema.default !== undefined) {
      config[key] = schema.default;
    }
  }

  if (allErrors.length > 0) {
    if (!silent) {
      console.error(chalk.red.bold('\n❌ Configuration Validation Failed\n'));
      allErrors.forEach(error => {
        console.error(chalk.red(`  • ${error}`));
      });
      console.error(chalk.yellow('\n💡 Tips:'));
      console.error(chalk.gray('  1. Copy .env.example to .env'));
      console.error(chalk.gray('     → cp .env.example .env'));
      console.error(chalk.gray('  2. Fill in your API keys'));
      console.error(chalk.gray('  3. Check the .env.example file for format examples\n'));
    }
    throw new ConfigurationError(
      `Configuration validation failed with ${allErrors.length} error(s)`,
      allErrors
    );
  }

  return config;
}

/**
 * Check if configuration is valid without throwing
 */
function isConfigValid() {
  try {
    validateConfig(true);
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Get configuration value with validation
 */
function getConfig(key) {
  const schema = CONFIG_SCHEMA[key];
  if (!schema) {
    throw new Error(`Unknown configuration key: ${key}`);
  }

  const value = process.env[key];
  const errors = validateValue(key, value, schema);

  if (errors.length > 0) {
    throw new ConfigurationError(errors[0], errors);
  }

  if (value) {
    return schema.type === 'number' ? Number(value) : value;
  }

  return schema.default;
}

/**
 * Print configuration summary
 */
function printConfigSummary() {
  console.log(chalk.blue.bold('\n📋 Configuration Summary\n'));

  for (const [key, schema] of Object.entries(CONFIG_SCHEMA)) {
    const value = process.env[key];
    const hasValue = Boolean(value);
    const isRequired = schema.required;

    const status = hasValue
      ? chalk.green('✓')
      : isRequired
      ? chalk.red('✗')
      : chalk.gray('○');

    const displayValue = hasValue
      ? key.includes('KEY')
        ? chalk.gray('***hidden***')
        : chalk.cyan(value)
      : schema.default
      ? chalk.gray(`(default: ${schema.default})`)
      : chalk.gray('(not set)');

    console.log(`${status} ${chalk.bold(key)}: ${displayValue}`);
  }

  console.log();
}

module.exports = {
  validateConfig,
  isConfigValid,
  getConfig,
  printConfigSummary,
  ConfigurationError,
  CONFIG_SCHEMA,
};
