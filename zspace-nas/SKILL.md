---
name: zspace-nas
description: Use when user wants to connect to, manage, or run commands on their ZSpace (极空间) NAS. Triggers on keywords like "极空间", "NAS", "zspace", "nas上", "家里的服务器".
---

# ZSpace NAS Remote Access

## Connection

SSH alias `nas` is pre-configured. Connect via:

```bash
ssh nas
```

## Details

- **Host:** ssh.superdyland.uk (Cloudflare Tunnel)
- **User:** 15869560895
- **Proxy:** cloudflared via local proxy (127.0.0.1:7892)
- **Auth:** Cloudflare Access (browser auth on first connection per session)

## Running Remote Commands

Single command:
```bash
ssh nas "ls /path"
```

Interactive session:
```bash
ssh nas
```

## Notes

- First connection in a session triggers Cloudflare Access browser authentication
- Requires local proxy (Clash etc.) running on port 7892
- If connection times out, check: (1) proxy is running, (2) tunnel is healthy in Cloudflare dashboard
- NAS SSH port is non-standard (10000), handled by tunnel config server-side
