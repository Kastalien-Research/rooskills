/**
 * Sequential Feynman Batch Executor - TypeScript SDK
 * 
 * Programmatic API for running multiple sequential-feynman iterations
 * with progress monitoring, artifact collection, and report generation.
 */

import { query } from '@anthropic-ai/claude-agent-sdk';
import * as fs from 'fs/promises';
import * as path from 'path';
import { EventEmitter } from 'events';

export interface BatchExecutorOptions {
  /** Number of iterations to run */
  iterations: number;
  
  /** Maximum concurrent executions (default: 1) */
  concurrency?: number;
  
  /** Output directory for results (default: ./feynman-batch-outputs) */
  outputDir?: string;
  
  /** Timeout per iteration in milliseconds (default: 14400000 = 4 hours) */
  timeout?: number;
  
  /** Maximum retry attempts per iteration (default: 3) */
  maxRetries?: number;
  
  /** Claude model to use (default: claude-sonnet-4-5) */
  model?: string;
  
  /** Permission mode (default: acceptEdits) */
  permissionMode?: 'acceptEdits' | 'prompt' | 'reject';
  
  /** Allowed tools for execution */
  allowedTools?: string[];
}

export interface IterationResult {
  iteration: number;
  status: 'completed' | 'failed' | 'timeout';
  startedAt: Date;
  completedAt: Date;
  duration: number;
  artifacts: string[];
  error?: Error;
  output?: string;
}

export interface BatchResult {
  runId: string;
  topic: string;
  iterations: IterationResult[];
  completed: number;
  failed: number;
  totalDuration: number;
  outputDir: string;
  reportPath: string;
}

export interface ProgressEvent {
  type: 'start' | 'iteration-start' | 'iteration-complete' | 'iteration-failed' | 'complete';
  iteration?: number;
  total: number;
  completed: number;
  failed: number;
  message: string;
}

/**
 * Batch executor for sequential-feynman workflow
 */
export class FeynmanBatchExecutor extends EventEmitter {
  private options: Required<BatchExecutorOptions>;
  private runId: string;
  private runDir: string;
  private startTime: Date;

  constructor(private topic: string, options: BatchExecutorOptions) {
    super();
    
    this.options = {
      iterations: options.iterations,
      concurrency: options.concurrency ?? 1,
      outputDir: options.outputDir ?? './feynman-batch-outputs',
      timeout: options.timeout ?? 14400000, // 4 hours
      maxRetries: options.maxRetries ?? 3,
      model: options.model ?? 'claude-sonnet-4-5',
      permissionMode: options.permissionMode ?? 'acceptEdits',
      allowedTools: options.allowedTools ?? [
        'Read', 'Write', 'Edit', 'Bash', 'Grep', 'Glob', 
        'WebSearch', 'TodoWrite', 'NotebookEdit'
      ],
    };

    this.runId = this.generateRunId();
    this.runDir = path.join(this.options.outputDir, this.runId);
    this.startTime = new Date();
  }

  /**
   * Execute batch of sequential-feynman iterations
   */
  async execute(): Promise<BatchResult> {
    await this.initialize();
    
    this.emit('progress', {
      type: 'start',
      total: this.options.iterations,
      completed: 0,
      failed: 0,
      message: `Starting ${this.options.iterations} iterations for: ${this.topic}`,
    } as ProgressEvent);

    const results: IterationResult[] = [];
    
    if (this.options.concurrency === 1) {
      // Sequential execution
      for (let i = 1; i <= this.options.iterations; i++) {
        const result = await this.runIteration(i);
        results.push(result);
      }
    } else {
      // Parallel execution with concurrency limit
      const queue = Array.from({ length: this.options.iterations }, (_, i) => i + 1);
      const running = new Set<Promise<IterationResult>>();
      
      while (queue.length > 0 || running.size > 0) {
        // Start new iterations up to concurrency limit
        while (queue.length > 0 && running.size < this.options.concurrency) {
          const iteration = queue.shift()!;
          const promise = this.runIteration(iteration);
          running.add(promise);
          
          promise.finally(() => running.delete(promise));
        }
        
        // Wait for at least one to complete
        if (running.size > 0) {
          const result = await Promise.race(running);
          results.push(result);
        }
      }
    }

    const batchResult = await this.finalize(results);
    
    this.emit('progress', {
      type: 'complete',
      total: this.options.iterations,
      completed: batchResult.completed,
      failed: batchResult.failed,
      message: `Completed ${batchResult.completed}/${this.options.iterations} iterations`,
    } as ProgressEvent);

    return batchResult;
  }

  /**
   * Run a single iteration with retry logic
   */
  private async runIteration(iteration: number): Promise<IterationResult> {
    const iterDir = path.join(this.runDir, `iteration-${iteration}`);
    await fs.mkdir(iterDir, { recursive: true });
    
    const startedAt = new Date();
    
    this.emit('progress', {
      type: 'iteration-start',
      iteration,
      total: this.options.iterations,
      completed: iteration - 1,
      failed: 0,
      message: `Starting iteration ${iteration}/${this.options.iterations}`,
    } as ProgressEvent);

    let lastError: Error | undefined;
    
    for (let attempt = 1; attempt <= this.options.maxRetries; attempt++) {
      try {
        const result = await this.executeWithTimeout(iteration, iterDir);
        
        const completedAt = new Date();
        const duration = completedAt.getTime() - startedAt.getTime();
        
        this.emit('progress', {
          type: 'iteration-complete',
          iteration,
          total: this.options.iterations,
          completed: iteration,
          failed: 0,
          message: `Completed iteration ${iteration} in ${Math.round(duration / 1000)}s`,
        } as ProgressEvent);

        return {
          iteration,
          status: 'completed',
          startedAt,
          completedAt,
          duration,
          artifacts: result.artifacts,
          output: result.output,
        };
        
      } catch (error) {
        lastError = error as Error;
        
        if (attempt < this.options.maxRetries) {
          console.warn(`Iteration ${iteration} failed (attempt ${attempt}/${this.options.maxRetries}), retrying...`);
          await this.sleep(10000); // Wait 10s before retry
        }
      }
    }

    const completedAt = new Date();
    const duration = completedAt.getTime() - startedAt.getTime();
    
    this.emit('progress', {
      type: 'iteration-failed',
      iteration,
      total: this.options.iterations,
      completed: iteration - 1,
      failed: 1,
      message: `Failed iteration ${iteration} after ${this.options.maxRetries} attempts`,
    } as ProgressEvent);

    return {
      iteration,
      status: 'failed',
      startedAt,
      completedAt,
      duration,
      artifacts: [],
      error: lastError,
    };
  }

  /**
   * Execute single iteration with timeout
   */
  private async executeWithTimeout(
    iteration: number,
    iterDir: string
  ): Promise<{ artifacts: string[]; output: string }> {
    return new Promise(async (resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error(`Iteration ${iteration} timed out after ${this.options.timeout}ms`));
      }, this.options.timeout);

      try {
        const result = await query({
          prompt: `/sequential-feynman ${this.topic}`,
          model: this.options.model,
          permissionMode: this.options.permissionMode,
          allowedTools: this.options.allowedTools,
          systemPromptPreset: 'claude-code',
        });

        clearTimeout(timeoutId);

        // Save output
        const outputPath = path.join(iterDir, 'output.json');
        await fs.writeFile(outputPath, JSON.stringify(result, null, 2));

        // Collect artifacts
        const artifacts = await this.collectArtifacts(iteration, iterDir);

        resolve({ artifacts, output: result.text });
        
      } catch (error) {
        clearTimeout(timeoutId);
        reject(error);
      }
    });
  }

  /**
   * Collect artifacts from workspace
   */
  private async collectArtifacts(iteration: number, iterDir: string): Promise<string[]> {
    const artifactsDir = path.join(iterDir, 'artifacts');
    await fs.mkdir(artifactsDir, { recursive: true });
    
    const artifacts: string[] = [];
    
    // Collect notebooks
    const notebooksDir = path.join(process.cwd(), 'notebooks');
    try {
      const files = await fs.readdir(notebooksDir);
      for (const file of files) {
        if (file.startsWith('feynman-') && file.endsWith('.ipynb')) {
          const src = path.join(notebooksDir, file);
          const dest = path.join(artifactsDir, file);
          await fs.copyFile(src, dest);
          artifacts.push(file);
        }
      }
    } catch (error) {
      // Directory might not exist
    }

    // Collect skills
    const skillsDir = path.join(process.cwd(), '.claude', 'skills');
    try {
      const dirs = await fs.readdir(skillsDir);
      for (const dir of dirs) {
        const src = path.join(skillsDir, dir);
        const dest = path.join(artifactsDir, dir);
        await this.copyDir(src, dest);
        artifacts.push(dir);
      }
    } catch (error) {
      // Directory might not exist
    }

    // Save metadata
    const metadata = {
      iteration,
      topic: this.topic,
      timestamp: new Date().toISOString(),
      artifacts: artifacts.length,
    };
    await fs.writeFile(
      path.join(artifactsDir, 'metadata.json'),
      JSON.stringify(metadata, null, 2)
    );

    return artifacts;
  }

  /**
   * Initialize batch execution
   */
  private async initialize(): Promise<void> {
    await fs.mkdir(this.runDir, { recursive: true });
    
    const status = {
      runId: this.runId,
      topic: this.topic,
      iterations: this.options.iterations,
      concurrency: this.options.concurrency,
      status: 'running',
      startedAt: this.startTime.toISOString(),
      completedAt: null,
    };
    
    await fs.writeFile(
      path.join(this.runDir, 'STATUS.json'),
      JSON.stringify(status, null, 2)
    );
  }

  /**
   * Finalize batch execution and generate report
   */
  private async finalize(results: IterationResult[]): Promise<BatchResult> {
    const completed = results.filter(r => r.status === 'completed').length;
    const failed = results.filter(r => r.status === 'failed').length;
    const totalDuration = Date.now() - this.startTime.getTime();

    // Update status
    const status = {
      runId: this.runId,
      topic: this.topic,
      iterations: this.options.iterations,
      concurrency: this.options.concurrency,
      status: failed === 0 ? 'completed' : 'partial',
      startedAt: this.startTime.toISOString(),
      completedAt: new Date().toISOString(),
      results: results.map(r => ({
        iteration: r.iteration,
        status: r.status,
        duration: r.duration,
        artifacts: r.artifacts.length,
        error: r.error?.message,
      })),
    };
    
    await fs.writeFile(
      path.join(this.runDir, 'STATUS.json'),
      JSON.stringify(status, null, 2)
    );

    // Generate report
    const reportPath = path.join(this.runDir, 'REPORT.md');
    await this.generateReport(results, reportPath);

    return {
      runId: this.runId,
      topic: this.topic,
      iterations: results,
      completed,
      failed,
      totalDuration,
      outputDir: this.runDir,
      reportPath,
    };
  }

  /**
   * Generate markdown report
   */
  private async generateReport(results: IterationResult[], reportPath: string): Promise<void> {
    const completed = results.filter(r => r.status === 'completed').length;
    const failed = results.filter(r => r.status === 'failed').length;
    const totalDuration = Date.now() - this.startTime.getTime();

    const report = `# Sequential Feynman Batch Report

## Summary

- **Topic**: ${this.topic}
- **Run ID**: ${this.runId}
- **Total Iterations**: ${this.options.iterations}
- **Completed**: ${completed}
- **Failed**: ${failed}
- **Total Duration**: ${Math.round(totalDuration / 1000)}s
- **Started**: ${this.startTime.toISOString()}
- **Completed**: ${new Date().toISOString()}

## Execution Status

| Iteration | Status | Duration | Artifacts | Error |
|-----------|--------|----------|-----------|-------|
${results.map(r => 
  `| ${r.iteration} | ${r.status} | ${Math.round(r.duration / 1000)}s | ${r.artifacts.length} | ${r.error?.message || '-'} |`
).join('\n')}

## Artifacts by Iteration

${results.map(r => `
### Iteration ${r.iteration}

${r.artifacts.length > 0 ? r.artifacts.map(a => `- ${a}`).join('\n') : '*No artifacts collected*'}
`).join('\n')}

## Output Location

All outputs are stored in: \`${this.runDir}\`

## Next Steps

1. Review notebooks in \`iteration-*/artifacts/\`
2. Compare insights across iterations
3. Integrate validated skills into \`.claude/skills/\`
4. Archive or clean up outputs

---

*Generated by FeynmanBatchExecutor on ${new Date().toISOString()}*
`;

    await fs.writeFile(reportPath, report);
  }

  /**
   * Generate unique run ID
   */
  private generateRunId(): string {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const topicSlug = this.topic
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .slice(0, 30);
    return `${timestamp}-${topicSlug}`;
  }

  /**
   * Copy directory recursively
   */
  private async copyDir(src: string, dest: string): Promise<void> {
    await fs.mkdir(dest, { recursive: true });
    const entries = await fs.readdir(src, { withFileTypes: true });
    
    for (const entry of entries) {
      const srcPath = path.join(src, entry.name);
      const destPath = path.join(dest, entry.name);
      
      if (entry.isDirectory()) {
        await this.copyDir(srcPath, destPath);
      } else {
        await fs.copyFile(srcPath, destPath);
      }
    }
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Convenience function to run batch execution
 */
export async function runFeynmanBatch(
  topic: string,
  options: BatchExecutorOptions
): Promise<BatchResult> {
  const executor = new FeynmanBatchExecutor(topic, options);
  return executor.execute();
}
