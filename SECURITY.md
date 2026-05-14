# Security Policy

The DERMS project takes security seriously. We appreciate responsible
disclosure of vulnerabilities and aim to respond promptly and transparently.

---

## Supported Versions

Security updates are provided for the following versions:

| Version | Supported            |
| ------- | -------------------- |
| 0.1.x   | :white_check_mark:   |
| < 0.1   | :x: (pre-release)    |

Once a version is no longer supported, users are strongly encouraged to
upgrade to the latest stable release.

---

## Reporting a Vulnerability

**Please DO NOT open a public GitHub issue for security vulnerabilities.**  
Public disclosure before a fix is available puts all users at risk.

### Private Disclosure Process

1. **GitHub Security Advisories (preferred)**  
   Report privately at:  
   https://github.com/AUREX-ML/DERMS/security/advisories/new

2. **Email fallback**  
   If you cannot use GitHub, email **aurexcv@gmail.com** with:
   - Subject: `[DERMS SECURITY] <brief description>`
   - A description of the vulnerability and affected component
   - Steps to reproduce (proof-of-concept code if available)
   - Potential impact assessment
   - Your preferred disclosure timeline

### What to Expect

| Stage | Timeline |
|---|---|
| Acknowledgement | Within **72 hours** of receipt |
| Initial assessment | Within **7 days** |
| Fix / patch release | Target **30 days** (complex issues may take longer) |
| Public disclosure | After the fix is released and users have had time to upgrade |

We follow **coordinated disclosure**: we work with the reporter to agree on a
disclosure date, credit the reporter in the release notes (unless anonymity
is requested), and publish a GitHub Security Advisory once the fix is live.

---

## CVE Process

For confirmed, high-severity vulnerabilities, AUREX-ML will:
- Request a CVE identifier via the GitHub CNA programme.
- Reference the CVE in the patch release and CHANGELOG.
- Publish a Security Advisory with CVSS score, affected versions, and
  remediation instructions.

---

## Scope

In-scope for security reports:
- Authentication or authorisation bypass in the DERMS API
- Injection vulnerabilities (SQL, command, MQTT payload)
- Insecure handling of secrets or credentials
- Dependencies with known high/critical CVEs (`pip-audit` findings)
- Data exposure of sensitive DER telemetry or operator credentials

Out-of-scope:
- Vulnerabilities in third-party services (PostgreSQL, Redis, Mosquitto)
  unless they are caused by DERMS misconfiguration
- Social engineering attacks
- Physical security of DER hardware

---

## Security Best Practices for Operators

- Always override `SECRET_KEY` and `API_KEY` in production `.env`.
- Use TLS for all MQTT connections; disable anonymous access in Mosquitto.
- Rotate database credentials regularly.
- Run `pip-audit -r requirements.txt` before deploying dependency updates.
- Enable GitHub Dependabot alerts on your fork.
