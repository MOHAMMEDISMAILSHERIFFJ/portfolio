"""Start the Python portfolio API and Vite preview together."""

from __future__ import annotations

import subprocess
import sys
import socket
import time
import urllib.error
import urllib.request
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def find_free_port(start: int, end: int) -> int:
    for port in range(start, end):
        with socket.socket() as probe:
            try:
                probe.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free local port found between {start} and {end - 1}.")


def wait_for_api(process: subprocess.Popen[bytes], port: int) -> None:
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("The Python portfolio API exited before it was ready.")
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/portfolio", timeout=1) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.15)
    raise RuntimeError("The Python portfolio API did not start on port 8000.")


def stop(process: subprocess.Popen[bytes] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def main() -> int:
    api_port = find_free_port(8000, 8020)
    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend:app", "--host", "127.0.0.1", "--port", str(api_port)],
        cwd=ROOT,
    )
    vite: subprocess.Popen[bytes] | None = None
    try:
        wait_for_api(api, api_port)
        preview_port = find_free_port(5173, 5200)
        vite_entry = ROOT / "node_modules" / "vite" / "bin" / "vite.js"
        environment = os.environ.copy()
        environment["PORTFOLIO_API_URL"] = f"http://127.0.0.1:{api_port}"
        vite = subprocess.Popen(
            ["node", str(vite_entry), "--host", "127.0.0.1", "--port", str(preview_port), "--strictPort"],
            cwd=ROOT,
            env=environment,
        )
        print(f"Python API: http://127.0.0.1:{api_port}  |  Portfolio preview: http://127.0.0.1:{preview_port}", flush=True)
        return vite.wait()
    except KeyboardInterrupt:
        return 0
    except Exception as error:
        print(f"Could not start the portfolio: {error}", file=sys.stderr)
        return 1
    finally:
        stop(vite)
        stop(api)


if __name__ == "__main__":
    raise SystemExit(main())
