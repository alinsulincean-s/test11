#!/usr/bin/env python3
"""Check uptime on Linux servers over SSH."""

import argparse
import subprocess


def check_uptime(host: str, timeout: int) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [
                "ssh",
                "-o", "BatchMode=yes",
                "-o", f"ConnectTimeout={timeout}",
                host,
                "uptime -p",
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 2,
            check=False,
        )
    except FileNotFoundError:
        return False, "ssh command not found"
    except subprocess.TimeoutExpired:
        return False, "connection timed out"

    if result.returncode == 0:
        return True, result.stdout.strip()

    error = result.stderr.strip() or f"ssh exited with code {result.returncode}"
    return False, error


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Display uptime for Linux servers reachable over SSH."
    )
    parser.add_argument("hosts", nargs="+", help="SSH hostnames or user@host values")
    parser.add_argument(
        "--timeout", type=int, default=5, help="SSH connection timeout in seconds"
    )
    args = parser.parse_args()

    failed = False
    for host in args.hosts:
        ok, message = check_uptime(host, args.timeout)
        status = "OK" if ok else "ERROR"
        print(f"{host}: {status} — {message}")
        failed |= not ok

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
