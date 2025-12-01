#!/bin/bash
tmux kill-session -t apex 2>/dev/null

tmux new-session -d -s apex -n monitor

# Top pane: Railway logs (auto-refresh every 10s)
tmux send-keys 'cd ~/projects/apex && watch -n 10 "railway logs 2>&1 | tail -40"' C-m

# Bottom half
tmux split-window -v -p 40

# Bottom-left: btop
tmux send-keys 'btop' C-m

# Bottom-right: local server or status
tmux split-window -h -p 35
tmux send-keys 'cd ~/projects/apex && echo "Ready for commands"' C-m

# Focus logs pane
tmux select-pane -t 0

tmux attach -t apex
