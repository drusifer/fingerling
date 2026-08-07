#!/usr/bin/env bash
# Shell launcher for Project Fingerling interactive demo (STORY-FING-19).

# Get current script directory
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$DIR/.." && pwd)"

# Style formatting variables
BOLD="\033[1m"
RESET="\033[0m"
BLUE="\033[1;34m"
CYAN="\033[36m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"

echo "=================================================================="
echo -e "      ${BOLD}🛡️  PROJECT FINGERLING - INTERACTIVE DEMO LAUNCHER  🛡️${RESET}"
echo "=================================================================="

# Check if tmux is installed and we have a terminal (TTY)
if ! command -v tmux &> /dev/null || ! tty -s; then
    echo -e "${YELLOW}⚠️  tmux terminal multiplexer is not installed on this system.${RESET}"
    echo -e "${CYAN}Falling back to single-terminal interactive step-through mode...${RESET}"
    echo ""
    python3 "$ROOT_DIR/examples/interactive_controller.py" --mode standalone
    exit $?
fi

# We have tmux! Allocate random/free TCP ports for services
echo -e "${BLUE}Allocating ports and provisioning sandbox...${RESET}"
APP_PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()')
WEBHOOK_PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()')

# Cleanup handler to ensure no orphaned directories or tmux sessions are left behind
cleanup() {
    # Silence tmux errors if session is already dead
    if command -v tmux &> /dev/null && tmux has-session -t fingerling-demo 2>/dev/null; then
        tmux kill-session -t fingerling-demo 2>/dev/null
    fi
    if [ -n "$REPO_PATH" ] && [ -d "$REPO_PATH" ]; then
        rm -rf "$REPO_PATH"
    fi
}
trap cleanup EXIT INT TERM SIGHUP

# Create temporary GitOps repository directory
REPO_PATH=$(mktemp -d -t gitops-demo-XXXXXX)
mkdir -p "$REPO_PATH/policies"

# Initialize GitOps repository
python3 -c "
import sys, os
sys.path.insert(0, '$ROOT_DIR')
from fingerling.gitops import initialize_repo
initialize_repo('$REPO_PATH', default_branch='main')
" &> /dev/null

echo -e "  * Target App Port:    ${GREEN}$APP_PORT${RESET}"
echo -e "  * Webhook Server Port:${GREEN}$WEBHOOK_PORT${RESET}"
echo -e "  * GitOps Repository:  ${GREEN}$REPO_PATH${RESET}"
echo ""
echo -e "${BLUE}Launching 4-pane tmux session named 'fingerling-demo'...${RESET}"

# Start new detached tmux session running the controller in Pane 0 (top-left)
# The controller will execute and upon completion it will prompt to exit, terminating the session.
CONTROLLER_CMD="PYTHONPATH=\"$ROOT_DIR\" python3 \"$ROOT_DIR/examples/interactive_controller.py\" --mode tmux --app-port $APP_PORT --webhook-port $WEBHOOK_PORT --repo-path \"$REPO_PATH\"; echo; echo 'Press any key to close session...'; read -n 1; tmux kill-session -t fingerling-demo"

tmux new-session -d -s fingerling-demo -n "Fingerling Demo" -x 160 -y 48 "$CONTROLLER_CMD"

# Split pane 0 horizontally (left and right panes)
tmux split-window -h -t fingerling-demo:0.0

# Split left pane (top-left) vertically
tmux split-window -v -t fingerling-demo:0.0

# Split right pane (top-right) vertically
tmux split-window -v -t fingerling-demo:0.1

# Assign programs to empty panes:
# Pane 1 (top-right): Telemetry Webhook Server
tmux send-keys -t fingerling-demo:0.1 "python3 \"$ROOT_DIR/examples/run_webhook_server.py\" --port $WEBHOOK_PORT --repo-path \"$REPO_PATH\"" C-m

# Pane 2 (bottom-left): Target Application
# App is started with the path of the generated policy to allow real-time GitOps loading
POLICY_PATH="$REPO_PATH/policies/fingerling-vulnerable-target-app.yaml"
tmux send-keys -t fingerling-demo:0.2 "python3 \"$ROOT_DIR/examples/vulnerable_app.py\" --port $APP_PORT --policy-file \"$POLICY_PATH\"" C-m

# Pane 3 (bottom-right): GitOps status visual monitor
WATCHER_LOOP="while true; do clear; echo '=== GitOps Repository Status ==='; echo; echo 'Policies directory ($REPO_PATH/policies):'; ls -la \"$REPO_PATH/policies\" 2>/dev/null || echo ' (no policies generated yet)'; echo; echo 'Git Repository Commit History:'; git -C \"$REPO_PATH\" log --oneline --graph --all 2>/dev/null || echo ' (no commits recorded yet)'; sleep 1; done"
tmux send-keys -t fingerling-demo:0.3 "$WATCHER_LOOP" C-m

# Select Pane 0 (the controller pane) as active
tmux select-pane -t fingerling-demo:0.0

# Attach to the tmux session
tmux attach-session -t fingerling-demo

