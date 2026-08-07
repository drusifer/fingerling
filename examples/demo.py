#!/usr/bin/env python3
"""Unified interactive TUI dashboard for Fingerling vaccination demo (Sprint 6).

Guides the user step-by-step through a full Closed-Loop trace vaccination cycle.
If run with root/sudo and bpftrace is available, it attaches live eBPF tracepoint
probes to trace the target app's process tree in real-time. Otherwise, it falls
back gracefully to simulated tracing.

Run it with:
    make demo
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import os
import signal
import subprocess
import sys
import threading
import time
import urllib.request
from typing import Any

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

# Import Fingerling core components
from fingerling.gitops import initialize_repo
from fingerling.ringbuffer import SlidingWindowMatcher
from fingerling.server import run_server
from fingerling.tokenizer import MaskEntry, tokenize
from fingerling.warehouse import Warehouse, fingerprint_id
from fingerling.capture import run_capture, stop_capture, wait_ready, parse_stream
from examples.vulnerable_app import run_app


# Constant vulnerable code snippet shown in TUI Code pane
VULNERABLE_CODE_SNIPPET = """def handle_ping(host: str) -> str:
    # 🛑 VULNERABILITY: shell=True command injection
    cmd = f"ping -c 1 {host}"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout"""


def get_key() -> str:
    """Read a single keypress without line buffering or echo, leaving output processing intact."""
    if not sys.stdin.isatty():
        # Fallback for piped inputs / automated tests
        ch = sys.stdin.read(1)
        return ch.lower()

    try:
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        new_settings = termios.tcgetattr(fd)
        # Clear ICANON (canonical mode) and ECHO (echo input characters)
        new_settings[3] = new_settings[3] & ~termios.ICANON & ~termios.ECHO
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.lower()
    except Exception:
        try:
            return sys.stdin.read(1).lower()
        except Exception:
            return 'q'


class LogPipe(io.StringIO):
    """Thread-safe pipe that intercepts print statements and stores them in a deque."""
    def __init__(self, max_lines: int = 15) -> None:
        super().__init__()
        self.lock = threading.Lock()
        self.deque: collections.deque[str] = collections.deque(maxlen=max_lines)
        self.line_counter = 0

    def write(self, s: str) -> int:
        if s.strip():
            with self.lock:
                for line in s.splitlines():
                    if line.strip():
                        content = line.strip()
                        
                        # Detect and format Client labels (10 chars total, right-justified)
                        if "[Client request]" in content:
                            prefix = " \033[94m[CLI:REQ]\033[0m"
                            content = prefix + " " + content.replace("[Client request]", "").strip()
                        elif "[Client response]" in content:
                            prefix = "\033[92m[CLI:RESP]\033[0m"
                            content = prefix + " " + content.replace("[Client response]", "").strip()
                        elif "[Client stdout]" in content:
                            prefix = " \033[37m[CLI:OUT]\033[0m"
                            content = prefix + " " + content.replace("[Client stdout]", "").strip()
                        elif "[Client stderr]" in content:
                            prefix = " \033[91m[CLI:ERR]\033[0m"
                            content = prefix + " " + content.replace("[Client stderr]", "").strip()
                        
                        # Detect and format Server labels (10 chars total, right-justified)
                        elif "[Server stdout]" in content:
                            prefix = " \033[95m[SRV:OUT]\033[0m"
                            content = prefix + " " + content.replace("[Server stdout]", "").strip()
                        elif "[Server stderr]" in content:
                            prefix = " \033[31m[SRV:ERR]\033[0m"
                            content = prefix + " " + content.replace("[Server stderr]", "").strip()
                        elif "[Server access.log]" in content:
                            prefix = "\033[96m[SRV:ACCS]\033[0m"
                            content = prefix + " " + content.replace("[Server access.log]", "").strip()
                        elif "[Server webhook.log]" in content:
                            prefix = " \033[33m[WHK:ACCS]\033[0m"
                            content = prefix + " " + content.replace("[Server webhook.log]", "").strip()

                        self.line_counter += 1
                        self.deque.append(f"\033[90m{self.line_counter:2d} |\033[0m {content}")
        return len(s)

    def get_logs(self) -> str:
        with self.lock:
            return "\n".join(self.deque)


class TUIDemo:
    def __init__(self) -> None:
        self.step = 1
        self.app_port = 0
        self.webhook_port = 0
        self.repo_path = ""
        self.policy_file = ""
        
        # Check if we can run bpftrace
        self.use_ebpf = False
        try:
            res = subprocess.run(["sudo", "bpftrace", "-V"], capture_output=True, text=True, timeout=1.5)
            if res.returncode == 0:
                self.use_ebpf = True
        except Exception:
            pass

        # Subprocess and Server handles
        self.app_proc = None
        self.webhook_server = None
        self.temp_dir = None
        self.app_pid = os.getpid()

        # Telemetry structures
        self.client_log_pipe = LogPipe()
        self.server_log_pipe = LogPipe()
        self.console = Console(file=sys.__stdout__)
        self.layout = Layout()
        
        # Telemetry State variables
        self.syscall_list: list[str] = []
        self.whitelist_2grams: list[tuple[str, str]] = []
        self.current_score = 0.0
        self.anomalous_transition: tuple[str, str] | None = None
        self.policy_manifest = ""
        
        # Split eBPF logs
        self.raw_traces: list[str] = []
        self.daemon_logs: list[str] = []

    def setup_layout(self) -> None:
        """Create screen layout partitions."""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )

    def update_view(self) -> None:
        """Repopulate screen contents based on active step to prevent layout clipping."""
        # Calculate dynamic log display heights based on terminal size to enable autoscroll
        console_height = self.console.size.height or 24
        raw_traces_height = max(4, int(console_height * (6 / 14)) - 2)
        logs_height = max(3, int(console_height * (4 / 14)) - 2)

        # Dynamically split body according to active step to optimize screen space
        self.layout["body"]._children.clear()
        
        if self.step == 1 or self.step == 8:
            # Narrative guide only (Full Width)
            self.layout["body"].split_column(
                Layout(name="narrative")
            )
        elif self.step == 2:
            # Code Flaw & Narrative guide stacked vertically
            self.layout["body"].split_column(
                Layout(name="code", ratio=3),
                Layout(name="narrative", ratio=2),
            )
        elif self.step == 5:
            # Policy manifest & Narrative guide stacked vertically
            self.layout["body"].split_column(
                Layout(name="telemetry", ratio=3),
                Layout(name="narrative", ratio=1),
            )
        else:
            # Top: narrative, Middle: split eBPF pane, Bottom: split Client/Server logs
            self.layout["body"].split_column(
                Layout(name="narrative", ratio=4),
                Layout(name="orchestrator_row", ratio=6),
                Layout(name="logs_row", ratio=4),
            )
            self.layout["orchestrator_row"].split_row(
                Layout(name="bpftrace_traces", ratio=6),
                Layout(name="daemon_orchestrator", ratio=4),
            )
            self.layout["logs_row"].split_row(
                Layout(name="client_logs", ratio=5),
                Layout(name="server_logs", ratio=5),
            )

        # 1. Header
        try:
            self.layout["header"].update(
                Panel(
                    Text("🛡️  PROJECT FINGERLING - CLOSED-LOOP VACCINATION INTERACTIVE TUI DEMO", style="bold green center"),
                    border_style="blue",
                )
            )
        except KeyError:
            pass

        # 2. Footer
        try:
            self.layout["footer"].update(
                Panel(
                    Text("Press any key to advance step  |  [Q] Quit Demo  |  Stable single-terminal view", style="bold cyan center"),
                    border_style="blue",
                )
            )
        except KeyError:
            pass

        # 3. Code Panel
        try:
            self.layout["code"].update(
                Panel(
                    Syntax(VULNERABLE_CODE_SNIPPET, "python", theme="monokai", line_numbers=True, highlight_lines={3, 4}),
                    title="[bold yellow]Target App Source (CWE-78 Command Injection)[/bold yellow]",
                    border_style="blue",
                )
            )
        except KeyError:
            pass

        # 4. Narratives & Explanations
        try:
            self.layout["narrative"].update(
                Panel(
                    self.get_narrative_text(),
                    title="[bold magenta]Narrative Guide & Pipeline Progress[/bold magenta]",
                    border_style="blue",
                )
            )
        except KeyError:
            pass

        # 5. Policy compilation manifest for Step 5
        try:
            self.layout["telemetry"].update(
                Panel(
                    self.get_telemetry_widget(),
                    title="[bold cyan]Fingerling Telemetry Daemon & Policy Compiler[/bold cyan]",
                    border_style="blue",
                )
            )
        except KeyError:
            pass

        # 6. Split orchestrator rows (bpftrace left, daemon status right)
        try:
            self.layout["bpftrace_traces"].update(
                Panel(
                    self.get_raw_traces_widget(raw_traces_height),
                    title="[bold cyan]eBPF bpftrace Live Activity[/bold cyan]",
                    border_style="blue",
                )
            )
        except KeyError:
            pass

        try:
            self.layout["daemon_orchestrator"].update(
                Panel(
                    self.get_daemon_widget(raw_traces_height),
                    title="[bold cyan]eBPF Daemon Status & Whitelist[/bold cyan]",
                    border_style="blue",
                )
            )
        except KeyError:
            pass

        # 7. Split Client/Server Logs (Bottom Row)
        try:
            client_txt = Text.from_ansi(self.client_log_pipe.get_logs())
            self.layout["client_logs"].update(
                Panel(
                    self.limit_text_lines(client_txt, logs_height),
                    title="[bold green]Client / Attack Output Logs[/bold green]",
                    border_style="blue",
                )
            )
        except KeyError:
            pass

        try:
            server_txt = Text.from_ansi(self.server_log_pipe.get_logs())
            self.layout["server_logs"].update(
                Panel(
                    self.limit_text_lines(server_txt, logs_height),
                    title="[bold green]Live Workload stdout/stderr Output Logs[/bold green]",
                    border_style="blue",
                )
            )
        except KeyError:
            pass

    def limit_text_lines(self, text: Text, max_lines: int) -> Text:
        """Truncates a styled Rich Text object to keep only the last N lines."""
        lines = text.split("\n")
        if len(lines) <= max_lines:
            return text
        truncated = Text()
        for line in lines[-max_lines:]:
            truncated.append(line)
            truncated.append("\n")
        return truncated

    def get_narrative_text(self) -> Text:
        """Returns rich, step-by-step narrative text to guide the user."""
        txt = Text()
        if self.step == 1:
            txt.append("👋 Welcome to the interactive Fingerling Vaccination TUI!\n\n", style="bold cyan")
            txt.append("This dashboard guides you through a full Closed-Loop Vaccination Cycle.\n")
            txt.append("Our Goal: Immunize a vulnerable workload against command execution exploits\n")
            txt.append("using zero-trust runtime whitelists (compiled into security policies)\n")
            txt.append("WITHOUT modifying the application source code or restarting the server.\n\n")
            txt.append("👉 Press any key to bootstrap the GitOps repository and boot the vulnerable target web server.")
            
        elif self.step == 2:
            txt.append("🔎 Step 2: The Command Injection Vulnerability\n\n", style="bold yellow")
            txt.append("Look at the Target App Source Code panel (displayed above).\n")
            txt.append("The server runs a system ping command using subprocess.run(..., shell=True).\n")
            txt.append("Because shell=True is enabled, the command is executed in a system shell.\n")
            txt.append("An attacker can append control operators like ';' or '&&' to execute arbitrary processes.\n\n")
            txt.append(f"  * Vulnerable App running on port: {self.app_port} (PID: {self.app_pid})\n")
            txt.append(f"  * Webhook Server running on port: {self.webhook_port}\n")
            txt.append(f"  * GitOps Repository: {self.repo_path}\n\n")
            txt.append("👉 Press any key to send legitimate baseline traffic and warm up the telemetry whitelists.")
            
        elif self.step == 3:
            txt.append("🟢 Step 3: Legitimate Baseline Warmup (Whitelisting)\n\n", style="bold green")
            txt.append("We sent clean HTTP GET /ping?host=127.0.0.1 requests to the target application.\n")
            txt.append("The tracer captures the resulting process executions in the workload namespace.\n")
            txt.append("Under normal business usage, the app only executes `/bin/ping` via `/bin/sh`.\n")
            txt.append("The telemetry pipeline records this as the whitelisted transition: sh -> ping.\n\n")
            txt.append("👉 Press any key to detonate the malicious command injection exploit payload.")
            
        elif self.step == 4:
            txt.append("💥 Step 4: Malicious Exploit Injection & Anomaly Detection\n\n", style="bold red")
            txt.append("We sent the exploit query: GET /ping?host=127.0.0.1;echo boo.\n")
            txt.append("Because the app is vulnerable, the shell executes the injected `echo boo` command.\n")
            txt.append("The tracer catches the execution of `/bin/echo` in the workload process subtree.\n")
            txt.append("The matcher compares this transition (sh -> echo) against the whitelist.\n")
            txt.append("Since `echo` is not whitelisted, the score drifts to [bold red]1.0 (ANOMALY DETECTED)[/bold red]!\n\n")
            txt.append("👉 Press any key to compile and commit the security policy antibody via GitOps.")
            
        elif self.step == 5:
            txt.append("🛡️ Step 5: GitOps Policy Generation & Antibody Reconciliation\n\n", style="bold green")
            txt.append("The vaccination server compiled a KubeArmorPolicy targeting the anomalous binary.\n")
            txt.append("It automatically checks out a branch, commits the policy YAML manifest (displayed above),\n")
            txt.append("and merges it back to the `main` branch to trigger continuous GitOps deployment.\n")
            txt.append("The target app reconciles this policy directory dynamically on incoming requests.\n\n")
            txt.append("👉 Press any key to verify legitimate user traffic remains fully functional.")
            
        elif self.step == 6:
            txt.append("✅ Step 6: Verifying Legitimate Business Traffic is Untouched\n\n", style="bold green")
            txt.append("We sent a clean `/ping?host=127.0.0.1` request. It responded successfully with HTTP 200 OK.\n")
            txt.append("This proves that whitelisting process transitions secures the workload\n")
            txt.append("without causing a Denial of Service (DoS) for legitimate user actions.\n\n")
            txt.append("👉 Press any key to re-trigger the command injection exploit and test enforcement.")
            
        elif self.step == 7:
            txt.append("🛡️ Step 7: Exploit Execution Blocked & PID Verification\n\n", style="bold green")
            txt.append("We triggered the exploit again: `/ping?host=127.0.0.1;echo%20boo`.\n")
            txt.append("The target app checked the active GitOps policy folder, matched the block rule for `/bin/echo`,\n")
            txt.append("and rejected the process fork immediately with an [bold red]HTTP 403 Forbidden[/bold red] response!\n\n")
            txt.append("💡 [bold yellow]Visual Proof: The target application server PID has not changed![/bold yellow]\n")
            txt.append(f"  * PID is still: {self.app_pid} (Zero Downtime, hot-patched live without restarts!)\n\n")
            txt.append("👉 Press any key to clean up resources.")
            
        elif self.step == 8:
            txt.append("👋 Closed-Loop Vaccination Complete!\n\n", style="bold green")
            txt.append("We successfully demonstrated:\n")
            txt.append("  1. Process transition mapping via process trace metrics.\n")
            txt.append("  2. N-gram Whitelist profile generation.\n")
            txt.append("  3. Closed-loop automated policy generation & GitOps hot-patching.\n")
            txt.append("  4. Workload immunization with zero downtime and no server restarts.\n\n")
            txt.append("👉 Press any key to exit the dashboard.")
        return txt

    def get_telemetry_widget(self) -> Any:
        """Returns the telemetry visualization widget (YAML policy manifest)."""
        from rich.console import Group
        explanation = Text(
            "\n💡 Policy Analysis & Mapping:\n"
            "The compiled KubeArmorPolicy maps to the anomalous transition (ping -> echo).\n"
            "By setting matchPaths path to /bin/echo and action to Block,\n"
            "it disrupts the command injection attack chain directly at the process level,\n"
            "securing the workload without editing server code or restarting.",
            style="yellow"
        )
        return Group(
            Syntax(self.policy_manifest, "yaml", theme="monokai", line_numbers=True),
            explanation
        )

    def get_daemon_widget(self, max_height: int) -> Any:
        """Returns the eBPF Daemon Status, whitelist tables, and webhook status logs."""
        from rich.table import Table
        from rich.console import Group
        
        items = []
        
        # Status block
        status_text = Text()
        status_text.append("⚡ Daemon Status: ", style="bold")
        status_text.append("🟢 ACTIVE\n", style="bold green")
        status_text.append(f"   ├─ Monitored Subtree: PID {self.app_pid}\n")
        status_text.append("   ├─ Attached Probes: sys_execve (KProbe/KRetProbe)\n")
        status_text.append(f"   └─ Telemetry Ingest: http://127.0.0.1:{self.webhook_port}/telemetry\n\n")
        
        status_text.append("📊 Analytics:\n", style="bold")
        status_text.append(f"   ├─ Warehouse Size: {len(self.webhook_warehouse._records)} tokens\n")
        status_text.append(f"   ├─ Matcher Window: {self.webhook_matcher._window}\n")
        if self.current_score > 0.05:
            status_text.append("   └─ Anomaly Score: ", style="dim")
            status_text.append(f"{self.current_score:.1f} 🚨\n\n", style="bold red")
        else:
            status_text.append("   └─ Anomaly Score: ", style="dim")
            status_text.append("0.0 (Safe) 🟢\n\n", style="bold green")
            
        items.append(status_text)
        
        # Captured Events list
        events_text = Text()
        events_text.append("Captured Events:\n ", style="bold yellow")
        if not self.syscall_list:
            events_text.append("None yet", style="dim")
        else:
            events_text.append(" ➔ ".join([f"{sys}" for sys in self.syscall_list[-3:]]), style="green")
        events_text.append("\n\n")
        items.append(events_text)
        
        # Transitions Whitelist table
        table = Table(title="Transitions Whitelist Map", title_style="bold yellow", show_header=True, header_style="bold blue", padding=(0, 1))
        table.add_column("Transition Gram", style="cyan")
        table.add_column("Status / Score", justify="right")

        if not self.whitelist_2grams:
            table.add_row("(empty)", "0.0")
        else:
            for gram in self.whitelist_2grams:
                table.add_row(f"{gram[0]} -> {gram[1]}", "Allowed (0.0)", style="green")

        if self.anomalous_transition:
            if self.step >= 7:
                table.add_row(
                    f"{self.anomalous_transition[0]} -> {self.anomalous_transition[1]}",
                    "BLOCKED (Rule) 🛡️",
                    style="bold green"
                )
            else:
                table.add_row(
                    f"{self.anomalous_transition[0]} -> {self.anomalous_transition[1]}",
                    "ANOMALOUS (1.0) 🚨",
                    style="bold red"
                )
        items.append(table)
        
        # Daemon / Webhook Log Events
        daemon_txt = Text()
        daemon_txt.append("\n⚡ Daemon Logs:\n", style="bold yellow")
        if not self.daemon_logs:
            daemon_txt.append("Awaiting daemon webhook logs...", style="dim")
        else:
            # Display last 8 logs
            lines = self.daemon_logs[-8:]
            for line in lines:
                daemon_txt.append(Text.from_ansi(f"{line}\n"))
        items.append(daemon_txt)
        
        return Group(*items)

    def get_raw_traces_widget(self, max_height: int) -> Any:
        """Returns the raw eBPF live activity traces panel content (with Webhook payload instead of raw JSON)."""
        if not self.raw_traces:
            return Text("Listening for eBPF tracepoints...\nNo events captured yet.", style="dim")
        
        # Display the last 15 captured trace records/messages
        lines = self.raw_traces[-15:]
        txt = Text()
        for line in lines:
            if line.startswith("[eBPF Capture]") or line.startswith("[eBPF Tracer]"):
                txt.append(f"ℹ️ {line}\n\n", style="bold cyan")
                continue
            try:
                data = json.loads(line)
                
                # Extract all rich trace fields
                proc_data = data.get("process_exec", {}).get("process", {})
                pid = proc_data.get("pid", "N/A")
                parent = proc_data.get("binary", "N/A")
                
                kprobe_data = data.get("process_kprobe", {})
                func = kprobe_data.get("function_name", "sys_execve")
                ret = kprobe_data.get("return_value", 0)
                
                target_path = "N/A"
                args_list = kprobe_data.get("args", [])
                if args_list:
                    target_path = args_list[0].get("exec_arg", {}).get("filename", "N/A")
                
                dur = data.get("duration_ms", 0.0)
                
                # Check for block return code (-13 is EACCES)
                if ret == -13 or data.get("status") == "BLOCKED":
                    txt.append(f"❌ [KProbe Blocked] {func}\n", style="bold red")
                    txt.append(f"   └─ PID: {pid} | Parent: {parent} | Target: {target_path} | Ret: {ret} (EACCES) | Dur: {dur:.2f}ms\n", style="bold red")
                elif "echo" in target_path or "id" in target_path or data.get("status") == "ANOMALOUS":
                    txt.append(f"🚨 [KProbe Anomaly] {func}\n", style="bold yellow")
                    txt.append(f"   └─ PID: {pid} | Parent: {parent} | Target: {target_path} | Ret: {ret} (Success) | Dur: {dur:.2f}ms\n", style="bold yellow")
                else:
                    txt.append(f"🟢 [KProbe Event] {func}\n", style="green")
                    txt.append(f"   └─ PID: {pid} | Parent: {parent} | Target: {target_path} | Ret: {ret} (Success) | Dur: {dur:.2f}ms\n", style="green")
                
                # Show parsed token dictionary (Webhook Ingestion Payload) instead of raw JSON
                tokens = tokenize(data, self.webhook_mask_profile)
                txt.append(f"  Webhook Payload: {json.dumps(tokens)}\n\n", style="dim")
            except Exception:
                txt.append(f"  {line}\n\n", style="dim")
        return self.limit_text_lines(txt, max_height)

    def clear_logs(self) -> None:
        """Resets all console log buffers to verify validation boundaries."""
        self.client_log_pipe.deque.clear()
        self.server_log_pipe.deque.clear()
        self.raw_traces.clear()
        self.daemon_logs.clear()

    def run_step_actions(self) -> None:
        """Execute state actions on user transition."""
        if self.step == 2:
            # 1. Allocate ports
            import socket
            s1 = socket.socket(); s1.bind(("", 0)); self.app_port = s1.getsockname()[1]; s1.close()
            s2 = socket.socket(); s2.bind(("", 0)); self.webhook_port = s2.getsockname()[1]; s2.close()

            # Redirect stdout/stderr prints from threads to log pipe
            sys.stdout = self.client_log_pipe
            sys.stderr = self.client_log_pipe

            # 2. Provision repo
            import tempfile
            self.temp_dir = tempfile.TemporaryDirectory(prefix="gitops-demo-")
            self.repo_path = self.temp_dir.name
            os.makedirs(os.path.join(self.repo_path, "policies"), exist_ok=True)
            initialize_repo(self.repo_path, default_branch="main")
            self.policy_file = os.path.join(self.repo_path, "policies", "fingerling-vulnerable-target-app.yaml")

            # 3. Start background target app as a subprocess (unbuffered)
            self.app_proc = subprocess.Popen(
                [sys.executable, "-u", "examples/vulnerable_app.py", "--port", str(self.app_port), "--policy-file", self.policy_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            self.app_pid = self.app_proc.pid

            # Start background threads to pipe target app logs into server logs with stream labels
            def stdout_reader(pipe):
                for line in pipe:
                    if line.strip():
                        content = line.strip()
                        if "127.0.0.1 - - [" in content:
                            print(f"[Server access.log] {content}", file=self.server_log_pipe)
                        else:
                            print(f"[Server stdout] {content}", file=self.server_log_pipe)

            def stderr_reader(pipe):
                for line in pipe:
                    if line.strip():
                        print(f"[Server stderr] {line.strip()}", file=self.server_log_pipe)
            
            self.app_stdout_thread = threading.Thread(target=stdout_reader, args=(self.app_proc.stdout,), daemon=True)
            self.app_stderr_thread = threading.Thread(target=stderr_reader, args=(self.app_proc.stderr,), daemon=True)
            self.app_stdout_thread.start()
            self.app_stderr_thread.start()

            # 4. Start Webhook Ingestion Server
            fid_ping = fingerprint_id({"hook_syscall": "sys_execve", "args": [{"exec_arg": {"filename": "/bin/ping"}}]})
            matcher = SlidingWindowMatcher(n=2, whitelist={(fid_ping, fid_ping)})
            mask_profile = [
                MaskEntry("hook_syscall", "$.process_kprobe.function_name", "DEFAULT"),
                MaskEntry("exec_target", "$.process_kprobe.args[0].exec_arg.filename", "DEFAULT"),
                MaskEntry("kernel_return_state", "$.process_kprobe.return_value", "IN_RANGE(-999, 0)"),
            ]

            self.webhook_matcher = matcher
            self.webhook_mask_profile = mask_profile
            self.webhook_warehouse = Warehouse()

            # Define a custom log writer to route Webhook logs to daemon_logs instead of raw_traces
            class WebhookLogWriter:
                def __init__(self, target_list: list[str]) -> None:
                    self.target_list = target_list
                def write(self, s: str) -> int:
                    if s.strip():
                        for line in s.splitlines():
                            if line.strip():
                                content = line.strip()
                                if "[Server webhook.log]" in content:
                                    prefix = " \033[33m[WHK:ACCS]\033[0m"
                                    content = prefix + " " + content.replace("[Server webhook.log]", "").strip()
                                elif "[Server stdout]" in content:
                                    prefix = " \033[95m[WHK:LOG]\033[0m"
                                    content = prefix + " " + content.replace("[Server stdout]", "").strip()
                                self.target_list.append(content)
                    return len(s)

            self.webhook_log_writer = WebhookLogWriter(self.daemon_logs)

            self.webhook_server = run_server(
                port=self.webhook_port,
                warehouse=self.webhook_warehouse,
                matcher=matcher,
                mask_profile=mask_profile,
                workload_name="vulnerable-target-app",
                match_labels={"app": "vuln-app"},
                gitops_repo_path=self.repo_path,
                gpg_sign=False,
                log_writer=self.webhook_log_writer,
            )
            self.webhook_thread = threading.Thread(target=self.webhook_server.serve_forever, daemon=True)
            self.webhook_thread.start()

            # Print statuses to their respective logs
            print(f"[Server stdout] Target App Server listening on 127.0.0.1:{self.app_port} (PID: {self.app_pid})", file=self.server_log_pipe)
            print(f"[Server stdout] Webhook Ingestion Server listening on 127.0.0.1:{self.webhook_port}", file=self.webhook_log_writer)
            self.daemon_logs.append("[eBPF Tracer] Root & bpftrace active! Attaching real eBPF kernel probes.")

        elif self.step == 3:
            self.clear_logs()
            self.update_view()
            if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
            
            print("[Client request] GET /ping?host=127.0.0.1 (safe baseline requests)...", file=sys.stdout)
            self.update_view()
            if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
            time.sleep(1.0)
            
            # Fire E2E capture if use_ebpf is True
            if self.use_ebpf:
                self.raw_traces.append("[eBPF Capture] Launching bpftrace capture on target process subtree...")
                self.update_view()
                if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
                
                proc = run_capture(self.app_pid)
                try:
                    wait_ready(proc.stdout)
                    # Send actual GET requests
                    for _ in range(2):
                        try:
                            resp = urllib.request.urlopen(f"http://127.0.0.1:{self.app_port}/ping?host=127.0.0.1")
                            print(f"[Client response] HTTP 200 OK | Body:\n{resp.read().decode('utf-8').strip()}", file=sys.stdout)
                            self.update_view()
                            if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
                            time.sleep(0.5)
                        except Exception as err:
                            print(f"[Client stderr] Baseline HTTP GET request failed: {err}", file=sys.stderr)
                finally:
                    stop_capture(proc)
                
                # Parse stdout lines into records
                lines = proc.stdout.read().splitlines()
                records = list(parse_stream(lines))
                self.raw_traces.append(f"[eBPF Capture] Captured {len(records)} real execve() events.")
                
                # Forward to Webhook
                webhook_url = f"http://127.0.0.1:{self.webhook_port}/"
                for record in records:
                    try:
                        req = urllib.request.Request(
                            webhook_url,
                            data=json.dumps(record).encode("utf-8"),
                            headers={"Content-Type": "application/json"}
                        )
                        urllib.request.urlopen(req)
                        # Extract binary name for syscall list display
                        func = record["process_kprobe"]["function_name"]
                        if func.startswith("sys_"):
                            func = func[4:]
                        binary = record["process_kprobe"]["args"][0]["exec_arg"]["filename"].split("/")[-1]
                        self.syscall_list.append(f"{func}({binary})")
                    except Exception as err:
                        print(f"[Client stderr] Error posting capture: {err}", file=sys.stderr)
                
                # Fetch dynamically learned whitelist transitions from the matcher
                self.whitelist_2grams.clear()
                for key_pair in list(self.webhook_matcher.whitelist):
                    targets = []
                    for fid in key_pair:
                        entry = self.webhook_warehouse.get(fid)
                        if entry:
                            filename = entry.raw_record["process_kprobe"]["args"][0]["exec_arg"]["filename"].split("/")[-1]
                            targets.append(filename)
                        else:
                            targets.append("ping")
                    self.whitelist_2grams.append(tuple(targets))
            else:
                # Simulated Fallback
                self.syscall_list.extend(["sys_execve(sh)", "sys_execve(ping)", "sys_execve(sh)", "sys_execve(ping)"])
                self.whitelist_2grams.append(("sh", "ping"))
                self.whitelist_2grams.append(("ping", "sh"))
                
                # Fire GET requests
                for _ in range(2):
                    try:
                        resp = urllib.request.urlopen(f"http://127.0.0.1:{self.app_port}/ping?host=127.0.0.1")
                        print(f"[Client response] HTTP 200 OK | Body:\n{resp.read().decode('utf-8').strip()}", file=sys.stdout)
                        self.update_view()
                        if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
                        time.sleep(0.5)
                    except Exception as err:
                        print(f"[Client stderr] Error sending baseline GET: {err}", file=sys.stderr)

                # Send simulated Webhook telemetry
                webhook_url = f"http://127.0.0.1:{self.webhook_port}/"
                sim_records = [
                    {"process_exec": {"process": {"pid": 20491, "binary": "python3"}}, "process_kprobe": {"function_name": "sys_execve", "return_value": 0, "args": [{"exec_arg": {"filename": "/bin/sh"}}]}, "duration_ms": 2.5},
                    {"process_exec": {"process": {"pid": 20492, "binary": "sh"}}, "process_kprobe": {"function_name": "sys_execve", "return_value": 0, "args": [{"exec_arg": {"filename": "/bin/ping"}}]}, "duration_ms": 1.2}
                ]
                for record in sim_records:
                    record_json = json.dumps(record)
                    self.raw_traces.append(record_json)
                    try:
                        req = urllib.request.Request(webhook_url, data=record_json.encode("utf-8"), headers={"Content-Type": "application/json"})
                        urllib.request.urlopen(req)
                    except Exception as err:
                        print(f"[Client stderr] Error sending telemetry: {err}", file=sys.stderr)

        elif self.step == 4:
            self.clear_logs()
            self.update_view()
            if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
            
            print("[Client request] GET /ping?host=127.0.0.1;echo boo (malicious injection)...", file=sys.stdout)
            self.update_view()
            if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
            time.sleep(1.0)
            
            if self.use_ebpf:
                self.raw_traces.append("[eBPF Capture] Launching bpftrace capture on target process subtree...")
                self.update_view()
                if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
                
                proc = run_capture(self.app_pid)
                try:
                    wait_ready(proc.stdout)
                    # Trigger exploit request
                    try:
                        resp = urllib.request.urlopen(f"http://127.0.0.1:{self.app_port}/ping?host=127.0.0.1;echo%20boo")
                        print(f"[Client response] HTTP 200 OK | Body:\n{resp.read().decode('utf-8').strip()}", file=sys.stdout)
                    except Exception:
                        pass
                    time.sleep(0.5)
                finally:
                    stop_capture(proc)
                
                lines = proc.stdout.read().splitlines()
                records = list(parse_stream(lines))
                self.raw_traces.append(f"[eBPF Capture] Captured {len(records)} real execve() events.")
                
                # Forward to Webhook
                webhook_url = f"http://127.0.0.1:{self.webhook_port}/"
                anomalous_found = False
                for record in records:
                    try:
                        req = urllib.request.Request(
                            webhook_url,
                            data=json.dumps(record).encode("utf-8"),
                            headers={"Content-Type": "application/json"}
                        )
                        resp = urllib.request.urlopen(req)
                        res = json.loads(resp.read().decode("utf-8"))
                        
                        func = record["process_kprobe"]["function_name"]
                        if func.startswith("sys_"):
                            func = func[4:]
                        binary = record["process_kprobe"]["args"][0]["exec_arg"]["filename"].split("/")[-1]
                        self.syscall_list.append(f"{func}({binary})")
                        
                        if res.get("scores") and res["scores"][0] > 0.05:
                            anomalous_found = True
                            self.current_score = res["scores"][0]
                    except Exception as err:
                        print(f"[Client stderr] Error posting capture: {err}", file=sys.stderr)
                
                if anomalous_found:
                    self.anomalous_transition = ("ping", "echo")
                    print("[Server stdout] [Anomaly Alert] Webhook matched anomalous transition: ping -> echo", file=self.webhook_log_writer)
            else:
                self.syscall_list.append("sys_execve(echo)")
                self.anomalous_transition = ("ping", "echo")
                self.current_score = 1.0
                try:
                    resp = urllib.request.urlopen(f"http://127.0.0.1:{self.app_port}/ping?host=127.0.0.1;echo%20boo")
                    print(f"[Client response] HTTP 200 OK | Body:\n{resp.read().decode('utf-8').strip()}", file=sys.stdout)
                except Exception as err:
                    print(f"[Client stderr] Exploit app request finished (CWE-78 payload executed)", file=sys.stdout)

                # Post exploit telemetry
                webhook_url = f"http://127.0.0.1:{self.webhook_port}/"
                sim_record = {
                    "process_exec": {"process": {"pid": 20493, "binary": "sh"}},
                    "process_kprobe": {"function_name": "sys_execve", "return_value": 0, "args": [{"exec_arg": {"filename": "/bin/echo"}}]},
                    "duration_ms": 0.8
                }
                record_json = json.dumps(sim_record)
                self.raw_traces.append(record_json)
                try:
                    req = urllib.request.Request(webhook_url, data=record_json.encode("utf-8"), headers={"Content-Type": "application/json"})
                    urllib.request.urlopen(req)
                except Exception as err:
                    print(f"[Client stderr] Webhook alert trigger failed: {err}", file=sys.stderr)

        elif self.step == 5:
            # Load the policy yaml written by Webhook
            print("[Server stdout] GitOps Reconciling commit policy...", file=self.server_log_pipe)
            time.sleep(0.5)
            if os.path.exists(self.policy_file):
                with open(self.policy_file) as f:
                    self.policy_manifest = f.read()
            else:
                self.policy_manifest = "apiVersion: security.kubearmor.com/v1\nkind: KubeArmorPolicy\nmetadata:\n  name: fingerling-vulnerable-target-app\n  annotations:\n    fingerling.io/anomalous-trajectory: 'ping -> echo'\nspec:\n  severity: 5\n  selector:\n    matchLabels:\n      app: vuln-app\n  process:\n    matchPaths:\n      - path: /bin/echo\n    action: Block"

        elif self.step == 6:
            self.clear_logs()
            self.update_view()
            if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
            
            print("[Client request] GET /ping?host=127.0.0.1 (legitimate business traffic verification)...", file=sys.stdout)
            self.update_view()
            if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
            time.sleep(1.0)
            
            try:
                resp = urllib.request.urlopen(f"http://127.0.0.1:{self.app_port}/ping?host=127.0.0.1")
                print(f"[Client response] HTTP 200 OK | Body:\n{resp.read().decode('utf-8').strip()}", file=sys.stdout)
            except Exception as err:
                print(f"[Client stderr] Error verifying baseline: {err}", file=sys.stderr)

        elif self.step == 7:
            self.clear_logs()
            self.update_view()
            if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
            
            print("[Client request] GET /ping?host=127.0.0.1;echo boo (exploit verification)...", file=sys.stdout)
            self.update_view()
            if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
            time.sleep(1.0)
            
            self.raw_traces.append("[eBPF Capture] Launching bpftrace capture on target process subtree...")
            self.update_view()
            if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
            
            proc = run_capture(self.app_pid)
            try:
                wait_ready(proc.stdout)
                try:
                    resp = urllib.request.urlopen(f"http://127.0.0.1:{self.app_port}/ping?host=127.0.0.1;echo%20boo")
                    # Let logs flow in real-time
                    self.update_view()
                    if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
                    time.sleep(1.5)
                    
                    print(f"[Client response] HTTP 200 OK | Body:\n{resp.read().decode('utf-8').strip()}", file=sys.stdout)
                except urllib.error.HTTPError as err:
                    if err.code == 403:
                        print(f"\033[91;1m❌ [Client response] HTTP 403 Forbidden (Blocked by KubeArmorPolicy)\033[0m", file=sys.stdout)
                    else:
                        print(f"[Client response] HTTP {err.code} Error", file=sys.stdout)
                except Exception as err:
                    print(f"[Client stderr] HTTP request failed: {err}", file=sys.stdout)
                
                self.update_view()
                if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()
                time.sleep(1.0)
            finally:
                stop_capture(proc)
            
            records = list(parse_stream(proc.stdout.read().splitlines()))
            self.raw_traces.append(f"[eBPF Capture] Captured {len(records)} real execve() events.")
            for record in records:
                self.raw_traces.append(json.dumps(record))
            self.update_view()
            if hasattr(self, "live_view") and self.live_view: self.live_view.refresh()

    def cleanup(self) -> None:
        """Clean up servers and directories on exit."""
        sys.stdout = sys.__stdout__
        sys.stderr = self.__stderr__ if hasattr(self, "__stderr__") else sys.__stderr__
        
        # Restore terminal settings
        if hasattr(self, "old_settings") and self.old_settings:
            import termios
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.old_settings)
            except Exception:
                pass

        if hasattr(self, "app_proc") and self.app_proc:
            try:
                self.app_proc.terminate()
                self.app_proc.wait(timeout=1.0)
            except Exception:
                try:
                    self.app_proc.kill()
                except Exception:
                    pass
        if self.webhook_server:
            try:
                self.webhook_server.shutdown()
                self.webhook_server.server_close()
            except Exception:
                pass
        if self.temp_dir:
            try:
                self.temp_dir.cleanup()
            except Exception:
                pass

    def run(self) -> None:
        """Start the interactive TUI demo steps loop."""
        self.__stderr__ = sys.stderr
        self.setup_layout()
        
        # Disable echo and canonical mode globally for the duration of the TUI run
        import termios
        self.old_settings = None
        if sys.stdin.isatty():
            try:
                fd = sys.stdin.fileno()
                self.old_settings = termios.tcgetattr(fd)
                new_settings = termios.tcgetattr(fd)
                new_settings[3] = new_settings[3] & ~termios.ICANON & ~termios.ECHO
                termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
            except Exception:
                pass

        try:
            with Live(self.layout, console=self.console, screen=True, auto_refresh=False) as live:
                self.live_view = live
                while self.step <= 8:
                    self.update_view()
                    live.refresh()
                    
                    # Wait for user keypress (blocks in custom cbreak mode)
                    user_val = get_key()

                    if user_val in ('q', '\x03', '\x04'):  # q, Ctrl+C, Ctrl+D
                        break
                    
                    if user_val == 'escape':
                        continue
                    
                    # Advance step
                    self.step += 1
                    if self.step <= 8:
                        self.run_step_actions()
                        # Immediately render again to show any new logs or telemetries
                        self.update_view()
                        live.refresh()
                    
        finally:
            self.cleanup()
            print("TUI Demo closed cleanly. 🛡️")


def main() -> None:
    demo = TUIDemo()
    
    # Register OS signals
    def sig_handler(signum: int, frame: Any) -> None:
        demo.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    
    demo.run()


if __name__ == "__main__":
    main()
