---
name: vault-lookup
description: Look up credentials from a self-hosted Vaultwarden (Bitwarden) server. Use when the user asks for a password, credential, login info, secret, or says "查密码", "vault里找", "vault查一下", "帮我找密码", "拿个凭据", or when you need credentials for another task (e.g. configuring a service).
---

## Config

Credentials are stored in:

```
~/.config/vault-lookup/config.json
```

Schema:

```json
{
  "base_url": "https://vault.superdyland.uk",
  "email": "user@example.com",
  "master_password": "<master-password>"
}
```

**Security:** Never echo the master password or any retrieved passwords to the user unless they explicitly ask to see a specific credential. Never commit config to git.

## When invoked

1. Read `~/.config/vault-lookup/config.json`. If missing, tell the user to create it.
2. Run the lookup script: `bash <skill-dir>/scripts/vault-lookup.sh [search-term]`
3. The script outputs JSON with matching entries. Parse and present results.
4. If the user asked for a specific credential by name or URL, show the username and password.
5. If multiple matches, list names and ask which one.

## Usage patterns

- **Direct lookup:** "vault里找 radicale 的密码" → search "radicale", return credentials
- **Service config:** When setting up a new service and need credentials, auto-lookup from vault
- **List all:** "vault里有什么" → run without search term, list all entry names

## Output format

When showing credentials to the user:
```
🔑 <entry-name>
   User: <username>
   Pass: <password>
   URI:  <uri>
```

When listing entries (no specific lookup):
```
📋 Vault entries:
  1. <name> (uri)
  2. <name> (uri)
  ...
```
