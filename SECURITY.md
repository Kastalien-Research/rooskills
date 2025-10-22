# Security Guide

This document outlines the security measures implemented in the rooskills project and best practices for secure usage.

## Overview

The rooskills project has been hardened against common security vulnerabilities including:
- Command injection attacks
- Path traversal attacks
- Input validation failures
- Unprotected environment variables
- Unsafe file operations

## Security Features

### 1. Input Validation & Sanitization

All user inputs are validated and sanitized before processing:

- **URL Validation**: Only `http://` and `https://` protocols allowed
- **Skill Name Validation**: Alphanumeric characters, hyphens, and underscores only
- **Path Validation**: Prevents path traversal attacks (`../`, `~`, etc.)
- **Parameter Validation**: Type checking, length limits, and format validation

**Files:**
- `cli/utils/security.js` - JavaScript validation functions
- `scripts/feynman-batch-sdk/src/validators.ts` - TypeScript validation functions

### 2. Command Injection Prevention

**Before (Vulnerable):**
```javascript
execSync(`"${scriptPath}" ${args.join(' ')}`);  // ❌ Shell injection possible
```

**After (Secure):**
```javascript
execFileSync(scriptPath, args, options);  // ✅ No shell interpretation
```

All command execution now uses `execFile` or `spawn` with array arguments, preventing shell interpretation.

**Fixed Files:**
- `cli/commands/generate.js`
- `cli/commands/init.js`
- `scripts/feynman-batch-sdk/src/tool-integration.ts`

### 3. Environment Variable Validation

Required environment variables are validated on startup:

```javascript
const { validateConfig } = require('./cli/utils/config-validator');

// Validates all required env vars with proper error messages
const config = validateConfig();
```

**Features:**
- Required field checking
- Type validation (string, number, boolean)
- Format validation (API key patterns, URL formats)
- Helpful error messages with troubleshooting tips

**File:** `cli/utils/config-validator.js`

### 4. Secure File Operations

File operations now include:
- Path validation to prevent traversal attacks
- Atomic writes (write to temp, then rename)
- Proper error handling
- Permission checking

**Fixed File:** `cli/commands/init.js`

### 5. API Security

- **Timeouts**: All API calls have configurable timeouts (default: 30s)
- **Retry Logic**: Exponential backoff with configurable max retries
- **Error Handling**: Safe error messages that don't expose sensitive data

**Fixed Files:**
- `scripts/sync-orchestrator/thoughtbox_client.py`

## Security Best Practices

### For Users

1. **Protect API Keys**
   ```bash
   # Never commit .env file
   echo ".env" >> .gitignore
   
   # Use strong, unique API keys
   # Rotate keys regularly
   ```

2. **Validate Input Sources**
   ```bash
   # Only generate skills from trusted documentation URLs
   rooskills generate https://trusted-source.com/docs
   ```

3. **Review Generated Code**
   ```bash
   # Always review generated skills before using them
   # Check for unexpected code or behavior
   ```

4. **Keep Dependencies Updated**
   ```bash
   npm update
   pip install --upgrade -r requirements.txt
   ```

### For Developers

1. **Use Validation Functions**
   ```javascript
   const { validateURL, validateSkillName } = require('./cli/utils/security');
   
   // Always validate user input
   const safeUrl = validateURL(userInput);
   ```

2. **Never Use Shell Execution**
   ```javascript
   // ❌ WRONG
   exec(`command ${userInput}`);
   
   // ✅ CORRECT
   execFile('command', [userInput], options);
   ```

3. **Validate File Paths**
   ```javascript
   const { validatePath } = require('./cli/utils/security');
   
   // Prevent path traversal
   const safePath = validatePath(userInput, baseDir);
   ```

4. **Handle Errors Safely**
   ```javascript
   try {
     // risky operation
   } catch (error) {
     // Don't expose internal details in production
     const safeMessage = createSafeErrorMessage(error);
     console.error(safeMessage);
   }
   ```

## Configuration

### Required Environment Variables

```bash
# REQUIRED
FIRECRAWL_API_KEY=fc_your_key_here
ANTHROPIC_API_KEY=sk-ant-your_key_here

# OPTIONAL
EXA_API_KEY=your_exa_key_here
LOG_LEVEL=info
TIMEOUT_MS=30000
MAX_RETRIES=3
```

### Security Constants

Located in `scripts/feynman-batch-sdk/src/constants.ts`:

```typescript
// Configurable security limits
export const MAX_COMMAND_NAME_LENGTH = 50;
export const MAX_URL_LENGTH = 2048;
export const MAX_BATCH_SIZE = 100;
export const DEFAULT_COMMAND_TIMEOUT_MS = 30000;
```

## Threat Model

### Protected Against

✅ **Command Injection**: All command execution sanitized  
✅ **Path Traversal**: All file paths validated  
✅ **SQL Injection**: N/A (no database)  
✅ **XSS**: N/A (CLI tool)  
✅ **Environment Variable Exposure**: Validated and hidden in logs  
✅ **Denial of Service**: Timeouts and rate limiting implemented  

### Not Protected Against

⚠️ **Malicious Documentation Sources**: Users must trust URLs they provide  
⚠️ **Supply Chain Attacks**: Dependencies should be audited regularly  
⚠️ **Social Engineering**: Users must verify instructions and generated code  

## Reporting Security Issues

If you discover a security vulnerability, please email: [security contact needed]

**Please do NOT:**
- Open a public GitHub issue
- Disclose the vulnerability publicly before it's fixed

**Please DO:**
- Provide detailed steps to reproduce
- Include potential impact assessment
- Suggest a fix if possible

## Security Checklist

Use this checklist when contributing code:

- [ ] All user inputs validated
- [ ] No shell command execution with string interpolation
- [ ] File paths validated to prevent traversal
- [ ] API calls have timeouts
- [ ] Errors don't expose sensitive information
- [ ] Environment variables validated
- [ ] No hardcoded credentials
- [ ] Dependencies are up to date
- [ ] New code follows security patterns in this guide

## Audit Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-01-22 | 1.2.1 | Initial security hardening |
| | | - Added input validation framework |
| | | - Fixed command injection vulnerabilities |
| | | - Implemented environment variable validation |
| | | - Added secure file operation patterns |
| | | - Implemented API timeouts |

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)
- [Python Security Guidelines](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)

## License

This security guide is part of the rooskills project and follows the same license.

---

**Last Updated:** January 22, 2025  
**Maintainers:** Rooskills Security Team
