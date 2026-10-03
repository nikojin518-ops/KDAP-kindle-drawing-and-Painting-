#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP HTTP 文字输入服务"""
import http.server
import socketserver
import threading
import os
import base64
import json
import urllib.parse
from core.config import KDAPConfig, BASE

HTTP_PIPE = os.path.join(BASE, "kdap_http_pipe")

INDEX_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KDAP Text Input</title>
<style>
body { font-family: sans-serif; max-width: 500px; margin: 40px auto; padding: 20px; background: #f5f5f5; }
h1 { color: #333; }
textarea { width: 100%; height: 120px; font-size: 18px; padding: 10px; border: 2px solid #999; border-radius: 6px; resize: vertical; }
input[type="text"] { width: 100%; font-size: 18px; padding: 10px; border: 2px solid #999; border-radius: 6px; margin-bottom: 10px; }
button { width: 100%; font-size: 20px; padding: 12px; background: #333; color: white; border: none; border-radius: 6px; cursor: pointer; }
button:hover { background: #555; }
.status { margin-top: 15px; padding: 10px; border-radius: 4px; }
.ok { background: #d4edda; color: #155724; }
.err { background: #f8d7da; color: #721c24; }
</style>
</head>
<body>
<h1>KDAP Text Input</h1>
<p>Type text below, it will appear on your Kindle canvas:</p>
<form id="f" action="/submit" method="POST">
    <input type="text" name="title" placeholder="Title (optional)" maxlength="50"><br>
    <textarea name="text" placeholder="Type your text here..." maxlength="500" required></textarea><br><br>
    <button type="submit">Send to Kindle</button>
</form>
<div class="status" id="status"></div>
<script>
document.getElementById('f').addEventListener('submit', async function(e) {
    e.preventDefault();
    const fd = new FormData(this);
    const resp = await fetch('/submit', { method: 'POST', body: fd });
    const result = await resp.text();
    const st = document.getElementById('status');
    if (resp.ok) {
        st.className = 'status ok';
        st.textContent = 'Sent! Text will appear on Kindle.';
        this.reset();
    } else if (resp.status === 401) {
        st.className = 'status err';
        st.textContent = 'Auth failed. Check username/password.';
    } else {
        st.className = 'status err';
        st.textContent = 'Error: ' + result;
    }
});
</script>
</body>
</html>"""


class KDAPTextHandler(http.server.SimpleHTTPRequestHandler):
    def _check_auth(self):
        if not self.server.kdap_user:
            return True
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
            user, pwd = decoded.split(":", 1)
            return user == self.server.kdap_user and pwd == self.server.kdap_pass
        except Exception:
            return False

    def _require_auth(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="KDAP"')
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Authentication required")

    def do_GET(self):
        if not self._check_auth():
            self._require_auth()
            return
        if self.path == "/" or self.path == "/index.html":
            self._serve_page()
        else:
            super().do_GET()

    def do_POST(self):
        if not self._check_auth():
            self._require_auth()
            return
        if self.path == "/submit":
            self._handle_submit()
        else:
            self.send_error(404)

    def _serve_page(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(INDEX_HTML.encode("utf-8")))
        self.end_headers()
        self.wfile.write(INDEX_HTML.encode("utf-8"))

    def _handle_submit(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        params = {}
        for pair in body.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params[k] = urllib.parse.unquote_plus(v)

        text = params.get("text", "").strip()
        title = params.get("title", "").strip()

        if not text:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Empty text")
            return

        combined = f"{title}\n{text}" if title else text
        try:
            if not os.path.exists(HTTP_PIPE):
                os.mkfifo(HTTP_PIPE)
            fd = os.open(HTTP_PIPE, os.O_WRONLY | os.O_NONBLOCK)
            os.write(fd, (combined + "\n").encode("utf-8"))
            os.close(fd)
        except BlockingIOError:
            pass
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass


_httpd = None
_httpd_thread = None


def kdap_http_start(cfg, port=None, host=None, user=None, pwd=None):
    global _httpd, _httpd_thread
    if _httpd is not None:
        return False
    port = port or cfg.HTTP_PORT
    host = host or cfg.HTTP_IP
    try:
        _httpd = socketserver.TCPServer((host, port), KDAPTextHandler)
        _httpd.kdap_user = user if user is not None else cfg.HTTP_USER
        _httpd.kdap_pass = pwd if pwd is not None else cfg.HTTP_PASS
    except OSError:
        _httpd = None
        return False
    _httpd_thread = threading.Thread(target=_httpd.serve_forever, daemon=True)
    _httpd_thread.start()
    return True


def kdap_http_stop():
    global _httpd, _httpd_thread
    if _httpd is None:
        return
    _httpd.shutdown()
    _httpd.server_close()
    _httpd = None
    _httpd_thread = None


def kdap_http_running():
    return _httpd is not None


def kdap_http_configure(cfg, port=None, ip=None, user=None, pwd=None):
    if port is not None:
        cfg.HTTP_PORT = port
    if ip is not None:
        cfg.HTTP_IP = ip
    if user is not None:
        cfg.HTTP_USER = user
    if pwd is not None:
        cfg.HTTP_PASS = pwd
    cfg.save_conf()


def kdap_get_http_text(timeout=0.1):
    if not os.path.exists(HTTP_PIPE):
        return None
    try:
        fd = os.open(HTTP_PIPE, os.O_RDONLY | os.O_NONBLOCK)
        data = os.read(fd, 4096)
        os.close(fd)
        text = data.decode("utf-8").strip()
        return text if text else None
    except BlockingIOError:
        return None
    except Exception:
        return None
