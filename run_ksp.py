"""Single-command launcher for the KSP Drishti Challenge 02 prototype.

The launcher deliberately keeps all generated artefacts inside this repository:
logs, synthetic data, the virtual environment, and frontend dependencies.  It
briefs the operator, prepares dependencies on approval, starts the API and UI,
and mirrors service output to a timestamped log file.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
VENV_DIR = ROOT / ".venv"
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"
ANSI = {
    "reset": "\033[0m", "navy": "\033[38;5;25m", "green": "\033[38;5;79m",
    "gold": "\033[38;5;221m", "red": "\033[38;5;203m", "dim": "\033[2m", "bold": "\033[1m",
}


def colour(text: str, tone: str) -> str:
    return f"{ANSI[tone]}{text}{ANSI['reset']}" if sys.stdout.isatty() else text


def print_banner() -> None:
    border = "+" + ("-" * 70) + "+"
    print(colour(f"\n{border}", "navy"))
    print(colour(f"| {'KSP DRISHTI':^68} |", "gold"))
    print(colour(f"| {'AI-Driven Crime Analytics & Visualization Platform':^68} |", "gold"))
    print(colour(border, "navy"))
    print("Developed by Himanshu Yadav and team")
    print("For the Karnataka State Police and Zoho Datathon - Challenge 02\n")
    print(colour("Objective", "green") + ": transform fragmented FIR-style records into reviewed, place-based intelligence.")
    print("Capabilities: maps, hotspots, district drilldowns, anomalies, CaseLink networks,")
    print("repeat case-history tracking, contextual associations, and advisory risk ranges.")
    print(colour("Guardrail", "gold") + ": all included records are synthetic. The system never scores a person as a future offender.\n")


class KspLauncher:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.processes: list[subprocess.Popen[str]] = []
        LOG_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = LOG_DIR / f"ksp_runtime_{timestamp}.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            handlers=[logging.FileHandler(self.log_path, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
        )
        self.logger = logging.getLogger("ksp_launcher")

    @property
    def venv_python(self) -> Path:
        return VENV_DIR / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

    def info(self, message: str) -> None:
        self.logger.info(message)

    def ask(self, question: str, default: bool = True) -> bool:
        if self.args.non_interactive:
            return default
        suffix = "[Y/n]" if default else "[y/N]"
        try:
            answer = input(f"{question} {suffix}: ").strip().lower()
        except EOFError:
            return default
        return default if not answer else answer in {"y", "yes"}

    def run_command(self, command: list[str], label: str, cwd: Path = ROOT) -> None:
        self.info(f"{label}: {' '.join(command)}")
        env = dict(os.environ)
        # pnpm otherwise asks whether it may recreate node_modules when the
        # launcher is started outside an interactive terminal.
        env["CI"] = "true"
        completed = subprocess.run(command, cwd=cwd, text=True, check=False, env=env)
        if completed.returncode != 0:
            raise RuntimeError(f"{label} failed with exit code {completed.returncode}.")

    def ensure_dependencies(self) -> None:
        if not self.ask("Install or update required Python and frontend dependencies?", default=True):
            self.info("Dependency installation skipped by operator.")
            return
        if not self.venv_python.exists():
            self.run_command([sys.executable, "-m", "venv", str(VENV_DIR)], "Create local virtual environment")
        self.run_command([str(self.venv_python), "-m", "pip", "install", "-r", "backend/requirements.txt"], "Install backend dependencies")
        package_manager = shutil.which("pnpm") or shutil.which("npm")
        if not package_manager:
            raise RuntimeError("Node package manager not found. Install Node.js 20+ with npm or pnpm, then rerun.")
        if Path(package_manager).stem.lower().startswith("pnpm"):
            command = [package_manager, "--dir", "frontend", "install"]
            command_cwd = ROOT
        else:
            # `npm --prefix frontend install` is unreliable with some Windows
            # npm shims and can look for ROOT/package.json. Run in frontend.
            command = [package_manager, "install"]
            command_cwd = ROOT / "frontend"
        self.run_command(command, "Install frontend dependencies", cwd=command_cwd)

    def prepare_data(self) -> None:
        self.run_command([str(self.venv_python), "execution/run_demo_pipeline.py"], "Generate, validate, and link synthetic data")
        if self.args.train or self.ask("Train the optional CPU risk model now?", default=False):
            self.run_command([str(self.venv_python), "execution/train_risk_model.py"], "Train risk model")

    def _stream_output(self, process: subprocess.Popen[str], label: str) -> None:
        assert process.stdout is not None
        for raw_line in iter(process.stdout.readline, ""):
            line = raw_line.rstrip()
            if line:
                self.logger.info("[%s] %s", label, line)

    def start_process(self, command: list[str], label: str, cwd: Path = ROOT) -> subprocess.Popen[str]:
        env = dict(os.environ)
        env["CI"] = "true"  # prevent package managers from prompting in the child process
        self.info(f"Starting {label}: {' '.join(command)}")
        process = subprocess.Popen(
            command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
        )
        self.processes.append(process)
        threading.Thread(target=self._stream_output, args=(process, label), daemon=True).start()
        return process

    def wait_for_url(self, url: str, label: str, timeout: int = 30) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(url, timeout=2) as response:
                    if 200 <= response.status < 500:
                        self.info(f"{label} is ready at {url}")
                        return
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.5)
        raise RuntimeError(f"{label} did not start within {timeout} seconds. See {self.log_path}.")

    def require_available_port(self, port: int, label: str) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.settimeout(0.5)
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(
                    f"{label} cannot start because port {port} is already in use. "
                    "Stop the existing service, then run KSP Drishti again."
                )

    def start_services(self) -> None:
        self.require_available_port(8000, "Backend API")
        self.require_available_port(5173, "Frontend dashboard")
        backend = self.start_process(
            [str(self.venv_python), "-m", "uvicorn", "app.main:app", "--app-dir", "backend", "--host", "127.0.0.1", "--port", "8000"],
            "backend",
        )
        self.wait_for_url(f"{BACKEND_URL}/health", "Backend API")
        if backend.poll() is not None:
            raise RuntimeError(f"Backend API exited early. See {self.log_path}.")
        package_manager = shutil.which("pnpm") or shutil.which("npm")
        if not package_manager:
            raise RuntimeError("Node package manager not found.")
        if Path(package_manager).stem.lower().startswith("pnpm"):
            frontend_command = [package_manager, "--dir", "frontend", "dev", "--host", "127.0.0.1"]
            frontend_cwd = ROOT
        else:
            frontend_command = [package_manager, "run", "dev", "--", "--host", "127.0.0.1"]
            frontend_cwd = ROOT / "frontend"
        self.start_process(frontend_command, "frontend", cwd=frontend_cwd)
        self.wait_for_url(FRONTEND_URL, "Frontend dashboard")
        print(colour(f"\nDashboard: {FRONTEND_URL}", "green"))
        print(colour(f"API docs:  {BACKEND_URL}/docs", "green"))
        print(f"Runtime log: {self.log_path}")
        print(f"Frontend interaction log: {LOG_DIR / 'frontend_events.jsonl'}")
        if not self.args.no_browser:
            webbrowser.open(FRONTEND_URL)

    def stop_services(self) -> None:
        for process in reversed(self.processes):
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill()
        self.info("All KSP Drishti services stopped.")

    def run(self) -> None:
        print_banner()
        self.info("Launcher initialised. Every service action will be mirrored to this terminal and the runtime log.")
        self.ensure_dependencies()
        self.prepare_data()
        if self.args.prepare_only:
            self.info("Prepare-only mode completed successfully.")
            return
        try:
            self.start_services()
            print("\nPress Ctrl+C to stop all services.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping KSP Drishti...")
        finally:
            self.stop_services()


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the KSP Drishti Challenge 02 prototype.")
    parser.add_argument("--train", action="store_true", help="Train the optional risk model before starting services.")
    parser.add_argument("--prepare-only", action="store_true", help="Install/prepare data, then exit without starting services.")
    parser.add_argument("--non-interactive", action="store_true", help="Accept default prompts for automation.")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the dashboard automatically.")
    return parser.parse_args(argv)


if __name__ == "__main__":
    KspLauncher(parse_args()).run()
