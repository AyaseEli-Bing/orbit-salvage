#!/usr/bin/env python3
"""Orbit Salvage 本地启动器。

用 Python 标准库起一个静态服务器并自动打开浏览器。
不依赖任何第三方包，Python 3.8+ 可直接运行。

用法:
    python3 serve.py              # 默认 8000 端口并打开浏览器
    python3 serve.py -p 5173      # 指定端口
    python3 serve.py --no-browser # 只起服务，不打开浏览器
"""
from __future__ import annotations

import argparse
import http.server
import socketserver
import threading
import webbrowser
from functools import partial
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """静音版静态文件处理器（不打印每条请求日志）。"""

    def log_message(self, fmt: str, *args: object) -> None:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="启动 Orbit Salvage 本地服务")
    parser.add_argument("-p", "--port", type=int, default=8000, help="监听端口，默认 8000")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    args = parser.parse_args()

    handler = partial(QuietHandler, directory=str(BASE_DIR))
    socketserver.ThreadingTCPServer.allow_reuse_address = True

    with socketserver.ThreadingTCPServer(("127.0.0.1", args.port), handler) as httpd:
        url = f"http://127.0.0.1:{args.port}/index.html"
        print(f"星轨回收者已启动 -> {url}")
        print("按 Ctrl+C 停止服务")
        if not args.no_browser:
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务已停止。")


if __name__ == "__main__":
    main()
