/**
 * Security Utilities
 * 
 * Input validation and sanitization functions to prevent security vulnerabilities
 * including command injection, path traversal, and other attacks.
 */

const path = require('path');

// Security constants
const VALID_NAME_PATTERN = /^[a-zA-Z0-9_-]+$/;
const VALID_URL_PROTOCOLS = ['http:', 'https:'];
const MAX_SKILL_NAME_LENGTH = 50;
const MAX_URL_LENGTH = 2048;
const MAX_PATH_LENGTH = 255;

const RESERVED_NAMES = [
  'test',
  'config',
  'node_modules',
  'package',
  'index',
  'main',
  'dist',
  'build',
  '.git',
  '.env',
];

// Dangerous characters that should never appear in inputs
const DANGEROUS_SHELL_CHARS = /[;&|`$()<>{}[\]\\!\n\r]/g;
const PATH_TRAVERSAL_PATTERN = /\.\.|~|\/\//g;

/**
 * Security validation error class
 */
class SecurityValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = 'SecurityValidationError';
    this.field = field;
  }
}

/**
 * Validate a URL
 * @param {string} url - URL to validate
 * @returns {string} Validated URL
 * @throws {SecurityValidationError} If URL is invalid
 */
function validateURL(url) {
  if (!url || typeof url !== 'string') {
    throw new SecurityValidationError('URL is required and must be a string', 'url');
  }

  if (url.length > MAX_URL_LENGTH) {
    throw new SecurityValidationError(
      `URL exceeds maximum length of ${MAX_URL_LENGTH} characters`,
      'url'
    );
  }

  // Parse URL
  let parsed;
  try {
    parsed = new URL(url);
  } catch (error) {
    throw new SecurityValidationError('Invalid URL format', 'url');
  }

  // Validate protocol
  if (!VALID_URL_PROTOCOLS.includes(parsed.protocol)) {
    throw new SecurityValidationError(
      `URL protocol must be one of: ${VALID_URL_PROTOCOLS.join(', ')}`,
      'url'
    );
  }

  // Prevent localhost/private IPs in production
  const hostname = parsed.hostname.toLowerCase();
  if (process.env.NODE_ENV === 'production') {
    const privatePatterns = [
      'localhost',
      '127.0.0.1',
      '0.0.0.0',
      '::1',
      /^192\.168\./,
      /^10\./,
      /^172\.(1[6-9]|2[0-9]|3[01])\./,
    ];

    for (const pattern of privatePatterns) {
      if (typeof pattern === 'string' ? hostname === pattern : pattern.test(hostname)) {
        throw new SecurityValidationError(
          'Private/localhost URLs not allowed in production',
          'url'
        );
      }
    }
  }

  return url;
}

/**
 * Validate a skill/command name
 * @param {string} name - Name to validate
 * @returns {string} Validated name
 * @throws {SecurityValidationError} If name is invalid
 */
function validateSkillName(name) {
  if (!name || typeof name !== 'string') {
    throw new SecurityValidationError('Skill name is required and must be a string', 'skillName');
  }

  // Check length
  if (name.length > MAX_SKILL_NAME_LENGTH) {
    throw new SecurityValidationError(
      `Skill name exceeds maximum length of ${MAX_SKILL_NAME_LENGTH} characters`,
      'skillName'
    );
  }

  // Check pattern (alphanumeric, hyphens, underscores only)
  if (!VALID_NAME_PATTERN.test(name)) {
    throw new SecurityValidationError(
      'Skill name can only contain letters, numbers, hyphens, and underscores',
      'skillName'
    );
  }

  // Check for reserved names
  if (RESERVED_NAMES.includes(name.toLowerCase())) {
    throw new SecurityValidationError(
      `'${name}' is a reserved name and cannot be used`,
      'skillName'
    );
  }

  return name;
}

/**
 * Validate and sanitize a file path
 * @param {string} filePath - Path to validate
 * @param {string} baseDir - Base directory (optional)
 * @returns {string} Validated absolute path
 * @throws {SecurityValidationError} If path is invalid
 */
function validatePath(filePath, baseDir = process.cwd()) {
  if (!filePath || typeof filePath !== 'string') {
    throw new SecurityValidationError('Path is required and must be a string', 'path');
  }

  if (filePath.length > MAX_PATH_LENGTH) {
    throw new SecurityValidationError(
      `Path exceeds maximum length of ${MAX_PATH_LENGTH} characters`,
      'path'
    );
  }

  // Check for path traversal attempts
  if (PATH_TRAVERSAL_PATTERN.test(filePath)) {
    throw new SecurityValidationError(
      'Path contains invalid sequences (.., ~, //)',
      'path'
    );
  }

  // Resolve to absolute path
  const resolvedPath = path.resolve(baseDir, filePath);

  // Ensure resolved path is within base directory
  if (!resolvedPath.startsWith(path.resolve(baseDir))) {
    throw new SecurityValidationError(
      'Path attempts to access files outside allowed directory',
      'path'
    );
  }

  return resolvedPath;
}

/**
 * Sanitize a string parameter for safe command-line use
 * @param {string} input - Input to sanitize
 * @returns {string} Sanitized input
 * @throws {SecurityValidationError} If input contains dangerous characters
 */
function sanitizeParameter(input) {
  if (typeof input !== 'string') {
    throw new SecurityValidationError('Parameter must be a string', 'parameter');
  }

  // Check for dangerous shell characters
  if (DANGEROUS_SHELL_CHARS.test(input)) {
    throw new SecurityValidationError(
      'Parameter contains dangerous characters that are not allowed',
      'parameter'
    );
  }

  // Remove any null bytes
  if (input.includes('\0')) {
    throw new SecurityValidationError(
      'Parameter contains null bytes',
      'parameter'
    );
  }

  return input.trim();
}

/**
 * Validate a positive integer parameter
 * @param {any} value - Value to validate
 * @param {string} name - Parameter name for error messages
 * @param {number} min - Minimum allowed value (default: 1)
 * @param {number} max - Maximum allowed value (default: 100)
 * @returns {number} Validated integer
 * @throws {SecurityValidationError} If value is invalid
 */
function validatePositiveInteger(value, name, min = 1, max = 100) {
  const num = Number(value);

  if (!Number.isInteger(num)) {
    throw new SecurityValidationError(
      `${name} must be an integer`,
      name
    );
  }

  if (num < min || num > max) {
    throw new SecurityValidationError(
      `${name} must be between ${min} and ${max}`,
      name
    );
  }

  return num;
}

/**
 * Validate boolean parameter
 * @param {any} value - Value to validate
 * @param {string} name - Parameter name for error messages
 * @returns {boolean} Validated boolean
 */
function validateBoolean(value, name) {
  if (typeof value === 'boolean') {
    return value;
  }

  if (typeof value === 'string') {
    const lower = value.toLowerCase();
    if (lower === 'true' || lower === '1' || lower === 'yes') {
      return true;
    }
    if (lower === 'false' || lower === '0' || lower === 'no') {
      return false;
    }
  }

  throw new SecurityValidationError(
    `${name} must be a boolean`,
    name
  );
}

/**
 * Validate all generate command parameters
 * @param {object} params - Parameters object
 * @returns {object} Validated parameters
 * @throws {SecurityValidationError} If any parameter is invalid
 */
function validateGenerateParams(params) {
  const validated = {};

  // Required: URL
  validated.url = validateURL(params.url);

  // Optional: Skill name
  if (params.skillName) {
    validated.skillName = validateSkillName(params.skillName);
  }

  // Optional: Max URLs
  if (params.maxUrls !== undefined) {
    validated.maxUrls = validatePositiveInteger(
      params.maxUrls,
      'maxUrls',
      1,
      100
    );
  } else {
    validated.maxUrls = 5; // Default
  }

  // Optional: Output directory
  if (params.outputDir) {
    validated.outputDir = validatePath(params.outputDir);
  }

  // Optional: Verbose flag
  if (params.verbose !== undefined) {
    validated.verbose = validateBoolean(params.verbose, 'verbose');
  } else {
    validated.verbose = false;
  }

  return validated;
}

/**
 * Create a safe error message (without sensitive details)
 * @param {Error} error - Original error
 * @returns {string} Safe error message
 */
function createSafeErrorMessage(error) {
  if (error instanceof SecurityValidationError) {
    return error.message;
  }

  // For other errors, provide generic message
  return 'An error occurred. Check logs for details.';
}

module.exports = {
  // Validation functions
  validateURL,
  validateSkillName,
  validatePath,
  sanitizeParameter,
  validatePositiveInteger,
  validateBoolean,
  validateGenerateParams,

  // Error handling
  SecurityValidationError,
  createSafeErrorMessage,

  // Constants (for external use)
  VALID_NAME_PATTERN,
  MAX_SKILL_NAME_LENGTH,
  MAX_URL_LENGTH,
  MAX_PATH_LENGTH,
  RESERVED_NAMES,
};
