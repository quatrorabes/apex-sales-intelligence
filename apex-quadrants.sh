#!/bin/bash
tmux kill-session -t apex 2>/dev/null || true

tmux new-session -d -s apex -n quadrants 'export TERM=xterm-256color'

# Top-left: Railway logs
tmux send-keys 'cd ~/projects/apex && watch -n 10 "railway logs --json 2>/dev/null | tail -40"' C-m

# Top-right: Status
tmux split-window -h -p 50 'export TERM=xterm-256color && cd ~/projects/apex && railway status'

# Bottom-left: btop (from top-left)
tmux select-pane -t 0
tmux split-window -v -p 50 'export TERM=xterm-256color && btop'

# Bottom-right: Commands (from top-right)
tmux select-pane -t 1
tmux split-window -v -p 50 'export TERM=xterm-256color && cd ~/projects/apex && echo "Commands: e.g., railway up, curl localhost:8000"'

tmux select-pane -t 0  # Focus logs
tmux attach -t apex
