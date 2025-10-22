/**
 * Constants for Feynman Batch SDK
 * 
 * This file centralizes all magic numbers and configuration values
 * to improve maintainability and reduce hardcoded values throughout the codebase.
 */

// ============================================================================
// TIMEOUT CONFIGURATION
// ============================================================================

/**
 * Default timeout for command execution in milliseconds
 * @default 30000 (30 seconds)
 */
export const DEFAULT_COMMAND_TIMEOUT_MS = 30000;

/**
 * Default timeout for API requests in milliseconds
 * @default 30000 (30 seconds)
 */
export const DEFAULT_API_TIMEOUT_MS = 30000;

/**
 * Connection timeout for initial connections in milliseconds
 * @default 5000 (5 seconds)
 */
export const DEFAULT_CONNECTION_TIMEOUT_MS = 5000;

/**
 * Maximum timeout allowed for any operation in milliseconds
 * @default 300000 (5 minutes)
 */
export const MAX_TIMEOUT_MS = 300000;

// ============================================================================
// RETRY CONFIGURATION
// ============================================================================

/**
 * Default number of retry attempts for failed operations
 * @default 3
 */
export const DEFAULT_MAX_RETRIES = 3;

/**
 * Initial delay before first retry in milliseconds
 * @default 1000 (1 second)
 */
export const DEFAULT_RETRY_DELAY_MS = 1000;

/**
 * Maximum delay between retries in milliseconds (for exponential backoff)
 * @default 10000 (10 seconds)
 */
export const MAX_RETRY_DELAY_MS = 10000;

/**
 * Exponential backoff multiplier
 * @default 2
 */
export const RETRY_BACKOFF_MULTIPLIER = 2;

// ============================================================================
// BATCH PROCESSING
// ============================================================================

/**
 * Default batch size for parallel processing
 * @default 10
 */
export const DEFAULT_BATCH_SIZE = 10;

/**
 * Maximum batch size allowed
 * @default 100
 */
export const MAX_BATCH_SIZE = 100;

/**
 * Default concurrency limit for batch operations
 * @default 3
 */
export const DEFAULT_BATCH_CONCURRENCY = 3;

/**
 * Maximum concurrency allowed
 * @default 10
 */
export const MAX_BATCH_CONCURRENCY = 10;

// ============================================================================
// BUFFER AND MEMORY
// ============================================================================

/**
 * Maximum buffer size for command output in bytes
 * @default 1048576 (1 MB)
 */
export const MAX_BUFFER_SIZE = 1024 * 1024;

/**
 * Maximum buffer size for large operations in bytes
 * @default 10485760 (10 MB)
 */
export const MAX_LARGE_BUFFER_SIZE = 10 * 1024 * 1024;

/**
 * Default chunk size for streaming operations in bytes
 * @default 65536 (64 KB)
 */
export const DEFAULT_CHUNK_SIZE = 64 * 1024;

// ============================================================================
// RATE LIMITING
// ============================================================================

/**
 * Default rate limit (requests per second)
 * @default 10
 */
export const DEFAULT_RATE_LIMIT_PER_SECOND = 10;

/**
 * Minimum interval between requests in milliseconds
 * @default 100
 */
export const MIN_REQUEST_INTERVAL_MS = 100;

/**
 * Maximum requests allowed in burst
 * @default 50
 */
export const MAX_BURST_REQUESTS = 50;

// ============================================================================
// CACHE CONFIGURATION
// ============================================================================

/**
 * Default cache TTL in seconds
 * @default 3600 (1 hour)
 */
export const DEFAULT_CACHE_TTL_SECONDS = 3600;

/**
 * Maximum cache entries
 * @default 1000
 */
export const MAX_CACHE_ENTRIES = 1000;

/**
 * Cache cleanup interval in milliseconds
 * @default 300000 (5 minutes)
 */
export const CACHE_CLEANUP_INTERVAL_MS = 5 * 60 * 1000;

// ============================================================================
// STRING LIMITS
// ============================================================================

/**
 * Maximum length for command names
 * @default 50
 */
export const MAX_COMMAND_NAME_LENGTH = 50;

/**
 * Maximum length for error messages
 * @default 500
 */
export const MAX_ERROR_MESSAGE_LENGTH = 500;

/**
 * Maximum length for log entries
 * @default 1000
 */
export const MAX_LOG_ENTRY_LENGTH = 1000;

/**
 * Content truncation length for prompts
 * @default 2000
 */
export const PROMPT_CONTENT_TRUNCATE_LENGTH = 2000;

// ============================================================================
// HTTP STATUS CODES
// ============================================================================

/**
 * HTTP status codes that indicate retryable errors
 */
export const RETRYABLE_STATUS_CODES = [408, 429, 500, 502, 503, 504] as const;

/**
 * HTTP status codes that indicate success
 */
export const SUCCESS_STATUS_CODES = [200, 201, 202, 204] as const;

// ============================================================================
// FILE SYSTEM
// ============================================================================

/**
 * Maximum file size for processing in bytes
 * @default 10485760 (10 MB)
 */
export const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;

/**
 * Default file encoding
 * @default 'utf-8'
 */
export const DEFAULT_FILE_ENCODING = 'utf-8';

/**
 * Temporary file prefix
 * @default 'rooskills-temp-'
 */
export const TEMP_FILE_PREFIX = 'rooskills-temp-';

// ============================================================================
// VALIDATION PATTERNS
// ============================================================================

/**
 * Valid skill/command name pattern (alphanumeric, hyphens, underscores)
 */
export const VALID_NAME_PATTERN = /^[a-zA-Z0-9_-]+$/;

/**
 * Reserved names that cannot be used
 */
export const RESERVED_NAMES = [
    'test',
    'config',
    'node_modules',
    'package',
    'index',
    'main',
    'dist',
    'build',
] as const;

// ============================================================================
// ENVIRONMENT
// ============================================================================

/**
 * Default log level
 * @default 'info'
 */
export const DEFAULT_LOG_LEVEL = 'info';

/**
 * Valid log levels
 */
export const VALID_LOG_LEVELS = ['debug', 'info', 'warn', 'error'] as const;

/**
 * Default environment
 * @default 'development'
 */
export const DEFAULT_ENVIRONMENT = 'development';

// ============================================================================
// COMMAND ALLOWLIST
// ============================================================================

/**
 * List of allowed commands for execution (security)
 */
export const ALLOWED_COMMANDS = [
    'npm',
    'node',
    'python',
    'python3',
    'git',
    'pnpm',
    'yarn',
] as const;

/**
 * Dangerous characters that should be filtered from command arguments
 */
export const DANGEROUS_COMMAND_CHARS = /[;&|`$(){}[\]<>]/g;

// ============================================================================
// ERROR MESSAGES
// ============================================================================

/**
 * Standard error messages
 */
export const ERROR_MESSAGES = {
    TIMEOUT: 'Operation timed out',
    INVALID_INPUT: 'Invalid input provided',
    COMMAND_NOT_ALLOWED: 'Command not allowed',
    FILE_NOT_FOUND: 'File not found',
    PERMISSION_DENIED: 'Permission denied',
    NETWORK_ERROR: 'Network error occurred',
    UNKNOWN_ERROR: 'An unknown error occurred',
} as const;

// ============================================================================
// TYPE EXPORTS
// ============================================================================

/**
 * Type for valid log levels
 */
export type LogLevel = typeof VALID_LOG_LEVELS[number];

/**
 * Type for allowed commands
 */
export type AllowedCommand = typeof ALLOWED_COMMANDS[number];

/**
 * Type for reserved names
 */
export type ReservedName = typeof RESERVED_NAMES[number];

/**
 * Type for retryable status codes
 */
export type RetryableStatusCode = typeof RETRYABLE_STATUS_CODES[number];

/**
 * Type for success status codes
 */
export type SuccessStatusCode = typeof SUCCESS_STATUS_CODES[number];
