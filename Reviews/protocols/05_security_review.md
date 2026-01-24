# PROTOCOL 05: Security Review
**Role:** Code Review Coordinator
**Extends:** 00_review_core.md

**Purpose:** Conduct a security-focused audit of the codebase to identify vulnerabilities, security weaknesses, and areas where security best practices are not followed.

---

## Overview

The Security Review focuses specifically on finding security vulnerabilities and weaknesses. While other reviews may touch on security, this review makes it the primary focus with specialized agents trained to think like attackers.

**Best For:**
- Pre-release security assessments
- After security incidents (to find similar issues)
- Code handling sensitive data
- Public-facing APIs and interfaces
- Authentication/authorization code
- Compliance requirements

---

## Default Agent Configuration

### Required Agents
| Agent | Focus |
|-------|-------|
| Security Auditor | Primary security analysis - OWASP Top 10, common vulnerabilities |
| Input Validation Analyst | Input sanitization, boundary checks, injection points |
| Auth/Access Reviewer | Authentication, authorization, permissions, session management |

### Recommended Agents
| Agent | Focus |
|-------|-------|
| Data Flow Tracer | How sensitive data moves through the system |
| Error Handling Auditor | Information leakage via errors, exception handling |

### Optional Agents
| Agent | Focus | Include When |
|-------|-------|--------------|
| Code Quality Analyst | Security-relevant code quality | Large codebase |
| Architecture Reviewer | Security architecture patterns | System-wide review |
| Module Specialist (x N) | Deep dive on security-critical modules | Complex systems |

### Typical Agent Count: 5-8

---

## Phase A: Scope Definition (Extended)

### Questions to Ask User

Use AskUserQuestion with these options:

1. **Review Scope**
   - Entire codebase
   - Specific attack surface (API, user input, file handling)
   - Specific module/feature
   - Authentication/authorization only

2. **Security Priorities**
   - Injection vulnerabilities (SQL, command, XSS)
   - Authentication & session management
   - Authorization & access control
   - Sensitive data exposure
   - Input validation
   - Error handling & logging
   - All of the above

3. **Known Sensitive Areas**
   - Where is authentication handled?
   - Where is sensitive data processed?
   - What external APIs are called?
   - Where is user input accepted?

4. **Threat Model Context**
   - Who are the potential attackers? (external users, internal users, etc.)
   - What are the crown jewels? (most sensitive data/functionality)
   - Any compliance requirements? (GDPR, PCI-DSS, etc.)

5. **Previous Security Work**
   - Previous security audits?
   - Known vulnerabilities addressed?
   - Security tools in use?

---

## Phase B: Agent Planning (Extended)

### Scaling Guidelines for Security Review

| Scope | Recommended Configuration |
|-------|--------------------------|
| Targeted (specific feature) | 5 agents: Core 3 + DFT + ERR |
| Module-level | 6-7 agents: Core 3 + DFT + ERR + CQ |
| System-wide | 7-8 agents: All recommended + Architecture |
| Comprehensive | 8+ agents: Add Module Specialists for critical areas |

### Security-Critical Module Identification
Prioritize modules that:
- Handle authentication/authorization
- Process user input
- Store/transmit sensitive data
- Interface with external systems
- Handle file operations
- Execute system commands

---

## Phase C: Review Swarm Launch (Extended)

### Agent-Specific Instructions

#### Security Auditor (Primary)
```markdown
# Security Audit Task

## Scope
{SCOPE_FROM_PHASE_A}

## Primary Focus: OWASP Top 10 & Common Vulnerabilities

### 1. Injection (SQL, Command, LDAP, XPath, etc.)
Look for:
- String concatenation in queries/commands
- Unparameterized database queries
- System command execution with user input
- Template injection possibilities

### 2. Broken Authentication
Look for:
- Weak password policies
- Credential storage issues
- Session fixation vulnerabilities
- Missing brute-force protection

### 3. Sensitive Data Exposure
Look for:
- Hardcoded credentials/secrets
- Sensitive data in logs
- Unencrypted storage of sensitive data
- Sensitive data in URLs

### 4. XML External Entities (XXE)
Look for:
- XML parsing without disabling external entities
- Unsafe XML configuration

### 5. Broken Access Control
Look for:
- Missing authorization checks
- Insecure direct object references
- Path traversal vulnerabilities
- Privilege escalation possibilities

### 6. Security Misconfiguration
Look for:
- Debug mode in production paths
- Default credentials
- Unnecessary features enabled
- Missing security headers

### 7. Cross-Site Scripting (XSS)
Look for:
- Unsanitized output rendering
- DOM-based XSS
- Stored XSS possibilities

### 8. Insecure Deserialization
Look for:
- Pickle/marshal usage with untrusted data
- JSON deserialization to arbitrary objects

### 9. Using Components with Known Vulnerabilities
Look for:
- Outdated dependencies
- Known vulnerable patterns

### 10. Insufficient Logging & Monitoring
Look for:
- Missing security event logging
- Sensitive data in logs
- No audit trails for security events

## Severity Rating
- CRITICAL: Directly exploitable, high impact
- HIGH: Exploitable with some effort, significant impact
- MEDIUM: Requires specific conditions, moderate impact
- LOW: Difficult to exploit, limited impact
- INFO: Best practice recommendations
```

#### Input Validation Analyst
```markdown
# Input Validation Analysis

## Focus Areas

### 1. Entry Points
- Identify all input entry points
- User input, API parameters, file uploads, environment variables

### 2. Validation Presence
For each entry point:
- Is input validated?
- What validation is performed?
- Is it sufficient?

### 3. Validation Bypass
- Can validation be bypassed?
- Type confusion possibilities?
- Encoding bypass possibilities?

### 4. Boundary Checks
- Buffer/array bounds checking
- Integer overflow/underflow
- Length limits enforced?

### 5. Sanitization
- Is output sanitized appropriately?
- Context-aware sanitization?
- Proper encoding for output context?

## Report Each Finding:
- Entry point location
- What input is accepted
- What validation exists (or doesn't)
- Potential attack vector
- Recommended fix
```

#### Auth/Access Reviewer
```markdown
# Authentication & Authorization Analysis

## Authentication Review

### 1. Credential Handling
- How are credentials stored?
- Password hashing algorithm and parameters
- Credential transmission security

### 2. Session Management
- Session token generation (randomness)
- Session storage and transmission
- Session expiration and invalidation
- Session fixation prevention

### 3. Authentication Flow
- Login process security
- Logout completeness
- Password reset process
- Multi-factor authentication (if applicable)

### 4. Brute Force Protection
- Rate limiting
- Account lockout
- CAPTCHA usage

## Authorization Review

### 1. Access Control Model
- What model is used? (RBAC, ABAC, etc.)
- Is it consistently applied?

### 2. Authorization Checks
- Are all sensitive operations protected?
- Are checks performed server-side?
- Horizontal access control (user A accessing user B's data)
- Vertical access control (privilege escalation)

### 3. Default Deny
- Is access denied by default?
- Are there permissive defaults?

### 4. Indirect References
- Are object IDs exposed directly?
- Can references be manipulated?
```

#### Data Flow Tracer (Security Focus)
```markdown
# Sensitive Data Flow Analysis

## Focus Areas

### 1. Sensitive Data Identification
- What data is sensitive? (credentials, PII, financial, etc.)
- Where does it originate?
- Where does it terminate?

### 2. Data in Transit
- How is sensitive data transmitted?
- Encryption in transit?
- Secure protocols used?

### 3. Data at Rest
- How is sensitive data stored?
- Encryption at rest?
- Access controls on storage?

### 4. Data Processing
- Where is sensitive data processed?
- Is it exposed during processing?
- Temporary storage during processing?

### 5. Data Leakage Points
- Logging
- Error messages
- Debug output
- Caching
- Backup systems

## Map Data Flows
For each sensitive data type:
- Entry point
- Processing steps
- Storage locations
- Exit points
- Potential leakage points
```

---

## Phase D: Findings Compilation (Extended)

### Security Report Structure

```markdown
# Security Review Report

## Executive Summary
- **Overall Security Posture:** [Good / Needs Improvement / Concerning / Critical]
- **Critical Vulnerabilities:** {N}
- **High Vulnerabilities:** {N}
- **Medium/Low/Info:** {N}
- **Immediate Actions Required:** {list}

## Critical Findings (Fix Immediately)

### SEC-C01: {Title}
**Severity:** CRITICAL
**Location:** `file:lines`
**Vulnerability Type:** {type}
**Description:** {description}
**Attack Scenario:** {how it could be exploited}
**Impact:** {what an attacker could achieve}
**Recommendation:** {how to fix}
**References:** {CVE, OWASP, etc.}

## High Severity Findings
[Same format as Critical]

## Medium Severity Findings
[Same format]

## Low Severity / Informational
[Abbreviated format]

## Security by Category

### Injection Vulnerabilities
| ID | Severity | Type | Location | Status |
|----|----------|------|----------|--------|

### Authentication Issues
...

### Authorization Issues
...

### Data Exposure
...

### Input Validation
...

## Positive Findings
[Security measures done well - reinforce good practices]

## Recommendations Summary
1. Immediate (Critical/High)
2. Short-term (Medium)
3. Long-term (Low/Best practices)

## Appendix: Methodology
[How the review was conducted]
```

---

## Phase E: User Summary (Extended)

### Presenting Security Findings

1. **Lead with Risk Assessment**
   - Overall security posture
   - Critical findings count

2. **Present Critical Issues First**
   - These need immediate attention
   - Explain attack scenarios simply

3. **Provide Actionable Recommendations**
   - Clear steps to fix each issue
   - Priority order

4. **Don't Overwhelm**
   - Focus on what matters most
   - Group similar issues

5. **Offer to Deep Dive**
   - User may want more detail on specific findings
   - Can demonstrate vulnerabilities if helpful

---

## Special Considerations

### Responsible Disclosure
- Be careful about documenting exploit details
- Consider who has access to the report
- Mask sensitive paths/data in examples

### False Positives
- Security tools often have false positives
- Manual verification is important
- Note confidence level

### Risk Context
- Consider the application's threat model
- An issue in an internal tool ≠ issue in public API
- Severity should reflect actual risk

### Compliance
- Note any compliance implications
- Reference relevant standards (OWASP, CWE, etc.)

---

## Example Workflow

1. User runs "Security Review" prompt
2. Coordinator asks scope questions
3. User: "Review the API endpoints, focus on authentication and input validation"
4. Review folder: `2026-01-23_security_api-endpoints/`
5. Agents: Security Auditor, Input Validation Analyst, Auth/Access Reviewer, Data Flow Tracer, Error Handling Auditor
6. Agents analyze API code
7. Findings:
   - 2 Critical: SQL injection in search endpoint, hardcoded API key
   - 3 High: Missing rate limiting, weak session tokens, path traversal
   - 5 Medium: Various input validation gaps
8. Report prioritizes critical fixes
9. User creates project to address critical and high findings

---

## Termination

After presenting findings:
1. Ensure user understands critical issues
2. Discuss remediation timeline
3. Offer options:
   - Create security remediation project
   - Provide detailed fix guidance for specific issues
   - Schedule follow-up review after fixes
4. Update `reviews_index.md`
5. Note: Consider report confidentiality
