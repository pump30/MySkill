#!/usr/bin/env python3
"""Send email via Gmail SMTP with HTTP CONNECT proxy support."""

import smtplib
import argparse
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse
import ssl

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = "clawdbot.dyland@gmail.com"
SMTP_PASS = "mlnv duuy qcgt veiz"
FROM_EMAIL = "clawdbot.dyland@gmail.com"
DEFAULT_TO = "1069235479@qq.com"
PROXY = "http://127.0.0.1:7892"


def connect_via_proxy(host, port, proxy_url):
    """Establish TCP connection through HTTP CONNECT proxy, then wrap with SSL."""
    proxy = urlparse(proxy_url)
    sock = socket.create_connection((proxy.hostname, proxy.port), timeout=30)

    connect_req = f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n"
    sock.sendall(connect_req.encode())

    response = b""
    while b"\r\n\r\n" not in response:
        response += sock.recv(4096)

    status_line = response.split(b"\r\n")[0].decode()
    if "200" not in status_line:
        raise ConnectionError(f"Proxy CONNECT failed: {status_line}")

    context = ssl.create_default_context()
    ssl_sock = context.wrap_socket(sock, server_hostname=host)
    return ssl_sock


def send_email(subject, body, to=None):
    """Send email through Gmail SMTP via proxy."""
    recipient = to or DEFAULT_TO

    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    ssl_sock = connect_via_proxy(SMTP_HOST, SMTP_PORT, PROXY)

    smtp = smtplib.SMTP()
    smtp.sock = ssl_sock
    smtp.file = ssl_sock.makefile("rb")
    # Read server greeting
    code, greeting = smtp.getreply()
    if code != 220:
        raise ConnectionError(f"SMTP greeting failed: {code} {greeting}")
    smtp.ehlo()
    smtp.login(SMTP_USER, SMTP_PASS)
    smtp.sendmail(FROM_EMAIL, recipient, msg.as_string())
    smtp.quit()

    print(f"[SUCCESS] 邮件发送成功！")
    print(f"  收件人: {recipient}")
    print(f"  主题: {subject}")


def main():
    parser = argparse.ArgumentParser(description="Send email via Gmail SMTP")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", required=True, help="Email body")
    parser.add_argument("--to", default=None, help=f"Recipient (default: {DEFAULT_TO})")
    args = parser.parse_args()

    try:
        send_email(args.subject, args.body, args.to)
    except Exception as e:
        print(f"[ERROR] 发送失败: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
