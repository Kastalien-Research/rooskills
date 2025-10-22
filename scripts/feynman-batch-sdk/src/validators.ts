/**
 * Input Validators for Feynman Batch SDK
 * 
 * TypeScript validation functions to prevent security vulnerabilities
 */

import {
  VALID_NAME_PATTERN,
  MAX_COMMAND_NAME_LENGTH,
  RESERVED_NAMES,
  DEFAULT_BATCH_SIZE,
  MAX_BATCH_SIZE,
  DEFAULT_BATCH_CONCURRENCY,
  MAX_BATCH_CONCURRENCY,
  DEFAULT_MAX_RETRIES,
} from './constants';

/**
 * Validation error class
 */
export class ValidationError extends Error {
  constructor(
    message: string,
    public readonly field: string
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Validate topic/command name
 */
export function validateTopic(topic: string): string {
  if (!topic || typeof topic !== 'string') {
    throw new ValidationError('Topic is required and must be a string', 'topic');
  }

  if (topic.length > MAX_COMMAND_NAME_LENGTH) {
    throw new ValidationError(
      `Topic exceeds maximum length of ${MAX_COMMAND_NAME_LENGTH} characters`,
      'topic'
    );
  }

  if (!VALID_NAME_PATTERN.test(topic)) {
    throw new ValidationError(
      'Topic can only contain letters, numbers, hyphens, and underscores',
      'topic'
    );
  }

  if (RESERVED_NAMES.includes(topic.toLowerCase() as any)) {
    throw new ValidationError(
      `'${topic}' is a reserved name and cannot be used`,
      'topic'
    );
  }

  return topic;
}

/**
 * Validate iterations parameter
 */
export function validateIterations(iterations?: number): number {
  if (iterations === undefined || iterations === null) {
    return 1; // Default
  }

  const num = Number(iterations);

  if (!Number.isInteger(num)) {
    throw new ValidationError('Iterations must be an integer', 'iterations');
  }

  if (num < 1 || num > 100) {
    throw new ValidationError(
      'Iterations must be between 1 and 100',
      'iterations'
    );
  }

  return num;
}

/**
 * Validate concurrency parameter
 */
export function validateConcurrency(concurrency?: number): number {
  if (concurrency === undefined || concurrency === null) {
    return DEFAULT_BATCH_CONCURRENCY;
  }

  const num = Number(concurrency);

  if (!Number.isInteger(num)) {
    throw new ValidationError('Concurrency must be an integer', 'concurrency');
  }

  if (num < 1 || num > MAX_BATCH_CONCURRENCY) {
    throw new ValidationError(
      `Concurrency must be between 1 and ${MAX_BATCH_CONCURRENCY}`,
      'concurrency'
    );
  }

  return num;
}

/**
 * Validate batch size parameter
 */
export function validateBatchSize(batchSize?: number): number {
  if (batchSize === undefined || batchSize === null) {
    return DEFAULT_BATCH_SIZE;
  }

  const num = Number(batchSize);

  if (!Number.isInteger(num)) {
    throw new ValidationError('Batch size must be an integer', 'batchSize');
  }

  if (num < 1 || num > MAX_BATCH_SIZE) {
    throw new ValidationError(
      `Batch size must be between 1 and ${MAX_BATCH_SIZE}`,
      'batchSize'
    );
  }

  return num;
}

/**
 * Validate retry count parameter
 */
export function validateRetries(retries?: number): number {
  if (retries === undefined || retries === null) {
    return DEFAULT_MAX_RETRIES;
  }

  const num = Number(retries);

  if (!Number.isInteger(num)) {
    throw new ValidationError('Retries must be an integer', 'retries');
  }

  if (num < 0 || num > 10) {
    throw new ValidationError(
      'Retries must be between 0 and 10',
      'retries'
    );
  }

  return num;
}

/**
 * Validate boolean parameter
 */
export function validateBoolean(value: unknown, fieldName: string): boolean {
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

  if (value === undefined || value === null) {
    return false; // Default
  }

  throw new ValidationError(
    `${fieldName} must be a boolean`,
    fieldName
  );
}

/**
 * Validate timeout value
 */
export function validateTimeout(timeout?: number): number {
  if (timeout === undefined || timeout === null) {
    return 30000; // Default 30 seconds
  }

  const num = Number(timeout);

  if (!Number.isInteger(num)) {
    throw new ValidationError('Timeout must be an integer', 'timeout');
  }

  if (num < 1000 || num > 300000) {
    throw new ValidationError(
      'Timeout must be between 1000ms (1s) and 300000ms (5min)',
      'timeout'
    );
  }

  return num;
}

/**
 * Validate Feynman tool parameters
 */
export interface FeynmanToolParams {
  topic: string;
  iterations?: number;
  concurrency?: number;
  background?: boolean;
  batchSize?: number;
  timeout?: number;
}

export interface ValidatedFeynmanParams {
  topic: string;
  iterations: number;
  concurrency: number;
  background: boolean;
  batchSize: number;
  timeout: number;
}

export function validateFeynmanToolParams(
  params: FeynmanToolParams
): ValidatedFeynmanParams {
  return {
    topic: validateTopic(params.topic),
    iterations: validateIterations(params.iterations),
    concurrency: validateConcurrency(params.concurrency),
    background: validateBoolean(params.background, 'background'),
    batchSize: validateBatchSize(params.batchSize),
    timeout: validateTimeout(params.timeout),
  };
}

/**
 * Sanitize error message for safe display
 */
export function sanitizeErrorMessage(error: unknown, isProduction = false): string {
  if (error instanceof ValidationError) {
    return `Validation Error (${error.field}): ${error.message}`;
  }

  if (error instanceof Error) {
    // Don't expose internal errors in production
    if (isProduction) {
      return 'An error occurred during processing';
    }
    return error.message;
  }

  return 'An unknown error occurred';
}
