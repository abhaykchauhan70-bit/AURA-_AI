# Security notes

- Passwords are hashed; JWT secret must be changed from the development default.
- API routes check ownership before returning or deleting user records.
- Upload names are replaced with generated identifiers; extensions and size are restricted.
- Files are stored privately in the backend upload volume.
- No arbitrary code execution, shell tool, email sender, or web search is enabled.
- The current memory feature stores only explicit user-created memories.
- Configure HTTPS, stronger token/session handling, rate limits, malware scanning, SSRF defenses, retention controls, and a sandbox before deployment beyond a trusted local environment.
- Never commit `.env` or log credentials and API keys.
