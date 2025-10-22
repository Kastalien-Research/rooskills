# https://google-gemini.github.io/gemini-cli/docs/ llms-full.txt

## Gemini CLI File System Tools
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Gemini CLI file system tools

The Gemini CLI provides a comprehensive suite of tools for interacting with the local file system. These tools allow the Gemini model to read from, write to, list, search, and modify files and directories, all under your control and typically with confirmation for sensitive operations.

**Note:** All file system tools operate within a `rootDirectory` (usually the current working directory where you launched the CLI) for security. Paths that you provide to these tools are generally expected to be absolute or are resolved relative to this root directory.

## 1\. `list_directory` (ReadFolder) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/file-system.html\#1-list_directory-readfolder)

`list_directory` lists the names of files and subdirectories directly within a specified directory path. It can optionally ignore entries matching provided glob patterns.

- **Tool name:** `list_directory`
- **Display name:** ReadFolder
- **File:** `ls.ts`
- **Parameters:**
  - `path` (string, required): The absolute path to the directory to list.
  - `ignore` (array of strings, optional): A list of glob patterns to exclude from the listing (e.g., `["*.log", ".git"]`).
  - `respect_git_ignore` (boolean, optional): Whether to respect `.gitignore` patterns when listing files. Defaults to `true`.
- **Behavior:**
  - Returns a list of file and directory names.
  - Indicates whether each entry is a directory.
  - Sorts entries with directories first, then alphabetically.
- **Output ( `llmContent`):** A string like: `Directory listing for /path/to/your/folder:\n[DIR] subfolder1\nfile1.txt\nfile2.png`
- **Confirmation:** No.

## 2\. `read_file` (ReadFile) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/file-system.html\#2-read_file-readfile)

`read_file` reads and returns the content of a specified file. This tool handles text, images (PNG, JPG, GIF, WEBP, SVG, BMP), and PDF files. For text files, it can read specific line ranges. Other binary file types are generally skipped.

- **Tool name:** `read_file`
- **Display name:** ReadFile
- **File:** `read-file.ts`
- **Parameters:**
  - `path` (string, required): The absolute path to the file to read.
  - `offset` (number, optional): For text files, the 0-based line number to start reading from. Requires `limit` to be set.
  - `limit` (number, optional): For text files, the maximum number of lines to read. If omitted, reads a default maximum (e.g., 2000 lines) or the entire file if feasible.
- **Behavior:**
  - For text files: Returns the content. If `offset` and `limit` are used, returns only that slice of lines. Indicates if content was truncated due to line limits or line length limits.
  - For image and PDF files: Returns the file content as a base64-encoded data structure suitable for model consumption.
  - For other binary files: Attempts to identify and skip them, returning a message indicating it’s a generic binary file.
- **Output:** ( `llmContent`):

  - For text files: The file content, potentially prefixed with a truncation message (e.g., `[File content truncated: showing lines 1-100 of 500 total lines...]\nActual file content...`).
  - For image/PDF files: An object containing `inlineData` with `mimeType` and base64 `data` (e.g., `{ inlineData: { mimeType: 'image/png', data: 'base64encodedstring' } }`).
  - For other binary files: A message like `Cannot display content of binary file: /path/to/data.bin`.
- **Confirmation:** No.

## 3\. `write_file` (WriteFile) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/file-system.html\#3-write_file-writefile)

`write_file` writes content to a specified file. If the file exists, it will be overwritten. If the file doesn’t exist, it (and any necessary parent directories) will be created.

- **Tool name:** `write_file`
- **Display name:** WriteFile
- **File:** `write-file.ts`
- **Parameters:**
  - `file_path` (string, required): The absolute path to the file to write to.
  - `content` (string, required): The content to write into the file.
- **Behavior:**
  - Writes the provided `content` to the `file_path`.
  - Creates parent directories if they don’t exist.
- **Output ( `llmContent`):** A success message, e.g., `Successfully overwrote file: /path/to/your/file.txt` or `Successfully created and wrote to new file: /path/to/new/file.txt`.
- **Confirmation:** Yes. Shows a diff of changes and asks for user approval before writing.

## 4\. `glob` (FindFiles) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/file-system.html\#4-glob-findfiles)

`glob` finds files matching specific glob patterns (e.g., `src/**/*.ts`, `*.md`), returning absolute paths sorted by modification time (newest first).

- **Tool name:** `glob`
- **Display name:** FindFiles
- **File:** `glob.ts`
- **Parameters:**
  - `pattern` (string, required): The glob pattern to match against (e.g., `"*.py"`, `"src/**/*.js"`).
  - `path` (string, optional): The absolute path to the directory to search within. If omitted, searches the tool’s root directory.
  - `case_sensitive` (boolean, optional): Whether the search should be case-sensitive. Defaults to `false`.
  - `respect_git_ignore` (boolean, optional): Whether to respect .gitignore patterns when finding files. Defaults to `true`.
- **Behavior:**
  - Searches for files matching the glob pattern within the specified directory.
  - Returns a list of absolute paths, sorted with the most recently modified files first.
  - Ignores common nuisance directories like `node_modules` and `.git` by default.
- **Output ( `llmContent`):** A message like: `Found 5 file(s) matching "*.ts" within src, sorted by modification time (newest first):\nsrc/file1.ts\nsrc/subdir/file2.ts...`
- **Confirmation:** No.

## 5\. `search_file_content` (SearchText) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/file-system.html\#5-search_file_content-searchtext)

`search_file_content` searches for a regular expression pattern within the content of files in a specified directory. Can filter files by a glob pattern. Returns the lines containing matches, along with their file paths and line numbers.

- **Tool name:** `search_file_content`
- **Display name:** SearchText
- **File:** `grep.ts`
- **Parameters:**
  - `pattern` (string, required): The regular expression (regex) to search for (e.g., `"function\s+myFunction"`).
  - `path` (string, optional): The absolute path to the directory to search within. Defaults to the current working directory.
  - `include` (string, optional): A glob pattern to filter which files are searched (e.g., `"*.js"`, `"src/**/*.{ts,tsx}"`). If omitted, searches most files (respecting common ignores).
- **Behavior:**
  - Uses `git grep` if available in a Git repository for speed; otherwise, falls back to system `grep` or a JavaScript-based search.
  - Returns a list of matching lines, each prefixed with its file path (relative to the search directory) and line number.
- **Output ( `llmContent`):** A formatted string of matches, e.g.:





```
Found 3 matches for pattern "myFunction" in path "." (filter: "*.ts"):
  ---
File: src/utils.ts
L15: export function myFunction() {
L22:   myFunction.call();
  ---
File: src/index.ts
L5: import { myFunction } from './utils';
  ---

```

- **Confirmation:** No.

## 6\. `replace` (Edit) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/file-system.html\#6-replace-edit)

`replace` replaces text within a file. By default, replaces a single occurrence, but can replace multiple occurrences when `expected_replacements` is specified. This tool is designed for precise, targeted changes and requires significant context around the `old_string` to ensure it modifies the correct location.

- **Tool name:** `replace`
- **Display name:** Edit
- **File:** `edit.ts`
- **Parameters:**
  - `file_path` (string, required): The absolute path to the file to modify.
  - `old_string` (string, required): The exact literal text to replace.

    **CRITICAL:** This string must uniquely identify the single instance to change. It should include at least 3 lines of context _before_ and _after_ the target text, matching whitespace and indentation precisely. If `old_string` is empty, the tool attempts to create a new file at `file_path` with `new_string` as content.

  - `new_string` (string, required): The exact literal text to replace `old_string` with.
  - `expected_replacements` (number, optional): The number of occurrences to replace. Defaults to `1`.
- **Behavior:**
  - If `old_string` is empty and `file_path` does not exist, creates a new file with `new_string` as content.
  - If `old_string` is provided, it reads the `file_path` and attempts to find exactly one occurrence of `old_string`.
  - If one occurrence is found, it replaces it with `new_string`.
  - **Enhanced Reliability (Multi-Stage Edit Correction):** To significantly improve the success rate of edits, especially when the model-provided `old_string` might not be perfectly precise, the tool incorporates a multi-stage edit correction mechanism.

    - If the initial `old_string` isn’t found or matches multiple locations, the tool can leverage the Gemini model to iteratively refine `old_string` (and potentially `new_string`).
    - This self-correction process attempts to identify the unique segment the model intended to modify, making the `replace` operation more robust even with slightly imperfect initial context.
- **Failure conditions:** Despite the correction mechanism, the tool will fail if:

  - `file_path` is not absolute or is outside the root directory.
  - `old_string` is not empty, but the `file_path` does not exist.
  - `old_string` is empty, but the `file_path` already exists.
  - `old_string` is not found in the file after attempts to correct it.
  - `old_string` is found multiple times, and the self-correction mechanism cannot resolve it to a single, unambiguous match.
- **Output ( `llmContent`):**
  - On success: `Successfully modified file: /path/to/file.txt (1 replacements).` or `Created new file: /path/to/new_file.txt with provided content.`
  - On failure: An error message explaining the reason (e.g., `Failed to edit, 0 occurrences found...`, `Failed to edit, expected 1 occurrences but found 2...`).
- **Confirmation:** Yes. Shows a diff of the proposed changes and asks for user approval before writing to the file.

These file system tools provide a foundation for the Gemini CLI to understand and interact with your local project context.

## Gemini CLI Commands Reference
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# CLI Commands

Gemini CLI supports several built-in commands to help you manage your session, customize the interface, and control its behavior. These commands are prefixed with a forward slash ( `/`), an at symbol ( `@`), or an exclamation mark ( `!`).

## Slash commands ( `/`) [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/commands.html\#slash-commands-)

Slash commands provide meta-level control over the CLI itself.

### Built-in Commands [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/commands.html\#built-in-commands)

- **`/bug`**
  - **Description:** File an issue about Gemini CLI. By default, the issue is filed within the GitHub repository for Gemini CLI. The string you enter after `/bug` will become the headline for the bug being filed. The default `/bug` behavior can be modified using the `advanced.bugCommand` setting in your `.gemini/settings.json` files.
- **`/chat`**
  - **Description:** Save and resume conversation history for branching conversation state interactively, or resuming a previous state from a later session.
  - **Sub-commands:**
    - **`save`**
      - **Description:** Saves the current conversation history. You must add a `<tag>` for identifying the conversation state.
      - **Usage:** `/chat save <tag>`
      - **Details on Checkpoint Location:** The default locations for saved chat checkpoints are:

        - Linux/macOS: `~/.gemini/tmp/<project_hash>/`
        - Windows: `C:\Users\<YourUsername>\.gemini\tmp\<project_hash>\`
        - When you run `/chat list`, the CLI only scans these specific directories to find available checkpoints.
        - **Note:** These checkpoints are for manually saving and resuming conversation states. For automatic checkpoints created before file modifications, see the [Checkpointing documentation](https://google-gemini.github.io/gemini-cli/docs/cli/checkpointing.html).
    - **`resume`**
      - **Description:** Resumes a conversation from a previous save.
      - **Usage:** `/chat resume <tag>`
    - **`list`**
      - **Description:** Lists available tags for chat state resumption.
    - **`delete`**
      - **Description:** Deletes a saved conversation checkpoint.
      - **Usage:** `/chat delete <tag>`
    - **`share`**
      - **Description** Writes the current conversation to a provided Markdown or JSON file.
      - **Usage** `/chat share file.md` or `/chat share file.json`. If no filename is provided, then the CLI will generate one.
- **`/clear`**
  - **Description:** Clear the terminal screen, including the visible session history and scrollback within the CLI. The underlying session data (for history recall) might be preserved depending on the exact implementation, but the visual display is cleared.
  - **Keyboard shortcut:** Press **Ctrl+L** at any time to perform a clear action.
- **`/compress`**
  - **Description:** Replace the entire chat context with a summary. This saves on tokens used for future tasks while retaining a high level summary of what has happened.
- **`/copy`**
  - **Description:** Copies the last output produced by Gemini CLI to your clipboard, for easy sharing or reuse.
  - **Note:** This command requires platform-specific clipboard tools to be installed.

    - On Linux, it requires `xclip` or `xsel`. You can typically install them using your system’s package manager.
    - On macOS, it requires `pbcopy`, and on Windows, it requires `clip`. These tools are typically pre-installed on their respective systems.
- **`/directory`** (or **`/dir`**)

  - **Description:** Manage workspace directories for multi-directory support.
  - **Sub-commands:**
    - **`add`**:

      - **Description:** Add a directory to the workspace. The path can be absolute or relative to the current working directory. Moreover, the reference from home directory is supported as well.
      - **Usage:** `/directory add <path1>,<path2>`
      - **Note:** Disabled in restrictive sandbox profiles. If you’re using that, use `--include-directories` when starting the session instead.
    - **`show`**:

      - **Description:** Display all directories added by `/directory add` and `--include-directories`.
      - **Usage:** `/directory show`
- **`/editor`**
  - **Description:** Open a dialog for selecting supported editors.
- **`/extensions`**
  - **Description:** Lists all active extensions in the current Gemini CLI session. See [Gemini CLI Extensions](https://google-gemini.github.io/gemini-cli/docs/extensions/).
- **`/help`** (or **`/?`**)

  - **Description:** Display help information about Gemini CLI, including available commands and their usage.
- **`/mcp`**
  - **Description:** List configured Model Context Protocol (MCP) servers, their connection status, server details, and available tools.
  - **Sub-commands:**
    - **`desc`** or **`descriptions`**:

      - **Description:** Show detailed descriptions for MCP servers and tools.
    - **`nodesc`** or **`nodescriptions`**:

      - **Description:** Hide tool descriptions, showing only the tool names.
    - **`schema`**:

      - **Description:** Show the full JSON schema for the tool’s configured parameters.
  - **Keyboard Shortcut:** Press **Ctrl+T** at any time to toggle between showing and hiding tool descriptions.
- **`/memory`**
  - **Description:** Manage the AI’s instructional context (hierarchical memory loaded from `GEMINI.md` files).
  - **Sub-commands:**
    - **`add`**:

      - **Description:** Adds the following text to the AI’s memory. Usage: `/memory add <text to remember>`
    - **`show`**:

      - **Description:** Display the full, concatenated content of the current hierarchical memory that has been loaded from all `GEMINI.md` files. This lets you inspect the instructional context being provided to the Gemini model.
    - **`refresh`**:

      - **Description:** Reload the hierarchical instructional memory from all `GEMINI.md` files found in the configured locations (global, project/ancestors, and sub-directories). This command updates the model with the latest `GEMINI.md` content.
    - **`list`**:

      - **Description:** Lists the paths of the GEMINI.md files in use for hierarchical memory.
    - **Note:** For more details on how `GEMINI.md` files contribute to hierarchical memory, see the [CLI Configuration documentation](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html).
- **`/restore`**
  - **Description:** Restores the project files to the state they were in just before a tool was executed. This is particularly useful for undoing file edits made by a tool. If run without a tool call ID, it will list available checkpoints to restore from.
  - **Usage:** `/restore [tool_call_id]`
  - **Note:** Only available if the CLI is invoked with the `--checkpointing` option or configured via [settings](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html). See [Checkpointing documentation](https://google-gemini.github.io/gemini-cli/docs/cli/checkpointing.html) for more details.
- **`/settings`**
  - **Description:** Open the settings editor to view and modify Gemini CLI settings.
  - **Details:** This command provides a user-friendly interface for changing settings that control the behavior and appearance of Gemini CLI. It is equivalent to manually editing the `.gemini/settings.json` file, but with validation and guidance to prevent errors.
  - **Usage:** Simply run `/settings` and the editor will open. You can then browse or search for specific settings, view their current values, and modify them as desired. Changes to some settings are applied immediately, while others require a restart.
- **`/stats`**
  - **Description:** Display detailed statistics for the current Gemini CLI session, including token usage, cached token savings (when available), and session duration. Note: Cached token information is only displayed when cached tokens are being used, which occurs with API key authentication but not with OAuth authentication at this time.
- [**`/theme`**](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html)
  - **Description:** Open a dialog that lets you change the visual theme of Gemini CLI.
- **`/auth`**
  - **Description:** Open a dialog that lets you change the authentication method.
- **`/about`**
  - **Description:** Show version info. Please share this information when filing issues.
- [**`/tools`**](https://google-gemini.github.io/gemini-cli/docs/tools/)
  - **Description:** Display a list of tools that are currently available within Gemini CLI.
  - **Usage:** `/tools [desc]`
  - **Sub-commands:**
    - **`desc`** or **`descriptions`**:

      - **Description:** Show detailed descriptions of each tool, including each tool’s name with its full description as provided to the model.
    - **`nodesc`** or **`nodescriptions`**:

      - **Description:** Hide tool descriptions, showing only the tool names.
- **`/privacy`**
  - **Description:** Display the Privacy Notice and allow users to select whether they consent to the collection of their data for service improvement purposes.
- **`/quit`** (or **`/exit`**)

  - **Description:** Exit Gemini CLI.
- **`/vim`**
  - **Description:** Toggle vim mode on or off. When vim mode is enabled, the input area supports vim-style navigation and editing commands in both NORMAL and INSERT modes.
  - **Features:**
    - **NORMAL mode:** Navigate with `h`, `j`, `k`, `l`; jump by words with `w`, `b`, `e`; go to line start/end with `0`, `$`, `^`; go to specific lines with `G` (or `gg` for first line)
    - **INSERT mode:** Standard text input with escape to return to NORMAL mode
    - **Editing commands:** Delete with `x`, change with `c`, insert with `i`, `a`, `o`, `O`; complex operations like `dd`, `cc`, `dw`, `cw`
    - **Count support:** Prefix commands with numbers (e.g., `3h`, `5w`, `10G`)
    - **Repeat last command:** Use `.` to repeat the last editing operation
    - **Persistent setting:** Vim mode preference is saved to `~/.gemini/settings.json` and restored between sessions
  - **Status indicator:** When enabled, shows `[NORMAL]` or `[INSERT]` in the footer
- **`/init`**
  - **Description:** To help users easily create a `GEMINI.md` file, this command analyzes the current directory and generates a tailored context file, making it simpler for them to provide project-specific instructions to the Gemini agent.

### Custom Commands [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/commands.html\#custom-commands)

Custom commands allow you to create personalized shortcuts for your most-used prompts. For detailed instructions on how to create, manage, and use them, please see the dedicated [Custom Commands documentation](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html).

## Input Prompt Shortcuts [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/commands.html\#input-prompt-shortcuts)

These shortcuts apply directly to the input prompt for text manipulation.

- **Undo:**
  - **Keyboard shortcut:** Press **Ctrl+z** to undo the last action in the input prompt.
- **Redo:**
  - **Keyboard shortcut:** Press **Ctrl+Shift+Z** to redo the last undone action in the input prompt.

## At commands ( `@`) [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/commands.html\#at-commands-)

At commands are used to include the content of files or directories as part of your prompt to Gemini. These commands include git-aware filtering.

- **`@<path_to_file_or_directory>`**
  - **Description:** Inject the content of the specified file or files into your current prompt. This is useful for asking questions about specific code, text, or collections of files.
  - **Examples:**
    - `@path/to/your/file.txt Explain this text.`
    - `@src/my_project/ Summarize the code in this directory.`
    - `What is this file about? @README.md`
  - **Details:**
    - If a path to a single file is provided, the content of that file is read.
    - If a path to a directory is provided, the command attempts to read the content of files within that directory and any subdirectories.
    - Spaces in paths should be escaped with a backslash (e.g., `@My\ Documents/file.txt`).
    - The command uses the `read_many_files` tool internally. The content is fetched and then inserted into your query before being sent to the Gemini model.
    - **Git-aware filtering:** By default, git-ignored files (like `node_modules/`, `dist/`, `.env`, `.git/`) are excluded. This behavior can be changed via the `context.fileFiltering` settings.
    - **File types:** The command is intended for text-based files. While it might attempt to read any file, binary files or very large files might be skipped or truncated by the underlying `read_many_files` tool to ensure performance and relevance. The tool indicates if files were skipped.
  - **Output:** The CLI will show a tool call message indicating that `read_many_files` was used, along with a message detailing the status and the path(s) that were processed.
- **`@` (Lone at symbol)**
  - **Description:** If you type a lone `@` symbol without a path, the query is passed as-is to the Gemini model. This might be useful if you are specifically talking _about_ the `@` symbol in your prompt.

### Error handling for `@` commands [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/commands.html\#error-handling-for--commands)

- If the path specified after `@` is not found or is invalid, an error message will be displayed, and the query might not be sent to the Gemini model, or it will be sent without the file content.
- If the `read_many_files` tool encounters an error (e.g., permission issues), this will also be reported.

## Shell mode & passthrough commands ( `!`) [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/commands.html\#shell-mode--passthrough-commands-)

The `!` prefix lets you interact with your system’s shell directly from within Gemini CLI.

- **`!<shell_command>`**
  - **Description:** Execute the given `<shell_command>` using `bash` on Linux/macOS or `cmd.exe` on Windows. Any output or errors from the command are displayed in the terminal.
  - **Examples:**
    - `!ls -la` (executes `ls -la` and returns to Gemini CLI)
    - `!git status` (executes `git status` and returns to Gemini CLI)
- **`!` (Toggle shell mode)**
  - **Description:** Typing `!` on its own toggles shell mode.

    - **Entering shell mode:**
      - When active, shell mode uses a different coloring and a “Shell Mode Indicator”.
      - While in shell mode, text you type is interpreted directly as a shell command.
    - **Exiting shell mode:**
      - When exited, the UI reverts to its standard appearance and normal Gemini CLI behavior resumes.
- **Caution for all `!` usage:** Commands you execute in shell mode have the same permissions and impact as if you ran them directly in your terminal.

- **Environment Variable:** When a command is executed via `!` or in shell mode, the `GEMINI_CLI=1` environment variable is set in the subprocess’s environment. This allows scripts or tools to detect if they are being run from within the Gemini CLI.

## Gemini CLI Extensions Guide
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Gemini CLI Extensions

_This documentation is up-to-date with the v0.4.0 release._

Gemini CLI extensions package prompts, MCP servers, and custom commands into a familiar and user-friendly format. With extensions, you can expand the capabilities of Gemini CLI and share those capabilities with others. They are designed to be easily installable and shareable.

See [getting started docs](https://google-gemini.github.io/gemini-cli/docs/extensions/getting-started-extensions.html) for a guide on creating your first extension.

See [releasing docs](https://google-gemini.github.io/gemini-cli/docs/extensions/extension-releasing.html) for an advanced guide on setting up GitHub releases.

## Extension management [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#extension-management)

We offer a suite of extension management tools using `gemini extensions` commands.

Note that these commands are not supported from within the CLI, although you can list installed extensions using the `/extensions list` subcommand.

Note that all of these commands will only be reflected in active CLI sessions on restart.

### Installing an extension [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#installing-an-extension)

You can install an extension using `gemini extensions install` with either a GitHub URL or a local path\`.

Note that we create a copy of the installed extension, so you will need to run `gemini extensions update` to pull in changes from both locally-defined extensions and those on GitHub.

NOTE: If you are installing an extension from GitHub, you’ll need to have `git` installed on your machine. See [git installation instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) for help.

```
gemini extensions install https://github.com/gemini-cli-extensions/security

```

This will install the Gemini CLI Security extension, which offers support for a `/security:analyze` command.

### Uninstalling an extension [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#uninstalling-an-extension)

To uninstall, run `gemini extensions uninstall extension-name`, so, in the case of the install example:

```
gemini extensions uninstall gemini-cli-security

```

### Disabling an extension [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#disabling-an-extension)

Extensions are, by default, enabled across all workspaces. You can disable an extension entirely or for specific workspace.

For example, `gemini extensions disable extension-name` will disable the extension at the user level, so it will be disabled everywhere. `gemini extensions disable extension-name --scope=workspace` will only disable the extension in the current workspace.

### Enabling an extension [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#enabling-an-extension)

You can enable extensions using `gemini extensions enable extension-name`. You can also enable an extension for a specific workspace using `gemini extensions enable extension-name --scope=workspace` from within that workspace.

This is useful if you have an extension disabled at the top-level and only enabled in specific places.

### Updating an extension [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#updating-an-extension)

For extensions installed from a local path or a git repository, you can explicitly update to the latest version (as reflected in the `gemini-extension.json` `version` field) with `gemini extensions update extension-name`.

You can update all extensions with:

```
gemini extensions update --all

```

## Extension creation [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#extension-creation)

We offer commands to make extension development easier.

### Create a boilerplate extension [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#create-a-boilerplate-extension)

We offer several example extensions `context`, `custom-commands`, `exclude-tools` and `mcp-server`. You can view these examples [here](https://github.com/google-gemini/gemini-cli/tree/main/packages/cli/src/commands/extensions/examples).

To copy one of these examples into a development directory using the type of your choosing, run:

```
gemini extensions new path/to/directory custom-commands

```

### Link a local extension [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#link-a-local-extension)

The `gemini extensions link` command will create a symbolic link from the extension installation directory to the development path.

This is useful so you don’t have to run `gemini extensions update` every time you make changes you’d like to test.

```
gemini extensions link path/to/directory

```

## How it works [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#how-it-works)

On startup, Gemini CLI looks for extensions in `<home>/.gemini/extensions`

Extensions exist as a directory that contains a `gemini-extension.json` file. For example:

`<home>/.gemini/extensions/my-extension/gemini-extension.json`

### `gemini-extension.json` [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#gemini-extensionjson)

The `gemini-extension.json` file contains the configuration for the extension. The file has the following structure:

```
{
  "name": "my-extension",
  "version": "1.0.0",
  "mcpServers": {
    "my-server": {
      "command": "node my-server.js"
    }
  },
  "contextFileName": "GEMINI.md",
  "excludeTools": ["run_shell_command"]
}

```

- `name`: The name of the extension. This is used to uniquely identify the extension and for conflict resolution when extension commands have the same name as user or project commands. The name should be lowercase or numbers and use dashes instead of underscores or spaces. This is how users will refer to your extension in the CLI. Note that we expect this name to match the extension directory name.
- `version`: The version of the extension.
- `mcpServers`: A map of MCP servers to configure. The key is the name of the server, and the value is the server configuration. These servers will be loaded on startup just like MCP servers configured in a [`settings.json` file](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html). If both an extension and a `settings.json` file configure an MCP server with the same name, the server defined in the `settings.json` file takes precedence.

  - Note that all MCP server configuration options are supported except for `trust`.
- `contextFileName`: The name of the file that contains the context for the extension. This will be used to load the context from the extension directory. If this property is not used but a `GEMINI.md` file is present in your extension directory, then that file will be loaded.
- `excludeTools`: An array of tool names to exclude from the model. You can also specify command-specific restrictions for tools that support it, like the `run_shell_command` tool. For example, `"excludeTools": ["run_shell_command(rm -rf)"]` will block the `rm -rf` command. Note that this differs from the MCP server `excludeTools` functionality, which can be listed in the MCP server config.

When Gemini CLI starts, it loads all the extensions and merges their configurations. If there are any conflicts, the workspace configuration takes precedence.

### Custom commands [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#custom-commands)

Extensions can provide [custom commands](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html) by placing TOML files in a `commands/` subdirectory within the extension directory. These commands follow the same format as user and project custom commands and use standard naming conventions.

**Example**

An extension named `gcp` with the following structure:

```
.gemini/extensions/gcp/
├── gemini-extension.json
└── commands/
    ├── deploy.toml
    └── gcs/
        └── sync.toml

```

Would provide these commands:

- `/deploy` \- Shows as `[gcp] Custom command from deploy.toml` in help
- `/gcs:sync` \- Shows as `[gcp] Custom command from sync.toml` in help

### Conflict resolution [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#conflict-resolution)

Extension commands have the lowest precedence. When a conflict occurs with user or project commands:

1. **No conflict**: Extension command uses its natural name (e.g., `/deploy`)
2. **With conflict**: Extension command is renamed with the extension prefix (e.g., `/gcp.deploy`)

For example, if both a user and the `gcp` extension define a `deploy` command:

- `/deploy` \- Executes the user’s deploy command
- `/gcp.deploy` \- Executes the extension’s deploy command (marked with `[gcp]` tag)

## Variables [Anchor](https://google-gemini.github.io/gemini-cli/docs/extensions/\#variables)

Gemini CLI extensions allow variable substitution in `gemini-extension.json`. This can be useful if e.g., you need the current directory to run an MCP server using `"cwd": "${extensionPath}${/}run.ts"`.

**Supported variables:**

| variable | description |
| --- | --- |
| `${extensionPath}` | The fully-qualified path of the extension in the user’s filesystem e.g., ‘/Users/username/.gemini/extensions/example-extension’. This will not unwrap symlinks. |
| `${workspacePath}` | The fully-qualified path of the current workspace. |
| `${/} or ${pathSeparator}` | The path separator (differs per OS). |

## Gemini CLI Release Notes
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Gemini CLI Changelog

Wondering what’s new in Gemini CLI? This document provides key highlights and notable changes to Gemini CLI.

## v0.7.0 - Gemini CLI weekly update - 2025-09-22 [Anchor](https://google-gemini.github.io/gemini-cli/docs/changelogs/\#v070---gemini-cli-weekly-update---2025-09-22)

- 🎉 **Build your own Gemini CLI IDE plugin:** We’ve published a spec for creating IDE plugins to enable rich context-aware experiences and native in-editor diffing in your IDE of choice. ( [pr](https://github.com/google-gemini/gemini-cli/pull/8479) by [@skeshive](https://github.com/skeshive))
- 🎉 **Gemini CLI extensions**
  - **Flutter:** An early version to help you create, build, test, and run Flutter apps with Gemini CLI ( [extension](https://github.com/flutter/gemini-cli-extension))
  - **nanobanana:** Integrate nanobanana into Gemini CLI ( [extension](https://github.com/gemini-cli-extensions/nanobanana))
- **Telemetry config via environment:** Manage telemetry settings using environment variables for a more flexible setup. ( [docs](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/telemetry.md#configuration), [pr](https://github.com/google-gemini/gemini-cli/pull/9113) by [@jerop](https://github.com/jerop))
- **​​Experimental todos:** Track and display progress on complex tasks with a managed checklist. Off by default but can be enabled via `"useWriteTodos": true` ( [pr](https://github.com/google-gemini/gemini-cli/pull/8761) by [@anj-s](https://github.com/anj-s))
- **Share chat support for tools:** Using `/chat share` will now also render function calls and responses in the final markdown file. ( [pr](https://github.com/google-gemini/gemini-cli/pull/8693) by [@rramkumar1](https://github.com/rramkumar1))
- **Citations:** Now enabled for all users ( [pr](https://github.com/google-gemini/gemini-cli/pull/8570) by [@scidomino](https://github.com/scidomino))
- **Custom commands in Headless Mode:** Run custom slash commands directly from the command line in non-interactive mode: `gemini "/joke Chuck Norris"` ( [pr](https://github.com/google-gemini/gemini-cli/pull/8305) by [@capachino](https://github.com/capachino))
- **Small features, polish, reliability & bug fixes:** A large amount of changes, smaller features, UI updates, reliability and bug fixes + general polish made it in this week!

## v0.6.0 - Gemini CLI weekly update - 2025-09-15 [Anchor](https://google-gemini.github.io/gemini-cli/docs/changelogs/\#v060---gemini-cli-weekly-update---2025-09-15)

- 🎉 **Higher limits for Google AI Pro and Ultra subscribers:** We’re psyched to finally announce that Google AI Pro and AI Ultra subscribers now get access to significantly higher 2.5 quota limits for Gemini CLI!

  - **Announcement:** [https://blog.google/technology/developers/gemini-cli-code-assist-higher-limits/](https://blog.google/technology/developers/gemini-cli-code-assist-higher-limits/)
- 🎉 **Gemini CLI Databases and BigQuery Extensions:** Connect Gemini CLI to all of your cloud data with Gemini CLI.

  - Announcement and how to get started with each of the below extensions: [https://cloud.google.com/blog/products/databases/gemini-cli-extensions-for-google-data-cloud?e=48754805](https://cloud.google.com/blog/products/databases/gemini-cli-extensions-for-google-data-cloud?e=48754805)
  - **AlloyDB:** Interact, manage and observe AlloyDB for PostgreSQL databases ( [manage](https://github.com/gemini-cli-extensions/alloydb#configuration), [observe](https://github.com/gemini-cli-extensions/alloydb-observability#configuration))
  - **BigQuery:** Connect and query your BigQuery datasets or utilize a sub-agent for contextual insights ( [query](https://github.com/gemini-cli-extensions/bigquery-data-analytics#configuration), [sub-agent](https://github.com/gemini-cli-extensions/bigquery-conversational-analytics))
  - **Cloud SQL:** Interact, manage and observe Cloud SQL for PostgreSQL ( [manage](https://github.com/gemini-cli-extensions/cloud-sql-postgresql#configuration), [observe](https://github.com/gemini-cli-extensions/cloud-sql-postgresql-observability#configuration)), Cloud SQL for MySQL ( [manage](https://github.com/gemini-cli-extensions/cloud-sql-mysql#configuration), [observe](https://github.com/gemini-cli-extensions/cloud-sql-mysql-observability#configuration)) and Cloud SQL for SQL Server ( [manage](https://github.com/gemini-cli-extensions/cloud-sql-sqlserver#configuration), [observe](https://github.com/gemini-cli-extensions/cloud-sql-sqlserver-observability#configuration)) databases.
  - **Dataplex:** Discover, manage, and govern data and AI artifacts ( [extension](https://github.com/gemini-cli-extensions/dataplex#configuration))
  - **Firestore:** Interact with Firestore databases, collections and documents ( [extension](https://github.com/gemini-cli-extensions/firestore-native#configuration))
  - **Looker:** Query data, run Looks and create dashboards ( [extension](https://github.com/gemini-cli-extensions/looker#configuration))
  - **MySQL:** Interact with MySQL databases ( [extension](https://github.com/gemini-cli-extensions/mysql#configuration))
  - **Postgres:** Interact with PostgreSQL databases ( [extension](https://github.com/gemini-cli-extensions/postgres#configuration))
  - **Spanner:** Interact with Spanner databases ( [extension](https://github.com/gemini-cli-extensions/spanner#configuration))
  - **SQL Server:** Interact with SQL Server databases ( [extension](https://github.com/gemini-cli-extensions/sql-server#configuration))
  - **MCP Toolbox:** Configure and load custom tools for more than 30+ data sources ( [extension](https://github.com/gemini-cli-extensions/mcp-toolbox#configuration))
- **JSON output mode:** Have Gemini CLI output JSON with `--output-format json` when invoked headlessly for easy parsing and post-processing. Includes response, stats and errors. ( [pr](https://github.com/google-gemini/gemini-cli/pull/8119) by [@jerop](https://github.com/jerop))
- **Keybinding triggered approvals:** When you use shortcuts ( `shift+y` or `shift+tab`) to activate YOLO/auto-edit modes any pending confirmation dialogs will now approve. ( [pr](https://github.com/google-gemini/gemini-cli/pull/6665) by [@bulkypanda](https://github.com/bulkypanda))
- |     |     |
| --- | --- |
| **Chat sharing:** Convert the current conversation to a Markdown or JSON file with \_/chat share <file.md | file.json>\_ ( [pr](https://github.com/google-gemini/gemini-cli/pull/8139) by [@rramkumar1](https://github.com/rramkumar1)) |

- **Prompt search:** Search your prompt history using `ctrl+r`. ( [pr](https://github.com/google-gemini/gemini-cli/pull/5539) by [@Aisha630](https://github.com/Aisha630))
- **Input undo/redo:** Recover accidentally deleted text in the input prompt using `ctrl+z` (undo) and `ctrl+shift+z` (redo). ( [pr](https://github.com/google-gemini/gemini-cli/pull/4625) by [@masiafrest](https://github.com/masiafrest))
- **Loop detection confirmation:** When loops are detected you are now presented with a dialog to disable detection for the current session. ( [pr](https://github.com/google-gemini/gemini-cli/pull/8231) by [@SandyTao520](https://github.com/SandyTao520))
- **Direct to Google Cloud Telemetry:** Directly send telemetry to Google Cloud for a simpler and more streamlined setup. ( [pr](https://github.com/google-gemini/gemini-cli/pull/8541) by [@jerop](https://github.com/jerop))
- **Visual Mode Indicator Revamp:** ‘shell’, ‘accept edits’ and ‘yolo’ modes now have colors to match their impact / usage. Input box now also updates. ( [shell](https://imgur.com/a/DovpVF1), [accept-edits](https://imgur.com/a/33KDz3J), [yolo](https://imgur.com/a/tbFwIWp), [pr](https://github.com/google-gemini/gemini-cli/pull/8200) by [@miguelsolorio](https://github.com/miguelsolorio))
- **Small features, polish, reliability & bug fixes:** A large amount of changes, smaller features, UI updates, reliability and bug fixes + general polish made it in this week!

## v0.5.0 - Gemini CLI weekly update - 2025-09-08 [Anchor](https://google-gemini.github.io/gemini-cli/docs/changelogs/\#v050---gemini-cli-weekly-update---2025-09-08)

- 🎉 **FastMCP + Gemini CLI** 🎉: Quickly install and manage your Gemini CLI MCP servers with FastMCP ( [video](https://imgur.com/a/m8QdCPh), [pr](https://github.com/jlowin/fastmcp/pull/1709) by [@jackwotherspoon](https://github.com/jackwotherspoon) **)**
  - Getting started: [https://gofastmcp.com/integrations/gemini-cli](https://gofastmcp.com/integrations/gemini-cli)
- **Positional Prompt for Non-Interactive:** Seamlessly invoke Gemini CLI headlessly via `gemini "Hello"`. Synonymous with passing `-p`. ( [gif](https://imgur.com/a/hcBznpB), [pr](https://github.com/google-gemini/gemini-cli/pull/7668) by [@allenhutchison](https://github.com/allenhutchison))
- **Experimental Tool output truncation:** Enable truncating shell tool outputs and saving full output to a file by setting `"enableToolOutputTruncation": true `( [pr](https://github.com/google-gemini/gemini-cli/pull/8039) by [@SandyTao520](https://github.com/SandyTao520))
- **Edit Tool improvements:** Gemini CLI’s ability to edit files should now be far more capable. ( [pr](https://github.com/google-gemini/gemini-cli/pull/7679) by [@silviojr](https://github.com/silviojr))
- **Custom witty messages:** The feature you’ve all been waiting for… Personalized witty loading messages via `"ui": { "customWittyPhrases": ["YOLO"]}` in `settings.json`. ( [pr](https://github.com/google-gemini/gemini-cli/pull/7641) by [@JayadityaGit](https://github.com/JayadityaGit))
- **Nested .gitignore File Handling:** Nested `.gitignore` files are now respected. ( [pr](https://github.com/google-gemini/gemini-cli/pull/7645) by [@gsquared94](https://github.com/gsquared94))
- **Enforced authentication:** System administrators can now mandate a specific authentication method via `"enforcedAuthType": "oauth-personal|gemini-api-key|…"` in `settings.json`. ( [pr](https://github.com/google-gemini/gemini-cli/pull/6564) by [@chrstnb](https://github.com/chrstnb))
- **A2A development-tool extension:** An RFC for an Agent2Agent ( [A2A](https://a2a-protocol.org/latest/)) powered extension for developer tool use cases. ( [feedback](https://github.com/google-gemini/gemini-cli/discussions/7822), [pr](https://github.com/google-gemini/gemini-cli/pull/7817) by [@skeshive](https://github.com/skeshive))
- \*\*Hands on Codelab: \*\* [https://codelabs.developers.google.com/gemini-cli-hands-on](https://codelabs.developers.google.com/gemini-cli-hands-on)
- **Small features, polish, reliability & bug fixes:** A large amount of changes, smaller features, UI updates, reliability and bug fixes + general polish made it in this week!

## v0.4.0 - Gemini CLI weekly update - 2025-09-01 [Anchor](https://google-gemini.github.io/gemini-cli/docs/changelogs/\#v040---gemini-cli-weekly-update---2025-09-01)

- 🎉 **Gemini CLI CloudRun and Security Integrations** 🎉: Automate app deployment and security analysis with CloudRun and Security extension integrations. Once installed deploy your app to the cloud with `/deploy` and find and fix security vulnerabilities with `/security:analyze`.

  - Announcement and how to get started: [https://cloud.google.com/blog/products/ai-machine-learning/automate-app-deployment-and-security-analysis-with-new-gemini-cli-extensions](https://cloud.google.com/blog/products/ai-machine-learning/automate-app-deployment-and-security-analysis-with-new-gemini-cli-extensions)
- **Experimental**
  - **Edit Tool:** Give our new edit tool a try by setting `"useSmartEdit": true` in `settings.json`! ( [feedback](https://github.com/google-gemini/gemini-cli/discussions/7758), [pr](https://github.com/google-gemini/gemini-cli/pull/6823) by [@silviojr](https://github.com/silviojr))
  - **Model talking to itself fix:** We’ve removed a model workaround that would encourage Gemini CLI to continue conversations on your behalf. This may be disruptive and can be disabled via `"skipNextSpeakerCheck": false` in your `settings.json` ( [feedback](https://github.com/google-gemini/gemini-cli/discussions/6666), [pr](https://github.com/google-gemini/gemini-cli/pull/7614) by [@SandyTao520](https://github.com/SandyTao520))
  - **Prompt completion:** Get real-time AI suggestions to complete your prompts as you type. Enable it with `"general": { "enablePromptCompletion": true }` and share your feedback! ( [gif](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*hvegW7YXOg6N_beUWhTdxA.gif), [pr](https://github.com/google-gemini/gemini-cli/pull/4691) by [@3ks](https://github.com/3ks))
- **Footer visibility configuration:** Customize the CLI’s footer look and feel in `settings.json` ( [pr](https://github.com/google-gemini/gemini-cli/pull/7419) by [@miguelsolorio](https://github.com/miguelsolorio))

  - `hideCWD`: hide current working directory.
  - `hideSandboxStatus`: hide sandbox status.
  - `hideModelInfo`: hide current model information.
  - `hideContextSummary`: hide request context summary.
- **Citations:** For enterprise Code Assist licenses users will now see citations in their responses by default. Enable this yourself with `"showCitations": true` ( [pr](https://github.com/google-gemini/gemini-cli/pull/7350) by [@scidomino](https://github.com/scidomino))
- **Pro Quota Ddalog:** Handle daily Pro model usage limits with an interactive dialog that lets you immediately switch auth or fallback. ( [pr](https://github.com/google-gemini/gemini-cli/pull/7094) by [@JayadityaGit](https://github.com/JayadityaGit))
- **Custom commands @:** Embed local file or directory content directly into your custom command prompts using `@{path}` syntax ( [gif](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*GosBAo2SjMfFffAnzT7ZMg.gif), [pr](https://github.com/google-gemini/gemini-cli/pull/6716) by [@abhipatel12](https://github.com/abhipatel12))
- **2.5 Flash Lite support:** You can now use the `gemini-2.5-flash-lite` model for Gemini CLI via `gemini -m …`. ( [gif](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*P4SKwnrsyBuULoHrFqsFKQ.gif), [pr](https://github.com/google-gemini/gemini-cli/pull/4652) by [@psinha40898](https://github.com/psinha40898))
- **CLI streamlining:** We have deprecated a number of command line arguments in favor of `settings.json` alternatives. We will remove these arguments in a future release. See the PR for the full list of deprecations. ( [pr](https://github.com/google-gemini/gemini-cli/pull/7360) by [@allenhutchison](https://github.com/allenhutchison))
- **JSON session summary:** Track and save detailed CLI session statistics to a JSON file for performance analysis with `--session-summary <path>` ( [pr](https://github.com/google-gemini/gemini-cli/pull/7347) by [@leehagoodjames](https://github.com/leehagoodjames))
- **Robust keyboard handling:** More reliable and consistent behavior for arrow keys, special keys (Home, End, etc.), and modifier combinations across various terminals. ( [pr](https://github.com/google-gemini/gemini-cli/pull/7118) by [@deepankarsharma](https://github.com/deepankarsharma))
- **MCP loading indicator:** Provides visual feedback during CLI initialization when connecting to multiple servers. ( [pr](https://github.com/google-gemini/gemini-cli/pull/6923) by [@swissspidy](https://github.com/swissspidy))
- **Small features, polish, reliability & bug fixes:** A large amount of changes, smaller features, UI updates, reliability and bug fixes + general polish made it in this week!

## Gemini CLI Tools Guide
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Gemini CLI tools

The Gemini CLI includes built-in tools that the Gemini model uses to interact with your local environment, access information, and perform actions. These tools enhance the CLI’s capabilities, enabling it to go beyond text generation and assist with a wide range of tasks.

## Overview of Gemini CLI tools [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/\#overview-of-gemini-cli-tools)

In the context of the Gemini CLI, tools are specific functions or modules that the Gemini model can request to be executed. For example, if you ask Gemini to “Summarize the contents of `my_document.txt`,” the model will likely identify the need to read that file and will request the execution of the `read_file` tool.

The core component ( `packages/core`) manages these tools, presents their definitions (schemas) to the Gemini model, executes them when requested, and returns the results to the model for further processing into a user-facing response.

These tools provide the following capabilities:

- **Access local information:** Tools allow Gemini to access your local file system, read file contents, list directories, etc.
- **Execute commands:** With tools like `run_shell_command`, Gemini can run shell commands (with appropriate safety measures and user confirmation).
- **Interact with the web:** Tools can fetch content from URLs.
- **Take actions:** Tools can modify files, write new files, or perform other actions on your system (again, typically with safeguards).
- **Ground responses:** By using tools to fetch real-time or specific local data, Gemini’s responses can be more accurate, relevant, and grounded in your actual context.

## How to use Gemini CLI tools [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/\#how-to-use-gemini-cli-tools)

To use Gemini CLI tools, provide a prompt to the Gemini CLI. The process works as follows:

1. You provide a prompt to the Gemini CLI.
2. The CLI sends the prompt to the core.
3. The core, along with your prompt and conversation history, sends a list of available tools and their descriptions/schemas to the Gemini API.
4. The Gemini model analyzes your request. If it determines that a tool is needed, its response will include a request to execute a specific tool with certain parameters.
5. The core receives this tool request, validates it, and (often after user confirmation for sensitive operations) executes the tool.
6. The output from the tool is sent back to the Gemini model.
7. The Gemini model uses the tool’s output to formulate its final answer, which is then sent back through the core to the CLI and displayed to you.

You will typically see messages in the CLI indicating when a tool is being called and whether it succeeded or failed.

## Security and confirmation [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/\#security-and-confirmation)

Many tools, especially those that can modify your file system or execute commands ( `write_file`, `edit`, `run_shell_command`), are designed with safety in mind. The Gemini CLI will typically:

- **Require confirmation:** Prompt you before executing potentially sensitive operations, showing you what action is about to be taken.
- **Utilize sandboxing:** All tools are subject to restrictions enforced by sandboxing (see [Sandboxing in the Gemini CLI](https://google-gemini.github.io/gemini-cli/docs/cli/sandbox.html)). This means that when operating in a sandbox, any tools (including MCP servers) you wish to use must be available _inside_ the sandbox environment. For example, to run an MCP server through `npx`, the `npx` executable must be installed within the sandbox’s Docker image or be available in the `sandbox-exec` environment.

It’s important to always review confirmation prompts carefully before allowing a tool to proceed.

## Learn more about Gemini CLI’s tools [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/\#learn-more-about-gemini-clis-tools)

Gemini CLI’s built-in tools can be broadly categorized as follows:

- **[File System Tools](https://google-gemini.github.io/gemini-cli/docs/tools/file-system.html):** For interacting with files and directories (reading, writing, listing, searching, etc.).
- **[Shell Tool](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html) ( `run_shell_command`):** For executing shell commands.
- **[Web Fetch Tool](https://google-gemini.github.io/gemini-cli/docs/tools/web-fetch.html) ( `web_fetch`):** For retrieving content from URLs.
- **[Web Search Tool](https://google-gemini.github.io/gemini-cli/docs/tools/web-search.html) ( `google_web_search`):** For searching the web.
- **[Multi-File Read Tool](https://google-gemini.github.io/gemini-cli/docs/tools/multi-file.html) ( `read_many_files`):** A specialized tool for reading content from multiple files or directories.
- **[Memory Tool](https://google-gemini.github.io/gemini-cli/docs/tools/memory.html) ( `save_memory`):** For saving and recalling information across sessions.

Additionally, these tools incorporate:

- **[MCP servers](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html)**: MCP servers act as a bridge between the Gemini model and your local environment or other services like APIs.
- **[Sandboxing](https://google-gemini.github.io/gemini-cli/docs/cli/sandbox.html)**: Sandboxing isolates the model and its changes from your environment to reduce potential risk.

## Gemini CLI Documentation Guide
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Gemini CLI

Within Gemini CLI, `packages/cli` is the frontend for users to send and receive prompts with the Gemini AI model and its associated tools. For a general overview of Gemini CLI, see the [main documentation page](https://google-gemini.github.io/gemini-cli/docs/).

## Basic features [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/\#basic-features)

- **[Commands](https://google-gemini.github.io/gemini-cli/docs/cli/commands.html):** A reference for all built-in slash commands (e.g., `/help`, `/chat`, `/tools`).
- **[Custom Commands](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html):** Create your own commands and shortcuts for frequently used prompts.
- **[Headless Mode](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html):** Use Gemini CLI programmatically for scripting and automation.
- **[Themes](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html):** Customizing the CLI’s appearance with different themes.
- **[Keyboard Shortcuts](https://google-gemini.github.io/gemini-cli/docs/cli/keyboard-shortcuts.html):** A reference for all keyboard shortcuts to improve your workflow.
- **[Tutorials](https://google-gemini.github.io/gemini-cli/docs/cli/tutorials.html):** Step-by-step guides for common tasks.

## Advanced features [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/\#advanced-features)

- **[Checkpointing](https://google-gemini.github.io/gemini-cli/docs/cli/checkpointing.html):** Automatically save and restore snapshots of your session and files.
- **[Enterprise Configuration](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html):** Deploying and manage Gemini CLI in an enterprise environment.
- **[Sandboxing](https://google-gemini.github.io/gemini-cli/docs/cli/sandbox.html):** Isolate tool execution in a secure, containerized environment.
- **[Telemetry](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html):** Configure observability to monitor usage and performance.
- **[Token Caching](https://google-gemini.github.io/gemini-cli/docs/cli/token-caching.html):** Optimize API costs by caching tokens.
- **[Trusted Folders](https://google-gemini.github.io/gemini-cli/docs/cli/trusted-folders.html):** A security feature to control which projects can use the full capabilities of the CLI.
- **[Ignoring Files (.geminiignore)](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-ignore.html):** Exclude specific files and directories from being accessed by tools.
- **[Context Files (GEMINI.md)](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html):** Provide persistent, hierarchical context to the model.

## Non-interactive mode [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/\#non-interactive-mode)

Gemini CLI can be run in a non-interactive mode, which is useful for scripting and automation. In this mode, you pipe input to the CLI, it executes the command, and then it exits.

The following example pipes a command to Gemini CLI from your terminal:

```
echo "What is fine tuning?" | gemini

```

You can also use the `--prompt` or `-p` flag:

```
gemini -p "What is fine tuning?"

```

For comprehensive documentation on headless usage, scripting, automation, and advanced examples, see the **[Headless Mode](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html)** guide.

## Gemini CLI Frequently Asked Questions
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Frequently Asked Questions (FAQ)

This page provides answers to common questions and solutions to frequent problems encountered while using Gemini CLI.

## General issues [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#general-issues)

### Why am I getting an `API error: 429 - Resource exhausted`? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#why-am-i-getting-an-api-error-429---resource-exhausted)

This error indicates that you have exceeded your API request limit. The Gemini API has rate limits to prevent abuse and ensure fair usage.

To resolve this, you can:

- **Check your usage:** Review your API usage in the Google AI Studio or your Google Cloud project dashboard.
- **Optimize your prompts:** If you are making many requests in a short period, try to batch your prompts or introduce delays between requests.
- **Request a quota increase:** If you consistently need a higher limit, you can request a quota increase from Google.

### Why am I getting an `ERR_REQUIRE_ESM` error when running `npm run start`? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#why-am-i-getting-an-err_require_esm-error-when-running-npm-run-start)

This error typically occurs in Node.js projects when there is a mismatch between CommonJS and ES Modules.

This is often due to a misconfiguration in your `package.json` or `tsconfig.json`. Ensure that:

1. Your `package.json` has `"type": "module"`.
2. Your `tsconfig.json` has `"module": "NodeNext"` or a compatible setting in the `compilerOptions`.

If the problem persists, try deleting your `node_modules` directory and `package-lock.json` file, and then run `npm install` again.

### Why don’t I see cached token counts in my stats output? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#why-dont-i-see-cached-token-counts-in-my-stats-output)

Cached token information is only displayed when cached tokens are being used. This feature is available for API key users (Gemini API key or Google Cloud Vertex AI) but not for OAuth users (such as Google Personal/Enterprise accounts like Google Gmail or Google Workspace, respectively). This is because the Gemini Code Assist API does not support cached content creation. You can still view your total token usage using the `/stats` command in Gemini CLI.

## Installation and updates [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#installation-and-updates)

### How do I update Gemini CLI to the latest version? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#how-do-i-update-gemini-cli-to-the-latest-version)

If you installed it globally via `npm`, update it using the command `npm install -g @google/gemini-cli@latest`. If you compiled it from source, pull the latest changes from the repository, and then rebuild using the command `npm run build`.

## Platform-specific issues [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#platform-specific-issues)

### Why does the CLI crash on Windows when I run a command like `chmod +x`? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#why-does-the-cli-crash-on-windows-when-i-run-a-command-like-chmod-x)

Commands like `chmod` are specific to Unix-like operating systems (Linux, macOS). They are not available on Windows by default.

To resolve this, you can:

- **Use Windows-equivalent commands:** Instead of `chmod`, you can use `icacls` to modify file permissions on Windows.
- **Use a compatibility layer:** Tools like Git Bash or Windows Subsystem for Linux (WSL) provide a Unix-like environment on Windows where these commands will work.

## Configuration [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#configuration)

### How do I configure my `GOOGLE_CLOUD_PROJECT`? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#how-do-i-configure-my-google_cloud_project)

You can configure your Google Cloud Project ID using an environment variable.

Set the `GOOGLE_CLOUD_PROJECT` environment variable in your shell:

```
export GOOGLE_CLOUD_PROJECT="your-project-id"

```

To make this setting permanent, add this line to your shell’s startup file (e.g., `~/.bashrc`, `~/.zshrc`).

### What is the best way to store my API keys securely? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#what-is-the-best-way-to-store-my-api-keys-securely)

Exposing API keys in scripts or checking them into source control is a security risk.

To store your API keys securely, you can:

- **Use a `.env` file:** Create a `.env` file in your project’s `.gemini` directory ( `.gemini/.env`) and store your keys there. Gemini CLI will automatically load these variables.
- **Use your system’s keyring:** For the most secure storage, use your operating system’s secret management tool (like macOS Keychain, Windows Credential Manager, or a secret manager on Linux). You can then have your scripts or environment load the key from the secure storage at runtime.

### Where are the Gemini CLI configuration and settings files stored? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#where-are-the-gemini-cli-configuration-and-settings-files-stored)

The Gemini CLI configuration is stored in two `settings.json` files:

1. In your home directory: `~/.gemini/settings.json`.
2. In your project’s root directory: `./.gemini/settings.json`.

Refer to [Gemini CLI Configuration](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html) for more details.

## Google AI Pro/Ultra and subscription FAQs [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#google-ai-proultra-and-subscription-faqs)

### Where can I learn more about my Google AI Pro or Google AI Ultra subscription? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#where-can-i-learn-more-about-my-google-ai-pro-or-google-ai-ultra-subscription)

To learn more about your Google AI Pro or Google AI Ultra subscription, visit **Manage subscription** in your [subscription settings](https://one.google.com/).

### How do I know if I have higher limits for Google AI Pro or Ultra? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#how-do-i-know-if-i-have-higher-limits-for-google-ai-pro-or-ultra)

If you’re subscribed to Google AI Pro or Ultra, you automatically have higher limits to Gemini Code Assist and Gemini CLI. These are shared across Gemini CLI and agent mode in the IDE. You can confirm you have higher limits by checking if you are still subscribed to Google AI Pro or Ultra in your [subscription settings](https://one.google.com/).

### What is the privacy policy for using Gemini Code Assist or Gemini CLI if I’ve subscribed to Google AI Pro or Ultra? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#what-is-the-privacy-policy-for-using-gemini-code-assist-or-gemini-cli-if-ive-subscribed-to-google-ai-pro-or-ultra)

To learn more about your privacy policy and terms of service governed by your subscription, visit [Gemini Code Assist: Terms of Service and Privacy Policies](https://developers.google.com/gemini-code-assist/resources/privacy-notices).

### I’ve upgraded to Google AI Pro or Ultra but it still says I am hitting quota limits. Is this a bug? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#ive-upgraded-to-google-ai-pro-or-ultra-but-it-still-says-i-am-hitting-quota-limits-is-this-a-bug)

The higher limits in your Google AI Pro or Ultra subscription are for Gemini 2.5 across both Gemini 2.5 Pro and Flash. They are shared quota across Gemini CLI and agent mode in Gemini Code Assist IDE extensions. You can learn more about quota limits for Gemini CLI, Gemini Code Assist and agent mode in Gemini Code Assist at [Quotas and limits](https://developers.google.com/gemini-code-assist/resources/quotas).

### If I upgrade to higher limits for Gemini CLI and Gemini Code Assist by purchasing a Google AI Pro or Ultra subscription, will Gemini start using my data to improve its machine learning models? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#if-i-upgrade-to-higher-limits-for-gemini-cli-and-gemini-code-assist-by-purchasing-a-google-ai-pro-or-ultra-subscription-will-gemini-start-using-my-data-to-improve-its-machine-learning-models)

Google does not use your data to improve Google’s machine learning models if you purchase a paid plan. Note: If you decide to remain on the free version of Gemini Code Assist, Gemini Code Assist for individuals, you can also opt out of using your data to improve Google’s machine learning models. See the [Gemini Code Assist for individuals privacy notice](https://developers.google.com/gemini-code-assist/resources/privacy-notice-gemini-code-assist-individuals) for more information.

## Not seeing your question? [Anchor](https://google-gemini.github.io/gemini-cli/docs/faq.html\#not-seeing-your-question)

Search the Gemini CLI [Issue tracker on GitHub](https://github.com/google-gemini/gemini-cli/issues). If you can’t find an issue similar to yours, consider creating a new GitHub Issue with a detailed description. Pull requests are also welcome!

## Gemini CLI IDE Integration
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# IDE Integration

Gemini CLI can integrate with your IDE to provide a more seamless and context-aware experience. This integration allows the CLI to understand your workspace better and enables powerful features like native in-editor diffing.

Currently, the only supported IDE is [Visual Studio Code](https://code.visualstudio.com/) and other editors that support VS Code extensions. To build support for other editors, see the [IDE Companion Extension Spec](https://google-gemini.github.io/gemini-cli/docs/ide-integration/ide-companion-spec.html).

## Features [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#features)

- **Workspace Context:** The CLI automatically gains awareness of your workspace to provide more relevant and accurate responses. This context includes:

  - The **10 most recently accessed files** in your workspace.
  - Your active cursor position.
  - Any text you have selected (up to a 16KB limit; longer selections will be truncated).
- **Native Diffing:** When Gemini suggests code modifications, you can view the changes directly within your IDE’s native diff viewer. This allows you to review, edit, and accept or reject the suggested changes seamlessly.

- **VS Code Commands:** You can access Gemini CLI features directly from the VS Code Command Palette ( `Cmd+Shift+P` or `Ctrl+Shift+P`):

  - `Gemini CLI: Run`: Starts a new Gemini CLI session in the integrated terminal.
  - `Gemini CLI: Accept Diff`: Accepts the changes in the active diff editor.
  - `Gemini CLI: Close Diff Editor`: Rejects the changes and closes the active diff editor.
  - `Gemini CLI: View Third-Party Notices`: Displays the third-party notices for the extension.

## Installation and Setup [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#installation-and-setup)

There are three ways to set up the IDE integration:

### 1\. Automatic Nudge (Recommended) [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#1-automatic-nudge-recommended)

When you run Gemini CLI inside a supported editor, it will automatically detect your environment and prompt you to connect. Answering “Yes” will automatically run the necessary setup, which includes installing the companion extension and enabling the connection.

### 2\. Manual Installation from CLI [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#2-manual-installation-from-cli)

If you previously dismissed the prompt or want to install the extension manually, you can run the following command inside Gemini CLI:

```
/ide install

```

This will find the correct extension for your IDE and install it.

### 3\. Manual Installation from a Marketplace [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#3-manual-installation-from-a-marketplace)

You can also install the extension directly from a marketplace.

- **For Visual Studio Code:** Install from the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=google.gemini-cli-vscode-ide-companion).
- **For VS Code Forks:** To support forks of VS Code, the extension is also published on the [Open VSX Registry](https://open-vsx.org/extension/google/gemini-cli-vscode-ide-companion). Follow your editor’s instructions for installing extensions from this registry.

> NOTE:
> The “Gemini CLI Companion” extension may appear towards the bottom of search results. If you don’t see it immediately, try scrolling down or sorting by “Newly Published”.
>
> After manually installing the extension, you must run `/ide enable` in the CLI to activate the integration.

## Usage [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#usage)

### Enabling and Disabling [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#enabling-and-disabling)

You can control the IDE integration from within the CLI:

- To enable the connection to the IDE, run:





```
/ide enable

```

- To disable the connection, run:





```
/ide disable

```


When enabled, Gemini CLI will automatically attempt to connect to the IDE companion extension.

### Checking the Status [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#checking-the-status)

To check the connection status and see the context the CLI has received from the IDE, run:

```
/ide status

```

If connected, this command will show the IDE it’s connected to and a list of recently opened files it is aware of.

(Note: The file list is limited to 10 recently accessed files within your workspace and only includes local files on disk.)

### Working with Diffs [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#working-with-diffs)

When you ask Gemini to modify a file, it can open a diff view directly in your editor.

**To accept a diff**, you can perform any of the following actions:

- Click the **checkmark icon** in the diff editor’s title bar.
- Save the file (e.g., with `Cmd+S` or `Ctrl+S`).
- Open the Command Palette and run **Gemini CLI: Accept Diff**.
- Respond with `yes` in the CLI when prompted.

**To reject a diff**, you can:

- Click the **‘x’ icon** in the diff editor’s title bar.
- Close the diff editor tab.
- Open the Command Palette and run **Gemini CLI: Close Diff Editor**.
- Respond with `no` in the CLI when prompted.

You can also **modify the suggested changes** directly in the diff view before accepting them.

If you select ‘Yes, allow always’ in the CLI, changes will no longer show up in the IDE as they will be auto-accepted.

## Using with Sandboxing [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#using-with-sandboxing)

If you are using Gemini CLI within a sandbox, please be aware of the following:

- **On macOS:** The IDE integration requires network access to communicate with the IDE companion extension. You must use a Seatbelt profile that allows network access.
- **In a Docker Container:** If you run Gemini CLI inside a Docker (or Podman) container, the IDE integration can still connect to the VS Code extension running on your host machine. The CLI is configured to automatically find the IDE server on `host.docker.internal`. No special configuration is usually required, but you may need to ensure your Docker networking setup allows connections from the container to the host.

## Troubleshooting [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#troubleshooting)

If you encounter issues with IDE integration, here are some common error messages and how to resolve them.

### Connection Errors [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#connection-errors)

- **Message:** `🔴 Disconnected: Failed to connect to IDE companion extension in [IDE Name]. Please ensure the extension is running. To install the extension, run /ide install.`
  - **Cause:** Gemini CLI could not find the necessary environment variables ( `GEMINI_CLI_IDE_WORKSPACE_PATH` or `GEMINI_CLI_IDE_SERVER_PORT`) to connect to the IDE. This usually means the IDE companion extension is not running or did not initialize correctly.
  - **Solution:**
    1. Make sure you have installed the **Gemini CLI Companion** extension in your IDE and that it is enabled.
    2. Open a new terminal window in your IDE to ensure it picks up the correct environment.
- **Message:** `🔴 Disconnected: IDE connection error. The connection was lost unexpectedly. Please try reconnecting by running /ide enable`
  - **Cause:** The connection to the IDE companion was lost.
  - **Solution:** Run `/ide enable` to try and reconnect. If the issue continues, open a new terminal window or restart your IDE.

### Configuration Errors [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#configuration-errors)

- **Message:** `🔴 Disconnected: Directory mismatch. Gemini CLI is running in a different location than the open workspace in [IDE Name]. Please run the CLI from one of the following directories: [List of directories]`
  - **Cause:** The CLI’s current working directory is outside the workspace you have open in your IDE.
  - **Solution:** `cd` into the same directory that is open in your IDE and restart the CLI.
- **Message:** `🔴 Disconnected: To use this feature, please open a workspace folder in [IDE Name] and try again.`
  - **Cause:** You have no workspace open in your IDE.
  - **Solution:** Open a workspace in your IDE and restart the CLI.

### General Errors [Anchor](https://google-gemini.github.io/gemini-cli/docs/ide-integration/\#general-errors)

- **Message:** `IDE integration is not supported in your current environment. To use this feature, run Gemini CLI in one of these supported IDEs: [List of IDEs]`
  - **Cause:** You are running Gemini CLI in a terminal or environment that is not a supported IDE.
  - **Solution:** Run Gemini CLI from the integrated terminal of a supported IDE, like VS Code.
- **Message:** `No installer is available for IDE. Please install the Gemini CLI Companion extension manually from the marketplace.`
  - **Cause:** You ran `/ide install`, but the CLI does not have an automated installer for your specific IDE.
  - **Solution:** Open your IDE’s extension marketplace, search for “Gemini CLI Companion”, and [install it manually](https://google-gemini.github.io/gemini-cli/docs/ide-integration/#3-manual-installation-from-a-marketplace).

## Gemini CLI Troubleshooting Guide
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Troubleshooting guide

This guide provides solutions to common issues and debugging tips, including topics on:

- Authentication or login errors
- Frequently asked questions (FAQs)
- Debugging tips
- Existing GitHub Issues similar to yours or creating new Issues

## Authentication or login errors [Anchor](https://google-gemini.github.io/gemini-cli/docs/troubleshooting.html\#authentication-or-login-errors)

- **Error: `Failed to login. Message: Request contains an invalid argument`**
  - Users with Google Workspace accounts or Google Cloud accounts
    associated with their Gmail accounts may not be able to activate the free
    tier of the Google Code Assist plan.
  - For Google Cloud accounts, you can work around this by setting
    `GOOGLE_CLOUD_PROJECT` to your project ID.
  - Alternatively, you can obtain the Gemini API key from
    [Google AI Studio](http://aistudio.google.com/app/apikey), which also includes a
    separate free tier.
- **Error: `UNABLE_TO_GET_ISSUER_CERT_LOCALLY` or `unable to get local issuer certificate`**
  - **Cause:** You may be on a corporate network with a firewall that intercepts and inspects SSL/TLS traffic. This often requires a custom root CA certificate to be trusted by Node.js.
  - **Solution:** Set the `NODE_EXTRA_CA_CERTS` environment variable to the absolute path of your corporate root CA certificate file.

    - Example: `export NODE_EXTRA_CA_CERTS=/path/to/your/corporate-ca.crt`

## Common error messages and solutions [Anchor](https://google-gemini.github.io/gemini-cli/docs/troubleshooting.html\#common-error-messages-and-solutions)

- **Error: `EADDRINUSE` (Address already in use) when starting an MCP server.**
  - **Cause:** Another process is already using the port that the MCP server is trying to bind to.
  - **Solution:**
    Either stop the other process that is using the port or configure the MCP server to use a different port.
- **Error: Command not found (when attempting to run Gemini CLI with `gemini`).**
  - **Cause:** Gemini CLI is not correctly installed or it is not in your system’s `PATH`.
  - **Solution:**
    The update depends on how you installed Gemini CLI:

    - If you installed `gemini` globally, check that your `npm` global binary directory is in your `PATH`. You can update Gemini CLI using the command `npm install -g @google/gemini-cli@latest`.
    - If you are running `gemini` from source, ensure you are using the correct command to invoke it (e.g., `node packages/cli/dist/index.js ...`). To update Gemini CLI, pull the latest changes from the repository, and then rebuild using the command `npm run build`.
- **Error: `MODULE_NOT_FOUND` or import errors.**
  - **Cause:** Dependencies are not installed correctly, or the project hasn’t been built.
  - **Solution:**
    1. Run `npm install` to ensure all dependencies are present.
    2. Run `npm run build` to compile the project.
    3. Verify that the build completed successfully with `npm run start`.
- **Error: “Operation not permitted”, “Permission denied”, or similar.**
  - **Cause:** When sandboxing is enabled, Gemini CLI may attempt operations that are restricted by your sandbox configuration, such as writing outside the project directory or system temp directory.
  - **Solution:** Refer to the [Configuration: Sandboxing](https://google-gemini.github.io/gemini-cli/docs/cli/sandbox.html) documentation for more information, including how to customize your sandbox configuration.
- **Gemini CLI is not running in interactive mode in “CI” environments**
  - **Issue:** The Gemini CLI does not enter interactive mode (no prompt appears) if an environment variable starting with `CI_` (e.g., `CI_TOKEN`) is set. This is because the `is-in-ci` package, used by the underlying UI framework, detects these variables and assumes a non-interactive CI environment.
  - **Cause:** The `is-in-ci` package checks for the presence of `CI`, `CONTINUOUS_INTEGRATION`, or any environment variable with a `CI_` prefix. When any of these are found, it signals that the environment is non-interactive, which prevents the Gemini CLI from starting in its interactive mode.
  - **Solution:** If the `CI_` prefixed variable is not needed for the CLI to function, you can temporarily unset it for the command. e.g., `env -u CI_TOKEN gemini`
- **DEBUG mode not working from project .env file**
  - **Issue:** Setting `DEBUG=true` in a project’s `.env` file doesn’t enable debug mode for gemini-cli.
  - **Cause:** The `DEBUG` and `DEBUG_MODE` variables are automatically excluded from project `.env` files to prevent interference with gemini-cli behavior.
  - **Solution:** Use a `.gemini/.env` file instead, or configure the `advanced.excludedEnvVars` setting in your `settings.json` to exclude fewer variables.

## Exit Codes [Anchor](https://google-gemini.github.io/gemini-cli/docs/troubleshooting.html\#exit-codes)

The Gemini CLI uses specific exit codes to indicate the reason for termination. This is especially useful for scripting and automation.

| Exit Code | Error Type | Description |
| --- | --- | --- |
| 41 | `FatalAuthenticationError` | An error occurred during the authentication process. |
| 42 | `FatalInputError` | Invalid or missing input was provided to the CLI. (non-interactive mode only) |
| 44 | `FatalSandboxError` | An error occurred with the sandboxing environment (e.g., Docker, Podman, or Seatbelt). |
| 52 | `FatalConfigError` | A configuration file ( `settings.json`) is invalid or contains errors. |
| 53 | `FatalTurnLimitedError` | The maximum number of conversational turns for the session was reached. (non-interactive mode only) |

## Debugging Tips [Anchor](https://google-gemini.github.io/gemini-cli/docs/troubleshooting.html\#debugging-tips)

- **CLI debugging:**
  - Use the `--verbose` flag (if available) with CLI commands for more detailed output.
  - Check the CLI logs, often found in a user-specific configuration or cache directory.
- **Core debugging:**
  - Check the server console output for error messages or stack traces.
  - Increase log verbosity if configurable.
  - Use Node.js debugging tools (e.g., `node --inspect`) if you need to step through server-side code.
- **Tool issues:**
  - If a specific tool is failing, try to isolate the issue by running the simplest possible version of the command or operation the tool performs.
  - For `run_shell_command`, check that the command works directly in your shell first.
  - For _file system tools_, verify that paths are correct and check the permissions.
- **Pre-flight checks:**
  - Always run `npm run preflight` before committing code. This can catch many common issues related to formatting, linting, and type errors.

## Existing GitHub Issues similar to yours or creating new Issues [Anchor](https://google-gemini.github.io/gemini-cli/docs/troubleshooting.html\#existing-github-issues-similar-to-yours-or-creating-new-issues)

If you encounter an issue that was not covered here in this _Troubleshooting guide_, consider searching the Gemini CLI [Issue tracker on GitHub](https://github.com/google-gemini/gemini-cli/issues). If you can’t find an issue similar to yours, consider creating a new GitHub Issue with a detailed description. Pull requests are also welcome!

## Gemini CLI Release Management
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Gemini CLI Releases

## Release Cadence and Tags [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#release-cadence-and-tags)

We will follow https://semver.org/ as closely as possible but will call out when or if we have to deviate from it. Our weekly releases will be minor version increments and any bug or hotfixes between releases will go out as patch versions on the most recent release.

Each Tuesday ~2000 UTC new Stable and Preview releases will be cut. The promotion flow is:

- Code is committed to main and pushed each night to nightly
- After no more than 1 week on main, code is promoted to the `preview` channel
- After 1 week the most recent `preview` channel is promoted to `stable` channel
- Patch fixes will be produced against both `preview` and `stable` as needed, with the final ‘patch’ version number incrementing each time.

### Preview [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#preview)

These releases will not have been fully vetted and may contain regressions or other outstanding issues. Please help us test and install with `preview` tag.

```
npm install -g @google/gemini-cli@preview

```

### Stable [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#stable)

This will be the full promotion of last week’s release + any bug fixes and validations. Use `latest` tag.

```
npm install -g @google/gemini-cli@latest

```

### Nightly [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#nightly)

- New releases will be published each day at UTC 0000. This will be all changes from the main branch as represented at time of release. It should be assumed there are pending validations and issues. Use `nightly` tag.

```
npm install -g @google/gemini-cli@nightly

```

## Weekly Release Promotion [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#weekly-release-promotion)

Each Tuesday, the on-call engineer will trigger the “Promote Release” workflow. This single action automates the entire weekly release process:

1. **Promotes Preview to Stable:** The workflow identifies the latest `preview` release and promotes it to `stable`. This becomes the new `latest` version on npm.
2. **Promotes Nightly to Preview:** The latest `nightly` release is then promoted to become the new `preview` version.
3. **Prepares for next Nightly:** A pull request is automatically created and merged to bump the version in `main` in preparation for the next nightly release.

This process ensures a consistent and reliable release cadence with minimal manual intervention.

### Source of Truth for Versioning [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#source-of-truth-for-versioning)

To ensure the highest reliability, the release promotion process uses the **NPM registry as the single source of truth** for determining the current version of each release channel ( `stable`, `preview`, and `nightly`).

1. **Fetch from NPM:** The workflow begins by querying NPM’s `dist-tags` ( `latest`, `preview`, `nightly`) to get the exact version strings for the packages currently available to users.
2. **Cross-Check for Integrity:** For each version retrieved from NPM, the workflow performs a critical integrity check:

   - It verifies that a corresponding **git tag** exists in the repository.
   - It verifies that a corresponding **GitHub Release** has been created.
3. **Halt on Discrepancy:** If either the git tag or the GitHub Release is missing for a version listed on NPM, the workflow will immediately fail. This strict check prevents promotions from a broken or incomplete previous release and alerts the on-call engineer to a release state inconsistency that must be manually resolved.
4. **Calculate Next Version:** Only after these checks pass does the workflow proceed to calculate the next semantic version based on the trusted version numbers retrieved from NPM.

This NPM-first approach, backed by integrity checks, makes the release process highly robust and prevents the kinds of versioning discrepancies that can arise from relying solely on git history or API outputs.

## Manual Releases [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#manual-releases)

For situations requiring a release outside of the regular nightly and weekly promotion schedule, and NOT already covered by patching process, you can use the `Release: Manual` workflow. This workflow provides a direct way to publish a specific version from any branch, tag, or commit SHA.

### How to Create a Manual Release [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#how-to-create-a-manual-release)

1. Navigate to the **Actions** tab of the repository.
2. Select the **Release: Manual** workflow from the list.
3. Click the **Run workflow** dropdown button.
4. Fill in the required inputs:
   - **Version**: The exact version to release (e.g., `v0.6.1`). This must be a valid semantic version with a `v` prefix.
   - **Ref**: The branch, tag, or full commit SHA to release from.
   - **NPM Channel**: The npm channel to publish to. The options are `preview`, `nightly`, `latest` (for stable releases), and `dev`. The default is `dev`.
   - **Dry Run**: Leave as `true` to run all steps without publishing, or set to `false` to perform a live release.
   - **Force Skip Tests**: Set to `true` to skip the test suite. This is not recommended for production releases.
   - **Skip GitHub Release**: Set to `true` to skip creating a GitHub release and create an npm release only.
5. Click **Run workflow**.

The workflow will then proceed to test (if not skipped), build, and publish the release. If the workflow fails during a non-dry run, it will automatically create a GitHub issue with the failure details.

## Rollback/Rollforward [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#rollbackrollforward)

In the event that a release has a critical regression, you can quickly roll back to a previous stable version or roll forward to a new patch by changing the npm `dist-tag`. The `Release: Change Tags` workflow provides a safe and controlled way to do this.

This is the preferred method for both rollbacks and rollforwards, as it does not require a full release cycle.

### How to Change a Release Tag [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#how-to-change-a-release-tag)

1. Navigate to the **Actions** tab of the repository.
2. Select the **Release: Change Tags** workflow from the list.
3. Click the **Run workflow** dropdown button.
4. Fill in the required inputs:
   - **Version**: The existing package version that you want to point the tag to (e.g., `0.5.0-preview-2`). This version **must** already be published to the npm registry.
   - **Channel**: The npm `dist-tag` to apply (e.g., `preview`, `stable`).
   - **Dry Run**: Leave as `true` to log the action without making changes, or set to `false` to perform the live tag change.
5. Click **Run workflow**.

The workflow will then run `npm dist-tag add` for both the `@google/gemini-cli` and `@google/gemini-cli-core` packages, pointing the specified channel to the specified version.

## Patching [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#patching)

If a critical bug that is already fixed on `main` needs to be patched on a `stable` or `preview` release, the process is now highly automated.

### How to Patch [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#how-to-patch)

#### 1\. Create the Patch Pull Request [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#1-create-the-patch-pull-request)

There are two ways to create a patch pull request:

**Option A: From a GitHub Comment (Recommended)**

After a pull request containing the fix has been merged, a maintainer can add a comment on that same PR with the following format:

`/patch [channel]`

- **channel** (optional):

  - _no channel_ \- patches both stable and preview channels (default, recommended for most fixes)
  - `both` \- patches both stable and preview channels (same as default)
  - `stable` \- patches only the stable channel
  - `preview` \- patches only the preview channel

Examples:

- `/patch` (patches both stable and preview - default)
- `/patch both` (patches both stable and preview - explicit)
- `/patch stable` (patches only stable)
- `/patch preview` (patches only preview)

The `Release: Patch from Comment` workflow will automatically find the merge commit SHA and trigger the `Release: Patch (1) Create PR` workflow. If the PR is not yet merged, it will post a comment indicating the failure.

**Option B: Manually Triggering the Workflow**

Navigate to the **Actions** tab and run the **Release: Patch (1) Create PR** workflow.

- **Commit**: The full SHA of the commit on `main` that you want to cherry-pick.
- **Channel**: The channel you want to patch ( `stable` or `preview`).

This workflow will automatically:

1. Find the latest release tag for the channel.
2. Create a release branch from that tag if one doesn’t exist (e.g., `release/v0.5.1-pr-12345`).
3. Create a new hotfix branch from the release branch.
4. Cherry-pick your specified commit into the hotfix branch.
5. Create a pull request from the hotfix branch back to the release branch.

#### 2\. Review and Merge [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#2-review-and-merge)

Review the automatically created pull request(s) to ensure the cherry-pick was successful and the changes are correct. Once approved, merge the pull request.

**Security Note:** The `release/*` branches are protected by branch protection rules. A pull request to one of these branches requires at least one review from a code owner before it can be merged. This ensures that no unauthorized code is released.

#### 2.5. Adding Multiple Commits to a Hotfix (Advanced) [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#25-adding-multiple-commits-to-a-hotfix-advanced)

If you need to include multiple fixes in a single patch release, you can add additional commits to the hotfix branch after the initial patch PR has been created:

1. **Start with the primary fix**: Use `/patch` (or `/patch both`) on the most important PR to create the initial hotfix branch and PR.

2. **Checkout the hotfix branch locally**:





```
git fetch origin
git checkout hotfix/v0.5.1/stable/cherry-pick-abc1234  # Use the actual branch name from the PR

```

3. **Cherry-pick additional commits**:





```
git cherry-pick <commit-sha-1>
git cherry-pick <commit-sha-2>
# Add as many commits as needed

```

4. **Push the updated branch**:





```
git push origin hotfix/v0.5.1/stable/cherry-pick-abc1234

```

5. **Test and review**: The existing patch PR will automatically update with your additional commits. Test thoroughly since you’re now releasing multiple changes together.

6. **Update the PR description**: Consider updating the PR title and description to reflect that it includes multiple fixes.


This approach allows you to group related fixes into a single patch release while maintaining full control over what gets included and how conflicts are resolved.

#### 3\. Automatic Release [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#3-automatic-release)

Upon merging the pull request, the `Release: Patch (2) Trigger` workflow is automatically triggered. It will then start the `Release: Patch (3) Release` workflow, which will:

1. Build and test the patched code.
2. Publish the new patch version to npm.
3. Create a new GitHub release with the patch notes.

This fully automated process ensures that patches are created and released consistently and reliably.

#### Troubleshooting: Older Branch Workflows [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#troubleshooting-older-branch-workflows)

**Issue**: If the patch trigger workflow fails with errors like “Resource not accessible by integration” or references to non-existent workflow files (e.g., `patch-release.yml`), this indicates the hotfix branch contains an outdated version of the workflow files.

**Root Cause**: When a PR is merged, GitHub Actions runs the workflow definition from the **source branch** (the hotfix branch), not from the target branch (the release branch). If the hotfix branch was created from an older release branch that predates workflow improvements, it will use the old workflow logic.

**Solutions**:

**Option 1: Manual Trigger (Quick Fix)**
Manually trigger the updated workflow from the branch with the latest workflow code:

```
# For a preview channel patch with tests skipped
gh workflow run release-patch-2-trigger.yml --ref <branch-with-updated-workflow> \
  --field ref="hotfix/v0.6.0-preview.2/preview/cherry-pick-abc1234" \
  --field workflow_ref=<branch-with-updated-workflow> \
  --field dry_run=false \
  --field force_skip_tests=true

# For a stable channel patch
gh workflow run release-patch-2-trigger.yml --ref <branch-with-updated-workflow> \
  --field ref="hotfix/v0.5.1/stable/cherry-pick-abc1234" \
  --field workflow_ref=<branch-with-updated-workflow> \
  --field dry_run=false \
  --field force_skip_tests=false

# Example using main branch (most common case)
gh workflow run release-patch-2-trigger.yml --ref main \
  --field ref="hotfix/v0.6.0-preview.2/preview/cherry-pick-abc1234" \
  --field workflow_ref=main \
  --field dry_run=false \
  --field force_skip_tests=true

```

**Note**: Replace `<branch-with-updated-workflow>` with the branch containing the latest workflow improvements (usually `main`, but could be a feature branch if testing updates).

**Option 2: Update the Hotfix Branch**
Merge the latest main branch into your hotfix branch to get the updated workflows:

```
git checkout hotfix/v0.6.0-preview.2/preview/cherry-pick-abc1234
git merge main
git push

```

Then close and reopen the PR to retrigger the workflow with the updated version.

**Option 3: Direct Release Trigger**
Skip the trigger workflow entirely and directly run the release workflow:

```
# Replace channel and release_ref with appropriate values
gh workflow run release-patch-3-release.yml --ref main \
  --field type="preview" \
  --field dry_run=false \
  --field force_skip_tests=true \
  --field release_ref="release/v0.6.0-preview.2"

```

### Docker [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#docker)

We also run a Google cloud build called [release-docker.yml](https://google-gemini.github.io/gemini-cli/.gcp/release-docker.yml). Which publishes the sandbox docker to match your release. This will also be moved to GH and combined with the main release file once service account permissions are sorted out.

## Release Validation [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#release-validation)

After pushing a new release smoke testing should be performed to ensure that the packages are working as expected. This can be done by installing the packages locally and running a set of tests to ensure that they are functioning correctly.

- `npx -y @google/gemini-cli@latest --version` to validate the push worked as expected if you were not doing a rc or dev tag
- `npx -y @google/gemini-cli@<release tag> --version` to validate the tag pushed appropriately
- _This is destructive locally_ `npm uninstall @google/gemini-cli && npm uninstall -g @google/gemini-cli && npm cache clean --force &&  npm install @google/gemini-cli@<version>`
- Smoke testing a basic run through of exercising a few llm commands and tools is recommended to ensure that the packages are working as expected. We’ll codify this more in the future.

## Local Testing and Validation: Changes to the Packaging and Publishing Process [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#local-testing-and-validation-changes-to-the-packaging-and-publishing-process)

If you need to test the release process without actually publishing to NPM or creating a public GitHub release, you can trigger the workflow manually from the GitHub UI.

1. Go to the [Actions tab](https://github.com/google-gemini/gemini-cli/actions/workflows/release-manual.yml) of the repository.
2. Click on the “Run workflow” dropdown.
3. Leave the `dry_run` option checked ( `true`).
4. Click the “Run workflow” button.

This will run the entire release process but will skip the `npm publish` and `gh release create` steps. You can inspect the workflow logs to ensure everything is working as expected.

It is crucial to test any changes to the packaging and publishing process locally before committing them. This ensures that the packages will be published correctly and that they will work as expected when installed by a user.

To validate your changes, you can perform a dry run of the publishing process. This will simulate the publishing process without actually publishing the packages to the npm registry.

```
npm_package_version=9.9.9 SANDBOX_IMAGE_REGISTRY="registry" SANDBOX_IMAGE_NAME="thename" npm run publish:npm --dry-run

```

This command will do the following:

1. Build all the packages.
2. Run all the prepublish scripts.
3. Create the package tarballs that would be published to npm.
4. Print a summary of the packages that would be published.

You can then inspect the generated tarballs to ensure that they contain the correct files and that the `package.json` files have been updated correctly. The tarballs will be created in the root of each package’s directory (e.g., `packages/cli/google-gemini-cli-0.1.6.tgz`).

By performing a dry run, you can be confident that your changes to the packaging process are correct and that the packages will be published successfully.

## Release Deep Dive [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#release-deep-dive)

The release process creates two distinct types of artifacts for different distribution channels: standard packages for the NPM registry and a single, self-contained executable for GitHub Releases.

Here are the key stages:

**Stage 1: Pre-Release Sanity Checks and Versioning**

- **What happens:** Before any files are moved, the process ensures the project is in a good state. This involves running tests, linting, and type-checking ( `npm run preflight`). The version number in the root `package.json` and `packages/cli/package.json` is updated to the new release version.

**Stage 2: Building the Source Code for NPM**

- **What happens:** The TypeScript source code in `packages/core/src` and `packages/cli/src` is compiled into standard JavaScript.
- **File movement:**
  - `packages/core/src/**/*.ts` -\> compiled to -> `packages/core/dist/`
  - `packages/cli/src/**/*.ts` -\> compiled to -> `packages/cli/dist/`
- **Why:** The TypeScript code written during development needs to be converted into plain JavaScript that can be run by Node.js. The `core` package is built first as the `cli` package depends on it.

**Stage 3: Publishing Standard Packages to NPM**

- **What happens:** The `npm publish` command is run for the `@google/gemini-cli-core` and `@google/gemini-cli` packages.
- **Why:** This publishes them as standard Node.js packages. Users installing via `npm install -g @google/gemini-cli` will download these packages, and `npm` will handle installing the `@google/gemini-cli-core` dependency automatically. The code in these packages is not bundled into a single file.

**Stage 4: Assembling and Creating the GitHub Release Asset**

This stage happens _after_ the NPM publish and creates the single-file executable that enables `npx` usage directly from the GitHub repository.

1. **The JavaScript Bundle is Created:**
   - **What happens:** The built JavaScript from both `packages/core/dist` and `packages/cli/dist`, along with all third-party JavaScript dependencies, are bundled by `esbuild` into a single, executable JavaScript file (e.g., `gemini.js`). The `node-pty` library is excluded from this bundle as it contains native binaries.
   - **Why:** This creates a single, optimized file that contains all the necessary application code. It simplifies execution for users who want to run the CLI without a full `npm install`, as all dependencies (including the `core` package) are included directly.
2. **The `bundle` Directory is Assembled:**
   - **What happens:** A temporary `bundle` folder is created at the project root. The single `gemini.js` executable is placed inside it, along with other essential files.
   - **File movement:**
     - `gemini.js` (from esbuild) -> `bundle/gemini.js`
     - `README.md` -\> `bundle/README.md`
     - `LICENSE` -\> `bundle/LICENSE`
     - `packages/cli/src/utils/*.sb` (sandbox profiles) -> `bundle/`
   - **Why:** This creates a clean, self-contained directory with everything needed to run the CLI and understand its license and usage.
3. **The GitHub Release is Created:**
   - **What happens:** The contents of the `bundle` directory, including the `gemini.js` executable, are attached as assets to a new GitHub Release.
   - **Why:** This makes the single-file version of the CLI available for direct download and enables the `npx https://github.com/google-gemini/gemini-cli` command, which downloads and runs this specific bundled asset.

**Summary of Artifacts**

- **NPM:** Publishes standard, un-bundled Node.js packages. The primary artifact is the code in `packages/cli/dist`, which depends on `@google/gemini-cli-core`.
- **GitHub Release:** Publishes a single, bundled `gemini.js` file that contains all dependencies, for easy execution via `npx`.

This dual-artifact process ensures that both traditional `npm` users and those who prefer the convenience of `npx` have an optimized experience.

## Notifications [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#notifications)

Failing release workflows will automatically create an issue with the label
`release-failure`.

A notification will be posted to the maintainer’s chat channel when issues with
this type are created.

### Modifying chat notifications [Anchor](https://google-gemini.github.io/gemini-cli/docs/releases.html\#modifying-chat-notifications)

Notifications use [GitHub for Google Chat](https://workspace.google.com/marketplace/app/github_for_google_chat/536184076190). To modify the notifications, use `/github-settings` within the chat space.

> \[!WARNING\]
> The following instructions describe a fragile workaround that depends on the internal structure of the chat application’s UI. It is likely to break with future updates.

The list of available labels is not currently populated correctly. If you want to add a label that does not appear alphabetically in the first 30 labels in the repo, you must use your browser’s developer tools to manually modify the UI:

1. Open your browser’s developer tools (e.g., Chrome DevTools).
2. In the `/github-settings` dialog, inspect the list of labels.
3. Locate one of the `<li>` elements representing a label.
4. In the HTML, modify the `data-option-value` attribute of that `<li>` element to the desired label name (e.g., `release-failure`).
5. Click on your modified label in the UI to select it, then save your settings.

## Gemini CLI Architecture Overview
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Gemini CLI Architecture Overview

This document provides a high-level overview of the Gemini CLI’s architecture.

## Core components [Anchor](https://google-gemini.github.io/gemini-cli/docs/architecture.html\#core-components)

The Gemini CLI is primarily composed of two main packages, along with a suite of tools that can be used by the system in the course of handling command-line input:

1. **CLI package ( `packages/cli`):**
   - **Purpose:** This contains the user-facing portion of the Gemini CLI, such as handling the initial user input, presenting the final output, and managing the overall user experience.
   - **Key functions contained in the package:**
     - [Input processing](https://google-gemini.github.io/gemini-cli/cli/commands.md)
     - History management
     - Display rendering
     - [Theme and UI customization](https://google-gemini.github.io/gemini-cli/cli/themes.md)
     - [CLI configuration settings](https://google-gemini.github.io/gemini-cli/get-started/configuration.md)
2. **Core package ( `packages/core`):**
   - **Purpose:** This acts as the backend for the Gemini CLI. It receives requests sent from `packages/cli`, orchestrates interactions with the Gemini API, and manages the execution of available tools.
   - **Key functions contained in the package:**
     - API client for communicating with the Google Gemini API
     - Prompt construction and management
     - Tool registration and execution logic
     - State management for conversations or sessions
     - Server-side configuration
3. **Tools ( `packages/core/src/tools/`):**
   - **Purpose:** These are individual modules that extend the capabilities of the Gemini model, allowing it to interact with the local environment (e.g., file system, shell commands, web fetching).
   - **Interaction:** `packages/core` invokes these tools based on requests from the Gemini model.

## Interaction Flow [Anchor](https://google-gemini.github.io/gemini-cli/docs/architecture.html\#interaction-flow)

A typical interaction with the Gemini CLI follows this flow:

1. **User input:** The user types a prompt or command into the terminal, which is managed by `packages/cli`.
2. **Request to core:** `packages/cli` sends the user’s input to `packages/core`.
3. **Request processed:** The core package:

   - Constructs an appropriate prompt for the Gemini API, possibly including conversation history and available tool definitions.
   - Sends the prompt to the Gemini API.
4. **Gemini API response:** The Gemini API processes the prompt and returns a response. This response might be a direct answer or a request to use one of the available tools.
5. **Tool execution (if applicable):**
   - When the Gemini API requests a tool, the core package prepares to execute it.
   - If the requested tool can modify the file system or execute shell commands, the user is first given details of the tool and its arguments, and the user must approve the execution.
   - Read-only operations, such as reading files, might not require explicit user confirmation to proceed.
   - Once confirmed, or if confirmation is not required, the core package executes the relevant action within the relevant tool, and the result is sent back to the Gemini API by the core package.
   - The Gemini API processes the tool result and generates a final response.
6. **Response to CLI:** The core package sends the final response back to the CLI package.
7. **Display to user:** The CLI package formats and displays the response to the user in the terminal.

## Key Design Principles [Anchor](https://google-gemini.github.io/gemini-cli/docs/architecture.html\#key-design-principles)

- **Modularity:** Separating the CLI (frontend) from the Core (backend) allows for independent development and potential future extensions (e.g., different frontends for the same backend).
- **Extensibility:** The tool system is designed to be extensible, allowing new capabilities to be added.
- **User experience:** The CLI focuses on providing a rich and interactive terminal experience.

## Gemini CLI Getting Started
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Get Started with Gemini CLI

Welcome to Gemini CLI! This guide will help you install, configure, and start using the Gemini CLI to enhance your workflow right from your terminal.

## Quickstart: Install, authenticate, configure, and use Gemini CLI [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/\#quickstart-install-authenticate-configure-and-use-gemini-cli)

Gemini CLI brings the power of advanced language models directly to your command line interface. As an AI-powered assistant, Gemini CLI can help you with a variety of tasks, from understanding and generating code to reviewing and editing documents.

## Install [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/\#install)

The standard method to install and run Gemini CLI uses `npm`:

```
npm install -g @google/gemini-cli

```

Once Gemini CLI is installed, run Gemini CLI from your command line:

```
gemini

```

For more deployment options, see [Gemini CLI Execution and Deployment](https://google-gemini.github.io/gemini-cli/docs/get-started/deployment.html).

## Authenticate [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/\#authenticate)

To begin using Gemini CLI, you must authenticate with a Google service. The most straightforward authentication method uses your existing Google account:

1. Run Gemini CLI after installation:





```
gemini

```

2. When asked “How would you like to authenticate for this project?” select **1\. Login with Google**.
3. Select your Google account.
4. Click on **Sign in**.

For other authentication options and information, see [GeminI CLI Authentication Setup](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html).

## Configure [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/\#configure)

Gemini CLI offers several ways to configure its behavior, including environment variables, command-line arguments, and settings files.

To explore your configuration options, see [Gemini CLI Configuration](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html).

## Use [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/\#use)

Once installed and authenticated, you can start using Gemini CLI by issuing commands and prompts in your terminal. Ask it to generate code, explain files, and more.

To explore the power of Gemini CLI, see [Gemini CLI examples](https://google-gemini.github.io/gemini-cli/docs/get-started/examples.html).

## What’s next? [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/\#whats-next)

- Find out more about [Gemini CLI’s tools](https://google-gemini.github.io/gemini-cli/docs/tools/).
- Review [Gemini CLI’s commands](https://google-gemini.github.io/gemini-cli/docs/cli/commands.html).

## Gemini CLI Shell Tool
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Shell Tool ( `run_shell_command`)

This document describes the `run_shell_command` tool for the Gemini CLI.

## Description [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#description)

Use `run_shell_command` to interact with the underlying system, run scripts, or perform command-line operations. `run_shell_command` executes a given shell command, including interactive commands that require user input (e.g., `vim`, `git rebase -i`) if the `tools.shell.enableInteractiveShell` setting is set to `true`.

On Windows, commands are executed with `cmd.exe /c`. On other platforms, they are executed with `bash -c`.

### Arguments [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#arguments)

`run_shell_command` takes the following arguments:

- `command` (string, required): The exact shell command to execute.
- `description` (string, optional): A brief description of the command’s purpose, which will be shown to the user.
- `directory` (string, optional): The directory (relative to the project root) in which to execute the command. If not provided, the command runs in the project root.

## How to use `run_shell_command` with the Gemini CLI [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#how-to-use-run_shell_command-with-the-gemini-cli)

When using `run_shell_command`, the command is executed as a subprocess. `run_shell_command` can start background processes using `&`. The tool returns detailed information about the execution, including:

- `Command`: The command that was executed.
- `Directory`: The directory where the command was run.
- `Stdout`: Output from the standard output stream.
- `Stderr`: Output from the standard error stream.
- `Error`: Any error message reported by the subprocess.
- `Exit Code`: The exit code of the command.
- `Signal`: The signal number if the command was terminated by a signal.
- `Background PIDs`: A list of PIDs for any background processes started.

Usage:

```
run_shell_command(command="Your commands.", description="Your description of the command.", directory="Your execution directory.")

```

## `run_shell_command` examples [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#run_shell_command-examples)

List files in the current directory:

```
run_shell_command(command="ls -la")

```

Run a script in a specific directory:

```
run_shell_command(command="./my_script.sh", directory="scripts", description="Run my custom script")

```

Start a background server:

```
run_shell_command(command="npm run dev &", description="Start development server in background")

```

## Configuration [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#configuration)

You can configure the behavior of the `run_shell_command` tool by modifying your `settings.json` file or by using the `/settings` command in the Gemini CLI.

### Enabling Interactive Commands [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#enabling-interactive-commands)

To enable interactive commands, you need to set the `tools.shell.enableInteractiveShell` setting to `true`. This will use `node-pty` for shell command execution, which allows for interactive sessions. If `node-pty` is not available, it will fall back to the `child_process` implementation, which does not support interactive commands.

**Example `settings.json`:**

```
{
  "tools": {
    "shell": {
      "enableInteractiveShell": true
    }
  }
}

```

### Showing Color in Output [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#showing-color-in-output)

To show color in the shell output, you need to set the `tools.shell.showColor` setting to `true`. **Note: This setting only applies when `tools.shell.enableInteractiveShell` is enabled.**

**Example `settings.json`:**

```
{
  "tools": {
    "shell": {
      "showColor": true
    }
  }
}

```

### Setting the Pager [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#setting-the-pager)

You can set a custom pager for the shell output by setting the `tools.shell.pager` setting. The default pager is `cat`. **Note: This setting only applies when `tools.shell.enableInteractiveShell` is enabled.**

**Example `settings.json`:**

```
{
  "tools": {
    "shell": {
      "pager": "less"
    }
  }
}

```

## Interactive Commands [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#interactive-commands)

The `run_shell_command` tool now supports interactive commands by integrating a pseudo-terminal (pty). This allows you to run commands that require real-time user input, such as text editors ( `vim`, `nano`), terminal-based UIs ( `htop`), and interactive version control operations ( `git rebase -i`).

When an interactive command is running, you can send input to it from the Gemini CLI. To focus on the interactive shell, press `ctrl+f`. The terminal output, including complex TUIs, will be rendered correctly.

## Important notes [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#important-notes)

- **Security:** Be cautious when executing commands, especially those constructed from user input, to prevent security vulnerabilities.
- **Error handling:** Check the `Stderr`, `Error`, and `Exit Code` fields to determine if a command executed successfully.
- **Background processes:** When a command is run in the background with `&`, the tool will return immediately and the process will continue to run in the background. The `Background PIDs` field will contain the process ID of the background process.

## Environment Variables [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#environment-variables)

When `run_shell_command` executes a command, it sets the `GEMINI_CLI=1` environment variable in the subprocess’s environment. This allows scripts or tools to detect if they are being run from within the Gemini CLI.

## Command Restrictions [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#command-restrictions)

You can restrict the commands that can be executed by the `run_shell_command` tool by using the `tools.core` and `tools.exclude` settings in your configuration file.

- `tools.core`: To restrict `run_shell_command` to a specific set of commands, add entries to the `core` list under the `tools` category in the format `run_shell_command(<command>)`. For example, `"tools": {"core": ["run_shell_command(git)"]}` will only allow `git` commands. Including the generic `run_shell_command` acts as a wildcard, allowing any command not explicitly blocked.
- `tools.exclude`: To block specific commands, add entries to the `exclude` list under the `tools` category in the format `run_shell_command(<command>)`. For example, `"tools": {"exclude": ["run_shell_command(rm)"]}` will block `rm` commands.

The validation logic is designed to be secure and flexible:

1. **Command Chaining Disabled**: The tool automatically splits commands chained with `&&`, `||`, or `;` and validates each part separately. If any part of the chain is disallowed, the entire command is blocked.
2. **Prefix Matching**: The tool uses prefix matching. For example, if you allow `git`, you can run `git status` or `git log`.
3. **Blocklist Precedence**: The `tools.exclude` list is always checked first. If a command matches a blocked prefix, it will be denied, even if it also matches an allowed prefix in `tools.core`.

### Command Restriction Examples [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#command-restriction-examples)

**Allow only specific command prefixes**

To allow only `git` and `npm` commands, and block all others:

```
{
  "tools": {
    "core": ["run_shell_command(git)", "run_shell_command(npm)"]
  }
}

```

- `git status`: Allowed
- `npm install`: Allowed
- `ls -l`: Blocked

**Block specific command prefixes**

To block `rm` and allow all other commands:

```
{
  "tools": {
    "core": ["run_shell_command"],
    "exclude": ["run_shell_command(rm)"]
  }
}

```

- `rm -rf /`: Blocked
- `git status`: Allowed
- `npm install`: Allowed

**Blocklist takes precedence**

If a command prefix is in both `tools.core` and `tools.exclude`, it will be blocked.

```
{
  "tools": {
    "core": ["run_shell_command(git)"],
    "exclude": ["run_shell_command(git push)"]
  }
}

```

- `git push origin main`: Blocked
- `git status`: Allowed

**Block all shell commands**

To block all shell commands, add the `run_shell_command` wildcard to `tools.exclude`:

```
{
  "tools": {
    "exclude": ["run_shell_command"]
  }
}

```

- `ls -l`: Blocked
- `any other command`: Blocked

## Security Note for `excludeTools` [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html\#security-note-for-excludetools)

Command-specific restrictions in `excludeTools` for `run_shell_command` are based on simple string matching and can be easily bypassed. This feature is **not a security mechanism** and should not be relied upon to safely execute untrusted code. It is recommended to use `coreTools` to explicitly select commands
that can be executed.

## Gemini CLI Headless Mode
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Headless Mode

Headless mode allows you to run Gemini CLI programmatically from command line
scripts and automation tools without any interactive UI. This is ideal for
scripting, automation, CI/CD pipelines, and building AI-powered tools.

- [Headless Mode](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#headless-mode)
  - [Overview](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#overview)
  - [Basic Usage](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#basic-usage)
    - [Direct Prompts](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#direct-prompts)
    - [Stdin Input](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#stdin-input)
    - [Combining with File Input](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#combining-with-file-input)
  - [Output Formats](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#output-formats)
    - [Text Output (Default)](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#text-output-default)
    - [JSON Output](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#json-output)
      - [Response Schema](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#response-schema)
      - [Example Usage](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#example-usage)
    - [File Redirection](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#file-redirection)
  - [Configuration Options](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#configuration-options)
  - [Examples](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#examples)
    - [Code review](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#code-review)
    - [Generate commit messages](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#generate-commit-messages)
    - [API documentation](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#api-documentation)
    - [Batch code analysis](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#batch-code-analysis)
    - [Code review](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#code-review-1)
    - [Log analysis](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#log-analysis)
    - [Release notes generation](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#release-notes-generation)
    - [Model and tool usage tracking](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#model-and-tool-usage-tracking)
  - [Resources](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html#resources)

## Overview [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#overview)

The headless mode provides a headless interface to Gemini CLI that:

- Accepts prompts via command line arguments or stdin
- Returns structured output (text or JSON)
- Supports file redirection and piping
- Enables automation and scripting workflows
- Provides consistent exit codes for error handling

## Basic Usage [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#basic-usage)

### Direct Prompts [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#direct-prompts)

Use the `--prompt` (or `-p`) flag to run in headless mode:

```
gemini --prompt "What is machine learning?"

```

### Stdin Input [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#stdin-input)

Pipe input to Gemini CLI from your terminal:

```
echo "Explain this code" | gemini

```

### Combining with File Input [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#combining-with-file-input)

Read from files and process with Gemini:

```
cat README.md | gemini --prompt "Summarize this documentation"

```

## Output Formats [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#output-formats)

### Text Output (Default) [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#text-output-default)

Standard human-readable output:

```
gemini -p "What is the capital of France?"

```

Response format:

```
The capital of France is Paris.

```

### JSON Output [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#json-output)

Returns structured data including response, statistics, and metadata. This
format is ideal for programmatic processing and automation scripts.

#### Response Schema [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#response-schema)

The JSON output follows this high-level structure:

```
{
  "response": "string", // The main AI-generated content answering your prompt
  "stats": {
    // Usage metrics and performance data
    "models": {
      // Per-model API and token usage statistics
      "[model-name]": {
        "api": {
          /* request counts, errors, latency */
        },
        "tokens": {
          /* prompt, response, cached, total counts */
        }
      }
    },
    "tools": {
      // Tool execution statistics
      "totalCalls": "number",
      "totalSuccess": "number",
      "totalFail": "number",
      "totalDurationMs": "number",
      "totalDecisions": {
        /* accept, reject, modify, auto_accept counts */
      },
      "byName": {
        /* per-tool detailed stats */
      }
    },
    "files": {
      // File modification statistics
      "totalLinesAdded": "number",
      "totalLinesRemoved": "number"
    }
  },
  "error": {
    // Present only when an error occurred
    "type": "string", // Error type (e.g., "ApiError", "AuthError")
    "message": "string", // Human-readable error description
    "code": "number" // Optional error code
  }
}

```

#### Example Usage [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#example-usage)

```
gemini -p "What is the capital of France?" --output-format json

```

Response:

```
{
  "response": "The capital of France is Paris.",
  "stats": {
    "models": {
      "gemini-2.5-pro": {
        "api": {
          "totalRequests": 2,
          "totalErrors": 0,
          "totalLatencyMs": 5053
        },
        "tokens": {
          "prompt": 24939,
          "candidates": 20,
          "total": 25113,
          "cached": 21263,
          "thoughts": 154,
          "tool": 0
        }
      },
      "gemini-2.5-flash": {
        "api": {
          "totalRequests": 1,
          "totalErrors": 0,
          "totalLatencyMs": 1879
        },
        "tokens": {
          "prompt": 8965,
          "candidates": 10,
          "total": 9033,
          "cached": 0,
          "thoughts": 30,
          "tool": 28
        }
      }
    },
    "tools": {
      "totalCalls": 1,
      "totalSuccess": 1,
      "totalFail": 0,
      "totalDurationMs": 1881,
      "totalDecisions": {
        "accept": 0,
        "reject": 0,
        "modify": 0,
        "auto_accept": 1
      },
      "byName": {
        "google_web_search": {
          "count": 1,
          "success": 1,
          "fail": 0,
          "durationMs": 1881,
          "decisions": {
            "accept": 0,
            "reject": 0,
            "modify": 0,
            "auto_accept": 1
          }
        }
      }
    },
    "files": {
      "totalLinesAdded": 0,
      "totalLinesRemoved": 0
    }
  }
}

```

### File Redirection [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#file-redirection)

Save output to files or pipe to other commands:

```
# Save to file
gemini -p "Explain Docker" > docker-explanation.txt
gemini -p "Explain Docker" --output-format json > docker-explanation.json

# Append to file
gemini -p "Add more details" >> docker-explanation.txt

# Pipe to other tools
gemini -p "What is Kubernetes?" --output-format json | jq '.response'
gemini -p "Explain microservices" | wc -w
gemini -p "List programming languages" | grep -i "python"

```

## Configuration Options [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#configuration-options)

Key command-line options for headless usage:

| Option | Description | Example |
| --- | --- | --- |
| `--prompt`, `-p` | Run in headless mode | `gemini -p "query"` |
| `--output-format` | Specify output format (text, json) | `gemini -p "query" --output-format json` |
| `--model`, `-m` | Specify the Gemini model | `gemini -p "query" -m gemini-2.5-flash` |
| `--debug`, `-d` | Enable debug mode | `gemini -p "query" --debug` |
| `--all-files`, `-a` | Include all files in context | `gemini -p "query" --all-files` |
| `--include-directories` | Include additional directories | `gemini -p "query" --include-directories src,docs` |
| `--yolo`, `-y` | Auto-approve all actions | `gemini -p "query" --yolo` |
| `--approval-mode` | Set approval mode | `gemini -p "query" --approval-mode auto_edit` |

For complete details on all available configuration options, settings files, and environment variables, see the [Configuration Guide](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html).

## Examples [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#examples)

#### Code review [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#code-review)

```
cat src/auth.py | gemini -p "Review this authentication code for security issues" > security-review.txt

```

#### Generate commit messages [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#generate-commit-messages)

```
result=$(git diff --cached | gemini -p "Write a concise commit message for these changes" --output-format json)
echo "$result" | jq -r '.response'

```

#### API documentation [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#api-documentation)

```
result=$(cat api/routes.js | gemini -p "Generate OpenAPI spec for these routes" --output-format json)
echo "$result" | jq -r '.response' > openapi.json

```

#### Batch code analysis [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#batch-code-analysis)

```
for file in src/*.py; do
    echo "Analyzing $file..."
    result=$(cat "$file" | gemini -p "Find potential bugs and suggest improvements" --output-format json)
    echo "$result" | jq -r '.response' > "reports/$(basename "$file").analysis"
    echo "Completed analysis for $(basename "$file")" >> reports/progress.log
done

```

#### Code review [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#code-review-1)

```
result=$(git diff origin/main...HEAD | gemini -p "Review these changes for bugs, security issues, and code quality" --output-format json)
echo "$result" | jq -r '.response' > pr-review.json

```

#### Log analysis [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#log-analysis)

```
grep "ERROR" /var/log/app.log | tail -20 | gemini -p "Analyze these errors and suggest root cause and fixes" > error-analysis.txt

```

#### Release notes generation [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#release-notes-generation)

```
result=$(git log --oneline v1.0.0..HEAD | gemini -p "Generate release notes from these commits" --output-format json)
response=$(echo "$result" | jq -r '.response')
echo "$response"
echo "$response" >> CHANGELOG.md

```

#### Model and tool usage tracking [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#model-and-tool-usage-tracking)

```
result=$(gemini -p "Explain this database schema" --include-directories db --output-format json)
total_tokens=$(echo "$result" | jq -r '.stats.models // {} | to_entries | map(.value.tokens.total) | add // 0')
models_used=$(echo "$result" | jq -r '.stats.models // {} | keys | join(", ") | if . == "" then "none" else . end')
tool_calls=$(echo "$result" | jq -r '.stats.tools.totalCalls // 0')
tools_used=$(echo "$result" | jq -r '.stats.tools.byName // {} | keys | join(", ") | if . == "" then "none" else . end')
echo "$(date): $total_tokens tokens, $tool_calls tool calls ($tools_used) used with models: $models_used" >> usage.log
echo "$result" | jq -r '.response' > schema-docs.md
echo "Recent usage trends:"
tail -5 usage.log

```

## Resources [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/headless.html\#resources)

- [CLI Configuration](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html) \- Complete configuration guide
- [Authentication](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html) \- Setup authentication
- [Commands](https://google-gemini.github.io/gemini-cli/docs/cli/commands.html) \- Interactive commands reference
- [Tutorials](https://google-gemini.github.io/gemini-cli/docs/cli/tutorials.html) \- Step-by-step automation guides

## Enterprise Gemini CLI Configuration
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Gemini CLI for the Enterprise

This document outlines configuration patterns and best practices for deploying and managing Gemini CLI in an enterprise environment. By leveraging system-level settings, administrators can enforce security policies, manage tool access, and ensure a consistent experience for all users.

> **A Note on Security:** The patterns described in this document are intended to help administrators create a more controlled and secure environment for using Gemini CLI. However, they should not be considered a foolproof security boundary. A determined user with sufficient privileges on their local machine may still be able to circumvent these configurations. These measures are designed to prevent accidental misuse and enforce corporate policy in a managed environment, not to defend against a malicious actor with local administrative rights.

## Centralized Configuration: The System Settings File [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#centralized-configuration-the-system-settings-file)

The most powerful tools for enterprise administration are the system-wide settings files. These files allow you to define a baseline configuration ( `system-defaults.json`) and a set of overrides ( `settings.json`) that apply to all users on a machine. For a complete overview of configuration options, see the [Configuration documentation](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html).

Settings are merged from four files. The precedence order for single-value settings (like `theme`) is:

1. System Defaults ( `system-defaults.json`)
2. User Settings ( `~/.gemini/settings.json`)
3. Workspace Settings ( `<project>/.gemini/settings.json`)
4. System Overrides ( `settings.json`)

This means the System Overrides file has the final say. For settings that are arrays ( `includeDirectories`) or objects ( `mcpServers`), the values are merged.

**Example of Merging and Precedence:**

Here is how settings from different levels are combined.

- **System Defaults `system-defaults.json`:**





```
{
    "ui": {
      "theme": "default-corporate-theme"
    },
    "context": {
      "includeDirectories": ["/etc/gemini-cli/common-context"]
    }
}

```

- **User `settings.json` ( `~/.gemini/settings.json`):**





```
{
    "ui": {
      "theme": "user-preferred-dark-theme"
    },
    "mcpServers": {
      "corp-server": {
        "command": "/usr/local/bin/corp-server-dev"
      },
      "user-tool": {
        "command": "npm start --prefix ~/tools/my-tool"
      }
    },
    "context": {
      "includeDirectories": ["~/gemini-context"]
    }
}

```

- **Workspace `settings.json` ( `<project>/.gemini/settings.json`):**





```
{
    "ui": {
      "theme": "project-specific-light-theme"
    },
    "mcpServers": {
      "project-tool": {
        "command": "npm start"
      }
    },
    "context": {
      "includeDirectories": ["./project-context"]
    }
}

```

- **System Overrides `settings.json`:**





```
{
    "ui": {
      "theme": "system-enforced-theme"
    },
    "mcpServers": {
      "corp-server": {
        "command": "/usr/local/bin/corp-server-prod"
      }
    },
    "context": {
      "includeDirectories": ["/etc/gemini-cli/global-context"]
    }
}

```


This results in the following merged configuration:

- **Final Merged Configuration:**




```
{
    "ui": {
      "theme": "system-enforced-theme"
    },
    "mcpServers": {
      "corp-server": {
        "command": "/usr/local/bin/corp-server-prod"
      },
      "user-tool": {
        "command": "npm start --prefix ~/tools/my-tool"
      },
      "project-tool": {
        "command": "npm start"
      }
    },
    "context": {
      "includeDirectories": [\
        "/etc/gemini-cli/common-context",\
        "~/gemini-context",\
        "./project-context",\
        "/etc/gemini-cli/global-context"\
      ]
    }
}

```


**Why:**

- **`theme`**: The value from the system overrides ( `system-enforced-theme`) is used, as it has the highest precedence.
- **`mcpServers`**: The objects are merged. The `corp-server` definition from the system overrides takes precedence over the user’s definition. The unique `user-tool` and `project-tool` are included.
- **`includeDirectories`**: The arrays are concatenated in the order of System Defaults, User, Workspace, and then System Overrides.

- **Location**:

  - **Linux**: `/etc/gemini-cli/settings.json`
  - **Windows**: `C:\ProgramData\gemini-cli\settings.json`
  - **macOS**: `/Library/Application Support/GeminiCli/settings.json`
  - The path can be overridden using the `GEMINI_CLI_SYSTEM_SETTINGS_PATH` environment variable.
- **Control**: This file should be managed by system administrators and protected with appropriate file permissions to prevent unauthorized modification by users.

By using the system settings file, you can enforce the security and configuration patterns described below.

## Restricting Tool Access [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#restricting-tool-access)

You can significantly enhance security by controlling which tools the Gemini model can use. This is achieved through the `tools.core` and `tools.exclude` settings. For a list of available tools, see the [Tools documentation](https://google-gemini.github.io/gemini-cli/docs/tools/).

### Allowlisting with `coreTools` [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#allowlisting-with-coretools)

The most secure approach is to explicitly add the tools and commands that users are permitted to execute to an allowlist. This prevents the use of any tool not on the approved list.

**Example:** Allow only safe, read-only file operations and listing files.

```
{
  "tools": {
    "core": ["ReadFileTool", "GlobTool", "ShellTool(ls)"]
  }
}

```

### Blocklisting with `excludeTools` [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#blocklisting-with-excludetools)

Alternatively, you can add specific tools that are considered dangerous in your environment to a blocklist.

**Example:** Prevent the use of the shell tool for removing files.

```
{
  "tools": {
    "exclude": ["ShellTool(rm -rf)"]
  }
}

```

**Security Note:** Blocklisting with `excludeTools` is less secure than allowlisting with `coreTools`, as it relies on blocking known-bad commands, and clever users may find ways to bypass simple string-based blocks. **Allowlisting is the recommended approach.**

## Managing Custom Tools (MCP Servers) [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#managing-custom-tools-mcp-servers)

If your organization uses custom tools via [Model-Context Protocol (MCP) servers](https://google-gemini.github.io/gemini-cli/docs/core/tools-api.html), it is crucial to understand how server configurations are managed to apply security policies effectively.

### How MCP Server Configurations are Merged [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#how-mcp-server-configurations-are-merged)

Gemini CLI loads `settings.json` files from three levels: System, Workspace, and User. When it comes to the `mcpServers` object, these configurations are **merged**:

1. **Merging:** The lists of servers from all three levels are combined into a single list.
2. **Precedence:** If a server with the **same name** is defined at multiple levels (e.g., a server named `corp-api` exists in both system and user settings), the definition from the highest-precedence level is used. The order of precedence is: **System > Workspace > User**.

This means a user **cannot** override the definition of a server that is already defined in the system-level settings. However, they **can** add new servers with unique names.

### Enforcing a Catalog of Tools [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#enforcing-a-catalog-of-tools)

The security of your MCP tool ecosystem depends on a combination of defining the canonical servers and adding their names to an allowlist.

### Restricting Tools Within an MCP Server [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#restricting-tools-within-an-mcp-server)

For even greater security, especially when dealing with third-party MCP servers, you can restrict which specific tools from a server are exposed to the model. This is done using the `includeTools` and `excludeTools` properties within a server’s definition. This allows you to use a subset of tools from a server without allowing potentially dangerous ones.

Following the principle of least privilege, it is highly recommended to use `includeTools` to create an allowlist of only the necessary tools.

**Example:** Only allow the `code-search` and `get-ticket-details` tools from a third-party MCP server, even if the server offers other tools like `delete-ticket`.

```
{
  "mcp": {
    "allowed": ["third-party-analyzer"]
  },
  "mcpServers": {
    "third-party-analyzer": {
      "command": "/usr/local/bin/start-3p-analyzer.sh",
      "includeTools": ["code-search", "get-ticket-details"]
    }
  }
}

```

#### More Secure Pattern: Define and Add to Allowlist in System Settings [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#more-secure-pattern-define-and-add-to-allowlist-in-system-settings)

To create a secure, centrally-managed catalog of tools, the system administrator **must** do both of the following in the system-level `settings.json` file:

1. **Define the full configuration** for every approved server in the `mcpServers` object. This ensures that even if a user defines a server with the same name, the secure system-level definition will take precedence.
2. **Add the names** of those servers to an allowlist using the `mcp.allowed` setting. This is a critical security step that prevents users from running any servers that are not on this list. If this setting is omitted, the CLI will merge and allow any server defined by the user.

**Example System `settings.json`:**

1. Add the _names_ of all approved servers to an allowlist.
This will prevent users from adding their own servers.

2. Provide the canonical _definition_ for each server on the allowlist.


```
{
  "mcp": {
    "allowed": ["corp-data-api", "source-code-analyzer"]
  },
  "mcpServers": {
    "corp-data-api": {
      "command": "/usr/local/bin/start-corp-api.sh",
      "timeout": 5000
    },
    "source-code-analyzer": {
      "command": "/usr/local/bin/start-analyzer.sh"
    }
  }
}

```

This pattern is more secure because it uses both definition and an allowlist. Any server a user defines will either be overridden by the system definition (if it has the same name) or blocked because its name is not in the `mcp.allowed` list.

### Less Secure Pattern: Omitting the Allowlist [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#less-secure-pattern-omitting-the-allowlist)

If the administrator defines the `mcpServers` object but fails to also specify the `mcp.allowed` allowlist, users may add their own servers.

**Example System `settings.json`:**

This configuration defines servers but does not enforce the allowlist.
The administrator has NOT included the “mcp.allowed” setting.

```
{
  "mcpServers": {
    "corp-data-api": {
      "command": "/usr/local/bin/start-corp-api.sh"
    }
  }
}

```

In this scenario, a user can add their own server in their local `settings.json`. Because there is no `mcp.allowed` list to filter the merged results, the user’s server will be added to the list of available tools and allowed to run.

## Enforcing Sandboxing for Security [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#enforcing-sandboxing-for-security)

To mitigate the risk of potentially harmful operations, you can enforce the use of sandboxing for all tool execution. The sandbox isolates tool execution in a containerized environment.

**Example:** Force all tool execution to happen within a Docker sandbox.

```
{
  "tools": {
    "sandbox": "docker"
  }
}

```

You can also specify a custom, hardened Docker image for the sandbox using the `--sandbox-image` command-line argument or by building a custom `sandbox.Dockerfile` as described in the [Sandboxing documentation](https://google-gemini.github.io/gemini-cli/docs/cli/sandbox.html).

## Controlling Network Access via Proxy [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#controlling-network-access-via-proxy)

In corporate environments with strict network policies, you can configure Gemini CLI to route all outbound traffic through a corporate proxy. This can be set via an environment variable, but it can also be enforced for custom tools via the `mcpServers` configuration.

**Example (for an MCP Server):**

```
{
  "mcpServers": {
    "proxied-server": {
      "command": "node",
      "args": ["mcp_server.js"],
      "env": {
        "HTTP_PROXY": "http://proxy.example.com:8080",
        "HTTPS_PROXY": "http://proxy.example.com:8080"
      }
    }
  }
}

```

## Telemetry and Auditing [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#telemetry-and-auditing)

For auditing and monitoring purposes, you can configure Gemini CLI to send telemetry data to a central location. This allows you to track tool usage and other events. For more information, see the [telemetry documentation](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html).

**Example:** Enable telemetry and send it to a local OTLP collector. If `otlpEndpoint` is not specified, it defaults to `http://localhost:4317`.

```
{
  "telemetry": {
    "enabled": true,
    "target": "gcp",
    "logPrompts": false
  }
}

```

**Note:** Ensure that `logPrompts` is set to `false` in an enterprise setting to avoid collecting potentially sensitive information from user prompts.

## Authentication [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#authentication)

You can enforce a specific authentication method for all users by setting the `enforcedAuthType` in the system-level `settings.json` file. This prevents users from choosing a different authentication method. See the [Authentication docs](https://google-gemini.github.io/gemini-cli/docs/cli/authentication.html) for more details.

**Example:** Enforce the use of Google login for all users.

```
{
  "enforcedAuthType": "oauth-personal"
}

```

If a user has a different authentication method configured, they will be prompted to switch to the enforced method. In non-interactive mode, the CLI will exit with an error if the configured authentication method does not match the enforced one.

## Putting It All Together: Example System `settings.json` [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html\#putting-it-all-together-example-system-settingsjson)

Here is an example of a system `settings.json` file that combines several of the patterns discussed above to create a secure, controlled environment for Gemini CLI.

```
{
  "tools": {
    "sandbox": "docker",
    "core": [\
      "ReadFileTool",\
      "GlobTool",\
      "ShellTool(ls)",\
      "ShellTool(cat)",\
      "ShellTool(grep)"\
    ]
  },
  "mcp": {
    "allowed": ["corp-tools"]
  },
  "mcpServers": {
    "corp-tools": {
      "command": "/opt/gemini-tools/start.sh",
      "timeout": 5000
    }
  },
  "telemetry": {
    "enabled": true,
    "target": "gcp",
    "otlpEndpoint": "https://telemetry-prod.example.com:4317",
    "logPrompts": false
  },
  "advanced": {
    "bugCommand": {
      "urlTemplate": "https://servicedesk.example.com/new-ticket?title={title}&details={info}"
    }
  },
  "privacy": {
    "usageStatisticsEnabled": false
  }
}

```

This configuration:

- Forces all tool execution into a Docker sandbox.
- Strictly uses an allowlist for a small set of safe shell commands and file tools.
- Defines and allows a single corporate MCP server for custom tools.
- Enables telemetry for auditing, without logging prompt content.
- Redirects the `/bug` command to an internal ticketing system.
- Disables general usage statistics collection.

## Gemini CLI OpenTelemetry Telemetry
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Observability with OpenTelemetry

Learn how to enable and setup OpenTelemetry for Gemini CLI.

- [Observability with OpenTelemetry](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#observability-with-opentelemetry)
  - [Key Benefits](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#key-benefits)
  - [OpenTelemetry Integration](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#opentelemetry-integration)
  - [Configuration](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#configuration)
  - [Google Cloud Telemetry](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#google-cloud-telemetry)
    - [Prerequisites](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#prerequisites)
    - [Direct Export (Recommended)](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#direct-export-recommended)
    - [Collector-Based Export (Advanced)](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#collector-based-export-advanced)
  - [Local Telemetry](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#local-telemetry)
    - [File-based Output (Recommended)](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#file-based-output-recommended)
    - [Collector-Based Export (Advanced)](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#collector-based-export-advanced-1)
  - [Logs and Metrics](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#logs-and-metrics)
    - [Logs](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#logs)
    - [Metrics](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#metrics)
      - [Custom](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#custom)
      - [GenAI Semantic Convention](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html#genai-semantic-convention)

## Key Benefits [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#key-benefits)

- **🔍 Usage Analytics**: Understand interaction patterns and feature adoption
across your team
- **⚡ Performance Monitoring**: Track response times, token consumption, and
resource utilization
- **🐛 Real-time Debugging**: Identify bottlenecks, failures, and error patterns
as they occur
- **📊 Workflow Optimization**: Make informed decisions to improve
configurations and processes
- **🏢 Enterprise Governance**: Monitor usage across teams, track costs, ensure
compliance, and integrate with existing monitoring infrastructure

## OpenTelemetry Integration [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#opentelemetry-integration)

Built on **[OpenTelemetry](https://opentelemetry.io/)** — the vendor-neutral, industry-standard
observability framework — Gemini CLI’s observability system provides:

- **Universal Compatibility**: Export to any OpenTelemetry backend (Google
Cloud, Jaeger, Prometheus, Datadog, etc.)
- **Standardized Data**: Use consistent formats and collection methods across
your toolchain
- **Future-Proof Integration**: Connect with existing and future observability
infrastructure
- **No Vendor Lock-in**: Switch between backends without changing your
instrumentation

## Configuration [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#configuration)

All telemetry behavior is controlled through your `.gemini/settings.json` file.
These settings can be overridden by environment variables or CLI flags.

| Setting | Environment Variable | CLI Flag | Description | Values | Default |
| --- | --- | --- | --- | --- | --- |
| `enabled` | `GEMINI_TELEMETRY_ENABLED` | `--telemetry` / `--no-telemetry` | Enable or disable telemetry | `true`/ `false` | `false` |
| `target` | `GEMINI_TELEMETRY_TARGET` | `--telemetry-target <local\|gcp>` | Where to send telemetry data | `"gcp"`/ `"local"` | `"local"` |
| `otlpEndpoint` | `GEMINI_TELEMETRY_OTLP_ENDPOINT` | `--telemetry-otlp-endpoint <URL>` | OTLP collector endpoint | URL string | `http://localhost:4317` |
| `otlpProtocol` | `GEMINI_TELEMETRY_OTLP_PROTOCOL` | `--telemetry-otlp-protocol <grpc\|http>` | OTLP transport protocol | `"grpc"`/ `"http"` | `"grpc"` |
| `outfile` | `GEMINI_TELEMETRY_OUTFILE` | `--telemetry-outfile <path>` | Save telemetry to file (overrides `otlpEndpoint`) | file path | - |
| `logPrompts` | `GEMINI_TELEMETRY_LOG_PROMPTS` | `--telemetry-log-prompts` / `--no-telemetry-log-prompts` | Include prompts in telemetry logs | `true`/ `false` | `true` |
| `useCollector` | `GEMINI_TELEMETRY_USE_COLLECTOR` | - | Use external OTLP collector (advanced) | `true`/ `false` | `false` |

**Note on boolean environment variables:** For the boolean settings ( `enabled`,
`logPrompts`, `useCollector`), setting the corresponding environment variable to
`true` or `1` will enable the feature. Any other value will disable it.

For detailed information about all configuration options, see the
[Configuration Guide](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html).

## Google Cloud Telemetry [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#google-cloud-telemetry)

### Prerequisites [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#prerequisites)

Before using either method below, complete these steps:

1. Set your Google Cloud project ID:
   - For telemetry in a separate project from inference:





     ```
     export OTLP_GOOGLE_CLOUD_PROJECT="your-telemetry-project-id"

     ```

   - For telemetry in the same project as inference:





     ```
     export GOOGLE_CLOUD_PROJECT="your-project-id"

     ```
2. Authenticate with Google Cloud:
   - If using a user account:





     ```
     gcloud auth application-default login

     ```

   - If using a service account:





     ```
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account.json"

     ```
3. Make sure your account or service account has these IAM roles:
   - Cloud Trace Agent
   - Monitoring Metric Writer
   - Logs Writer
4. Enable the required Google Cloud APIs (if not already enabled):





```
gcloud services enable \
     cloudtrace.googleapis.com \
     monitoring.googleapis.com \
     logging.googleapis.com \
     --project="$OTLP_GOOGLE_CLOUD_PROJECT"

```


### Direct Export (Recommended) [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#direct-export-recommended)

Sends telemetry directly to Google Cloud services. No collector needed.

1. Enable telemetry in your `.gemini/settings.json`:





```
{
     "telemetry": {
       "enabled": true,
       "target": "gcp"
     }
}

```

2. Run Gemini CLI and send prompts.
3. View logs and metrics:
   - Open the Google Cloud Console in your browser after sending prompts:
     - Logs: https://console.cloud.google.com/logs/
     - Metrics: https://console.cloud.google.com/monitoring/metrics-explorer
     - Traces: https://console.cloud.google.com/traces/list

### Collector-Based Export (Advanced) [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#collector-based-export-advanced)

For custom processing, filtering, or routing, use an OpenTelemetry collector to
forward data to Google Cloud.

1. Configure your `.gemini/settings.json`:





```
{
     "telemetry": {
       "enabled": true,
       "target": "gcp",
       "useCollector": true
     }
}

```

2. Run the automation script:





```
npm run telemetry -- --target=gcp

```





This will:
   - Start a local OTEL collector that forwards to Google Cloud
   - Configure your workspace
   - Provide links to view traces, metrics, and logs in Google Cloud Console
   - Save collector logs to `~/.gemini/tmp/<projectHash>/otel/collector-gcp.log`
   - Stop collector on exit (e.g. `Ctrl+C`)
3. Run Gemini CLI and send prompts.
4. View logs and metrics:
   - Open the Google Cloud Console in your browser after sending prompts:
     - Logs: https://console.cloud.google.com/logs/
     - Metrics: https://console.cloud.google.com/monitoring/metrics-explorer
     - Traces: https://console.cloud.google.com/traces/list
   - Open `~/.gemini/tmp/<projectHash>/otel/collector-gcp.log` to view local
     collector logs.

## Local Telemetry [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#local-telemetry)

For local development and debugging, you can capture telemetry data locally:

### File-based Output (Recommended) [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#file-based-output-recommended)

1. Enable telemetry in your `.gemini/settings.json`:





```
{
     "telemetry": {
       "enabled": true,
       "target": "local",
       "otlpEndpoint": "",
       "outfile": ".gemini/telemetry.log"
     }
}

```

2. Run Gemini CLI and send prompts.
3. View logs and metrics in the specified file (e.g., `.gemini/telemetry.log`).

### Collector-Based Export (Advanced) [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#collector-based-export-advanced-1)

1. Run the automation script:





```
npm run telemetry -- --target=local

```





This will:
   - Download and start Jaeger and OTEL collector
   - Configure your workspace for local telemetry
   - Provide a Jaeger UI at http://localhost:16686
   - Save logs/metrics to `~/.gemini/tmp/<projectHash>/otel/collector.log`
   - Stop collector on exit (e.g. `Ctrl+C`)
2. Run Gemini CLI and send prompts.
3. View traces at http://localhost:16686 and logs/metrics in the collector log
file.

## Logs and Metrics [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#logs-and-metrics)

The following section describes the structure of logs and metrics generated for
Gemini CLI.

- A `sessionId` is included as a common attribute on all logs and metrics.

### Logs [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#logs)

Logs are timestamped records of specific events. The following events are logged
for Gemini CLI:

- `gemini_cli.config`: This event occurs once at startup with the CLI’s
configuration.

  - **Attributes**:

    - `model` (string)
    - `embedding_model` (string)
    - `sandbox_enabled` (boolean)
    - `core_tools_enabled` (string)
    - `approval_mode` (string)
    - `api_key_enabled` (boolean)
    - `vertex_ai_enabled` (boolean)
    - `code_assist_enabled` (boolean)
    - `log_prompts_enabled` (boolean)
    - `file_filtering_respect_git_ignore` (boolean)
    - `debug_mode` (boolean)
    - `mcp_servers` (string)
    - `output_format` (string: “text” or “json”)
- `gemini_cli.user_prompt`: This event occurs when a user submits a prompt.

  - **Attributes**:

    - `prompt_length` (int)
    - `prompt_id` (string)
    - `prompt` (string, this attribute is excluded if `log_prompts_enabled` is
      configured to be `false`)
    - `auth_type` (string)
- `gemini_cli.tool_call`: This event occurs for each function call.

  - **Attributes**:

    - `function_name`
    - `function_args`
    - `duration_ms`
    - `success` (boolean)
    - `decision` (string: “accept”, “reject”, “auto\_accept”, or “modify”, if
      applicable)
    - `error` (if applicable)
    - `error_type` (if applicable)
    - `content_length` (int, if applicable)
    - `metadata` (if applicable, dictionary of string -> any)
- `gemini_cli.file_operation`: This event occurs for each file operation.

  - **Attributes**:

    - `tool_name` (string)
    - `operation` (string: “create”, “read”, “update”)
    - `lines` (int, if applicable)
    - `mimetype` (string, if applicable)
    - `extension` (string, if applicable)
    - `programming_language` (string, if applicable)
    - `diff_stat` (json string, if applicable): A JSON string with the following members:

      - `ai_added_lines` (int)
      - `ai_removed_lines` (int)
      - `user_added_lines` (int)
      - `user_removed_lines` (int)
- `gemini_cli.api_request`: This event occurs when making a request to Gemini API.

  - **Attributes**:

    - `model`
    - `request_text` (if applicable)
- `gemini_cli.api_error`: This event occurs if the API request fails.

  - **Attributes**:

    - `model`
    - `error`
    - `error_type`
    - `status_code`
    - `duration_ms`
    - `auth_type`
- `gemini_cli.api_response`: This event occurs upon receiving a response from Gemini API.

  - **Attributes**:

    - `model`
    - `status_code`
    - `duration_ms`
    - `error` (optional)
    - `input_token_count`
    - `output_token_count`
    - `cached_content_token_count`
    - `thoughts_token_count`
    - `tool_token_count`
    - `response_text` (if applicable)
    - `auth_type`
- `gemini_cli.tool_output_truncated`: This event occurs when the output of a tool call is too large and gets truncated.

  - **Attributes**:

    - `tool_name` (string)
    - `original_content_length` (int)
    - `truncated_content_length` (int)
    - `threshold` (int)
    - `lines` (int)
    - `prompt_id` (string)
- `gemini_cli.malformed_json_response`: This event occurs when a `generateJson` response from Gemini API cannot be parsed as a json.

  - **Attributes**:

    - `model`
- `gemini_cli.flash_fallback`: This event occurs when Gemini CLI switches to flash as fallback.

  - **Attributes**:

    - `auth_type`
- `gemini_cli.slash_command`: This event occurs when a user executes a slash command.

  - **Attributes**:

    - `command` (string)
    - `subcommand` (string, if applicable)
- `gemini_cli.extension_enable`: This event occurs when an extension is enabled
- `gemini_cli.extension_install`: This event occurs when an extension is installed

  - **Attributes**:

    - `extension_name` (string)
    - `extension_version` (string)
    - `extension_source` (string)
    - `status` (string)
- `gemini_cli.extension_uninstall`: This event occurs when an extension is uninstalled

### Metrics [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#metrics)

Metrics are numerical measurements of behavior over time.

#### Custom [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#custom)

- `gemini_cli.session.count` (Counter, Int): Incremented once per CLI startup.

- `gemini_cli.tool.call.count` (Counter, Int): Counts tool calls.

  - **Attributes**:

    - `function_name`
    - `success` (boolean)
    - `decision` (string: “accept”, “reject”, or “modify”, if applicable)
    - `tool_type` (string: “mcp”, or “native”, if applicable)
- `gemini_cli.tool.call.latency` (Histogram, ms): Measures tool call latency.

  - **Attributes**:

    - `function_name`
    - `decision` (string: “accept”, “reject”, or “modify”, if applicable)
- `gemini_cli.api.request.count` (Counter, Int): Counts all API requests.

  - **Attributes**:

    - `model`
    - `status_code`
    - `error_type` (if applicable)
- `gemini_cli.api.request.latency` (Histogram, ms): Measures API request latency.

  - **Attributes**:

    - `model`
  - **Note**: This metric overlaps with `gen_ai.client.operation.duration` below
    that’s compliant with GenAI Semantic Conventions.
- `gemini_cli.token.usage` (Counter, Int): Counts the number of tokens used.

  - **Attributes**:

    - `model`
    - `type` (string: “input”, “output”, “thought”, “cache”, or “tool”)
  - **Note**: This metric overlaps with `gen_ai.client.token.usage` below for
    `input`/ `output` token types that’s compliant with GenAI Semantic
    Conventions.
- `gemini_cli.file.operation.count` (Counter, Int): Counts file operations.

  - **Attributes**:

    - `operation` (string: “create”, “read”, “update”): The type of file operation.
    - `lines` (Int, if applicable): Number of lines in the file.
    - `mimetype` (string, if applicable): Mimetype of the file.
    - `extension` (string, if applicable): File extension of the file.
    - `model_added_lines` (Int, if applicable): Number of lines added/changed by the model.
    - `model_removed_lines` (Int, if applicable): Number of lines removed/changed by the model.
    - `user_added_lines` (Int, if applicable): Number of lines added/changed by user in AI proposed changes.
    - `user_removed_lines` (Int, if applicable): Number of lines removed/changed by user in AI proposed changes.
    - `programming_language` (string, if applicable): The programming language of the file.
- `gemini_cli.chat_compression` (Counter, Int): Counts chat compression operations

  - **Attributes**:

    - `tokens_before`: (Int): Number of tokens in context prior to compression
    - `tokens_after`: (Int): Number of tokens in context after compression

#### GenAI Semantic Convention [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html\#genai-semantic-convention)

The following metrics comply with [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-metrics.md)
for standardized observability across GenAI applications:

- `gen_ai.client.token.usage` (Histogram, token): Number of input and output tokens used per operation.

  - **Attributes**:

    - `gen_ai.operation.name` (string): The operation type (e.g., “generate\_content”, “chat”)
    - `gen_ai.provider.name` (string): The GenAI provider (“gcp.gen\_ai” or “gcp.vertex\_ai”)
    - `gen_ai.token.type` (string): The token type (“input” or “output”)
    - `gen_ai.request.model` (string, optional): The model name used for the request
    - `gen_ai.response.model` (string, optional): The model name that generated the response
    - `server.address` (string, optional): GenAI server address
    - `server.port` (int, optional): GenAI server port
- `gen_ai.client.operation.duration` (Histogram, s): GenAI operation duration in seconds.

  - **Attributes**:

    - `gen_ai.operation.name` (string): The operation type (e.g., “generate\_content”, “chat”)
    - `gen_ai.provider.name` (string): The GenAI provider (“gcp.gen\_ai” or “gcp.vertex\_ai”)
    - `gen_ai.request.model` (string, optional): The model name used for the request
    - `gen_ai.response.model` (string, optional): The model name that generated the response
    - `server.address` (string, optional): GenAI server address
    - `server.port` (int, optional): GenAI server port
    - `error.type` (string, optional): Error type if the operation failed

## Gemini CLI Themes Guide
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Themes

Gemini CLI supports a variety of themes to customize its color scheme and appearance. You can change the theme to suit your preferences via the `/theme` command or `"theme":` configuration setting.

## Available Themes [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#available-themes)

Gemini CLI comes with a selection of pre-defined themes, which you can list using the `/theme` command within Gemini CLI:

- **Dark Themes:**
  - `ANSI`
  - `Atom One`
  - `Ayu`
  - `Default`
  - `Dracula`
  - `GitHub`
- **Light Themes:**
  - `ANSI Light`
  - `Ayu Light`
  - `Default Light`
  - `GitHub Light`
  - `Google Code`
  - `Xcode`

### Changing Themes [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#changing-themes)

1. Enter `/theme` into Gemini CLI.
2. A dialog or selection prompt appears, listing the available themes.
3. Using the arrow keys, select a theme. Some interfaces might offer a live preview or highlight as you select.
4. Confirm your selection to apply the theme.

**Note:** If a theme is defined in your `settings.json` file (either by name or by a file path), you must remove the `"theme"` setting from the file before you can change the theme using the `/theme` command.

### Theme Persistence [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#theme-persistence)

Selected themes are saved in Gemini CLI’s [configuration](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html) so your preference is remembered across sessions.

* * *

## Custom Color Themes [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#custom-color-themes)

Gemini CLI allows you to create your own custom color themes by specifying them in your `settings.json` file. This gives you full control over the color palette used in the CLI.

### How to Define a Custom Theme [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#how-to-define-a-custom-theme)

Add a `customThemes` block to your user, project, or system `settings.json` file. Each custom theme is defined as an object with a unique name and a set of color keys. For example:

```
{
  "ui": {
    "customThemes": {
      "MyCustomTheme": {
        "name": "MyCustomTheme",
        "type": "custom",
        "Background": "#181818",
        ...
      }
    }
  }
}

```

**Color keys:**

- `Background`
- `Foreground`
- `LightBlue`
- `AccentBlue`
- `AccentPurple`
- `AccentCyan`
- `AccentGreen`
- `AccentYellow`
- `AccentRed`
- `Comment`
- `Gray`
- `DiffAdded` (optional, for added lines in diffs)
- `DiffRemoved` (optional, for removed lines in diffs)
- `DiffModified` (optional, for modified lines in diffs)

**Required Properties:**

- `name` (must match the key in the `customThemes` object and be a string)
- `type` (must be the string `"custom"`)
- `Background`
- `Foreground`
- `LightBlue`
- `AccentBlue`
- `AccentPurple`
- `AccentCyan`
- `AccentGreen`
- `AccentYellow`
- `AccentRed`
- `Comment`
- `Gray`

You can use either hex codes (e.g., `#FF0000`) **or** standard CSS color names (e.g., `coral`, `teal`, `blue`) for any color value. See [CSS color names](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value#color_keywords) for a full list of supported names.

You can define multiple custom themes by adding more entries to the `customThemes` object.

### Loading Themes from a File [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#loading-themes-from-a-file)

In addition to defining custom themes in `settings.json`, you can also load a theme directly from a JSON file by specifying the file path in your `settings.json`. This is useful for sharing themes or keeping them separate from your main configuration.

To load a theme from a file, set the `theme` property in your `settings.json` to the path of your theme file:

```
{
  "ui": {
    "theme": "/path/to/your/theme.json"
  }
}

```

The theme file must be a valid JSON file that follows the same structure as a custom theme defined in `settings.json`.

**Example `my-theme.json`:**

```
{
  "name": "My File Theme",
  "type": "custom",
  "Background": "#282A36",
  "Foreground": "#F8F8F2",
  "LightBlue": "#82AAFF",
  "AccentBlue": "#61AFEF",
  "AccentPurple": "#BD93F9",
  "AccentCyan": "#8BE9FD",
  "AccentGreen": "#50FA7B",
  "AccentYellow": "#F1FA8C",
  "AccentRed": "#FF5555",
  "Comment": "#6272A4",
  "Gray": "#ABB2BF",
  "DiffAdded": "#A6E3A1",
  "DiffRemoved": "#F38BA8",
  "DiffModified": "#89B4FA",
  "GradientColors": ["#4796E4", "#847ACE", "#C3677F"]
}

```

**Security Note:** For your safety, Gemini CLI will only load theme files that are located within your home directory. If you attempt to load a theme from outside your home directory, a warning will be displayed and the theme will not be loaded. This is to prevent loading potentially malicious theme files from untrusted sources.

### Example Custom Theme [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#example-custom-theme)

![Custom theme example](https://google-gemini.github.io/gemini-cli/docs/assets/theme-custom.png)

### Using Your Custom Theme [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#using-your-custom-theme)

- Select your custom theme using the `/theme` command in Gemini CLI. Your custom theme will appear in the theme selection dialog.
- Or, set it as the default by adding `"theme": "MyCustomTheme"` to the `ui` object in your `settings.json`.
- Custom themes can be set at the user, project, or system level, and follow the same [configuration precedence](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html) as other settings.

* * *

## Dark Themes [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#dark-themes)

### ANSI [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#ansi)

![ANSI theme](https://google-gemini.github.io/gemini-cli/docs/assets/theme-ansi.png)

### Atom OneDark [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#atom-onedark)

![Atom One theme](https://google-gemini.github.io/gemini-cli/docs/assets/theme-atom-one.png)

### Ayu [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#ayu)

![Ayu theme](https://google-gemini.github.io/gemini-cli/docs/assets/theme-ayu.png)

### Default [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#default)

![Default theme](https://google-gemini.github.io/gemini-cli/docs/assets/theme-default.png)

### Dracula [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#dracula)

![Dracula theme](https://google-gemini.github.io/gemini-cli/docs/assets/theme-dracula.png)

### GitHub [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#github)

![GitHub theme](https://google-gemini.github.io/gemini-cli/docs/assets/theme-github.png)

## Light Themes [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#light-themes)

### ANSI Light [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#ansi-light)

![ANSI Light theme](https://google-gemini.github.io/gemini-cli/docs/assets/theme-ansi-light.png)

### Ayu Light [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#ayu-light)

![Ayu Light theme](https://google-gemini.github.io/gemini-cli/docs/assets/theme-ayu-light.png)

### Default Light [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#default-light)

![Default Light theme](https://google-gemini.github.io/gemini-cli/docs/assets/theme-default-light.png)

### GitHub Light [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#github-light)

![GitHub Light theme](https://google-gemini.github.io/gemini-cli/docs/assets/theme-github-light.png)

### Google Code [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#google-code)

![Google Code theme](https://google-gemini.github.io/gemini-cli/docs/assets/theme-google-light.png)

### Xcode [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html\#xcode)

![Xcode Light theme](https://google-gemini.github.io/gemini-cli/docs/assets/theme-xcode-light.png)

## Gemini CLI Terms Privacy
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Gemini CLI: Terms of Service and Privacy Notice

Gemini CLI is an open-source tool that lets you interact with Google’s powerful language models directly from your command-line interface. The Terms of Service and Privacy Notices that apply to your usage of the Gemini CLI depend on the type of account you use to authenticate with Google.

This article outlines the specific terms and privacy policies applicable for different account types and authentication methods. Note: See [quotas and pricing](https://google-gemini.github.io/gemini-cli/docs/quota-and-pricing.html) for the quota and pricing details that apply to your usage of the Gemini CLI.

## How to determine your authentication method [Anchor](https://google-gemini.github.io/gemini-cli/docs/tos-privacy.html\#how-to-determine-your-authentication-method)

Your authentication method refers to the method you use to log into and access the Gemini CLI. There are four ways to authenticate:

- Logging in with your Google account to Gemini Code Assist for individuals
- Logging in with your Google account to Gemini Code Assist for Standard, or Enterprise Users
- Using an API key with Gemini Developer
- Using an API key with Vertex AI GenAI API

For each of these four methods of authentication, different Terms of Service and Privacy Notices may apply.

| Authentication | Account | Terms of Service | Privacy Notice |
| --- | --- | --- | --- |
| Gemini Code Assist via Google | Individual | [Google Terms of Service](https://policies.google.com/terms?hl=en-US) | [Gemini Code Assist Privacy Notice for individuals](https://developers.google.com/gemini-code-assist/resources/privacy-notice-gemini-code-assist-individuals) |
| Gemini Code Assist via Google | Standard/Enterprise | [Google Cloud Platform Terms of Service](https://cloud.google.com/terms) | [Gemini Code Assist Privacy Notice for Standard and Enterprise](https://cloud.google.com/gemini/docs/codeassist/security-privacy-compliance#standard_and_enterprise_data_protection_and_privacy) |
| Gemini Developer API | Unpaid | [Gemini API Terms of Service - Unpaid Services](https://ai.google.dev/gemini-api/terms#unpaid-services) | [Google Privacy Policy](https://policies.google.com/privacy) |
| Gemini Developer API | Paid | [Gemini API Terms of Service - Paid Services](https://ai.google.dev/gemini-api/terms#paid-services) | [Google Privacy Policy](https://policies.google.com/privacy) |
| Vertex AI Gen API |  | [Google Cloud Platform Service Terms](https://cloud.google.com/terms/service-terms/) | [Google Cloud Privacy Notice](https://cloud.google.com/terms/cloud-privacy-notice) |

## 1\. If you have logged in with your Google account to Gemini Code Assist for individuals [Anchor](https://google-gemini.github.io/gemini-cli/docs/tos-privacy.html\#1-if-you-have-logged-in-with-your-google-account-to-gemini-code-assist-for-individuals)

For users who use their Google account to access [Gemini Code Assist for individuals](https://developers.google.com/gemini-code-assist/docs/overview#supported-features-gca), these Terms of Service and Privacy Notice documents apply:

- **Terms of Service:** Your use of the Gemini CLI is governed by the [Google Terms of Service](https://policies.google.com/terms?hl=en-US).
- **Privacy Notice:** The collection and use of your data is described in the [Gemini Code Assist Privacy Notice for individuals](https://developers.google.com/gemini-code-assist/resources/privacy-notice-gemini-code-assist-individuals).

## 2\. If you have logged in with your Google account to Gemini Code Assist for Standard, or Enterprise Users [Anchor](https://google-gemini.github.io/gemini-cli/docs/tos-privacy.html\#2-if-you-have-logged-in-with-your-google-account-to-gemini-code-assist-for-standard-or-enterprise-users)

For users who use their Google account to access the [Standard or Enterprise edition](https://cloud.google.com/gemini/docs/codeassist/overview#editions-overview) of Gemini Code Assist, these Terms of Service and Privacy Notice documents apply:

- **Terms of Service:** Your use of the Gemini CLI is governed by the [Google Cloud Platform Terms of Service](https://cloud.google.com/terms).
- **Privacy Notice:** The collection and use of your data is described in the [Gemini Code Assist Privacy Notices for Standard and Enterprise Users](https://cloud.google.com/gemini/docs/codeassist/security-privacy-compliance#standard_and_enterprise_data_protection_and_privacy).

## 3\. If you have logged in with a Gemini API key to the Gemini Developer API [Anchor](https://google-gemini.github.io/gemini-cli/docs/tos-privacy.html\#3-if-you-have-logged-in-with-a-gemini-api-key-to-the-gemini-developer-api)

If you are using a Gemini API key for authentication with the [Gemini Developer API](https://ai.google.dev/gemini-api/docs), these Terms of Service and Privacy Notice documents apply:

- **Terms of Service:** Your use of the Gemini CLI is governed by the [Gemini API Terms of Service](https://ai.google.dev/gemini-api/terms). These terms may differ depending on whether you are using an unpaid or paid service:

  - For unpaid services, refer to the [Gemini API Terms of Service - Unpaid Services](https://ai.google.dev/gemini-api/terms#unpaid-services).
  - For paid services, refer to the [Gemini API Terms of Service - Paid Services](https://ai.google.dev/gemini-api/terms#paid-services).
- **Privacy Notice:** The collection and use of your data is described in the [Google Privacy Policy](https://policies.google.com/privacy).

## 4\. If you have logged in with a Gemini API key to the Vertex AI GenAI API [Anchor](https://google-gemini.github.io/gemini-cli/docs/tos-privacy.html\#4-if-you-have-logged-in-with-a-gemini-api-key-to-the-vertex-ai-genai-api)

If you are using a Gemini API key for authentication with a [Vertex AI GenAI API](https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest) backend, these Terms of Service and Privacy Notice documents apply:

- **Terms of Service:** Your use of the Gemini CLI is governed by the [Google Cloud Platform Service Terms](https://cloud.google.com/terms/service-terms/).
- **Privacy Notice:** The collection and use of your data is described in the [Google Cloud Privacy Notice](https://cloud.google.com/terms/cloud-privacy-notice).

### Usage Statistics Opt-Out [Anchor](https://google-gemini.github.io/gemini-cli/docs/tos-privacy.html\#usage-statistics-opt-out)

You may opt-out from sending Usage Statistics to Google by following the instructions available here: [Usage Statistics Configuration](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html#usage-statistics).

## Frequently Asked Questions (FAQ) for the Gemini CLI [Anchor](https://google-gemini.github.io/gemini-cli/docs/tos-privacy.html\#frequently-asked-questions-faq-for-the-gemini-cli)

### 1\. Is my code, including prompts and answers, used to train Google’s models? [Anchor](https://google-gemini.github.io/gemini-cli/docs/tos-privacy.html\#1-is-my-code-including-prompts-and-answers-used-to-train-googles-models)

Whether your code, including prompts and answers, is used to train Google’s models depends on the type of authentication method you use and your account type.

By default (if you have not opted out):

- **Google account with Gemini Code Assist for individuals**: Yes. When you use your personal Google account, the [Gemini Code Assist Privacy Notice for individuals](https://developers.google.com/gemini-code-assist/resources/privacy-notice-gemini-code-assist-individuals) applies. Under this notice,
your **prompts, answers, and related code are collected** and may be used to improve Google’s products, including for model training.
- **Google account with Gemini Code Assist for Standard, or Enterprise**: No. For these accounts, your data is governed by the [Gemini Code Assist Privacy Notices](https://cloud.google.com/gemini/docs/codeassist/security-privacy-compliance#standard_and_enterprise_data_protection_and_privacy) terms, which treat your inputs as confidential. Your **prompts, answers, and related code are not collected** and are not used to train models.
- **Gemini API key via the Gemini Developer API**: Whether your code is collected or used depends on whether you are using an unpaid or paid service.

  - **Unpaid services**: Yes. When you use the Gemini API key via the Gemini Developer API with an unpaid service, the [Gemini API Terms of Service - Unpaid Services](https://ai.google.dev/gemini-api/terms#unpaid-services) terms apply. Under this notice, your **prompts, answers, and related code are collected** and may be used to improve Google’s products, including for model training.
  - **Paid services**: No. When you use the Gemini API key via the Gemini Developer API with a paid service, the [Gemini API Terms of Service - Paid Services](https://ai.google.dev/gemini-api/terms#paid-services) terms apply, which treats your inputs as confidential. Your **prompts, answers, and related code are not collected** and are not used to train models.
- **Gemini API key via the Vertex AI GenAI API**: No. For these accounts, your data is governed by the [Google Cloud Privacy Notice](https://cloud.google.com/terms/cloud-privacy-notice) terms, which treat your inputs as confidential. Your **prompts, answers, and related code are not collected** and are not used to train models.

For more information about opting out, refer to the next question.

### 2\. What are Usage Statistics and what does the opt-out control? [Anchor](https://google-gemini.github.io/gemini-cli/docs/tos-privacy.html\#2-what-are-usage-statistics-and-what-does-the-opt-out-control)

The **Usage Statistics** setting is the single control for all optional data collection in the Gemini CLI.

The data it collects depends on your account and authentication type:

- **Google account with Gemini Code Assist for individuals**: When enabled, this setting allows Google to collect both anonymous telemetry (for example, commands run and performance metrics) and **your prompts and answers, including code,** for model improvement.
- **Google account with Gemini Code Assist for Standard, or Enterprise**: This setting only controls the collection of anonymous telemetry. Your prompts and answers, including code, are never collected, regardless of this setting.
- **Gemini API key via the Gemini Developer API**:
**Unpaid services**: When enabled, this setting allows Google to collect both anonymous telemetry (like commands run and performance metrics) and **your prompts and answers, including code,** for model improvement. When disabled we will use your data as described in [How Google Uses Your Data](https://ai.google.dev/gemini-api/terms#data-use-unpaid).
**Paid services**: This setting only controls the collection of anonymous telemetry. Google logs prompts and responses for a limited period of time, solely for the purpose of detecting violations of the Prohibited Use Policy and any required legal or regulatory disclosures.
- **Gemini API key via the Vertex AI GenAI API:** This setting only controls the collection of anonymous telemetry. Your prompts and answers, including code, are never collected, regardless of this setting.

Please refer to the Privacy Notice that applies to your authentication method for more information about what data is collected and how this data is used.

You can disable Usage Statistics for any account type by following the instructions in the [Usage Statistics Configuration](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration-v1.html#usage-statistics) documentation.

## Gemini CLI Tools API
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Gemini CLI Core: Tools API

The Gemini CLI core ( `packages/core`) features a robust system for defining, registering, and executing tools. These tools extend the capabilities of the Gemini model, allowing it to interact with the local environment, fetch web content, and perform various actions beyond simple text generation.

## Core Concepts [Anchor](https://google-gemini.github.io/gemini-cli/docs/core/tools-api.html\#core-concepts)

- **Tool ( `tools.ts`):** An interface and base class ( `BaseTool`) that defines the contract for all tools. Each tool must have:

  - `name`: A unique internal name (used in API calls to Gemini).
  - `displayName`: A user-friendly name.
  - `description`: A clear explanation of what the tool does, which is provided to the Gemini model.
  - `parameterSchema`: A JSON schema defining the parameters that the tool accepts. This is crucial for the Gemini model to understand how to call the tool correctly.
  - `validateToolParams()`: A method to validate incoming parameters.
  - `getDescription()`: A method to provide a human-readable description of what the tool will do with specific parameters before execution.
  - `shouldConfirmExecute()`: A method to determine if user confirmation is required before execution (e.g., for potentially destructive operations).
  - `execute()`: The core method that performs the tool’s action and returns a `ToolResult`.
- **`ToolResult` ( `tools.ts`):** An interface defining the structure of a tool’s execution outcome:

  - `llmContent`: The factual content to be included in the history sent back to the LLM for context. This can be a simple string or a `PartListUnion` (an array of `Part` objects and strings) for rich content.
  - `returnDisplay`: A user-friendly string (often Markdown) or a special object (like `FileDiff`) for display in the CLI.
- **Returning Rich Content:** Tools are not limited to returning simple text. The `llmContent` can be a `PartListUnion`, which is an array that can contain a mix of `Part` objects (for images, audio, etc.) and `string` s. This allows a single tool execution to return multiple pieces of rich content.

- **Tool Registry ( `tool-registry.ts`):** A class ( `ToolRegistry`) responsible for:

  - **Registering Tools:** Holding a collection of all available built-in tools (e.g., `ReadFileTool`, `ShellTool`).
  - **Discovering Tools:** It can also discover tools dynamically:

    - **Command-based Discovery:** If `tools.discoveryCommand` is configured in settings, this command is executed. It’s expected to output JSON describing custom tools, which are then registered as `DiscoveredTool` instances.
    - **MCP-based Discovery:** If `mcp.serverCommand` is configured, the registry can connect to a Model Context Protocol (MCP) server to list and register tools ( `DiscoveredMCPTool`).
  - **Providing Schemas:** Exposing the `FunctionDeclaration` schemas of all registered tools to the Gemini model, so it knows what tools are available and how to use them.
  - **Retrieving Tools:** Allowing the core to get a specific tool by name for execution.

## Built-in Tools [Anchor](https://google-gemini.github.io/gemini-cli/docs/core/tools-api.html\#built-in-tools)

The core comes with a suite of pre-defined tools, typically found in `packages/core/src/tools/`. These include:

- **File System Tools:**
  - `LSTool` ( `ls.ts`): Lists directory contents.
  - `ReadFileTool` ( `read-file.ts`): Reads the content of a single file. It takes an `absolute_path` parameter, which must be an absolute path.
  - `WriteFileTool` ( `write-file.ts`): Writes content to a file.
  - `GrepTool` ( `grep.ts`): Searches for patterns in files.
  - `GlobTool` ( `glob.ts`): Finds files matching glob patterns.
  - `EditTool` ( `edit.ts`): Performs in-place modifications to files (often requiring confirmation).
  - `ReadManyFilesTool` ( `read-many-files.ts`): Reads and concatenates content from multiple files or glob patterns (used by the `@` command in CLI).
- **Execution Tools:**
  - `ShellTool` ( `shell.ts`): Executes arbitrary shell commands (requires careful sandboxing and user confirmation).
- **Web Tools:**
  - `WebFetchTool` ( `web-fetch.ts`): Fetches content from a URL.
  - `WebSearchTool` ( `web-search.ts`): Performs a web search.
- **Memory Tools:**
  - `MemoryTool` ( `memoryTool.ts`): Interacts with the AI’s memory.

Each of these tools extends `BaseTool` and implements the required methods for its specific functionality.

## Tool Execution Flow [Anchor](https://google-gemini.github.io/gemini-cli/docs/core/tools-api.html\#tool-execution-flow)

1. **Model Request:** The Gemini model, based on the user’s prompt and the provided tool schemas, decides to use a tool and returns a `FunctionCall` part in its response, specifying the tool name and arguments.
2. **Core Receives Request:** The core parses this `FunctionCall`.
3. **Tool Retrieval:** It looks up the requested tool in the `ToolRegistry`.
4. **Parameter Validation:** The tool’s `validateToolParams()` method is called.
5. **Confirmation (if needed):**
   - The tool’s `shouldConfirmExecute()` method is called.
   - If it returns details for confirmation, the core communicates this back to the CLI, which prompts the user.
   - The user’s decision (e.g., proceed, cancel) is sent back to the core.
6. **Execution:** If validated and confirmed (or if no confirmation is needed), the core calls the tool’s `execute()` method with the provided arguments and an `AbortSignal` (for potential cancellation).
7. **Result Processing:** The `ToolResult` from `execute()` is received by the core.
8. **Response to Model:** The `llmContent` from the `ToolResult` is packaged as a `FunctionResponse` and sent back to the Gemini model so it can continue generating a user-facing response.
9. **Display to User:** The `returnDisplay` from the `ToolResult` is sent to the CLI to show the user what the tool did.

## Extending with Custom Tools [Anchor](https://google-gemini.github.io/gemini-cli/docs/core/tools-api.html\#extending-with-custom-tools)

While direct programmatic registration of new tools by users isn’t explicitly detailed as a primary workflow in the provided files for typical end-users, the architecture supports extension through:

- **Command-based Discovery:** Advanced users or project administrators can define a `tools.discoveryCommand` in `settings.json`. This command, when run by the Gemini CLI core, should output a JSON array of `FunctionDeclaration` objects. The core will then make these available as `DiscoveredTool` instances. The corresponding `tools.callCommand` would then be responsible for actually executing these custom tools.
- **MCP Server(s):** For more complex scenarios, one or more MCP servers can be set up and configured via the `mcpServers` setting in `settings.json`. The Gemini CLI core can then discover and use tools exposed by these servers. As mentioned, if you have multiple MCP servers, the tool names will be prefixed with the server name from your configuration (e.g., `serverAlias__actualToolName`).

This tool system provides a flexible and powerful way to augment the Gemini model’s capabilities, making the Gemini CLI a versatile assistant for a wide range of tasks.

## Gemini CLI Authentication Methods
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Gemini CLI Authentication Setup

Gemini CLI requires authentication using Google’s services. Before using Gemini CLI, configure **one** of the following authentication methods:

- Interactive mode:
  - Recommended: Login with Google
  - Use Gemini API key
  - Use Vertex AI
- Headless (non-interactive) mode
- Google Cloud Shell

## Quick Check: Running in Google Cloud Shell? [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html\#quick-check-running-in-google-cloud-shell)

If you are running the Gemini CLI within a Google Cloud Shell environment, authentication is typically automatic using your Cloud Shell credentials.

## Authenticate in Interactive mode [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html\#authenticate-in-interactive-mode)

When you run Gemini CLI through the command-line, Gemini CLI will provide the following options:

```
> 1. Login with Google
> 2. Use Gemini API key
> 3. Vertex AI

```

The following sections provide instructions for each of these authentication options.

### Recommended: Login with Google [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html\#recommended-login-with-google)

If you are running Gemini CLI on your local machine, the simplest method is logging in with your Google account.

> **Important:** Use this method if you are a **Google AI Pro** or **Google AI Ultra** subscriber.

1. Select **Login with Google**. Gemini CLI will open a login prompt using your web browser.

If you are a **Google AI Pro** or **Google AI Ultra** subscriber, login with the Google account associated with your subscription.

2. Follow the on-screen instructions. Your credentials will be cached locally for future sessions.


> **Note:** This method requires a web browser on a machine that can communicate with the terminal running the CLI (e.g., your local machine). The browser will be redirected to a `localhost` URL that the CLI listens on during setup.


#### (Optional) Set your GOOGLE\_CLOUD\_PROJECT [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html\#optional-set-your-google_cloud_project)

When you log in using a Google account, you may be prompted to select a `GOOGLE_CLOUD_PROJECT`.

This can be necessary if you are:

- Using a Google Workspace account.
- Using a Gemini Code Assist license from the Google Developer Program.
- Using a license from a Gemini Code Assist subscription.
- Using the product outside the [supported regions](https://developers.google.com/gemini-code-assist/resources/available-locations) for free individual usage.
- A Google account holder under the age of 18.

If you fall into one of these categories, you must:

1. Have a Google Cloud Project ID.
2. [Enable the Gemini for Cloud API](https://cloud.google.com/gemini/docs/discover/set-up-gemini#enable-api).
3. [Configure necessary IAM access permissions](https://cloud.google.com/gemini/docs/discover/set-up-gemini#grant-iam).

To set the project ID, export the `GOOGLE_CLOUD_PROJECT` environment variable:

```
# Replace YOUR_PROJECT_ID with your actual Google Cloud Project ID
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"

```

To make this setting persistent, see [Persisting Environment Variables](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html#persisting-environment-variables).

### Use Gemini API Key [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html\#use-gemini-api-key)

If you don’t want to authenticate using your Google account, you can use an API key from Google AI Studio.

1. Obtain your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Set the `GEMINI_API_KEY` environment variable:





```
# Replace YOUR_GEMINI_API_KEY with the key from AI Studio
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

```


To make this setting persistent, see [Persisting Environment Variables](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html#persisting-environment-variables).

> **Warning:** Treat API keys, especially for services like Gemini, as sensitive credentials. Protect them to prevent unauthorized access and potential misuse of the service under your account.

### Use Vertex AI [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html\#use-vertex-ai)

If you intend to use Google Cloud’s Vertex AI platform, you have several authentication options:

- Application Default Credentials (ADC) and `gcloud`.
- A Service Account JSON key.
- A Google Cloud API key.

#### First: Set required environment variables [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html\#first-set-required-environment-variables)

Regardless of your method of authentication, you’ll typically need to set the following variables: `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`.

To set these variables:

```
# Replace with your project ID and desired location (e.g., us-central1)
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="YOUR_PROJECT_LOCATION"

```

#### A. Vertex AI - Application Default Credentials (ADC) using `gcloud` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html\#a-vertex-ai---application-default-credentials-adc-using-gcloud)

Consider this method of authentication if you have Google Cloud CLI installed.

> **Note:** If you have previously set `GOOGLE_API_KEY` or `GEMINI_API_KEY`, you must unset them to use ADC:

```
unset GOOGLE_API_KEY GEMINI_API_KEY

```

1. Ensure you have a Google Cloud project and Vertex AI API is enabled.
2. Log in to Google Cloud:





```
gcloud auth application-default login

```





See [Set up Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc) for details.

3. Ensure `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` are set.

#### B. Vertex AI - Service Account JSON key [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html\#b-vertex-ai---service-account-json-key)

Consider this method of authentication in non-interactive environments, CI/CD, or if your organization restricts user-based ADC or API key creation.

> **Note:** If you have previously set `GOOGLE_API_KEY` or `GEMINI_API_KEY`, you must unset them:

```
unset GOOGLE_API_KEY GEMINI_API_KEY

```

1. [Create a service account and key](https://cloud.google.com/iam/docs/keys-create-delete) and download the provided JSON file. Assign the “Vertex AI User” role to the service account.
2. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the JSON file’s absolute path:





```
# Replace /path/to/your/keyfile.json with the actual path
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"

```

3. Ensure `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` are set.

> **Warning:** Protect your service account key file as it provides access to your resources.

#### C. Vertex AI - Google Cloud API key [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html\#c-vertex-ai---google-cloud-api-key)

1. Obtain a Google Cloud API key: [Get an API Key](https://cloud.google.com/vertex-ai/generative-ai/docs/start/api-keys?usertype=newuser).
2. Set the `GOOGLE_API_KEY` environment variable:





```
# Replace YOUR_GOOGLE_API_KEY with your Vertex AI API key
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"

```






> **Note:** If you see errors like `"API keys are not supported by this API..."`, your organization might restrict API key usage for this service. Try the [Service Account JSON Key](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html#b-vertex-ai-service-account-json-key) or [ADC](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html#a-vertex-ai-application-default-credentials-adc-using-gcloud) methods instead.


To make any of these Vertex AI environment variable settings persistent, see [Persisting Environment Variables](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html#persisting-environment-variables).

## Persisting Environment Variables [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html\#persisting-environment-variables)

To avoid setting environment variables in every terminal session, you can:

1. **Add your environment variables to your shell configuration file:** Append the `export ...` commands to your shell’s startup file (e.g., `~/.bashrc`, `~/.zshrc`, or `~/.profile`) and reload your shell (e.g., `source ~/.bashrc`).





```
# Example for .bashrc
echo 'export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"' >> ~/.bashrc
source ~/.bashrc

```






> **Warning:** Be advised that when you export API keys or service account paths in your shell configuration file, any process executed from the shell can potentially read them.

2. **Use a `.env` file:** Create a `.gemini/.env` file in your project directory or home directory. Gemini CLI automatically loads variables from the first `.env` file it finds, searching up from the current directory, then in `~/.gemini/.env` or `~/.env`. `.gemini/.env` is recommended.

Example for user-wide settings:





```
mkdir -p ~/.gemini
cat >> ~/.gemini/.env <<'EOF'
GOOGLE_CLOUD_PROJECT="your-project-id"
# Add other variables like GEMINI_API_KEY as needed
EOF

```





Variables are loaded from the first file found, not merged.


## Non-interactive mode / headless environments [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html\#non-interactive-mode--headless-environments)

Non-interative mode / headless environments will use your existing authentication method, if an existing authentication credential is cached.

If you have not already logged in with an authentication credential (such as a Google account), you **must** configure authentication using environment variables:

1. **Gemini API Key:** Set `GEMINI_API_KEY`.
2. **Vertex AI:**
   - Set `GOOGLE_GENAI_USE_VERTEXAI=true`.
   - **With Google Cloud API Key:** Set `GOOGLE_API_KEY`.
   - **With ADC:** Ensure ADC is configured (e.g., via a service account with `GOOGLE_APPLICATION_CREDENTIALS`) and set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`.

The CLI will exit with an error in non-interactive mode if no suitable environment variables are found.

## What’s next? [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html\#whats-next)

Your authentication method affects your quotas, pricing, Terms of Service, and privacy notices. Review the following pages to learn more:

- [Gemini CLI: Quotas and Pricing](https://google-gemini.github.io/gemini-cli/docs/quota-and-pricing.html).
- [Gemini CLI: Terms of Service and Privacy Notice](https://google-gemini.github.io/gemini-cli/docs/tos-privacy.html).

## Gemini CLI Configuration Setup
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Gemini CLI Configuration

> **Note on Configuration Format, 9/17/25:** The format of the `settings.json` file has been updated to a new, more organized structure.
>
> - The new format will be supported in the stable release starting **\[09/10/25\]**.
> - Automatic migration from the old format to the new format will begin on **\[09/17/25\]**.
>
> For details on the previous format, please see the [v1 Configuration documentation](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration-v1.html).

Gemini CLI offers several ways to configure its behavior, including environment variables, command-line arguments, and settings files. This document outlines the different configuration methods and available settings.

## Configuration layers [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#configuration-layers)

Configuration is applied in the following order of precedence (lower numbers are overridden by higher numbers):

1. **Default values:** Hardcoded defaults within the application.
2. **System defaults file:** System-wide default settings that can be overridden by other settings files.
3. **User settings file:** Global settings for the current user.
4. **Project settings file:** Project-specific settings.
5. **System settings file:** System-wide settings that override all other settings files.
6. **Environment variables:** System-wide or session-specific variables, potentially loaded from `.env` files.
7. **Command-line arguments:** Values passed when launching the CLI.

## Settings files [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#settings-files)

Gemini CLI uses JSON settings files for persistent configuration. There are four locations for these files:

- **System defaults file:**
  - **Location:** `/etc/gemini-cli/system-defaults.json` (Linux), `C:\ProgramData\gemini-cli\system-defaults.json` (Windows) or `/Library/Application Support/GeminiCli/system-defaults.json` (macOS). The path can be overridden using the `GEMINI_CLI_SYSTEM_DEFAULTS_PATH` environment variable.
  - **Scope:** Provides a base layer of system-wide default settings. These settings have the lowest precedence and are intended to be overridden by user, project, or system override settings.
- **User settings file:**
  - **Location:** `~/.gemini/settings.json` (where `~` is your home directory).
  - **Scope:** Applies to all Gemini CLI sessions for the current user. User settings override system defaults.
- **Project settings file:**
  - **Location:** `.gemini/settings.json` within your project’s root directory.
  - **Scope:** Applies only when running Gemini CLI from that specific project. Project settings override user settings and system defaults.
- **System settings file:**
  - **Location:** `/etc/gemini-cli/settings.json` (Linux), `C:\ProgramData\gemini-cli\settings.json` (Windows) or `/Library/Application Support/GeminiCli/settings.json` (macOS). The path can be overridden using the `GEMINI_CLI_SYSTEM_SETTINGS_PATH` environment variable.
  - **Scope:** Applies to all Gemini CLI sessions on the system, for all users. System settings act as overrides, taking precedence over all other settings files. May be useful for system administrators at enterprises to have controls over users’ Gemini CLI setups.

**Note on environment variables in settings:** String values within your `settings.json` files can reference environment variables using either `$VAR_NAME` or `${VAR_NAME}` syntax. These variables will be automatically resolved when the settings are loaded. For example, if you have an environment variable `MY_API_TOKEN`, you could use it in `settings.json` like this: `"apiKey": "$MY_API_TOKEN"`.

> **Note for Enterprise Users:** For guidance on deploying and managing Gemini CLI in a corporate environment, please see the [Enterprise Configuration](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html) documentation.

### The `.gemini` directory in your project [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#the-gemini-directory-in-your-project)

In addition to a project settings file, a project’s `.gemini` directory can contain other project-specific files related to Gemini CLI’s operation, such as:

- [Custom sandbox profiles](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html#sandboxing) (e.g., `.gemini/sandbox-macos-custom.sb`, `.gemini/sandbox.Dockerfile`).

### Available settings in `settings.json` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#available-settings-in-settingsjson)

Settings are organized into categories. All settings should be placed within their corresponding top-level category object in your `settings.json` file.

#### `general` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#general)

- **`general.preferredEditor`** (string):

  - **Description:** The preferred editor to open files in.
  - **Default:** `undefined`
- **`general.vimMode`** (boolean):

  - **Description:** Enable Vim keybindings.
  - **Default:** `false`
- **`general.disableAutoUpdate`** (boolean):

  - **Description:** Disable automatic updates.
  - **Default:** `false`
- **`general.disableUpdateNag`** (boolean):

  - **Description:** Disable update notification prompts.
  - **Default:** `false`
- **`general.checkpointing.enabled`** (boolean):

  - **Description:** Enable session checkpointing for recovery.
  - **Default:** `false`

#### `output` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#output)

- **`output.format`** (string):

  - **Description:** The format of the CLI output.
  - **Default:** `"text"`
  - **Values:** `"text"`, `"json"`

#### `ui` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#ui)

- **`ui.theme`** (string):

  - **Description:** The color theme for the UI. See [Themes](https://google-gemini.github.io/gemini-cli/docs/cli/themes.html) for available options.
  - **Default:** `undefined`
- **`ui.customThemes`** (object):

  - **Description:** Custom theme definitions.
  - **Default:** `{}`
- **`ui.hideWindowTitle`** (boolean):

  - **Description:** Hide the window title bar.
  - **Default:** `false`
- **`ui.hideTips`** (boolean):

  - **Description:** Hide helpful tips in the UI.
  - **Default:** `false`
- **`ui.hideBanner`** (boolean):

  - **Description:** Hide the application banner.
  - **Default:** `false`
- **`ui.hideFooter`** (boolean):

  - **Description:** Hide the footer from the UI.
  - **Default:** `false`
- **`ui.showMemoryUsage`** (boolean):

  - **Description:** Display memory usage information in the UI.
  - **Default:** `false`
- **`ui.showLineNumbers`** (boolean):

  - **Description:** Show line numbers in the chat.
  - **Default:** `false`
- **`ui.showCitations`** (boolean):

  - **Description:** Show citations for generated text in the chat.
  - **Default:** `true`
- **`ui.accessibility.disableLoadingPhrases`** (boolean):

  - **Description:** Disable loading phrases for accessibility.
  - **Default:** `false`
- **`ui.customWittyPhrases`** (array of strings):

  - **Description:** A list of custom phrases to display during loading states. When provided, the CLI will cycle through these phrases instead of the default ones.
  - **Default:** `[]`

#### `ide` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#ide)

- **`ide.enabled`** (boolean):

  - **Description:** Enable IDE integration mode.
  - **Default:** `false`
- **`ide.hasSeenNudge`** (boolean):

  - **Description:** Whether the user has seen the IDE integration nudge.
  - **Default:** `false`

#### `privacy` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#privacy)

- **`privacy.usageStatisticsEnabled`** (boolean):

  - **Description:** Enable collection of usage statistics.
  - **Default:** `true`

#### `model` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#model)

- **`model.name`** (string):

  - **Description:** The Gemini model to use for conversations.
  - **Default:** `undefined`
- **`model.maxSessionTurns`** (number):

  - **Description:** Maximum number of user/model/tool turns to keep in a session. -1 means unlimited.
  - **Default:** `-1`
- **`model.summarizeToolOutput`** (object):

  - **Description:** Enables or disables the summarization of tool output. You can specify the token budget for the summarization using the `tokenBudget` setting. Note: Currently only the `run_shell_command` tool is supported. For example `{"run_shell_command": {"tokenBudget": 2000}}`
  - **Default:** `undefined`
- **`model.chatCompression.contextPercentageThreshold`** (number):

  - **Description:** Sets the threshold for chat history compression as a percentage of the model’s total token limit. This is a value between 0 and 1 that applies to both automatic compression and the manual `/compress` command. For example, a value of `0.6` will trigger compression when the chat history exceeds 60% of the token limit.
  - **Default:** `0.7`
- **`model.skipNextSpeakerCheck`** (boolean):

  - **Description:** Skip the next speaker check.
  - **Default:** `false`

#### `context` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#context)

- **`context.fileName`** (string or array of strings):

  - **Description:** The name of the context file(s).
  - **Default:** `undefined`
- **`context.importFormat`** (string):

  - **Description:** The format to use when importing memory.
  - **Default:** `undefined`
- **`context.discoveryMaxDirs`** (number):

  - **Description:** Maximum number of directories to search for memory.
  - **Default:** `200`
- **`context.includeDirectories`** (array):

  - **Description:** Additional directories to include in the workspace context. Missing directories will be skipped with a warning.
  - **Default:** `[]`
- **`context.loadFromIncludeDirectories`** (boolean):

  - **Description:** Controls the behavior of the `/memory refresh` command. If set to `true`, `GEMINI.md` files should be loaded from all directories that are added. If set to `false`, `GEMINI.md` should only be loaded from the current directory.
  - **Default:** `false`
- **`context.fileFiltering.respectGitIgnore`** (boolean):

  - **Description:** Respect .gitignore files when searching.
  - **Default:** `true`
- **`context.fileFiltering.respectGeminiIgnore`** (boolean):

  - **Description:** Respect .geminiignore files when searching.
  - **Default:** `true`
- **`context.fileFiltering.enableRecursiveFileSearch`** (boolean):

  - **Description:** Whether to enable searching recursively for filenames under the current tree when completing `@` prefixes in the prompt.
  - **Default:** `true`

#### `tools` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#tools)

- **`tools.sandbox`** (boolean or string):

  - **Description:** Sandbox execution environment (can be a boolean or a path string).
  - **Default:** `undefined`
- **`tools.shell.enableInteractiveShell`** (boolean):

Use `node-pty` for an interactive shell experience. Fallback to `child_process` still applies. Defaults to `false`.

- **`tools.core`** (array of strings):

  - **Description:** This can be used to restrict the set of built-in tools [with an allowlist](https://google-gemini.github.io/gemini-cli/docs/cli/enterprise.html#restricting-tool-access). See [Built-in Tools](https://google-gemini.github.io/gemini-cli/docs/core/tools-api.html#built-in-tools) for a list of core tools. The match semantics are the same as `tools.allowed`.
  - **Default:** `undefined`
- **`tools.exclude`** (array of strings):

  - **Description:** Tool names to exclude from discovery.
  - **Default:** `undefined`
- **`tools.allowed`** (array of strings):

  - **Description:** A list of tool names that will bypass the confirmation dialog. This is useful for tools that you trust and use frequently. For example, `["run_shell_command(git)", "run_shell_command(npm test)"]` will skip the confirmation dialog to run any `git` and `npm test` commands. See [Shell Tool command restrictions](https://google-gemini.github.io/gemini-cli/docs/tools/shell.html#command-restrictions) for details on prefix matching, command chaining, etc.
  - **Default:** `undefined`
- **`tools.discoveryCommand`** (string):

  - **Description:** Command to run for tool discovery.
  - **Default:** `undefined`
- **`tools.callCommand`** (string):

  - **Description:** Defines a custom shell command for calling a specific tool that was discovered using `tools.discoveryCommand`. The shell command must meet the following criteria:

    - It must take function `name` (exactly as in [function declaration](https://ai.google.dev/gemini-api/docs/function-calling#function-declarations)) as the first command line argument.
    - It must read function arguments as JSON on `stdin`, analogous to [`functionCall.args`](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference#functioncall).
    - It must return function output as JSON on `stdout`, analogous to [`functionResponse.response.content`](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference#functionresponse).
  - **Default:** `undefined`

#### `mcp` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#mcp)

- **`mcp.serverCommand`** (string):

  - **Description:** Command to start an MCP server.
  - **Default:** `undefined`
- **`mcp.allowed`** (array of strings):

  - **Description:** An allowlist of MCP servers to allow.
  - **Default:** `undefined`
- **`mcp.excluded`** (array of strings):

  - **Description:** A denylist of MCP servers to exclude.
  - **Default:** `undefined`

#### `security` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#security)

- **`security.folderTrust.enabled`** (boolean):

  - **Description:** Setting to track whether Folder trust is enabled.
  - **Default:** `false`
- **`security.auth.selectedType`** (string):

  - **Description:** The currently selected authentication type.
  - **Default:** `undefined`
- **`security.auth.enforcedType`** (string):

  - **Description:** The required auth type (useful for enterprises).
  - **Default:** `undefined`
- **`security.auth.useExternal`** (boolean):

  - **Description:** Whether to use an external authentication flow.
  - **Default:** `undefined`

#### `advanced` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#advanced)

- **`advanced.autoConfigureMemory`** (boolean):

  - **Description:** Automatically configure Node.js memory limits.
  - **Default:** `false`
- **`advanced.dnsResolutionOrder`** (string):

  - **Description:** The DNS resolution order.
  - **Default:** `undefined`
- **`advanced.excludedEnvVars`** (array of strings):

  - **Description:** Environment variables to exclude from project context.
  - **Default:** `["DEBUG","DEBUG_MODE"]`
- **`advanced.bugCommand`** (object):

  - **Description:** Configuration for the bug report command.
  - **Default:** `undefined`

#### `mcpServers` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#mcpservers)

Configures connections to one or more Model-Context Protocol (MCP) servers for discovering and using custom tools. Gemini CLI attempts to connect to each configured MCP server to discover available tools. If multiple MCP servers expose a tool with the same name, the tool names will be prefixed with the server alias you defined in the configuration (e.g., `serverAlias__actualToolName`) to avoid conflicts. Note that the system might strip certain schema properties from MCP tool definitions for compatibility. At least one of `command`, `url`, or `httpUrl` must be provided. If multiple are specified, the order of precedence is `httpUrl`, then `url`, then `command`.

- **`mcpServers.<SERVER_NAME>`** (object): The server parameters for the named server.

  - `command` (string, optional): The command to execute to start the MCP server via standard I/O.
  - `args` (array of strings, optional): Arguments to pass to the command.
  - `env` (object, optional): Environment variables to set for the server process.
  - `cwd` (string, optional): The working directory in which to start the server.
  - `url` (string, optional): The URL of an MCP server that uses Server-Sent Events (SSE) for communication.
  - `httpUrl` (string, optional): The URL of an MCP server that uses streamable HTTP for communication.
  - `headers` (object, optional): A map of HTTP headers to send with requests to `url` or `httpUrl`.
  - `timeout` (number, optional): Timeout in milliseconds for requests to this MCP server.
  - `trust` (boolean, optional): Trust this server and bypass all tool call confirmations.
  - `description` (string, optional): A brief description of the server, which may be used for display purposes.
  - `includeTools` (array of strings, optional): List of tool names to include from this MCP server. When specified, only the tools listed here will be available from this server (allowlist behavior). If not specified, all tools from the server are enabled by default.
  - `excludeTools` (array of strings, optional): List of tool names to exclude from this MCP server. Tools listed here will not be available to the model, even if they are exposed by the server. **Note:** `excludeTools` takes precedence over `includeTools` \- if a tool is in both lists, it will be excluded.

#### `telemetry` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#telemetry)

Configures logging and metrics collection for Gemini CLI. For more information, see [Telemetry](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html).

- **Properties:**
  - **`enabled`** (boolean): Whether or not telemetry is enabled.
  - **`target`** (string): The destination for collected telemetry. Supported values are `local` and `gcp`.
  - **`otlpEndpoint`** (string): The endpoint for the OTLP Exporter.
  - **`otlpProtocol`** (string): The protocol for the OTLP Exporter ( `grpc` or `http`).
  - **`logPrompts`** (boolean): Whether or not to include the content of user prompts in the logs.
  - **`outfile`** (string): The file to write telemetry to when `target` is `local`.
  - **`useCollector`** (boolean): Whether to use an external OTLP collector.

### Example `settings.json` [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#example-settingsjson)

Here is an example of a `settings.json` file with the nested structure, new as of v0.3.0:

```
{
  "general": {
    "vimMode": true,
    "preferredEditor": "code"
  },
  "ui": {
    "theme": "GitHub",
    "hideBanner": true,
    "hideTips": false,
    "customWittyPhrases": [\
      "You forget a thousand things every day. Make sure this is one of ’em",\
      "Connecting to AGI"\
    ]
  },
  "tools": {
    "sandbox": "docker",
    "discoveryCommand": "bin/get_tools",
    "callCommand": "bin/call_tool",
    "exclude": ["write_file"]
  },
  "mcpServers": {
    "mainServer": {
      "command": "bin/mcp_server.py"
    },
    "anotherServer": {
      "command": "node",
      "args": ["mcp_server.js", "--verbose"]
    }
  },
  "telemetry": {
    "enabled": true,
    "target": "local",
    "otlpEndpoint": "http://localhost:4317",
    "logPrompts": true
  },
  "privacy": {
    "usageStatisticsEnabled": true
  },
  "model": {
    "name": "gemini-1.5-pro-latest",
    "maxSessionTurns": 10,
    "summarizeToolOutput": {
      "run_shell_command": {
        "tokenBudget": 100
      }
    }
  },
  "context": {
    "fileName": ["CONTEXT.md", "GEMINI.md"],
    "includeDirectories": ["path/to/dir1", "~/path/to/dir2", "../path/to/dir3"],
    "loadFromIncludeDirectories": true,
    "fileFiltering": {
      "respectGitIgnore": false
    }
  },
  "advanced": {
    "excludedEnvVars": ["DEBUG", "DEBUG_MODE", "NODE_ENV"]
  }
}

```

## Shell History [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#shell-history)

The CLI keeps a history of shell commands you run. To avoid conflicts between different projects, this history is stored in a project-specific directory within your user’s home folder.

- **Location:** `~/.gemini/tmp/<project_hash>/shell_history`
  - `<project_hash>` is a unique identifier generated from your project’s root path.
  - The history is stored in a file named `shell_history`.

## Environment Variables & `.env` Files [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#environment-variables--env-files)

Environment variables are a common way to configure applications, especially for sensitive information like API keys or for settings that might change between environments. For authentication setup, see the [Authentication documentation](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html) which covers all available authentication methods.

The CLI automatically loads environment variables from an `.env` file. The loading order is:

1. `.env` file in the current working directory.
2. If not found, it searches upwards in parent directories until it finds an `.env` file or reaches the project root (identified by a `.git` folder) or the home directory.
3. If still not found, it looks for `~/.env` (in the user’s home directory).

**Environment Variable Exclusion:** Some environment variables (like `DEBUG` and `DEBUG_MODE`) are automatically excluded from being loaded from project `.env` files to prevent interference with gemini-cli behavior. Variables from `.gemini/.env` files are never excluded. You can customize this behavior using the `advanced.excludedEnvVars` setting in your `settings.json` file.

- **`GEMINI_API_KEY`**:

  - Your API key for the Gemini API.
  - One of several available [authentication methods](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html).
  - Set this in your shell profile (e.g., `~/.bashrc`, `~/.zshrc`) or an `.env` file.
- **`GEMINI_MODEL`**:

  - Specifies the default Gemini model to use.
  - Overrides the hardcoded default
  - Example: `export GEMINI_MODEL="gemini-2.5-flash"`
- **`GOOGLE_API_KEY`**:

  - Your Google Cloud API key.
  - Required for using Vertex AI in express mode.
  - Ensure you have the necessary permissions.
  - Example: `export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"`.
- **`GOOGLE_CLOUD_PROJECT`**:

  - Your Google Cloud Project ID.
  - Required for using Code Assist or Vertex AI.
  - If using Vertex AI, ensure you have the necessary permissions in this project.
  - **Cloud Shell Note:** When running in a Cloud Shell environment, this variable defaults to a special project allocated for Cloud Shell users. If you have `GOOGLE_CLOUD_PROJECT` set in your global environment in Cloud Shell, it will be overridden by this default. To use a different project in Cloud Shell, you must define `GOOGLE_CLOUD_PROJECT` in a `.env` file.
  - Example: `export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"`.
- **`GOOGLE_APPLICATION_CREDENTIALS`** (string):

  - **Description:** The path to your Google Application Credentials JSON file.
  - **Example:** `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"`
- **`OTLP_GOOGLE_CLOUD_PROJECT`**:

  - Your Google Cloud Project ID for Telemetry in Google Cloud
  - Example: `export OTLP_GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"`.
- **`GEMINI_TELEMETRY_ENABLED`**:

  - Set to `true` or `1` to enable telemetry. Any other value is treated as disabling it.
  - Overrides the `telemetry.enabled` setting.
- **`GEMINI_TELEMETRY_TARGET`**:

  - Sets the telemetry target ( `local` or `gcp`).
  - Overrides the `telemetry.target` setting.
- **`GEMINI_TELEMETRY_OTLP_ENDPOINT`**:

  - Sets the OTLP endpoint for telemetry.
  - Overrides the `telemetry.otlpEndpoint` setting.
- **`GEMINI_TELEMETRY_OTLP_PROTOCOL`**:

  - Sets the OTLP protocol ( `grpc` or `http`).
  - Overrides the `telemetry.otlpProtocol` setting.
- **`GEMINI_TELEMETRY_LOG_PROMPTS`**:

  - Set to `true` or `1` to enable or disable logging of user prompts. Any other value is treated as disabling it.
  - Overrides the `telemetry.logPrompts` setting.
- **`GEMINI_TELEMETRY_OUTFILE`**:

  - Sets the file path to write telemetry to when the target is `local`.
  - Overrides the `telemetry.outfile` setting.
- **`GEMINI_TELEMETRY_USE_COLLECTOR`**:

  - Set to `true` or `1` to enable or disable using an external OTLP collector. Any other value is treated as disabling it.
  - Overrides the `telemetry.useCollector` setting.
- **`GOOGLE_CLOUD_LOCATION`**:

  - Your Google Cloud Project Location (e.g., us-central1).
  - Required for using Vertex AI in non-express mode.
  - Example: `export GOOGLE_CLOUD_LOCATION="YOUR_PROJECT_LOCATION"`.
- **`GEMINI_SANDBOX`**:

  - Alternative to the `sandbox` setting in `settings.json`.
  - Accepts `true`, `false`, `docker`, `podman`, or a custom command string.
- **`SEATBELT_PROFILE`** (macOS specific):

  - Switches the Seatbelt ( `sandbox-exec`) profile on macOS.
  - `permissive-open`: (Default) Restricts writes to the project folder (and a few other folders, see `packages/cli/src/utils/sandbox-macos-permissive-open.sb`) but allows other operations.
  - `strict`: Uses a strict profile that declines operations by default.
  - `<profile_name>`: Uses a custom profile. To define a custom profile, create a file named `sandbox-macos-<profile_name>.sb` in your project’s `.gemini/` directory (e.g., `my-project/.gemini/sandbox-macos-custom.sb`).
- **`DEBUG` or `DEBUG_MODE`** (often used by underlying libraries or the CLI itself):

  - Set to `true` or `1` to enable verbose debug logging, which can be helpful for troubleshooting.
  - **Note:** These variables are automatically excluded from project `.env` files by default to prevent interference with gemini-cli behavior. Use `.gemini/.env` files if you need to set these for gemini-cli specifically.
- **`NO_COLOR`**:

  - Set to any value to disable all color output in the CLI.
- **`CLI_TITLE`**:

  - Set to a string to customize the title of the CLI.
- **`CODE_ASSIST_ENDPOINT`**:

  - Specifies the endpoint for the code assist server.
  - This is useful for development and testing.

## Command-Line Arguments [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#command-line-arguments)

Arguments passed directly when running the CLI can override other configurations for that specific session.

- **`--model <model_name>`** ( **`-m <model_name>`**):

  - Specifies the Gemini model to use for this session.
  - Example: `npm start -- --model gemini-1.5-pro-latest`
- **`--prompt <your_prompt>`** ( **`-p <your_prompt>`**):

  - Used to pass a prompt directly to the command. This invokes Gemini CLI in a non-interactive mode.
  - For scripting examples, use the `--output-format json` flag to get structured output.
- **`--prompt-interactive <your_prompt>`** ( **`-i <your_prompt>`**):

  - Starts an interactive session with the provided prompt as the initial input.
  - The prompt is processed within the interactive session, not before it.
  - Cannot be used when piping input from stdin.
  - Example: `gemini -i "explain this code"`
- **`--output-format <format>`**:

  - **Description:** Specifies the format of the CLI output for non-interactive mode.
  - **Values:**
    - `text`: (Default) The standard human-readable output.
    - `json`: A machine-readable JSON output.
  - **Note:** For structured output and scripting, use the `--output-format json` flag.
- **`--sandbox`** ( **`-s`**):

  - Enables sandbox mode for this session.
- **`--sandbox-image`**:

  - Sets the sandbox image URI.
- **`--debug`** ( **`-d`**):

  - Enables debug mode for this session, providing more verbose output.
- **`--all-files`** ( **`-a`**):

  - If set, recursively includes all files within the current directory as context for the prompt.
- **`--help`** (or **`-h`**):

  - Displays help information about command-line arguments.
- **`--show-memory-usage`**:

  - Displays the current memory usage.
- **`--yolo`**:

  - Enables YOLO mode, which automatically approves all tool calls.
- **`--approval-mode <mode>`**:

  - Sets the approval mode for tool calls. Available modes:
    - `default`: Prompt for approval on each tool call (default behavior)
    - `auto_edit`: Automatically approve edit tools (replace, write\_file) while prompting for others
    - `yolo`: Automatically approve all tool calls (equivalent to `--yolo`)
  - Cannot be used together with `--yolo`. Use `--approval-mode=yolo` instead of `--yolo` for the new unified approach.
  - Example: `gemini --approval-mode auto_edit`
- **`--allowed-tools <tool1,tool2,...>`**:

  - A comma-separated list of tool names that will bypass the confirmation dialog.
  - Example: `gemini --allowed-tools "ShellTool(git status)"`
- **`--telemetry`**:

  - Enables [telemetry](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html).
- **`--telemetry-target`**:

  - Sets the telemetry target. See [telemetry](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html) for more information.
- **`--telemetry-otlp-endpoint`**:

  - Sets the OTLP endpoint for telemetry. See [telemetry](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html) for more information.
- **`--telemetry-otlp-protocol`**:

  - Sets the OTLP protocol for telemetry ( `grpc` or `http`). Defaults to `grpc`. See [telemetry](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html) for more information.
- **`--telemetry-log-prompts`**:

  - Enables logging of prompts for telemetry. See [telemetry](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html) for more information.
- **`--checkpointing`**:

  - Enables [checkpointing](https://google-gemini.github.io/gemini-cli/docs/cli/checkpointing.html).
- **`--extensions <extension_name ...>`** ( **`-e <extension_name ...>`**):

  - Specifies a list of extensions to use for the session. If not provided, all available extensions are used.
  - Use the special term `gemini -e none` to disable all extensions.
  - Example: `gemini -e my-extension -e my-other-extension`
- **`--list-extensions`** ( **`-l`**):

  - Lists all available extensions and exits.
- **`--proxy`**:

  - Sets the proxy for the CLI.
  - Example: `--proxy http://localhost:7890`.
- **`--include-directories <dir1,dir2,...>`**:

  - Includes additional directories in the workspace for multi-directory support.
  - Can be specified multiple times or as comma-separated values.
  - 5 directories can be added at maximum.
  - Example: `--include-directories /path/to/project1,/path/to/project2` or `--include-directories /path/to/project1 --include-directories /path/to/project2`
- **`--screen-reader`**:

  - Enables screen reader mode, which adjusts the TUI for better compatibility with screen readers.
- **`--version`**:

  - Displays the version of the CLI.

## Context Files (Hierarchical Instructional Context) [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#context-files-hierarchical-instructional-context)

While not strictly configuration for the CLI’s _behavior_, context files (defaulting to `GEMINI.md` but configurable via the `context.fileName` setting) are crucial for configuring the _instructional context_ (also referred to as “memory”) provided to the Gemini model. This powerful feature allows you to give project-specific instructions, coding style guides, or any relevant background information to the AI, making its responses more tailored and accurate to your needs. The CLI includes UI elements, such as an indicator in the footer showing the number of loaded context files, to keep you informed about the active context.

- **Purpose:** These Markdown files contain instructions, guidelines, or context that you want the Gemini model to be aware of during your interactions. The system is designed to manage this instructional context hierarchically.

### Example Context File Content (e.g., `GEMINI.md`) [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#example-context-file-content-eg-geminimd)

Here’s a conceptual example of what a context file at the root of a TypeScript project might contain:

```
# Project: My Awesome TypeScript Library

## General Instructions:

- When generating new TypeScript code, please follow the existing coding style.
- Ensure all new functions and classes have JSDoc comments.
- Prefer functional programming paradigms where appropriate.
- All code should be compatible with TypeScript 5.0 and Node.js 20+.

## Coding Style:

- Use 2 spaces for indentation.
- Interface names should be prefixed with `I` (e.g., `IUserService`).
- Private class members should be prefixed with an underscore (`_`).
- Always use strict equality (`===` and `!==`).

## Specific Component: `src/api/client.ts`

- This file handles all outbound API requests.
- When adding new API call functions, ensure they include robust error handling and logging.
- Use the existing `fetchWithRetry` utility for all GET requests.

## Regarding Dependencies:

- Avoid introducing new external dependencies unless absolutely necessary.
- If a new dependency is required, please state the reason.

```

This example demonstrates how you can provide general project context, specific coding conventions, and even notes about particular files or components. The more relevant and precise your context files are, the better the AI can assist you. Project-specific context files are highly encouraged to establish conventions and context.

- **Hierarchical Loading and Precedence:** The CLI implements a sophisticated hierarchical memory system by loading context files (e.g., `GEMINI.md`) from several locations. Content from files lower in this list (more specific) typically overrides or supplements content from files higher up (more general). The exact concatenation order and final context can be inspected using the `/memory show` command. The typical loading order is:

1. **Global Context File:**
     - Location: `~/.gemini/<configured-context-filename>` (e.g., `~/.gemini/GEMINI.md` in your user home directory).
     - Scope: Provides default instructions for all your projects.
2. **Project Root & Ancestors Context Files:**
     - Location: The CLI searches for the configured context file in the current working directory and then in each parent directory up to either the project root (identified by a `.git` folder) or your home directory.
     - Scope: Provides context relevant to the entire project or a significant portion of it.
3. **Sub-directory Context Files (Contextual/Local):**
     - Location: The CLI also scans for the configured context file in subdirectories _below_ the current working directory (respecting common ignore patterns like `node_modules`, `.git`, etc.). The breadth of this search is limited to 200 directories by default, but can be configured with the `context.discoveryMaxDirs` setting in your `settings.json` file.
     - Scope: Allows for highly specific instructions relevant to a particular component, module, or subsection of your project.
- **Concatenation & UI Indication:** The contents of all found context files are concatenated (with separators indicating their origin and path) and provided as part of the system prompt to the Gemini model. The CLI footer displays the count of loaded context files, giving you a quick visual cue about the active instructional context.
- **Importing Content:** You can modularize your context files by importing other Markdown files using the `@path/to/file.md` syntax. For more details, see the [Memory Import Processor documentation](https://google-gemini.github.io/gemini-cli/docs/core/memport.html).
- **Commands for Memory Management:**
  - Use `/memory refresh` to force a re-scan and reload of all context files from all configured locations. This updates the AI’s instructional context.
  - Use `/memory show` to display the combined instructional context currently loaded, allowing you to verify the hierarchy and content being used by the AI.
  - See the [Commands documentation](https://google-gemini.github.io/gemini-cli/docs/cli/commands.html#memory) for full details on the `/memory` command and its sub-commands ( `show` and `refresh`).

By understanding and utilizing these configuration layers and the hierarchical nature of context files, you can effectively manage the AI’s memory and tailor the Gemini CLI’s responses to your specific needs and projects.

## Sandboxing [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#sandboxing)

The Gemini CLI can execute potentially unsafe operations (like shell commands and file modifications) within a sandboxed environment to protect your system.

Sandboxing is disabled by default, but you can enable it in a few ways:

- Using `--sandbox` or `-s` flag.
- Setting `GEMINI_SANDBOX` environment variable.
- Sandbox is enabled when using `--yolo` or `--approval-mode=yolo` by default.

By default, it uses a pre-built `gemini-cli-sandbox` Docker image.

For project-specific sandboxing needs, you can create a custom Dockerfile at `.gemini/sandbox.Dockerfile` in your project’s root directory. This Dockerfile can be based on the base sandbox image:

```
FROM gemini-cli-sandbox

# Add your custom dependencies or configurations here
# For example:
# RUN apt-get update && apt-get install -y some-package
# COPY ./my-config /app/my-config

```

When `.gemini/sandbox.Dockerfile` exists, you can use `BUILD_SANDBOX` environment variable when running Gemini CLI to automatically build the custom sandbox image:

```
BUILD_SANDBOX=1 gemini -s

```

## Usage Statistics [Anchor](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html\#usage-statistics)

To help us improve the Gemini CLI, we collect anonymized usage statistics. This data helps us understand how the CLI is used, identify common issues, and prioritize new features.

**What we collect:**

- **Tool Calls:** We log the names of the tools that are called, whether they succeed or fail, and how long they take to execute. We do not collect the arguments passed to the tools or any data returned by them.
- **API Requests:** We log the Gemini model used for each request, the duration of the request, and whether it was successful. We do not collect the content of the prompts or responses.
- **Session Information:** We collect information about the configuration of the CLI, such as the enabled tools and the approval mode.

**What we DON’T collect:**

- **Personally Identifiable Information (PII):** We do not collect any personal information, such as your name, email address, or API keys.
- **Prompt and Response Content:** We do not log the content of your prompts or the responses from the Gemini model.
- **File Content:** We do not log the content of any files that are read or written by the CLI.

**How to opt out:**

You can opt out of usage statistics collection at any time by setting the `usageStatisticsEnabled` property to `false` under the `privacy` category in your `settings.json` file:

```
{
  "privacy": {
    "usageStatisticsEnabled": false
  }
}

```

## Gemini CLI Memory Tool
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Memory Tool ( `save_memory`)

This document describes the `save_memory` tool for the Gemini CLI.

## Description [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/memory.html\#description)

Use `save_memory` to save and recall information across your Gemini CLI sessions. With `save_memory`, you can direct the CLI to remember key details across sessions, providing personalized and directed assistance.

### Arguments [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/memory.html\#arguments)

`save_memory` takes one argument:

- `fact` (string, required): The specific fact or piece of information to remember. This should be a clear, self-contained statement written in natural language.

## How to use `save_memory` with the Gemini CLI [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/memory.html\#how-to-use-save_memory-with-the-gemini-cli)

The tool appends the provided `fact` to a special `GEMINI.md` file located in the user’s home directory ( `~/.gemini/GEMINI.md`). This file can be configured to have a different name.

Once added, the facts are stored under a `## Gemini Added Memories` section. This file is loaded as context in subsequent sessions, allowing the CLI to recall the saved information.

Usage:

```
save_memory(fact="Your fact here.")

```

### `save_memory` examples [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/memory.html\#save_memory-examples)

Remember a user preference:

```
save_memory(fact="My preferred programming language is Python.")

```

Store a project-specific detail:

```
save_memory(fact="The project I'm currently working on is called 'gemini-cli'.")

```

## Important notes [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/memory.html\#important-notes)

- **General usage:** This tool should be used for concise, important facts. It is not intended for storing large amounts of data or conversational history.
- **Memory file:** The memory file is a plain text Markdown file, so you can view and edit it manually if needed.

## Page Not Found Error
# 404

**File not found**

The site configured at this address does not
contain the requested file.


If this is your site, make sure that the filename case matches the URL
as well as any file permissions.

For root URLs (like `http://example.com/`) you must provide an
`index.html` file.


[Read the full documentation](https://help.github.com/pages/)
for more information about using **GitHub Pages**.


[GitHub Status](https://githubstatus.com/) —
[@githubstatus](https://twitter.com/githubstatus)

[![](<Base64-Image-Removed>)](https://google-gemini.github.io/)[![](<Base64-Image-Removed>)](https://google-gemini.github.io/)

## MCP Server Configuration Guide
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# MCP servers with the Gemini CLI

This document provides a guide to configuring and using Model Context Protocol (MCP) servers with the Gemini CLI.

## What is an MCP server? [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#what-is-an-mcp-server)

An MCP server is an application that exposes tools and resources to the Gemini CLI through the Model Context Protocol, allowing it to interact with external systems and data sources. MCP servers act as a bridge between the Gemini model and your local environment or other services like APIs.

An MCP server enables the Gemini CLI to:

- **Discover tools:** List available tools, their descriptions, and parameters through standardized schema definitions.
- **Execute tools:** Call specific tools with defined arguments and receive structured responses.
- **Access resources:** Read data from specific resources (though the Gemini CLI primarily focuses on tool execution).

With an MCP server, you can extend the Gemini CLI’s capabilities to perform actions beyond its built-in features, such as interacting with databases, APIs, custom scripts, or specialized workflows.

## Core Integration Architecture [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#core-integration-architecture)

The Gemini CLI integrates with MCP servers through a sophisticated discovery and execution system built into the core package ( `packages/core/src/tools/`):

### Discovery Layer ( `mcp-client.ts`) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#discovery-layer-mcp-clientts)

The discovery process is orchestrated by `discoverMcpTools()`, which:

1. **Iterates through configured servers** from your `settings.json` `mcpServers` configuration
2. **Establishes connections** using appropriate transport mechanisms (Stdio, SSE, or Streamable HTTP)
3. **Fetches tool definitions** from each server using the MCP protocol
4. **Sanitizes and validates** tool schemas for compatibility with the Gemini API
5. **Registers tools** in the global tool registry with conflict resolution

### Execution Layer ( `mcp-tool.ts`) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#execution-layer-mcp-toolts)

Each discovered MCP tool is wrapped in a `DiscoveredMCPTool` instance that:

- **Handles confirmation logic** based on server trust settings and user preferences
- **Manages tool execution** by calling the MCP server with proper parameters
- **Processes responses** for both the LLM context and user display
- **Maintains connection state** and handles timeouts

### Transport Mechanisms [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#transport-mechanisms)

The Gemini CLI supports three MCP transport types:

- **Stdio Transport:** Spawns a subprocess and communicates via stdin/stdout
- **SSE Transport:** Connects to Server-Sent Events endpoints
- **Streamable HTTP Transport:** Uses HTTP streaming for communication

## How to set up your MCP server [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#how-to-set-up-your-mcp-server)

The Gemini CLI uses the `mcpServers` configuration in your `settings.json` file to locate and connect to MCP servers. This configuration supports multiple servers with different transport mechanisms.

### Configure the MCP server in settings.json [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#configure-the-mcp-server-in-settingsjson)

You can configure MCP servers in your `settings.json` file in two main ways: through the top-level `mcpServers` object for specific server definitions, and through the `mcp` object for global settings that control server discovery and execution.

#### Global MCP Settings ( `mcp`) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#global-mcp-settings-mcp)

The `mcp` object in your `settings.json` allows you to define global rules for all MCP servers.

- **`mcp.serverCommand`** (string): A global command to start an MCP server.
- **`mcp.allowed`** (array of strings): A list of MCP server names to allow. If this is set, only servers from this list (matching the keys in the `mcpServers` object) will be connected to.
- **`mcp.excluded`** (array of strings): A list of MCP server names to exclude. Servers in this list will not be connected to.

**Example:**

```
{
  "mcp": {
    "allowed": ["my-trusted-server"],
    "excluded": ["experimental-server"]
  }
}

```

#### Server-Specific Configuration ( `mcpServers`) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#server-specific-configuration-mcpservers)

The `mcpServers` object is where you define each individual MCP server you want the CLI to connect to.

### Configuration Structure [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#configuration-structure)

Add an `mcpServers` object to your `settings.json` file:

```
{ ...file contains other config objects
  "mcpServers": {
    "serverName": {
      "command": "path/to/server",
      "args": ["--arg1", "value1"],
      "env": {
        "API_KEY": "$MY_API_TOKEN"
      },
      "cwd": "./server-directory",
      "timeout": 30000,
      "trust": false
    }
  }
}

```

### Configuration Properties [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#configuration-properties)

Each server configuration supports the following properties:

#### Required (one of the following) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#required-one-of-the-following)

- **`command`** (string): Path to the executable for Stdio transport
- **`url`** (string): SSE endpoint URL (e.g., `"http://localhost:8080/sse"`)
- **`httpUrl`** (string): HTTP streaming endpoint URL

#### Optional [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#optional)

- **`args`** (string\[\]): Command-line arguments for Stdio transport
- **`headers`** (object): Custom HTTP headers when using `url` or `httpUrl`
- **`env`** (object): Environment variables for the server process. Values can reference environment variables using `$VAR_NAME` or `${VAR_NAME}` syntax
- **`cwd`** (string): Working directory for Stdio transport
- **`timeout`** (number): Request timeout in milliseconds (default: 600,000ms = 10 minutes)
- **`trust`** (boolean): When `true`, bypasses all tool call confirmations for this server (default: `false`)
- **`includeTools`** (string\[\]): List of tool names to include from this MCP server. When specified, only the tools listed here will be available from this server (allowlist behavior). If not specified, all tools from the server are enabled by default.
- **`excludeTools`** (string\[\]): List of tool names to exclude from this MCP server. Tools listed here will not be available to the model, even if they are exposed by the server. **Note:** `excludeTools` takes precedence over `includeTools` \- if a tool is in both lists, it will be excluded.
- **`targetAudience`** (string): The OAuth Client ID allowlisted on the IAP-protected application you are trying to access. Used with `authProviderType: 'service_account_impersonation'`.
- **`targetServiceAccount`** (string): The email address of the Google Cloud Service Account to impersonate. Used with `authProviderType: 'service_account_impersonation'`.

### OAuth Support for Remote MCP Servers [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#oauth-support-for-remote-mcp-servers)

The Gemini CLI supports OAuth 2.0 authentication for remote MCP servers using SSE or HTTP transports. This enables secure access to MCP servers that require authentication.

#### Automatic OAuth Discovery [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#automatic-oauth-discovery)

For servers that support OAuth discovery, you can omit the OAuth configuration and let the CLI discover it automatically:

```
{
  "mcpServers": {
    "discoveredServer": {
      "url": "https://api.example.com/sse"
    }
  }
}

```

The CLI will automatically:

- Detect when a server requires OAuth authentication (401 responses)
- Discover OAuth endpoints from server metadata
- Perform dynamic client registration if supported
- Handle the OAuth flow and token management

#### Authentication Flow [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#authentication-flow)

When connecting to an OAuth-enabled server:

1. **Initial connection attempt** fails with 401 Unauthorized
2. **OAuth discovery** finds authorization and token endpoints
3. **Browser opens** for user authentication (requires local browser access)
4. **Authorization code** is exchanged for access tokens
5. **Tokens are stored** securely for future use
6. **Connection retry** succeeds with valid tokens

#### Browser Redirect Requirements [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#browser-redirect-requirements)

**Important:** OAuth authentication requires that your local machine can:

- Open a web browser for authentication
- Receive redirects on `http://localhost:7777/oauth/callback`

This feature will not work in:

- Headless environments without browser access
- Remote SSH sessions without X11 forwarding
- Containerized environments without browser support

#### Managing OAuth Authentication [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#managing-oauth-authentication)

Use the `/mcp auth` command to manage OAuth authentication:

```
# List servers requiring authentication
/mcp auth

# Authenticate with a specific server
/mcp auth serverName

# Re-authenticate if tokens expire
/mcp auth serverName

```

#### OAuth Configuration Properties [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#oauth-configuration-properties)

- **`enabled`** (boolean): Enable OAuth for this server
- **`clientId`** (string): OAuth client identifier (optional with dynamic registration)
- **`clientSecret`** (string): OAuth client secret (optional for public clients)
- **`authorizationUrl`** (string): OAuth authorization endpoint (auto-discovered if omitted)
- **`tokenUrl`** (string): OAuth token endpoint (auto-discovered if omitted)
- **`scopes`** (string\[\]): Required OAuth scopes
- **`redirectUri`** (string): Custom redirect URI (defaults to `http://localhost:7777/oauth/callback`)
- **`tokenParamName`** (string): Query parameter name for tokens in SSE URLs
- **`audiences`** (string\[\]): Audiences the token is valid for

#### Token Management [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#token-management)

OAuth tokens are automatically:

- **Stored securely** in `~/.gemini/mcp-oauth-tokens.json`
- **Refreshed** when expired (if refresh tokens are available)
- **Validated** before each connection attempt
- **Cleaned up** when invalid or expired

#### Authentication Provider Type [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#authentication-provider-type)

You can specify the authentication provider type using the `authProviderType` property:

- **`authProviderType`** (string): Specifies the authentication provider. Can be one of the following:

  - **`dynamic_discovery`** (default): The CLI will automatically discover the OAuth configuration from the server.
  - **`google_credentials`**: The CLI will use the Google Application Default Credentials (ADC) to authenticate with the server. When using this provider, you must specify the required scopes.
  - **`service_account_impersonation`**: The CLI will impersonate a Google Cloud Service Account to authenticate with the server. This is useful for accessing IAP-protected services (this was specifically designed for Cloud Run services).

#### Google Credentials [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#google-credentials)

```
{
  "mcpServers": {
    "googleCloudServer": {
      "httpUrl": "https://my-gcp-service.run.app/mcp",
      "authProviderType": "google_credentials",
      "oauth": {
        "scopes": ["https://www.googleapis.com/auth/userinfo.email"]
      }
    }
  }
}

```

#### Service Account Impersonation [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#service-account-impersonation)

To authenticate with a server using Service Account Impersonation, you must set the `authProviderType` to `service_account_impersonation` and provide the following properties:

- **`targetAudience`** (string): The OAuth Client ID allowslisted on the IAP-protected application you are trying to access.
- **`targetServiceAccount`** (string): The email address of the Google Cloud Service Account to impersonate.

The CLI will use your local Application Default Credentials (ADC) to generate an OIDC ID token for the specified service account and audience. This token will then be used to authenticate with the MCP server.

#### Setup Instructions [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#setup-instructions)

1. **[Create](https://cloud.google.com/iap/docs/oauth-client-creation) or use an existing OAuth 2.0 client ID.** To use an existing OAuth 2.0 client ID, follow the steps in [How to share OAuth Clients](https://cloud.google.com/iap/docs/sharing-oauth-clients).
2. **Add the OAuth ID to the allowlist for [programmatic access](https://cloud.google.com/iap/docs/sharing-oauth-clients#programmatic_access) for the application.** Since Cloud Run is not yet a supported resource type in gcloud iap, you must allowlist the Client ID on the project.
3. **Create a service account.** [Documentation](https://cloud.google.com/iam/docs/service-accounts-create#creating), [Cloud Console Link](https://console.cloud.google.com/iam-admin/serviceaccounts)
4. **Add both the service account and users to the IAP Policy** in the “Security” tab of the Cloud Run service itself or via gcloud.
5. **Grant all users and groups** who will access the MCP Server the necessary permissions to [impersonate the service account](https://cloud.google.com/docs/authentication/use-service-account-impersonation) (i.e., `roles/iam.serviceAccountTokenCreator`).
6. **[Enable](https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com) the IAM Credentials API** for your project.

### Example Configurations [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#example-configurations)

#### Python MCP Server (Stdio) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#python-mcp-server-stdio)

```
{
  "mcpServers": {
    "pythonTools": {
      "command": "python",
      "args": ["-m", "my_mcp_server", "--port", "8080"],
      "cwd": "./mcp-servers/python",
      "env": {
        "DATABASE_URL": "$DB_CONNECTION_STRING",
        "API_KEY": "${EXTERNAL_API_KEY}"
      },
      "timeout": 15000
    }
  }
}

```

#### Node.js MCP Server (Stdio) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#nodejs-mcp-server-stdio)

```
{
  "mcpServers": {
    "nodeServer": {
      "command": "node",
      "args": ["dist/server.js", "--verbose"],
      "cwd": "./mcp-servers/node",
      "trust": true
    }
  }
}

```

#### Docker-based MCP Server [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#docker-based-mcp-server)

```
{
  "mcpServers": {
    "dockerizedServer": {
      "command": "docker",
      "args": [\
        "run",\
        "-i",\
        "--rm",\
        "-e",\
        "API_KEY",\
        "-v",\
        "${PWD}:/workspace",\
        "my-mcp-server:latest"\
      ],
      "env": {
        "API_KEY": "$EXTERNAL_SERVICE_TOKEN"
      }
    }
  }
}

```

#### HTTP-based MCP Server [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#http-based-mcp-server)

```
{
  "mcpServers": {
    "httpServer": {
      "httpUrl": "http://localhost:3000/mcp",
      "timeout": 5000
    }
  }
}

```

#### HTTP-based MCP Server with Custom Headers [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#http-based-mcp-server-with-custom-headers)

```
{
  "mcpServers": {
    "httpServerWithAuth": {
      "httpUrl": "http://localhost:3000/mcp",
      "headers": {
        "Authorization": "Bearer your-api-token",
        "X-Custom-Header": "custom-value",
        "Content-Type": "application/json"
      },
      "timeout": 5000
    }
  }
}

```

#### MCP Server with Tool Filtering [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#mcp-server-with-tool-filtering)

```
{
  "mcpServers": {
    "filteredServer": {
      "command": "python",
      "args": ["-m", "my_mcp_server"],
      "includeTools": ["safe_tool", "file_reader", "data_processor"],
      // "excludeTools": ["dangerous_tool", "file_deleter"],
      "timeout": 30000
    }
  }
}

```

### SSE MCP Server with SA Impersonation [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#sse-mcp-server-with-sa-impersonation)

```
{
  "mcpServers": {
    "myIapProtectedServer": {
      "url": "https://my-iap-service.run.app/sse",
      "authProviderType": "service_account_impersonation",
      "targetAudience": "YOUR_IAP_CLIENT_ID.apps.googleusercontent.com",
      "targetServiceAccount": "your-sa@your-project.iam.gserviceaccount.com"
    }
  }
}

```

## Discovery Process Deep Dive [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#discovery-process-deep-dive)

When the Gemini CLI starts, it performs MCP server discovery through the following detailed process:

### 1\. Server Iteration and Connection [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#1-server-iteration-and-connection)

For each configured server in `mcpServers`:

1. **Status tracking begins:** Server status is set to `CONNECTING`
2. **Transport selection:** Based on configuration properties:

   - `httpUrl` → `StreamableHTTPClientTransport`
   - `url` → `SSEClientTransport`
   - `command` → `StdioClientTransport`
3. **Connection establishment:** The MCP client attempts to connect with the configured timeout
4. **Error handling:** Connection failures are logged and the server status is set to `DISCONNECTED`

### 2\. Tool Discovery [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#2-tool-discovery)

Upon successful connection:

1. **Tool listing:** The client calls the MCP server’s tool listing endpoint
2. **Schema validation:** Each tool’s function declaration is validated
3. **Tool filtering:** Tools are filtered based on `includeTools` and `excludeTools` configuration
4. **Name sanitization:** Tool names are cleaned to meet Gemini API requirements:

   - Invalid characters (non-alphanumeric, underscore, dot, hyphen) are replaced with underscores
   - Names longer than 63 characters are truncated with middle replacement ( `___`)

### 3\. Conflict Resolution [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#3-conflict-resolution)

When multiple servers expose tools with the same name:

1. **First registration wins:** The first server to register a tool name gets the unprefixed name
2. **Automatic prefixing:** Subsequent servers get prefixed names: `serverName__toolName`
3. **Registry tracking:** The tool registry maintains mappings between server names and their tools

### 4\. Schema Processing [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#4-schema-processing)

Tool parameter schemas undergo sanitization for Gemini API compatibility:

- **`$schema` properties** are removed
- **`additionalProperties`** are stripped
- **`anyOf` with `default`** have their default values removed (Vertex AI compatibility)
- **Recursive processing** applies to nested schemas

### 5\. Connection Management [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#5-connection-management)

After discovery:

- **Persistent connections:** Servers that successfully register tools maintain their connections
- **Cleanup:** Servers that provide no usable tools have their connections closed
- **Status updates:** Final server statuses are set to `CONNECTED` or `DISCONNECTED`

## Tool Execution Flow [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#tool-execution-flow)

When the Gemini model decides to use an MCP tool, the following execution flow occurs:

### 1\. Tool Invocation [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#1-tool-invocation)

The model generates a `FunctionCall` with:

- **Tool name:** The registered name (potentially prefixed)
- **Arguments:** JSON object matching the tool’s parameter schema

### 2\. Confirmation Process [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#2-confirmation-process)

Each `DiscoveredMCPTool` implements sophisticated confirmation logic:

#### Trust-based Bypass [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#trust-based-bypass)

```
if (this.trust) {
  return false; // No confirmation needed
}

```

#### Dynamic Allow-listing [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#dynamic-allow-listing)

The system maintains internal allow-lists for:

- **Server-level:** `serverName` → All tools from this server are trusted
- **Tool-level:** `serverName.toolName` → This specific tool is trusted

#### User Choice Handling [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#user-choice-handling)

When confirmation is required, users can choose:

- **Proceed once:** Execute this time only
- **Always allow this tool:** Add to tool-level allow-list
- **Always allow this server:** Add to server-level allow-list
- **Cancel:** Abort execution

### 3\. Execution [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#3-execution)

Upon confirmation (or trust bypass):

1. **Parameter preparation:** Arguments are validated against the tool’s schema
2. **MCP call:** The underlying `CallableTool` invokes the server with:





```
const functionCalls = [\
     {\
       name: this.serverToolName, // Original server tool name\
       args: params,\
     },\
];

```

3. **Response processing:** Results are formatted for both LLM context and user display

### 4\. Response Handling [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#4-response-handling)

The execution result contains:

- **`llmContent`:** Raw response parts for the language model’s context
- **`returnDisplay`:** Formatted output for user display (often JSON in markdown code blocks)

## How to interact with your MCP server [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#how-to-interact-with-your-mcp-server)

### Using the `/mcp` Command [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#using-the-mcp-command)

The `/mcp` command provides comprehensive information about your MCP server setup:

```
/mcp

```

This displays:

- **Server list:** All configured MCP servers
- **Connection status:** `CONNECTED`, `CONNECTING`, or `DISCONNECTED`
- **Server details:** Configuration summary (excluding sensitive data)
- **Available tools:** List of tools from each server with descriptions
- **Discovery state:** Overall discovery process status

### Example `/mcp` Output [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#example-mcp-output)

```
MCP Servers Status:

📡 pythonTools (CONNECTED)
  Command: python -m my_mcp_server --port 8080
  Working Directory: ./mcp-servers/python
  Timeout: 15000ms
  Tools: calculate_sum, file_analyzer, data_processor

🔌 nodeServer (DISCONNECTED)
  Command: node dist/server.js --verbose
  Error: Connection refused

🐳 dockerizedServer (CONNECTED)
  Command: docker run -i --rm -e API_KEY my-mcp-server:latest
  Tools: docker__deploy, docker__status

Discovery State: COMPLETED

```

### Tool Usage [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#tool-usage)

Once discovered, MCP tools are available to the Gemini model like built-in tools. The model will automatically:

1. **Select appropriate tools** based on your requests
2. **Present confirmation dialogs** (unless the server is trusted)
3. **Execute tools** with proper parameters
4. **Display results** in a user-friendly format

## Status Monitoring and Troubleshooting [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#status-monitoring-and-troubleshooting)

### Connection States [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#connection-states)

The MCP integration tracks several states:

#### Server Status ( `MCPServerStatus`) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#server-status-mcpserverstatus)

- **`DISCONNECTED`:** Server is not connected or has errors
- **`CONNECTING`:** Connection attempt in progress
- **`CONNECTED`:** Server is connected and ready

#### Discovery State ( `MCPDiscoveryState`) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#discovery-state-mcpdiscoverystate)

- **`NOT_STARTED`:** Discovery hasn’t begun
- **`IN_PROGRESS`:** Currently discovering servers
- **`COMPLETED`:** Discovery finished (with or without errors)

### Common Issues and Solutions [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#common-issues-and-solutions)

#### Server Won’t Connect [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#server-wont-connect)

**Symptoms:** Server shows `DISCONNECTED` status

**Troubleshooting:**

1. **Check configuration:** Verify `command`, `args`, and `cwd` are correct
2. **Test manually:** Run the server command directly to ensure it works
3. **Check dependencies:** Ensure all required packages are installed
4. **Review logs:** Look for error messages in the CLI output
5. **Verify permissions:** Ensure the CLI can execute the server command

#### No Tools Discovered [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#no-tools-discovered)

**Symptoms:** Server connects but no tools are available

**Troubleshooting:**

1. **Verify tool registration:** Ensure your server actually registers tools
2. **Check MCP protocol:** Confirm your server implements the MCP tool listing correctly
3. **Review server logs:** Check stderr output for server-side errors
4. **Test tool listing:** Manually test your server’s tool discovery endpoint

#### Tools Not Executing [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#tools-not-executing)

**Symptoms:** Tools are discovered but fail during execution

**Troubleshooting:**

1. **Parameter validation:** Ensure your tool accepts the expected parameters
2. **Schema compatibility:** Verify your input schemas are valid JSON Schema
3. **Error handling:** Check if your tool is throwing unhandled exceptions
4. **Timeout issues:** Consider increasing the `timeout` setting

#### Sandbox Compatibility [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#sandbox-compatibility)

**Symptoms:** MCP servers fail when sandboxing is enabled

**Solutions:**

1. **Docker-based servers:** Use Docker containers that include all dependencies
2. **Path accessibility:** Ensure server executables are available in the sandbox
3. **Network access:** Configure sandbox to allow necessary network connections
4. **Environment variables:** Verify required environment variables are passed through

### Debugging Tips [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#debugging-tips)

1. **Enable debug mode:** Run the CLI with `--debug` for verbose output
2. **Check stderr:** MCP server stderr is captured and logged (INFO messages filtered)
3. **Test isolation:** Test your MCP server independently before integrating
4. **Incremental setup:** Start with simple tools before adding complex functionality
5. **Use `/mcp` frequently:** Monitor server status during development

## Important Notes [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#important-notes)

### Security Considerations [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#security-considerations)

- **Trust settings:** The `trust` option bypasses all confirmation dialogs. Use cautiously and only for servers you completely control
- **Access tokens:** Be security-aware when configuring environment variables containing API keys or tokens
- **Sandbox compatibility:** When using sandboxing, ensure MCP servers are available within the sandbox environment
- **Private data:** Using broadly scoped personal access tokens can lead to information leakage between repositories

### Performance and Resource Management [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#performance-and-resource-management)

- **Connection persistence:** The CLI maintains persistent connections to servers that successfully register tools
- **Automatic cleanup:** Connections to servers providing no tools are automatically closed
- **Timeout management:** Configure appropriate timeouts based on your server’s response characteristics
- **Resource monitoring:** MCP servers run as separate processes and consume system resources

### Schema Compatibility [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#schema-compatibility)

- **Property stripping:** The system automatically removes certain schema properties ( `$schema`, `additionalProperties`) for Gemini API compatibility
- **Name sanitization:** Tool names are automatically sanitized to meet API requirements
- **Conflict resolution:** Tool name conflicts between servers are resolved through automatic prefixing

This comprehensive integration makes MCP servers a powerful way to extend the Gemini CLI’s capabilities while maintaining security, reliability, and ease of use.

## Returning Rich Content from Tools [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#returning-rich-content-from-tools)

MCP tools are not limited to returning simple text. You can return rich, multi-part content, including text, images, audio, and other binary data in a single tool response. This allows you to build powerful tools that can provide diverse information to the model in a single turn.

All data returned from the tool is processed and sent to the model as context for its next generation, enabling it to reason about or summarize the provided information.

### How It Works [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#how-it-works)

To return rich content, your tool’s response must adhere to the MCP specification for a [`CallToolResult`](https://modelcontextprotocol.io/specification/2025-06-18/server/tools#tool-result). The `content` field of the result should be an array of `ContentBlock` objects. The Gemini CLI will correctly process this array, separating text from binary data and packaging it for the model.

You can mix and match different content block types in the `content` array. The supported block types include:

- `text`
- `image`
- `audio`
- `resource` (embedded content)
- `resource_link`

### Example: Returning Text and an Image [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#example-returning-text-and-an-image)

Here is an example of a valid JSON response from an MCP tool that returns both a text description and an image:

```
{
  "content": [\
    {\
      "type": "text",\
      "text": "Here is the logo you requested."\
    },\
    {\
      "type": "image",\
      "data": "BASE64_ENCODED_IMAGE_DATA_HERE",\
      "mimeType": "image/png"\
    },\
    {\
      "type": "text",\
      "text": "The logo was created in 2025."\
    }\
  ]
}

```

When the Gemini CLI receives this response, it will:

1. Extract all the text and combine it into a single `functionResponse` part for the model.
2. Present the image data as a separate `inlineData` part.
3. Provide a clean, user-friendly summary in the CLI, indicating that both text and an image were received.

This enables you to build sophisticated tools that can provide rich, multi-modal context to the Gemini model.

## MCP Prompts as Slash Commands [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#mcp-prompts-as-slash-commands)

In addition to tools, MCP servers can expose predefined prompts that can be executed as slash commands within the Gemini CLI. This allows you to create shortcuts for common or complex queries that can be easily invoked by name.

### Defining Prompts on the Server [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#defining-prompts-on-the-server)

Here’s a small example of a stdio MCP server that defines prompts:

```
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

const server = new McpServer({
  name: 'prompt-server',
  version: '1.0.0',
});

server.registerPrompt(
  'poem-writer',
  {
    title: 'Poem Writer',
    description: 'Write a nice haiku',
    argsSchema: { title: z.string(), mood: z.string().optional() },
  },
  ({ title, mood }) => ({
    messages: [\
      {\
        role: 'user',\
        content: {\
          type: 'text',\
          text: `Write a haiku${mood ? ` with the mood ${mood}` : ''} called ${title}. Note that a haiku is 5 syllables followed by 7 syllables followed by 5 syllables `,\
        },\
      },\
    ],
  }),
);

const transport = new StdioServerTransport();
await server.connect(transport);

```

This can be included in `settings.json` under `mcpServers` with:

```
{
  "mcpServers": {
    "nodeServer": {
      "command": "node",
      "args": ["filename.ts"]
    }
  }
}

```

### Invoking Prompts [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#invoking-prompts)

Once a prompt is discovered, you can invoke it using its name as a slash command. The CLI will automatically handle parsing arguments.

```
/poem-writer --title="Gemini CLI" --mood="reverent"

```

or, using positional arguments:

```
/poem-writer "Gemini CLI" reverent

```

When you run this command, the Gemini CLI executes the `prompts/get` method on the MCP server with the provided arguments. The server is responsible for substituting the arguments into the prompt template and returning the final prompt text. The CLI then sends this prompt to the model for execution. This provides a convenient way to automate and share common workflows.

## Managing MCP Servers with `gemini mcp` [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#managing-mcp-servers-with-gemini-mcp)

While you can always configure MCP servers by manually editing your `settings.json` file, the Gemini CLI provides a convenient set of commands to manage your server configurations programmatically. These commands streamline the process of adding, listing, and removing MCP servers without needing to directly edit JSON files.

### Adding a Server ( `gemini mcp add`) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#adding-a-server-gemini-mcp-add)

The `add` command configures a new MCP server in your `settings.json`. Based on the scope ( `-s, --scope`), it will be added to either the user config `~/.gemini/settings.json` or the project config `.gemini/settings.json` file.

**Command:**

```
gemini mcp add [options] <name> <commandOrUrl> [args...]

```

- `<name>`: A unique name for the server.
- `<commandOrUrl>`: The command to execute (for `stdio`) or the URL (for `http`/ `sse`).
- `[args...]`: Optional arguments for a `stdio` command.

**Options (Flags):**

- `-s, --scope`: Configuration scope (user or project). \[default: “project”\]
- `-t, --transport`: Transport type (stdio, sse, http). \[default: “stdio”\]
- `-e, --env`: Set environment variables (e.g. -e KEY=value).
- `-H, --header`: Set HTTP headers for SSE and HTTP transports (e.g. -H “X-Api-Key: abc123” -H “Authorization: Bearer abc123”).
- `--timeout`: Set connection timeout in milliseconds.
- `--trust`: Trust the server (bypass all tool call confirmation prompts).
- `--description`: Set the description for the server.
- `--include-tools`: A comma-separated list of tools to include.
- `--exclude-tools`: A comma-separated list of tools to exclude.

#### Adding an stdio server [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#adding-an-stdio-server)

This is the default transport for running local servers.

```
# Basic syntax
gemini mcp add <name> <command> [args...]

# Example: Adding a local server
gemini mcp add my-stdio-server -e API_KEY=123 /path/to/server arg1 arg2 arg3

# Example: Adding a local python server
gemini mcp add python-server python server.py --port 8080

```

#### Adding an HTTP server [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#adding-an-http-server)

This transport is for servers that use the streamable HTTP transport.

```
# Basic syntax
gemini mcp add --transport http <name> <url>

# Example: Adding an HTTP server
gemini mcp add --transport http http-server https://api.example.com/mcp/

# Example: Adding an HTTP server with an authentication header
gemini mcp add --transport http secure-http https://api.example.com/mcp/ --header "Authorization: Bearer abc123"

```

#### Adding an SSE server [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#adding-an-sse-server)

This transport is for servers that use Server-Sent Events (SSE).

```
# Basic syntax
gemini mcp add --transport sse <name> <url>

# Example: Adding an SSE server
gemini mcp add --transport sse sse-server https://api.example.com/sse/

# Example: Adding an SSE server with an authentication header
gemini mcp add --transport sse secure-sse https://api.example.com/sse/ --header "Authorization: Bearer abc123"

```

### Listing Servers ( `gemini mcp list`) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#listing-servers-gemini-mcp-list)

To view all MCP servers currently configured, use the `list` command. It displays each server’s name, configuration details, and connection status.

**Command:**

```
gemini mcp list

```

**Example Output:**

```
✓ stdio-server: command: python3 server.py (stdio) - Connected
✓ http-server: https://api.example.com/mcp (http) - Connected
✗ sse-server: https://api.example.com/sse (sse) - Disconnected

```

### Removing a Server ( `gemini mcp remove`) [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html\#removing-a-server-gemini-mcp-remove)

To delete a server from your configuration, use the `remove` command with the server’s name.

**Command:**

```
gemini mcp remove <name>

```

**Example:**

```
gemini mcp remove my-server

```

This will find and delete the “my-server” entry from the `mcpServers` object in the appropriate `settings.json` file based on the scope ( `-s, --scope`).

## Custom Commands Guide
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Custom Commands

Custom commands let you save and reuse your favorite or most frequently used prompts as personal shortcuts within Gemini CLI. You can create commands that are specific to a single project or commands that are available globally across all your projects, streamlining your workflow and ensuring consistency.

## File locations and precedence [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html\#file-locations-and-precedence)

Gemini CLI discovers commands from two locations, loaded in a specific order:

1. **User Commands (Global):** Located in `~/.gemini/commands/`. These commands are available in any project you are working on.
2. **Project Commands (Local):** Located in `<your-project-root>/.gemini/commands/`. These commands are specific to the current project and can be checked into version control to be shared with your team.

If a command in the project directory has the same name as a command in the user directory, the **project command will always be used.** This allows projects to override global commands with project-specific versions.

## Naming and namespacing [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html\#naming-and-namespacing)

The name of a command is determined by its file path relative to its `commands` directory. Subdirectories are used to create namespaced commands, with the path separator ( `/` or `\`) being converted to a colon ( `:`).

- A file at `~/.gemini/commands/test.toml` becomes the command `/test`.
- A file at `<project>/.gemini/commands/git/commit.toml` becomes the namespaced command `/git:commit`.

## TOML File Format (v1) [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html\#toml-file-format-v1)

Your command definition files must be written in the TOML format and use the `.toml` file extension.

### Required fields [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html\#required-fields)

- `prompt` (String): The prompt that will be sent to the Gemini model when the command is executed. This can be a single-line or multi-line string.

### Optional fields [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html\#optional-fields)

- `description` (String): A brief, one-line description of what the command does. This text will be displayed next to your command in the `/help` menu. **If you omit this field, a generic description will be generated from the filename.**

## Handling arguments [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html\#handling-arguments)

Custom commands support two powerful methods for handling arguments. The CLI automatically chooses the correct method based on the content of your command's `prompt`.

### 1\. Context-aware injection with \`\` [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html\#1-context-aware-injection-with-)

If your `prompt` contains the special placeholder \`\`, the CLI will replace that placeholder with the text the user typed after the command name.

The behavior of this injection depends on where it is used:

**A. Raw injection (outside Shell commands)**

When used in the main body of the prompt, the arguments are injected exactly as the user typed them.

**Example ( `git/fix.toml`):**

```
# Invoked via: /git:fix "Button is misaligned"

description = "Generates a fix for a given issue."
prompt = "Please provide a code fix for the issue described here: ."

```

The model receives: `Please provide a code fix for the issue described here: "Button is misaligned".`

**B. Using arguments in Shell commands (inside `!{...}` blocks)**

When you use \`\` inside a shell injection block ( `!{...}`), the arguments are automatically **shell-escaped** before replacement. This allows you to safely pass arguments to shell commands, ensuring the resulting command is syntactically correct and secure while preventing command injection vulnerabilities.

**Example ( `/grep-code.toml`):**

```
prompt = """
Please summarize the findings for the pattern ``.

Search Results:
!{grep -r  .}
"""

```

When you run `/grep-code It\'s complicated`:

1. The CLI sees \`\` used both outside and inside `!{...}`.
2. Outside: The first \`\` is replaced raw with `It\'s complicated`.
3. Inside: The second \`\` is replaced with the escaped version (e.g., on Linux: `"It\'s complicated"`).
4. The command executed is `grep -r "It\'s complicated" .`.
5. The CLI prompts you to confirm this exact, secure command before execution.
6. The final prompt is sent.

### 2\. Default argument handling [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html\#2-default-argument-handling)

If your `prompt` does **not** contain the special placeholder \`\`, the CLI uses a default behavior for handling arguments.

If you provide arguments to the command (e.g., `/mycommand arg1`), the CLI will append the full command you typed to the end of the prompt, separated by two newlines. This allows the model to see both the original instructions and the specific arguments you just provided.

If you do **not** provide any arguments (e.g., `/mycommand`), the prompt is sent to the model exactly as it is, with nothing appended.

**Example ( `changelog.toml`):**

This example shows how to create a robust command by defining a role for the model, explaining where to find the user’s input, and specifying the expected format and behavior.

```
# In: <project>/.gemini/commands/changelog.toml
# Invoked via: /changelog 1.2.0 added "Support for default argument parsing."

description = "Adds a new entry to the project\'s CHANGELOG.md file."
prompt = """
# Task: Update Changelog

You are an expert maintainer of this software project. A user has invoked a command to add a new entry to the changelog.

**The user\'s raw command is appended below your instructions.**

Your task is to parse the `<version>`, `<change_type>`, and `<message>` from their input and use the `write_file` tool to correctly update the `CHANGELOG.md` file.

## Expected Format
The command follows this format: `/changelog <version> <type> <message>`
- `<type>` must be one of: "added", "changed", "fixed", "removed".

## Behavior
1. Read the `CHANGELOG.md` file.
2. Find the section for the specified `<version>`.
3. Add the `<message>` under the correct `<type>` heading.
4. If the version or type section doesn\'t exist, create it.
5. Adhere strictly to the "Keep a Changelog" format.
"""

```

When you run `/changelog 1.2.0 added "New feature"`, the final text sent to the model will be the original prompt followed by two newlines and the command you typed.

### 3\. Executing Shell commands with `!{...}` [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html\#3-executing-shell-commands-with-)

You can make your commands dynamic by executing shell commands directly within your `prompt` and injecting their output. This is ideal for gathering context from your local environment, like reading file content or checking the status of Git.

When a custom command attempts to execute a shell command, Gemini CLI will now prompt you for confirmation before proceeding. This is a security measure to ensure that only intended commands can be run.

**How it works:**

1. **Inject commands:** Use the `!{...}` syntax.
2. **Argument substitution:** If \`\` is present inside the block, it is automatically shell-escaped (see [Context-Aware Injection](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html#1-context-aware-injection-with-args) above).
3. **Robust parsing:** The parser correctly handles complex shell commands that include nested braces, such as JSON payloads. **Note:** The content inside `!{...}` must have balanced braces ( `{` and `}`). If you need to execute a command containing unbalanced braces, consider wrapping it in an external script file and calling the script within the `!{...}` block.
4. **Security check and confirmation:** The CLI performs a security check on the final, resolved command (after arguments are escaped and substituted). A dialog will appear showing the exact command(s) to be executed.
5. **Execution and error reporting:** The command is executed. If the command fails, the output injected into the prompt will include the error messages (stderr) followed by a status line, e.g., `[Shell command exited with code 1]`. This helps the model understand the context of the failure.

**Example ( `git/commit.toml`):**

This command gets the staged git diff and uses it to ask the model to write a commit message.

````
# In: <project>/.gemini/commands/git/commit.toml
# Invoked via: /git:commit

description = "Generates a Git commit message based on staged changes."

# The prompt uses !{...} to execute the command and inject its output.
prompt = """
Please generate a Conventional Commit message based on the following git diff:

```diff
!{git diff --staged}
```

"""

````

When you run `/git:commit`, the CLI first executes `git diff --staged`, then replaces `!{git diff --staged}` with the output of that command before sending the final, complete prompt to the model.

### 4\. Injecting file content with `@{...}` [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html\#4-injecting-file-content-with-)

You can directly embed the content of a file or a directory listing into your prompt using the `@{...}` syntax. This is useful for creating commands that operate on specific files.

**How it works:**

- **File injection**: `@{path/to/file.txt}` is replaced by the content of `file.txt`.
- **Multimodal support**: If the path points to a supported image (e.g., PNG, JPEG), PDF, audio, or video file, it will be correctly encoded and injected as multimodal input. Other binary files are handled gracefully and skipped.
- **Directory listing**: `@{path/to/dir}` is traversed and each file present within the directory and all subdirectories is inserted into the prompt. This respects `.gitignore` and `.geminiignore` if enabled.
- **Workspace-aware**: The command searches for the path in the current directory and any other workspace directories. Absolute paths are allowed if they are within the workspace.
- **Processing order**: File content injection with `@{...}` is processed _before_ shell commands ( `!{...}`) and argument substitution (\`\`).
- **Parsing**: The parser requires the content inside `@{...}` (the path) to have balanced braces ( `{` and `}`).

**Example ( `review.toml`):**

This command injects the content of a _fixed_ best practices file ( `docs/best-practices.md`) and uses the user's arguments to provide context for the review.

```
# In: <project>/.gemini/commands/review.toml
# Invoked via: /review FileCommandLoader.ts

description = "Reviews the provided context using a best practice guide."
prompt = """
You are an expert code reviewer.

Your task is to review .

Use the following best practices when providing your review:

@{docs/best-practices.md}
"""

```

When you run `/review FileCommandLoader.ts`, the `@{docs/best-practices.md}` placeholder is replaced by the content of that file, and \`\` is replaced by the text you provided, before the final prompt is sent to the model.

* * *

## Example: A “Pure Function” refactoring command [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html\#example-a-pure-function-refactoring-command)

Let’s create a global command that asks the model to refactor a piece of code.

**1\. Create the file and directories:**

First, ensure the user commands directory exists, then create a `refactor` subdirectory for organization and the final TOML file.

```
mkdir -p ~/.gemini/commands/refactor
touch ~/.gemini/commands/refactor/pure.toml

```

**2\. Add the content to the file:**

Open `~/.gemini/commands/refactor/pure.toml` in your editor and add the following content. We are including the optional `description` for best practice.

```
# In: ~/.gemini/commands/refactor/pure.toml
# This command will be invoked via: /refactor:pure

description = "Asks the model to refactor the current context into a pure function."

prompt = """
Please analyze the code I\'ve provided in the current context.
Refactor it into a pure function.

Your response should include:
1. The refactored, pure function code block.
2. A brief explanation of the key changes you made and why they contribute to purity.
"""

```

**3\. Run the Command:**

That’s it! You can now run your command in the CLI. First, you might add a file to the context, and then invoke your command:

```
> @my-messy-function.js
> /refactor:pure

```

Gemini CLI will then execute the multi-line prompt defined in your TOML file.

## Multi File Read Tool
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Multi File Read Tool ( `read_many_files`)

This document describes the `read_many_files` tool for the Gemini CLI.

## Description [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/multi-file.html\#description)

Use `read_many_files` to read content from multiple files specified by paths or glob patterns. The behavior of this tool depends on the provided files:

- For text files, this tool concatenates their content into a single string.
- For image (e.g., PNG, JPEG), PDF, audio (MP3, WAV), and video (MP4, MOV) files, it reads and returns them as base64-encoded data, provided they are explicitly requested by name or extension.

`read_many_files` can be used to perform tasks such as getting an overview of a codebase, finding where specific functionality is implemented, reviewing documentation, or gathering context from multiple configuration files.

**Note:** `read_many_files` looks for files following the provided paths or glob patterns. A directory path such as `"/docs"` will return an empty result; the tool requires a pattern such as `"/docs/*"` or `"/docs/*.md"` to identify the relevant files.

### Arguments [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/multi-file.html\#arguments)

`read_many_files` takes the following arguments:

- `paths` (list\[string\], required): An array of glob patterns or paths relative to the tool’s target directory (e.g., `["src/**/*.ts"]`, `["README.md", "docs/*", "assets/logo.png"]`).
- `exclude` (list\[string\], optional): Glob patterns for files/directories to exclude (e.g., `["**/*.log", "temp/"]`). These are added to default excludes if `useDefaultExcludes` is true.
- `include` (list\[string\], optional): Additional glob patterns to include. These are merged with `paths` (e.g., `["*.test.ts"]` to specifically add test files if they were broadly excluded, or `["images/*.jpg"]` to include specific image types).
- `recursive` (boolean, optional): Whether to search recursively. This is primarily controlled by `**` in glob patterns. Defaults to `true`.
- `useDefaultExcludes` (boolean, optional): Whether to apply a list of default exclusion patterns (e.g., `node_modules`, `.git`, non image/pdf binary files). Defaults to `true`.
- `respect_git_ignore` (boolean, optional): Whether to respect .gitignore patterns when finding files. Defaults to true.

## How to use `read_many_files` with the Gemini CLI [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/multi-file.html\#how-to-use-read_many_files-with-the-gemini-cli)

`read_many_files` searches for files matching the provided `paths` and `include` patterns, while respecting `exclude` patterns and default excludes (if enabled).

- For text files: it reads the content of each matched file (attempting to skip binary files not explicitly requested as image/PDF) and concatenates it into a single string, with a separator `--- {filePath} ---` between the content of each file. Uses UTF-8 encoding by default.
- The tool inserts a `--- End of content ---` after the last file.
- For image and PDF files: if explicitly requested by name or extension (e.g., `paths: ["logo.png"]` or `include: ["*.pdf"]`), the tool reads the file and returns its content as a base64 encoded string.
- The tool attempts to detect and skip other binary files (those not matching common image/PDF types or not explicitly requested) by checking for null bytes in their initial content.

Usage:

```
read_many_files(paths=["Your files or paths here."], include=["Additional files to include."], exclude=["Files to exclude."], recursive=False, useDefaultExcludes=false, respect_git_ignore=true)

```

## `read_many_files` examples [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/multi-file.html\#read_many_files-examples)

Read all TypeScript files in the `src` directory:

```
read_many_files(paths=["src/**/*.ts"])

```

Read the main README, all Markdown files in the `docs` directory, and a specific logo image, excluding a specific file:

```
read_many_files(paths=["README.md", "docs/**/*.md", "assets/logo.png"], exclude=["docs/OLD_README.md"])

```

Read all JavaScript files but explicitly include test files and all JPEGs in an `images` folder:

```
read_many_files(paths=["**/*.js"], include=["**/*.test.js", "images/**/*.jpg"], useDefaultExcludes=False)

```

## Important notes [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/multi-file.html\#important-notes)

- **Binary file handling:**
  - **Image/PDF/Audio/Video files:** The tool can read common image types (PNG, JPEG, etc.), PDF, audio (mp3, wav), and video (mp4, mov) files, returning them as base64 encoded data. These files _must_ be explicitly targeted by the `paths` or `include` patterns (e.g., by specifying the exact filename like `video.mp4` or a pattern like `*.mov`).
  - **Other binary files:** The tool attempts to detect and skip other types of binary files by examining their initial content for null bytes. The tool excludes these files from its output.
- **Performance:** Reading a very large number of files or very large individual files can be resource-intensive.
- **Path specificity:** Ensure paths and glob patterns are correctly specified relative to the tool’s target directory. For image/PDF files, ensure the patterns are specific enough to include them.
- **Default excludes:** Be aware of the default exclusion patterns (like `node_modules`, `.git`) and use `useDefaultExcludes=False` if you need to override them, but do so cautiously.

## Gemini CLI Keyboard Shortcuts
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Gemini CLI Keyboard Shortcuts

This document lists the available keyboard shortcuts in the Gemini CLI.

## General [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/keyboard-shortcuts.html\#general)

| Shortcut | Description |
| --- | --- |
| `Esc` | Close dialogs and suggestions. |
| `Ctrl+C` | Cancel the ongoing request and clear the input. Press twice to exit the application. |
| `Ctrl+D` | Exit the application if the input is empty. Press twice to confirm. |
| `Ctrl+L` | Clear the screen. |
| `Ctrl+O` | Toggle the display of the debug console. |
| `Ctrl+S` | Allows long responses to print fully, disabling truncation. Use your terminal’s scrollback to view the entire output. |
| `Ctrl+T` | Toggle the display of tool descriptions. |
| `Ctrl+Y` | Toggle auto-approval (YOLO mode) for all tool calls. |

## Input Prompt [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/keyboard-shortcuts.html\#input-prompt)

| Shortcut | Description |
| --- | --- |
| `!` | Toggle shell mode when the input is empty. |
| `\` (at end of line) + `Enter` | Insert a newline. |
| `Down Arrow` | Navigate down through the input history. |
| `Enter` | Submit the current prompt. |
| `Meta+Delete` / `Ctrl+Delete` | Delete the word to the right of the cursor. |
| `Tab` | Autocomplete the current suggestion if one exists. |
| `Up Arrow` | Navigate up through the input history. |
| `Ctrl+A` / `Home` | Move the cursor to the beginning of the line. |
| `Ctrl+B` / `Left Arrow` | Move the cursor one character to the left. |
| `Ctrl+C` | Clear the input prompt |
| `Esc` (double press) | Clear the input prompt. |
| `Ctrl+D` / `Delete` | Delete the character to the right of the cursor. |
| `Ctrl+E` / `End` | Move the cursor to the end of the line. |
| `Ctrl+F` / `Right Arrow` | Move the cursor one character to the right. |
| `Ctrl+H` / `Backspace` | Delete the character to the left of the cursor. |
| `Ctrl+K` | Delete from the cursor to the end of the line. |
| `Ctrl+Left Arrow` / `Meta+Left Arrow` / `Meta+B` | Move the cursor one word to the left. |
| `Ctrl+N` | Navigate down through the input history. |
| `Ctrl+P` | Navigate up through the input history. |
| `Ctrl+Right Arrow` / `Meta+Right Arrow` / `Meta+F` | Move the cursor one word to the right. |
| `Ctrl+U` | Delete from the cursor to the beginning of the line. |
| `Ctrl+V` | Paste clipboard content. If the clipboard contains an image, it will be saved and a reference to it will be inserted in the prompt. |
| `Ctrl+W` / `Meta+Backspace` / `Ctrl+Backspace` | Delete the word to the left of the cursor. |
| `Ctrl+X` / `Meta+Enter` | Open the current input in an external editor. |

## Suggestions [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/keyboard-shortcuts.html\#suggestions)

| Shortcut | Description |
| --- | --- |
| `Down Arrow` | Navigate down through the suggestions. |
| `Tab` / `Enter` | Accept the selected suggestion. |
| `Up Arrow` | Navigate up through the suggestions. |

## Radio Button Select [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/keyboard-shortcuts.html\#radio-button-select)

| Shortcut | Description |
| --- | --- |
| `Down Arrow` / `j` | Move selection down. |
| `Enter` | Confirm selection. |
| `Up Arrow` / `k` | Move selection up. |
| `1-9` | Select an item by its number. |
| (multi-digit) | For items with numbers greater than 9, press the digits in quick succession to select the corresponding item. |

## IDE Integration [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/keyboard-shortcuts.html\#ide-integration)

| Shortcut | Description |
| --- | --- |
| `Ctrl+G` | See context CLI received from IDE |

## Gemini CLI Uninstall Guide
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Uninstalling the CLI

Your uninstall method depends on how you ran the CLI. Follow the instructions for either npx or a global npm installation.

## Method 1: Using npx [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/uninstall.html\#method-1-using-npx)

npx runs packages from a temporary cache without a permanent installation. To “uninstall” the CLI, you must clear this cache, which will remove gemini-cli and any other packages previously executed with npx.

The npx cache is a directory named `_npx` inside your main npm cache folder. You can find your npm cache path by running `npm config get cache`.

**For macOS / Linux**

```
# The path is typically ~/.npm/_npx
rm -rf "$(npm config get cache)/_npx"

```

**For Windows**

_Command Prompt_

```cmd
:: The path is typically %LocalAppData%\npm-cache\_npx
rmdir /s /q "%LocalAppData%\npm-cache\_npx"

```

_PowerShell_

```
# The path is typically $env:LocalAppData\npm-cache\_npx
Remove-Item -Path (Join-Path $env:LocalAppData "npm-cache\_npx") -Recurse -Force

```

## Method 2: Using npm (Global Install) [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/uninstall.html\#method-2-using-npm-global-install)

If you installed the CLI globally (e.g., `npm install -g @google/gemini-cli`), use the `npm uninstall` command with the `-g` flag to remove it.

```
npm uninstall -g @google/gemini-cli

```

This command completely removes the package from your system.

## Trusted Folders Security
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Trusted Folders

The Trusted Folders feature is a security setting that gives you control over which projects can use the full capabilities of the Gemini CLI. It prevents potentially malicious code from running by asking you to approve a folder before the CLI loads any project-specific configurations from it.

## Enabling the Feature [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/trusted-folders.html\#enabling-the-feature)

The Trusted Folders feature is **disabled by default**. To use it, you must first enable it in your settings.

Add the following to your user `settings.json` file:

```
{
  "security": {
    "folderTrust": {
      "enabled": true
    }
  }
}

```

## How It Works: The Trust Dialog [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/trusted-folders.html\#how-it-works-the-trust-dialog)

Once the feature is enabled, the first time you run the Gemini CLI from a folder, a dialog will automatically appear, prompting you to make a choice:

- **Trust folder**: Grants full trust to the current folder (e.g., `my-project`).
- **Trust parent folder**: Grants trust to the parent directory (e.g., `safe-projects`), which automatically trusts all of its subdirectories as well. This is useful if you keep all your safe projects in one place.
- **Don’t trust**: Marks the folder as untrusted. The CLI will operate in a restricted “safe mode.”

Your choice is saved in a central file ( `~/.gemini/trustedFolders.json`), so you will only be asked once per folder.

## Why Trust Matters: The Impact of an Untrusted Workspace [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/trusted-folders.html\#why-trust-matters-the-impact-of-an-untrusted-workspace)

When a folder is **untrusted**, the Gemini CLI runs in a restricted “safe mode” to protect you. In this mode, the following features are disabled:

1. **Workspace Settings are Ignored**: The CLI will **not** load the `.gemini/settings.json` file from the project. This prevents the loading of custom tools and other potentially dangerous configurations.

2. **Environment Variables are Ignored**: The CLI will **not** load any `.env` files from the project.

3. **Extension Management is Restricted**: You **cannot install, update, or uninstall** extensions.

4. **Tool Auto-Acceptance is Disabled**: You will always be prompted before any tool is run, even if you have auto-acceptance enabled globally.

5. **Automatic Memory Loading is Disabled**: The CLI will not automatically load files into context from directories specified in local settings.


Granting trust to a folder unlocks the full functionality of the Gemini CLI for that workspace.

## Managing Your Trust Settings [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/trusted-folders.html\#managing-your-trust-settings)

If you need to change a decision or see all your settings, you have a couple of options:

- **Change the Current Folder’s Trust**: Run the `/permissions` command from within the CLI. This will bring up the same interactive dialog, allowing you to change the trust level for the current folder.

- **View All Trust Rules**: To see a complete list of all your trusted and untrusted folder rules, you can inspect the contents of the `~/.gemini/trustedFolders.json` file in your home directory.


## The Trust Check Process (Advanced) [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/trusted-folders.html\#the-trust-check-process-advanced)

For advanced users, it’s helpful to know the exact order of operations for how trust is determined:

1. **IDE Trust Signal**: If you are using the [IDE Integration](https://google-gemini.github.io/gemini-cli/docs/ide-integration/), the CLI first asks the IDE if the workspace is trusted. The IDE’s response takes highest priority.

2. **Local Trust File**: If the IDE is not connected, the CLI checks the central `~/.gemini/trustedFolders.json` file.

## GEMINI.md Context Files
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Provide Context with GEMINI.md Files

Context files, which use the default name `GEMINI.md`, are a powerful feature for providing instructional context to the Gemini model. You can use these files to give project-specific instructions, define a persona, or provide coding style guides to make the AI’s responses more accurate and tailored to your needs.

Instead of repeating instructions in every prompt, you can define them once in a context file.

## Understand the context hierarchy [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html\#understand-the-context-hierarchy)

The CLI uses a hierarchical system to source context. It loads various context files from several locations, concatenates the contents of all found files, and sends them to the model with every prompt. The CLI loads files in the following order:

1. **Global context file:**
   - **Location:** `~/.gemini/GEMINI.md` (in your user home directory).
   - **Scope:** Provides default instructions for all your projects.
2. **Project root and ancestor context files:**
   - **Location:** The CLI searches for a `GEMINI.md` file in your current working directory and then in each parent directory up to the project root (identified by a `.git` folder).
   - **Scope:** Provides context relevant to the entire project.
3. **Sub-directory context files:**
   - **Location:** The CLI also scans for `GEMINI.md` files in subdirectories below your current working directory. It respects rules in `.gitignore` and `.geminiignore`.
   - **Scope:** Lets you write highly specific instructions for a particular component or module.

The CLI footer displays the number of loaded context files, which gives you a quick visual cue of the active instructional context.

### Example `GEMINI.md` file [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html\#example-geminimd-file)

Here is an example of what you can include in a `GEMINI.md` file at the root of a TypeScript project:

```
# Project: My TypeScript Library

## General Instructions

- When you generate new TypeScript code, follow the existing coding style.
- Ensure all new functions and classes have JSDoc comments.
- Prefer functional programming paradigms where appropriate.

## Coding Style

- Use 2 spaces for indentation.
- Prefix interface names with `I` (for example, `IUserService`).
- Always use strict equality (`===` and `!==`).

```

## Manage context with the `/memory` command [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html\#manage-context-with-the-memory-command)

You can interact with the loaded context files by using the `/memory` command.

- **`/memory show`**: Displays the full, concatenated content of the current hierarchical memory. This lets you inspect the exact instructional context being provided to the model.
- **`/memory refresh`**: Forces a re-scan and reload of all `GEMINI.md` files from all configured locations.
- **`/memory add <text>`**: Appends your text to your global `~/.gemini/GEMINI.md` file. This lets you add persistent memories on the fly.

## Modularize context with imports [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html\#modularize-context-with-imports)

You can break down large `GEMINI.md` files into smaller, more manageable components by importing content from other files using the `@file.md` syntax. This feature supports both relative and absolute paths.

**Example `GEMINI.md` with imports:**

```
# Main GEMINI.md file

This is the main content.

@./components/instructions.md

More content here.

@../shared/style-guide.md

```

For more details, see the [Memory Import Processor](https://google-gemini.github.io/gemini-cli/docs/core/memport.html) documentation.

## Customize the context file name [Anchor](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html\#customize-the-context-file-name)

While `GEMINI.md` is the default filename, you can configure this in your `settings.json` file. To specify a different name or a list of names, use the `context.fileName` property.

**Example `settings.json`:**

```
{
  "context": {
    "fileName": ["AGENTS.md", "CONTEXT.md", "GEMINI.md"]
  }
}

```

## Web Fetch Tool Documentation
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Web Fetch Tool ( `web_fetch`)

This document describes the `web_fetch` tool for the Gemini CLI.

## Description [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/web-fetch.html\#description)

Use `web_fetch` to summarize, compare, or extract information from web pages. The `web_fetch` tool processes content from one or more URLs (up to 20) embedded in a prompt. `web_fetch` takes a natural language prompt and returns a generated response.

### Arguments [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/web-fetch.html\#arguments)

`web_fetch` takes one argument:

- `prompt` (string, required): A comprehensive prompt that includes the URL(s) (up to 20) to fetch and specific instructions on how to process their content. For example: `"Summarize https://example.com/article and extract key points from https://another.com/data"`. The prompt must contain at least one URL starting with `http://` or `https://`.

## How to use `web_fetch` with the Gemini CLI [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/web-fetch.html\#how-to-use-web_fetch-with-the-gemini-cli)

To use `web_fetch` with the Gemini CLI, provide a natural language prompt that contains URLs. The tool will ask for confirmation before fetching any URLs. Once confirmed, the tool will process URLs through Gemini API’s `urlContext`.

If the Gemini API cannot access the URL, the tool will fall back to fetching content directly from the local machine. The tool will format the response, including source attribution and citations where possible. The tool will then provide the response to the user.

Usage:

```
web_fetch(prompt="Your prompt, including a URL such as https://google.com.")

```

## `web_fetch` examples [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/web-fetch.html\#web_fetch-examples)

Summarize a single article:

```
web_fetch(prompt="Can you summarize the main points of https://example.com/news/latest")

```

Compare two articles:

```
web_fetch(prompt="What are the differences in the conclusions of these two papers: https://arxiv.org/abs/2401.0001 and https://arxiv.org/abs/2401.0002?")

```

## Important notes [Anchor](https://google-gemini.github.io/gemini-cli/docs/tools/web-fetch.html\#important-notes)

- **URL processing:** `web_fetch` relies on the Gemini API’s ability to access and process the given URLs.
- **Output quality:** The quality of the output will depend on the clarity of the instructions in the prompt.

## Token Caching Cost Optimization
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Token Caching and Cost Optimization

Gemini CLI automatically optimizes API costs through token caching when using API key authentication (Gemini API key or Vertex AI). This feature reuses previous system instructions and context to reduce the number of tokens processed in subsequent requests.

**Token caching is available for:**

- API key users (Gemini API key)
- Vertex AI users (with project and location setup)

**Token caching is not available for:**

- OAuth users (Google Personal/Enterprise accounts) - the Code Assist API does not support cached content creation at this time

You can view your token usage and cached token savings using the `/stats` command. When cached tokens are available, they will be displayed in the stats output.

## Gemini CLI Authentication Setup
# [gemini-cli](https://google-gemini.github.io/gemini-cli/)

# Authentication Setup

See: [Getting Started - Authentication Setup](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html).

