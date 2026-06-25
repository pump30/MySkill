# vault-lookup

Claude Code skill to look up credentials from a self-hosted Vaultwarden (Bitwarden-compatible) server.

## Features

- Authenticates via Bitwarden API with PBKDF2 + HKDF key derivation
- Decrypts vault entries client-side (AES-256-CBC)
- Search by name, URI, username, or notes
- List all entries

## Setup

1. Install dependencies:
   ```bash
   pip3 install cryptography requests
   ```

2. Create config:
   ```bash
   mkdir -p ~/.config/vault-lookup
   cp config.example.json ~/.config/vault-lookup/config.json
   # Edit with your actual credentials
   ```

3. Install skill:
   ```bash
   cp -r vault-lookup ~/.claude/skills/vault-lookup
   ```

## Trigger phrases

- "查密码", "vault里找", "vault查一下"
- "帮我找密码", "拿个凭据"
- Any time credentials are needed for configuring a service

## Security

- Master password is stored locally in `~/.config/vault-lookup/config.json`
- Never commit config to git
- Decryption happens entirely client-side
