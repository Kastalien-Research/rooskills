/**
 * Tool integration for Claude agents
 * 
 * Wraps batch executor as a tool that agents can invoke
 */

import { tool } from '@anthropic-ai/claude-agent-sdk';
import { FeynmanBatchExecutor, BatchExecutorOptions } from './batch-executor';
import { spawn } from 'child_process';
import * as path from 'path';
import {
  validateFeynmanToolParams,
  ValidationError,
  sanitizeErrorMessage,
  type FeynmanToolParams,
} from './validators';
import { DEFAULT_COMMAND_TIMEOUT_MS, MAX_BUFFER_SIZE } from './constants';

/**
 * Create a tool for running feynman batch research
 */
export function createFeynmanTool() {
  return tool({
    name: 'run_feynman_batch',
    description: 'Run sequential-feynman workflow multiple times for deep research. Can run in background while agent continues other work.',
    parameters: {
      topic: {
        type: 'string',
        description: 'Topic to research in depth (alphanumeric, hyphens, underscores only)',
      },
      iterations: {
        type: 'number',
        description: 'Number of research iterations to run (default: 1, max: 100)',
        default: 1,
      },
      concurrency: {
        type: 'number',
        description: 'Number of parallel iterations (default: 1, max: 10)',
        default: 1,
      },
      background: {
        type: 'boolean',
        description: 'Run in background and return immediately (default: false)',
        default: false,
      },
    },
  })(async (params: FeynmanToolParams) => {
    // SECURITY: Validate all inputs
    let validatedParams;
    try {
      validatedParams = validateFeynmanToolParams(params);
    } catch (error) {
      if (error instanceof ValidationError) {
        return JSON.stringify({
          status: 'error',
          error: 'Validation failed',
          message: error.message,
          field: error.field,
        }, null, 2);
      }
      throw error;
    }

    try {
      if (validatedParams.background) {
        // Run in detached background process
        return await runInBackground(
          validatedParams.topic,
          validatedParams.iterations,
          validatedParams.concurrency,
          validatedParams.timeout
        );
      } else {
        // Run synchronously with progress updates
        return await runSynchronously(
          validatedParams.topic,
          validatedParams.iterations,
          validatedParams.concurrency
        );
      }
    } catch (error) {
      return JSON.stringify({
        status: 'error',
        error: 'Execution failed',
        message: sanitizeErrorMessage(error),
      }, null, 2);
    }
  });
}

/**
 * Run batch executor in background
 */
async function runInBackground(
  topic: string,
  iterations: number,
  concurrency: number,
  timeout: number
): Promise<string> {
  const scriptPath = path.join(__dirname, '../../feynman-batch.sh');
  
  // Build arguments array (validated inputs only)
  const args = [
    topic,
    iterations.toString(),
    '--parallel',
    concurrency.toString(),
  ];

  try {
    const child = spawn(scriptPath, args, {
      detached: true,
      stdio: 'ignore',
      cwd: process.cwd(),
      timeout,
      // Set resource limits
      shell: false, // Explicitly no shell
    });

    child.unref();

    return JSON.stringify({
      status: 'started',
      pid: child.pid,
      topic,
      iterations,
      concurrency,
      message: `Started ${iterations} iterations of sequential-feynman for "${topic}" in background (PID: ${child.pid})`,
      checkStatus: 'Check feynman-batch-outputs/ for results and STATUS.json for progress',
    }, null, 2);
  } catch (error) {
    return JSON.stringify({
      status: 'error',
      error: 'Failed to start background process',
      message: sanitizeErrorMessage(error),
    }, null, 2);
  }
}

/**
 * Run batch executor synchronously with progress
 */
async function runSynchronously(
  topic: string,
  iterations: number,
  concurrency: number
): Promise<string> {
  const options: BatchExecutorOptions = {
    iterations,
    concurrency,
  };

  try {
    const executor = new FeynmanBatchExecutor(topic, options);

    // Log progress events
    executor.on('progress', (event) => {
      console.log(`[${event.type}] ${event.message}`);
    });

    const result = await executor.execute();

    return JSON.stringify({
      status: 'completed',
      runId: result.runId,
      topic: result.topic,
      completed: result.completed,
      failed: result.failed,
      totalDuration: Math.round(result.totalDuration / 1000),
      outputDir: result.outputDir,
      reportPath: result.reportPath,
      message: `Completed ${result.completed}/${iterations} iterations successfully`,
      nextSteps: [
        `Review report: ${result.reportPath}`,
        `Check notebooks: ${result.outputDir}/iteration-*/artifacts/`,
        `Integrate skills into .claude/skills/`,
      ],
    }, null, 2);
  } catch (error) {
    return JSON.stringify({
      status: 'error',
      error: 'Execution failed',
      message: sanitizeErrorMessage(error),
      topic,
      iterations,
    }, null, 2);
  }
}

/**
 * Example usage in an agent
 */
export async function exampleAgentUsage() {
  const feynmanTool = createFeynmanTool();

  // Background execution - agent can continue other work
  const backgroundResult = await feynmanTool({
    topic: 'distributed consensus algorithms',
    iterations: 3,
    concurrency: 2,
    background: true,
  });

  console.log('Background job started:', backgroundResult);
  
  // Agent can now work on other tasks...
  // Check status later by reading STATUS.json file

  // Synchronous execution - wait for completion
  const syncResult = await feynmanTool({
    topic: 'WebAssembly optimization techniques',
    iterations: 2,
    concurrency: 1,
    background: false,
  });

  console.log('Synchronous job completed:', syncResult);
}
