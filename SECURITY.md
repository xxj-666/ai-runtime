# Security Policy

ai-runtime is experimental and is not production-hardened. The current release
does not provide sandboxing, authorization, secret management, or tenant
isolation. Applications are responsible for restricting the tools they
register and the data they send to providers.

## Supported versions

There are no tagged releases yet. Security fixes currently target the `main`
branch. This policy will be updated when the first release is published.

## Reporting a vulnerability

Do not disclose sensitive vulnerability details in a public GitHub issue.

Use GitHub private vulnerability reporting if the repository's **Security**
page offers that option. If it is not available, open a minimal public issue
requesting a private contact channel without including exploit details,
credentials, customer information, or other sensitive material.

The maintainer still needs to verify and, if necessary, enable private
vulnerability reporting in the GitHub repository settings.

## Security scope

Reports are especially useful when they concern:

- API key or credential leakage;
- unsafe tool registration or execution;
- prompt, model, and tool-boundary confusion;
- provider-adapter request or response handling;
- dependency vulnerabilities;
- future permission, persistence, or isolation features.

The existence of this policy does not imply that the project has completed a
security audit.
